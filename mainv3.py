import os
import time

import pyautogui
import pygetwindow as gw
import mss
import cv2
import numpy as np
from skimage.metrics import structural_similarity
import pandas as pd

# Função para capturar a janela do BlueStacks
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
            y_celula_fim = (i + 1) * altura_celula - 2 if i == 0 else (i + 1) * altura_celula
            x_celula_inicio = j * largura_celula
            x_celula_fim = (j + 1) * largura_celula + 5 if j == 7 else (j + 1) * largura_celula
            celula = grid_recortado[y_celula_inicio:y_celula_fim, x_celula_inicio:x_celula_fim]
            imagem = get_name_of_celula(celula)
            linha_info.append(imagem)
            linha_possicoes.append(((x_celula_inicio, x_celula_fim), (y_celula_inicio, y_celula_fim)))
            linha.append(celula)
        grid_array.append(linha)
        info_array.append(linha_info)
        possicoes_array.append(linha_possicoes)

    i1, j1 = encontrar_interseccao(info_array, grid_array)

    if i1 is None or j1 is None:
        print("Não encontrado")
        return info_array, ultima_interseccao

    if (i1, j1) == ultima_interseccao:
        print(f"Já cliquei na interseção em {i1}, {j1}. Ignorando novo clique.")
        return info_array, ultima_interseccao

    print(f"Clicando em {i1}, {j1}")
    (x_celula_inicio, x_celula_fim), (y_celula_inicio, y_celula_fim) = possicoes_array[i1][j1]

    x_inicio_janela, y_inicio_janela = get_bluestacks_window_position()
    x_absoluto = x_inicio_janela + x_inicio + x_celula_inicio
    y_absoluto = y_inicio_janela + y_inicio + y_celula_inicio + 55
    largura_celula = x_celula_fim - x_celula_inicio
    altura_celula = y_celula_fim - y_celula_inicio

    clicar_no_centro_da_area_bluestacks(x_absoluto, y_absoluto, largura_celula, altura_celula)

    return info_array, (i1, j1)

def get_name_of_celula(celula_img, assets_dir='./assets'):
    """
    Verifica qual imagem no diretório de assets mais se assemelha à célula fornecida.

    :param celula_img: A imagem da célula a ser comparada.
    :param assets_dir: O diretório onde as imagens de referência estão armazenadas.
    :return: O nome do item que mais se assemelha à célula (por exemplo, 'pizza', 'bread').
    """
    melhor_similaridade = -1
    nome_melhor_celula = None

    cor1 = "E4D8C6"
    cor2 = "F7F1D6"

    if verificar_cor_predominante(celula_img, cor1) or verificar_cor_predominante(celula_img, cor2):
        return "NONE"

    # Iterar sobre todas as imagens no diretório de assets
    for filename in os.listdir(assets_dir):
        if filename.endswith('.png') or filename.endswith('.jpg'):
            # print("Arquivo: ", filename)
            # Carregar a imagem de referência
            caminho_imagem_referencia = os.path.join(assets_dir, filename)

            # Verificar se o arquivo existe
            if not os.path.exists(caminho_imagem_referencia):
                # print(f"Arquivo não encontrado: {caminho_imagem_referencia}")
                continue

            # Carregar a imagem de referência
            imagem_referencia = cv2.imread(caminho_imagem_referencia)

            # Verificar se a imagem foi carregada corretamente
            if imagem_referencia is None:
                # print(f"Erro ao carregar a imagem: {caminho_imagem_referencia}")
                continue

            # cv2.imshow("imagem_referencia", imagem_referencia)
            # cv2.imshow("celula_img", celula_img)
            #
            # cv2.waitKey(0)

            # Comparar a célula com a imagem de referência
            similaridade = calcular_similaridade_sem_fundo(celula_img, imagem_referencia)

            # print(f"{filename} - {similaridade}")

            # Se a similaridade atual for melhor, atualizar o melhor resultado
            if similaridade > melhor_similaridade:
                melhor_similaridade = similaridade
                nome_melhor_celula = filename.split('.')[0]  # Extrair o nome sem a extensão

    return nome_melhor_celula

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


def encontrar_interseccao(array2d, array_grid):
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
            if array2d[i][j] == 'NONE':
                # Verificar sequências horizontais e verticais
                pos_hor = verificar_sequencia_horizontal(array2d, i, j, colunas)
                pos_ver = verificar_sequencia_vertical(array2d, i, j, linhas)

                if pos_hor or pos_ver:
                    interseccao_pos = (i, j)
                    if pos_hor:
                        print(f"Interseção encontrada na posição {interseccao_pos} entre as posições {pos_hor}")
                        posImg1, posImg2 = pos_hor
                        posImgI1, posImgJ1 = posImg1
                        posImgI2, posImgJ2 = posImg2
                        img1 = array_grid[posImgI1][posImgJ1]
                        img2 = array_grid[posImgI2][posImgJ2]


                        if calcular_similaridade_sem_fundo(img1, img2) < 0.5:
                            print(f"Similaridade muito baixa {calcular_similaridade_sem_fundo(img1, img2)}")
                            continue

                    if pos_ver:
                        vposImg1, vposImg2 = pos_ver
                        vposImgI1, vposImgJ1 = vposImg1
                        vposImgI2, vposImgJ2 = vposImg2
                        vimg1 = array_grid[vposImgI1][vposImgJ1]
                        vimg2 = array_grid[vposImgI2][vposImgJ2]


                        if calcular_similaridade_sem_fundo(vimg1, vimg2) < 0.5:
                            print(f"Similaridade muito baixa {calcular_similaridade_sem_fundo(vimg1, vimg2)}")
                            continue
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
    while esquerda >= 0 and array2d[i][esquerda] == 'NONE':
        esquerda -= 1

    # Procurar a primeira imagem à direita da sequência de NONE
    direita = j + 1
    while direita < colunas and array2d[i][direita] == 'NONE':
        direita += 1

    # Verificar se as imagens em esquerda e direita são iguais e não são 'NONE'
    if esquerda >= 0 and direita < colunas and array2d[i][esquerda] == array2d[i][direita] and array2d[i][
        esquerda] != 'NONE':
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
    while acima >= 0 and array2d[acima][j] == 'NONE':
        acima -= 1

    # Procurar a primeira imagem abaixo da sequência de NONE
    abaixo = i + 1
    while abaixo < linhas and array2d[abaixo][j] == 'NONE':
        abaixo += 1

    # Verificar se as imagens em acima e abaixo são iguais e não são 'NONE'
    if acima >= 0 and abaixo < linhas and array2d[acima][j] == array2d[abaixo][j] and array2d[acima][j] != 'NONE':
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

