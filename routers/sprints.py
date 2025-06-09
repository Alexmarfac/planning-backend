import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import schemas, crud
from database import get_db

# Configurar logger
default_log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=default_log_format)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/sprints",
    tags=["Sprints"]
)

@router.post("/", response_model=schemas.Sprint, status_code=status.HTTP_201_CREATED)
def create_sprint(sprint: schemas.SprintCreate, db: Session = Depends(get_db)) -> schemas.Sprint:
    try:
        created = crud.create_sprint(db, sprint)
        logger.info(f"Sprint created with id={created.id}")
        return created
    except Exception as e:
        logger.error(f"Error creating sprint: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.get("/", response_model=List[schemas.Sprint])
def get_sprints(db: Session = Depends(get_db)) -> List[schemas.Sprint]:
    return crud.get_sprints(db)

@router.get("/{sprint_id}", response_model=schemas.Sprint)
def get_sprint_by_id(sprint_id: int, db: Session = Depends(get_db)) -> schemas.Sprint:
    sprint = crud.get_sprint_by_id(db, sprint_id)
    if not sprint:
        logger.warning(f"Sprint not found: id={sprint_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found")
    return sprint

@router.put("/{sprint_id}", response_model=schemas.Sprint)
def update_sprint(sprint_id: int, sprint_data: schemas.SprintUpdate, db: Session = Depends(get_db)) -> schemas.Sprint:
    updated = crud.update_sprint(db, sprint_id, sprint_data)
    if not updated:
        logger.warning(f"Sprint not found for update: id={sprint_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found")
    return updated

@router.delete("/{sprint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sprint(sprint_id: int, db: Session = Depends(get_db)):
    success = crud.delete_sprint(db, sprint_id)
    if not success:
        logger.warning(f"Sprint not found for delete: id={sprint_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found")
    logger.info(f"Sprint deleted: id={sprint_id}")
    return None
