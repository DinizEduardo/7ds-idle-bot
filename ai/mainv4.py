import time

import cv2
import mss
import numpy as np
import pyautogui
import pygetwindow as gw

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


def transform_to_array(captura, ultima_interseccao=None):
    x_inicio = 13
    y_inicio = 368
    largura_celula = 67
    altura_celula = 57
    colunas = 8
    linhas = 10
    ajuste_x = 0
    ajuste_y = -8

    x_inicio += ajuste_x
    y_inicio += ajuste_y

    x_fim = x_inicio + colunas * largura_celula
    y_fim = y_inicio + linhas * altura_celula

    grid_recortado = captura[y_inicio:y_fim, x_inicio:x_fim - 5]
    grid_array = []
    info_array = []
    possicoes_array = []

    for i in range(linhas):
        linha = []
        linha_info = []
        linha_possicoes = []
        for j in range(colunas):
            y_celula_inicio = i * altura_celula
            y_celula_fim = (i + 1) * altura_celula # if i == 0 else (i + 1) * altura_celula
            x_celula_inicio = j * largura_celula
            x_celula_fim = (j + 1) * largura_celula # if j == 7 else (j + 1) * largura_celula
            celula = grid_recortado[y_celula_inicio:y_celula_fim, x_celula_inicio:x_celula_fim]

            imagem = descobrir_imagem(celula, model)

            linha_info.append(imagem)
            linha_possicoes.append(((x_celula_inicio, x_celula_fim), (y_celula_inicio, y_celula_fim)))
            linha.append(celula)
        grid_array.append(linha)
        info_array.append(linha_info)
        possicoes_array.append(linha_possicoes)

    i1, j1 = encontrar_interseccao(info_array, grid_array, ultima_interseccao)

    if i1 is None or j1 is None:
        print("Não encontrado")
        return grid_array, ultima_interseccao

    if (i1, j1) == ultima_interseccao:
        print(f"Já cliquei na interseção em {i1}, {j1}. Ignorando novo clique.")
        return grid_array, ultima_interseccao

    print(f"Clicando em {i1}, {j1}")
    (x_celula_inicio, x_celula_fim), (y_celula_inicio, y_celula_fim) = possicoes_array[i1][j1]

    x_inicio_janela, y_inicio_janela = get_bluestacks_window_position()
    x_absoluto = x_inicio_janela + x_inicio + x_celula_inicio
    y_absoluto = y_inicio_janela + y_inicio + y_celula_inicio
    largura_celula = x_celula_fim - x_celula_inicio
    altura_celula = y_celula_fim - y_celula_inicio

    clicar_no_centro_da_area_bluestacks(x_absoluto, y_absoluto, largura_celula, altura_celula)

    return grid_array, (11, 11)


def encontrar_interseccao(array2d, array_grid, ultima_interseccao):
    """
    Encontra a interseção marcada como 'NONE' em que duas imagens iguais estejam conectadas por uma sequência de 'NONE'.
    Verifica tanto na horizontal quanto na vertical.

    :param array2d: Array 2D contendo as imagens e interseções (marcadas como 'NONE').
    :return: A posição da interseção encontrada e as posições das duas imagens iguais.
    """
    linhas = len(array2d)
    colunas = len(array2d[0])

    for i in range(linhas):
        for j in range(colunas):
            if array2d[i][j] == 'none':
                # Verificar sequências horizontais e verticais
                pos_hor = verificar_sequencia_horizontal(array2d, i, j, colunas)
                pos_ver = verificar_sequencia_vertical(array2d, i, j, linhas)

                if pos_hor or pos_ver:
                    interseccao_pos = (i, j)
                    if interseccao_pos == ultima_interseccao:
                        continue

                    if pos_hor:
                        print(f"Interseção encontrada na posição {interseccao_pos} entre as posições {pos_hor}")
                        posImg1, posImg2 = pos_hor
                        posImgI1, posImgJ1 = posImg1
                        posImgI2, posImgJ2 = posImg2
                        img1 = array_grid[posImgI1][posImgJ1]
                        img2 = array_grid[posImgI2][posImgJ2]


                        # if calcular_similaridade_sem_fundo(img1, img2) < 0.5:
                        #     print(f"Similaridade muito baixa {calcular_similaridade_sem_fundo(img1, img2)}")
                        #     continue

                    if pos_ver:
                        vposImg1, vposImg2 = pos_ver
                        vposImgI1, vposImgJ1 = vposImg1
                        vposImgI2, vposImgJ2 = vposImg2
                        vimg1 = array_grid[vposImgI1][vposImgJ1]
                        vimg2 = array_grid[vposImgI2][vposImgJ2]


                        # if calcular_similaridade_sem_fundo(vimg1, vimg2) < 0.5:
                        #     print(f"Similaridade muito baixa {calcular_similaridade_sem_fundo(vimg1, vimg2)}")
                        #     continue
                        print(f"Interseção encontrada na posição {interseccao_pos} entre as posições {pos_ver}")
                    return interseccao_pos

    return None, None