def calcular_similaridade_sem_fundo(imagem1, imagem2, cor_fundo1=(228, 216, 196), cor_fundo2=(247, 241, 214)):
    """
    Compara duas imagens onde uma delas pode ter fundo e a outra não, focando no formato e nas cores presentes.
    A função remove o fundo baseado em duas possíveis cores de fundo.

    :param imagem1: A primeira imagem (BGR) que pode ter fundo.
    :param imagem2: A segunda imagem (BGR) que está sem fundo.
    :param cor_fundo1: Primeira cor do fundo que deve ser removida (default é "#E4D8C6").
    :param cor_fundo2: Segunda cor do fundo que deve ser removida (default é "#F7F1D6").
    :return: Um valor entre 0 e 1 representando a similaridade (1 é idêntico, 0 é totalmente diferente).
    """
    # Redimensionar imagens para o menor tamanho comum
    if imagem1.shape != imagem2.shape:
        altura_min = min(imagem1.shape[0], imagem2.shape[0])
        largura_min = min(imagem1.shape[1], imagem2.shape[1])
        imagem1 = cv2.resize(imagem1, (largura_min, altura_min), interpolation=cv2.INTER_AREA)
        imagem2 = cv2.resize(imagem2, (largura_min, altura_min), interpolation=cv2.INTER_AREA)

    # Converter as cores de fundo para o formato BGR (já estão no formato BGR na definição)
    cor_fundo1 = np.array(cor_fundo1, dtype=np.uint8)
    cor_fundo2 = np.array(cor_fundo2, dtype=np.uint8)

    # Criar máscaras para as duas cores de fundo
    mask_fundo1 = cv2.inRange(imagem1, cor_fundo1, cor_fundo1)
    mask_fundo2 = cv2.inRange(imagem1, cor_fundo2, cor_fundo2)

    # Combinar as duas máscaras
    mask_fundo = cv2.bitwise_or(mask_fundo1, mask_fundo2)

    # Inverter a máscara para obter apenas os objetos (sem o fundo)
    mask_fundo_inv = cv2.bitwise_not(mask_fundo)

    # Aplicar a máscara na imagem para remover o fundo
    imagem1_sem_fundo = cv2.bitwise_and(imagem1, imagem1, mask=mask_fundo_inv)

    # Inicializar uma lista para armazenar as similaridades de cada canal
    similaridades_hist = []

    # Comparar histograma de cada canal de cor B, G e R usando a métrica de Chi-square
    for i in range(3):
        # Calcular o histograma apenas nas áreas que não são de fundo
        hist1 = cv2.calcHist([imagem1_sem_fundo], [i], mask_fundo_inv, [256], [0, 256])
        hist2 = cv2.calcHist([imagem2], [i], None, [256], [0, 256])

        # Normalizar os histogramas
        hist1 = cv2.normalize(hist1, hist1)
        hist2 = cv2.normalize(hist2, hist2)

        # Comparar histogramas usando Chi-square (métrica alternativa à correlação)
        similaridade_hist = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)
        similaridades_hist.append(similaridade_hist)

    # Tirar a média da similaridade dos canais de cor (invertendo o Chi-square para que um valor menor seja melhor)
    similaridade_hist_media = 1 / (1 + np.mean(similaridades_hist))

    # Converter as imagens para escala de cinza para usar SSIM, aplicando a máscara também
    imagem1_gray = cv2.cvtColor(imagem1_sem_fundo.astype(np.uint8), cv2.COLOR_BGR2GRAY)
    imagem2_gray = cv2.cvtColor(imagem2.astype(np.uint8), cv2.COLOR_BGR2GRAY)

    # Aplicar a máscara também na versão em escala de cinza da imagem com fundo
    imagem1_gray = cv2.bitwise_and(imagem1_gray, imagem1_gray, mask=mask_fundo_inv)

    # Calcular o SSIM entre as duas imagens em escala de cinza
    similaridade_ssim, _ = structural_similarity(imagem1_gray, imagem2_gray, full=True)

    # Combinar as duas similaridades (70% de peso para histogramas e 30% para SSIM)
    similaridade_final = (0.7 * similaridade_hist_media) + (0.3 * similaridade_ssim)

    return similaridade_final

if __name__ == '__main__':
    ultima_interseccao = None

    while True:
        captura = capturar_janela_bluestacks()

        if captura is not None:
            # Recortar e dividir o grid em células, retornando também a última interseção
            grid_array, ultima_interseccao = transform_to_array(captura, ultima_interseccao)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
