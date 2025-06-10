#!/usr/bin/env python3
import logging
from datetime import date
from sqlalchemy.exc import SQLAlchemyError

from database import engine, SessionLocal
from models import Base, Sprint, PBI, Story
from schemas import Criticity, StoryType

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def seed_sprints(session):
    example = {
        "Sprint 1": (date(2025, 4, 1), date(2025, 4, 15)),
        "Sprint 2": (date(2025, 4, 16), date(2025, 4, 30)),
    }
    for name, (start, end) in example.items():
        sprint = session.query(Sprint).filter_by(name=name).first()
        if not sprint:
            sprint = Sprint(name=name, start_date=start, end_date=end)
            session.add(sprint)
            logger.info(f"Sembrando Sprint: {name}")
    session.commit()


def seed_pbis_and_stories(session):
    templates = {
        "Sprint 1": [
            {
                "title": "PBI Login y Seguridad",
                "description": "Autenticación y gestión de sesiones",
                "stories": [
                    {"title": "Usuario puede iniciar sesión", "raw_description": "Login básico", "criticity": 2, "story_points": 3, "business_value": 8, "complexity": 2, "story_type": StoryType.USER, "continuation": 0, "internal_dependencies": 0},
                    {"title": "Usuario puede cerrar sesión", "raw_description": "Logout visible y seguro", "criticity": 1, "story_points": 1, "business_value": 5, "complexity": 1, "story_type": StoryType.TECHNICAL, "continuation": 0, "internal_dependencies": 1},
                    {"title": "Bloqueo tras intentos fallidos", "raw_description": "Bloqueo tras 3 intentos", "criticity": 4, "story_points": 5, "business_value": 6, "complexity": 3, "story_type": StoryType.USER, "continuation": 0, "internal_dependencies": 1},
                    {"title": "Recuperación de contraseña", "raw_description": "Enlace para reset", "criticity": 2, "story_points": 3, "business_value": 7, "complexity": 2, "story_type": StoryType.USER, "continuation": 0, "internal_dependencies": 0},
                    {"title": "Validación de correo", "raw_description": "Email válido al registrarse", "criticity": 1, "story_points": 2, "business_value": 5, "complexity": 1, "story_type": StoryType.TECHNICAL, "continuation": 0, "internal_dependencies": 1},
                    {"title": "Registro de actividad", "raw_description": "Log de sesiones", "criticity": 2, "story_points": 3, "business_value": 4, "complexity": 2, "story_type": StoryType.TECHNICAL, "continuation": 0, "internal_dependencies": 1},
                    {"title": "Inicio de sesión con doble factor", "raw_description": "OTP por email", "criticity": 5, "story_points": 5, "business_value": 9, "complexity": 4, "story_type": StoryType.USER, "continuation": 0, "internal_dependencies": 1},
                    {"title": "Página de error personalizada", "raw_description": "Pantalla bonita si falla login", "criticity": 1, "story_points": 1, "business_value": 3, "complexity": 1, "story_type": StoryType.USER, "continuation": 0, "internal_dependencies": 0},
                ]
            }
        ],
        "Sprint 2": [
            {
                "title": "PBI Perfil de Usuario",
                "description": "Gestión del perfil del usuario",
                "stories": [
                    {"title": "Editar perfil", "raw_description": "Modificar nombre, email", "criticity": 2, "story_points": 3, "business_value": 6, "complexity": 2, "story_type": StoryType.USER, "continuation": 0, "internal_dependencies": 0},
                    {"title": "Subir foto de perfil", "raw_description": "Imagen visible", "criticity": 1, "story_points": 2, "business_value": 4, "complexity": 1, "story_type": StoryType.USER, "continuation": 0, "internal_dependencies": 0},
                    {"title": "Eliminar cuenta", "raw_description": "Borrar perfil del sistema", "criticity": 3, "story_points": 5, "business_value": 7, "complexity": 3, "story_type": StoryType.USER, "continuation": 0, "internal_dependencies": 1},
                    {"title": "Cambiar contraseña", "raw_description": "Seguridad de cuenta", "criticity": 2, "story_points": 3, "business_value": 5, "complexity": 2, "story_type": StoryType.USER, "continuation": 0, "internal_dependencies": 1},
                    {"title": "Ver historial de sesiones", "raw_description": "Lista de inicios recientes", "criticity": 2, "story_points": 3, "business_value": 6, "complexity": 2, "story_type": StoryType.TECHNICAL, "continuation": 0, "internal_dependencies": 1},
                    {"title": "Notificaciones por email", "raw_description": "Avisos por cambios", "criticity": 2, "story_points": 2, "business_value": 4, "complexity": 2, "story_type": StoryType.TECHNICAL, "continuation": 0, "internal_dependencies": 1},
                    {"title": "Configurar visibilidad de perfil", "raw_description": "Privado o público", "criticity": 3, "story_points": 3, "business_value": 5, "complexity": 2, "story_type": StoryType.USER, "continuation": 0, "internal_dependencies": 1},
                    {"title": "Validación de cambios", "raw_description": "Verificación de seguridad", "criticity": 5, "story_points": 4, "business_value": 7, "complexity": 3, "story_type": StoryType.TECHNICAL, "continuation": 0, "internal_dependencies": 1},
                ]
            }
        ]
    }

    for sprint_name, pbis in templates.items():
        sprint = session.query(Sprint).filter_by(name=sprint_name).first()
        if not sprint:
            logger.warning(f"Sprint {sprint_name} no encontrado.")
            continue

        for pbi_data in pbis:
            pbi = session.query(PBI).filter_by(title=pbi_data["title"], sprint_id=sprint.id).first()
            if not pbi:
                pbi = PBI(title=pbi_data["title"], description=pbi_data["description"], sprint_id=sprint.id)
                session.add(pbi)
                session.flush()
                logger.info(f"Sembrando PBI: {pbi.title} en {sprint_name}")

            for story_data in pbi_data["stories"]:
                story = session.query(Story).filter_by(title=story_data["title"], pbi_id=pbi.id).first()
                if not story:
                    story = Story(**story_data, pbi_id=pbi.id)
                    session.add(story)
                    logger.info(f"  - Sembrando Story: {story.title}")
    session.commit()


def main():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tablas creadas o existentes.")
    except SQLAlchemyError as err:
        logger.error(f"Error creando tablas: {err}")
        return

    session = SessionLocal()
    try:
        seed_sprints(session)
        seed_pbis_and_stories(session)
        logger.info("Datos iniciales sembrados correctamente.")
    except SQLAlchemyError as err:
        session.rollback()
        logger.error(f"Error sembrando datos: {err}")
    finally:
        session.close()


if __name__ == '__main__':
    main()