def verificar_sequencia_horizontal(array2d, i, j, colunas):
    """
    Verifica se há uma sequência horizontal de 'NONE' com duas imagens iguais nas extremidades e retorna suas posições.

    :param array2d: Array 2D com as imagens.
    :param i: Índice da linha atual.
    :param j: Índice da coluna atual.
    :param colunas: Número de colunas no array.
    :return: As posições das duas imagens que conectam a sequência de NONE, ou None se não houver.
    """
    # Procurar a primeira imagem à esquerda da sequência de NONE
    esquerda = j - 1
    while esquerda >= 0 and array2d[i][esquerda] == 'none':
        esquerda -= 1

    # Procurar a primeira imagem à direita da sequência de NONE
    direita = j + 1
    while direita < colunas and array2d[i][direita] == 'none':
        direita += 1

    # Verificar se as imagens em esquerda e direita são iguais e não são 'NONE'
    if esquerda >= 0 and direita < colunas and array2d[i][esquerda] == array2d[i][direita] and array2d[i][
        esquerda] != 'none':
        return ((i, esquerda), (i, direita))  # Retornar as posições das duas imagens

    return None


def verificar_sequencia_vertical(array2d, i, j, linhas):
    """
    Verifica se há uma sequência vertical de 'NONE' com duas imagens iguais nas extremidades e retorna suas posições.

    :param array2d: Array 2D com as imagens.
    :param i: Índice da linha atual.
    :param j: Índice da coluna atual.
    :param linhas: Número de linhas no array.
    :return: As posições das duas imagens que conectam a sequência de NONE, ou None se não houver.
    """
    # Procurar a primeira imagem acima da sequência de NONE
    acima = i - 1
    while acima >= 0 and array2d[acima][j] == 'none':
        acima -= 1

    # Procurar a primeira imagem abaixo da sequência de NONE
    abaixo = i + 1
    while abaixo < linhas and array2d[abaixo][j] == 'none':
        abaixo += 1

    # Verificar se as imagens em acima e abaixo são iguais e não são 'NONE'
    if acima >= 0 and abaixo < linhas and array2d[acima][j] == array2d[abaixo][j] and array2d[acima][j] != 'none':
        return ((acima, j), (abaixo, j))  # Retornar as posições das duas imagens

    return None


def verificar_cor_predominante(celula, cor_hex, tolerancia=30):
    """
    Verifica se pelo menos 70% da célula está próxima da cor fornecida.

    :param celula: A imagem da célula (em BGR).
    :param cor_hex: A cor de referência em formato HEX (string).
    :param tolerancia: A tolerância de cor para considerar o pixel como uma correspondência.
    :return: True se pelo menos 70% dos pixels corresponderem à cor, False caso contrário.
    """
    # Converter cor de HEX para BGR
    cor_rgb = tuple(int(cor_hex[i:i + 2], 16) for i in (0, 2, 4))
    cor_bgr = (cor_rgb[2], cor_rgb[1], cor_rgb[0])  # OpenCV usa BGR

    # Contar quantos pixels estão dentro da tolerância de cor
    total_pixels = celula.shape[0] * celula.shape[1]
    pixels_correspondentes = np.sum(np.all(np.abs(celula - cor_bgr) <= tolerancia, axis=-1))

    # Verificar se pelo menos 70% dos pixels correspondem à cor
    return (pixels_correspondentes / total_pixels) >= 0.7

def get_bluestacks_window_position(nome_janela='BlueStacks'):
    try:
        janela = gw.getWindowsWithTitle(nome_janela)[0]
    except IndexError:
        return None

    if janela.isMinimized:
        janela.restore()

    return janela.left, janela.top


def clicar_no_centro_da_area_bluestacks(x_inicio, y_fim, largura, altura, nome_janela='BlueStacks App Player'):
    try:
        janela = gw.getWindowsWithTitle(nome_janela)[0]
    except IndexError:
        return

    if janela.isMinimized:
        janela.restore()

    x_janela, y_janela = janela.left, janela.top
    centro_x = x_janela + x_inicio + largura // 2
    centro_y = y_janela + y_fim - altura // 2
    # time.sleep(2)
    pyautogui.moveTo(centro_x, centro_y)
    pyautogui.click()

def combinar_grid_em_imagem(grid_array):
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
            texto = f"{i},{j}"
            cv2.putText(
                celula_com_padding, texto, posicao_texto,
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2, cv2.LINE_AA
            )

            linha_com_padding.append(celula_com_padding)
        grid_com_padding.append(linha_com_padding)

    # Combinar cada linha (células concatenadas horizontalmente)
    linhas_combinadas = [np.hstack(linha) for linha in grid_com_padding]

    # Combinar todas as linhas (linhas concatenadas verticalmente)
    imagem_completa = np.vstack(linhas_combinadas)

    return imagem_completa


if __name__ == '__main__':
    ultima_interseccao = None
    print("Inicio")
    # clicar_no_centro_da_area_bluestacks(100, 550, 30, 30)

    # time.sleep(4)

    while True:
        captura = capturar_janela_bluestacks()

        if captura is not None:
            # Recortar e dividir o grid em células, retornando também a última interseção
            grid_array, ultima_interseccao = transform_to_array(captura, ultima_interseccao)

            # Combinar o grid em uma única imagem
            imagem_completa = combinar_grid_em_imagem(grid_array)

            # Exibir a imagem completa com as interseções marcadas
            if imagem_completa is not None:
                cv2.imshow('Imagem Completa com Interseções', imagem_completa)
            else:
                print("Grid não encontrado ou vazio.")

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
