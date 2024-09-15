import os
import random

import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.python.keras import layers, models  # Certifique-se de usar o tf.keras

data_directory = "dataset"
categories = ["abacate", "apple", "bread", "grapes", "hamburguer", "pear", "pizza", "none"]
img_size = 56

training_data = []


def create_training_data():
    for category in categories:
        path = os.path.join(data_directory, category)
        class_num = categories.index(category)
        for img in os.listdir(path):
            try:
                # Alterando para carregar as imagens no formato RGB
                img_array = cv2.imread(os.path.join(path, img), cv2.IMREAD_COLOR)
                new_array = cv2.resize(img_array, (img_size, img_size))
                training_data.append([new_array, class_num])
            except Exception as e:
                pass


def get_model():
    create_training_data()

    random.shuffle(training_data)

    X = []
    y = []

    for features, label in training_data:
        X.append(features)
        y.append(label)

    # Alterando para (img_size, img_size, 3) para refletir imagens coloridas
    X = np.array(X).reshape(-1, img_size, img_size, 3)
    y = np.array(y)

    # Normalizando os dados (valores entre 0 e 1)
    X = X / 255.0

    # Criando o modelo
    model = models.Sequential()
    model.add(layers.Conv2D(64, (3, 3), activation='relu', input_shape=(img_size, img_size, 3)))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(128, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Flatten())
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dense(len(categories), activation='softmax'))

    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    # Dividindo os dados em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    acc = 0

    while acc < 0.9:
        # Treinando o modelo
        history = model.fit(X_train, y_train, epochs=333, validation_data=(X_test, y_test))

        # Avaliando o modelo
        test_loss, test_acc = model.evaluate(X_test, y_test)
        print(f"Test Accuracy: {test_acc * 100:.2f}%")
        acc = test_acc

    return model
