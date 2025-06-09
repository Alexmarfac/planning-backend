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
    prefix="/stories",
    tags=["Stories"]
)

@router.post("/{pbi_id}", response_model=schemas.Story, status_code=status.HTTP_201_CREATED)
def create_story(pbi_id: int, story: schemas.StoryCreate, db: Session = Depends(get_db)) -> schemas.Story:
    try:
        created = crud.create_story(db, story, pbi_id)
        logger.info(f"Story created with id={created.id} under PBI {pbi_id}")
        return created
    except Exception as e:
        logger.error(f"Error creating story: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/by_pbi/{pbi_id}", response_model=List[schemas.Story])
def get_stories(pbi_id: int, db: Session = Depends(get_db)) -> List[schemas.Story]:
    return crud.get_stories_by_pbi(db, pbi_id)

@router.get("/{story_id}", response_model=schemas.Story)
def get_story_by_id(story_id: int, db: Session = Depends(get_db)) -> schemas.Story:
    story = crud.get_story_by_id(db, story_id)
    if not story:
        logger.warning(f"Story not found: id={story_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    return story

@router.put("/{story_id}", response_model=schemas.Story)
def update_story(story_id: int, story_data: schemas.StoryUpdate, db: Session = Depends(get_db)) -> schemas.Story:
    updated = crud.update_story(db, story_id, story_data)
    if not updated:
        logger.warning(f"Story not found for update: id={story_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    return updated

@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_story(story_id: int, db: Session = Depends(get_db)):
    success = crud.delete_story(db, story_id)
    if not success:
        logger.warning(f"Story not found for delete: id={story_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    logger.info(f"Story deleted: id={story_id}")
    return None
