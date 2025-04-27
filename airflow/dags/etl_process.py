from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import boto3
from io import BytesIO

@dag(
    schedule_interval="@once",
    start_date=days_ago(1),
    catchup=False,
    tags=["etl", "ventas"],
    is_paused_upon_creation=False
)
def etl_proceso_ventas():
    """
    1. Realiza proceso de limpieza del dataset.
    2. Genera train.csv y test.csv en MinIO.
    """
    
    @task()
    def cargar_y_guardar_en_minio():
        """
        1. Lee '/opt/airflow/data/ventas.csv'.
        2. Elimina nulos. 
        3. Convierte 'Fecha' a datetime.
        4. Split train/test (70/30).
        5. Elimina outliers en train (IQR).
        6. Escala features con StandardScaler.
        7. Sube 'train.csv' y 'test.csv' al bucket 'data' en MinIO.
        """
    
        # Leer CSV local montado en el contenedor
        df = pd.read_csv("/opt/airflow/data/ventas.csv")
        
        # Eliminar valores nulos
        df = df.dropna()

        # Convertir fecha y eliminar outliers con IQR
        df['Fecha'] = pd.to_datetime(df['Fecha'])

        # Dividir en train/test (antes de eliminar outliers)
        train, test = train_test_split(df, test_size=0.3, random_state=42)

        # 2. Eliminar outliers solo en train
        Q1 = train['Ventas'].quantile(0.25)
        Q3 = train['Ventas'].quantile(0.75)
        IQR = Q3 - Q1
        train_sin_outliers = train[~((train['Ventas'] < (Q1 - 1.5 * IQR)) | (train['Ventas'] > (Q3 + 1.5 * IQR)))]

        # Normalizar usando solo train_sin_outliers para ajustar el escalador
        escalador = StandardScaler()
        columnas_escalar = train_sin_outliers.drop(["Ventas", "Fecha"], axis=1).columns
        
        # Ajustar escalador a train y aplicar a ambos conjuntos
        train_sin_outliers[columnas_escalar] = escalador.fit_transform(train_sin_outliers[columnas_escalar])
        test[columnas_escalar] = escalador.transform(test[columnas_escalar])  # ¡Usar transform(), no fit_transform()!

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
        subir_a_minio(train_sin_outliers, "data", "train.csv")
        subir_a_minio(test, "data", "test.csv")

    cargar_y_guardar_en_minio()

etl_proceso_ventas()