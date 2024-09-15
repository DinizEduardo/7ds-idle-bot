import time

import cv2
import mss
import numpy as np
import pyautogui
import pygetwindow as gw

from ai.image_classifier import descobrir_imagem
from ai.prepare_data import get_model


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

    x_grid = 13
    y_grid = 368

    x_janela, y_janela = janela.left, janela.top
    centro_x = x_grid + x_janela + x_inicio + largura // 2
    centro_y = y_grid + y_janela + y_fim - altura // 2
    # time.sleep(1)
    pyautogui.moveTo(centro_x, centro_y)
    pyautogui.click()
