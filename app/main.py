from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routers import auth
from app.routers import ingredientes
from app.routers import recetas

app = FastAPI()

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