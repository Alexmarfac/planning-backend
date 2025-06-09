import os
from pathlib import Path
from functools import lru_cache
import joblib
import pandas as pd
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict
import logging

from schemas import Criticity, StoryType, Priority

# Configuración del logger
default_log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=default_log_format)
logger = logging.getLogger(__name__)

# Ruta del modelo ML
MODEL_PATH = Path(__file__).parent / 'ml' / 'priority_model.pkl'

# --- Input Schema ---
class PriorityInput(BaseModel):
    story_points: int = Field(..., ge=0)
    business_value: int = Field(..., ge=0)
    criticity: Criticity
    internal_dependencies: int = Field(..., ge=0)
    continuation: int = Field(..., ge=0)
    story_type: StoryType

    @validator('story_type', pre=True)
    def cast_story_type(cls, v):
        if isinstance(v, str):
            return StoryType(v)
        return v

# --- Model Loader ---
@lru_cache(maxsize=1)
def load_model() -> Optional[joblib.Bunch]:
    """
    Carga el modelo de disco la primera vez y lo cachea.
    """
    try:
        if MODEL_PATH.exists():
            logger.info(f"Cargando modelo desde {MODEL_PATH}")
            return joblib.load(MODEL_PATH)
        else:
            logger.warning(f"No se encontró el archivo de modelo en {MODEL_PATH}")
            return None
    except Exception as e:
        logger.error(f"Error cargando el modelo: {e}")
        return None

# --- Prediction ---
def predict_priority(input_data: Dict) -> Dict[str, Optional[str]]:
    """
    Recibe un dict con los campos necesarios, valida con Pydantic,
    aplica el pipeline del modelo y devuelve la prioridad prevista.
    """
    try:
        data = PriorityInput(**input_data)
    except Exception as e:
        logger.error(f"Error validando input: {e}")
        return {"error": f"Datos inválidos: {e}"}

    model = load_model()
    if model is None:
        return {"error": "Modelo no entrenado o ruta inválida."}

    # Preparar DataFrame para la predicción
    df = pd.DataFrame([{
        "story_points": data.story_points,
        "business_value": data.business_value,
        "criticity": data.criticity.value,
        "internal_dependencies": data.internal_dependencies,
        "continuation": data.continuation,
        "story_type": data.story_type.value
    }])

    try:
        pred = model.predict(df)[0]
        prioridad = Priority(pred)
        logger.info(f"Predicción completada: {prioridad}")
        return {"prioridad": prioridad.value}
    except Exception as e:
        logger.error(f"Error en la predicción: {e}")
        return {"error": f"Error en la predicción: {e}"}
