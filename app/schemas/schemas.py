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
