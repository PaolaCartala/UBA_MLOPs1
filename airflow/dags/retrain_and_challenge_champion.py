from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import boto3
import pandas as pd
from io import BytesIO
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import mlflow
from mlflow.tracking import MlflowClient
import mlflow.sklearn

# --- Configuración global ---
BUCKET_NAME = "data"
TRAIN_FILE = "train.csv"
TEST_FILE = "test.csv"
TARGET_COLUMN = "Ventas"
MODEL_NAME = "prediccion_ventas_model_prod"

MLFLOW_TRACKING_URI = "http://mlflow:5000"

# --- Funciones auxiliares ---
def load_dataset_from_minio(file_name):
    s3 = boto3.client(
        "s3",
        endpoint_url="http://s3:9000",
        aws_access_key_id="minio",
        aws_secret_access_key="minio123"
    )
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=file_name)
    return pd.read_csv(BytesIO(obj['Body'].read()))

def train_sales_model(**kwargs):
    # Cargar datasets
    train_df = load_dataset_from_minio(TRAIN_FILE)
    test_df = load_dataset_from_minio(TEST_FILE)

    # Preparar datos
    X_train = train_df.drop(columns=[TARGET_COLUMN]).select_dtypes(include=["number"])
    y_train = train_df[TARGET_COLUMN]
    X_test = test_df.drop(columns=[TARGET_COLUMN]).select_dtypes(include=["number"])
    y_test = test_df[TARGET_COLUMN]

    # Configurar MLflow
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment("Prediccion de Ventas")

    with mlflow.start_run() as run:
        params = {"n_estimators": 100, "random_state": 42}
        model = RandomForestRegressor(**params)
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        rmse = mean_squared_error(y_test, predictions, squared=False)

        # Log en MLflow
        mlflow.log_params(params)
        mlflow.log_metric("rmse", rmse)
        mlflow.sklearn.log_model(model, artifact_path="modelo_random_forest")

        # Registrar el modelo en el registry
        mlflow.register_model(
            model_uri=f"runs:/{run.info.run_id}/modelo_random_forest",
            name=MODEL_NAME
        )

        # Guardar info del run_id para la siguiente tarea
        kwargs['ti'].xcom_push(key='challenger_run_id', value=run.info.run_id)
        kwargs['ti'].xcom_push(key='challenger_rmse', value=rmse)

def compare_and_promote_model(**kwargs):
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = MlflowClient()

    # Obtener challenger info desde XCom
    challenger_run_id = kwargs['ti'].xcom_pull(key='challenger_run_id')
    challenger_rmse = kwargs['ti'].xcom_pull(key='challenger_rmse')

    # Registrar el modelo si no existe
    try:
        client.get_registered_model(MODEL_NAME)
    except mlflow.exceptions.RestException as e:
        if e.error_code == "RESOURCE_DOES_NOT_EXIST":
            client.create_registered_model(MODEL_NAME)

    # Buscar el champion actual
    try:
        latest_versions = client.get_latest_versions(name=MODEL_NAME, stages=["Production"])
        champion = latest_versions[0] if latest_versions else None
    except mlflow.exceptions.RestException:
        champion = None

    # Buscar la versión del challenger en el registry
    challenger_versions = client.search_model_versions(f"run_id='{challenger_run_id}'")
    challenger_version = list(challenger_versions)[0].version

    if champion:
        # Obtener el RMSE del champion
        champion_metrics = client.get_run(champion.run_id).data.metrics
        champion_rmse = champion_metrics.get("rmse")

        print(f"Champion RMSE: {champion_rmse} | Challenger RMSE: {challenger_rmse}")

        # Comparar y promover si el challenger es mejor
        if challenger_rmse < champion_rmse:
            print("✅ Challenger es mejor. Promoviendo a Production...")
            client.transition_model_version_stage(name=MODEL_NAME, version=champion.version, stage="Archived")
            client.transition_model_version_stage(name=MODEL_NAME, version=challenger_version, stage="Production")
        else:
            print("⚠️ El champion sigue siendo mejor. No se promueve el challenger.")
    else:
        # Si no hay champion, promover directamente al challenger
        print("⚠️ No hay champion actual. Promoviendo challenger a Production...")
        client.transition_model_version_stage(name=MODEL_NAME, version=challenger_version, stage="Production")

# --- DAG definition ---
default_args = {
    "owner": "airflow",
    "depends_on_past": False
}

with DAG(
    dag_id="retrain_and_promote_sales_model",
    default_args=default_args,
    description="Reentrena, evalúa y promueve el modelo de predicción de ventas",
    schedule_interval=None,
    is_paused_upon_creation=False,
    start_date=datetime(2025, 4, 1),
    catchup=False,
    tags=["mlflow", "ventas", "retraining", "promotion"]
) as dag:

    retrain_model = PythonOperator(
        task_id="train_sales_model",
        python_callable=train_sales_model
    )

    promote_model = PythonOperator(
        task_id="compare_and_promote_model",
        python_callable=compare_and_promote_model
    )

    retrain_model >> promote_model