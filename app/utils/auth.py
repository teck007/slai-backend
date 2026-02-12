import os
from flask import request, jsonify
from functools import wraps

# Cargar variables de entorno
API_TOKEN = os.getenv('API_TOKEN')

# Decorador para requerir token de autorización en las rutas protegidas
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        # Verifica si el token es válido
        if not token or token != f"Bearer {API_TOKEN}":
            return jsonify({'error': 'No autorizado'}), 401
        return f(*args, **kwargs)
    return decorated