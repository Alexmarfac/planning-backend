# reset_router.py
from fastapi import APIRouter
from models import Base
from database import engine

router = APIRouter()

@router.post("/reset-db", tags=["Mantenimiento"])
def reset_database():
    """
    Elimina TODAS las tablas y las vuelve a crear.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
        session = SessionLocal()
    try:
        seed_sprints(session)
        seed_pbis_and_stories(session)
    finally:
        session.close()

    return {"message": "Base de datos reiniciada y sembrada correctamente."}


