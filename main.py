import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from database import Base, engine
from routers import sprints, pbis, stories, ml

# Configurar logging
default_log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=default_log_format)
logger = logging.getLogger(__name__)

# Inicializar la base de datos
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tablas creadas o existentes en la base de datos.")
    except SQLAlchemyError as e:
        logger.error(f"Error creando las tablas en la base de datos: {e}")
        raise

# Configuración de la aplicación FastAPI
app = FastAPI(
    title="Sprint Planning Tool",
    version="1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Permitir CORS (modificar orígenes según necesidades)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Eventos de arranque y apagado\@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("Aplicación arrancada y base de datos inicializada.")

@ app.on_event("shutdown")
def on_shutdown():
    logger.info("Aplicación detenida.")

# Incluir routers con prefijos y tags para mejor organización
def include_routers(app: FastAPI):
    app.include_router(
        sprints.router,
        prefix="/sprints",
        tags=["Sprints"],
    )
    app.include_router(
        pbis.router,
        prefix="/pbis",
        tags=["PBIs"],
    )
    app.include_router(
        stories.router,
        prefix="/stories",
        tags=["Stories"],
    )
    app.include_router(
        ml.router,
        prefix="/ml",
        tags=["ML"],
    )

# Registrar routers
def main():
    include_routers(app)
    logger.info("Routers registrados en la aplicación.")


# Ejecutar registro de routers al importar
main()

# Punto de entrada para uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
