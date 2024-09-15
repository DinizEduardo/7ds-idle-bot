minI = 0
maxI = 9  # 10
minJ = 0
maxJ = 7  # 8


def encontrar_uma_interseccao(array2d, ultima_interseccao):
    linhas = len(array2d)
    colunas = len(array2d[0])
    for i in range(linhas):
        for j in range(colunas):
            if array2d[i][j] == 'none':
                interseccao_pos = (i, j)

                if interseccao_pos == ultima_interseccao:
                    continue
                # i, j -> posicao do local clicavel

                # primeira posicao que aparece algum texto diferente de none
                firstLeft, firstRight, firstTop, firstBottom = None, None, None, None

                firstRight = findRight(array2d, i, j)
                firstLeft = findLeft(array2d, i, j)
                firstTop = findTop(array2d, i, j)
                firstBottom = findBottom(array2d, i, j)

                # firstLeft, firstRight, firstTop, firstBottom
                if comparar_posicoes(array2d, firstLeft, firstRight):
                    p1PosI, p1PosJ = firstLeft
                    p2PosI, p2PosJ = firstRight
                elif comparar_posicoes(array2d, firstLeft, firstTop):
                    p1PosI, p1PosJ = firstLeft
                    p2PosI, p2PosJ = firstTop
                elif comparar_posicoes(array2d, firstLeft, firstBottom):
                    p1PosI, p1PosJ = firstLeft
                    p2PosI, p2PosJ = firstBottom
                elif comparar_posicoes(array2d, firstBottom, firstTop):
                    p1PosI, p1PosJ = firstBottom
                    p2PosI, p2PosJ = firstTop
                elif comparar_posicoes(array2d, firstBottom, firstRight):
                    p1PosI, p1PosJ = firstBottom
                    p2PosI, p2PosJ = firstRight
                elif comparar_posicoes(array2d, firstTop, firstRight):
                    p1PosI, p1PosJ = firstTop
                    p2PosI, p2PosJ = firstRight
                else:
                    continue

                array2d[p1PosI][p1PosJ] = "none"
                array2d[p2PosI][p2PosJ] = "none"

                return interseccao_pos, array2d

    return (None, None), array2d


def findRight(array2d, i, j):
    posIAtual = i + 1
    while minI <= posIAtual <= maxI:
        if array2d[posIAtual][j] != "none":
            return posIAtual, j
        posIAtual += 1


def findLeft(array2d, i, j):
    posIAtual = i - 1
    while minI <= posIAtual <= maxI:
        if array2d[posIAtual][j] != "none":
            return posIAtual, j
        posIAtual -= 1


def findBottom(array2d, i, j):
    posJAtual = j + 1
    while minJ <= posJAtual <= maxJ:
        if array2d[i][posJAtual] != "none":
            return i, posJAtual
        posJAtual += 1


def findTop(array2d, i, j):
    posJAtual = j - 1
    while minJ <= posJAtual <= maxJ:
        if array2d[i][posJAtual] != "none":
            return i, posJAtual
        posJAtual -= 1


def comparar_posicoes(array2d, pos1, pos2):
    if pos1 is None or pos2 is None:
        return False
    """
    Compara se os itens nas duas posições especificadas no array 2D são iguais.

    :param array2d: O array 2D onde a comparação será realizada.
    :param pos1: Primeira posição (tupla de dois inteiros, ex: (linha, coluna)).
    :param pos2: Segunda posição (tupla de dois inteiros, ex: (linha, coluna)).
    :return: True se os itens nas duas posições forem iguais, False caso contrário.
    """
    # Extraindo os índices das posições
    i1, j1 = pos1
    i2, j2 = pos2

    # Verificando se os valores nas duas posições são iguais
    return array2d[i1][j1] == array2d[i2][j2]


def encontrar_interseccao(array2d, ultima_interseccao):
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
                        (firstPos), (secondPos) = pos_hor
                        (fIHor, fJHor) = firstPos
                        (sIHor, sJHor) = secondPos

                        array2d[fIHor][fJHor] = "none"
                        array2d[sIHor][sJHor] = "none"

                    if pos_ver:
                        print(f"Interseção encontrada na posição {interseccao_pos} entre as posições {pos_ver}")
                        (firstPos), (secondPos) = pos_ver
                        (fIHor, fJHor) = firstPos
                        (sIHor, sJHor) = secondPos

                        array2d[fIHor][fJHor] = "none"
                        array2d[sIHor][sJHor] = "none"

                    return interseccao_pos, array2d

    return (None, None), array2d


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
