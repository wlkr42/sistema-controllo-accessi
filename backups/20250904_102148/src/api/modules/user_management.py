# File: /opt/access_control/src/api/modules/user_management.py
from flask import Blueprint, render_template_string, request, jsonify, session
from functools import wraps
import sqlite3
import os
import hashlib
from datetime import datetime

# Import auth per i decoratori
from ..utils import require_auth, require_permission
from ..auth import USER_ROLES

user_management_bp = Blueprint('user_management', __name__)

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'access.db')

def get_db_connection():
    """Connessione al database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Errore connessione DB: {e}")
        return None

@user_management_bp.route('/admin/users')
@require_auth()
@require_permission('all')
def admin_users():
    """Gestione completa utenti - Solo Admin"""
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 
              'static', 'html', 'user-management.html'), 'r') as f:
        template = f.read()
    return render_template_string(template, session=session)

@user_management_bp.route('/api/users/list')
@require_auth()
@require_permission('all')
def api_users_list():
    """Lista utenti di sistema"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                username,
                role,
                attivo,
                DATETIME(created_at, 'localtime') as created_at,
                created_by,
                DATETIME(modified_at, 'localtime') as modified_at,
                modified_by,
                DATETIME(last_login, 'localtime') as last_login
            FROM utenti_sistema
            ORDER BY username
        """)
        users = []
        for row in cursor.fetchall():
            role = row['role']
            users.append({
                'username': row['username'],
                'role': role,
                'role_name': USER_ROLES.get(role, {}).get('name', role),
                'attivo': bool(row['attivo']),
                'created_at': row['created_at'],
                'created_by': row['created_by'] or 'system',
                'modified_at': row['modified_at'],
                'modified_by': row['modified_by'],
                'last_login': row['last_login'] or 'Mai'
            })
        return jsonify({'success': True, 'users': users})
    finally:
        conn.close()

@user_management_bp.route('/api/users/create', methods=['POST'])
@require_auth()
@require_permission('all')
def api_users_create():
    """Crea nuovo utente di sistema"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    role = data.get('role', '').strip()
    
    if not username or not password or not role:
        return jsonify({'success': False, 'error': 'Dati mancanti'}), 400
    
    if role not in USER_ROLES:
        return jsonify({'success': False, 'error': 'Ruolo non valido'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Verifica se username esiste già
        cursor.execute("SELECT 1 FROM utenti_sistema WHERE username = ?", (username,))
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'Username già esistente'}), 400
        
        # Inserisci nuovo utente
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("""
            INSERT INTO utenti_sistema (
                username, password, role, attivo, 
                created_at, created_by, last_login
            ) VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP, ?, NULL)
        """, (username, password_hash, role, session.get('username')))
        
        conn.commit()
        return jsonify({
            'success': True,
            'message': f'Utente {username} creato con ruolo {USER_ROLES[role]["name"]}'
        })
    finally:
        conn.close()

@user_management_bp.route('/api/users/update', methods=['POST'])
@require_auth()
@require_permission('all')
def api_users_update():
    """Aggiorna dati utente di sistema (ruolo, stato, password)"""
    data = request.get_json()
    username = data.get('username', '').strip()
    role = data.get('role', '').strip() if data.get('role') else None
    attivo = data.get('attivo')
    password = data.get('password', '').strip() if data.get('password') else None
    
    if not username:
        return jsonify({'success': False, 'error': 'Username mancante'}), 400
    
    if role and role not in USER_ROLES:
        return jsonify({'success': False, 'error': 'Ruolo non valido'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Verifica se utente esiste
        cursor.execute("SELECT 1 FROM utenti_sistema WHERE username = ?", (username,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Utente non trovato'}), 404
        
        # Aggiorna i campi specificati
        updates = []
        params = []
        
        if role is not None:
            updates.append("role = ?")
            params.append(role)
        
        if attivo is not None:
            updates.append("attivo = ?")
            params.append(int(attivo))
        
        if password:
            updates.append("password = ?")
            params.append(hashlib.sha256(password.encode()).hexdigest())
        
        if updates:
            query = f"""
                UPDATE utenti_sistema 
                SET {', '.join(updates)},
                    modified_at = CURRENT_TIMESTAMP,
                    modified_by = ?
                WHERE username = ?
            """
            params.extend([session.get('username'), username])
            cursor.execute(query, params)
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': f'Utente {username} aggiornato'
            })
        else:
            return jsonify({'success': False, 'error': 'Nessun dato da aggiornare'}), 400
    finally:
        conn.close()

@user_management_bp.route('/api/users/delete', methods=['POST'])
@require_auth()
@require_permission('all')
def api_users_delete():
    """Elimina utente di sistema"""
    data = request.get_json()
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'success': False, 'error': 'Username mancante'}), 400
    
    # Non permettere di eliminare l'utente corrente
    if username == session.get('username'):
        return jsonify({'success': False, 'error': 'Non puoi eliminare il tuo utente'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Verifica se utente esiste
        cursor.execute("SELECT role FROM utenti_sistema WHERE username = ?", (username,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'success': False, 'error': 'Utente non trovato'}), 404
        
        # Elimina utente
        cursor.execute("DELETE FROM utenti_sistema WHERE username = ?", (username,))
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': f'Utente {username} eliminato'
        })
    finally:
        conn.close()
