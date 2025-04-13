# Plan de Trabajo Final – MLOps 1

**Implementación de un sistema productivo de predicción de ventas con MLOps**

---

## Modelo base

- El trabajo se basa en el modelo desarrollado en el notebook `prediccion_ventas.ipynb`.
- El modelo predice ventas futuras en función de variables como tienda, producto, día de la semana, promociones, precios, entre otros.
- Se trata de un problema de regresión.

---

## Componentes del sistema

### 1. Infraestructura con Docker Compose

Se levantará un entorno productivo compuesto por múltiples servicios:

- **Apache Airflow**: para orquestar procesos de ETL y reentrenamiento del modelo.
- **MLflow**: para trackear experimentos, métricas e hiperparámetros.
- **MinIO**: para guardar datasets procesados, artefactos del modelo y metadatos.
- **PostgreSQL**: base de datos utilizada por Airflow y MLflow.
- **FastAPI**: para desplegar el modelo vía una API REST.
- **Streamlit**: para ofrecer una interfaz visual amigable a usuarios no técnicos.

---

### 2. Entrenamiento y experimentación

- Se desarrollará un notebook basado en `prediccion_ventas.ipynb` para:
  - Carga y limpieza de datos.
  - Feature engineering y normalización.
  - Entrenamiento del modelo.
  - Optimización de hiperparámetros (Optuna, si aplica).
  - Registro de experimentos, métricas y artefactos en MLflow.
  - Almacenamiento de datos y archivo `data.json` en MinIO.

---

### 3. DAGs de Airflow

#### `process_etl_sales_data.py`
- Descarga o carga los datos brutos.
- Realiza limpieza, creación de dummies y estandarización.
- Divide en train/test y guarda en MinIO.
- Loguea el proceso completo en MLflow.

#### `retrain_sales_model.py`
- Carga los datos procesados desde MinIO.
- Entrena un nuevo modelo ("challenger").
- Evalúa contra el modelo actual ("champion").
- Promueve al nuevo modelo si mejora la métrica.

---

### 4. API con FastAPI

- Se implementará una API REST en FastAPI para exponer el modelo predictivo.
- Se conectará con MLflow para obtener el modelo en producción y realizar inferencias.

#### Endpoints tentativos:

- `GET /health`: Verifica que la API esté corriendo correctamente.
- `POST /predict`: Recibe datos estructurados y devuelve la predicción del modelo.
- `GET /docs`: Provee documentación interactiva (Swagger).
- `GET /historical-predictions`: Devuelve un historial de predicciones realizadas.

La API se montará en el contenedor `fastapi` y expondrá el puerto `8800`.

---

### 5. Interfaz Web con Streamlit

- Se desarrollará una app con Streamlit que consuma los endpoints de la API.
- Permitirá a usuarios no técnicos:
  - Cargar datos manualmente o desde archivos.
  - Obtener predicciones de forma interactiva.
  - Visualizar los resultados con gráficos dinámicos.
- La app se ejecutará como servicio aparte y se conectará vía HTTP a la API de FastAPI.