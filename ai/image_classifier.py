import cv2
import numpy as np
from tensorflow.python.keras.models import load_model
from PIL import Image  # Para trabalhar com a imagem na memória
import io  # Para gerenciar buffer de memória

# Função para pré-processar a imagem de entrada diretamente da memória
def prepare_image_from_memory(image_bytes):
    img_size = 56  # Tamanho usado no treinamento

    # Abrir a imagem a partir do buffer de bytes
    img = Image.open(io.BytesIO(image_bytes)).convert('L')  # Convertendo para escala de cinza

    # Redimensionar para 100x100 e converter para um array numpy
    img = img.resize((img_size, img_size))
    img_array = np.array(img)

    # Normalizar e redimensionar para o formato esperado pelo modelo
    img_array = img_array / 255.0
    return img_array.reshape(-1, img_size, img_size, 1)


def descobrir_imagem(celula, model):
    img_size = 56  # Tamanho da imagem esperado pelo modelo

    # Converta o recorte do OpenCV (NumPy array) para uma imagem Pillow
    img_pil = Image.fromarray(celula)

    # Garantir que a imagem esteja no formato RGB
    img_pil = img_pil.convert('RGB')

    # Redimensionar a imagem para o tamanho esperado pelo modelo (56x56)
    img_pil = img_pil.resize((img_size, img_size))

    # Converter a imagem Pillow de volta para um array NumPy
    img_array = np.array(img_pil)

    # Normalizar os pixels para valores entre 0 e 1
    img_array = img_array / 255.0

    # Redimensionar o array para o formato (1, img_size, img_size, 3) para a predição
    img_array = img_array.reshape(-1, img_size, img_size, 3)

    # Fazer a predição usando o modelo carregado
    prediction = model.predict(img_array)

    predicted_class_index = np.argmax(prediction)

    # Definir as categorias
    categories = ["abacate", "apple", "bread", "grapes", "hamburguer", "pear", "pizza", "none"]

    # Exibir o resultado
    predicted_class = categories[predicted_class_index]

    return predicted_class
