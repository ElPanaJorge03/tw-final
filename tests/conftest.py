import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.database import get_db
from app.main import app
from app.models.models import Ingredient
from app.models.models import Rating
from app.models.models import Recipe
from app.models.models import User


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
	raise RuntimeError("DATABASE_URL is not set for tests")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> None:
	Base.metadata.create_all(bind=engine)
	yield
	Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
	db = TestingSessionLocal()
	try:
		yield db
	finally:
		db.close()


@pytest.fixture()
def client(db_session):
	def override_get_db():
		try:
			yield db_session
		finally:
			pass

	app.dependency_overrides[get_db] = override_get_db

	for model in (Rating, Recipe, Ingredient, User):
		db_session.query(model).delete()
		db_session.commit()

	with TestClient(app) as test_client:
		yield test_client

	app.dependency_overrides.clear()
