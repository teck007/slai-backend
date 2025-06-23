# Importar las librerías necesarias
from flask import Flask, redirect, jsonify, request
from src.chat_openai import shorten  # Función para acortar URLs usando OpenAI
from src.url_analize import url_content  # Función para analizar el contenido de una URL
from flask_cors import CORS  # Habilita CORS para la API
from src.database import save_url, get_url, find_url  # Funciones para interactuar con la base de datos
import os
from dotenv import load_dotenv  # Para cargar variables de entorno desde un archivo .env
from functools import wraps  # Para crear decoradores
load_dotenv()

# Crear la aplicación Flask
app = Flask(__name__)
CORS(app)

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

# Ruta para acortar una URL
@app.route('/api/shorten',methods=['POST'])
@token_required
def short():
    data = request.get_json()  # Obtiene los datos del request
    url = data['url']  # Extrae la URL
    exists = find_url(url)  # Verifica si la URL ya fue acortada
    if (exists):
        return jsonify({'status': 'exists','result': exists})  # Si existe, retorna la URL acortada existente
    content = url_content(url)  # Analiza el contenido de la URL
    short_url = shorten(url,content)  # Acorta la URL usando el contenido
    save_url(url, short_url)  # Guarda la nueva URL acortada en la base de datos
    return jsonify({'status': 'shorted','result': short_url})  # Retorna la nueva URL acortada

# Ruta para redirigir desde una URL acortada a la original
@app.route('/<short_url>', methods=['GET'])
def redirect_short(short_url):
    original_url = get_url(short_url)  # Busca la URL original
    if original_url:
        return redirect(original_url)  # Redirige si existe
    else:
        return jsonify({'error': 'URL no encontrada'}), 404  # Retorna error si no existe

if __name__ == '__main__':
    app.run(debug=True)