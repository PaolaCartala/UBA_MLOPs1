FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD mlflow server \
    --backend-store-uri postgresql://airflow:airflow@postgres:5432/mlflow_db \
    --default-artifact-root s3://mlflow/ \
    --host 0.0.0.0 \
    --port 5000