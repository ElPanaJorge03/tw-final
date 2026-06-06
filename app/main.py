import time
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import Base
from app.database import engine
from app.routers import auth
from app.routers import ingredientes
from app.routers import recetas

# Import all models so Base.metadata knows about them
import app.models.models  # noqa: F401

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Create tables if they don't exist, retrying until the DB is ready."""
    for attempt in range(1, 6):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created / verified successfully.")
            return
        except Exception as exc:
            logger.warning("DB not ready (attempt %d/5): %s", attempt, exc)
            if attempt < 5:
                time.sleep(2)
    logger.error("Could not connect to the database after 5 attempts.")

app.include_router(auth.router)
app.include_router(ingredientes.router)
app.include_router(recetas.router)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("frontend/index.html")

@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}