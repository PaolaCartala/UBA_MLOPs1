from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from api.models.schemas import PredictionInput, PredictionOutput
from api.services.prediction_service import predict_sales
from api.services.history_service import log_prediction


router = APIRouter(prefix="/predict", tags=["Prediction"])

@router.post("/", response_model=PredictionOutput, status_code=HTTPStatus.OK, description="Recibe datos de ventas y devuelve la predicción")
def predict(input_data: PredictionInput) -> PredictionOutput:
    """Genera una predicción de ventas y la registra en el historial."""
    try:
        pred = predict_sales(input_data)
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Error al generar la predicción: {e}"
        )
    try:
        log_prediction(input_data, pred)
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Predicción generada ({pred}) pero fallo al registrar el historial: {e}"
        )
    return PredictionOutput(prediction=pred)
