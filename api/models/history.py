from datetime import datetime

from sqlalchemy import Column, Integer, Float, DateTime, JSON

from api.db import Base


class PredictionHistory(Base):
    """Modelo de ORM para el historial de predicciones."""
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    input_data = Column(JSON, nullable=False)
    prediction = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
