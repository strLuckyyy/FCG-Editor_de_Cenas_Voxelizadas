'''
Objetivo

Desenvolver um protótipo de editor de cenas voxelizadas, aplicando os conceitos abordados em aula. Para o Grau B, serão explorados os conhecimentos sobre câmera sintética e OpenGL.

Instruções de desenvolvimento:

O programa deve atender, no mínimo, aos seguintes requisitos:
* Criação e utilização corretas dos buffers (VAO, VBO(s));
* Utilização adequada das transformações de câmera e de objetos:
    * Quando, como e por que as matrizes de view e projection são atualizadas?
    * Como são realizadas e atualizadas as transformações nos objetos da cena?
* Gerenciamento dos voxels: estrutura de dados (a grid pode ter tamanho fixo) e lógica para inserção e deleção;
* Controle de movimentação (via teclado e/ou mouse), permitindo navegar pela grid e inserir ou apagar voxels;
* Paleta de cores para definir a cor do voxel (pode ser pequena; o controle pode ser feito por teclado ou mouse);
* Salvamento e carregamento de cenas. Sugere-se um formato de arquivo texto simples.

EXTRAS (opcionais, mas acrescentam nota extra):
* Voxels com textura
* HUDs com texto
* Som
* Seleção com mouse
* Otimizações

Apresentação e entrega

A apresentação será realizada em aula virtual. É essencial que todos os integrantes compreendam a estrutura do código (classes, funções, decisões de implementação).

Durante a apresentação, devem ser abordados os seguintes pontos:
* Apresentação do grupo (nomes dos integrantes);
* Estrutura geral do código (classes e/ou funções);
* Estrutura dos buffers e shaders (como os vértices e seus atributos são definidos e enviados aos shaders);
* Gerenciamento dos voxels: armazenamento de transformações, cores e demais informações;
* Inserção e deleção de voxels;
* Demonstração do programa em funcionamento
    * Sugestão: realizar a demonstração logo após a introdução. Caso necessário, mostrá-la novamente ao longo da explicação.

Observações:
* Trabalho individual ou em grupos de até 3 participantes;
* Entrega até 29/11/2025, via Moodle;

Apenas um integrante do grupo deve enviar o projeto contendo:
* O código-fonte completo;
* Um arquivo README.md com:
    * Nomes completos dos integrantes;
    * Instruções de uso do programa.
'''
import random
from cube import Cube
from window import Window

# variables and objects
win = Window()
cube = Cube(grid_size=5)

# definindo o objeto cubo como alvo para acessar seus atributos na window
win.target_cube = cube

if __name__ == "__main__":
    win.openGLInit("Editor de Cenas Voxelizadas")
    cube.draw()
    win.shaderInit()
    win.renderInit([cube])