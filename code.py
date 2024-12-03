# -*- coding: utf-8 -*-
"""Proyecto2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ZiydXyY200ZnqrkT63IYLPokakE93avN

# **Machine Learning: Proyecto 2**
##**Integrantes**
*   Willian Berrocal Alvarado
*   John Rodrigo Monroy Angeles
*   Tania Araceli Barreda Galvez
*   Bianca Brunella Aguinaga Pizarro
*   Melisa Karen Rivera Alagon
*   Luis Robledo
"""

!pip install tqdm
!pip install PyWavelets

from sklearn.model_selection import train_test_split
from tqdm import tqdm
import tensorflow as tf # para obtener las imagenes MNIST
import matplotlib.pyplot as plt #para graficar
import numpy as np  # para los arreglos
import pandas as pd
import pywt
from sklearn.model_selection import KFold
from sklearn.metrics import precision_score, recall_score, f1_score



## DATA
# Cargar el dataset MNIST desde TensorFlow
(train_images, train_labels), (test_images, test_labels) = tf.keras.datasets.mnist.load_data()

#Análisis de la información:
print("\033[34mAnálisis de la información:\033[0m")
print("(train_images contiene (cantidad de imagenes,pixeles x,pixeles y):",train_images.shape)
print("Cada imagen contiene los pixeles del tipo (",train_images.dtype,") para indicar la itensidad:",train_images.min()," al ",train_images.max())
print("\033[4;35;47m0 es totalmente negro y 255 es totalmente blanco \033[0m")


# Normalizar las imágenes (entre 0 y 1)
train_images = train_images.astype(np.float32) / 255.0
test_imagenes =train_images.astype(np.float32) / 255.0
# el resultado demuestra que la matriz se ha normalizado
print("\033[34mluego de la normalización:\033[0m")
print("train_images contien los pixeles(",train_images.dtype,")de la imagen normalizada tienen valores del:",train_images.min()," al ",train_images.max())
print("train_labels contien las etiquetas del tipo (", train_labels.dtype,")de cada imagen y van del:", train_labels.min()," al ", train_labels.max())

# Seleccionar imagenes de muestra
# Función para mostrar múltiples imágenes
def plot_images(images, titles):
    fig, axs = plt.subplots(1, len(images), figsize=(10, 10))

    for i, image in enumerate(images):
        axs[i].imshow(image, cmap='gray')
        axs[i].set_title(titles[i])
        axs[i].axis('off')

    plt.show()

# Indice_temporal para seleccionar cuantas imagenes quieres ver:
indice_temporal=10
print("\033[34mSe visualiza las primeras ",indice_temporal,"imagenes(28x28) de la matriz train_images \033[0m")
plot_images(train_images[:indice_temporal],train_labels[:indice_temporal])






## Generacion de Vectores Caracteristicos
# Aplicar la Transformada Wavelet Haar para extraer características


