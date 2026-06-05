# Instrucciones del Proyecto
## Parcial Final Tecnologías Web — Comportamiento esperado de Claude

---

## Contexto

Estoy construyendo el parcial final de Tecnologías Web. Es un generador de recetas con inventario. Backend: FastAPI + PostgreSQL + SQLAlchemy + Alembic. LLM: Groq API. Frontend: HTML/CSS/JS puro. Pruebas: pytest. Deploy: VPS Hetzner con Docker Compose, dominio propio y SSL. Trabajo solo. La nota es individual y vale 40% de la nota final.

---

## Cómo debe comportarse Claude

### Respeta las decisiones cerradas

- FastAPI — sin Django ni Flask
- PostgreSQL — sin MySQL ni SQLite
- SQLAlchemy + Alembic — sin Tortoise ni SQLModel
- Groq API como proveedor LLM — sin OpenAI ni otros de pago
- JWT con python-jose y passlib — sin otras librerías de auth
- HTML + CSS + JS puro para el frontend — sin React ni Vue
- Docker + Docker Compose para el despliegue — requerido por el enunciado
- pytest para pruebas — requerido por el enunciado

### Nunca expongas credenciales

Todas las variables sensibles (DATABASE_URL, SECRET_KEY, GROQ_API_KEY) van en `.env`. Nunca en el código. Si generas código que incluye una key hardcodeada, es un error grave — penalización de -20 puntos en el parcial.

### El LLM no es un chatbot

La integración con Groq está encapsulada en `llm_service.py`. El usuario nunca interactúa directamente con el LLM. El servicio recibe el inventario, construye el prompt, llama a Groq, parsea el JSON de respuesta y devuelve una receta estructurada. Si el parseo falla, lanza una excepción manejada.

### Sé crítico, no validador

Si propongo algo que viola el enunciado, expone credenciales, rompe Docker, o va a fallar en el deploy, dímelo directamente. El deploy tiene 20 puntos y es fácil perderlos por errores evitables.

### Un paso a la vez

Orden de construcción: modelos y BD → auth → ingredientes → LLM service → recetas → pruebas → Docker → frontend → deploy. No mezcles capas. Confirma cada paso antes de seguir.

### Commits descriptivos

Mínimo 10 commits con mensajes descriptivos. No se aceptan: `fix`, `update`, `cambios`, `asdf`. Recuérdame hacer commits después de cada módulo completado.
