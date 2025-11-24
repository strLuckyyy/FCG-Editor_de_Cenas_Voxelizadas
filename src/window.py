
import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
from typing import Optional, List, Any
import numpy as np


class Window:
    def __init__(self, width=800, height=600) -> None:
        # window
        self.window = None
        self.WIDTH = width
        self.HEIGHT = height
        self.shader_program = None
        
        self.delta_time = 0.0
        
        # movement
        self.cam_speed, self.cam_yaw_speed = 10., 30.
        self.cam_pos = np.array([0., 0., 2.])
        
        self.cam_yaw, self.cam_pitch = -90., 0.
        self.last_x, self.last_y = self.WIDTH / 2, self.HEIGHT / 2
        
        self.first_mouse = True
    
    # Callback -----------------------------------
    def redimensionCallback(self, window, w, h):
        self.WIDTH = w
        self.HEIGHT = h
    
    def mouseCallback(self, window, xpos, ypos):
        if self.first_mouse:
            self.last_x, self.last_y = xpos, ypos
            self.first_mouse = False
        
        xoffset = xpos - self.last_x
        yoffset = self.last_y - ypos
        self.last_x, self.last_y = xpos, ypos
        
        sensitivity = 0.1
        xoffset *= sensitivity
        yoffset *= sensitivity
        
        self.cam_yaw += xoffset
        self.cam_pitch += yoffset
    
    def keyCallback(self, window, key, scancode, action, mods):  
        '''
        Inputs do teclado
        '''

        if action == glfw.PRESS: # verificando se a tecla foi pressionada
            
            # --- INSERÇÃO ---
            if key == glfw.KEY_SPACE:
                print("Inserindo Voxel...")
                # Chamando uma função a ser criada no cubo
                if hasattr(self, 'target_cube'):
                    self.target_cube.add_voxel()

            # --- DELEÇÃO ---
            elif key == glfw.KEY_DELETE or key == glfw.KEY_BACKSPACE:
                print("Deletando Voxel...")
                if hasattr(self, 'target_cube'):
                    self.target_cube.remove_voxel()
    
    # --------------------------------------------
    
    def openGLInit(self, name="Casa 3D"): 
        '''
        Initialize GLFW and create a window
        Here you will find the window creation and context initialization
        '''
        glfw.init()
        
        self.window = glfw.create_window(self.WIDTH, self.HEIGHT, name, None, None)
        if not self.window:
            glfw.terminate()
            exit()
            
        glfw.set_window_size_callback(self.window, self.redimensionCallback)
        glfw.make_context_current(self.window)
        
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        glfw.set_cursor_pos_callback(self.window, self.mouseCallback)
        glfw.set_key_callback(self.window, self.keyCallback)

    def shaderInit(self):
        '''
        Initialize shaders
        Here you will find the vertex and fragment shaders code and their compilation
        '''
        vertex_shader = """
            #version 400
            layout(location = 0) in vec3 vertex_posicao;        
            //view - matriz da câmera recebida do PYTHON
            //proj - matriz de projeção recebida do PYTHON
            //transform - matriz de transformação geométrica do objeto recebida do PYTHON
            uniform mat4 transform, view, proj;
            void main () {
                gl_Position = proj*view*transform*vec4 (vertex_posicao, 1.0);
            }
        """
        
        vs = compileShader(vertex_shader, GL_VERTEX_SHADER)
        if not glGetShaderiv(vs, GL_COMPILE_STATUS):
            infoLog = glGetShaderInfoLog(vs, 512, None)
            print("Erro no vertex shader:\n", infoLog)
            
        fragment_shader = """
            #version 400
            out vec4 frag_colour;
            uniform vec4 objColor;
            void main () {
                frag_colour = objColor;
            }
        """
        
        fs = compileShader(fragment_shader, GL_FRAGMENT_SHADER)
        if not glGetShaderiv(fs, GL_COMPILE_STATUS):
            infoLog = glGetShaderInfoLog(fs, 512, None)
            print("Erro no fragment shader:\n", infoLog)
            
        self.shader_program = compileProgram(vs, fs)
        if not glGetProgramiv(self.shader_program, GL_LINK_STATUS):
            infoLog = glGetProgramInfoLog(self.shader_program)
            print("Erro no shader program:\n", infoLog)
        
        glDeleteShader(vs)
        glDeleteShader(fs)
    
    def visualizationMatrixEsp(self):
        '''
        Define the view matrix (camera)
        '''
        front = np.array([
            np.cos(np.radians(self.cam_yaw)) * np.cos(np.radians(self.cam_pitch)),
            np.sin(np.radians(self.cam_pitch)),
            np.sin(np.radians(self.cam_yaw)) * np.cos(np.radians(self.cam_pitch))
        ])
        front = front / np.linalg.norm(front)

        center = self.cam_pos + front
        up = np.array([0.0, 1.0, 0.0])

        f = (center - self.cam_pos)
        f = f / np.linalg.norm(f)
        s = np.cross(f, up)
        s = s / np.linalg.norm(s)
        u = np.cross(s, f)

        view = np.identity(4, dtype=np.float32)
        view[0, :3] = s
        view[1, :3] = u
        view[2, :3] = -f
        view[0, 3] = -np.dot(s, self.cam_pos)
        view[1, 3] = -np.dot(u, self.cam_pos)
        view[2, 3] = np.dot(f, self.cam_pos)

        transformLoc = glGetUniformLocation(self.shader_program, "view")
        glUniformMatrix4fv(transformLoc, 1, GL_TRUE, view)
    
    def projectionMatrixEsp(self):
        '''
        Define the projection matrix (perspective)
        '''
        znear = 0.1 #recorte z-near
        zfar = 100.0 #recorte z-far
        fov = np.radians(67.0) #campo de visão
        aspecto = self.WIDTH/self.HEIGHT #aspecto

        a = 1/(np.tan(fov/2)*aspecto)
        b = 1/(np.tan(fov/2))
        c = (zfar + znear) / (znear - zfar)
        d = (2*znear*zfar) / (znear - zfar)
        projecao = np.array([
            [a,   0.0, 0.0,  0.0],
            [0.0, b,   0.0,  0.0],
            [0.0, 0.0, c,    d],
            [0.0, 0.0, -1.0, 1.0]
        ])

        transformLoc = glGetUniformLocation(self.shader_program, "proj")
        glUniformMatrix4fv(transformLoc, 1, GL_TRUE, projecao)
    
    def camInit(self):
        self.visualizationMatrixEsp()
        self.projectionMatrixEsp()
    
    def keyboardHandle(self):
        '''
        Responsible for handling keyboard inputs for camera movement
        Maybe this can be moved to the keyCallback method
        '''
        speed = self.cam_speed * self.delta_time
        
        foward = np.array([
            np.cos(np.radians(self.cam_yaw)) * np.cos(np.radians(self.cam_pitch)),
            np.sin(np.radians(self.cam_pitch)),
            np.sin(np.radians(self.cam_yaw)) * np.cos(np.radians(self.cam_pitch))
        ])
        foward /= np.linalg.norm(foward)
        
        right = np.cross(foward, np.array([0.0, 1.0, 0.0]))
        right /= np.linalg.norm(right)
        
        # W/S
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
            self.cam_pos += foward * speed
        if glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS:
            self.cam_pos -= foward * speed
            
        # A/D
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
            self.cam_pos -= right * speed
        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
            self.cam_pos += right * speed
            
        if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(self.window, True)
    
    def renderInit(self, objects: Optional[List[Any]] = None):
        '''
        Render initialization and main loop
        '''
        before_time = glfw.get_time()
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        while not glfw.window_should_close(self.window):
            current_time = glfw.get_time()
            self.delta_time = current_time - before_time
            before_time = current_time
            
            glClearColor(0.5, 0.7, 1.0, 1.0)
            glClear(GL_COLOR_BUFFER_BIT)
            glClear(GL_DEPTH_BUFFER_BIT)
            
            glViewport(0, 0, self.WIDTH, self.HEIGHT)
            glUseProgram(self.shader_program)
            
            self.camInit()
            
            if objects is not None:
                for obj in objects:
                    self.shader_program = obj.render(self.shader_program)
            
            glfw.swap_buffers(self.window)
            glfw.poll_events()
            
            self.keyboardHandle()
            
        glfw.terminate()

