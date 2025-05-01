# Predicción de Ventas: Entrenamiento y Promoción Automática de Modelos

Este proyecto implementa un pipeline de Machine Learning para **predecir ventas** utilizando **Airflow** para la orquestación, **MinIO** como almacenamiento de datasets y artefactos, y **MLflow** para el tracking de experimentos y la gestión del modelo.

## Tabla de Contenidos

- [Visión General](#visión-general)
- [Tecnologías](#tecnologías)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso de Airflow: Orquestación del Pipeline](#uso-de-airflow-orquestación-del-pipeline)
- [Uso de MLflow: Tracking y Registro de Modelos](#uso-de-mlflow-tracking-y-registro-de-modelos)
- [FastAPI](#fastapi)
- [Streamlit](#streamlit)
- [Equipo](#equipo)

## Visión General

El objetivo es automatizar el proceso de:

1. **Preprocesar los datos de ventas** (limpieza, escalado, división train/test).
2. **Entrenar un modelo de Random Forest con búsqueda de hiperparámetros**.
3. **Comparar el nuevo modelo (challenger) con el modelo en producción (champion)**.
4. **Promover automáticamente el challenger a production si es mejor**.

Todo esto gestionado mediante **Airflow**, con artefactos almacenados en **MinIO** y experimentos registrados en **MLflow**.

## Tecnologías

- [Apache Airflow](https://airflow.apache.org/): Orquestación de workflows.
- [MinIO](https://min.io/): Almacenamiento de datasets y artefactos (compatible con S3).
- [MLflow](https://mlflow.org/): Tracking de experimentos y gestión de modelos.
- [scikit-learn](https://scikit-learn.org/): Entrenamiento y evaluación de modelos.
- [Docker Compose](https://docs.docker.com/compose/): Contenerización del entorno.

## Estructura del Proyecto

```
.
├── dags/
│   ├── etl_proceso_ventas.py           # DAG de ETL (limpieza, split, MinIO)
│   └── retrain_and_challenge_champion.py # DAG de entrenamiento y promoción
├── data/
│   └── ventas.csv                      # Dataset original (local)
├── mlflow/                             # Tracking server
├── minio/                              # Almacenamiento MinIO
├── docker-compose.yml                  # Configuración de servicios
└── README.md                           # Documentación del proyecto
```

## Requisitos

- Docker y Docker Compose instalados.

## Instalación

1. **Clonar el repositorio:**

```bash
git clone <URL-del-repo>
cd <nombre-del-repo>
```

2. **Levantar los servicios:**

```bash
docker compose --profile all up --build
```

Esto inicia:
- Airflow (webserver, scheduler, workers)
- MLflow Tracking Server (http://localhost:5000)
- MinIO (http://localhost:9000, usuario: `minio`, clave: `minio123`)
- FastApi
- Streamlit

3. **Acceder a Airflow:**

http://localhost:8080 (usuario: `airflow`, clave: `airflow`)

## Uso de Airflow: Orquestación del Pipeline

### DAGs disponibles

#### 1. `etl_proceso_ventas`

- Este DAG **se ejecuta automáticamente** una única vez al iniciar el entorno.
- Realiza el procesamiento de los datos originales (`ventas.csv`), aplicando limpieza, escalado y división entre **train** y **test** (70/30).
- Los datasets generados (`train.csv` y `test.csv`) se almacenan en **MinIO** (bucket `data`).
- **No es necesario ejecutarlo manualmente**, pero queda registrado en Airflow para referencia.

#### 2. `retrain_and_promote_sales_model`

- Reentrena el modelo de predicción de ventas utilizando los datasets procesados.
- Evalúa si el modelo nuevo (**challenger**) supera al actual (**champion**) en base al **RMSE** sobre el conjunto de **test**.
- Si el challenger es mejor, lo promueve automáticamente a **Production** en **MLflow Model Registry**.

## Uso de MLflow: Tracking y Registro de Modelos

- Acceder a MLflow en: http://localhost:5000
- Cada corrida registra:
  - **Parámetros** del modelo seleccionado por GridSearch (n_estimators, max_depth, etc.).
  - **Métricas**: `cv_mse`, `cv_rmse`, `test_mse`, `test_rmse`, `test_r2`.
  - **Modelo entrenado** como artefacto.
  - Registro de versiones en el **Model Registry** bajo el nombre `prediccion_ventas_model_prod`.

## FastAPI

El proyecto incluye una API desarrollada en **FastAPI** para realizar predicciones de ventas en tiempo real y acceder al historial de predicciones realizadas.

### Funcionalidades

- **Predicción de ventas**: Envía datos relevantes (día de la semana, promociones, días festivos) para obtener predicciones en tiempo real.
- **Historial de predicciones**: Consulta las predicciones anteriores y sus detalles.
- **Chequeo de salud**: Verifica el estado de la API.

### Endpoints disponibles

- `POST /predict`: Recibe datos para realizar una predicción y retorna la predicción generada.
- `GET /history/`: Retorna el historial de predicciones.
- `GET /history/{id}`: Retorna detalles específicos de una predicción pasada por su ID.
- `GET /health`: Endpoint para verificar el estado de la API.

### Ejecución de la API

La API se levanta automáticamente al ejecutar los servicios mediante Docker Compose:

```bash
docker compose --profile all up --build
```

### Acceso

- La API está disponible en: `http://localhost:8000`
- Documentación interactiva de la API con Swagger UI: `http://localhost:8000/docs`

## Streamlit



## Equipo

- Miembro 1: Paola Cartalá (paola.cartala@gmail.com)
- Miembro 2: Gastón Schvarchman (gastonezequiel.sch@gmail.com)  
- Miembro 3: Adrian Lapaz Olveira (adrianlapaz2010@gmail.com)  
- Miembro 4: Cristian Marino (cristian.dam.marino@gmail.com)