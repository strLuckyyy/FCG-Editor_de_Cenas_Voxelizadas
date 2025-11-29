'''
    Final project for the Graphics Computing Fundamentals course
    at the Universidade do Vale do Rio dos Sinos (UNISINOS).
    
    Developed by: Abrahão Francis & Marcos Rocha
'''


from cube import Cube
from window import Window

# variables and objects
win = Window()
cube = Cube()

win.target_cube = cube

if __name__ == "__main__":
    win.openGLInit("Editor de Cenas Voxelizadas")
    cube.draw()
    win.shaderInit()
    win.renderInit([cube])