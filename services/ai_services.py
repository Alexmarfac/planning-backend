import os
import logging
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import List, Dict, Any, Optional

import numpy as np
import pandas as pd
import joblib
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, Field, validator, ValidationError

# Configuración de logging
default_log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=default_log_format)
logger = logging.getLogger(__name__)

# API Key de OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Ruta al modelo
MODEL_FILE = Path(__file__).parent.parent / 'ml' / 'modelo_prioridad.pkl'

# --- SCHEMAS ---
class PriorityCalcInput(BaseModel):
    story_points: float = Field(..., alias='story_points')
    business_value: float = Field(..., alias='business_value')
    criticidad: float = Field(..., alias='criticidad')
    internal_dependencies: float = Field(..., alias='internal_dependencies')
    continuation: float = Field(..., alias='continuation')
    story_type: str = Field(..., alias='story_type')

    @validator('*')
    def non_negative(cls, v):
        if isinstance(v, (int, float)) and v < 0:
            raise ValueError("Los valores numéricos no pueden ser negativos")
        return v

    @validator('story_type')
    def clean_str(cls, v):
        return v.strip().capitalize()  # Ej: "technical" → "Technical"

class SprintGoalInput(BaseModel):
    stories: List[str]

    @validator('stories')
    def non_empty(cls, v):
        if not v:
            raise ValueError("La lista de historias no puede estar vacía")
        return v

class DescriptionInput(BaseModel):
    idea_general: str = Field(..., min_length=10)

# --- MODELO ---
@lru_cache(maxsize=1)
def load_priority_model() -> Optional[Any]:
    try:
        if MODEL_FILE.exists():
            logger.info(f'Cargando modelo ML desde {MODEL_FILE}')
            return joblib.load(MODEL_FILE)
        logger.warning(f'No se encontró el modelo en {MODEL_FILE}')
    except Exception as e:
        logger.error(f'Error cargando modelo ML: {e}')
    return None

def calculate_priority(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcula la prioridad de una historia según el modelo entrenado.
    """
    try:
        inp = PriorityCalcInput(**data)
    except ValidationError as ve:
        logger.error(f'Error validando datos para prioridad: {ve}')
        return {'error': str(ve)}

    model = load_priority_model()
    if model is None:
        return {'error': 'Modelo ML no disponible.'}

    try:
        df = pd.DataFrame([{
            "Story Points": inp.story_points,
            "Business Value": inp.business_value,
            "Criticidad": inp.criticidad,
            "Nº dep inter": inp.internal_dependencies,
            "Continuacion": inp.continuation,
            "Story Type": inp.story_type  # Ya viene como "User", "Technical", etc.
        }])

        pred = model.predict(df)[0]
        prioridad_num = int(pred)
        mapa_prioridad = {0: "baja", 1: "media", 2: "alta"}
        prioridad_str = mapa_prioridad.get(prioridad_num, "desconocida")

        logger.info(f'Prioridad predicha: {prioridad_num} → {prioridad_str}')
        return {
            'prioridad_num': prioridad_num,
            'prioridad': prioridad_str
        }

    except Exception as e:
        logger.error(f'Error en predicción de prioridad: {e}')
        return {'error': 'Error durante predicción ML.'}

# --- FUNCIONES CON GPT ---
def generate_sprint_goal(input_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        inp = SprintGoalInput(**input_data)
    except ValidationError as ve:
        logger.error(f'Error validando historias: {ve}')
        return {'error': str(ve)}

    prompt = (
        f"Eres un asistente ágil experto en Scrum.\n"
        f"Dadas estas historias: {'; '.join(inp.stories)}\n"
        "Redacta un objetivo de sprint en español, una sola frase, máximo 20 palabras."
    )

    try:
        resp = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {'role': 'system', 'content': 'Eres un asistente experto en metodologías ágiles.'},
                {'role': 'user', 'content': prompt}
            ],
            temperature=0.7,
            max_tokens=60
        )
        return {'sprint_goal': resp.choices[0].message.content.strip()}
    except OpenAIError as e:
        logger.error(f'Error con OpenAI: {e}')
        return {'error': 'Error al generar objetivo de sprint.'}

def generate_description_and_acceptance(input_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        inp = DescriptionInput(**input_data)
    except ValidationError as ve:
        logger.error(f'Error validando idea general: {ve}')
        return {'error': str(ve)}

    prompt = (
        "Eres un Asistente Ágil experto en Scrum.\n"
        f"Idea general: \"{inp.idea_general}\".\n"
        "Devuelve un JSON válido con doble comilla, con los siguientes campos:\n"
        "  \"historia\": descripción clara en formato historia de usuario,\n"
        "  \"criterios\": lista de criterios de aceptación.\n"
        "No añadas ninguna explicación ni texto adicional, solo el JSON."
    )

    try:
        resp = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {'role': 'system', 'content': 'Eres un asistente experto en desarrollo ágil.'},
                {'role': 'user', 'content': prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        content = resp.choices[0].message.content.strip()
        logger.info(f"Respuesta cruda IA: {content}")

        # Limpieza segura del bloque ```json ... ```
        content = re.sub(r'^```(?:json)?\s*', '', content)
        content = re.sub(r'\s*```$', '', content)

        result = json.loads(content)
        return result

    except json.JSONDecodeError as je:
        logger.error(f'Error parseando JSON: {je}')
        return {'error': 'Error al parsear la respuesta de la IA.'}
    except OpenAIError as oe:
        logger.error(f'Error con OpenAI: {oe}')
        return {'error': 'Error al generar descripción y criterios.'}
    except Exception as e:
        logger.error(f'Error inesperado: {e}')
        return {'error': 'Error inesperado durante la generación.'}
