from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from datetime import timedelta
import pandas as pd
from sklearn.model_selection import train_test_split
import boto3
from io import BytesIO

@dag(
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
    tags=["etl", "ventas"]
)
def etl_proceso_ventas():

    @task()
    def cargar_y_guardar_en_minio():
        # Leer CSV local montado en el contenedor
        df = pd.read_csv("/opt/airflow/data/ventas.csv")

        # División en train/test
        train, test = train_test_split(df, test_size=0.3, random_state=42)

        # Conexión a MinIO
        s3 = boto3.client(
            "s3",
            endpoint_url="http://s3:9000",
            aws_access_key_id="minio",
            aws_secret_access_key="minio123"
        )

        def subir_a_minio(df, bucket, key):
            buffer = BytesIO()
            df.to_csv(buffer, index=False)
            buffer.seek(0)
            s3.put_object(Bucket=bucket, Key=key, Body=buffer.getvalue())

        # Subir archivos
        subir_a_minio(train, "data", "train.csv")
        subir_a_minio(test, "data", "test.csv")

    cargar_y_guardar_en_minio()

etl_proceso_ventas()