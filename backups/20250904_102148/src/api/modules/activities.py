from flask import Blueprint, jsonify
from ..utils import get_db_connection, require_auth

activities_bp = Blueprint('activities', __name__)

@activities_bp.route('/api/recent-activities')
@require_auth()
def api_recent_activities():
    """Restituisce le attività recenti del sistema"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tipo_evento as type, 
                   messaggio as message,
                   DATETIME(timestamp, 'localtime') as timestamp
            FROM eventi_sistema 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        activities = [dict(row) for row in cursor.fetchall()]
        return jsonify({'success': True, 'activities': activities})
    finally:
        conn.close()
