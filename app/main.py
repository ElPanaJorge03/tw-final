from fastapi import FastAPI

from app.routers import auth
from app.routers import ingredientes
from app.routers import recetas

app = FastAPI()

app.include_router(auth.router)
app.include_router(ingredientes.router)
app.include_router(recetas.router)


@app.get("/health")
def health_check() -> dict:
	return {"status": "ok"}
