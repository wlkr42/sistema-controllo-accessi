# File: /opt/access_control/src/api/modules/password_management.py
# Sistema completo di gestione password con reset, recupero e validazione

from flask import Blueprint, jsonify, request, session, render_template_string
import hashlib
import secrets
import sqlite3
import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Blueprint per gestione password
password_management_bp = Blueprint('password_management', __name__)

# Import path database
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.dirname(parent_dir))
from core.db_config import CURRENT_DB_PATH as DB_PATH

# Import delle funzioni di utilità
def get_db_connection():
    """Connessione al database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Errore connessione DB: {e}")
        return None

def require_auth():
    """Placeholder per import"""
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            from flask import session, redirect
            if not session.get('logged_in'):
                return redirect('/login')
            return f(*args, **kwargs)
        return wrapper
    return decorator

def require_permission(*perms):
    """Placeholder per import"""
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapper
    return decorator

def init_password_tables():
    """Inizializza tabelle per gestione password avanzata"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Tabella per reset tokens
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at DATETIME NOT NULL,
                used BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                used_at DATETIME,
                ip_address TEXT,
                FOREIGN KEY (username) REFERENCES utenti_sistema(username)
            )
        ''')
        
        # Tabella per storico password
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                changed_by TEXT,
                reason TEXT,
                FOREIGN KEY (username) REFERENCES utenti_sistema(username)
            )
        ''')
        
        # Tabella per politiche password
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_policies (
                id INTEGER PRIMARY KEY,
                min_length INTEGER DEFAULT 8,
                require_uppercase BOOLEAN DEFAULT 1,
                require_lowercase BOOLEAN DEFAULT 1,
                require_numbers BOOLEAN DEFAULT 1,
                require_special BOOLEAN DEFAULT 1,
                max_age_days INTEGER DEFAULT 90,
                min_age_hours INTEGER DEFAULT 24,
                history_count INTEGER DEFAULT 5,
                max_attempts INTEGER DEFAULT 5,
                lockout_minutes INTEGER DEFAULT 30,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_by TEXT
            )
        ''')
        
        # Inserisci policy default se non esiste
        cursor.execute('SELECT COUNT(*) FROM password_policies')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO password_policies (
                    id, min_length, require_uppercase, require_lowercase,
                    require_numbers, require_special, max_age_days,
                    min_age_hours, history_count, max_attempts, lockout_minutes
                ) VALUES (1, 8, 1, 1, 1, 1, 90, 24, 5, 5, 30)
            ''')
        
        # Aggiungi colonne mancanti a utenti_sistema
        cursor.execute("PRAGMA table_info(utenti_sistema)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'email' not in columns:
            cursor.execute('ALTER TABLE utenti_sistema ADD COLUMN email TEXT')
        if 'password_changed_at' not in columns:
            cursor.execute('ALTER TABLE utenti_sistema ADD COLUMN password_changed_at DATETIME')
        if 'password_expires_at' not in columns:
            cursor.execute('ALTER TABLE utenti_sistema ADD COLUMN password_expires_at DATETIME')
        if 'failed_attempts' not in columns:
            cursor.execute('ALTER TABLE utenti_sistema ADD COLUMN failed_attempts INTEGER DEFAULT 0')
        if 'locked_until' not in columns:
            cursor.execute('ALTER TABLE utenti_sistema ADD COLUMN locked_until DATETIME')
        if 'must_change_password' not in columns:
            cursor.execute('ALTER TABLE utenti_sistema ADD COLUMN must_change_password BOOLEAN DEFAULT 0')
        
        conn.commit()
        logger.info("Tabelle gestione password inizializzate")
        return True
        
    except Exception as e:
        logger.error(f"Errore inizializzazione tabelle password: {e}")
        return False
    finally:
        conn.close()

def validate_password_strength(password, username=None):
    """Valida la forza della password secondo le policy"""
    conn = get_db_connection()
    if not conn:
        return False, "Database non disponibile"
    
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM password_policies WHERE id = 1')
        policy = cursor.fetchone()
        
        if not policy:
            return False, "Policy password non configurate"
        
        errors = []
        
        # Lunghezza minima
        if len(password) < policy[1]:  # min_length
            errors.append(f"Minimo {policy[1]} caratteri")
        
        # Maiuscole
        if policy[2] and not re.search(r'[A-Z]', password):  # require_uppercase
            errors.append("Almeno una lettera maiuscola")
        
        # Minuscole
        if policy[3] and not re.search(r'[a-z]', password):  # require_lowercase
            errors.append("Almeno una lettera minuscola")
        
        # Numeri
        if policy[4] and not re.search(r'\d', password):  # require_numbers
            errors.append("Almeno un numero")
        
        # Caratteri speciali
        if policy[5] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):  # require_special
            errors.append("Almeno un carattere speciale")
        
        # Controlla che non sia uguale username
        if username and password.lower() == username.lower():
            errors.append("La password non può essere uguale all'username")
        
        # Controlla password comuni
        common_passwords = ['password', '12345678', 'admin123', 'qwerty', 'letmein']
        if password.lower() in common_passwords:
            errors.append("Password troppo comune")
        
        if errors:
            return False, "Password non valida: " + ", ".join(errors)
        
        return True, "Password valida"
        
    except Exception as e:
        logger.error(f"Errore validazione password: {e}")
        return False, str(e)
    finally:
        conn.close()

