
from dataclasses import dataclass
from typing import override
from object import Object
from OpenGL.GL import *
import numpy as np
import random

@dataclass
class Voxel:
    pos: np.ndarray
    scale: float
    color: np.ndarray
    is_visible: bool = True
    is_selected: bool = False


class Cube(Object):
    def __init__(self, grid_size=3): # tamanho padrão da grid
        super().__init__()
        self.cube_vao = None
        
        self.size = grid_size # handle of the grid size
        self.grid = np.empty((self.size,self.size,self.size), dtype=object) # grid to hold the voxels
        self.selection_x, self.selection_y, self.selection_z = 0,0,self.size-1 # current selected voxel coordinates
        # nesse trecho fica definido o voxel selecionado no início do programa 
    

    def get_selected_voxel(self):
        """Retorna o objeto Voxel que está atualmente selecionado"""
        return self.grid[self.selection_x, self.selection_y, self.selection_z]
    
    def add_voxel(self): 
        """Torna o voxel selecionado visível (adiciona) e define uma cor"""
        voxel = self.get_selected_voxel()

    # adiciona se ele não estiver visível
        if not voxel.is_visible:
            voxel.is_visible = True

            # Cor aleatória para o cubo adicionado
            r, g, b = random.random(), random.random(), random.random()
            voxel.color = np.array([r, g, b, 1.0])
            print(f"Voxel adicionado em {voxel.pos}")

    def remove_voxel(self):
        """Torna o voxel selecionado invisível (remove)"""
        voxel = self.get_selected_voxel()

        if voxel.is_visible:
            voxel.is_visible = False
            print(f"Voxel removido de {voxel.pos}")


    @override
    def draw(self):
        self.cube_vao = self.cubeInit(size=[1.,1.,1.]) # initialize cube geometry

        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    # define a random color for the voxel
                    r = random.random()
                    g = random.random()
                    b = random.random()
                    #a = random.random()
                    a = 0.8
                    color = np.array([r,g,b,a])
                    
                    # define if voxel is visible or not
                    #visible = random.choice([True, False])
                    visible = True
                    
                    #cria o objeto Voxel na grid
                    self.grid[x, y, z] = Voxel(np.array([x, y, z], dtype=float), scale=0.75, color=color, is_visible=visible)
                    
        self.grid[
            self.selection_x,
            self.selection_y,
            self.selection_z].is_selected = True
    
    @override
    def render(self, shader_program):
        cube_count = self.vertex_count[self.cube_vao]
        
        glBindVertexArray(self.cube_vao)
        
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    #pega se o voxel ta visível ou não
                    visible = self.grid[x, y, z].is_visible
                    
                    if visible:
                        #pega a posição do voxel
                        Tx = self.grid[x, y, z].pos[0]
                        Ty = self.grid[x, y, z].pos[1]
                        Tz = self.grid[x, y, z].pos[2]
                        
                        #pega o fator de escala do voxel
                        S = self.grid[x, y, z].scale
                        
                        #pega a cor do voxel
                        r = self.grid[x, y, z].color[0]
                        g = self.grid[x, y, z].color[1]
                        b = self.grid[x, y, z].color[2]
                        a = self.grid[x, y, z].color[3]
                        
                        #se estiver selecionado, deixa a cor + forte
                        if self.grid[x, y, z].is_selected:
                            r+=0.5
                            g+=0.5
                            b+=0.5
                            
                        self.defineColor(shader_program, r, g, b, a)
                        transform = self.transformation(Tx, Ty, Tz, Sx=S, Sy=S, Sz=S)
                        transform_loc = glGetUniformLocation(shader_program, "transform")
                        glUniformMatrix4fv(transform_loc, 1, GL_TRUE, transform)
                        glDrawArrays(GL_TRIANGLES, 0, cube_count)
        
        return shader_program