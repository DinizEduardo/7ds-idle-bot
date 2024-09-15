import pygetwindow as gw
import mss
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim, structural_similarity


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

            img = img[:, :-50]

            # Exibir a captura para verificar
            cv2.imshow('BlueStacks Captura', img)

            return img
    else:
        print("Janela do BlueStacks não encontrada!")
        return None


def recortar_area_grid(img, x_inicio=13, y_inicio=368, largura_celula=67, altura_celula=57, colunas=10, linhas=10,
                       ajuste_x=0, ajuste_y=-8):
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
    grid_recortado = img[y_inicio:y_fim, x_inicio:x_fim - 10]

    # Criar um array 2D para armazenar as imagens de cada célula
    grid_array = []

    for i in range(linhas):
        linha = []
        for j in range(colunas):
            # Definir os limites de cada célula (região de interesse)
            if i == 0:
                y_celula_inicio = i * altura_celula
                y_celula_fim = (i + 1) * altura_celula -2
            else:
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


def aplicar_opacidade(celula, opacidade=0.25):
    """
    Aplica opacidade a uma imagem de célula.

    :param celula: A imagem da célula (em BGR).
    :param opacidade: O nível de opacidade (0.25 significa 25% de visibilidade).
    :return: A imagem da célula com a opacidade aplicada.
    """
    # Criar uma imagem preta (fundo) do mesmo tamanho que a célula
    fundo = np.zeros_like(celula)

    # Misturar a célula com o fundo usando a opacidade fornecida
    celula_opaca = cv2.addWeighted(celula, opacidade, fundo, 1 - opacidade, 0)

    return celula_opaca


def identificar_intersecoes_e_aplicar_opacidade(grid_array):
    """
    Identifica interseções no grid e aplica opacidade nas células que formam interseção,
    caso as células sejam predominantemente de uma cor específica.

    :param grid_array: O array 2D contendo as imagens do grid.
    :return: O grid modificado com as interseções marcadas com opacidade.
    """
    tamanho_grid = len(grid_array)

    # Cores de referência em HEX
    cor1 = "E4D8C6"
    cor2 = "F7F1D6"

    # Lista para armazenar as posições das células que podem ser clicadas
    posicoes_pode_clicar = []

    # Iterar sobre cada célula do grid
    for i in range(tamanho_grid):
        for j in range(tamanho_grid):
            celula_atual = grid_array[i][j]

            # Verificar se a célula atual corresponde à cor
            if celula_atual is not None:
                if verificar_cor_predominante(celula_atual, cor1) or verificar_cor_predominante(celula_atual, cor2):
                    # print(i, ",", j, " -> Pode Clicar")
                    posicoes_pode_clicar.append((i, j))
                # else:
                # print(i, ",", j, " -> Não Clicar")

    novo_grid = identificar_interceccoes(grid_array, posicoes_pode_clicar)

    # for celula in novo_grid:
    #     print("Posição", celula)

    return novo_grid


def identificar_interceccoes(grid_array, posicoes_pode_clicar):
    novo_grid_array = grid_array

    for pos in posicoes_pode_clicar:
        posI, posJ = pos
        minI = 0
        maxI = 9  # 10
        minJ = 0
        maxJ = 7  # 8

        posIAtual, posJAtual = posI, posJ

        opcaoIPlus, opcaoIMinus, opcaoJPlus, opcaoJMinus = None, None, None, None
        posIPlus, posIMinus, posJPlus, posJMinus = None, None, None, None
        # i -> Linha
        # j -> Coluna

        # Verificar para opcaoIPlus (linha +)
        posIAtual, posJAtual = posI, posJ
        posIAtual += 1
        while minI <= posIAtual <= maxI:
            if not (posIAtual, posJAtual) in posicoes_pode_clicar:
                opcaoIPlus = grid_array[posIAtual][posJAtual]
                posIPlus = (posIAtual, posJAtual)
                break
            posIAtual += 1

        # Verificar para opcaoIMinus (linha -)
        posIAtual, posJAtual = posI, posJ
        posIAtual -= 1
        while minI <= posIAtual <= maxI:
            if not (posIAtual, posJAtual) in posicoes_pode_clicar:
                opcaoIMinus = grid_array[posIAtual][posJAtual]
                posIMinus = (posIAtual, posJAtual)
                break
            posIAtual -= 1

        # Verificar para opcaoJPlus (coluna +)
        posIAtual, posJAtual = posI, posJ
        posJAtual += 1
        while minJ <= posJAtual <= maxJ:
            if not (posIAtual, posJAtual) in posicoes_pode_clicar:
                opcaoJPlus = grid_array[posIAtual][posJAtual]
                posJPlus = (posIAtual, posJAtual)
                break
            posJAtual += 1

        # Verificar para opcaoJMinus (coluna -)
        posIAtual, posJAtual = posI, posJ
        posJAtual -= 1
        while minJ <= posJAtual <= maxJ:
            if not (posIAtual, posJAtual) in posicoes_pode_clicar:
                opcaoJMinus = grid_array[posIAtual][posJAtual]
                posJMinus = (posIAtual, posJAtual)
                break
            posJAtual -= 1

        if comparar_e_escrever(posIPlus, posIMinus, grid_array, novo_grid_array, posI, posJ):
            continue
        if comparar_e_escrever(posIPlus, posJMinus, grid_array, novo_grid_array, posI, posJ):
            continue
        if comparar_e_escrever(posIPlus, posJPlus, grid_array, novo_grid_array, posI, posJ):
            continue

        if comparar_e_escrever(posJPlus, posIMinus, grid_array, novo_grid_array, posI, posJ):
            continue
        if comparar_e_escrever(posJPlus, posJMinus, grid_array, novo_grid_array, posI, posJ):
            continue

        if comparar_e_escrever(posIMinus, posJMinus, grid_array, novo_grid_array, posI, posJ):
            continue

    return novo_grid_array


