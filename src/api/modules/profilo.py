# File: /opt/access_control/src/api/modules/profilo.py
# Modulo per la gestione del profilo utente - FIXED IMPORTS

import logging
import hashlib
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, session, render_template, redirect

logger = logging.getLogger(__name__)

# Blueprint per il modulo profilo
profilo_bp = Blueprint('profilo', __name__)

# Storage temporaneo per password modificate (in produzione usare DB)
temp_passwords = {}

def require_login(f):
    """Decorator per richiedere login"""
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_users():
    """Ottieni USERS dal modulo principale per evitare import circolari"""
    # Usa le credenziali di default hardcoded
    import hashlib
    return {
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

@profilo_bp.route('/profilo')
@require_login
def profilo_redirect():
    """Redirect alla dashboard con apertura automatica del profilo"""
    return redirect('/?show_profile=true')
    
@profilo_bp.route('/api/profile/info')
@require_login
def api_profile_info():
    """API per ottenere informazioni profilo"""
    try:
        return jsonify({
            'success': True,
            'user': {
                'username': session.get('username'),
                'role': session.get('role'),
                'login_time': session.get('login_time', '')
            }
        })
    except Exception as e:
        logger.error(f"Errore recupero info profilo: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@profilo_bp.route('/api/profile/change-password', methods=['POST'])
@require_login
def api_change_password():
    """API per cambio password"""
    try:
        data = request.get_json()
        
        current_password = data.get('current_password', '').strip()
        new_password = data.get('new_password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        
        username = session.get('username')
        
        # Validazioni
        if not all([current_password, new_password, confirm_password]):
            return jsonify({'success': False, 'error': 'Tutti i campi sono richiesti'}), 400
        
        if new_password != confirm_password:
            return jsonify({'success': False, 'error': 'Le password non coincidono'}), 400
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'error': 'La password deve essere di almeno 6 caratteri'}), 400
        
        # Verifica password attuale
        # Prima controlla se c'è una password temporanea modificata
        if username in temp_passwords:
            current_hash = temp_passwords[username]
        else:
            # Altrimenti usa la password di default dal sistema
            USERS = get_users()
            if username not in USERS:
                return jsonify({'success': False, 'error': 'Utente non trovato'}), 404
            current_hash = USERS[username]['password']
        
        # Verifica la password attuale
        if hashlib.sha256(current_password.encode()).hexdigest() != current_hash:
            return jsonify({'success': False, 'error': 'Password attuale non corretta'}), 400
        
        # Salva la nuova password (temporaneamente in memoria)
        new_hash = hashlib.sha256(new_password.encode()).hexdigest()
        temp_passwords[username] = new_hash
        
        logger.info(f"Password cambiata per utente: {username}")
        
        return jsonify({
            'success': True, 
            'message': 'Password aggiornata con successo (temporaneamente)'
        })
        
    except Exception as e:
        logger.error(f"Errore cambio password: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500