from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field


class PredictionInput(BaseModel):
    """Esquema de entrada para predicción de ventas."""
    dia_de_la_semana: int = Field(..., alias="DíaDeLaSemana", description="Día de la semana (1=lunes, ..., 7=domingo)")
    promociones: int = Field(..., alias="Promociones", description="0=no hubo promoción, 1=hubo promoción")
    festivo: int = Field(..., alias="Festivo", description="0=no festivo, 1=festivo")

    class Config:
        allow_population_by_alias = True


class PredictionOutput(BaseModel):
    """Esquema de salida de la predicción."""
    prediction: float = Field(..., description="Valor de ventas predicho")


class HistoryEntry(BaseModel):
    """Esquema para una entrada del historial de predicciones."""
    id: int
    input_data: Dict[str, Any]
    prediction: float
    timestamp: datetime

    class Config:
        orm_mode = True