def comparar_e_escrever(pos1, pos2, grid_array, novo_grid_array, posI, posJ):
    if pos1 is None or pos2 is None:
        return False
    i1, j1 = pos1
    i2, j2 = pos2
    opcao1 = grid_array[i1][j1]
    opcao2 = grid_array[i2][j2]
    if opcao1 is not None and opcao2 is not None:
        similaridade = calcular_similaridade(opcao1, opcao2)
        if similaridade >= 0.79:
            texto = f"{posI},{posJ}-({i1},{j1}),({i2},{j2})"
            print(texto, " -> Similaridade: ", similaridade)

            escrever_texto_no_grid(novo_grid_array, (posI, posJ), texto)
            return True

    return False


def escrever_texto_no_grid(grid_array, pos, texto):
    """
    Escreve um texto em uma célula do grid_array.

    :param grid_array: O array 2D contendo as imagens do grid.
    :param pos: A posição (i, j) da célula onde o texto será escrito.
    :param texto: O texto a ser escrito na célula.
    :return: O grid_array com o texto adicionado à célula.
    """
    posI, posJ = pos  # Posição da célula no grid

    # Obter a célula onde o texto será escrito
    celula = grid_array[posI][posJ]

    # Definir a posição do texto na célula
    posicao_texto = (10, 30)  # Posição inicial do texto (ajuste conforme necessário)

    # Definir a fonte, tamanho e cor do texto
    fonte = cv2.FONT_HERSHEY_SIMPLEX
    tamanho_fonte = 0.25
    cor = (0, 0, 0)  # Cor verde (BGR)
    espessura = 1

    # Escrever o texto na célula
    cv2.putText(celula, texto, posicao_texto, fonte, tamanho_fonte, cor, espessura, cv2.LINE_AA)

    # Atualizar o grid_array com a célula modificada
    grid_array[posI][posJ] = celula

    return grid_array


