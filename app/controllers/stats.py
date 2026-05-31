from app import app, limiter
from app.utils.auth import required_auth, g
from flask import jsonify
from app.utils.database import get_link_stats


@app.route('/api/stats/<short_url>', methods=['GET'])
@limiter.limit("30 per minute")
@required_auth
def get_link_stats_endpoint(short_url):
    """Retorna estadísticas detalladas de un link (clicks totales, desglose diario)."""
    if not g.user_id:
        return jsonify({'error': 'No autorizado'}), 401

    stats = get_link_stats(g.user_id, short_url)
    if stats is None:
        return jsonify({'error': 'Enlace no encontrado'}), 404

    return jsonify({'status': 'success', 'stats': stats})
