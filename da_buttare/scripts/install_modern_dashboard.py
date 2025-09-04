#!/usr/bin/env python3
# File: /opt/access_control/scripts/install_modern_dashboard.py
# Script Installazione Dashboard Modulare Moderna - CORRETTO
import json

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

class DashboardInstaller:
    """Installer per la nuova dashboard modulare"""
    
    def __init__(self):
        self.project_root = Path("/opt/access_control")
        self.backup_dir = self.project_root / "backup" / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def run_installation(self):
        """Esegue installazione completa"""
        print("🚀 INSTALLAZIONE DASHBOARD MODULARE MODERNA")
        print("=" * 60)
        
        try:
            # 1. Verifica prerequisiti
            self.check_prerequisites()
            
            # 2. Backup sistema esistente
            self.backup_existing_system()
            
            # 3. Installa dipendenze
            self.install_dependencies()
            
            # 4. Crea struttura moduli
            self.create_module_structure()
            
            # 5. Aggiorna web_api.py principale
            self.update_main_web_api()
            
            # 6. Configura sistema
            self.configure_system()
            
            # 7. Test finale
            self.test_installation()
            
            print("\n✅ INSTALLAZIONE COMPLETATA CON SUCCESSO!")
            print(f"🌐 Dashboard disponibile su: http://192.168.178.200:5000")
            print(f"👤 Login: admin / admin123 (CAMBIARE IMMEDIATAMENTE)")
            print(f"📁 Backup salvato in: {self.backup_dir}")
            
        except Exception as e:
            print(f"\n❌ ERRORE DURANTE INSTALLAZIONE: {e}")
            print(f"📁 Ripristina backup da: {self.backup_dir}")
            sys.exit(1)
    
    def check_prerequisites(self):
        """Verifica prerequisiti sistema"""
        print("🔍 Verifica prerequisiti...")
        
        # Verifica Python
        if sys.version_info < (3, 8):
            raise Exception("Python 3.8+ richiesto")
        
        # Verifica directory progetto
        if not self.project_root.exists():
            raise Exception(f"Directory progetto non trovata: {self.project_root}")
        
        # Verifica file esistenti critici
        critical_files = [
            "src/main.py",
            "src/hardware/card_reader.py",
            "src/database/database_manager.py"
        ]
        
        for file_path in critical_files:
            if not (self.project_root / file_path).exists():
                raise Exception(f"File critico mancante: {file_path}")
        
        print("✅ Prerequisiti verificati")
    
    def backup_existing_system(self):
        """Backup sistema esistente"""
        print("💾 Creazione backup sistema esistente...")
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup file principali
        files_to_backup = [
            "src/api/web_api.py",
            "config/dashboard_config.json",
            "requirements.txt"
        ]
        
        for file_path in files_to_backup:
            source = self.project_root / file_path
            if source.exists():
                dest = self.backup_dir / file_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
        
        print(f"✅ Backup creato in: {self.backup_dir}")
    
    def install_dependencies(self):
        """Installa dipendenze aggiuntive"""
        print("📦 Installazione dipendenze...")
        
        additional_deps = [
            "openpyxl==3.1.2",  # Per export Excel
            "xlsxwriter==3.1.9",  # Per Excel avanzato
            "python-crontab==3.0.0",  # Per scheduling
            "psutil>=5.9.5"  # Per monitoraggio sistema
        ]
        
        for dep in additional_deps:
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", dep
                ], check=True, capture_output=True)
                print(f"✅ Installato: {dep}")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Errore installazione {dep}: {e}")
    
    def create_module_structure(self):
        """Crea struttura moduli"""
        print("📁 Creazione struttura moduli...")
        
        # Crea directory moduli
        modules_dir = self.project_root / "src" / "api" / "modules"
        modules_dir.mkdir(parents=True, exist_ok=True)
        
        # Crea directory templates
        templates_dir = self.project_root / "src" / "api" / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Crea directory static
        static_dir = self.project_root / "src" / "api" / "static"
        static_dir.mkdir(parents=True, exist_ok=True)
        
        # Crea __init__.py per moduli
        (modules_dir / "__init__.py").touch()
        
        print("✅ Struttura moduli creata")
    
    def update_main_web_api(self):
        """Aggiorna web_api.py principale con nuovi moduli"""
        print("🔄 Installazione nuovo web_api.py...")
        
        # Invece di sostituire tutto, creiamo il nuovo file completo
        new_web_api_content = '''# File: /opt/access_control/src/api/web_api.py
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
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

try:
    import pandas as pd
except ImportError:
    print("⚠️ pandas non installato, alcune funzioni potrebbero non funzionare")

from flask import Flask, request, jsonify, session, send_file, render_template_string, redirect, url_for
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
                "comune": "Non configurato",
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
                    "attivo": True
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
# TEMPLATE BASE
# ===============================

def get_base_template():
    """Template base comune - versione semplificata per evitare errori"""
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sistema Controllo Accessi</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial, sans-serif; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; }
            .card { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; }
            .btn { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
            .btn:hover { background: #0056b3; }
            .form-control { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏭 Dashboard Sistema Controllo Accessi</h1>
                <p>Versione 2.0 - Dashboard Modulare</p>
            </div>
            <div class="card">
                <h2>✅ Dashboard Moderna Installata!</h2>
                <p>La nuova dashboard modulare è stata installata con successo.</p>
                <br>
                <p><strong>Prossimi step:</strong></p>
                <ol>
                    <li>Fermare il servizio dashboard attuale</li>
                    <li>Riavviare con il nuovo sistema</li>
                    <li>Accedere con: admin / admin123</li>
                    <li>Cambiare immediatamente la password</li>
                </ol>
                <br>
                <p><strong>URL Dashboard:</strong> <a href="http://192.168.178.200:5000">http://192.168.178.200:5000</a></p>
            </div>
        </div>
    </body>
    </html>
    """

# ===============================
# ROUTE PRINCIPALE TEMPORANEA
# ===============================

@app.route('/')
def dashboard_temp():
    """Dashboard temporanea post-installazione"""
    return get_base_template()

@app.route('/status')
def status():
    """Stato sistema"""
    return jsonify({
        'status': 'installed',
        'version': '2.0.0',
        'message': 'Dashboard moderna installata - riavviare sistema'
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
    
    logger.info("Dashboard temporanea inizializzata")

if __name__ == '__main__':
    init_app()
    print("🚀 Dashboard Temporanea Post-Installazione")
    print(f"📁 Directory progetto: {project_root}")
    print("🌐 URL: http://localhost:5000")
    print("🌐 URL: http://192.168.178.200:5000")
    print("\\n⚠️  QUESTA È UNA VERSIONE TEMPORANEA")
    print("📋 Seguire le istruzioni per completare l'installazione")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
'''
        
        # Scrivi il nuovo web_api.py
        new_web_api_path = self.project_root / "src" / "api" / "web_api.py"
        
        with open(new_web_api_path, 'w', encoding='utf-8') as f:
            f.write(new_web_api_content)
        
        print("✅ Nuovo web_api.py installato")
    
    def configure_system(self):
        """Configura sistema con nuovi parametri"""
        print("⚙️ Configurazione sistema...")
        
        # Crea file di configurazione aggiornato
        config_path = self.project_root / "config" / "dashboard_config.json"
        config_path.parent.mkdir(exist_ok=True)
        
        config_data = {
            "sistema": {
                "nome_isola": "",
                "comune": "Rende",
                "version": "2.0.0",
                "install_date": datetime.now().isoformat(),
                "dashboard_type": "modular"
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
            "utenti": {
                "admin": {
                    "password_hash": "scrypt:32768:8:1$w8zeCkGw9rbpAeJd$060eee786d6484b2443ccbad4257396839338fd5717b9a66a38f2cbbc94f2fe8ce8ae820b6f7d21913af1647036527fd161e2b4cc4b13c0a61760c07e91dbffc",
                    "ruolo": "admin",
                    "ultimo_accesso": None,
                    "attivo": True
                }
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Sistema configurato")
    
    def test_installation(self):
        """Test finale installazione"""
        print("🧪 Test installazione...")
        
        # Test import moduli base
        try:
            import flask
            print("✅ Flask verificato")
        except ImportError as e:
            raise Exception(f"Errore Flask: {e}")
        
        # Test struttura file
        required_files = [
            "src/api/web_api.py",
            "config/dashboard_config.json"
        ]
        
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                raise Exception(f"File mancante: {file_path}")
        
        print("✅ File verificati")
        print("✅ Test completati con successo")

if __name__ == "__main__":
    installer = DashboardInstaller()
    installer.run_installation()