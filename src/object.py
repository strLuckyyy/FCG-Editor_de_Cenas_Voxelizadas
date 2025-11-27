from OpenGL.GL import *
import numpy as np

class Object:
    def __init__(self):
        self.vertex_count = {}
    
    # ------------------- Color Helpers ------------------- #
    
    def defineColor(self, shader_program, r, g, b, a=1.0):
        '''
        Define the object color in shader using float values (0.0 - 1.0)
        '''
        color = np.array([float(r), float(g), float(b), float(a)], dtype=np.float32)
        colorLoc = glGetUniformLocation(shader_program, "objColor")
        glUniform4fv(colorLoc, 1, color)
        return shader_program
    
    def rgbToFloat(self, r, g, b):
        ''' Convert RGB values (0 - 255) to float (0.0 - 1.0) '''
        return [float(r) / 255.0, float(g) / 255.0, float(b) / 255.0]

    def objColor(self, tri_amount, r, g, b):
        ''' Generate color array for given number of triangles '''
        colors = [float(r), float(g), float(b)] * 3    
        return np.array(colors * tri_amount, dtype=np.float32) 
    
    # ------------------- Mesh Initializer ------------------- #
    
    def __meshInit(self, vertices, colors=None):
        ''' 
        ## PRIVATE\n 
        Initialize a mesh with given vertices and colors
        
        Returns the VAO ID
        '''
        
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        points = np.array(vertices, dtype=np.float32)
        pvbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, pvbo)
        glBufferData(GL_ARRAY_BUFFER, points, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        
        if colors is not None:
            color = np.array(colors, dtype=np.float32)
            cvbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, cvbo)
            glBufferData(GL_ARRAY_BUFFER, color, GL_STATIC_DRAW)
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
        
        glBindVertexArray(0)
        self.vertex_count[vao] = len(vertices) // 3
        return vao
        
    # ------------------- Builders 3D ------------------- #     
    
    def cubeInit(self, size=[1.,1.,1.], face_colors=None):
        ''' 
        Initialize a cube mesh with given size and face colors 
        
        Returns the VAO ID
        '''
        sx, sy, sz = size[0]/2, size[1]/2, size[2]/2

        vertices = [
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
        ]

        # Colors per face
        if face_colors is not None:
            colors = []
            for color in face_colors:
                colors.extend(color * 6)

            vao = self.__meshInit(vertices, colors)
        vao = self.__meshInit(vertices)
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

        return transform
    
    # ------------------- Abstract Methods ------------------- #
    
    def draw(self):
        '''
        ## Must be implemented in child classes
        
        -- Initialize geometry here ---
        
        self.vao = self.cubeInit(size=[1,1,1])
        
        --------------------------------
        '''
        pass
    
    def render(self, shader_program):
        '''
        ## Must be implemented in child classes
        
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
