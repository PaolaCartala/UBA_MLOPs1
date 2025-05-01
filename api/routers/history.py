from http import HTTPStatus
from typing import List

from fastapi import APIRouter, HTTPException

from api.services.history_service import get_prediction_by_id, get_predictions
from api.models.schemas import HistoryEntry


router = APIRouter(prefix="/history", tags=["History"])

@router.get("/", response_model=List[HistoryEntry], status_code=HTTPStatus.OK, description="Devuelve todas las entradas del historial de predicciones")
def list_history(skip: int = 0, limit: int = 100) -> List[HistoryEntry]:
    """Lista el historial de predicciones."""
    try:
        entries = get_predictions(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Error al recuperar el historial: {e}"
        )
    return entries

@router.get("/{entry_id}", response_model=HistoryEntry, status_code=HTTPStatus.OK, description="Obtiene una entrada de historial por su ID")
def get_history_entry(entry_id: int) -> HistoryEntry:
    """Obtiene una predicción específica del historial."""
    try:
        entry = get_prediction_by_id(entry_id)
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Error al recuperar la entrada con ID {entry_id}: {e}"
        )
    if not entry:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Entrada con ID {entry_id} no encontrada"
        )
    return entry
