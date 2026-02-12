# Importar las librerías necesarias
from app import app
from app.utils.database import save_url, get_url, find_url  # Funciones para interactuar con la base de datos
from app.utils.llm_service import resume_url  # Función para acortar URLs usando IA
from app.utils.url_analize import url_content  # Función para analizar el contenido de una URL
from app.utils.auth import token_required
from flask import request, jsonify, redirect
from functools import wraps  # Para crear decoradores

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
    if not content:
        return jsonify({'status': 'error','result': 'La URL no esta disponible o es inaccesible'}), 400
    short_url = resume_url(url, content)  # Acorta la URL usando el contenido
    save_url(url, short_url)  # Guarda la nueva URL acortada en la base de datos
    return jsonify({'status': 'shorted','result': short_url})  # Retorna la nueva URL acortada

# Ruta para redirigir desde una URL acortada a la original
@app.route('/<short_url>', methods=['GET'])
def redirect_short(short_url):
    original_url = get_url(short_url)  # Busca la URL original
    if not original_url:
        return jsonify({'error': 'URL no encontrada'}), 404  # Retorna error si no existe
    
    return redirect(original_url)  # Redirige si existe

if __name__ == '__main__':
    app.run(debug=True)