def haar_wavelet_transform_2d_batch(images):
    n_images, height, width = images.shape
    transformed_images = np.zeros_like(images)

    def haar_wavelet_transform_2d(image):
        transformed_image = np.zeros_like(image)
        rows, cols = image.shape

        for i in range(rows):
            approximations, details = pywt.dwt(image[i, :], 'haar')
            transformed_image[i, :cols//2] = approximations
            transformed_image[i, cols//2:] = details

        for i in range(cols):
            approximations, details = pywt.dwt(transformed_image[:, i], 'haar')
            transformed_image[:rows//2, i] = approximations
            transformed_image[rows//2:, i] = details

        return transformed_image

    for i in range(n_images):
        transformed_images[i] = haar_wavelet_transform_2d(images[i])

    return transformed_images

# Aplicar la transformada Haar a los datos
transformed_train_images = haar_wavelet_transform_2d_batch(train_images)
transformed_test_images = haar_wavelet_transform_2d_batch(test_images)

# Solo usamos las matrices de aproximación
rows, cols = transformed_train_images[0].shape
half_rows, half_cols = rows // 2, cols // 2
LL_train = transformed_train_images[:, :half_rows, :half_cols].reshape(len(train_images), -1)
LL_test = transformed_test_images[:, :half_rows, :half_cols].reshape(len(test_images), -1)

# Separar en entrenamiento, validación y prueba (70% entrenamiento, 15% validación, 15% prueba)
X_train, X_temp, y_train, y_temp = train_test_split(LL_train, train_labels, test_size=0.3, stratify=train_labels, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42)






## KNN
def euclidean_distance(x1, x2):
  return np.sqrt(np.sum((x1-x2)**2))

def knn(X_train, y_train, X_test, k):
    y_pred = []

    for test_point in tqdm(X_test, desc="Knn:"):

        distances = [euclidean_distance(test_point, train_point) for train_point in X_train]
        k_nearest_indices = np.argsort(distances)[:k]
        k_nearest_labels = [y_train[i] for i in k_nearest_indices]

        pred_label = max(set(k_nearest_labels), key=k_nearest_labels.count)
        y_pred.append(pred_label)

    return np.array(y_pred)

# Entrenar y predecir con KNN
k = 3
y_pred_knn = knn(X_train, y_train, X_test, k=k)

# Métricas KNN


precision_knn = precision_score(y_test, y_pred_knn, average='weighted')
recall_knn = recall_score(y_test, y_pred_knn, average='weighted')
f1_knn = f1_score(y_test, y_pred_knn, average='weighted')

print(f"KNN - Precisión: {precision_knn:.4f}, Recall: {recall_knn:.4f}, F1-Score: {f1_knn:.4f}")

# Métricas KNN para 3 diferentes k

# Valores de k para probar
k_values = [3, 5, 7]

# Diccionario para almacenar los resultados
metrics_results_knn = {}

for k in k_values:
    # Entrenar y predecir con KNN usando el valor actual de k
    y_pred_knn = knn(X_train, y_train, X_test, k=k)

    # Calcular las métricas
    precision_knn = precision_score(y_test, y_pred_knn, average='weighted')
    recall_knn = recall_score(y_test, y_pred_knn, average='weighted')
    f1_knn = f1_score(y_test, y_pred_knn, average='weighted')

    # Almacenar las métricas en el diccionario
    metrics_results_knn[k] = {
        'Precision': precision_knn,
        'Recall': recall_knn,
        'F1-Score': f1_knn
    }

# Mostrar los resultados para cada valor de k
for k, metrics in metrics_results_knn.items():
    print(f"KNN con k = {k}")
    print(f"Precisión: {metrics['Precision']:.4f}")
    print(f"Recall: {metrics['Recall']:.4f}")
    print(f"F1-Score: {metrics['F1-Score']:.4f}")
    print("-" * 40)





## Regresión Logística
class LogisticRegressionMulticlass:
    def __init__(self, input_size, num_classes, learning_rate=0.01, num_epochs=100, regularization=None, reg_lambda=0.0):
        self.weights = np.random.randn(input_size, num_classes) * 0.01
        self.bias = np.zeros((1, num_classes))
        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        self.regularization = regularization
        self.reg_lambda = reg_lambda

    def softmax(self, logits):
        exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
        return exp_logits / np.sum(exp_logits, axis=1, keepdims=True)

    def cross_entropy_loss(self, y_true, y_pred):
        n_samples = y_true.shape[0]
        log_likelihood = -np.log(y_pred[range(n_samples), y_true])
        loss = np.sum(log_likelihood) / n_samples

        if self.regularization == 'L2':
            loss += self.reg_lambda * np.sum(self.weights ** 2) / 2
        elif self.regularization == 'L1':
            loss += self.reg_lambda * np.sum(np.abs(self.weights))

        return loss

    def one_hot_encode(self, y, num_classes):
        n_samples = y.shape[0]
        y_one_hot = np.zeros((n_samples, num_classes))
        y_one_hot[np.arange(n_samples), y] = 1
        return y_one_hot

    def fit(self, X_train, y_train, X_val=None, y_val=None):
        n_samples = X_train.shape[0]
        num_classes = len(np.unique(y_train))
        train_losses = []
        val_losses = []

        # Barra de progreso para el número de épocas
        for epoch in tqdm(range(self.num_epochs), desc="Entrenando Regresión Logística"):
            logits = np.dot(X_train, self.weights) + self.bias
            y_pred = self.softmax(logits)
            train_loss = self.cross_entropy_loss(y_train, y_pred)
            train_losses.append(train_loss)

            error = y_pred - self.one_hot_encode(y_train, num_classes)
            dw = np.dot(X_train.T, error) / n_samples
            db = np.sum(error, axis=0, keepdims=True) / n_samples

            if self.regularization == 'L2':
                dw += self.reg_lambda * self.weights
            elif self.regularization == 'L1':
                dw += self.reg_lambda * np.sign(self.weights)

            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db

            if X_val is not None:
                val_logits = np.dot(X_val, self.weights) + self.bias
                val_pred = self.softmax(val_logits)
                val_loss = self.cross_entropy_loss(y_val, val_pred)
                val_losses.append(val_loss)

            if epoch % 10 == 0:
                print(f"Época {epoch}: Pérdida Entrenamiento = {train_loss}, Pérdida Validación = {val_loss if X_val is not None else 'N/A'}")

        return train_losses, val_losses

    def predict(self, X):
        logits = np.dot(X, self.weights) + self.bias
        y_pred = self.softmax(logits)
        return np.argmax(y_pred, axis=1)

# Configuraciones de entrenamiento
num_epochs_options = [50, 100, 200]
regularization_options = [None, 'L1', 'L2']
metrics = []

# Iterar sobre diferentes configuraciones de épocas y regularización
for num_epochs in num_epochs_options:
    for regularization in regularization_options:
        # Instanciar el modelo de Regresión Logística
        logistic_model = LogisticRegressionMulticlass(
            input_size=X_train.shape[1],
            num_classes=len(np.unique(y_train)),
            learning_rate=0.01,
            num_epochs=num_epochs,
            regularization=regularization,
            reg_lambda=0.01 if regularization else 0.0
        )

        # Ajustar el modelo en el conjunto de entrenamiento y validación
        train_losses, val_losses = logistic_model.fit(X_train, y_train, X_val, y_val)

        # Graficar las pérdidas de entrenamiento y validación
        plt.plot(train_losses, label='Pérdida de Entrenamiento')
        plt.plot(val_losses, label='Pérdida de Validación')
        plt.xlabel('Épocas')
        plt.ylabel('Pérdida')
        plt.title(f'Pérdida vs Épocas para Regresión Logística\nEpochs: {num_epochs}, Regularización: {regularization}')
        plt.legend()
        plt.show()

        # Predecir en el conjunto de prueba
        y_pred_test = logistic_model.predict(LL_test)

        # Calcular las métricas de Precisión, Recall y F1-Score
        precision = precision_score(test_labels, y_pred_test, average='weighted')
        recall = recall_score(test_labels, y_pred_test, average='weighted')
        f1 = f1_score(test_labels, y_pred_test, average='weighted')

        # Almacenar las métricas en una lista
        metrics.append({
            'num_epochs': num_epochs,
            'regularization': regularization,
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        })

# Convertir métricas a DataFrame y calcular promedios
metrics_df = pd.DataFrame(metrics)
averages = metrics_df.groupby(['num_epochs', 'regularization']).mean().reset_index()

# Imprimir las métricas promedio
print("\nMétricas Promedio:")
print(averages[['num_epochs', 'regularization', 'precision', 'recall', 'f1_score']])






## SVM


class SVM_Multiclass:
    def __init__(self, n_classes, learning_rate=0.001, lambda_param=0.01, n_iters=1000):
        self.n_classes = n_classes
        self.learning_rate = learning_rate
        self.lambda_param = lambda_param
        self.n_iters = n_iters
        self.weights = None
        self.biases = None

    def fit_one_vs_all(self, X, y, class_label):
        m, n = X.shape
        W = np.zeros(n)
        b = 0
        y_binary = np.where(y == class_label, 1, -1)

        # Barra de progreso para el número de iteraciones
        for _ in tqdm(range(self.n_iters), desc=f"Entrenando SVM para clase {class_label}"):
            for i in range(m):
                condition = y_binary[i] * (np.dot(X[i], W) + b) >= 1
                if condition:
                    W -= self.learning_rate * (2 * self.lambda_param * W)
                else:
                    W -= self.learning_rate * (2 * self.lambda_param * W - np.dot(X[i], y_binary[i]))
                    b -= self.learning_rate * y_binary[i]
        return W, b

    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.weights = np.zeros((self.n_classes, n_features))
        self.biases = np.zeros(self.n_classes)

        for c in range(self.n_classes):
            W, b = self.fit_one_vs_all(X, y, class_label=c)
            self.weights[c] = W
            self.biases[c] = b

    def predict(self, X):
        linear_outputs = np.dot(X, self.weights.T) + self.biases
        return np.argmax(linear_outputs, axis=1)


# Entrenar y predecir con SVM
svm_model = SVM_Multiclass(n_classes=len(np.unique(y_train)), learning_rate=0.001, lambda_param=0.01, n_iters=1000)
svm_model.fit(X_train, y_train)
y_pred_svm = svm_model.predict(X_test)

# Métricas SVM
precision_svm = precision_score(y_test, y_pred_svm, average='weighted')
recall_svm = recall_score(y_test, y_pred_svm, average='weighted')
f1_svm = f1_score(y_test, y_pred_svm, average='weighted')

print(f"SVM - Precisión: {precision_svm:.4f}, Recall: {recall_svm:.4f}, F1-Score: {f1_svm:.4f}")

# Metricas para 3 lambdas
# Valores de lambda_param para probar
lambda_values = [0.001, 0.01, 0.1]

# Diccionario para almacenar los resultados
metrics_results = {}

for lambda_param in lambda_values:
    # Crear e instanciar el modelo SVM con el valor de lambda actual
    svm_model = SVM_Multiclass(n_classes=len(np.unique(y_train)), learning_rate=0.001, lambda_param=lambda_param, n_iters=1000)

    # Entrenar el modelo
    svm_model.fit(X_train, y_train)

    # Predecir con el conjunto de prueba
    y_pred_svm = svm_model.predict(X_test)

    # Calcular las métricas
    precision_svm = precision_score(y_test, y_pred_svm, average='weighted')
    recall_svm = recall_score(y_test, y_pred_svm, average='weighted')
    f1_svm = f1_score(y_test, y_pred_svm, average='weighted')

    # Almacenar las métricas en el diccionario
    metrics_results[lambda_param] = {
        'Precision': precision_svm,
        'Recall': recall_svm,
        'F1-Score': f1_svm
    }

# Mostrar los resultados para cada lambda
for lambda_param, metrics in metrics_results.items():
    print(f"Lambda: {lambda_param}")
    print(f"Precisión: {metrics['Precision']:.4f}")
    print(f"Recall: {metrics['Recall']:.4f}")
    print(f"F1-Score: {metrics['F1-Score']:.4f}")
    print("-" * 40)





## Árbol de Decisión
class Node:
    def __init__(self, feature_index=None, threshold=None, left=None, right=None, value=None):
        self.feature_index = feature_index
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value

def entropy(y):
    hist = np.bincount(y)
    ps = hist / len(y)
    ps = ps[ps > 0]
    return -np.sum(ps * np.log2(ps))

def information_gain(y, y_left, y_right):
    H_before = entropy(y)
    H_left = entropy(y_left)
    H_right = entropy(y_right)
    w_left = len(y_left) / len(y)
    w_right = len(y_right) / len(y)
    return H_before - (w_left * H_left + w_right * H_right)

def best_split(X, y):
    best_gain = -1
    split_idx, split_threshold = None, None
    n_samples, n_features = X.shape

    for feature_index in range(n_features):
        X_column = X[:, feature_index]
        thresholds = np.unique(X_column)
        for threshold in thresholds:
            left_idxs = X_column <= threshold
            right_idxs = X_column > threshold
            if len(y[left_idxs]) == 0 or len(y[right_idxs]) == 0:
                continue

            gain = information_gain(y, y[left_idxs], y[right_idxs])
            if gain > best_gain:
                best_gain = gain
                split_idx = feature_index
                split_threshold = threshold

    return best_gain, split_idx, split_threshold

def most_common_label(y):
    counts = np.bincount(y)
    return np.argmax(counts)

def build_tree(X, y, max_depth=10, min_samples_split=2):
    num_samples, num_features = X.shape
    num_labels = len(np.unique(y))

    if (num_labels == 1) or (num_samples < min_samples_split) or (max_depth == 0):
        leaf_value = most_common_label(y)
        return Node(value=leaf_value)

    gain, feature_idx, threshold = best_split(X, y)
    if gain == -1:
        leaf_value = most_common_label(y)
        return Node(value=leaf_value)

    left_idxs = X[:, feature_idx] <= threshold
    right_idxs = X[:, feature_idx] > threshold
    left = build_tree(X[left_idxs], y[left_idxs], max_depth - 1, min_samples_split)
    right = build_tree(X[right_idxs], y[right_idxs], max_depth - 1, min_samples_split)

    return Node(feature_index=feature_idx, threshold=threshold, left=left, right=right)

def predict_sample(node, x):
    if node.value is not None:
        return node.value
    if x[node.feature_index] <= node.threshold:
        return predict_sample(node.left, x)
    else:
        return predict_sample(node.right, x)

def predict(tree, X):
    return [predict_sample(tree, x) for x in X]

# Entrenar Árbol de Decisión
tree = build_tree(X_train, y_train, max_depth=10, min_samples_split=10)
y_pred_tree = predict(tree, X_test)

# Métricas Árbol de Decisión
precision_tree = precision_score(y_test, y_pred_tree, average='weighted')
recall_tree = recall_score(y_test, y_pred_tree, average='weighted')
f1_tree = f1_score(y_test, y_pred_tree, average='weighted')

print(f"Árbol de Decisión - Precisión: {precision_tree:.4f}, Recall: {recall_tree:.4f}, F1-Score: {f1_tree:.4f}")

# Metricas para diferentes valores de max_depth
# Valores de max_depth para probar
max_depth_values = [5, 10, 15]

# Diccionario para almacenar los resultados
metrics_results_tree = {}

for max_depth in max_depth_values:
    # Entrenar el Árbol de Decisión con el valor actual de max_depth
    tree = build_tree(X_train, y_train, max_depth=max_depth, min_samples_split=10)

    # Predecir con el conjunto de prueba
    y_pred_tree = predict(tree, X_test)

    # Calcular las métricas
    precision_tree = precision_score(y_test, y_pred_tree, average='weighted')
    recall_tree = recall_score(y_test, y_pred_tree, average='weighted')
    f1_tree = f1_score(y_test, y_pred_tree, average='weighted')

    # Almacenar las métricas en el diccionario
    metrics_results_tree[max_depth] = {
        'Precision': precision_tree,
        'Recall': recall_tree,
        'F1-Score': f1_tree
    }

# Mostrar los resultados para cada max_depth
for max_depth, metrics in metrics_results_tree.items():
    print(f"Max Depth: {max_depth}")
    print(f"Precisión: {metrics['Precision']:.4f}")
    print(f"Recall: {metrics['Recall']:.4f}")
    print(f"F1-Score: {metrics['F1-Score']:.4f}")
    print("-" * 40)







## Entrenar Modelos Usando K-fold

# Función de K-fold para entrenar y evaluar los modelos
def cross_validate_model(model, X, y, k=5):
    kfold = KFold(n_splits=k, shuffle=True, random_state=42)
    fold_metrics = []

    for train_idx, val_idx in kfold.split(X):
        X_train_fold, X_val_fold = X[train_idx], X[val_idx]
        y_train_fold, y_val_fold = y[train_idx], y[val_idx]

        model.fit(X_train_fold, y_train_fold)  # Entrenar el modelo en los datos del fold actual
        y_pred_val = model.predict(X_val_fold)  # Predecir en el set de validación

        # Calcular las métricas
        precision = precision_score(y_val_fold, y_pred_val, average='weighted')
        recall = recall_score(y_val_fold, y_pred_val, average='weighted')
        f1 = f1_score(y_val_fold, y_pred_val, average='weighted')

        # Guardar las métricas para cada fold
        fold_metrics.append({
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        })

    return fold_metrics

# Regresión Logística
logistic_model = LogisticRegressionMulticlass(input_size=X_train.shape[1], num_classes=len(np.unique(y_train)))
logistic_metrics = cross_validate_model(logistic_model, LL_train, train_labels, k=5)
print(f"Resultados K-fold para Regresión Logística: {logistic_metrics}")


# KNN
k = 3  # Número de vecinos
knn_model = KNN(k=k)
knn_metrics = cross_validate_model(knn_model, LL_train, train_labels, k=5)
print(f"Resultados K-fold para KNN: {knn_metrics}")


# SVM
svm_model = SVM_Multiclass(n_classes=len(np.unique(y_train)), learning_rate=0.001, lambda_param=0.01, n_iters=1000)
svm_metrics = cross_validate_model(svm_model, LL_train, train_labels, k=5)
print(f"Resultados K-fold para SVM: {svm_metrics}")

# Árbol de Decisión
tree_model = build_tree(X_train, y_train, max_depth=10, min_samples_split=10)
tree_metrics = cross_validate_model(tree_model, LL_train, train_labels, k=5)
print(f"Resultados K-fold para Árbol de Decisión: {tree_metrics}")






## Generar las Gráficas de Pérdida vs Épocas

# Regresión Logísitca
# Modificar la regresión logística para que devuelva las pérdidas
train_losses, val_losses = logistic_model.fit(X_train, y_train, X_val, y_val)

# Graficar las pérdidas para la Regresión Logística
def plot_losses(train_losses, val_losses, title):
    plt.plot(train_losses, label='Pérdida de Entrenamiento')
    plt.plot(val_losses, label='Pérdida de Validación')
    plt.xlabel('Épocas')
    plt.ylabel('Pérdida')
    plt.title(title)
    plt.legend()
    plt.show()

plot_losses(train_losses, val_losses, 'Pérdida vs Épocas para Regresión Logística')

# SVM
train_losses, val_losses = svm_model.fit(X_train, y_train, X_val, y_val)
plot_losses(train_losses, val_losses, 'Pérdida vs Épocas para SVM')






## Colocar los Valores de Precisión, Recall, F1-Score e Hiperparámetros en una Tabla

def save_metrics_to_csv(model_name, metrics, filename="metrics_results.csv"):
    df = pd.DataFrame(metrics)
    df['model'] = model_name
    df.to_csv(filename, mode='a', index=False)

# Guardar los resultados de regresión logística
save_metrics_to_csv('Regresión Logística', logistic_metrics)

# Guardar los resultados de KNN
save_metrics_to_csv('KNN', knn_metrics)

# Guardar los resultados de SVM
save_metrics_to_csv('SVM', svm_metrics)

# Guardar los resultados de Árbol de Decisión
save_metrics_to_csv('Árbol de Decisión', tree_metrics)