def calcular_similaridade(imagem1, imagem2):
    """
    Compara duas imagens usando histograma de cor e SSIM, ignorando o fundo,
    e retorna a similaridade combinada entre elas.

    :param imagem1: A primeira imagem (BGR).
    :param imagem2: A segunda imagem (BGR).
    :return: Um valor entre 0 e 1 representando a similaridade (1 é idêntico, 0 é totalmente diferente).
    """

    # Verificar se ambas as imagens têm o mesmo tamanho
    if imagem1.shape != imagem2.shape:
        return 0.0

    # Converter as cores de fundo do formato hexadecimal para BGR
    cor_fundo_1 = np.array([198, 216, 228], dtype=np.uint8)  # "#E4D8C6" em BGR
    cor_fundo_2 = np.array([214, 241, 247], dtype=np.uint8)  # "#F7F1D6" em BGR

    # Criar máscaras para ignorar as cores de fundo
    mask1 = cv2.inRange(imagem1, cor_fundo_1, cor_fundo_1) | cv2.inRange(imagem1, cor_fundo_2, cor_fundo_2)
    mask2 = cv2.inRange(imagem2, cor_fundo_1, cor_fundo_1) | cv2.inRange(imagem2, cor_fundo_2, cor_fundo_2)

    # Inverter as máscaras (fundo é 0, o resto é 1)
    mask1_inv = cv2.bitwise_not(mask1)
    mask2_inv = cv2.bitwise_not(mask2)

    # Aplicar as máscaras para remover o fundo (mantendo apenas os objetos)
    imagem1 = cv2.bitwise_and(imagem1, imagem1, mask=mask1_inv)
    imagem2 = cv2.bitwise_and(imagem2, imagem2, mask=mask2_inv)

    # Converter para o formato de float para precisão nas operações
    imagem1 = imagem1.astype(np.float32)
    imagem2 = imagem2.astype(np.float32)

    # Inicializar uma lista para armazenar as similaridades de cada canal
    similaridades_hist = []

    # Comparar histograma de cada canal de cor B, G e R
    for i in range(3):
        hist1 = cv2.calcHist([imagem1], [i], None, [256], [0, 256])
        hist2 = cv2.calcHist([imagem2], [i], None, [256], [0, 256])

        # Normalizar os histogramas
        hist1 = cv2.normalize(hist1, hist1)
        hist2 = cv2.normalize(hist2, hist2)

        # Comparar histogramas usando correlação
        similaridade_hist = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        similaridades_hist.append(similaridade_hist)

    # Tirar a média da similaridade dos canais de cor
    similaridade_hist_media = np.mean(similaridades_hist)

    # Converter as imagens para escala de cinza para usar SSIM
    imagem1_gray = cv2.cvtColor(imagem1.astype(np.uint8), cv2.COLOR_BGR2GRAY)
    imagem2_gray = cv2.cvtColor(imagem2.astype(np.uint8), cv2.COLOR_BGR2GRAY)

    # Aplicar as máscaras também nas versões em escala de cinza
    imagem1_gray = cv2.bitwise_and(imagem1_gray, imagem1_gray, mask=mask1_inv)
    imagem2_gray = cv2.bitwise_and(imagem2_gray, imagem2_gray, mask=mask2_inv)

    # Calcular o SSIM entre as duas imagens em escala de cinza
    similaridade_ssim, _ = structural_similarity(imagem1_gray, imagem2_gray, full=True)

    # Combinar as duas similaridades (peso ajustado: 70% histograma, 30% SSIM)
    similaridade_final = (0.7 * similaridade_hist_media) + (0.3 * similaridade_ssim)

    return similaridade_final


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


# Função para combinar as células em uma única imagem (mesma função de antes)
def combinar_grid_em_imagem(grid_array):
    """
    Combina todas as células do grid em uma única imagem com 5px de espaço ao redor de cada célula.

    :param grid_array: Um array 2D contendo as imagens de cada célula do grid.
    :return: Uma única imagem que contém todas as células do grid.
    """
    # Verificar se o grid não está vazio
    if not grid_array:
        return None

    # Definir o tamanho do espaçamento (5px em todos os lados)
    padding = 5

    # Adicionar o espaçamento de 5px em torno de cada célula
    grid_com_padding = []
    for linha in grid_array:
        linha_com_padding = []
        for celula in linha:
            celula_com_padding = cv2.copyMakeBorder(
                celula,
                padding, padding, padding, padding,  # top, bottom, left, right
                cv2.BORDER_CONSTANT,
                value=[255, 255, 255]  # Cor do padding (branco)
            )
            linha_com_padding.append(celula_com_padding)
        grid_com_padding.append(linha_com_padding)

    # Combinar cada linha (células concatenadas horizontalmente)
    linhas_combinadas = [np.hstack(linha) for linha in grid_com_padding]

    # Combinar todas as linhas (linhas concatenadas verticalmente)
    imagem_completa = np.vstack(linhas_combinadas)

    return imagem_completa


if __name__ == '__main__':
    # Exemplo de uso:
    # Capturar a imagem do BlueStacks
    while True:
        captura = capturar_janela_bluestacks()

        # Recortar e dividir o grid em células
        grid_array = recortar_area_grid(captura)

        # Identificar interseções e desenhar o número nas imagens
        grid_com_intersecoes = identificar_intersecoes_e_aplicar_opacidade(grid_array)

        # Combinar o grid em uma única imagem
        imagem_completa = combinar_grid_em_imagem(grid_com_intersecoes)

        # Exibir a imagem completa com as interseções marcadas
        if imagem_completa is not None:
            cv2.imshow('Imagem Completa com Interseções', imagem_completa)
        else:
            print("Grid não encontrado ou vazio.")

        # Controlar a pausa entre capturas, e permitir fechar a janela com 'q'
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    # Fechar a janela ao final do loop
    cv2.destroyAllWindows()
