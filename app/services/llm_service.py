import json
import os
from typing import Any

from groq import Groq


class LLMServiceError(Exception):
	pass


class LLMService:
	def __init__(self) -> None:
		api_key = os.getenv("GROQ_API_KEY")
		if not api_key:
			raise RuntimeError("GROQ_API_KEY is not set")

		self._client = Groq(api_key=api_key)
		self._model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

	def generate_recipe(self, inventario: list[dict[str, Any]]) -> dict[str, Any]:
		if not inventario:
			raise LLMServiceError("El inventario esta vacio")

		prompt = self._build_prompt(inventario)
		content = self._call_llm(prompt)
		data = self._parse_response(content)

		data["prompt_usado"] = prompt
		return data

	def _build_prompt(self, inventario: list[dict[str, Any]]) -> str:
		ingredientes = []
		for item in inventario:
			nombre = str(item.get("nombre", "")).strip()
			cantidad = str(item.get("cantidad", "")).strip()
			unidad = str(item.get("unidad", "")).strip()
			if unidad:
				ingredientes.append(f"- {nombre}: {cantidad} {unidad}")
			else:
				ingredientes.append(f"- {nombre}: {cantidad}")

		inventario_texto = "\n".join(ingredientes)
		return (
			"Eres un asistente que genera recetas basadas en un inventario. "
			"Responde SOLO con un JSON valido usando exactamente estos campos: "
			"nombre_plato, ingredientes, pasos, tiempo_estimado, nivel_dificultad.\n\n"
			"Inventario disponible:\n"
			f"{inventario_texto}\n\n"
			"Reglas:\n"
			"- ingredientes es una lista de objetos con nombre, cantidad y unidad.\n"
			"- pasos es una lista de strings ordenados.\n"
			"- nivel_dificultad debe ser: Facil, Medio o Dificil.\n"
		)

	def _call_llm(self, prompt: str) -> str:
		import groq
		try:
			response = self._client.chat.completions.create(
				model=self._model,
				messages=[
					{"role": "system", "content": "Genera recetas en JSON estricto."},
					{"role": "user", "content": prompt},
				],
				temperature=0.2,
				response_format={"type": "json_object"},
			)
			content = response.choices[0].message.content
			if not content:
				raise LLMServiceError("Respuesta vacia del LLM")
			return content
		except groq.APIConnectionError as exc:
			raise LLMServiceError(f"No se pudo conectar a la API de Groq: {exc}") from exc
		except groq.AuthenticationError as exc:
			raise LLMServiceError("Clave de API de Groq invalida o no autorizada") from exc
		except groq.RateLimitError as exc:
			raise LLMServiceError("Limite de peticiones de la API de Groq excedido") from exc
		except Exception as exc:
			raise LLMServiceError(f"Error inesperado al llamar a Groq: {exc}") from exc

	def _parse_response(self, content: str) -> dict[str, Any]:
		payload = self._extract_json(content)
		try:
			data = json.loads(payload)
		except json.JSONDecodeError as exc:
			raise LLMServiceError("Respuesta del LLM no es JSON valido") from exc

		required_fields = {
			"nombre_plato",
			"ingredientes",
			"pasos",
			"tiempo_estimado",
			"nivel_dificultad",
		}
		missing = required_fields - set(data.keys())
		if missing:
			raise LLMServiceError("Faltan campos requeridos en la respuesta del LLM")

		return data

	def _extract_json(self, content: str) -> str:
		# Strip common markdown fences without altering JSON content.
		trimmed = content.strip()
		if trimmed.startswith("```"):
			trimmed = trimmed.strip("`")
			trimmed = trimmed.replace("json", "", 1).strip()
		return trimmed
