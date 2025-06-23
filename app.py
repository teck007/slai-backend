from flask import Flask, redirect, jsonify, request
from src.chat_openai import shorten
from src.url_analize import url_content
from flask_cors import CORS
from src.database import save_url, get_url, find_url
import os
from dotenv import load_dotenv
from functools import wraps
load_dotenv()

app = Flask(__name__)
CORS(app)

# Cargar variables de entorno
API_TOKEN = os.getenv('API_TOKEN')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or token != f"Bearer {API_TOKEN}":
            return jsonify({'error': 'No autorizado'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/shorten',methods=['POST'])
@token_required
def short():
    data = request.get_json()
    url = data['url']
    content = url_content(url)
    exists = find_url(url)
    if (exists):
        return jsonify({'status': 'exists','result': exists})
    short_url = shorten(url,content)
    save_url(url, short_url)
    return jsonify({'status': 'shorted','result': short_url})

@app.route('/<short_url>', methods=['GET'])
@token_required
def redirect_short(short_url):
    original_url = get_url(short_url)
    if original_url:
        return redirect(original_url)
    else:
        return jsonify({'error': 'URL no encontrada'}), 404

if __name__ == '__main__':
    app.run(debug=True)