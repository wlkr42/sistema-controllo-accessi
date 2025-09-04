# File: /opt/access_control/src/api/auth.py
from flask import session, jsonify, redirect
from functools import wraps
import hashlib

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

USERS = {
    'admin': {
        'password': hashlib.sha256('admin123'.encode()).hexdigest(), 
        'role': 'admin'
    },
    'manager': {
        'password': hashlib.sha256('manager123'.encode()).hexdigest(), 
        'role': 'user_manager'
    },
    'viewer': {
        'password': hashlib.sha256('viewer123'.encode()).hexdigest(), 
        'role': 'viewer'
    }
}

def require_auth():
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'username' not in session:
                return redirect('/login')
            return f(*args, **kwargs)
        return wrapper
    return decorator

def require_permission(*required_permissions):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'username' not in session:
                return redirect('/login')
            
            user_role = session.get('role', 'viewer')
            user_permissions = USER_ROLES.get(user_role, {}).get('permissions', [])
            
            if 'all' in user_permissions:
                return f(*args, **kwargs)
            
            if any(perm in user_permissions for perm in required_permissions):
                return f(*args, **kwargs)
            
            return jsonify({'error': 'Permessi insufficienti'}), 403
        return wrapper
    return decorator