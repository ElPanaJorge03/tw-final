import os

import pytest

from app.services.llm_service import LLMService
from app.services.llm_service import LLMServiceError


@pytest.fixture(autouse=True)
def set_groq_key(monkeypatch):
	monkeypatch.setenv("GROQ_API_KEY", "test-key")


def test_validar_ingredientes_vacios():
	service = LLMService()
	with pytest.raises(LLMServiceError):
		service.generate_recipe([])


def test_validar_ingredientes_validos(monkeypatch):
	service = LLMService()

	def fake_call_llm(prompt: str) -> str:
		return (
			"{\"nombre_plato\": \"Pasta\", "
			"\"ingredientes\": [{\"nombre\": \"pasta\", \"cantidad\": \"200\", \"unidad\": \"g\"}], "
			"\"pasos\": [\"Hervir\"], "
			"\"tiempo_estimado\": \"10 minutos\", "
			"\"nivel_dificultad\": \"Facil\"}"
		)

	monkeypatch.setattr(service, "_call_llm", fake_call_llm)
	data = service.generate_recipe([
		{"nombre": "pasta", "cantidad": "200", "unidad": "g"},
	])
	assert data["nombre_plato"] == "Pasta"
	assert data["nivel_dificultad"] == "Facil"
	assert data["prompt_usado"]


def test_generar_prompt():
	service = LLMService()
	prompt = service._build_prompt([
		{"nombre": "arroz", "cantidad": "1", "unidad": "taza"},
	])
	assert "arroz" in prompt
	assert "taza" in prompt


def test_parseo_respuesta_llm_valida():
	service = LLMService()
	content = (
		"{\"nombre_plato\": \"Sopa\", "
		"\"ingredientes\": [], "
		"\"pasos\": [\"Paso 1\"], "
		"\"tiempo_estimado\": \"5 minutos\", "
		"\"nivel_dificultad\": \"Facil\"}"
	)
	data = service._parse_response(content)
	assert data["nombre_plato"] == "Sopa"


def test_parseo_respuesta_llm_invalida():
	service = LLMService()
	with pytest.raises(LLMServiceError):
		service._parse_response("no json")
