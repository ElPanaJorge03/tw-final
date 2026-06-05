from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
	__tablename__ = "usuarios"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	nombre: Mapped[str] = mapped_column(String(255), nullable=False)
	email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
	password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

	ingredientes = relationship("Ingredient", back_populates="usuario", cascade="all, delete-orphan")
	recetas = relationship("Recipe", back_populates="usuario", cascade="all, delete-orphan")
	calificaciones = relationship("Rating", back_populates="usuario", cascade="all, delete-orphan")


class Ingredient(Base):
	__tablename__ = "ingredientes"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
	nombre: Mapped[str] = mapped_column(String(255), nullable=False)
	cantidad: Mapped[str] = mapped_column(String(100), nullable=False)
	unidad: Mapped[str | None] = mapped_column(String(50), nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

	usuario = relationship("User", back_populates="ingredientes")


class Recipe(Base):
	__tablename__ = "recetas"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
	nombre_plato: Mapped[str] = mapped_column(String(255), nullable=False)
	ingredientes_json: Mapped[str] = mapped_column(Text, nullable=False)
	pasos_json: Mapped[str] = mapped_column(Text, nullable=False)
	tiempo_estimado: Mapped[str] = mapped_column(String(100), nullable=False)
	nivel_dificultad: Mapped[str] = mapped_column(String(50), nullable=False)
	prompt_usado: Mapped[str] = mapped_column(Text, nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

	usuario = relationship("User", back_populates="recetas")
	calificaciones = relationship("Rating", back_populates="receta", cascade="all, delete-orphan")


class Rating(Base):
	__tablename__ = "calificaciones"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	receta_id: Mapped[int] = mapped_column(ForeignKey("recetas.id"), nullable=False)
	usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
	estrellas: Mapped[int] = mapped_column(Integer, nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

	receta = relationship("Recipe", back_populates="calificaciones")
	usuario = relationship("User", back_populates="calificaciones")
