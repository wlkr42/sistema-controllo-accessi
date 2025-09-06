# File: /opt/access_control/src/api/modules/email_config.py
# Modulo per configurazione servizio email SMTP

from flask import Blueprint, jsonify, request, session
import sqlite3
import os
import smtplib
import logging
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

# Blueprint per configurazione email
email_config_bp = Blueprint('email_config', __name__)

# Import database path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.db_config import CURRENT_DB_PATH as DB_PATH
from ..auth import require_auth, require_permission
from ..utils import get_db_connection

def init_email_settings():
    """Inizializza le impostazioni email nel database"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Impostazioni email di default
        email_settings = [
            ('email.smtp_server', ''),
            ('email.smtp_port', '587'),
            ('email.smtp_security', 'STARTTLS'),  # STARTTLS, SSL, NONE
            ('email.username', ''),
            ('email.password', ''),
            ('email.mittente', 'noreply@sistema.local'),
            ('email.nome_mittente', 'Sistema Controllo Accessi'),
            ('email.enabled', '0'),
            ('email.test_recipient', ''),
        ]
        
        for key, default_value in email_settings:
            cursor.execute("""
                INSERT OR IGNORE INTO system_settings (key, value)
                VALUES (?, ?)
            """, (key, default_value))
        
        conn.commit()
        return True
        
    except Exception as e:
        logger.error(f"Errore inizializzazione email settings: {e}")
        return False
    finally:
        conn.close()

@email_config_bp.route('/api/email/config', methods=['GET'])
@require_auth()
@require_permission('all')
def get_email_config():
    """Recupera configurazione email"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT key, value FROM system_settings 
            WHERE key LIKE 'email.%'
        """)
        
        settings = {}
        for row in cursor.fetchall():
            key = row[0].replace('email.', '')
            # Non restituire la password in chiaro
            if key == 'password' and row[1]:
                settings[key] = '********'
            else:
                settings[key] = row[1]
        
        return jsonify({
            'success': True,
            'config': settings
        })
        
    except Exception as e:
        logger.error(f"Errore recupero config email: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@email_config_bp.route('/api/email/config', methods=['POST'])
@require_auth()
@require_permission('all')
def save_email_config():
    """Salva configurazione email"""
    data = request.get_json()
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Mappa configurazioni
        config_map = {
            'smtp_server': 'email.smtp_server',
            'smtp_port': 'email.smtp_port',
            'smtp_security': 'email.smtp_security',
            'username': 'email.username',
            'password': 'email.password',
            'mittente': 'email.mittente',
            'nome_mittente': 'email.nome_mittente',
            'enabled': 'email.enabled',
            'test_recipient': 'email.test_recipient'
        }
        
        for field, db_key in config_map.items():
            if field in data:
                value = data[field]
                # Non aggiornare password se è mascherata
                if field == 'password' and value == '********':
                    continue
                    
                cursor.execute("""
                    UPDATE system_settings 
                    SET value = ? 
                    WHERE key = ?
                """, (value, db_key))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Configurazione email salvata'
        })
        
    except Exception as e:
        logger.error(f"Errore salvataggio config email: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@email_config_bp.route('/api/email/test', methods=['POST'])
@require_auth()
@require_permission('all')
def test_email():
    """Test invio email"""
    data = request.get_json()
    test_email = data.get('email', '').strip()
    
    if not test_email:
        return jsonify({'success': False, 'error': 'Email destinatario richiesta'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT key, value FROM system_settings 
            WHERE key LIKE 'email.%'
        """)
        
        config = dict(cursor.fetchall())
        conn.close()
        
        if not config.get('email.smtp_server'):
            return jsonify({'success': False, 'error': 'Server SMTP non configurato'}), 400
        
        # Prepara email di test
        msg = MIMEText("""
        Questa è un'email di test dal Sistema Controllo Accessi.
        
        Se ricevi questa email, la configurazione SMTP è corretta!
        
        ---
        Sistema Controllo Accessi
        Isola Ecologica RAEE - Rende
        """)
        
        msg['Subject'] = 'Test Email - Sistema Controllo Accessi'
        msg['From'] = f"{config.get('email.nome_mittente', 'Sistema')} <{config.get('email.mittente', 'noreply@sistema.local')}>"
        msg['To'] = test_email
        
        # Connessione SMTP
        smtp_port = int(config.get('email.smtp_port', 587))
        smtp_security = config.get('email.smtp_security', 'STARTTLS')
        
        if smtp_security == 'SSL':
            server = smtplib.SMTP_SSL(config['email.smtp_server'], smtp_port)
        else:
            server = smtplib.SMTP(config['email.smtp_server'], smtp_port)
            if smtp_security == 'STARTTLS':
                server.starttls()
        
        if config.get('email.username') and config.get('email.password'):
            server.login(config['email.username'], config['email.password'])
        
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email di test inviata a {test_email}")
        
        return jsonify({
            'success': True,
            'message': f'Email di test inviata a {test_email}'
        })
        
    except Exception as e:
        logger.error(f"Errore invio email test: {e}")
        return jsonify({'success': False, 'error': f'Errore invio: {str(e)}'}), 500

