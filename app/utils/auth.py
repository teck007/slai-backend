import os
import httpx
import dotenv
from functools import wraps
from flask import request, jsonify, g
from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions
dotenv.load_dotenv()
clerk = Clerk(bearer_auth=os.getenv('CLERK_SECRET_KEY'))


def _authorized_parties():
    raw = os.getenv("FRONTEND_URL") or ""
    parties = [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]
    if parties:
        return parties
    single = raw.strip().rstrip("/")
    return [single] if single else []


def optional_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization') or ''
        if not auth.startswith('Bearer ') or not auth[7:].strip():
            g.user_id = None
            return f(*args, **kwargs)

        req = httpx.Request(request.method, request.url, headers=dict(request.headers))
        state = clerk.authenticate_request(
            req,
            AuthenticateRequestOptions(
                authorized_parties=_authorized_parties()
            ),
        )
        if not state.is_signed_in:
            return jsonify({'error': 'No autorizado'}), 401
        g.user_id = state.payload.get('sub')
        return f(*args, **kwargs)
    return decorated


def required_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Preflight CORS (OPTIONS) no envía Authorization; flask-cors añade cabeceras al 204
        if request.method == 'OPTIONS':
            return '', 204

        auth = request.headers.get('Authorization') or ''
        if not auth.startswith('Bearer ') or not auth[7:].strip():
            return jsonify({'error': 'Autenticación requerida'}), 401

        req = httpx.Request(request.method, request.url, headers=dict(request.headers))
        state = clerk.authenticate_request(
            req,
            AuthenticateRequestOptions(
                authorized_parties=_authorized_parties()
            ),
        )
        if not state.is_signed_in:
            return jsonify({'error': 'No autorizado'}), 401
        g.user_id = state.payload.get('sub')
        return f(*args, **kwargs)
    return decorated
