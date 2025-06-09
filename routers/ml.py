import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
from database import get_db
from services.ai_services import (
    calculate_priority,
    generate_sprint_goal,
    generate_description_and_acceptance,
    PriorityCalcInput,
    DescriptionInput,
    SprintGoalInput
)
from schemas import Criticity, StoryType, Priority  # Asegúrate de importar los enums si están ahí

# Configuración de logger
default_log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=default_log_format)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ml",
    tags=["ML"]
)

# --- Endpoints ---

@router.post("/prioridad/", status_code=status.HTTP_200_OK)
def obtener_prioridad(
    data: PriorityCalcInput
) -> Dict[str, Any]:
    """Calcula la prioridad de una historia usando ML con todas las características relevantes."""
    result = calculate_priority(data.dict(by_alias=True))
    if 'error' in result:
        logger.error(f"Error calculando prioridad: {result['error']}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result['error']
        )
    logger.info("Prioridad calculada correctamente")
    return {'prioridad': result['prioridad']}


@router.post("/calcular_prioridades/{sprint_id}/", status_code=status.HTTP_200_OK)
def calcular_prioridades_para_sprint(
    sprint_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, List[Dict[str, Any]]]:
    """Calcula y ordena prioridades de todas las historias de un sprint usando todas las características."""
    sprint = db.query(models.Sprint).get(sprint_id)
    if not sprint:
        logger.warning(f"Sprint no encontrado: id={sprint_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprint not found"
        )

    results: List[Dict[str, Any]] = []
    for pbi in sprint.pbis:
        for story in pbi.stories:
            try:
                payload = {
                    "story_points": story.story_points or 0,
                    "business_value": story.business_value or 0,
                    "criticidad": float(story.criticity) if story.criticity is not None else 0,
                    "internal_dependencies": story.internal_dependencies or 0,
                    "continuation": story.continuation or 0,
                    "story_type": {1: "user", 2: "technical"}.get(story.story_type, "user")
                }

                res = calculate_priority(payload)
                if 'error' not in res:
                    story.priority = res['prioridad']
                    results.append({
                        'story_id': story.id,
                        'title': story.title,
                        'prioridad': res['prioridad']
                    })
            except Exception as e:
                logger.error(f"Error procesando story {story.id}: {e}")

    db.commit()
    ordered = sorted(results, key=lambda x: x['prioridad'], reverse=True)
    logger.info("Prioridades calculadas y ordenadas para sprint %s", sprint_id)
    return {'ordenadas_por_prioridad': ordered}


@router.get("/sprint_goal/{sprint_id}", status_code=status.HTTP_200_OK)
def obtener_sprint_goal(
    sprint_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Genera objetivo de sprint a partir de títulos y descripciones."""
    stories = (
        db.query(models.Story)
        .join(models.PBI)
        .filter(models.PBI.sprint_id == sprint_id)
        .all()
    )
    if not stories:
        logger.warning(f"No se encontraron historias para sprint {sprint_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No stories found"
        )

    try:
        goal_input = SprintGoalInput(
            stories=[f"{s.title}. {s.raw_description or ''}" for s in stories]
        )
    except Exception as e:
        logger.error(f"Error validando input para sprint goal: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    res = generate_sprint_goal(goal_input.dict())
    if 'error' in res:
        logger.error(f"Error generando objetivo de sprint: {res['error']}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=res['error']
        )
    logger.info("Objetivo de sprint generado para sprint %s", sprint_id)
    return {'sprint_id': str(sprint_id), 'goal': res['sprint_goal']}


@router.post("/stories/describir_criterios/{story_id}", status_code=status.HTTP_200_OK)
def generar_descripcion_criterios(
    story_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Genera descripción y criterios de aceptación para una historia."""
    story = db.query(models.Story).get(story_id)
    if not story:
        logger.warning(f"Historia no encontrada: id={story_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )

    try:
        desc_input = DescriptionInput(idea_general=story.raw_description or '')
    except Exception as e:
        logger.error(f"Error validando idea general: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    res = generate_description_and_acceptance(desc_input.dict())
    if 'error' in res:
        logger.error(f"Error generando descripción/criterios: {res['error']}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=res['error']
        )

    story.formatted_description = res.get('historia', '')
    story.acceptance_criteria = "\n".join(res.get('criterios', []))
    db.commit()
    logger.info(f"Descripción y criterios actualizados para story id={story_id}")

    return {
        'id': story.id,
        'formatted_description': story.formatted_description,
        'acceptance_criteria': story.acceptance_criteria
    }
