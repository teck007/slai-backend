from flask import request
from datetime import datetime
from app.utils.database import save_access_log

def get_visitor_data():
    """Extrae IP y datos del visitante desde headers de Cloudflare."""
    return {
        "ip": request.headers.get("CF-Connecting-IP") or request.remote_addr,
        "country": request.headers.get("CF-IPCountry", "Unknown"),
        "cf_ray": request.headers.get("CF-Ray"),
        "user_agent": request.headers.get("User-Agent"),
        "path": request.path,
        "method": request.method,
    }

def log_access():
    """Registra el acceso de un visitante a una ruta acortada."""
    save_access_log(get_visitor_data())