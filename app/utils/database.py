# Cliente Supabase - usa REST API sobre HTTPS (evita bloqueos del puerto 5432)
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

# Nombre de la tabla (DB_NAME es el nombre de la base de datos, no de la tabla)
TABLE_URLS = os.getenv("TABLE_URLS", "urls")

# URL derivada del host de Supabase: db.XXX.supabase.co -> https://XXX.supabase.co
_supabase_url = os.getenv("SUPABASE_URL")
if not _supabase_url and os.getenv("DB_HOST"):
    _host = os.getenv("DB_HOST", "").replace("db.", "")
    if _host:
        _supabase_url = f"https://{_host}"

_supabase: Client | None = None


def _get_client() -> Client:
    """Obtiene el cliente de Supabase (usa REST/HTTPS, no requiere puerto 5432)."""
    global _supabase
    if _supabase is None:
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not key or not _supabase_url:
            raise ValueError(
                "Falta SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY (o SUPABASE_ANON_KEY) en .env. "
                "Obtenlos en Supabase: Project Settings > API"
            )
        _supabase = create_client(_supabase_url, key)
    return _supabase


def save_url(original_url, short_url, user_id):
    """Guarda URL original y su versión corta en la base de datos."""
    try:
        _get_client().table(TABLE_URLS).insert({
            "orig_url": original_url,
            "short_url": short_url,
            "user_id": user_id,
        }).execute()
    except Exception as e:
        print(f"Error inserting into database: {e}")


def get_url(short_url):
    """Recupera la URL original a partir de la URL corta."""
    try:
        resp = _get_client().table(TABLE_URLS).select("orig_url").eq("short_url", short_url).limit(1).execute()
        if resp.data and len(resp.data) > 0:
            return resp.data[0]["orig_url"]
        return None
    except Exception as e:
        print(f"Error querying database: {e}")
        return None


def find_url(url):
    """Busca la URL corta correspondiente a una URL original."""
    try:
        resp = _get_client().table(TABLE_URLS).select("short_url").eq("orig_url", url).limit(1).execute()
        if resp.data and len(resp.data) > 0:
            return str(resp.data[0]["short_url"])
        return None
    except Exception as e:
        print(f"Error querying database: {e}")
        return None