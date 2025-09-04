from flask import jsonify, session, redirect, request
import sqlite3
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'access.db')

def get_db_connection():
    """Connessione database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Errore connessione DB: {e}")
        return None

def require_auth():
    """Decorator autenticazione"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if 'username' not in session:
                if request.path.startswith('/api/'):
                    return jsonify({'error': 'Non autenticato'}), 401
                return redirect('/login')
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

def require_permission(*required_permissions):
    """Decorator per verificare permessi specifici"""
    def decorator(f):
        @require_auth()
        def wrapper(*args, **kwargs):
            user_role = session.get('role', 'viewer')
            from src.api.auth import USER_ROLES
            user_permissions = USER_ROLES.get(user_role, {}).get('permissions', [])
            
            # Admin ha sempre accesso
            if 'all' in user_permissions:
                return f(*args, **kwargs)
            
            # Controlla se l'utente ha almeno uno dei permessi richiesti
            if any(perm in user_permissions for perm in required_permissions):
                return f(*args, **kwargs)
            
            return jsonify({'error': 'Permessi insufficienti'}), 403
        
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator
