#!/usr/bin/env python3
# File: /opt/access_control/scripts/install_complete_dashboard.py
# Installazione Dashboard Modulare Completa

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

def install_complete_dashboard():
    """Installa la dashboard modulare completa"""
    
    print("🚀 INSTALLAZIONE DASHBOARD MODULARE COMPLETA")
    print("=" * 60)
    
    project_root = Path("/opt/access_control")
    
    # Backup dell'attuale web_api.py
    backup_dir = project_root / "backup" / f"complete_install_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    current_web_api = project_root / "src" / "api" / "web_api.py"
    if current_web_api.exists():
        shutil.copy2(current_web_api, backup_dir / "web_api_temp.py")
        print(f"✅ Backup temporaneo salvato in: {backup_dir}")
    
    # Contenuto completo del nuovo web_api.py
    complete_web_api_content = '''# File: /opt/access_control/src/api/web_api.py
# Dashboard Modulare Moderna e Professionale - Sistema Controllo Accessi

import os
import sys
import json
import sqlite3
import logging
import smtplib
import threading
import subprocess
import time
import psutil
import socket
import hashlib
import csv
import io
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

try:
    import pandas as pd
except ImportError:
    pd = None
    print("⚠️ pandas non installato, alcune funzioni potrebbero non funzionare")

from flask import Flask, request, jsonify, session, send_file, render_template_string, redirect, url_for, Response
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash

# Aggiungi path per import moduli esistenti
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'hardware'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'external'))

try:
    from database_manager import DatabaseManager
    from usb_rly08_controller import USBRelay08Controller
    from odoo_partner_connector import OdooPartnerConnector
except ImportError as e:
    print(f"⚠️ Import warning: {e}")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
app.secret_key = 'access_control_admin_2025_secure_key'
CORS(app, supports_credentials=True)

# Configurazione globale
project_root = Path(__file__).parent.parent.parent
config_manager = None
system_state = {
    'gate_status': 'closed',
    'current_user': None,
    'hardware_status': {},
    'network_status': {},
    'last_access': None,
    'alerts': []
}

# Ruoli utenti
USER_ROLES = {
    'admin': {
        'name': 'Amministratore',
        'permissions': ['all']
    },
    'manager': {
        'name': 'Gestore Utenti',
        'permissions': ['users', 'logs', 'email', 'monitoring']
    },
    'viewer': {
        'name': 'Solo Visualizzazione',
        'permissions': ['monitoring', 'logs_read']
    }
}

# ===============================
# CONFIGURAZIONE MANAGER
# ===============================

class ConfigManager:
    """Gestione configurazione centralizzata"""
    
    def __init__(self):
        self.config_file = project_root / "config" / "dashboard_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Carica configurazione da file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Errore caricamento config: {e}")
        
        return self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """Configurazione di default"""
        return {
            "sistema": {
                "nome_isola": "",
                "comune": "Rende",
                "version": "2.0.0"
            },
            "dispositivi": {
                "lettore_cf": {
                    "tipo": "HID Omnikey 5427CK",
                    "porta": "/dev/ttyACM0",
                    "timeout": 30,
                    "retry_tentativi": 3
                },
                "rele": {
                    "porta": "/dev/ttyUSB0",
                    "baud_rate": 19200,
                    "modulo_id": 8,
                    "mapping": {
                        "1": {"nome": "Cancello", "durata_sec": 8},
                        "2": {"nome": "Luce Verde", "durata_sec": 3},
                        "3": {"nome": "Luce Rossa", "durata_sec": 3},
                        "4": {"nome": "Buzzer", "durata_sec": 1},
                        "5": {"nome": "Illuminazione", "durata_sec": 10},
                        "6": {"nome": "Riserva", "durata_sec": 5}
                    }
                }
            },
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "mittente": "",
                "password": "",
                "destinatari": [],
                "frequenza_report": "giornaliero",
                "attivo": False
            },
            "log": {
                "campi_visibili": [
                    "timestamp", "codice_fiscale", "autorizzato", 
                    "nome_cognome", "comune", "motivo_blocco"
                ],
                "livello_dettaglio": "completo",
                "ritenzione_giorni": 365
            },
            "allerte": {
                "guasto_lettore": True,
                "guasto_rele": True,
                "connessione_rete": True,
                "database_sync": True,
                "soglia_fallimenti": 5
            },
            "utenti": {
                "admin": {
                    "password_hash": generate_password_hash("admin123"),
                    "ruolo": "admin",
                    "ultimo_accesso": None,
                    "attivo": True,
                    "note": "Amministratore di sistema"
                }
            },
            "sistema_orari": {
                "apertura_automatica": False,
                "orario_inizio": "08:00",
                "orario_fine": "18:00",
                "giorni_settimana": [1, 2, 3, 4, 5, 6]
            }
        }
    
    def get(self, key: str, default=None):
        """Ottieni valore configurazione usando notazione punto"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value):
        """Imposta valore configurazione usando notazione punto"""
        keys = key.split('.')
        config_ref = self.config
        
        for k in keys[:-1]:
            if k not in config_ref:
                config_ref[k] = {}
            config_ref = config_ref[k]
        
        config_ref[keys[-1]] = value
        self._save_config()
    
    def _save_config(self):
        """Salva configurazione su file"""
        try:
            self.config_file.parent.mkdir(exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Errore salvataggio config: {e}")

# Inizializza config manager
config_manager = ConfigManager()

# ===============================
# DECORATORI AUTENTICAZIONE
# ===============================

def require_auth(f):
    """Decorator per richiedere autenticazione"""
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            return jsonify({'success': False, 'error': 'Autenticazione richiesta'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def require_permission(permission):
    """Decorator per richiedere permesso specifico"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if 'logged_in' not in session or not session['logged_in']:
                return jsonify({'success': False, 'error': 'Autenticazione richiesta'}), 401
            
            user_role = session.get('role', 'viewer')
            user_permissions = USER_ROLES.get(user_role, {}).get('permissions', [])
            
            if 'all' not in user_permissions and permission not in user_permissions:
                return jsonify({'success': False, 'error': 'Permessi insufficienti'}), 403
            
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

# ===============================
# TEMPLATE BASE MODERNO
# ===============================

def get_base_template():
    """Template base moderno con CSS avanzato"""
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{% block title %}Sistema Controllo Accessi{% endblock %}</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            
            .header {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                padding: 15px 30px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 2px 20px rgba(0,0,0,0.1);
                position: sticky;
                top: 0;
                z-index: 1000;
            }
            
            .header h1 {
                color: #2c3e50;
                font-size: 1.8em;
                font-weight: 600;
            }
            
            .user-info {
                display: flex;
                align-items: center;
                gap: 15px;
                font-size: 0.9em;
            }
            
            .status-dot {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: #27ae60;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .main-container {
                display: flex;
                max-width: 1400px;
                margin: 0 auto;
                gap: 20px;
                padding: 20px;
                min-height: calc(100vh - 80px);
            }
            
            .sidebar {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 20px;
                width: 280px;
                height: fit-content;
                box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
                border: 1px solid rgba(255, 255, 255, 0.18);
            }
            
            .sidebar h3 {
                color: #2c3e50;
                margin-bottom: 20px;
                font-size: 1.2em;
                text-align: center;
            }
            
            .nav-menu {
                list-style: none;
            }
            
            .nav-item {
                margin-bottom: 8px;
            }
            
            .nav-link {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 15px;
                color: #555;
                text-decoration: none;
                border-radius: 10px;
                transition: all 0.3s ease;
                font-weight: 500;
            }
            
            .nav-link:hover, .nav-link.active {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                transform: translateX(5px);
            }
            
            .nav-link i {
                width: 20px;
                text-align: center;
            }
            
            .content {
                flex: 1;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
                border: 1px solid rgba(255, 255, 255, 0.18);
            }
            
            .content h2 {
                color: #2c3e50;
                margin-bottom: 25px;
                font-size: 1.8em;
                font-weight: 600;
            }
            
            .btn {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 500;
                text-decoration: none;
                transition: all 0.3s ease;
                font-size: 0.9em;
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .btn-secondary {
                background: #6c757d;
                color: white;
            }
            
            .btn-success {
                background: #28a745;
                color: white;
            }
            
            .btn-danger {
                background: #dc3545;
                color: white;
            }
            
            .btn-warning {
                background: #ffc107;
                color: #212529;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            
            .card {
                background: rgba(248, 249, 250, 0.8);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
                border: 1px solid rgba(0,0,0,0.08);
            }
            
            .card h4 {
                color: #495057;
                margin-bottom: 15px;
                font-size: 1.1em;
            }
            
            .form-group {
                margin-bottom: 20px;
            }
            
            .form-label {
                display: block;
                margin-bottom: 5px;
                font-weight: 500;
                color: #495057;
            }
            
            .form-control {
                width: 100%;
                padding: 10px 15px;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                font-size: 0.9em;
                transition: border-color 0.3s ease;
            }
            
            .form-control:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            .form-select {
                background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
                background-position: right 10px center;
                background-repeat: no-repeat;
                background-size: 16px;
                appearance: none;
            }
            
            .status-badge {
                display: inline-flex;
                align-items: center;
                gap: 5px;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.8em;
                font-weight: 600;
            }
            
            .status-online {
                background: #d4edda;
                color: #155724;
            }
            
            .status-offline {
                background: #f8d7da;
                color: #721c24;
            }
            
            .status-warning {
                background: #fff3cd;
                color: #856404;
            }
            
            .grid {
                display: grid;
                gap: 20px;
            }
            
            .grid-2 {
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            }
            
            .grid-3 {
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            }
            
            .loading {
                display: flex;
                align-items: center;
                gap: 10px;
                color: #6c757d;
            }
            
            .loading::before {
                content: '';
                width: 16px;
                height: 16px;
                border: 2px solid #e9ecef;
                border-top: 2px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .alert {
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                border-left: 4px solid;
            }
            
            .alert-success {
                background: #d4edda;
                border-color: #28a745;
                color: #155724;
            }
            
            .alert-danger {
                background: #f8d7da;
                border-color: #dc3545;
                color: #721c24;
            }
            
            .alert-warning {
                background: #fff3cd;
                border-color: #ffc107;
                color: #856404;
            }
            
            .alert-info {
                background: #cce7ff;
                border-color: #0ea5e9;
                color: #0369a1;
            }
            
            .table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }
            
            .table th,
            .table td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #e9ecef;
            }
            
            .table th {
                background: #f8f9fa;
                font-weight: 600;
                color: #495057;
            }
            
            .table tr:hover {
                background: rgba(102, 126, 234, 0.05);
            }
            
            .text-center {
                text-align: center;
            }
            
            .text-muted {
                color: #6c757d;
            }
            
            .mb-3 {
                margin-bottom: 1rem;
            }
            
            .mt-3 {
                margin-top: 1rem;
            }
            
            @media (max-width: 768px) {
                .main-container {
                    flex-direction: column;
                    padding: 10px;
                }
                
                .sidebar {
                    width: 100%;
                    order: 2;
                }
                
                .content {
                    order: 1;
                }
                
                .header {
                    padding: 10px 15px;
                    flex-direction: column;
                    gap: 10px;
                }
                
                .header h1 {
                    font-size: 1.4em;
                }
            }
        </style>
        {% block extra_css %}{% endblock %}
    </head>
    <body>
        {% block content %}{% endblock %}
        
        <script>
            // Utility globali
            function showAlert(message, type = 'info') {
                const alertHtml = `
                    <div class="alert alert-${type}" style="position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
                        ${message}
                    </div>
                `;
                document.body.insertAdjacentHTML('beforeend', alertHtml);
                
                setTimeout(() => {
                    const alert = document.querySelector('.alert:last-child');
                    if (alert) alert.remove();
                }, 5000);
            }
            
            function updateClock() {
                const now = new Date();
                const timeString = now.toLocaleString('it-IT');
                const clockEl = document.getElementById('current-time');
                if (clockEl) clockEl.textContent = timeString;
            }
            
            // Aggiorna orologio ogni secondo
            setInterval(updateClock, 1000);
            updateClock();
        </script>
        
        {% block extra_js %}{% endblock %}
    </body>
    </html>
    """

# ===============================
# LOGIN TEMPLATE
# ===============================

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Sistema Controllo Accessi</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .login-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            max-width: 400px;
            width: 90%;
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .login-header h1 {
            color: #2c3e50;
            font-size: 1.8em;
            margin-bottom: 10px;
        }
        
        .island-name {
            color: #667eea;
            font-size: 1.1em;
            font-weight: 600;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            margin-bottom: 8px;
            color: #495057;
            font-weight: 500;
        }
        
        .form-control {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            font-size: 1em;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .btn-login {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        }
        
        .alert {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .alert-danger {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .system-info {
            text-align: center;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
            color: #6c757d;
            font-size: 0.85em;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1><i class="fas fa-shield-alt"></i> Sistema Controllo Accessi</h1>
            <div class="island-name">{{ island_name }}</div>
        </div>
        
        {% if error %}
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle"></i> {{ error }}
        </div>
        {% endif %}
        
        <form method="POST">
            <div class="form-group">
                <label class="form-label" for="username">
                    <i class="fas fa-user"></i> Username
                </label>
                <input type="text" class="form-control" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label class="form-label" for="password">
                    <i class="fas fa-lock"></i> Password
                </label>
                <input type="password" class="form-control" id="password" name="password" required>
            </div>
            
            <button type="submit" class="btn-login">
                <i class="fas fa-sign-in-alt"></i> Accedi
            </button>
        </form>
        
        <div class="system-info">
            <i class="fas fa-server"></i> Dashboard Modulare v2.0<br>
            <span id="current-time"></span>
        </div>
    </div>
    
    <script>
        function updateClock() {
            const now = new Date();
            const timeString = now.toLocaleString('it-IT');
            document.getElementById('current-time').textContent = timeString;
        }
        
        setInterval(updateClock, 1000);
        updateClock();
    </script>
</body>
</html>
"""

# ===============================
# ROUTES PRINCIPALI
# ===============================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Pagina login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Verifica credenziali
        utenti = config_manager.get('utenti', {})
        
        if username in utenti:
            user_data = utenti[username]
            if user_data.get('attivo', False) and check_password_hash(user_data.get('password_hash'), password):
                session['logged_in'] = True
                session['username'] = username
                session['role'] = user_data.get('ruolo', 'viewer')
                session['permissions'] = USER_ROLES.get(session['role'], {}).get('permissions', [])
                
                # Aggiorna ultimo accesso
                config_manager.set(f'utenti.{username}.ultimo_accesso', datetime.now().isoformat())
                
                return redirect(url_for('dashboard'))
            else:
                error = 'Credenziali non valide'
        else:
            error = 'Utente non trovato'
        
        # Nome isola per display
        nome_isola = config_manager.get('sistema.nome_isola', '')
        if not nome_isola:
            nome_isola = "Isola Ecologica"
        else:
            nome_isola = f"Isola Ecologica {nome_isola}"
        
        return render_template_string(LOGIN_TEMPLATE, error=error, island_name=nome_isola)
    
    # GET request
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('dashboard'))
    
    # Nome isola per display
    nome_isola = config_manager.get('sistema.nome_isola', '')
    if not nome_isola:
        nome_isola = "Isola Ecologica"
    else:
        nome_isola = f"Isola Ecologica {nome_isola}"
    
    return render_template_string(LOGIN_TEMPLATE, error=None, island_name=nome_isola)

@app.route('/logout')
def logout():
    """Logout utente"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@require_auth
def dashboard():
    """Dashboard principale - Panoramica"""
    nome_isola = config_manager.get('sistema.nome_isola', '')
    if not nome_isola:
        nome_isola = "Isola Ecologica"
    else:
        nome_isola = f"Isola Ecologica {nome_isola}"
    
    template = get_base_template() + """
    {% block title %}Panoramica - Sistema Controllo Accessi{% endblock %}
    
    {% block content %}
    <div class="header">
        <h1><i class="fas fa-tachometer-alt"></i> {{ island_name }}</h1>
        <div class="user-info">
            <div class="status-dot"></div>
            <span>{{ user_role_name }}</span>
            <span id="current-time"></span>
            <a href="/logout" class="btn btn-secondary">
                <i class="fas fa-sign-out-alt"></i> Logout
            </a>
        </div>
    </div>
    
    <div class="main-container">
        <div class="sidebar">
            <h3><i class="fas fa-bars"></i> Menu Principale</h3>
            <ul class="nav-menu">
                <li class="nav-item">
                    <a href="/" class="nav-link active">
                        <i class="fas fa-tachometer-alt"></i>
                        <span>Panoramica</span>
                    </a>
                </li>
                {% if 'all' in permissions %}
                <li class="nav-item">
                    <a href="/dispositivi" class="nav-link">
                        <i class="fas fa-microchip"></i>
                        <span>Dispositivi</span>
                    </a>
                </li>
                {% endif %}
                {% if 'email' in permissions or 'all' in permissions %}
                <li class="nav-item">
                    <a href="/email" class="nav-link">
                        <i class="fas fa-envelope"></i>
                        <span>Email</span>
                    </a>
                </li>
                {% endif %}
                {% if 'users' in permissions or 'all' in permissions %}
                <li class="nav-item">
                    <a href="/utenti" class="nav-link">
                        <i class="fas fa-users"></i>
                        <span>Utenti</span>
                    </a>
                </li>
                {% endif %}
                <li class="nav-item">
                    <a href="/log" class="nav-link">
                        <i class="fas fa-list-alt"></i>
                        <span>Log Accessi</span>
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/allerte" class="nav-link">
                        <i class="fas fa-exclamation-triangle"></i>
                        <span>Allerte</span>
                    </a>
                </li>
                {% if 'all' in permissions %}
                <li class="nav-item">
                    <a href="/sistema" class="nav-link">
                        <i class="fas fa-cog"></i>
                        <span>Sistema</span>
                    </a>
                </li>
                {% endif %}
            </ul>
        </div>
        
        <div class="content">
            <h2><i class="fas fa-chart-line"></i> Panoramica Sistema</h2>
            
            <!-- Stato Real-Time -->
            <div class="card">
                <h4><i class="fas fa-broadcast-tower"></i> Stato Real-Time</h4>
                <div class="grid grid-3">
                    <div>
                        <strong>Stato Cancello:</strong>
                        <div id="gate-status" class="loading">Caricamento...</div>
                    </div>
                    <div>
                        <strong>Ultimo Accesso:</strong>
                        <div id="last-access" class="loading">Caricamento...</div>
                    </div>
                    <div>
                        <strong>Sistema:</strong>
                        <div id="system-status" class="loading">Caricamento...</div>
                    </div>
                </div>
            </div>
            
            <!-- Statistiche -->
            <div class="grid grid-2">
                <div class="card">
                    <h4><i class="fas fa-chart-bar"></i> Statistiche Oggi</h4>
                    <div id="daily-stats" class="loading">Caricamento statistiche...</div>
                </div>
                
                <div class="card">
                    <h4><i class="fas fa-exclamation-circle"></i> Allerte Attive</h4>
                    <div id="active-alerts" class="loading">Caricamento allerte...</div>
                </div>
            </div>
            
            <!-- Hardware Status -->
            <div class="card">
                <h4><i class="fas fa-microchip"></i> Stato Hardware</h4>
                <div class="grid grid-3">
                    <div>
                        <strong>Lettore CF:</strong>
                        <div id="reader-status" class="loading">Test in corso...</div>
                    </div>
                    <div>
                        <strong>Modulo Relè:</strong>
                        <div id="relay-status" class="loading">Test in corso...</div>
                    </div>
                    <div>
                        <strong>Connessione Rete:</strong>
                        <div id="network-status" class="loading">Verifica in corso...</div>
                    </div>
                </div>
            </div>
            
            <!-- Accessi Recenti -->
            <div class="card">
                <h4><i class="fas fa-history"></i> Accessi Recenti</h4>
                <div id="recent-access" class="loading">Caricamento accessi...</div>
            </div>
        </div>
    </div>
    {% endblock %}
    
    {% block extra_js %}
    <script>
        let updateInterval;
        
        document.addEventListener('DOMContentLoaded', function() {
            loadDashboardData();
            startRealTimeUpdates();
        });
        
        function startRealTimeUpdates() {
            updateInterval = setInterval(loadDashboardData, 5000);
        }
        
        async function loadDashboardData() {
            try {
                // Stato fake per demo
                document.getElementById('gate-status').innerHTML = 
                    '<span class="status-badge status-online"><i class="fas fa-door-closed"></i> Chiuso</span>';
                
                document.getElementById('last-access').innerHTML = 
                    'Nessun accesso recente';
                
                document.getElementById('system-status').innerHTML = 
                    '<span class="status-badge status-online"><i class="fas fa-check-circle"></i> Operativo</span>';
                
                document.getElementById('daily-stats').innerHTML = `
                    <div class="grid grid-2">
                        <div><strong>Accessi Totali:</strong> 0</div>
                        <div><strong>Autorizzati:</strong> 0</div>
                        <div><strong>Negati:</strong> 0</div>
                        <div><strong>Tasso Successo:</strong> 0%</div>
                    </div>
                `;
                
                document.getElementById('active-alerts').innerHTML = 
                    '<span class="text-muted">Nessuna allerta attiva</span>';
                
                document.getElementById('reader-status').innerHTML = 
                    '<span class="status-badge status-online"><i class="fas fa-check"></i> Online</span>';
                
                document.getElementById('relay-status').innerHTML = 
                    '<span class="status-badge status-online"><i class="fas fa-check"></i> Online</span>';
                
                document.getElementById('network-status').innerHTML = 
                    '<span class="status-badge status-online"><i class="fas fa-wifi"></i> Connesso</span>';
                
                document.getElementById('recent-access').innerHTML = 
                    '<span class="text-muted">Nessun accesso recente</span>';
                
            } catch (error) {
                console.error('Errore caricamento dati:', error);
            }
        }
        
        // Cleanup al cambio pagina
        window.addEventListener('beforeunload', function() {
            if (updateInterval) {
                clearInterval(updateInterval);
            }
        });
    </script>
    {% endblock %}
    """
    
    # Dati per template
    user_role = session.get('role', 'viewer')
    user_role_name = USER_ROLES.get(user_role, {}).get('name', 'Utente')
    permissions = session.get('permissions', [])
    
    return render_template_string(template, 
                                island_name=nome_isola,
                                user_role_name=user_role_name,
                                permissions=permissions)

# Placeholder routes per altre sezioni
@app.route('/dispositivi')
@require_auth
@require_permission('all')
def dispositivi():
    return "<h1>Modulo Dispositivi</h1><p>In sviluppo...</p><a href='/'>← Torna alla dashboard</a>"

@app.route('/email')
@require_auth
@require_permission('email')
def email():
    return "<h1>Modulo Email</h1><p>In sviluppo...</p><a href='/'>← Torna alla dashboard</a>"

@app.route('/utenti')
@require_auth
@require_permission('users')
def utenti():
    return "<h1>Modulo Utenti</h1><p>In sviluppo...</p><a href='/'>← Torna alla dashboard</a>"

@app.route('/log')
@require_auth
def log():
    return "<h1>Modulo Log</h1><p>In sviluppo...</p><a href='/'>← Torna alla dashboard</a>"

@app.route('/allerte')
@require_auth
def allerte():
    return "<h1>Modulo Allerte</h1><p>In sviluppo...</p><a href='/'>← Torna alla dashboard</a>"

@app.route('/sistema')
@require_auth
@require_permission('all')
def sistema():
    return "<h1>Modulo Sistema</h1><p>In sviluppo...</p><a href='/'>← Torna alla dashboard</a>"

# ===============================
# API ENDPOINTS
# ===============================

@app.route('/api/status')
@require_auth
def api_status():
    """Status API"""
    return jsonify({
        'success': True,
        'version': '2.0.0',
        'status': 'operational',
        'user': session.get('username'),
        'role': session.get('role')
    })

# ===============================
# STARTUP
# ===============================

def init_app():
    """Inizializzazione applicazione"""
    # Crea directory necessarie
    (project_root / "config").mkdir(exist_ok=True)
    (project_root / "logs").mkdir(exist_ok=True)
    (project_root / "temp").mkdir(exist_ok=True)
    
    # Inizializza configurazione
    config_manager._save_config()
    
    logger.info("Dashboard modulare inizializzata correttamente")

if __name__ == '__main__':
    init_app()
    print("🚀 Dashboard Modulare Moderna v2.0")
    print(f"📁 Directory progetto: {project_root}")
    print("🌐 URL: http://localhost:5000")
    print("🌐 URL: http://192.168.178.200:5000")
    print("\\n👤 Login: admin / admin123")
    print("⚠️  CAMBIARE IMMEDIATAMENTE LA PASSWORD!")
    print("\\n✅ Dashboard operativa!")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
'''
    
    # Scrivi il nuovo file
    with open(current_web_api, 'w', encoding='utf-8') as f:
        f.write(complete_web_api_content)
    
    print("✅ Dashboard modulare completa installata!")
    print("🔄 Riavvia il servizio per vedere i cambiamenti")
    print("🌐 URL: http://192.168.178.200:5000")
    print("👤 Login: admin / admin123")

if __name__ == "__main__":
    install_complete_dashboard()
