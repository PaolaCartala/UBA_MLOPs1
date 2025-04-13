# UBA_MLOPs1

# 🛒 Predicción de Ventas para Tienda Minorista

Este proyecto implementa un pipeline completo para el entrenamiento, evaluación y despliegue de modelos predictivos de ventas diarias para una tienda minorista localizada en una única localidad. Todo el flujo sigue buenas prácticas de MLOps, incluyendo almacenamiento en MinIO y ejecución mediante DAGs.

---

## 🎯 1. Objetivo del Proyecto

Construir un modelo de predicción robusto que permita anticipar las ventas del próximo mes utilizando datos históricos. Las predicciones generadas se aplican en:

- Optimización de inventario.
- Planificación de promociones.
- Asignación eficiente de personal.

---

## ⚙️ 2. Flujo de Entrenamiento del Modelo (DAG)

El proceso de entrenamiento está organizado como un DAG que asegura ejecución reproducible y escalable.

### 📌 Pasos del DAG de entrenamiento:

1. **Carga de datos desde MinIO**
   - Se descarga el archivo `Ventas.csv` desde un bucket S3/MinIO configurado.

2. **Preprocesamiento**
   - Conversión de fechas.
   - Normalización con `MinMaxScaler`.
   - Feature engineering básico.

3. **División del dataset**
   - Separación en entrenamiento y prueba (70/30).

4. **Entrenamiento de modelos**
   - Regresión Lineal.
   - Árbol de Decisión.
   - Random Forest.
   - Comparación mediante métricas $R^2$ y RMSE.

5. **Generación de visualizaciones**
   - Histogramas, boxplots, comparaciones modelo vs realidad.
   - Gráficos de predicción temporal.

6. **Registro del modelo**
   - Serialización del modelo (`.pkl`).
   - Exportación de métricas y gráficos como artefactos.

---

## ☁️ 3. Integración con MinIO

MinIO funciona como sistema de almacenamiento para datos, modelos y artefactos del proyecto.

### Flujo con MinIO:

1. **Upload inicial**
   - Se sube `Ventas.csv` al bucket `dataset-predicciones/ventas/`.

2. **Descarga por el DAG**
   - El DAG descarga el dataset con credenciales de entorno seguras.

3. **Exportación de resultados**
   - Modelos `.pkl` y visualizaciones se suben a `modelos/ventas/`.

4. **Automatización futura**
   - El DAG puede extenderse para reentrenar automáticamente cuando se detecten nuevos datos.

---

## 📊 4. Visualizaciones Generadas

Las siguientes figuras se producen y almacenan en `./Salidas`:

1. **1_distribucion_y_dias.png**  
   - Histograma de ventas  
   - Promedio por día de la semana

2. **2_boxplots_comparativos.png**  
   - Boxplots por promociones y festivos

3. **3_pred_vs_real_modelos.png**  
   - Comparación real vs. predicho para 3 modelos

4. **4_comparacion_temporal_modelos.png**  
   - Predicción temporal para los 3 modelos

---

## 📁 5. Estructura del Proyecto

```bash
prediccion-ventas/
├── 📂 Datos/                      # Datos crudos (opcional si se usa MinIO)
├── 📂 Modelos/                    # Modelos entrenados (.pkl)
├── 📂 Salidas/                    # Figuras generadas desde notebook
├── 📜 prediccion_ventas.ipynb     # Notebook exploratorio y de pruebas
├── 📜 README.md                   # Este archivo
