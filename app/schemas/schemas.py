from datetime import datetime

from pydantic import BaseModel
from pydantic import EmailStr


class UserCreate(BaseModel):
	nombre: str
	email: EmailStr
	password: str


class UserLogin(BaseModel):
	email: EmailStr
	password: str


class UserOut(BaseModel):
	id: int
	nombre: str
	email: EmailStr
	created_at: datetime

	class Config:
		from_attributes = True


class Token(BaseModel):
	access_token: str
	token_type: str


class IngredientBase(BaseModel):
	nombre: str
	cantidad: str
	unidad: str | None = None


class IngredientCreate(IngredientBase):
	pass


class IngredientUpdate(IngredientBase):
	pass


class IngredientOut(IngredientBase):
	id: int
	created_at: datetime

	class Config:
		from_attributes = True


class RecipeBase(BaseModel):
	nombre_plato: str
	ingredientes: list[dict]
	pasos: list[str]
	tiempo_estimado: str
	nivel_dificultad: str


class RecipeOut(RecipeBase):
	id: int
	prompt_usado: str
	created_at: datetime

	class Config:
		from_attributes = True


class RatingCreate(BaseModel):
	estrellas: int


class RatingOut(RatingCreate):
	id: int
	receta_id: int
	usuario_id: int
	created_at: datetime

	class Config:
		from_attributes = True
