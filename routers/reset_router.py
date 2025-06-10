# reset_router.py
from fastapi import APIRouter
from models import Base
from database import engine

router = APIRouter()

@router.post("/reset-db", tags=["⚠️ Mantenimiento"])
def reset_database():
    """
    ⚠️ Elimina TODAS las tablas y las vuelve a crear.
    Úsalo solo en entornos de desarrollo.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return {"message": "Base de datos reiniciada correctamente"}
