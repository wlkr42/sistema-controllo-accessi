# File: /opt/access_control/src/api/modules/sync_module_db.py
# Modulo gestione sincronizzazione server remoto - Versione Database

import json
import logging
import threading
import time
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template_string
from pathlib import Path
import sys
import os

# Add external module path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../external'))

from functools import wraps
from api.utils import get_db_connection

logger = logging.getLogger(__name__)

# Blueprint
sync_bp = Blueprint('sync', __name__)

# Global variables
odoo_connector = None
sync_thread = None
sync_running = False
sync_logs = []
MAX_LOGS = 1000

def require_auth():
    """Decorator per autenticazione"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simplified auth check - in production use proper session management
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def add_log(level, message):
    """Add log entry to sync logs"""
    global sync_logs
    entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'level': level,
        'message': message
    }
    sync_logs.append(entry)
    # Keep only last MAX_LOGS entries
    if len(sync_logs) > MAX_LOGS:
        sync_logs = sync_logs[-MAX_LOGS:]
    
    # Also log to system logger
    if level == 'ERROR':
        logger.error(message)
    elif level == 'WARNING':
        logger.warning(message)
    else:
        logger.info(message)

def load_config():
    """Load sync configuration from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all sync settings from database
        cursor.execute("""
            SELECT key, value FROM system_settings 
            WHERE key LIKE 'sync.%'
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        # Default configuration
        config = {
            'url': 'https://app.calabramaceri.it',
            'database': 'cmapp',
            'username': 'controllo-accessi@calabramaceri.it',
            'password': 'AcC3ss0C0ntr0l!2025#Rnd',
            'comune': 'Rende',
            'sync_enabled': False,
            'sync_interval_hours': 12
        }
        
        # Update with values from database
        for row in rows:
            key = row['key'].replace('sync.', '')
            value = row['value']
            
            # Convert boolean strings
            if value == 'true':
                value = True
            elif value == 'false':
                value = False
            # Convert numeric strings
            elif key == 'sync_interval_hours':
                try:
                    value = int(value)
                except:
                    value = 12
            
            config[key] = value
        
        return config
        
    except Exception as e:
        add_log('ERROR', f'Errore caricamento configurazione da DB: {e}')
        # Fallback to default
        return {
            'url': 'https://app.calabramaceri.it',
            'database': 'cmapp',
            'username': 'controllo-accessi@calabramaceri.it',
            'password': 'AcC3ss0C0ntr0l!2025#Rnd',
            'comune': 'Rende',
            'sync_enabled': False,
            'sync_interval_hours': 12
        }

def save_config(config):
    """Save sync configuration to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Save each config item to database
        for key, value in config.items():
            # Skip internal fields that shouldn't be saved
            if key in ['last_sync']:
                continue
                
            # Convert value to string
            if isinstance(value, bool):
                value_str = 'true' if value else 'false'
            else:
                value_str = str(value)
            
            # Insert or update in database
            cursor.execute("""
                INSERT OR REPLACE INTO system_settings (key, value, updated_at)
                VALUES (?, ?, datetime('now'))
            """, (f'sync.{key}', value_str))
        
        # Save last_sync separately if present
        if 'last_sync' in config:
            cursor.execute("""
                INSERT OR REPLACE INTO system_settings (key, value, updated_at)
                VALUES ('sync.last_sync', ?, datetime('now'))
            """, (config['last_sync'],))
        
        conn.commit()
        conn.close()
        
        add_log('INFO', 'Configurazione salvata nel database')
        return True
        
    except Exception as e:
        add_log('ERROR', f'Errore salvataggio configurazione in DB: {e}')
        return False

def get_odoo_connector():
    """Get or create Odoo connector instance"""
    global odoo_connector
    
    if odoo_connector is None:
        try:
            from odoo_partner_connector import OdooPartnerConnector
            
            # Mock config manager for compatibility
            class MockConfigManager:
                def get_config(self):
                    return {'version': '1.0'}
            
            config_manager = MockConfigManager()
            odoo_connector = OdooPartnerConnector(config_manager)
            
            # Configure with saved settings
            config = load_config()
            odoo_connector.configure_connection(
                url=config['url'],
                database=config['database'],
                username=config['username'],
                password=config['password'],
                comune=config['comune'],
                sync_interval=config['sync_interval_hours'] * 3600
            )
        except Exception as e:
            add_log('ERROR', f'Errore inizializzazione connector: {e}')
            return None
    
    return odoo_connector

def sync_worker():
    """Worker thread for automatic sync"""
    global sync_running
    
    while sync_running:
        try:
            config = load_config()
            if config.get('sync_enabled', False):
                interval_hours = config.get('sync_interval_hours', 12)
                add_log('INFO', f'Prossima sincronizzazione in {interval_hours} ore')
                
                # Sleep in small chunks to allow thread interruption
                for _ in range(interval_hours * 60):  # Check every minute
                    if not sync_running:
                        break
                    time.sleep(60)
                
                if sync_running:
                    add_log('INFO', 'Avvio sincronizzazione automatica...')
                    perform_sync()
        except Exception as e:
            add_log('ERROR', f'Errore sync worker: {e}')
            time.sleep(3600)  # Wait 1 hour on error

def perform_sync():
    """Perform actual sync operation"""
    try:
        connector = get_odoo_connector()
        if not connector:
            add_log('ERROR', 'Connector non disponibile')
            return False, 'Connector non disponibile'
        
        add_log('INFO', 'Connessione al server...')
        config = load_config()
        add_log('DEBUG', f"Tentativo connessione a: {config.get('url', 'N/A')} - Database: {config.get('database', 'N/A')}")
        
        if not connector.connect():
            add_log('ERROR', f"Impossibile connettersi al server {config.get('url', 'N/A')}")
            add_log('DEBUG', f"Verifica credenziali: Username={config.get('username', 'N/A')}")
            return False, f"Impossibile connettersi al server {config.get('url', 'N/A')}"
        
        add_log('INFO', 'Recupero cittadini autorizzati...')
        
        # Get database connection
        conn = get_db_connection()
        
        # Create mock database manager
        class MockDatabaseManager:
            def __init__(self, connection):
                self.conn = connection
            
            def user_exists(self, cf):
                cursor = self.conn.execute(
                    "SELECT 1 FROM utenti_autorizzati WHERE codice_fiscale = ?",
                    (cf,)
                )
                return cursor.fetchone() is not None
            
            def add_user(self, codice_fiscale, nome, note, created_by):
                try:
                    self.conn.execute(
                        """INSERT INTO utenti_autorizzati 
                           (codice_fiscale, nome, attivo, note, creato_da, data_inserimento)
                           VALUES (?, ?, 1, ?, ?, datetime('now'))""",
                        (codice_fiscale, nome, note, created_by)
                    )
                    self.conn.commit()
                    return True
                except Exception as e:
                    add_log('ERROR', f'Errore inserimento utente {codice_fiscale}: {e}')
                    add_log('DEBUG', f'Dettagli errore SQL: {str(e)}')
                    return False
        
        db_manager = MockDatabaseManager(conn)
        
        # Perform sync
        success, stats = connector.sync_to_database(db_manager)
        
        conn.close()
        
        if success:
            # Log dettagliato dei risultati
            add_log('SUCCESS', f"Sincronizzazione completata: {stats['added']} aggiunti, {stats['skipped']} esistenti")
            
            if stats.get('errors', 0) > 0:
                add_log('WARNING', f"Ci sono stati {stats['errors']} errori durante la sincronizzazione")
                add_log('INFO', f"Totale cittadini recuperati: {stats.get('fetched', 0)}")
                add_log('INFO', f"Cittadini aggiunti con successo: {stats.get('added', 0)}")
                add_log('INFO', f"Cittadini già esistenti: {stats.get('skipped', 0)}")
                add_log('INFO', f"Cittadini con errori: {stats.get('errors', 0)}")
            
            # Update last sync time in database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO system_settings (key, value, updated_at)
                VALUES ('sync.last_sync', ?, datetime('now'))
            """, (datetime.now().isoformat(),))
            conn.commit()
            conn.close()
            
            return True, f"Sincronizzati {stats['fetched']} cittadini ({stats['added']} nuovi, {stats['skipped']} esistenti, {stats.get('errors', 0)} errori)"
        else:
            add_log('ERROR', f'Sincronizzazione fallita - Stats: {stats}')
            return False, f"Sincronizzazione fallita - Recuperati: {stats.get('fetched', 0)}, Errori: {stats.get('errors', 0)}"
            
    except Exception as e:
        add_log('ERROR', f'Errore durante sincronizzazione: {e}')
        return False, str(e)

# API Routes

@sync_bp.route('/config', methods=['GET', 'POST'])
@require_auth()
def api_sync_config():
    """Get or update sync configuration"""
    if request.method == 'GET':
        config = load_config()
        # Return full config including password (needed for form)
        return jsonify({'success': True, 'config': config})
    
    else:  # POST
        try:
            data = request.json
            config = load_config()
            
            # Update configuration
            if 'url' in data:
                config['url'] = data['url']
            if 'database' in data:
                config['database'] = data['database']
            if 'username' in data:
                config['username'] = data['username']
            if 'password' in data:
                config['password'] = data['password']
            if 'comune' in data:
                config['comune'] = data['comune']
            
            # Save configuration to database
            if save_config(config):
                # Reconfigure connector
                connector = get_odoo_connector()
                if connector:
                    connector.configure_connection(
                        url=config['url'],
                        database=config['database'],
                        username=config['username'],
                        password=config['password'],
                        comune=config['comune'],
                        sync_interval=config.get('sync_interval_hours', 12) * 3600
                    )
                
                add_log('INFO', 'Configurazione server aggiornata e salvata nel database')
                return jsonify({'success': True, 'message': 'Configurazione salvata nel database'})
            else:
                return jsonify({'success': False, 'error': 'Errore salvataggio configurazione nel database'})
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

@sync_bp.route('/schedule', methods=['POST'])
@require_auth()
def api_sync_schedule():
    """Update sync schedule"""
    global sync_thread, sync_running
    
    try:
        data = request.json
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if 'sync_enabled' in data:
            cursor.execute("""
                INSERT OR REPLACE INTO system_settings (key, value, updated_at)
                VALUES ('sync.sync_enabled', ?, datetime('now'))
            """, ('true' if data['sync_enabled'] else 'false',))
        
        if 'sync_interval_hours' in data:
            cursor.execute("""
                INSERT OR REPLACE INTO system_settings (key, value, updated_at)
                VALUES ('sync.sync_interval_hours', ?, datetime('now'))
            """, (str(data['sync_interval_hours']),))
        
        conn.commit()
        conn.close()
        
        # Restart sync thread if needed
        config = load_config()
        if config['sync_enabled']:
            if not sync_running:
                sync_running = True
                sync_thread = threading.Thread(target=sync_worker, daemon=True)
                sync_thread.start()
                add_log('INFO', 'Sincronizzazione automatica avviata')
        else:
            sync_running = False
            add_log('INFO', 'Sincronizzazione automatica disabilitata')
        
        return jsonify({'success': True, 'message': 'Schedulazione aggiornata nel database'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@sync_bp.route('/test', methods=['POST'])
@require_auth()
def api_sync_test():
    """Test server connection"""
    try:
        data = request.json
        
        # Create temporary connector for testing
        from odoo_partner_connector import OdooPartnerConnector
        
        class MockConfigManager:
            def get_config(self):
                return {'version': '1.0'}
        
        test_connector = OdooPartnerConnector(MockConfigManager())
        test_connector.configure_connection(
            url=data['url'],
            database=data['database'],
            username=data['username'],
            password=data['password'],
            comune=data.get('comune', 'Rende')
        )
        
        success, message = test_connector.test_connection()
        
        if success:
            add_log('SUCCESS', f'Test connessione riuscito: {message}')
        else:
            add_log('ERROR', f'Test connessione fallito: {message}')
        
        return jsonify({'success': success, 'message': message})
        
    except Exception as e:
        add_log('ERROR', f'Errore test connessione: {e}')
        return jsonify({'success': False, 'error': str(e)})

@sync_bp.route('/manual', methods=['POST'])
@require_auth()
def api_sync_manual():
    """Perform manual sync"""
    try:
        add_log('INFO', 'Avvio sincronizzazione manuale...')
        success, message = perform_sync()
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@sync_bp.route('/status', methods=['GET'])
@require_auth()
def api_sync_status():
    """Get sync status"""
    try:
        connector = get_odoo_connector()
        config = load_config()
        
        status = {
            'connected': False,
            'last_sync': config.get('last_sync', None),
            'sync_enabled': config.get('sync_enabled', False),
            'sync_interval_hours': config.get('sync_interval_hours', 12)
        }
        
        # Consider connected if there was a successful sync in the last 24 hours
        if status['last_sync']:
            try:
                from datetime import datetime, timedelta
                last_sync_time = datetime.fromisoformat(status['last_sync'].replace('Z', '+00:00'))
                time_since_sync = datetime.now(last_sync_time.tzinfo) - last_sync_time
                # Connected if synced in last 24 hours
                status['connected'] = time_since_sync < timedelta(hours=24)
            except:
                pass
        
        if connector:
            conn_status = connector.get_sync_status()
            # Use connector status if available and no recent sync
            if not status['connected']:
                status['connected'] = conn_status.get('connected', False)
            if conn_status.get('last_sync'):
                status['last_sync'] = conn_status['last_sync']
        
        return jsonify({'success': True, 'status': status})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@sync_bp.route('/logs', methods=['GET'])
@require_auth()
def api_sync_logs():
    """Get sync logs"""
    try:
        # Get last 100 logs
        recent_logs = sync_logs[-100:] if len(sync_logs) > 100 else sync_logs
        return jsonify({'success': True, 'logs': recent_logs})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Initialize on module load
def initialize_sync_module():
    """Initialize sync module on startup"""
    global sync_thread, sync_running
    
    config = load_config()
    if config.get('sync_enabled', False):
        sync_running = True
        sync_thread = threading.Thread(target=sync_worker, daemon=True)
        sync_thread.start()
        add_log('INFO', 'Modulo sincronizzazione inizializzato con database')

# Auto-initialize
initialize_sync_module()