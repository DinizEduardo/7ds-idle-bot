import time

import cv2
import mss
import numpy as np
import pyautogui
import pygetwindow as gw

from ai.clicar import clicar_no_centro_da_area_bluestacks
from ai.identificar_grid import transform_to_array
from ai.identificar_interseccao import encontrar_interseccao, encontrar_uma_interseccao
from ai.image_classifier import descobrir_imagem
from ai.prepare_data import get_model

model = get_model()


def capturar_janela_bluestacks():
    janela = None
    for win in gw.getWindowsWithTitle('BlueStacks App Player'):
        janela = win
        break

    if janela is not None:
        left, top, width, height = janela.left, janela.top, janela.width, janela.height
        with mss.mss() as sct:
            monitor = {"top": top, "left": left, "width": width, "height": height}
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            img = img[:, :-50]
            return img
    else:
        print("Janela do BlueStacks não encontrada!")
        return None


def combinar_grid_em_imagem(grid_array, info_array):
    """
    Combina todas as células do grid em uma única imagem com 5px de espaço ao redor de cada célula
    e adiciona a posição da célula (como "0,0", "0,1", etc.) em cada uma.

    :param grid_array: Um array 2D contendo as imagens de cada célula do grid.
    :return: Uma única imagem que contém todas as células do grid com a posição anotada.
    """
    # Verificar se o grid não está vazio
    if not grid_array:
        return None

    # Definir o tamanho do espaçamento (5px em todos os lados)
    padding = 5

    # Adicionar o espaçamento de 5px em torno de cada célula e adicionar a posição
    grid_com_padding = []
    for i, linha in enumerate(grid_array):
        linha_com_padding = []
        for j, celula in enumerate(linha):
            # Adicionar o padding em torno da célula
            celula_com_padding = cv2.copyMakeBorder(
                celula,
                padding, padding, padding, padding,  # top, bottom, left, right
                cv2.BORDER_CONSTANT,
                value=[255, 255, 255]  # Cor do padding (branco)
            )

            # Definir a posição para o texto (canto superior esquerdo)
            posicao_texto = (padding + 10, padding + 30)  # Ajustar conforme necessário

            # Adicionar o texto da posição da célula (i, j)
            texto = f"{info_array[i][j]}"
            cv2.putText(
                celula_com_padding, texto, posicao_texto,
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA
            )

            linha_com_padding.append(celula_com_padding)
        grid_com_padding.append(linha_com_padding)

    # Combinar cada linha (células concatenadas horizontalmente)
    linhas_combinadas = [np.hstack(linha) for linha in grid_com_padding]

    # Combinar todas as linhas (linhas concatenadas verticalmente)
    imagem_completa = np.vstack(linhas_combinadas)

    return imagem_completa


def processar_fase():
    largura_celula = 67
    altura_celula = 57
    ultima_interseccao = None

    print("Identificando imagens...")
    captura = capturar_janela_bluestacks()
    grid_array, info_array, possicoes_array = None, None, None

    if captura is not None:
        # grid_array -> grid com imagens
        # info_array -> grid com texto de cada imagem
        # possicoes_array -> possicao de cada celula no bluestacks
        grid_array, info_array, possicoes_array = transform_to_array(captura,
                                                                     model)  # fazer verificarção de fase dentro do while
        imagem_completa = combinar_grid_em_imagem(grid_array, info_array)

        # Exibir a imagem completa com as interseções marcadas
        if imagem_completa is not None:
            cv2.imshow('Imagem Completa com Interseções', imagem_completa)
        else:
            print("Grid não encontrado ou vazio.")

    while True:
        captura = capturar_janela_bluestacks()

        if captura is not None:
            # Combinar o grid em uma única imagem

            interseccao_pos, info_array = encontrar_uma_interseccao(info_array, ultima_interseccao)

            i, j = interseccao_pos

            if i is None or j is None:
                return

            ((x_celula_inicio, x_celula_fim), (y_celula_inicio, y_celula_fim)) = possicoes_array[i][j]

            clicar_no_centro_da_area_bluestacks(x_celula_inicio, y_celula_fim, largura_celula, altura_celula)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break  # Encerra o jogo se a tecla 'q' for pressionada
        elif cv2.waitKey(10) & 0x4E == ord('n'):
            print("Reiniciando a fase...")
            return  # Retorna para reiniciar o processo



if __name__ == '__main__':
    print("Inicio")
    clicar_no_centro_da_area_bluestacks(100, 550, 30, 30)
    #
    time.sleep(3)

    while True:
        processar_fase()
