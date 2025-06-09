import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import logging

from models import Base  # ← usa el Base de los modelos

# Cargar variables de entorno
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# URL base de datos
database_url = os.getenv('DATABASE_URL', 'sqlite:///./planning.db')

connect_args = {'check_same_thread': False} if database_url.startswith('sqlite') else {}
engine = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)

# Sesión
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Para FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Error en la sesión de DB: {e}")
        db.rollback()
        raise
    finally:
        db.close()
