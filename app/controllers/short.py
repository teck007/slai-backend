# Importar las librerías necesarias
from app import app, limiter
from app.utils.database import save_url, get_url, find_url  # Funciones para interactuar con la base de datos
from app.utils.llm_service import resume_url  # Función para acortar URLs usando IA
from app.utils.url_analize import url_content  # Función para analizar el contenido de una URL
from flask import request, jsonify, redirect
from app.utils.access_log import log_access  # Función para registrar el acceso
from app.utils.auth import optional_auth, g
# Ruta para acortar una URL
@app.route('/api/shorten',methods=['POST'])
@limiter.limit("10 per minute")
@optional_auth
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
    save_url(url, short_url, g.user_id)  # Guarda la nueva URL acortada en la base de datos
    return jsonify({'status': 'shorted','result': short_url})  # Retorna la nueva URL acortada

# Ruta para redirigir desde una URL acortada a la original
@app.route('/<short_url>', methods=['GET'])
def redirect_short(short_url):
    log_access()  # Registra el acceso
    original_url = get_url(short_url)  # Busca la URL original
    if not original_url:
        return "<h1>URL no encontrada</h1>", 404  # Retorna error si no existe
    
    return redirect(original_url)  # Redirige si existe

if __name__ == '__main__':
    app.run(debug=True)