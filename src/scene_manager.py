
from tkinter import Tk, filedialog
from cube import *
import numpy as np
import os

class SceneManager:
    def __init__(self, filename="grid_salva.txt"):
        self.filename = filename

    def ask_save_file(self, initial_dir="saves"):
        root = Tk()
        root.withdraw()

        os.makedirs(initial_dir, exist_ok=True)

        filepath = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            title="Salvar cena",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")]
        )

        root.destroy()
        return filepath

    def ask_open_file(self, initial_dir="saves"):
        root = Tk()
        root.withdraw()

        filepath = filedialog.askopenfilename(
            initialdir=initial_dir,
            title="Carregar cena",
            filetypes=[("Text Files", "*.txt")]
        )

        root.destroy()
        return filepath

    def save_scene(self, cube_object: Cube):
        """
        Lê a grid do cubo e salva no arquivo de texto.
        """
        filename = self.ask_save_file()

        if not filename:
            print("Salvamento cancelado.")
            return

        print(f"Salvando cena em {filename}...")
        self.filename = filename

        try:
            with open(filename, "w") as f:
                for x in range(cube_object.size):
                    for y in range(cube_object.size):
                        for z in range(cube_object.size):
                            voxel: Voxel = cube_object.grid[x, y, z]

                            if voxel and voxel.is_visible:
                                r, g, b, a = voxel.color
                                f.write(f"{x} {y} {z} {r} {g} {b}\n")

            print("Cena salva com sucesso!")
        except Exception as e:
            print(f"Erro ao salvar: {e}")

    def load_scene(self, cube_object: Cube):
        """
        Lê o arquivo de texto e modifica a grid do cubo.
        """
        filename = self.ask_open_file()

        if not filename:
            print("Carregamento cancelado.")
            return

        self.filename = filename
        print(f"Carregando cena de {filename}...")

        try:
            with open(filename, "r") as f:
                cube_object.clear_scene()
                for line in f:
                    if not line.strip():
                        continue

                    data = line.split()
                    x, y, z = map(int, data[:3])
                    r, g, b = map(float, data[3:6])

                    if (
                        0 <= x < cube_object.size and
                        0 <= y < cube_object.size and
                        0 <= z < cube_object.size
                    ):
                        voxel: Voxel = cube_object.grid[x, y, z]
                        voxel.is_visible = True
                        voxel.color = np.array([r, g, b, 1.0])

            print("Cena carregada com sucesso!")
        except Exception as e:
            print(f"Erro ao carregar: {e}")