# routers/reset_router.py
from fastapi import APIRouter
from models import Base
from database import engine, SessionLocal
from create_db import seed_sprints, seed_pbis_and_stories

router = APIRouter()

@router.post("/reset-db", tags=["Mantenimiento"])
def reset_database():
    """
    ⚠️ Elimina TODAS las tablas y las vuelve a crear con datos de ejemplo.
    """
    # 1. Borrar tablas
    Base.metadata.drop_all(bind=engine)

    # 2. Crear tablas
    Base.metadata.create_all(bind=engine)

    # 3. Sembrar datos
    session = SessionLocal()
    try:
        seed_sprints(session)
        seed_pbis_and_stories(session)
    finally:
        session.close()

    return {"message": "Base de datos reiniciada y sembrada correctamente."}
