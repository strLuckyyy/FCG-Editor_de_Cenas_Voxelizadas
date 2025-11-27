import numpy as np
from src.cube import Cube, Voxel

class SceneManager:
    def __init__(self, filename="grid_salva.txt"):
        self.filename = filename

    def save_scene(self, cube_object: Cube):
        """
        Lê a grid do cubo e salva no arquivo de texto.
        """
        print(f"Salvando cena em {self.filename}...")
        try:
            # 'w' = Write (Escrever/Sobrescrever)
            with open(self.filename, "w") as f:
                # Precisamos acessar os dados do cubo que foi passado como argumento
                for x in range(cube_object.size):
                    for y in range(cube_object.size):
                        for z in range(cube_object.size):
                            voxel: Voxel = cube_object.grid[x, y, z]
                            
                            # Só salvamos o que é visível para economizar espaço
                            if voxel and voxel.is_visible:
                                r, g, b, a = voxel.color
                                # Escrevemos uma linha no formato: X Y Z R G B
                                f.write(f"{x} {y} {z} {r} {g} {b}\n")
            print("Cena salva com sucesso!")
            
        except Exception as e:
            print(f"Erro ao salvar: {e}")

    def load_scene(self, cube_object: Cube):
        """
        Lê o arquivo de texto e modifica a grid do cubo.
        """
        print(f"Carregando cena de {self.filename}...")
        try:
            # 'r' = Read (Ler)
            with open(self.filename, "r") as f:
                # 1. Limpeza: Antes de carregar, apagamos o desenho atual
                cube_object.clear_scene()
                
                # 2. Leitura: Processamos linha por linha
                for line in f:
                    if not line.strip(): continue # Pula linhas vazias
                    
                    data = line.split() # Quebra a linha pelos espaços
                    
                    # Convertendo texto para números
                    x, y, z = int(data[0]), int(data[1]), int(data[2])
                    r, g, b = float(data[3]), float(data[4]), float(data[5])
                    
                    # Verificação de segurança (para não estourar a grid se o arquivo for de um tamanho diferente)
                    if 0 <= x < cube_object.size and 0 <= y < cube_object.size and 0 <= z < cube_object.size:
                        voxel: Voxel = cube_object.grid[x, y, z]
                        voxel.is_visible = True
                        voxel.color = np.array([r, g, b, 1.0])
                        
            print("Cena carregada com sucesso!")
            
        except FileNotFoundError:
            print("Arquivo de salvamento não encontrado. Salve algo primeiro!")
        except Exception as e:
            print(f"Erro ao carregar: {e}")