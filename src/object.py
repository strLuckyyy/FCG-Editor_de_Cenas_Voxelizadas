from OpenGL.GL import (
    glGenVertexArrays, glBindVertexArray,
    glGenBuffers, glBindBuffer, glBufferData,
    glEnableVertexAttribArray, glVertexAttribPointer,
    glGetUniformLocation, glUniform4f,
    GL_ARRAY_BUFFER, GL_STATIC_DRAW, GL_FLOAT, GL_FALSE
)
import numpy as np
from typing import Optional

class Object:
    _mesh_cache = {}
    _uniform_cache = {}
    
    def __init__(self):
        self.vertex_count = {}
    
    # ------------------- Uniform Location Cache ------------------- #
    
    def _get_uniform_location(self, shader_program, name: str):
        """Cacheia glGetUniformLocation por (program, name)."""
        key = (int(shader_program), name)
        loc = Object._uniform_cache.get(key)
        if loc is None:
            loc = glGetUniformLocation(shader_program, name)
            Object._uniform_cache[key] = loc
        return loc
    
    # ------------------- Color Helpers ------------------- #
    
    def defineColor(self, shader_program, r, g, b, a=1.0):
        '''
        Define the object color in shader using float values (0.0 - 1.0)
        '''
        glUniform4f(self._get_uniform_location(shader_program, "objColor"), 
                    float(r), float(g), float(b), float(a))
        return shader_program
    
    def rgbToFloat(self, r, g, b):
        ''' Convert RGB values (0 - 255) to float (0.0 - 1.0) '''
        return [float(r) / 255.0, float(g) / 255.0, float(b) / 255.0]

    def objColor(self, tri_amount, r, g, b):
        ''' Generate color array for given number of triangles '''
        color_vec = np.array([float(r), float(g), float(b)], dtype=np.float32)
        verts = tri_amount * 3
        return np.tile(color_vec, verts).astype(np.float32)
    
    # ------------------- Mesh Initializer ------------------- #
    def __meshInit(self, vertices: np.ndarray, colors: Optional[np.ndarray] = None):
        ''' 
        ## PRIVATE\n 
        Initialize a mesh with given vertices and colors
        
        Returns the VAO ID
        '''
        assert isinstance(vertices, np.ndarray) and vertices.dtype == np.float32
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        pvbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, pvbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        
        if colors is not None:
            assert isinstance(colors, np.ndarray) and colors.dtype == np.float32
            cvbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, cvbo)
            glBufferData(GL_ARRAY_BUFFER, colors.nbytes, colors, GL_STATIC_DRAW)
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
        
        glBindVertexArray(0)
        self.vertex_count[vao] = int(len(vertices) // 3)
        return vao
        
    # ------------------- Builders 3D ------------------- #     
    
    def cubeInit(self, size=[1.,1.,1.], face_colors=None):
        ''' 
        Initialize a cube mesh with given size and face colors 
        
        Returns the VAO ID
        '''
        sx, sy, sz = float(size[0]) / 2.0, float(size[1]) / 2.0, float(size[2]) / 2.0
        
        # Check cache
        key = ("cube", round(sx,6), round(sy,6), round(sz,6),
               tuple(tuple(map(float, c)) for c in (face_colors or ())))
        cached = Object._mesh_cache.get(key)
        if cached:
            return cached

        vertices = np.array([
            # Front
            -sx,-sy, sz,   sx,-sy, sz,   sx, sy, sz,
            -sx,-sy, sz,   sx, sy, sz,  -sx, sy, sz,
            # Back
            -sx,-sy,-sz,  -sx, sy,-sz,   sx, sy,-sz,
            -sx,-sy,-sz,   sx, sy,-sz,   sx,-sy,-sz,
            # Right
            sx,-sy,-sz,   sx, sy,-sz,   sx, sy, sz,
            sx,-sy,-sz,   sx, sy, sz,   sx,-sy, sz,
            # Left
            -sx,-sy,-sz,  -sx,-sy, sz,  -sx, sy, sz,
            -sx,-sy,-sz,  -sx, sy, sz,  -sx, sy,-sz,
            # Top
            -sx, sy, sz,   sx, sy, sz,   sx, sy,-sz,
            -sx, sy, sz,   sx, sy,-sz,  -sx, sy,-sz,
            # Base
            -sx,-sy,-sz,   sx,-sy,-sz,   sx,-sy, sz,
            -sx,-sy,-sz,   sx,-sy, sz,  -sx,-sy, sz
        ], dtype=np.float32)

        colors_array = None
        if face_colors is not None:
            fc = list(face_colors)
            if len(fc) != 6:
                raise ValueError("face_colors deve conter 6 cores (uma por face).")
            
            colors_list = []
            for color in fc:
                col = np.array(color, dtype=np.float32)
                colors_list.append(np.tile(col, 6)) 
            colors_array = np.concatenate(colors_list).astype(np.float32)

        vao = self.__meshInit(vertices, colors_array)
        Object._mesh_cache[key] = vao
        return vao
    
    # ------------------- Transformations ------------------- #
    
    def transformation(
        self, 
        Tx=0., Ty=0., Tz=0., 
        Rx=0., Ry=0., Rz=0., 
        Sx=1., Sy=1., Sz=1.
        ):
        '''
        Transformation matrix combining translation, rotation and scaling
        
        Tx, Ty, Tz -> Translation along x, y, z
        
        Rx, Ry, Rz -> Rotation angles (in degrees) around x, y,
        
        Sx, Sy, Sz -> Scaling along x, y, z
        
        If no parameters are provided, default transformations are applied
        0 translation, 0 rotation, 1 scale
        '''
        
        translation = np.array([
            [1.0, 0.0, 0.0, Tx],
            [0.0, 1.0, 0.0, Ty],
            [0.0, 0.0, 1.0, Tz],
            [0.0, 0.0, 0.0, 1.0]], np.float32
        )
        
        angle = np.radians(Rx)
        cos, sen = np.cos(angle), np.sin(angle)
        rotation_x = np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, cos, -sen, 0.0],
            [0.0, sen, cos, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])
        
        angle = np.radians(Ry)
        cos, sen = np.cos(angle), np.sin(angle)
        rotation_y = np.array([
            [cos, 0.0, sen, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [-sen, 0.0, cos, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])
        
        angle = np.radians(Rz)
        cos, sen = np.cos(angle), np.sin(angle)
        rotation_z = np.array([
            [cos, -sen, 0.0, 0.0],
            [sen, cos, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])
        
        scale = np.array([
            [Sx, 0.0, 0.0, 0.0],
            [0.0, Sy, 0.0, 0.0],
            [0.0, 0.0, Sz, 0.0],
            [0.0, 0.0, 0.0, 1.0]], np.float32
        )
        
        rotation = rotation_z @ rotation_y @ rotation_x
        transform = translation @ rotation @ scale

        return transform.astype(np.float32)
    
    # ------------------- Abstract Methods ------------------- #
    
    def draw(self):
        '''
        ## Must be implemented in child classes -> @override
        
        -- Initialize geometry here ---
        
        self.vao = self.cubeInit(size=[1,1,1])
        
        --------------------------------
        '''
        pass
    
    def render(self, shader_program):
        '''
        ## Must be implemented in child classes -> @override
        
        ----- bind vao -----\n
        glBindVertexArray(vao)
        
        ----- set transformation -----\n
        transform = self.transformation(tx, ty, tz, rx, ry, rz, sx, sy, sz)
        
        transformLoc = glGetUniformLocation(shader_programm, "transform")
        glUniformMatrix4fv(transformLoc, 1, GL_TRUE, transform)
        
        ----- draw call -----\n
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        
        ----- return shader program -----\n
        return shader_programm
        '''
        return shader_program
