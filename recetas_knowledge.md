# Archivo de Conocimiento del Proyecto
## Parcial Final — Generador de Recetas con Inventario

---

## 1. Descripción del Proyecto

Aplicación web fullstack que permite a usuarios registrar ingredientes disponibles en casa y generar recetas mediante un LLM (Groq). Las recetas generadas se almacenan en base de datos y el usuario puede calificarlas, guardarlas y eliminarlas. Proyecto individual para el parcial final de Tecnologías Web. Valor: 40% de la nota final.

---

## 2. Stack Tecnológico

| Capa | Tecnología | Nota |
|------|-----------|------|
| Backend | FastAPI + Python | Requerido por el enunciado |
| Base de datos | PostgreSQL | Alternativa aceptada al MySQL del enunciado |
| ORM | SQLAlchemy + Alembic | Migraciones con Alembic |
| Autenticación | JWT (python-jose + passlib) | Registro e inicio de sesión |
| LLM | Groq API | Gratuito, sin tarjeta — modelos LLaMA 3 |
| Frontend | HTML + CSS + JavaScript puro | Interfaz mínima funcional requerida |
| Pruebas | pytest | Mínimo 6 pruebas — requerido por el enunciado |
| Contenedores | Docker + Docker Compose | App + PostgreSQL como servicios separados |
| Deploy | VPS Hetzner | Con dominio propio y SSL via Certbot/Caddy |
| Control de versiones | Git + GitHub | Repositorio público — mínimo 10 commits descriptivos |

---

## 3. Modelo de Datos

### 3.1 Tabla: usuarios

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer PK autoincrement | |
| nombre | String | Nombre completo |
| email | String unique | Correo — identificador de login |
| password_hash | String | Contraseña hasheada con bcrypt |
| created_at | DateTime | |

### 3.2 Tabla: ingredientes

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer PK autoincrement | |
| usuario_id | Integer FK → usuarios.id | Propietario del ingrediente |
| nombre | String | Nombre del ingrediente |
| cantidad | String | Ej: '2 tazas', '500g' |
| unidad | String? | Opcional — kg, g, ml, unidades |
| created_at | DateTime | |

### 3.3 Tabla: recetas

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer PK autoincrement | |
| usuario_id | Integer FK → usuarios.id | Quién generó la receta |
| nombre_plato | String | Nombre del plato generado |
| ingredientes_json | Text (JSON) | Lista de ingredientes con cantidades |
| pasos_json | Text (JSON) | Pasos de preparación |
| tiempo_estimado | String | Ej: '30 minutos' |
| nivel_dificultad | String | Fácil / Medio / Difícil |
| prompt_usado | Text | Prompt enviado al LLM — para trazabilidad |
| created_at | DateTime | |

### 3.4 Tabla: calificaciones

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer PK autoincrement | |
| receta_id | Integer FK → recetas.id | |
| usuario_id | Integer FK → usuarios.id | |
| estrellas | Integer | Del 1 al 5 |
| created_at | DateTime | |

---

## 4. Endpoints de la API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | /auth/register | Registro de usuario |
| POST | /auth/login | Login — devuelve JWT |
| GET | /ingredientes | Lista ingredientes del usuario autenticado |
| POST | /ingredientes | Agrega un ingrediente |
| PUT | /ingredientes/{id} | Actualiza un ingrediente |
| DELETE | /ingredientes/{id} | Elimina un ingrediente |
| POST | /recetas/generar | Genera receta con el inventario actual via Groq |
| GET | /recetas | Lista recetas generadas por el usuario |
| DELETE | /recetas/{id} | Elimina una receta del historial |
| POST | /recetas/{id}/calificar | Califica una receta (1-5 estrellas) |
| GET | /health | Health check |

---

## 5. Integración con Groq LLM

- Proveedor: Groq API — gratuito, sin tarjeta requerida.
- Modelo recomendado: `llama3-8b-8192` o `llama3-70b-8192`.
- El servicio LLM está encapsulado en `app/services/llm_service.py` — no expuesto directamente al usuario.
- El prompt incluye el inventario completo del usuario y solicita respuesta en JSON con campos exactos: `nombre_plato`, `ingredientes`, `pasos`, `tiempo_estimado`, `nivel_dificultad`.
- La respuesta se parsea y valida antes de guardar en BD. Si el parseo falla, se devuelve error al usuario.

---

## 6. Pruebas Unitarias (pytest)

| # | Test | Descripción |
|---|------|-------------|
| 1 | test_validar_ingredientes_vacios | Error si el inventario está vacío al generar receta |
| 2 | test_validar_ingredientes_validos | Pasa correctamente con ingredientes válidos |
| 3 | test_generar_prompt | El prompt contiene los ingredientes del usuario |
| 4 | test_parseo_respuesta_llm_valida | Parsea correctamente un JSON válido del LLM |
| 5 | test_parseo_respuesta_llm_invalida | Lanza error si el LLM devuelve JSON malformado |
| 6 | test_endpoint_health | GET /health devuelve 200 |
| 7 | test_registro_usuario | POST /auth/register crea usuario correctamente |
| 8 | test_login_usuario | POST /auth/login devuelve JWT válido |

---

## 7. Estructura de Carpetas

```
proyecto-recetas/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   │   └── models.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── ingredientes.py
│   │   └── recetas.py
│   ├── services/
│   │   └── llm_service.py
│   └── schemas/
│       └── schemas.py
├── tests/
│   └── test_*.py
├── static/
│   └── favicon.ico
├── frontend/
│   └── index.html
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── README.md
└── requirements.txt
```

---

## 8. Despliegue

| Componente | Tecnología | Nota |
|-----------|-----------|------|
| VPS | Hetzner CX22 | ~4 EUR/mes |
| Dominio | Namecheap o Porkbun | Gratis con GitHub Student Pack (.me en Namecheap) |
| SSL | Certbot + Let's Encrypt o Caddy | HTTPS obligatorio |
| Contenedores | Docker + Docker Compose | App + PostgreSQL como servicios separados |
| Variables sensibles | .env — nunca en el repo | Penalización de -20 puntos si se exponen keys |

---

## 9. Variables de Entorno (.env.example)

```env
DATABASE_URL=postgresql://user:password@db:5432/recetas
SECRET_KEY=tu_secret_key_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GROQ_API_KEY=tu_groq_api_key_aqui
```

---

## 10. Rúbrica y Puntos Clave

| Criterio | Puntos | Riesgo de penalización |
|---------|--------|----------------------|
| Funcionalidad CRUD + generación + calificación + historial | 30 | App no accesible el día de revisión: -15 |
| Integración LLM correcta | 15 | API key expuesta en repo: -20 |
| Despliegue VPS + dominio + SSL + Docker | 20 | |
| Pruebas unitarias (mínimo 6 con pytest) | 15 | Pruebas vacías o que no corren: -10 |
| Git: commits descriptivos, README, .env.example | 10 | Sin commits o mensajes tipo 'fix': -10 |
| Presentación: favicon, interfaz, PDF | 10 | |
