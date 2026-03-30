from app import app, limiter
from app.utils.auth import required_auth, g
from flask import request, jsonify
from app.utils.database import find_user_links

@app.route('/api/user', methods=['GET'])
@limiter.limit("20 per minute")
@required_auth
def get_user_links():
    print(g.user_id)
    if not g.user_id:
        return jsonify({'error': 'No autorizado'}), 401

    return jsonify({'status': 'success', 'links': find_user_links(g.user_id)})