from flask import Flask, redirect, jsonify, request
from src.chat_openai import shorten
from src.url_analize import url_content
from flask_cors import CORS
from src.database import save_url, get_url

app = Flask(__name__)
CORS(app)

@app.route('/api/shorten',methods=['POST'])
def short():
    data = request.get_json()
    url = data['url']
    # description = data['description']
    content = url_content(url)
    short_url = shorten(url,content)
    save_url(url, short_url)
    return jsonify({'result': short_url})

@app.route('/<short_url>', methods=['GET'])
def redirect_short(short_url):
    original_url = get_url(short_url)
    if original_url:
        return redirect(original_url)
    else:
        return jsonify({'error': 'URL no encontrada'}), 404

if __name__ == '__main__':
    app.run(debug=True)