from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Ingredient
from app.models.models import User
from app.routers.auth import get_current_user
from app.schemas.schemas import IngredientCreate
from app.schemas.schemas import IngredientOut
from app.schemas.schemas import IngredientUpdate

router = APIRouter(prefix="/ingredientes", tags=["ingredientes"])


def _validate_ingredient_fields(nombre: str, cantidad: str) -> None:
	if not nombre.strip():
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nombre requerido")
	if not cantidad.strip():
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cantidad requerida")


@router.get("", response_model=list[IngredientOut])
def list_ingredientes(
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user),
) -> list[IngredientOut]:
	return (
		db.query(Ingredient)
		.filter(Ingredient.usuario_id == current_user.id)
		.order_by(Ingredient.created_at.desc())
		.all()
	)


@router.post("", response_model=IngredientOut, status_code=status.HTTP_201_CREATED)
def create_ingrediente(
	ingrediente_in: IngredientCreate,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user),
) -> IngredientOut:
	_validate_ingredient_fields(ingrediente_in.nombre, ingrediente_in.cantidad)
	ingrediente = Ingredient(
		usuario_id=current_user.id,
		nombre=ingrediente_in.nombre.strip(),
		cantidad=ingrediente_in.cantidad.strip(),
		unidad=ingrediente_in.unidad.strip() if ingrediente_in.unidad else None,
	)
	db.add(ingrediente)
	db.commit()
	db.refresh(ingrediente)
	return ingrediente


@router.put("/{ingrediente_id}", response_model=IngredientOut)
def update_ingrediente(
	ingrediente_id: int,
	ingrediente_in: IngredientUpdate,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user),
) -> IngredientOut:
	_validate_ingredient_fields(ingrediente_in.nombre, ingrediente_in.cantidad)
	ingrediente = (
		db.query(Ingredient)
		.filter(Ingredient.id == ingrediente_id, Ingredient.usuario_id == current_user.id)
		.first()
	)
	if not ingrediente:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingrediente no encontrado")

	ingrediente.nombre = ingrediente_in.nombre.strip()
	ingrediente.cantidad = ingrediente_in.cantidad.strip()
	ingrediente.unidad = ingrediente_in.unidad.strip() if ingrediente_in.unidad else None
	db.commit()
	db.refresh(ingrediente)
	return ingrediente


@router.delete("/{ingrediente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingrediente(
	ingrediente_id: int,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user),
) -> None:
	ingrediente = (
		db.query(Ingredient)
		.filter(Ingredient.id == ingrediente_id, Ingredient.usuario_id == current_user.id)
		.first()
	)
	if not ingrediente:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingrediente no encontrado")

	db.delete(ingrediente)
	db.commit()
	return None
