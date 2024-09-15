import cv2
import mss
import numpy as np
import pyautogui
import pygetwindow as gw

from ai.image_classifier import descobrir_imagem
from ai.prepare_data import get_model


def transform_to_array(captura, model):
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
            y_celula_fim = (i + 1) * altura_celula  # if i == 0 else (i + 1) * altura_celula
            x_celula_inicio = j * largura_celula
            x_celula_fim = (j + 1) * largura_celula  # if j == 7 else (j + 1) * largura_celula
            celula = grid_recortado[y_celula_inicio:y_celula_fim, x_celula_inicio:x_celula_fim]

            imagem = descobrir_imagem(celula, model)

            linha_info.append(imagem)
            linha_possicoes.append(((x_celula_inicio, x_celula_fim), (y_celula_inicio, y_celula_fim)))
            linha.append(celula)
        grid_array.append(linha)
        info_array.append(linha_info)
        possicoes_array.append(linha_possicoes)

    return grid_array, info_array, possicoes_array

