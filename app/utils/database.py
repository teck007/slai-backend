# Cliente Supabase - usa REST API sobre HTTPS (evita bloqueos del puerto 5432)
from supabase import create_client, Client
from dotenv import load_dotenv
from collections import Counter
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
    """Busca la URL corta correspondiente a una URL original.
    Argumentos:
        url (str): La URL original a buscar.
    Retorna:
        str | None: La URL corta correspondiente a la URL original, o None si no se encuentra.
    """
    try:
        resp = _get_client().table(TABLE_URLS).select("short_url").eq("orig_url", url).limit(1).execute()
        if resp.data and len(resp.data) > 0:
            return str(resp.data[0]["short_url"])
        return None
    except Exception as e:
        print(f"Error querying database: {e}")
        return None

def find_user_links(user_id):
    """Busca las URLs cortas de un usuario e incluye la cantidad de clicks por link."""
    try:
        resp = _get_client().table(TABLE_URLS).select("short_url, orig_url").eq("user_id", user_id).execute()
        if resp.data and len(resp.data) > 0:
            links = [{'short_url': str(link["short_url"]), 'orig_url': str(link["orig_url"])} for link in resp.data]
            # Consulta batch de access_logs para contar clicks
            short_urls = [link["short_url"] for link in links]
            paths = ["/" + s for s in short_urls]
            logs_resp = _get_client().table("access_logs").select("path").in_("path", paths).execute()
            counts = Counter(row["path"] for row in (logs_resp.data or []))
            for link in links:
                link["clicks"] = counts.get("/" + link["short_url"], 0)
            return links
        return []
    except Exception as e:
        print(f"Error querying database: {e}")
        return []


def get_link_stats(user_id, short_url):
    """Devuelve estadísticas detalladas de un link: total de clicks, desglose diario, primer y último acceso.
    Retorna None si el link no existe o no pertenece al usuario."""
    try:
        # Verificar propiedad del link
        client = _get_client()
        resp = client.table(TABLE_URLS).select("orig_url").eq("short_url", short_url).eq("user_id", user_id).limit(1).execute()
        if not resp.data:
            return None
        orig_url = resp.data[0]["orig_url"]

        # Obtener accesos ordenados por fecha
        resp = client.table("access_logs").select("created_at").eq("path", f"/{short_url}").order("created_at").execute()
        rows = resp.data if resp.data else []

        # Agrupar por fecha
        daily = Counter()
        for row in rows:
            date = row["created_at"][:10] if row.get("created_at") else "unknown"
            daily[date] += 1

        sorted_daily = sorted(daily.items())
        return {
            "short_url": short_url,
            "orig_url": orig_url,
            "total_clicks": len(rows),
            "daily": [{"date": d, "clicks": c} for d, c in sorted_daily],
            "first_access": rows[0]["created_at"] if rows else None,
            "last_access": rows[-1]["created_at"] if rows else None,
        }
    except Exception as e:
        print(f"Error obteniendo estadísticas del link: {e}")
        return None


def delete_user_links(user_id, short_urls: list[str]) -> bool:
    """Elimina enlaces del usuario solo si coinciden short_url y user_id."""
    if not short_urls:
        return True
    try:
        _get_client().table(TABLE_URLS).delete().eq("user_id", user_id).in_("short_url", short_urls).execute()
        return True
    except Exception as e:
        print(f"Error deleting user links: {e}")
        return False
    
def save_access_log(data):
    """Guarda el acceso de un visitante en la base de datos."""
    try:
        _get_client().table("access_logs").insert(data).execute()
    except Exception as e:
        print(f"Error inserting into access_logs: {e}")