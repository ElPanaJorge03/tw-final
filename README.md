# Generador de Recetas con Inventario

Proyecto de Tecnologias Web: FastAPI + PostgreSQL + SQLAlchemy + Alembic + Groq.

## Requisitos
- Python 3.12
- PostgreSQL

## Variables de entorno
Copia `.env.example` a `.env` y completa los valores.

## Desarrollo local
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Docker
```bash
docker compose up --build
```

## Endpoints
- POST /auth/register
- POST /auth/login
- GET /ingredientes
- POST /ingredientes
- PUT /ingredientes/{id}
- DELETE /ingredientes/{id}
- POST /recetas/generar
- GET /recetas
- DELETE /recetas/{id}
- POST /recetas/{id}/calificar
- GET /health
