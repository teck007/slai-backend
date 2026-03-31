from app import app, limiter
from app.utils.auth import required_auth, g
from flask import request, jsonify
from app.utils.database import find_user_links, delete_user_links

@app.route('/api/user', methods=['GET'])
@limiter.limit("20 per minute")
@required_auth
def get_user_links():
    print(g.user_id)
    if not g.user_id:
        return jsonify({'error': 'No autorizado'}), 401

    return jsonify({'status': 'success', 'links': find_user_links(g.user_id)})


@app.route('/api/user/delete', methods=['POST'])
@limiter.limit("20 per minute")
@required_auth
def post_delete_user_links():
    if not g.user_id:
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json(silent=True) or {}
    raw = data.get('short_urls')
    if not isinstance(raw, list):
        return jsonify({'error': 'Se esperaba short_urls: lista de cadenas'}), 400

    short_urls = [str(x).strip() for x in raw if str(x).strip()]
    if not short_urls:
        return jsonify({'error': 'No hay enlaces seleccionados'}), 400

    ok = delete_user_links(g.user_id, short_urls)
    if not ok:
        return jsonify({'error': 'No se pudieron eliminar los enlaces'}), 500

    return jsonify({'status': 'success', 'deleted': short_urls})