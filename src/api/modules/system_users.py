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
    """Lista utenti di sistema con info complete"""
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
                DATETIME(last_login, 'localtime') as last_login,
                email,
                DATETIME(password_changed_at, 'localtime') as password_changed_at,
                DATETIME(password_expires_at, 'localtime') as password_expires_at,
                must_change_password,
                failed_attempts,
                DATETIME(locked_until, 'localtime') as locked_until,
                nome,
                cognome,
                avatar_path,
                telefono,
                bio
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
                'last_login': row[7] or 'Mai',
                'email': row[8] if len(row) > 8 else None,
                'password_changed_at': row[9] if len(row) > 9 else None,
                'password_expires_at': row[10] if len(row) > 10 else None,
                'must_change_password': bool(row[11]) if len(row) > 11 else False,
                'failed_attempts': row[12] if len(row) > 12 else 0,
                'locked_until': row[13] if len(row) > 13 else None,
                'nome': row[14] if len(row) > 14 else None,
                'cognome': row[15] if len(row) > 15 else None,
                'avatar_path': row[16] if len(row) > 16 else None,
                'telefono': row[17] if len(row) > 17 else None,
                'bio': row[18] if len(row) > 18 else None
            })
        return jsonify({'success': True, 'users': users})
    finally:
        conn.close()

