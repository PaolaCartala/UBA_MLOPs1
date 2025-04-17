import pandas as pd
import boto3
from io import BytesIO
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import mlflow
import mlflow.sklearn

# Configuración de MinIO
s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="minio",
    aws_secret_access_key="minio123"
)

def cargar_desde_minio(bucket, nombre_archivo):
    obj = s3.get_object(Bucket=bucket, Key=nombre_archivo)
    return pd.read_csv(BytesIO(obj['Body'].read()))

# Cargar datasets
train_df = cargar_desde_minio("data", "train.csv")
test_df = cargar_desde_minio("data", "test.csv")

# Separar features y target
X_train = train_df.drop(columns=["ventas"])  # ajustá esto a tu target real
y_train = train_df["ventas"]
X_test = test_df.drop(columns=["ventas"])
y_test = test_df["ventas"]

# Configurar MLflow
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("prediccion_ventas")


##---------------------------- Hasta acá todo general -----------------



with mlflow.start_run(): ## acá hay que poner el modelo que utilicemos ↓
    # Entrenamiento
    n_estimators = 100
    model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)
    model.fit(X_train, y_train)

    # Predicción y evaluación
    y_pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)

    # Logging en MLflow. Si agregamos otros parámetros u otras métricas hay que agregarlas acá↓
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_metric("rmse", rmse)
    mlflow.sklearn.log_model(model, "modelo_random_forest")