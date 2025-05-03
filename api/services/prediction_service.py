from typing import Any, Dict, Union

import mlflow
import mlflow.pyfunc
from mlflow.exceptions import RestException
import pandas as pd
from api.models.schemas import PredictionInput
from fastapi import HTTPException


# --- URI fija al modelo en producción ---
MLFLOW_MODEL_URI = "models:/prediccion_ventas_model_prod/1"

mlflow.set_tracking_uri("http://mlflow:5000")

from sklearn.tree import DecisionTreeRegressor
DecisionTreeRegressor.monotonic_cst = None


def predict_sales(
    input_data: Union[PredictionInput, Dict[str, Any]]
) -> float:
    """Obtiene la predicción de ventas a partir de la entrada."""
    try:
        model = mlflow.pyfunc.load_model(MLFLOW_MODEL_URI)
    except RestException:
        raise HTTPException(status_code=503, detail="Modelo no disponible en MLflow todavía.")

    if hasattr(input_data, "dict"):
        data: Dict[str, Any] = input_data.dict(by_alias=True)
    else:
        data = input_data
    for k, v in data.items():
        if isinstance(v, str):
            try:
                fv = float(v)
                data[k] = int(fv) if fv.is_integer() else fv
            except ValueError:
                pass
    df = pd.DataFrame([data])
    df = df.astype(float)
    result = model.predict(df)
    return float(result[0])
