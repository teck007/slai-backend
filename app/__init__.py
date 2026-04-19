from flask import Flask, request
from flask_cors import CORS
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
load_dotenv()

app = Flask(__name__)

# Orígenes: admite varios separados por coma (ej. dev + prod). Sin barra final (Origin no la lleva).
_raw_origins = os.getenv("FRONTEND_URL") or ""
_cors_origins = [o.strip().rstrip("/") for o in _raw_origins.split(",") if o.strip()]
_cors_kw = dict(
    origins=_cors_origins if _cors_origins else os.getenv("FRONTEND_URL"),
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["Content-Type"],
)
CORS(app, **_cors_kw)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[os.getenv("LIMIT_IP_DAY"), os.getenv("LIMIT_IP_HOUR")],
    storage_uri=os.getenv("REDIS_URI")
)


@limiter.request_filter
def _skip_rate_limit_for_cors_preflight():
    """OPTIONS no debe contar ni fallar por límites; si no, el preflight devuelve 429/5xx y el navegador bloquea CORS."""
    return request.method == "OPTIONS"

from app.controllers.short import short
from app.controllers.main import main
from app.controllers.user import get_user_links, post_delete_user_links