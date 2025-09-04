# File: /opt/access_control/src/api/auth.py
from flask import session, jsonify, redirect
from functools import wraps
import hashlib
import sqlite3
import os

# Definizione ruoli e permessi
USER_ROLES = {
    'admin': {
        'name': 'Amministratore',
        'permissions': ['all'],
        'description': 'Accesso completo al sistema'
    },
    'user_manager': {
        'name': 'Gestore Utenti',
        'permissions': ['view_logs', 'filter_logs', 'export_logs', 'manage_viewers', 'reset_passwords'],
        'description': 'Gestione utenti viewer, visualizzazione ed export log'
    },
    'viewer': {
        'name': 'Visualizzatore',
        'permissions': ['view_logs', 'filter_logs'],
        'description': 'Solo visualizzazione e filtro log'
    }
}

# Path del database
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'access.db')

def get_db_connection():
    """Connessione al database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Errore connessione DB: {e}")
        return None

def verify_user(username: str, password: str) -> tuple:
    """Verifica credenziali utente nel database"""
    conn = get_db_connection()
    if not conn:
        print("Errore: Connessione al database fallita")
        return False, None
    
    try:
        cursor = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        print(f"Debug: Hash generato per la password: {password_hash}")
        
        cursor.execute("""
            SELECT username, role, attivo, password
            FROM utenti_sistema 
            WHERE username = ?
        """, (username,))
        
        user = cursor.fetchone()
        
        if user:
            print(f"Debug: Utente trovato: {user['username']}, Ruolo: {user['role']}, Attivo: {user['attivo']}")
            print(f"Debug: Hash password nel DB: {user['password']}")
            if user['password'] == password_hash and user['attivo']:
                print("Debug: Autenticazione riuscita")
                return True, user['role']
            else:
                print("Debug: Password non corrispondente o utente non attivo")
        else:
            print("Debug: Utente non trovato")
        
        return False, None
        
    except Exception as e:
        print(f"Errore verifica utente: {e}")
        return False, None
    finally:
        conn.close()

def require_auth():
    """Decorator per richiedere autenticazione con gestione errori"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                if not session.get('logged_in') or 'username' not in session:
                    session.clear()  # Pulisci la sessione se non valida
                    return redirect('/login')
                return f(*args, **kwargs)
            except Exception as e:
                print(f"Errore autenticazione: {e}")
                session.clear()  # Pulisci la sessione in caso di errori
                return redirect('/login')
        return wrapper
    return decorator

def require_permission(*required_permissions):
    """Decorator per verificare permessi specifici con gestione errori"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                if not session.get('logged_in') or 'username' not in session:
                    session.clear()  # Pulisci la sessione se non valida
                    return redirect('/login')
                
                user_role = session.get('role')
                if not user_role:
                    session.clear()  # Pulisci la sessione se ruolo mancante
                    return redirect('/login')
                
                user_permissions = USER_ROLES.get(user_role, {}).get('permissions', [])
                
                if 'all' in user_permissions:
                    return f(*args, **kwargs)
                
                if any(perm in user_permissions for perm in required_permissions):
                    return f(*args, **kwargs)
                
                return jsonify({'error': 'Permessi insufficienti'}), 403
            except Exception as e:
                print(f"Errore verifica permessi: {e}")
                session.clear()  # Pulisci la sessione in caso di errori
                return redirect('/login')
        return wrapper
    return decorator