# Template HTML per configurazione email
EMAIL_CONFIG_TEMPLATE = """
<div class="card">
    <div class="card-header">
        <h5 class="mb-0">
            <i class="fas fa-envelope me-2"></i>Configurazione Email SMTP
        </h5>
    </div>
    <div class="card-body">
        <form id="email-config-form">
            <div class="row">
                <div class="col-md-8">
                    <div class="mb-3">
                        <label class="form-label">Server SMTP</label>
                        <input type="text" class="form-control" id="smtp-server" 
                               placeholder="smtp.gmail.com">
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="mb-3">
                        <label class="form-label">Porta</label>
                        <input type="number" class="form-control" id="smtp-port" 
                               value="587">
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Sicurezza</label>
                        <select class="form-select" id="smtp-security">
                            <option value="STARTTLS">STARTTLS (Consigliato)</option>
                            <option value="SSL">SSL/TLS</option>
                            <option value="NONE">Nessuna</option>
                        </select>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Email Mittente</label>
                        <input type="email" class="form-control" id="email-mittente" 
                               placeholder="noreply@sistema.local">
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Username SMTP</label>
                        <input type="text" class="form-control" id="smtp-username" 
                               placeholder="username@gmail.com">
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Password SMTP</label>
                        <input type="password" class="form-control" id="smtp-password" 
                               placeholder="Password SMTP">
                    </div>
                </div>
            </div>
            
            <div class="form-check mb-3">
                <input type="checkbox" class="form-check-input" id="email-enabled">
                <label class="form-check-label" for="email-enabled">
                    Abilita invio email
                </label>
            </div>
            
            <div class="d-flex gap-2">
                <button type="submit" class="btn btn-primary">
                    <i class="fas fa-save me-2"></i>Salva Configurazione
                </button>
                <button type="button" class="btn btn-info" onclick="testEmailConfig()">
                    <i class="fas fa-paper-plane me-2"></i>Test Email
                </button>
            </div>
        </form>
        
        <div id="email-status" class="mt-3"></div>
    </div>
</div>

<script>
// Carica configurazione email
async function loadEmailConfig() {
    try {
        const response = await fetch('/api/email/config');
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('smtp-server').value = data.config.smtp_server || '';
            document.getElementById('smtp-port').value = data.config.smtp_port || '587';
            document.getElementById('smtp-security').value = data.config.smtp_security || 'STARTTLS';
            document.getElementById('smtp-username').value = data.config.username || '';
            document.getElementById('smtp-password').value = data.config.password || '';
            document.getElementById('email-mittente').value = data.config.mittente || '';
            document.getElementById('email-enabled').checked = data.config.enabled === '1';
        }
    } catch (error) {
        console.error('Errore caricamento config email:', error);
    }
}

// Salva configurazione email
document.getElementById('email-config-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const config = {
        smtp_server: document.getElementById('smtp-server').value,
        smtp_port: document.getElementById('smtp-port').value,
        smtp_security: document.getElementById('smtp-security').value,
        username: document.getElementById('smtp-username').value,
        password: document.getElementById('smtp-password').value,
        mittente: document.getElementById('email-mittente').value,
        enabled: document.getElementById('email-enabled').checked ? '1' : '0'
    };
    
    try {
        const response = await fetch('/api/email/config', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(config)
        });
        
        const data = await response.json();
        
        const statusDiv = document.getElementById('email-status');
        if (data.success) {
            statusDiv.innerHTML = '<div class="alert alert-success">Configurazione salvata</div>';
        } else {
            statusDiv.innerHTML = `<div class="alert alert-danger">Errore: ${data.error}</div>`;
        }
    } catch (error) {
        document.getElementById('email-status').innerHTML = 
            '<div class="alert alert-danger">Errore di connessione</div>';
    }
});

// Test invio email
async function testEmailConfig() {
    const email = prompt('Inserisci email destinatario per il test:');
    if (!email) return;
    
    try {
        const response = await fetch('/api/email/test', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email: email})
        });
        
        const data = await response.json();
        
        const statusDiv = document.getElementById('email-status');
        if (data.success) {
            statusDiv.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
        } else {
            statusDiv.innerHTML = `<div class="alert alert-danger">Errore: ${data.error}</div>`;
        }
    } catch (error) {
        document.getElementById('email-status').innerHTML = 
            '<div class="alert alert-danger">Errore di connessione</div>';
    }
}

// Carica config all'avvio
loadEmailConfig();
</script>
"""

# Inizializza impostazioni email
init_email_settings()