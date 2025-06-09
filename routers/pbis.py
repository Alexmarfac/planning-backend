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
    prefix="/pbis",
    tags=["PBIs"]
)

@router.post("/", response_model=schemas.PBI, status_code=status.HTTP_201_CREATED)
def create_pbi(pbi: schemas.PBICreate, db: Session = Depends(get_db)) -> schemas.PBI:
    try:
        created = crud.create_pbi(db, pbi)
        logger.info(f"PBI created with id={created.id}")
        return created
    except Exception as e:
        logger.error(f"Error creating PBI: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.get("/by_sprint/{sprint_id}", response_model=List[schemas.PBI])
def get_pbis_by_sprint(sprint_id: int, db: Session = Depends(get_db)) -> List[schemas.PBI]:
    return crud.get_pbis_by_sprint(db, sprint_id)

@router.get("/{pbi_id}", response_model=schemas.PBI)
def get_pbi_by_id(pbi_id: int, db: Session = Depends(get_db)) -> schemas.PBI:
    pbi = crud.get_pbi_by_id(db, pbi_id)
    if not pbi:
        logger.warning(f"PBI not found: id={pbi_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PBI not found")
    return pbi

@router.put("/{pbi_id}", response_model=schemas.PBI)
def update_pbi(pbi_id: int, pbi_data: schemas.PBIUpdate, db: Session = Depends(get_db)) -> schemas.PBI:
    updated = crud.update_pbi(db, pbi_id, pbi_data)
    if not updated:
        logger.warning(f"PBI not found for update: id={pbi_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PBI not found")
    logger.info(f"PBI updated: id={updated.id}")
    return updated

@router.delete("/{pbi_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pbi(pbi_id: int, db: Session = Depends(get_db)):
    success = crud.delete_pbi(db, pbi_id)
    if not success:
        logger.warning(f"PBI not found for delete: id={pbi_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PBI not found")
    logger.info(f"PBI deleted: id={pbi_id}")
    return None
