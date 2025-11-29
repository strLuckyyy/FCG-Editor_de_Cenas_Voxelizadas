
from dataclasses import dataclass
from typing import override
from object import Object
from OpenGL.GL import (
    glBindVertexArray, glGetUniformLocation, glDrawArrays, glPolygonMode, glLineWidth,
    glUniformMatrix4fv,
    GL_TRIANGLES, GL_TRUE, GL_FRONT_AND_BACK, GL_LINE, GL_FILL,
)
import numpy as np
from numpy.typing import NDArray
from random import random
from sound_manager import SoundManager

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
        
        # Sound manager for voxel actions
        self.sound: SoundManager = SoundManager()
        self.sound.load_sound('broke', 'broke_block.mp3')
        self.sound.load_sound('place', 'place_block.mp3')

        # Grid and Voxel Management
        self.size = grid_size # handle of the grid size
        self.grid = np.empty((self.size, self.size, self.size), dtype=Voxel) # grid to hold the voxels
        self.selection_x, self.selection_y, self.selection_z = 0,0,self.size-1 # current selected voxel coordinates      
        self.grid_space = 1.
        
        # Grid initialization with random colors
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    r, g, b, a = random(), random(), random(), random()
                    self.grid[x, y, z] = Voxel(
                        pos=np.array([x, y, z], dtype=float),
                        scale=self.grid_space,
                        color=np.array([r, g, b, a]),
                        is_visible=True
                    )

    # ------------------- Voxel Management Methods ------------------- #
    def get_selected_voxel(self):
        return self.grid[self.selection_x, self.selection_y, self.selection_z]
    
    def add_voxel(self): 
        voxel: Voxel = self.get_selected_voxel()

        # Place only if not already visible
        if not voxel.is_visible:
            voxel.is_visible = True
            
            r, g, b, a = random(), random(), random(), random()
            voxel.color = np.array([r, g, b, a])
            
            self.sound.play_sound('place', volume=0.5)

    def remove_voxel(self):
        voxel: Voxel = self.get_selected_voxel()

        if voxel.is_visible:
            voxel.is_visible = False
            
            self.sound.play_sound('broke', volume=0.5)

    def paint_selected_voxel(self, r, g, b):
        # Check if selection is within bounds
        if (0 <= self.selection_x < self.size and 
            0 <= self.selection_y < self.size and 
            0 <= self.selection_z < self.size):
            
            voxel: Voxel = self.grid[self.selection_x, self.selection_y, self.selection_z]
            
            # Only paint if the voxel is visible
            if voxel and voxel.is_visible:
                voxel.color = np.array([r, g, b, 1.0])

    def raycast_selection(self, cam_pos, cam_front, max_distance=20.0):
        """
        Performs ray casting from the camera and returns the nearest intersected voxel.
        Updates self.selection_x, self.selection_y, and self.selection_z.
        """
        best_t = float('inf')
        best_voxel = None

        # Normalize camera front direction
        direction = cam_front / np.linalg.norm(cam_front)

        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    voxel: Voxel = self.grid[x, y, z]
                    '''if not voxel.is_visible and not hasattr(voxel, 'is_visible'):
                        continue  # pula se ainda não foi criado'''

                    # Center of the voxel in world space (considering scale 0.75 and offset)
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
                            # Ray is parallel to slab
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

        if best_voxel is not None: # Unmark previous selection
            if hasattr(self, 'selection_x'):
                old = self.grid[self.selection_x, self.selection_y, self.selection_z]
                if old is not None:
                    old.is_selected = False

            # Mark new selection
            self.selection_x, self.selection_y, self.selection_z = best_voxel
            voxel = self.grid[best_voxel]
            voxel.is_selected = True

            return voxel.pos # to debug if needed
        return None

    def updateGridSpace(self, new_space):
        """Update the spacing of the voxel grid."""
        if new_space > 0:
            self.grid_space = min(1.0, self.grid_space + 0.1)
        else:
            self.grid_space = max(0.1, self.grid_space - 0.1)
            
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    self.grid[x, y, z].scale = self.grid_space

    @override
    def draw(self):
        self.cube_vao = self.cubeInit(size=[1.,1.,1.]) 
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
                    voxel: Voxel = self.grid[x, y, z]
                    visible = voxel.is_visible

                    if visible:
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

                    else: # --- Draw wireframe when the voxel is selected and not visible ---
                        if voxel.is_selected:
                            Tx, Ty, Tz = voxel.pos
                            S = voxel.scale

                            self.defineColor(shader_program, 1.0, 1.0, 1.0, 1.0)

                            transform = self.transformation(Tx, Ty, Tz, Sx=S, Sy=S, Sz=S)
                            transform_loc = glGetUniformLocation(shader_program, "transform")
                            glUniformMatrix4fv(transform_loc, 1, GL_TRUE, transform)

                            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                            glLineWidth(2.5)
                            glDrawArrays(GL_TRIANGLES, 0, cube_count)
                            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
        return shader_program