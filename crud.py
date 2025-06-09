import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import models
import schemas

logger = logging.getLogger(__name__)

# ----------------------------
# SPRINTS CRUD
# ----------------------------

def create_sprint(db: Session, sprint_in: schemas.SprintCreate) -> models.Sprint:
    """Create a new Sprint."""
    sprint = models.Sprint(**sprint_in.dict())
    try:
        db.add(sprint)
        db.commit()
        db.refresh(sprint)
        logger.info(f"Sprint created with id={sprint.id}")
        return sprint
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating sprint: {e}")
        raise


def get_sprints(db: Session) -> List[models.Sprint]:
    """Retrieve all Sprints."""
    return db.query(models.Sprint).all()


def get_sprint_by_id(db: Session, sprint_id: int) -> Optional[models.Sprint]:
    """Retrieve a Sprint by its ID."""
    return db.query(models.Sprint).get(sprint_id)


def update_sprint(db: Session, sprint_id: int, sprint_in: schemas.SprintUpdate) -> Optional[models.Sprint]:
    """Update fields of an existing Sprint."""
    sprint = db.query(models.Sprint).get(sprint_id)
    if not sprint:
        return None
    data = sprint_in.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(sprint, key, value)
    try:
        db.commit()
        db.refresh(sprint)
        logger.info(f"Sprint updated id={sprint.id}")
        return sprint
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating sprint {sprint_id}: {e}")
        raise


def delete_sprint(db: Session, sprint_id: int) -> bool:
    """Delete a Sprint by its ID."""
    sprint = db.query(models.Sprint).get(sprint_id)
    if not sprint:
        return False
    try:
        db.delete(sprint)
        db.commit()
        logger.info(f"Sprint deleted id={sprint_id}")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting sprint {sprint_id}: {e}")
        raise


# ----------------------------
# PBIs CRUD
# ----------------------------

def create_pbi(db: Session, pbi_in: schemas.PBICreate) -> models.PBI:
    """Create a new PBI."""
    pbi = models.PBI(**pbi_in.dict())
    try:
        db.add(pbi)
        db.commit()
        db.refresh(pbi)
        logger.info(f"PBI created with id={pbi.id}")
        return pbi
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating PBI: {e}")
        raise


def get_pbis_by_sprint(db: Session, sprint_id: int) -> List[models.PBI]:
    """Retrieve PBIs for a given Sprint."""
    return db.query(models.PBI).filter(models.PBI.sprint_id == sprint_id).all()


def get_pbi_by_id(db: Session, pbi_id: int) -> Optional[models.PBI]:
    """Retrieve a PBI by its ID."""
    return db.query(models.PBI).get(pbi_id)


def update_pbi(db: Session, pbi_id: int, pbi_in: schemas.PBIUpdate) -> Optional[models.PBI]:
    """Update fields of an existing PBI."""
    pbi = db.query(models.PBI).get(pbi_id)
    if not pbi:
        return None
    data = pbi_in.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(pbi, key, value)
    try:
        db.commit()
        db.refresh(pbi)
        logger.info(f"PBI updated id={pbi.id}")
        return pbi
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating PBI {pbi_id}: {e}")
        raise


def delete_pbi(db: Session, pbi_id: int) -> bool:
    """Delete a PBI by its ID."""
    pbi = db.query(models.PBI).get(pbi_id)
    if not pbi:
        return False
    try:
        db.delete(pbi)
        db.commit()
        logger.info(f"PBI deleted id={pbi_id}")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting PBI {pbi_id}: {e}")
        raise


# ----------------------------
# STORIES CRUD
# ----------------------------

def create_story(db: Session, story_in: schemas.StoryCreate, pbi_id: int) -> models.Story:
    """Create a new Story under a PBI."""
    story = models.Story(**story_in.dict(), pbi_id=pbi_id)
    try:
        db.add(story)
        db.commit()
        db.refresh(story)
        logger.info(f"Story created with id={story.id}")
        return story
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating story: {e}")
        raise


def get_stories_by_pbi(db: Session, pbi_id: int) -> List[models.Story]:
    """Retrieve Stories for a given PBI."""
    return db.query(models.Story).filter(models.Story.pbi_id == pbi_id).all()


def get_story_by_id(db: Session, story_id: int) -> Optional[models.Story]:
    """Retrieve a Story by its ID."""
    return db.query(models.Story).get(story_id)


def update_story(db: Session, story_id: int, story_in: schemas.StoryUpdate) -> Optional[models.Story]:
    """Update fields of an existing Story."""
    story = db.query(models.Story).get(story_id)
    if not story:
        return None
    data = story_in.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(story, key, value)
    try:
        db.commit()
        db.refresh(story)
        logger.info(f"Story updated id={story.id}")
        return story
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating story {story_id}: {e}")
        raise


def delete_story(db: Session, story_id: int) -> bool:
    """Delete a Story by its ID."""
    story = db.query(models.Story).get(story_id)
    if not story:
        return False
    try:
        db.delete(story)
        db.commit()
        logger.info(f"Story deleted id={story_id}")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting story {story_id}: {e}")
        raise
