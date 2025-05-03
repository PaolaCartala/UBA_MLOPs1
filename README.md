# Predicción de Ventas: Entrenamiento y Promoción Automática de Modelos, API REST y UI Interactiva con Docker

Este proyecto implementa un flujo de trabajo completo para **predecir ventas** que incluye:

1. **Orquestación de ETL y retraining** con **Apache Airflow**.  
2. **Almacenamiento de datos y artefactos** en **MinIO** (compatible con S3).  
3. **Tracking de experimentos y gestión de modelos** en **MLflow**.  
4. **API REST** para predicciones en tiempo real y acceso al historial, construida con **FastAPI**.  
5. **Interfaz gráfica multipágina** para consultas y documentación, desarrollada con **Streamlit**.  
6. **Contenerización y despliegue unificado** mediante **Docker Compose** (perfiles para todos los servicios).

## Tabla de Contenidos

- [Visión General](#visión-general)
- [Tecnologías](#tecnologías)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso de Airflow: Orquestación del Pipeline](#uso-de-airflow-orquestación-del-pipeline)
- [Uso de MLflow: Tracking y Registro de Modelos](#uso-de-mlflow-tracking-y-registro-de-modelos)
- [FastAPI](#fastapi)
- [Streamlit App](#streamlit-app)
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
- [FastAPI](https://fastapi.tiangolo.com/): Creación de la API REST.
- [Streamlit](https://streamlit.io/): Interfaz gráfica de usuario.

## Estructura del Proyecto

```
.
├── airflow/
│   ├── dags/
│   │   ├── etl_proceso_ventas.py           # DAG de ETL (limpieza, split, MinIO)
│   │   └── retrain_and_challenge_champion.py # DAG de entrenamiento y promoción
│   └── data/
│       └── ventas.csv                      # Dataset original (local)
├── api/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── Dockerfile
│   └── requirements.txt
├── mlflow/                                 # Tracking server
├── minio/                                  # Almacenamiento MinIO
├── streamlit_app/
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml                      # Configuración de servicios
└── README.md                               # Documentación del proyecto
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
- FastAPI
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

El proyecto incluye una API desarrollada en **[FastAPI](https://fastapi.tiangolo.com/)** para realizar predicciones de ventas en tiempo real y acceder al historial de predicciones realizadas.

### Funcionalidades

- **Predicción de ventas**: Envía datos relevantes (día de la semana, promociones, días festivos) para obtener predicciones en tiempo real.
- **Historial de predicciones**: Consulta las predicciones anteriores y sus detalles.
- **Chequeo de salud**: Verifica el estado de la API.

### Endpoints disponibles

- **Base URL**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **Endpoints Principales**:
  - `GET /health` — Verifica estado del servicio.
  - `POST /predict` — Recibe JSON con `{"DíaDeLaSemana":1,"Promociones":0,"Festivo":1}` y devuelve predicción.
  - `GET  /history/` — Lista historial de predicciones.
  - `GET  /history/{id}` — Detalle de una predicción.

### Acceso

- API disponible en: `http://localhost:8000`
- Documentación interactiva (Swagger UI): `http://localhost:8000/docs`

## Streamlit App

El proyecto incluye una interfaz gráfica desarrollada con **[Streamlit](https://streamlit.io/)**.

### Accesos

- Accede a **http://localhost:8501**.
- Navegación por pestañas: **Predictions**, **History**, **Docs**.
- Ingresa parámetros en pantalla para hacer peticiones a la API.
- Visualiza historial y documentación embebida.

## Equipo

- Paola Cartalá (paola.cartala@gmail.com)
- Gastón Schvarchman (gastonezequiel.sch@gmail.com)  
- Adrian Lapaz Olveira (adrianlapaz2010@gmail.com)  
- Cristian Marino (cristian.dam.marino@gmail.com)
