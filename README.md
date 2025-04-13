# UBA_MLOPs1

# 🛒 Predicción de Ventas para Tienda Minorista

Este proyecto implementa un pipeline de entrenamiento y despliegue de modelos de predicción de ventas diarias para una tienda minorista localizada en una única localidad. Se utiliza un único dataset y se estructura todo el flujo siguiendo prácticas de MLOps, incluyendo el uso de almacenamiento en MinIO y ejecución controlada mediante un DAG (Directed Acyclic Graph).

---

## 🎯 Objetivo

Construir un modelo de predicción robusto que permita anticipar las ventas del próximo mes utilizando datos históricos. Las predicciones pueden usarse para:

- Optimizar la gestión de inventario.
- Planificar promociones.
- Asignar personal de forma eficiente.

---

## ⚙️ 1. DAG de Entrenamiento del Modelo

El flujo de entrenamiento está organizado como un DAG que asegura la ejecución ordenada, reproducible y escalable del modelo. Considerando que se trata de una única localidad, se entrena un único modelo sobre un único conjunto de datos.

### Estructura del DAG:

1. **Carga de datos desde MinIO**
   - Descarga del archivo `Ventas.csv` desde un bucket definido.

2. **Preprocesamiento**
   - Conversión de fechas.
   - Normalización de variables numéricas mediante `MinMaxScaler`.

3. **División del dataset**
   - Separación en conjuntos de entrenamiento y prueba (e.g., 70/30).

4. **Entrenamiento del modelo**
   - Modelado con regresión lineal o técnica definida.
   - Evaluación con métricas como MAE y MSE.

5. **Registro del modelo**
   - Persistencia del modelo entrenado.
   - Generación de artefactos para visualización.

---

## ☁️ 2. DAG de Interacción con MinIO

MinIO se utiliza como almacenamiento objeto para contener tanto los datos como los modelos y artefactos resultantes del entrenamiento. Se utilizan rutas bien definidas para garantizar trazabilidad y versionado.

### Flujo de integración con MinIO:

1. **Subida inicial de datos**
   - Se almacena el dataset `Ventas.csv` en un bucket específico (por ejemplo, `dataset-predicciones/ventas/`).

2. **Lectura en tiempo de ejecución**
   - El DAG de entrenamiento descarga el archivo directamente desde MinIO utilizando las credenciales del entorno de ejecución.

3. **Almacenamiento de artefactos**
   - El modelo entrenado (`modelo.pkl`) y los gráficos de validación se suben a un bucket de resultados (`modelos/ventas/`).

4. **Posible futura automatización**
   - El DAG podría incorporar validación automática y reentrenamiento en función de nuevos datos subidos al bucket.

---

## 📁 Estructura del Proyecto

```bash
prediccion-ventas/
├── 📂 Datos/                      # Contiene datos crudos (opcional si se usa MinIO)
├── 📂 dags/                       # DAGs de entrenamiento y carga
├── 📂 modelos/                    # Modelos entrenados
├── 📂 artefactos/                # Métricas, visualizaciones, registros
├── 📜 prediccion_ventas.ipynb    # Notebook exploratorio y de prueba
├── 📜 README.md                   # Este archivo
