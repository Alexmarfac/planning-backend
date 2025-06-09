# planning-backend

Este es el backend del proyecto de TFM. Está desarrollado en Python con FastAPI y permite gestionar la planificación de sprints de forma más eficiente, utilizando inteligencia artificial para apoyar algunas tareas como la generación de descripciones, criterios de aceptación y la priorización de historias.

## Tecnologías utilizadas

- Python 3.13
- FastAPI
- SQLAlchemy
- SQLite
- Uvicorn
- Scikit-learn
- Pandas y Numpy
- OpenAI API
- python-dotenv

## Estructura del proyecto

- `main.py`: punto de entrada de la aplicación FastAPI.
- `crud.py`: contiene la lógica para acceder y modificar la base de datos.
- `models.py`: define los modelos con SQLAlchemy.
- `schemas.py`: define los esquemas de datos con Pydantic.
- `database.py`: configura la conexión a SQLite.
- `ml_model.py`: contiene el modelo de machine learning y su carga.
- `routers/`: rutas separadas por funcionalidad (sprints, pbis, stories, ml).
- `services/`: lógica auxiliar, incluida la relacionada con OpenAI.
- `planning.db`: base de datos SQLite.
- `.env`: variables de entorno (no se debe subir al repositorio).

## Pasos para ejecutar el proyecto

1. Clonar el repositorio y acceder a la carpeta:

git clone https://github.com/Alexmarfac/planning-backend.git && cd planning-backend

2. Crear un entorno virtual e instalar las dependencias necesarias:

python -m venv env && env\Scripts\activate && pip install --upgrade pip && pip install -r requirements.txt

3. Crear un archivo `.env` en la raíz del proyecto con tu clave de OpenAI:

echo OPENAI_API_KEY="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" > .env

4. Ejecutar el servidor de desarrollo:

uvicorn main:app --reload --port 8888

5. Acceder a la documentación interactiva:

- Swagger UI: http://127.0.0.1:8888/docs
- ReDoc: http://127.0.0.1:8888/redoc
- [http://localhost:8888/docs](http://localhost:8888/docs)

## Notas

- El modelo de machine learning está cargado en `ml_model.py` y sirve para predecir la prioridad de las historias.
- La generación automática de descripciones y criterios se realiza a través de la API de OpenAI.
- Este proyecto está pensado para ser el backend de una herramienta más grande que también tiene una interfaz web en React (fuera de este repositorio).

## Autor

Alejandro Martinez Faci
