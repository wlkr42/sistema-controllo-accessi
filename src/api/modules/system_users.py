from flask import Blueprint, jsonify, request, session
import hashlib
import sqlite3
import os

# Import delle funzioni di utilità
from ..auth import USER_ROLES
from ..utils import get_db_connection, require_auth, require_permission

system_users_bp = Blueprint('system_users', __name__)

@system_users_bp.route('/api/users/list')
@require_auth()
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
            role = row[1]
            users.append({
                'username': row[0],
                'role': role,
                'role_name': USER_ROLES.get(role, {}).get('name', role),
                'attivo': bool(row[2]),
                'created_at': row[3],
                'created_by': row[4] or 'system',
                'modified_at': row[5],
                'modified_by': row[6],
                'last_login': row[7] or 'Mai'
            })
        return jsonify({'success': True, 'users': users})
    finally:
        conn.close()

@system_users_bp.route('/api/users/create', methods=['POST'])
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
        
        # Log creazione utente
        cursor.execute("""
            INSERT INTO eventi_sistema (tipo_evento, livello, messaggio, componente)
            VALUES (?, ?, ?, ?)
        """, ('USER_CREATE', 'INFO', f'Creato nuovo utente {username} con ruolo {USER_ROLES[role]["name"]}', 'USER_MGMT'))
        
        conn.commit()
        return jsonify({
            'success': True,
            'message': f'Utente {username} creato con ruolo {USER_ROLES[role]["name"]}',
            'username': username,
            'password': password
        })
    finally:
        conn.close()

@system_users_bp.route('/api/users/update', methods=['POST'])
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
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            updates.append("password = ?")
            params.append(password_hash)
            
            # Log cambio password
            cursor.execute("""
                INSERT INTO eventi_sistema (tipo_evento, livello, messaggio, componente)
                VALUES (?, ?, ?, ?)
            """, ('PASSWORD_CHANGE', 'INFO', f'Modificata password utente {username}', 'USER_MGMT'))
        
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
                'message': f'Utente {username} aggiornato',
                'password': password if password else None
            })
        else:
            return jsonify({'success': False, 'error': 'Nessun dato da aggiornare'}), 400
    finally:
        conn.close()

@system_users_bp.route('/api/users/delete', methods=['POST'])
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
        
        # Log eliminazione utente
        cursor.execute("""
            INSERT INTO eventi_sistema (tipo_evento, livello, messaggio, componente)
            VALUES (?, ?, ?, ?)
        """, ('USER_DELETE', 'WARNING', f'Eliminato utente {username}', 'USER_MGMT'))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': f'Utente {username} eliminato'
        })
    finally:
        conn.close()
