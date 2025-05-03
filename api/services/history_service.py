from typing import Dict, Any, Optional, List

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from api.db import SessionLocal, engine, Base
from api.models.history import PredictionHistory
from api.models.schemas import PredictionInput

# Crear tablas al iniciar el servicio
Base.metadata.create_all(bind=engine)

def log_prediction(input_data: Dict[str, Any], prediction: float) -> PredictionHistory:
    """Registra una predicción en el historial."""
    if isinstance(input_data, PredictionInput):
        json_data = input_data.dict(by_alias=True)
    else:
        json_data = input_data
    db: Optional[Session] = None
    try:
        db = SessionLocal()
        record = PredictionHistory(
            input_data=json_data,
            prediction=prediction
        )
        db.add(record)
        db.commit()
    except SQLAlchemyError as e:
        if db:
            db.rollback()
        raise
    finally:
        if db:
            db.close()

def get_predictions(skip: int = 0, limit: int = 100) -> List[PredictionHistory]:
    """Obtiene el historial de predicciones."""
    db: Session = SessionLocal()
    entries = db.query(PredictionHistory).offset(skip).limit(limit).all()
    db.close()
    return entries

def get_prediction_by_id(entry_id: int) -> PredictionHistory:
    """Obtiene una predicción por ID."""
    db: Session = SessionLocal()
    entry = db.query(PredictionHistory).get(entry_id)
    db.close()
    return entry
