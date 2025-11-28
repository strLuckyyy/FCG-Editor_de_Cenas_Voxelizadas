
from dataclasses import dataclass
from typing import override
from object import Object
from OpenGL.GL import (
    glBindVertexArray,
    glGetUniformLocation,
    glUniformMatrix4fv,
    glDrawArrays,
    glPolygonMode,
    glLineWidth,
    GL_TRIANGLES,
    GL_TRUE,
    GL_FRONT_AND_BACK,
    GL_LINE,
    GL_FILL,
)
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
    def __init__(self, grid_size=3):
        super().__init__()
        self.cube_vao = None
        
        self.size = grid_size # handle of the grid size
        self.grid = np.empty((self.size,self.size,self.size), dtype=object) # grid to hold the voxels
        self.selection_x, self.selection_y, self.selection_z = 0,0,self.size-1 # current selected voxel coordinates

    # ------------------- Voxel Management Methods ------------------- #
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

    def remove_voxel(self):
        """Torna o voxel selecionado invisível (remove)"""
        voxel = self.get_selected_voxel()

        if voxel.is_visible:
            voxel.is_visible = False

    def paint_selected_voxel(self, r, g, b):
        """
        Altera a cor do voxel atualmente selecionado para a cor especificada.
        """
        # Verifica se as coordenadas de seleção são válidas na grid
        if (0 <= self.selection_x < self.size and 
            0 <= self.selection_y < self.size and 
            0 <= self.selection_z < self.size):
            
            voxel = self.grid[self.selection_x, self.selection_y, self.selection_z]
            
            # Só pinta se o voxel existir e estiver visível
            if voxel and voxel.is_visible:
                voxel.color = np.array([r, g, b, 1.0])

    def clear_scene(self):
        """
        Torna todos os voxels atuais invisíveis.
        Usado automaticamente antes de carregar um arquivo novo.
        """
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    # Se existe um voxel nessa posição, desliga a visibilidade dele
                    if self.grid[x, y, z]: 
                        self.grid[x, y, z].is_visible = False    

    def raycast_selection(self, cam_pos, cam_front, max_distance=20.0):
        """
        Faz ray casting a partir da câmera e retorna o voxel mais próximo intersectado
        Atualiza self.selection_x, y, z
        """
        best_t = float('inf')
        best_voxel = None

        # Direção normalizada do raio (cam_front já está normalizado no seu código)
        direction = cam_front / np.linalg.norm(cam_front)

        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    voxel: Voxel = self.grid[x, y, z]
                    '''if not voxel.is_visible and not hasattr(voxel, 'is_visible'):
                        continue  # pula se ainda não foi criado'''

                    # Centro do voxel no mundo (considerando escala 0.75 e offset)
                    center = np.array([x, y, z], dtype=float)
                    half_size = voxel.scale / 2.0  # 0.375

                    # AABB (Axis-Aligned Bounding Box) do voxel
                    min_bound = center - half_size
                    max_bound = center + half_size

                    # Ray-AABB intersection (slab method)
                    tmin = 0.0
                    tmax = max_distance

                    for i in range(3):
                        if abs(direction[i]) < 1e-6:
                            # Raio paralelo ao eixo
                            if cam_pos[i] < min_bound[i] or cam_pos[i] > max_bound[i]:
                                tmin = float('inf')
                                break
                        else:
                            t1 = (min_bound[i] - cam_pos[i]) / direction[i]
                            t2 = (max_bound[i] - cam_pos[i]) / direction[i]
                            tmin = max(tmin, min(t1, t2))
                            tmax = min(tmax, max(t1, t2))

                    if tmin <= tmax and tmin < best_t and tmax >= 0:
                        best_t = tmin
                        best_voxel = (x, y, z)

        if best_voxel is not None:
            # Desmarcar o anterior
            if hasattr(self, 'selection_x'):
                old = self.grid[self.selection_x, self.selection_y, self.selection_z]
                if old is not None:
                    old.is_selected = False

            # Marcar o novo
            self.selection_x, self.selection_y, self.selection_z = best_voxel
            voxel = self.grid[best_voxel]
            voxel.is_selected = True

            return voxel.pos  # retorna posição para debug se quiser

        return None

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
                    a = 1.
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
                    voxel = self.grid[x, y, z]
                    visible = voxel.is_visible

                    if visible:
                        # --- desenha normalmente ---
                        Tx, Ty, Tz = voxel.pos
                        S = voxel.scale

                        r, g, b, a = voxel.color

                        if voxel.is_selected:
                            r = min(r + 0.5, 1.0)
                            g = min(g + 0.5, 1.0)
                            b = min(b + 0.5, 1.0)

                        self.defineColor(shader_program, r, g, b, a)
                        transform = self.transformation(Tx, Ty, Tz, Sx=S, Sy=S, Sz=S)
                        transform_loc = glGetUniformLocation(shader_program, "transform")
                        glUniformMatrix4fv(transform_loc, 1, GL_TRUE, transform)

                        glDrawArrays(GL_TRIANGLES, 0, cube_count)

                    else:
                        # --- DESENHAR WIREFRAME SE ESTIVER SELECIONADO ---
                        if voxel.is_selected:
                            Tx, Ty, Tz = voxel.pos
                            S = voxel.scale

                            # cor branca do wireframe
                            self.defineColor(shader_program, 1.0, 1.0, 1.0, 1.0)

                            transform = self.transformation(Tx, Ty, Tz, Sx=S, Sy=S, Sz=S)
                            transform_loc = glGetUniformLocation(shader_program, "transform")
                            glUniformMatrix4fv(transform_loc, 1, GL_TRUE, transform)

                            # desenhar como wireframe
                            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                            glLineWidth(2.5)
                            glDrawArrays(GL_TRIANGLES, 0, cube_count)
                            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
        return shader_program