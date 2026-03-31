## SLAI Backend

Backend del acortador de URLs **SLAI**, construido con **Flask**. Expone endpoints para:

- Acortar una URL usando IA (DeepSeek via SDK de OpenAI).
- Redirigir desde `/<short_url>` hacia la URL original.
- Consultar y eliminar enlaces del usuario autenticado (Clerk).

La persistencia se hace vía **Supabase** (REST/HTTPS).

## Requisitos

- **Python**: 3.10+ (recomendado 3.11+)
- **Redis**: requerido si habilitas rate limiting (porque `flask-limiter` usa `REDIS_URI`)
- Cuenta/proyecto en:
  - **Supabase** (tabla `urls` por defecto)
  - **Clerk** (auth)
  - **DeepSeek** (API key; se usa `base_url="https://api.deepseek.com"`)

## Dependencias (Python)

Instalación vía `requirements.txt` (principales):

- `flask`, `flask-cors`
- `gunicorn` (producción)
- `flask-limiter` + `redis` (rate limit)
- `supabase` (DB)
- `clerk-backend-api` + `httpx` (auth)
- `openai` (cliente usado contra DeepSeek)
- `requests`, `beautifulsoup4` (análisis simple del contenido de una URL)
- `python-dotenv` (carga de `.env`)

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuración (.env)

Este backend carga variables con `python-dotenv` (archivo `.env` en la raíz).

Variables usadas:

- **App / CORS**
  - `FRONTEND_URL`: origen permitido para CORS y redirección en `/` (ej. `http://localhost:5173`)
- **Rate limiting (flask-limiter)**
  - `REDIS_URI`: ej. `redis://localhost:6379/0`
  - `LIMIT_IP_DAY`: ej. `200 per day`
  - `LIMIT_IP_HOUR`: ej. `50 per hour`
- **Supabase**
  - `SUPABASE_URL`: ej. `https://<project-ref>.supabase.co`
  - `SUPABASE_SERVICE_ROLE_KEY` **o** `SUPABASE_ANON_KEY`
  - `TABLE_URLS` (opcional, default `urls`)
  - `DB_HOST` (opcional): si lo defines y no defines `SUPABASE_URL`, se intenta derivar desde `db.<project-ref>.supabase.co`
- **IA (DeepSeek)**
  - `DEEPSEEK_API_KEY`
- **Clerk**
  - `CLERK_SECRET_KEY`

Ejemplo de `.env` (NO lo comitees):

```bash
FRONTEND_URL=http://localhost:5173

REDIS_URI=redis://localhost:6379/0
LIMIT_IP_DAY=200 per day
LIMIT_IP_HOUR=50 per hour

SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<tu_service_role_key>
TABLE_URLS=urls

DEEPSEEK_API_KEY=<tu_deepseek_api_key>
CLERK_SECRET_KEY=<tu_clerk_secret_key>
```

## Base de datos (Supabase)

Por defecto se usa la tabla `urls` (configurable con `TABLE_URLS`) con las columnas esperadas:

- `orig_url` (texto)
- `short_url` (texto)
- `user_id` (texto / nullable si acortas sin auth)

## Ejecutar en desarrollo

Opción A (simple):

```bash
source .venv/bin/activate
python app.py
```

Opción B (Flask CLI):

```bash
source .venv/bin/activate
export FLASK_APP=app.py
flask run --debug
```

Por defecto escucha en `http://127.0.0.1:5000`.

## Ejecutar en producción (Gunicorn)

```bash
source .venv/bin/activate
gunicorn -w 2 -b 0.0.0.0:8000 app:app
```

## Endpoints

- **GET** `/` redirige a `FRONTEND_URL`
- **POST** `/api/shorten` acorta una URL (auth opcional)
- **GET** `/<short_url>` redirige a la URL original
- **GET** `/api/user` lista links del usuario (requiere auth)
- **POST** `/api/user/delete` elimina links del usuario (requiere auth)

### Ejemplos (curl)

Acortar URL (sin auth):

```bash
curl -sS -X POST http://127.0.0.1:5000/api/shorten \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com"}'
```

Listar links del usuario (con token de Clerk):

```bash
curl -sS http://127.0.0.1:5000/api/user \
  -H "Authorization: Bearer <clerk_jwt>"
```

Eliminar links del usuario:

```bash
curl -sS -X POST http://127.0.0.1:5000/api/user/delete \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer <clerk_jwt>" \
  -d '{"short_urls":["mi-link-1","mi-link-2"]}'
```

## Notas y troubleshooting

- Si el backend falla al iniciar con rate limiting, revisa `REDIS_URI` y que Redis esté corriendo.
- Si falla Supabase con un error de credenciales, verifica `SUPABASE_URL` y `SUPABASE_SERVICE_ROLE_KEY` (o `SUPABASE_ANON_KEY`).
- CORS depende de `FRONTEND_URL`. Si tu frontend corre en otra URL/puerto, actualízalo.
