import pygetwindow as gw
import mss
import cv2
import numpy as np


# Função para capturar a janela do BlueStacks
def capturar_janela_bluestacks():
    # Procurar pela janela do BlueStacks
    janela = None
    for win in gw.getWindowsWithTitle('BlueStacks App Player'):
        janela = win
        break

    if janela is not None:
        # Obter a posição e tamanho da janela
        left, top, width, height = janela.left, janela.top, janela.width, janela.height

        # Capturar a área específica da janela usando mss
        with mss.mss() as sct:
            monitor = {"top": top, "left": left, "width": width, "height": height}
            screenshot = sct.grab(monitor)

            # Converter para um formato utilizável pelo OpenCV
            img = np.array(screenshot)

            # Converter de BGRA para RGB (mss captura em BGRA)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            img = img[:, :-30]

            # Exibir a captura para verificar
            cv2.imshow('BlueStacks Captura', img)

            return img
    else:
        print("Janela do BlueStacks não encontrada!")
        return None
def recorta_e_grid(img, x_inicio=12, y_inicio=365, largura_celula=68, altura_celula=57, colunas=10, linhas=10,
                       ajuste_x=-10, ajuste_y=-8):
    """
    Recorta e divide a área do grid em um array 2D de 10x10 células, ajustando a posição inicial.

    :param img: A imagem original (capturada).
    :param x_inicio: A coordenada X inicial do recorte.
    :param y_inicio: A coordenada Y inicial do recorte.
    :param largura_celula: A largura de cada célula no grid.
    :param altura_celula: A altura de cada célula no grid.
    :param colunas: Número de colunas no grid (default é 10).
    :param linhas: Número de linhas no grid (default é 10).
    :param ajuste_x: Ajuste para a posição X (default é -5 para mover para a esquerda).
    :param ajuste_y: Ajuste para a posição Y (default é -5 para mover para cima).
    :return: Um array 2D contendo as imagens de cada célula.
    """
    # Ajustar as coordenadas de início com base nos ajustes
    x_inicio += ajuste_x
    y_inicio += ajuste_y

    # Calcular o fim das coordenadas baseado no tamanho do grid (10x10)
    x_fim = x_inicio + colunas * largura_celula
    y_fim = y_inicio + linhas * altura_celula

    # Recortar a imagem para pegar apenas a área do grid
    grid_recortado = img[y_inicio:y_fim, x_inicio:x_fim]

    # Criar um array 2D para armazenar as imagens de cada célula
    grid_array = []

    for i in range(linhas):
        linha = []
        for j in range(colunas):
            # Definir os limites de cada célula (região de interesse)
            y_celula_inicio = i * altura_celula
            y_celula_fim = (i + 1) * altura_celula
            x_celula_inicio = j * largura_celula
            x_celula_fim = (j + 1) * largura_celula

            # Extrair a célula da imagem do grid
            celula = grid_recortado[y_celula_inicio:y_celula_fim, x_celula_inicio:x_celula_fim]

            # Adicionar a célula (imagem) à linha
            linha.append(celula)

        # Adicionar a linha ao array 2D
        grid_array.append(linha)

    return grid_array

def combinar_grid_em_imagem(grid_array):
    """
    Combina todas as células do grid em uma única imagem.

    :param grid_array: Um array 2D contendo as imagens de cada célula do grid.
    :return: Uma única imagem que contém todas as células do grid.
    """
    # Verificar se o grid não está vazio
    if not grid_array:
        return None

    # Combinar cada linha (células concatenadas horizontalmente)
    linhas_combinadas = [np.hstack(linha) for linha in grid_array]

    # Combinar todas as linhas (linhas concatenadas verticalmente)
    imagem_completa = np.vstack(linhas_combinadas)

    return imagem_completa


# Loop principal para capturar a tela do BlueStacks
while True:
    captura = capturar_janela_bluestacks()
    if captura is None:
        break  # Se a janela não for encontrada, encerra o loop

    grid_array = recorta_e_grid(captura)

    

    imagem_completa = combinar_grid_em_imagem(grid_array)

    if imagem_completa is not None:
        cv2.imshow('Imagem Completa do Grid', imagem_completa)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Grid não encontrado ou vazio.")

    # Pressione 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

if __name__ == '__main__':
    # Testar a função
    captura = capturar_janela_bluestacks()