def check_password_history(username, new_password_hash):
    """Verifica che la password non sia stata usata recentemente"""
    conn = get_db_connection()
    if not conn:
        return True  # In caso di errore, permetti il cambio
    
    try:
        cursor = conn.cursor()
        
        # Recupera policy
        cursor.execute('SELECT history_count FROM password_policies WHERE id = 1')
        policy = cursor.fetchone()
        history_count = policy[0] if policy else 5
        
        # Recupera ultime N password
        cursor.execute('''
            SELECT password_hash FROM password_history 
            WHERE username = ? 
            ORDER BY changed_at DESC 
            LIMIT ?
        ''', (username, history_count))
        
        old_passwords = cursor.fetchall()
        
        for old_pass in old_passwords:
            if old_pass[0] == new_password_hash:
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Errore controllo storico password: {e}")
        return True
    finally:
        conn.close()

def generate_reset_token(username):
    """Genera token sicuro per reset password"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=1)
    
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # Invalida token precedenti
        cursor.execute('''
            UPDATE password_reset_tokens 
            SET used = 1 
            WHERE username = ? AND used = 0
        ''', (username,))
        
        # Crea nuovo token
        cursor.execute('''
            INSERT INTO password_reset_tokens (username, token, expires_at, ip_address)
            VALUES (?, ?, ?, ?)
        ''', (username, token, expires_at, request.remote_addr))
        
        conn.commit()
        return token
        
    except Exception as e:
        logger.error(f"Errore generazione token: {e}")
        return None
    finally:
        conn.close()

def send_reset_email(email, username, token):
    """Invia email con link di reset password"""
    try:
        # Recupera configurazione SMTP dal database
        conn = get_db_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT key, value FROM system_settings 
            WHERE key LIKE 'email.%' OR key = 'sistema.nome_installazione'
        """)
        
        email_config = dict(cursor.fetchall())
        conn.close()
        
        if not email_config.get('email.smtp_server'):
            logger.warning("Server SMTP non configurato")
            return False
        
        # Recupera il nome installazione o usa default
        nome_installazione = email_config.get('sistema.nome_installazione', 'Sistema Controllo Accessi')
        
        # Prepara email
        reset_url = f"http://192.168.1.236:5000/reset-password?token={token}"
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Reset Password - Sistema Controllo Accessi'
        msg['From'] = email_config.get('email.mittente', 'noreply@sistema.local')
        msg['To'] = email
        
        # Corpo HTML
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #4c51bf;">Reset Password</h2>
                    <p>Ciao <strong>{username}</strong>,</p>
                    <p>Hai richiesto il reset della password per il Sistema Controllo Accessi.</p>
                    <p>Clicca sul link seguente per reimpostare la password:</p>
                    <p style="margin: 20px 0;">
                        <a href="{reset_url}" 
                           style="background: #4c51bf; color: white; padding: 10px 20px; 
                                  text-decoration: none; border-radius: 5px;">
                            Reset Password
                        </a>
                    </p>
                    <p>Oppure copia questo link nel browser:</p>
                    <p style="background: #f4f4f4; padding: 10px; word-break: break-all;">
                        {reset_url}
                    </p>
                    <p><strong>Il link scade tra 1 ora.</strong></p>
                    <p>Se non hai richiesto il reset, ignora questa email.</p>
                    <hr style="margin: 20px 0;">
                    <p style="color: #666; font-size: 12px;">
                        Sistema Controllo Accessi - {nome_installazione}
                    </p>
                </div>
            </body>
        </html>
        """
        
        part = MIMEText(html, 'html')
        msg.attach(part)
        
        # Invia email
        server = smtplib.SMTP(
            email_config.get('email.smtp_server'),
            int(email_config.get('email.smtp_port', 587))
        )
        server.starttls()
        
        if email_config.get('email.username') and email_config.get('email.password'):
            server.login(
                email_config.get('email.username'),
                email_config.get('email.password')
            )
        
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email reset inviata a {email}")
        return True
        
    except Exception as e:
        logger.error(f"Errore invio email: {e}")
        return False

# ===== ENDPOINTS API =====

@password_management_bp.route('/api/password/validate', methods=['POST'])
@require_auth()
def api_validate_password():
    """Valida una password secondo le policy"""
    data = request.get_json()
    password = data.get('password', '')
    username = data.get('username', session.get('username'))
    
    valid, message = validate_password_strength(password, username)
    
    return jsonify({
        'success': valid,
        'message': message,
        'strength': calculate_password_strength(password) if valid else 0
    })

@password_management_bp.route('/api/password/change', methods=['POST'])
@require_auth()
def api_change_password():
    """Cambio password con validazione completa"""
    data = request.get_json()
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')
    username = session.get('username')
    
    # Validazioni base
    if not all([current_password, new_password, confirm_password]):
        return jsonify({'success': False, 'error': 'Tutti i campi sono richiesti'}), 400
    
    if new_password != confirm_password:
        return jsonify({'success': False, 'error': 'Le password non coincidono'}), 400
    
    # Valida forza password
    valid, message = validate_password_strength(new_password, username)
    if not valid:
        return jsonify({'success': False, 'error': message}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Verifica password corrente
        cursor.execute('''
            SELECT password, password_changed_at 
            FROM utenti_sistema 
            WHERE username = ?
        ''', (username,))
        
        user = cursor.fetchone()
        if not user:
            return jsonify({'success': False, 'error': 'Utente non trovato'}), 404
        
        current_hash = hashlib.sha256(current_password.encode()).hexdigest()
        if current_hash != user[0]:
            return jsonify({'success': False, 'error': 'Password attuale non corretta'}), 400
        
        # Verifica tempo minimo tra cambi
        if user[1]:
            last_change = datetime.fromisoformat(user[1])
            cursor.execute('SELECT min_age_hours FROM password_policies WHERE id = 1')
            policy = cursor.fetchone()
            min_hours = policy[0] if policy else 24
            
            if (datetime.now() - last_change).total_seconds() < min_hours * 3600:
                return jsonify({
                    'success': False, 
                    'error': f'Devi attendere {min_hours} ore tra un cambio password e l\'altro'
                }), 400
        
        new_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        # Verifica storico password
        if not check_password_history(username, new_hash):
            return jsonify({
                'success': False,
                'error': 'Password già utilizzata recentemente'
            }), 400
        
        # Aggiorna password
        cursor.execute('SELECT max_age_days FROM password_policies WHERE id = 1')
        policy = cursor.fetchone()
        max_days = policy[0] if policy else 90
        expires_at = datetime.now() + timedelta(days=max_days)
        
        cursor.execute('''
            UPDATE utenti_sistema 
            SET password = ?,
                password_changed_at = CURRENT_TIMESTAMP,
                password_expires_at = ?,
                must_change_password = 0,
                failed_attempts = 0,
                locked_until = NULL,
                modified_at = CURRENT_TIMESTAMP,
                modified_by = ?
            WHERE username = ?
        ''', (new_hash, expires_at, username, username))
        
        # Salva in storico
        cursor.execute('''
            INSERT INTO password_history (username, password_hash, changed_by, reason)
            VALUES (?, ?, ?, ?)
        ''', (username, new_hash, username, 'Cambio volontario'))
        
        # Log evento
        cursor.execute('''
            INSERT INTO eventi_sistema (tipo_evento, livello, messaggio, componente)
            VALUES (?, ?, ?, ?)
        ''', ('PASSWORD_CHANGE', 'INFO', f'Password cambiata per utente {username}', 'PASSWORD_MGMT'))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password aggiornata con successo',
            'expires_at': expires_at.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Errore cambio password: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@password_management_bp.route('/api/password/forgot', methods=['POST'])
def api_forgot_password():
    """Richiesta reset password"""
    data = request.get_json()
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'success': False, 'error': 'Username richiesto'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Verifica utente e recupera email
        cursor.execute('''
            SELECT email, attivo 
            FROM utenti_sistema 
            WHERE username = ?
        ''', (username,))
        
        user = cursor.fetchone()
        
        # Sempre restituisci successo per sicurezza
        if not user or not user[0] or not user[1]:
            logger.warning(f"Reset password richiesto per utente inesistente/inattivo: {username}")
            return jsonify({
                'success': True,
                'message': 'Se l\'utente esiste, riceverà un\'email con le istruzioni'
            })
        
        email = user[0]
        
        # Genera token
        token = generate_reset_token(username)
        if not token:
            return jsonify({'success': False, 'error': 'Errore generazione token'}), 500
        
        # Invia email
        email_sent = send_reset_email(email, username, token)
        
        # Log evento
        cursor.execute('''
            INSERT INTO eventi_sistema (tipo_evento, livello, messaggio, componente)
            VALUES (?, ?, ?, ?)
        ''', ('PASSWORD_RESET_REQUEST', 'INFO', 
              f'Reset password richiesto per {username} - Email: {"inviata" if email_sent else "non inviata"}',
              'PASSWORD_MGMT'))
        
        conn.commit()
        
        if not email_sent:
            # Se email non configurata, mostra il token (solo per sviluppo)
            logger.warning(f"Email non inviata. Token reset per {username}: {token}")
            return jsonify({
                'success': True,
                'message': 'Token generato (email non configurata)',
                'debug_token': token if not email_sent else None
            })
        
        return jsonify({
            'success': True,
            'message': 'Email inviata con le istruzioni per il reset'
        })
        
    except Exception as e:
        logger.error(f"Errore richiesta reset: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@password_management_bp.route('/api/password/reset', methods=['POST'])
def api_reset_password():
    """Reset password con token"""
    data = request.get_json()
    token = data.get('token', '').strip()
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')
    
    if not all([token, new_password, confirm_password]):
        return jsonify({'success': False, 'error': 'Dati mancanti'}), 400
    
    if new_password != confirm_password:
        return jsonify({'success': False, 'error': 'Le password non coincidono'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Verifica token
        cursor.execute('''
            SELECT username, expires_at, used 
            FROM password_reset_tokens 
            WHERE token = ?
        ''', (token,))
        
        token_data = cursor.fetchone()
        
        if not token_data:
            return jsonify({'success': False, 'error': 'Token non valido'}), 400
        
        if token_data[2]:  # used
            return jsonify({'success': False, 'error': 'Token già utilizzato'}), 400
        
        if datetime.now() > datetime.fromisoformat(token_data[1]):
            return jsonify({'success': False, 'error': 'Token scaduto'}), 400
        
        username = token_data[0]
        
        # Valida password
        valid, message = validate_password_strength(new_password, username)
        if not valid:
            return jsonify({'success': False, 'error': message}), 400
        
        new_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        # Verifica storico
        if not check_password_history(username, new_hash):
            return jsonify({
                'success': False,
                'error': 'Password già utilizzata recentemente'
            }), 400
        
        # Aggiorna password
        cursor.execute('SELECT max_age_days FROM password_policies WHERE id = 1')
        policy = cursor.fetchone()
        max_days = policy[0] if policy else 90
        expires_at = datetime.now() + timedelta(days=max_days)
        
        cursor.execute('''
            UPDATE utenti_sistema 
            SET password = ?,
                password_changed_at = CURRENT_TIMESTAMP,
                password_expires_at = ?,
                must_change_password = 0,
                failed_attempts = 0,
                locked_until = NULL,
                modified_at = CURRENT_TIMESTAMP,
                modified_by = 'SYSTEM_RESET'
            WHERE username = ?
        ''', (new_hash, expires_at, username))
        
        # Marca token come usato
        cursor.execute('''
            UPDATE password_reset_tokens 
            SET used = 1, used_at = CURRENT_TIMESTAMP 
            WHERE token = ?
        ''', (token,))
        
        # Salva in storico
        cursor.execute('''
            INSERT INTO password_history (username, password_hash, changed_by, reason)
            VALUES (?, ?, ?, ?)
        ''', (username, new_hash, 'SYSTEM', 'Reset password'))
        
        # Log evento
        cursor.execute('''
            INSERT INTO eventi_sistema (tipo_evento, livello, messaggio, componente)
            VALUES (?, ?, ?, ?)
        ''', ('PASSWORD_RESET', 'WARNING', f'Password resettata per utente {username}', 'PASSWORD_MGMT'))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password resettata con successo'
        })
        
    except Exception as e:
        logger.error(f"Errore reset password: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@password_management_bp.route('/api/password/policy', methods=['GET'])
@require_auth()
def api_get_password_policy():
    """Recupera policy password correnti"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM password_policies WHERE id = 1')
        policy = cursor.fetchone()
        
        if not policy:
            return jsonify({'success': False, 'error': 'Policy non configurate'}), 404
        
        return jsonify({
            'success': True,
            'policy': {
                'min_length': policy[1],
                'require_uppercase': bool(policy[2]),
                'require_lowercase': bool(policy[3]),
                'require_numbers': bool(policy[4]),
                'require_special': bool(policy[5]),
                'max_age_days': policy[6],
                'min_age_hours': policy[7],
                'history_count': policy[8],
                'max_attempts': policy[9],
                'lockout_minutes': policy[10]
            }
        })
        
    except Exception as e:
        logger.error(f"Errore recupero policy: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@password_management_bp.route('/api/password/policy', methods=['POST'])
@require_auth()
@require_permission('all')
def api_update_password_policy():
    """Aggiorna policy password (solo admin)"""
    data = request.get_json()
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE password_policies 
            SET min_length = ?,
                require_uppercase = ?,
                require_lowercase = ?,
                require_numbers = ?,
                require_special = ?,
                max_age_days = ?,
                min_age_hours = ?,
                history_count = ?,
                max_attempts = ?,
                lockout_minutes = ?,
                updated_at = CURRENT_TIMESTAMP,
                updated_by = ?
            WHERE id = 1
        ''', (
            data.get('min_length', 8),
            int(data.get('require_uppercase', True)),
            int(data.get('require_lowercase', True)),
            int(data.get('require_numbers', True)),
            int(data.get('require_special', True)),
            data.get('max_age_days', 90),
            data.get('min_age_hours', 24),
            data.get('history_count', 5),
            data.get('max_attempts', 5),
            data.get('lockout_minutes', 30),
            session.get('username')
        ))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Policy password aggiornate'
        })
        
    except Exception as e:
        logger.error(f"Errore aggiornamento policy: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

def calculate_password_strength(password):
    """Calcola forza password (0-100)"""
    strength = 0
    
    # Lunghezza
    if len(password) >= 8:
        strength += 20
    if len(password) >= 12:
        strength += 10
    if len(password) >= 16:
        strength += 10
    
    # Complessità
    if re.search(r'[a-z]', password):
        strength += 15
    if re.search(r'[A-Z]', password):
        strength += 15
    if re.search(r'\d', password):
        strength += 15
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        strength += 15
    
    return min(strength, 100)

# Inizializza tabelle al caricamento del modulo
init_password_tables()