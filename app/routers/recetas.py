import json

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Ingredient
from app.models.models import Rating
from app.models.models import Recipe
from app.models.models import User
from app.routers.auth import get_current_user
from app.schemas.schemas import RatingCreate
from app.schemas.schemas import RatingOut
from app.schemas.schemas import RecipeOut
from app.services.llm_service import LLMService
from app.services.llm_service import LLMServiceError

router = APIRouter(prefix="/recetas", tags=["recetas"])


def _get_inventory(db: Session, user_id: int) -> list[dict]:
	ingredientes = db.query(Ingredient).filter(Ingredient.usuario_id == user_id).all()
	return [
		{
			"nombre": item.nombre,
			"cantidad": item.cantidad,
			"unidad": item.unidad,
		}
		for item in ingredientes
	]


@router.post("/generar", response_model=RecipeOut, status_code=status.HTTP_201_CREATED)
def generar_receta(
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user),
) -> RecipeOut:
	inventario = _get_inventory(db, current_user.id)
	service = LLMService()
	try:
		data = service.generate_recipe(inventario)
	except LLMServiceError as exc:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

	receta = Recipe(
		usuario_id=current_user.id,
		nombre_plato=data["nombre_plato"],
		ingredientes_json=json.dumps(data["ingredientes"], ensure_ascii=False),
		pasos_json=json.dumps(data["pasos"], ensure_ascii=False),
		tiempo_estimado=data["tiempo_estimado"],
		nivel_dificultad=data["nivel_dificultad"],
		prompt_usado=data["prompt_usado"],
	)
	db.add(receta)
	db.commit()
	db.refresh(receta)

	return RecipeOut(
		id=receta.id,
		nombre_plato=receta.nombre_plato,
		ingredientes=json.loads(receta.ingredientes_json),
		pasos=json.loads(receta.pasos_json),
		tiempo_estimado=receta.tiempo_estimado,
		nivel_dificultad=receta.nivel_dificultad,
		prompt_usado=receta.prompt_usado,
		created_at=receta.created_at,
	)


@router.get("", response_model=list[RecipeOut])
def list_recetas(
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user),
) -> list[RecipeOut]:
	recetas = (
		db.query(Recipe)
		.filter(Recipe.usuario_id == current_user.id)
		.order_by(Recipe.created_at.desc())
		.all()
	)
	return [
		RecipeOut(
			id=receta.id,
			nombre_plato=receta.nombre_plato,
			ingredientes=json.loads(receta.ingredientes_json),
			pasos=json.loads(receta.pasos_json),
			tiempo_estimado=receta.tiempo_estimado,
			nivel_dificultad=receta.nivel_dificultad,
			prompt_usado=receta.prompt_usado,
			created_at=receta.created_at,
		)
		for receta in recetas
	]


@router.delete("/{receta_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_receta(
	receta_id: int,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user),
) -> None:
	receta = (
		db.query(Recipe)
		.filter(Recipe.id == receta_id, Recipe.usuario_id == current_user.id)
		.first()
	)
	if not receta:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada")

	db.delete(receta)
	db.commit()
	return None


@router.post("/{receta_id}/calificar", response_model=RatingOut)
def calificar_receta(
	receta_id: int,
	calificacion: RatingCreate,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user),
) -> RatingOut:
	if calificacion.estrellas < 1 or calificacion.estrellas > 5:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estrellas fuera de rango")

	receta = (
		db.query(Recipe)
		.filter(Recipe.id == receta_id, Recipe.usuario_id == current_user.id)
		.first()
	)
	if not receta:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada")

	rating = Rating(
		receta_id=receta.id,
		usuario_id=current_user.id,
		estrellas=calificacion.estrellas,
	)
	db.add(rating)
	db.commit()
	db.refresh(rating)
	return rating
