
from tkinter import Tk, filedialog
from cube import *
import numpy as np
import os

class SceneManager:
    def __init__(self, filename="save1.txt"):
        self.filename = filename
        self.root = Tk()
        self.root.withdraw()
        
    # ------------------------- FILE DIALOGS ------------------------- #
    
    def ask_save_file(self, initial_dir="saves"):
        os.makedirs(initial_dir, exist_ok=True)

        filepath = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            title="Salvar cena",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")]
        )
        
        return filepath

    def ask_open_file(self, initial_dir="saves"):
        filepath = filedialog.askopenfilename(
            initialdir=initial_dir,
            title="Carregar cena",
            filetypes=[("Text Files", "*.txt")]
        )

        return filepath

    # ------------------------- SAVE ------------------------- #
    
    def save_scene(self, cube_object: Cube):
        """
        Read the cube_object grid and save the scene to a text file.
        
        Format:
        
        SIZE <grid_size>
        SPACE <grid_space>
        x y z r g b
        """
        filename = self.ask_save_file()

        if not filename:
            return
        
        self.filename = filename

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"SIZE {cube_object.size}\n")
                f.write(f"SPACE {cube_object.grid_space}\n")
                
                it = np.nditer(np.zeros(cube_object.grid.shape), flags=['multi_index'])
                for _ in it:
                    x, y, z = it.multi_index
                    voxel = cube_object.grid[x, y, z]

                    if voxel and voxel.is_visible:
                        r, g, b, a = voxel.color
                        f.write(f"{x} {y} {z} {r} {g} {b} {a}\n")

            print("Cena salva com sucesso!")
        except Exception as e:
            print(f"Erro ao salvar: {e}")

    def load_scene(self, cube_object: Cube):
        filename = self.ask_open_file()
        if not filename:
            print("Carregamento cancelado.")
            return

        with open(filename, "r") as f:
            lines = f.readlines()

        size_line = lines[0].split()
        space_line = lines[1].split()

        new_size = int(size_line[1])
        new_space = float(space_line[1])

        # Reinitialize cube grid
        cube_object.size = new_size
        cube_object.grid_space = new_space
        cube_object.grid = np.empty((new_size, new_size, new_size), dtype=Voxel)

        # Initialize all voxels as invisible
        for x in range(new_size):
            for y in range(new_size):
                for z in range(new_size):
                    cube_object.grid[x, y, z] = Voxel(
                        pos=np.array([x, y, z], dtype=float),
                        scale=new_space,
                        color=np.array([0, 0, 0, 1.0]),
                        is_visible=False
                    )

        # Load voxel data
        for line in lines[2:]:  # skip SIZE and SPACE lines
            if not line.strip():
                continue
            x, y, z, r, g, b = line.split()
            x = int(x); y = int(y); z = int(z)
            r = float(r); g = float(g); b = float(b)

            voxel = cube_object.grid[x, y, z]
            voxel.is_visible = True
            voxel.color = np.array([r, g, b, 1.0])

        print("Cena carregada com sucesso!")
