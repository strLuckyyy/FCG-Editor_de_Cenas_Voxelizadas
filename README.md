# Trabalho Final - Fundamentos de Computação Gráfica
## Editor_de_Cenas_Voxelizadas

### Integrantes do Grupo:
- Abrahão Francis Gonçalves
- Marcos Vinicius de Oliveira Rocha

### Descrição do Projeto:
Este projeto implementa um Editor 3D de Cenas Voxelizadas, utilizando Python + OpenGL (PyOpenGL). O sistema permite:

- Visualizar uma grade 3D de voxels
- Adicionar ou remover voxels individualmente
- Pintar voxels com diferentes cores
- Selecionar voxels via raycasting
- Mover a câmera livremente em 3D (FPS-style)
- Salvar e carregar cenas em arquivos .txt
- Controlar espaçamento entre voxels
- Interface de mira (crosshair)

---------

## Como Executar
### 1. Pré-requisitos

Tecnologia|Versão
-----|----
Python | 3.12
glfw      |          2.10
numpy      |         2.3
pip         |        25.3
pygame       |       2.6
PyOpenGL      |      3.1
PyOpenGL-accelerate| 3.1
tk                  |0.1

Antes de rodar o programa, instale as dependências:
```
pip install PyOpenGL PyOpenGL_accelerate glfw numpy pygame tk
```

###### Alguns sistemas já vêm com Tk disponível.

### 2. Execução

Dentro da pasta do projeto, execute:
```
python main.py
```

Uma janela OpenGL será aberta com o editor.

----

## Controles do Editor
### Movimentação da Câmera:

|Tecla|Ação|
|-----|----|
|AWSD|Mover pelo espaço|
|Mouse|Controla direção da câmera|
|ESC|Fecha o programa|

### Edição de Voxels
A seleção é feita automaticamente via raycasting na direção da mira.

O voxel selecionado fica com destaque, ficando em com uma cor mais clara.

|Botão|Ação|
|-----|----|
|Esquerdo do mouse|Adicionar voxel|
|Direito do mouse|Remover voxel|

### Pintar Voxel Selecionado
|Tecla|Cor|
|-----|---|
|1|Vermelho|
|2|Verde|
|3|Azul|
|4|Amarelo|
|5|Branco|
##### As cores são inicialmente definidas aleatoriamente pelo programa

### Espaçamento dos Voxels
|Controle|Ação|
|--------|----|
|Scroll do mouse|Aumenta/diminui espaçamento da grade|

### Salvar e Carregar Cenas
|Tecla|Ação|
|-----|----|
|K|Salvar cena em arquivo .txt|
|L|Carregar cena de arquivo .txt|

Ao salvar ou carregar, abre-se o explorador de arquivos dentro da pasta saves, onde possibilita a criação e seleção dos saves de forma mais prática.

#### Formato salvo:
```
SIZE <grid_size>
SPACE <grid_space>
x y z r g b a  <- (posição e cores do voxel)
...
```

### Arquitetura do Projeto
Arquivo|Função
|------|-----|
main.py|**Inicializa** a janela e os objetos principais.
window.py|**Gerencia** a janela OpenGL, a câmera, os callbacks de teclado/mouse, os shaders, a renderização e a mira (crosshair).
object.py|**Trata do** cache de malhas e uniforms, inicialização do cubo e transformações (translação, rotação, escala).
cube.py|**Organiza e implementa** a grade de voxels, a seleção, adição/remoção e pintura, a colisão por raycasting, a renderização dos voxels, os efeitos visuais (wireframe em invisíveis, highlight em selecionado) e sons.
scene_manager.py|**Salva e carrega** cenas da grade voxel.
sound_manager.py|**Gerencia** o carregamento e "play" dos sons no programa