@system_users_bp.route('/api/users/create', methods=['POST'])
@require_auth()
@require_permission('all')
def api_users_create():
    """Crea nuovo utente di sistema con email"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    role = data.get('role', '').strip()
    email = data.get('email', '').strip()
    nome = data.get('nome', '').strip()
    cognome = data.get('cognome', '').strip()
    
    if not username or not password or not role:
        return jsonify({'success': False, 'error': 'Dati mancanti'}), 400
    
    if role not in USER_ROLES:
        return jsonify({'success': False, 'error': 'Ruolo non valido'}), 400
    
    # Valida email se fornita
    if email:
        import re
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            return jsonify({'success': False, 'error': 'Email non valida'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Verifica se username esiste già
        cursor.execute("SELECT 1 FROM utenti_sistema WHERE username = ?", (username,))
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'Username già esistente'}), 400
        
        # Verifica se email esiste già
        if email:
            cursor.execute("SELECT 1 FROM utenti_sistema WHERE email = ?", (email,))
            if cursor.fetchone():
                return jsonify({'success': False, 'error': 'Email già in uso'}), 400
        
        # Inserisci nuovo utente con campi password management
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        from datetime import datetime, timedelta
        password_expires = datetime.now() + timedelta(days=90)
        
        cursor.execute("""
            INSERT INTO utenti_sistema (
                username, password, role, attivo, email, nome, cognome,
                created_at, created_by, last_login,
                password_changed_at, password_expires_at,
                must_change_password, failed_attempts
            ) VALUES (?, ?, ?, 1, ?, ?, ?, CURRENT_TIMESTAMP, ?, NULL, 
                     CURRENT_TIMESTAMP, ?, 1, 0)
        """, (username, password_hash, role, email, nome, cognome, session.get('username'), password_expires))
        
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

@system_users_bp.route('/api/users/admin-set-password', methods=['POST'])
@require_auth()
@require_permission('all')
def api_admin_set_password():
    """Admin imposta direttamente la password di un utente"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    must_change_password = data.get('must_change_password', True)
    
    if not username or not password:
        return jsonify({'success': False, 'error': 'Dati mancanti'}), 400
    
    # VALIDAZIONE RIGOROSA PASSWORD
    import re
    
    errors = []
    
    # Lunghezza minima
    if len(password) < 8:
        errors.append('Minimo 8 caratteri')
    
    # Almeno una maiuscola
    if not re.search(r'[A-Z]', password):
        errors.append('Almeno una lettera maiuscola')
    
    # Almeno una minuscola
    if not re.search(r'[a-z]', password):
        errors.append('Almeno una lettera minuscola')
    
    # Almeno un numero
    if not re.search(r'\d', password):
        errors.append('Almeno un numero')
    
    # Almeno un carattere speciale
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/]', password):
        errors.append('Almeno un carattere speciale')
    
    # Non deve contenere spazi
    if ' ' in password:
        errors.append('Non deve contenere spazi')
    
    # Password comuni da evitare
    common_passwords = ['password', '12345678', 'admin123', 'Password123!', 'Qwerty123!', 
                       'Welcome123!', 'Password1!', 'Admin123!']
    if any(common.lower() in password.lower() for common in common_passwords):
        errors.append('Password troppo comune o prevedibile')
    
    # Se ci sono errori, restituiscili
    if errors:
        return jsonify({
            'success': False, 
            'error': 'Password non valida',
            'details': errors
        }), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Verifica se utente esiste
        cursor.execute("SELECT 1 FROM utenti_sistema WHERE username = ?", (username,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Utente non trovato'}), 404
        
        # Imposta nuova password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        from datetime import datetime, timedelta
        password_expires = datetime.now() + timedelta(days=90)
        
        cursor.execute("""
            UPDATE utenti_sistema 
            SET password = ?,
                password_changed_at = CURRENT_TIMESTAMP,
                password_expires_at = ?,
                must_change_password = ?,
                failed_attempts = 0,
                locked_until = NULL,
                modified_at = CURRENT_TIMESTAMP,
                modified_by = ?
            WHERE username = ?
        """, (password_hash, password_expires, int(must_change_password), 
              session.get('username'), username))
        
        # Log evento
        cursor.execute("""
            INSERT INTO eventi_sistema (tipo_evento, livello, messaggio, componente)
            VALUES (?, ?, ?, ?)
        """, ('ADMIN_PASSWORD_SET', 'WARNING', 
              f'Admin {session.get("username")} ha impostato password per {username}', 
              'USER_MGMT'))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': f'Password impostata per {username}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@system_users_bp.route('/api/users/send-reset-link', methods=['POST'])
@require_auth()
@require_permission('all')
def api_send_reset_link():
    """Admin invia link di reset password a un utente"""
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    custom_message = data.get('message', '').strip()
    
    if not username or not email:
        return jsonify({'success': False, 'error': 'Username e email richiesti'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Verifica utente
        cursor.execute("SELECT attivo FROM utenti_sistema WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'error': 'Utente non trovato'}), 404
        
        if not user[0]:
            return jsonify({'success': False, 'error': 'Utente non attivo'}), 400
        
        # Aggiorna email se diversa
        cursor.execute("""
            UPDATE utenti_sistema 
            SET email = ?, modified_at = CURRENT_TIMESTAMP, modified_by = ?
            WHERE username = ?
        """, (email, session.get('username'), username))
        
        # Genera token reset
        import secrets
        from datetime import datetime, timedelta
        
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=24)  # Link valido 24 ore per admin
        
        # Invalida token precedenti
        cursor.execute("""
            UPDATE password_reset_tokens 
            SET used = 1 
            WHERE username = ? AND used = 0
        """, (username,))
        
        # Crea nuovo token
        cursor.execute("""
            INSERT INTO password_reset_tokens (username, token, expires_at, ip_address)
            VALUES (?, ?, ?, ?)
        """, (username, token, expires_at, request.remote_addr))
        
        # Prepara e invia email
        reset_url = f"http://192.168.1.236:5000/reset-password?token={token}"
        
        # Recupera configurazione SMTP
        cursor.execute("SELECT key, value FROM system_settings WHERE key LIKE 'email.%' OR key = 'sistema.nome_installazione'")
        email_config = dict(cursor.fetchall())
        
        # Recupera il nome installazione o usa default
        nome_installazione = email_config.get('sistema.nome_installazione', 'Sistema Controllo Accessi')
        
        if email_config.get('email.smtp_server') and email_config.get('email.enabled') == '1':
            # Invia email reale
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Reset Password - Sistema Controllo Accessi'
            msg['From'] = email_config.get('email.mittente', 'noreply@sistema.local')
            msg['To'] = email
            
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #4c51bf;">Reset Password</h2>
                        <p>Ciao <strong>{username}</strong>,</p>
                        <p>L'amministratore del sistema ti ha inviato un link per reimpostare la password.</p>
                        {f'<p style="background: #f0f0f0; padding: 10px; border-radius: 5px;">{custom_message}</p>' if custom_message else ''}
                        <p>Clicca sul pulsante qui sotto per creare una nuova password:</p>
                        <p style="margin: 20px 0;">
                            <a href="{reset_url}" 
                               style="background: #4c51bf; color: white; padding: 12px 24px; 
                                      text-decoration: none; border-radius: 5px; display: inline-block;">
                                Reset Password
                            </a>
                        </p>
                        <p>Oppure copia questo link nel browser:</p>
                        <p style="background: #f4f4f4; padding: 10px; word-break: break-all; font-size: 12px;">
                            {reset_url}
                        </p>
                        <p><strong>Il link scade tra 24 ore.</strong></p>
                        <hr style="margin: 20px 0;">
                        <p style="color: #666; font-size: 12px;">
                            Sistema Controllo Accessi - {nome_installazione}<br>
                            Inviato da: {session.get('username')} (Amministratore)
                        </p>
                    </div>
                </body>
            </html>
            """
            
            part = MIMEText(html, 'html')
            msg.attach(part)
            
            try:
                smtp_port = int(email_config.get('email.smtp_port', 587))
                server = smtplib.SMTP(email_config['email.smtp_server'], smtp_port)
                server.starttls()
                
                if email_config.get('email.username') and email_config.get('email.password'):
                    server.login(email_config['email.username'], email_config['email.password'])
                
                server.send_message(msg)
                server.quit()
                
                # Log evento
                cursor.execute("""
                    INSERT INTO eventi_sistema (tipo_evento, livello, messaggio, componente)
                    VALUES (?, ?, ?, ?)
                """, ('RESET_LINK_SENT', 'INFO', 
                      f'Link reset inviato a {username} ({email}) da {session.get("username")}', 
                      'USER_MGMT'))
                
                conn.commit()
                
                return jsonify({
                    'success': True,
                    'message': f'Link di reset inviato a {email}'
                })
                
            except Exception as e:
                # Email fallita ma token creato
                conn.commit()
                return jsonify({
                    'success': True,
                    'message': 'Token generato (invio email fallito)',
                    'debug_token': token,
                    'error': str(e)
                })
        else:
            # Email non configurata, restituisci token per debug
            conn.commit()
            return jsonify({
                'success': True,
                'message': 'Token generato (email non configurata)',
                'debug_token': token
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
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

@system_users_bp.route('/api/users/update-profile', methods=['POST'])
@require_auth()
def api_update_profile():
    """Aggiorna il profilo utente con campi aggiuntivi e avatar"""
    from werkzeug.utils import secure_filename
    import uuid
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Ottieni dati dal form
        username = request.form.get('username')
        if not username:
            return jsonify({'success': False, 'error': 'Username mancante'}), 400
        
        # Verifica che l'utente esista
        cursor.execute("SELECT username, role FROM utenti_sistema WHERE username = ?", (username,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'success': False, 'error': 'Utente non trovato'}), 404
        
        # Controlla permessi
        current_user = session.get('username')
        current_role = session.get('role')
        
        # Solo admin o user_manager possono modificare altri utenti
        if current_user != username and current_role not in ['admin', 'user_manager']:
            return jsonify({'success': False, 'error': 'Permessi insufficienti'}), 403
        
        # Prepara i campi da aggiornare
        update_fields = []
        update_values = []
        
        # Campi profilo
        profile_fields = ['nome', 'cognome', 'email', 'telefono', 'bio']
        for field in profile_fields:
            if field in request.form:
                update_fields.append(f"{field} = ?")
                update_values.append(request.form.get(field))
        
        # Ruolo (solo admin può modificare)
        if 'role' in request.form and current_role == 'admin':
            new_role = request.form.get('role')
            if new_role in USER_ROLES:
                update_fields.append("role = ?")
                update_values.append(new_role)
        
        # Gestione avatar upload
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename:
                # Genera nome univoco per il file
                ext = os.path.splitext(secure_filename(file.filename))[1]
                if ext.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    filename = f"{username}_{uuid.uuid4().hex[:8]}{ext}"
                    avatar_path = os.path.join('/opt/access_control/src/api/static/avatars', filename)
                    
                    # Salva il file
                    file.save(avatar_path)
                    
                    # Aggiungi path al database (relativo per URL)
                    update_fields.append("avatar_path = ?")
                    update_values.append(f"/api/static/avatars/{filename}")
        
        # Aggiorna timestamp modifica
        update_fields.append("modified_at = CURRENT_TIMESTAMP")
        update_fields.append("modified_by = ?")
        update_values.append(current_user)
        
        # Aggiungi username alla fine per WHERE clause
        update_values.append(username)
        
        # Esegui update
        if update_fields:
            query = f"UPDATE utenti_sistema SET {', '.join(update_fields)} WHERE username = ?"
            cursor.execute(query, update_values)
            conn.commit()
        
        # Recupera i dati aggiornati
        cursor.execute("""
            SELECT username, nome, cognome, email, telefono, bio, avatar_path, role
            FROM utenti_sistema WHERE username = ?
        """, (username,))
        updated_user = cursor.fetchone()
        
        return jsonify({
            'success': True,
            'message': 'Profilo aggiornato con successo',
            'user': {
                'username': updated_user[0],
                'nome': updated_user[1],
                'cognome': updated_user[2],
                'email': updated_user[3],
                'telefono': updated_user[4],
                'bio': updated_user[5],
                'avatar_path': updated_user[6],
                'role': updated_user[7]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()
