from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import boto3
import pandas as pd
from io import BytesIO
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV
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
    """
    Carga un archivo CSV desde MinIO y devuelve un DataFrame de pandas.

    Args:
        file_name (str): Nombre del archivo CSV a cargar desde el bucket configurado.

    Returns:
        pd.DataFrame: DataFrame con los datos cargados desde MinIO.
    """

    s3 = boto3.client(
        "s3",
        endpoint_url="http://s3:9000",
        aws_access_key_id="minio",
        aws_secret_access_key="minio123"
    )
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=file_name)
    return pd.read_csv(BytesIO(obj['Body'].read()))

def train_sales_model(**kwargs):
    """
    Entrena un modelo de RandomForestRegressor utilizando GridSearchCV y loguea la ejecución en MLflow.

    - Carga los datasets de entrenamiento y prueba desde MinIO.
    - Realiza búsqueda de hiperparámetros con validación cruzada.
    - Calcula y loguea métricas (MSE, RMSE, R2) en MLflow.
    - Registra el modelo entrenado en el Model Registry de MLflow.
    - Envía el run_id y el RMSE del challenger al siguiente task mediante XCom.

    Args:
        kwargs (dict): Contexto de Airflow que incluye `ti` (task instance) para usar XCom.
    """
    
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
        # Definir la grilla de hiperparámetros
        param_grid = {
            "n_estimators":      [100, 200],
            "max_depth":         [None, 10, 20],
            "min_samples_split": [2, 5]
        }

        # GridSearch con validación cruzada
        grid = GridSearchCV(
            RandomForestRegressor(random_state=42),
            param_grid,
            cv=5,
            n_jobs=-1,
            scoring="neg_mean_squared_error"
        )
        grid.fit(X_train, y_train)
        best_model = grid.best_estimator_

        # Métricas
        cv_mse   = -grid.best_score_
        cv_rmse  = cv_mse ** 0.5
        y_pred   = best_model.predict(X_test)
        test_mse = mean_squared_error(y_test, y_pred)
        test_rmse = test_mse ** 0.5
        test_r2  = r2_score(y_test, y_pred)

        # Log en MLflow
        mlflow.log_params(grid.best_params_)
        mlflow.log_metric("cv_mse", cv_mse)
        mlflow.log_metric("cv_rmse", cv_rmse)
        mlflow.log_metric("mse", test_mse)
        mlflow.log_metric("rmse", test_rmse)
        mlflow.log_metric("r2", test_r2)
        mlflow.sklearn.log_model(best_model, artifact_path="modelo_random_forest")

        run_id = run.info.run_id
        mlflow.end_run()

        # Registrar modelo en el registry
        client = MlflowClient()
        
        try:
            client.get_registered_model(MODEL_NAME)
        except mlflow.exceptions.RestException as e:
            if e.error_code == "RESOURCE_DOES_NOT_EXIST":
                client.create_registered_model(MODEL_NAME)

        client.create_model_version(
            name=MODEL_NAME,
            source=f"{run.info.artifact_uri}/modelo_random_forest",
            run_id=run_id
        )

        # Guardar el run_id y rmse para el siguiente task
        kwargs['ti'].xcom_push(key='challenger_run_id', value=run_id)
        kwargs['ti'].xcom_push(key='challenger_rmse', value=test_rmse)

def compare_and_promote_model(**kwargs):
    """
    Compara el modelo challenger entrenado con el modelo champion actual en producción.

    - Obtiene el RMSE del challenger desde XCom.
    - Recupera el modelo champion actual desde el Model Registry de MLflow.
    - Si el challenger tiene mejor RMSE que el champion, lo promueve a Production y archiva el anterior.
    - Si no existe un champion, promueve directamente el challenger.

    Args:
        kwargs (dict): Contexto de Airflow que incluye `ti` (task instance) para usar XCom.
    """

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

        if champion_rmse is None:
            print("⚠️ Champion no tiene RMSE registrado. Promoviendo challenger a Production...")
            client.transition_model_version_stage(name=MODEL_NAME, version=challenger_version, stage="Production")
            return

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