# File: /opt/access_control/src/api/web_api.py
# Dashboard web modulare - API principale - FIXED IMPORTS

import os
import sys
import json
import sqlite3
import logging
import shutil
import subprocess
import psutil
import threading
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List, Union, Callable

from flask import Flask, render_template_string, request, jsonify, session, redirect, send_from_directory, Response, Blueprint, current_app
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, InternalServerError
from werkzeug.wrappers import Response as WerkzeugResponse
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.local import LocalProxy

# Assicurati che il path sia corretto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configura il fuso orario per l'applicazione
import pytz
import time
os.environ['TZ'] = 'Europe/Rome'
try:
    time.tzset()  # Disponibile solo su Unix
except AttributeError:
    pass  # Su Windows non è disponibile

# Importazioni locali
from api.auth import verify_user, USER_ROLES
from api.utils import get_db_connection, require_auth, require_permission
import api.hardware_tests as hardware_tests
import api.backup_module as backup_module
import api.hardware_detection as hardware_detection
from core.config import get_config_manager
from api.dashboard_templates import LOGIN_TEMPLATE, get_dashboard_template, ADMIN_CONFIG_TEMPLATE, ADMIN_BACKUP_TEMPLATE

# Importazioni hardware
from hardware.reader_factory import ReaderFactory
from hardware.usb_rly08_controller import USBRLY08Controller
from external.odoo_partner_connector import OdooPartnerConnector

# Importazioni dei moduli
from api.modules.profilo import profilo_bp
from api.modules.user_management import user_management_bp
from api.modules.log_management import log_management_bp
from api.modules.utenti_autorizzati import utenti_autorizzati_bp
from api.modules.system_users import system_users_bp
from api.modules.activities import activities_bp
from api.modules.configurazione_accessi import configurazione_accessi_bp, verifica_orario, verifica_limite_mensile
from api.backup_module import backup_bp

# Definizione dei tipi personalizzati
FlaskResponse = Union[Response, str, Tuple[Union[Dict[str, Any], str], int]]
Request = Union[ImmutableMultiDict[str, str], Dict[str, Any]]

# Configurazione del logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Queste importazioni sono già state definite sopra e non sono necessarie qui

# Questi import sono già stati definiti sopra e non sono necessari qui

from typing import Optional

# Definizione dei tipi personalizzati
FlaskResponse = Union[Response, str, Tuple[Union[Dict[str, Any], str], int]]
Request = Union[ImmutableMultiDict[str, str], Dict[str, Any]]

# Gestione delle eccezioni
def handle_exception(e: Exception) -> Tuple[Dict[str, Any], int]:
    logger.error(f"Errore: {str(e)}", exc_info=True)
    if isinstance(e, BadRequest):
        return jsonify({"success": False, "error": "Richiesta non valida"}), 400
    elif isinstance(e, InternalServerError):
        return jsonify({"success": False, "error": "Errore interno del server"}), 500
    else:
        return jsonify({"success": False, "error": str(e)}), 500

# Definizione dei tipi per le funzioni di Flask
def flask_route(rule: str, **options: Any) -> Callable[[Callable[..., FlaskResponse]], Callable[..., FlaskResponse]]:
    return app.route(rule, **options)

def flask_jsonify(*args: Any, **kwargs: Any) -> WerkzeugResponse:
    return jsonify(*args, **kwargs)

# Tipo per le funzioni di route
RouteFunction = Callable[..., FlaskResponse]

app = Flask(__name__)
app.secret_key = 'raee-2025-access-control-system'

# Configura CORS per permettere richieste cross-origin con credenziali
CORS(app, 
     supports_credentials=True,
     resources={r"/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization"],
     expose_headers=["Content-Type", "X-CSRFToken"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Configura sessione per funzionare cross-origin
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Impostare a True se si usa HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Database path persistente
DB_PATH = '/opt/access_control/src/access.db'

# IMPORTA I MODULI DOPO aver definito le funzioni condivise
from api.modules.profilo import profilo_bp
from api.modules.user_management import user_management_bp
from api.modules.log_management import log_management_bp
from api.modules.utenti_autorizzati import utenti_autorizzati_bp
from api.modules.system_users import system_users_bp
from api.modules.activities import activities_bp
from api.modules.configurazione_accessi import configurazione_accessi_bp

# Route di test per visualizzare tutte le routes
@app.route('/api/routes')
def list_routes():
    """Lista tutte le routes registrate"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': sorted(list(rule.methods)),
            'path': str(rule)
        })
    return jsonify({
        'success': True,
        'routes': sorted(routes, key=lambda x: x['path'])
    })

# Registra i blueprint
app.register_blueprint(profilo_bp)
app.register_blueprint(user_management_bp)
app.register_blueprint(log_management_bp)
app.register_blueprint(utenti_autorizzati_bp)
app.register_blueprint(system_users_bp)
app.register_blueprint(activities_bp)
app.register_blueprint(configurazione_accessi_bp)
app.register_blueprint(backup_bp)

# ===============================
# ROUTES PRINCIPALI
# ===============================

@flask_route('/')
@require_auth()
def dashboard() -> FlaskResponse:
    """Dashboard principale con template personalizzato per ruolo"""
    # Menu items per admin
    menu_items: List[Dict[str, str]] = []
    if session.get('role') == 'admin':
        menu_items = [
            {
                'url': '/utenti-autorizzati',
                'icon': 'fas fa-users',
                'text': 'Utenti Autorizzati'
            },
            {
                'url': '/admin/users',
                'icon': 'fas fa-users-cog',
                'text': 'Gestione Utenti Sistema'
            },
            {
                'url': '/configurazione-orari',
                'icon': 'fas fa-clock',
                'text': 'Configurazione Orari'
            },
            {
                'url': '/test-accessi',
                'icon': 'fas fa-door-open',
                'text': 'Test Accessi'
            }
        ]
    
    return render_template_string(
        get_dashboard_template(), 
        session=session,
        menu_items=menu_items
    )

@app.route('/utenti-autorizzati')
@require_auth()
@require_permission('all')
def utenti_autorizzati_page() -> FlaskResponse:
    """Pagina gestione utenti autorizzati"""
    with open(os.path.join(os.path.dirname(__file__), 'templates', 'utenti_autorizzati.html'), 'r') as f:
        template = f.read()
    return render_template_string(template, session=session)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        logger.debug(f"Tentativo di login per l'utente: {username}")
        
        if not username or not password:
            logger.debug("Username o password mancanti")
            return render_template_string(LOGIN_TEMPLATE, error="Inserire username e password")
        
        # Verifica credenziali nel database
        success, role = verify_user(username, password)
        
        logger.debug(f"Risultato verifica utente: success={success}, role={role}")
        
        if success:
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    # Aggiorna last_login
                    cursor.execute("""
                        UPDATE utenti_sistema 
                        SET last_login = CURRENT_TIMESTAMP,
                            modified_at = CURRENT_TIMESTAMP,
                            modified_by = 'system'
                        WHERE username = ?
                    """, (username,))
                    
                    # Log accesso
                    cursor.execute("""
                        INSERT INTO eventi_sistema (tipo_evento, livello, messaggio, componente)
                        VALUES (?, ?, ?, ?)
                    """, ('LOGIN', 'INFO', f'Login utente {username} ({role})', 'AUTH'))
                    
                    conn.commit()
                    logger.debug("Aggiornamento last_login e log accesso completati")
                except Exception as e:
                    logger.error(f"Errore durante l'aggiornamento del database: {e}")
                    conn.rollback()
                finally:
                    conn.close()

            # Imposta dati sessione
            session['username'] = username
            session['role'] = role
            session['logged_in'] = True
            session['login_time'] = datetime.now().strftime('%d/%m/%Y %H:%M')
            session['role_name'] = USER_ROLES.get(role, {}).get('name', 'Utente')
            session['permissions'] = USER_ROLES.get(role, {}).get('permissions', [])
            
            logger.debug("Dati sessione impostati correttamente")
            logger.debug(f"Sessione attuale: {session}")
            
            return redirect('/')
        else:
            logger.debug("Autenticazione fallita")
            return render_template_string(LOGIN_TEMPLATE, error="Credenziali non valide")
    
    # Mostra info sui livelli nel form di login
    login_info = """
    <div class="mt-4 text-center">
        <small class="text-muted">
            <strong>Utenti di test:</strong><br>
            🔴 admin/admin123 (Amministratore)<br>
            🔵 manager/manager123 (Gestore Utenti)<br>
            🟢 viewer/viewer123 (Visualizzatore)
        </small>
    </div>
    """
    
    return render_template_string(LOGIN_TEMPLATE + login_info)

@app.route('/logout')
def logout():
    """Gestisce il logout utente con gestione errori robusta"""
    try:
        username = session.get('username')
        role = session.get('role')
        
        # Log logout se possibile
        if username:
            try:
                conn = get_db_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO eventi_sistema (tipo_evento, livello, messaggio, componente)
                            VALUES (?, ?, ?, ?)
                        """, ('LOGOUT', 'INFO', f'Logout utente {username} ({role})', 'AUTH'))
                        conn.commit()
                    except Exception as e:
                        logger.error(f"Errore logging logout: {e}")
                    finally:
                        conn.close()
            except Exception as e:
                logger.error(f"Errore connessione DB durante logout: {e}")
        
        # Pulisci la sessione in ogni caso
        session.clear()
        
        return redirect('/login')
        
    except Exception as e:
        logger.error(f"Errore durante logout: {e}")
        # Forza pulizia sessione anche in caso di errore
        session.clear()
        return redirect('/login')

@app.route('/api/profile/info')
@require_auth()
def api_profile_info():
    """Restituisce informazioni profilo dalla sessione"""
    return jsonify({
        'success': True,
        'user': {
            'username': session.get('username'),
            'role': session.get('role'),
            'login_time': session.get('login_time', datetime.now().strftime('%d/%m/%Y %H:%M'))
        }
    })

@app.route('/api/user-menu-html')
@require_auth()
def api_user_menu_html():
    """Restituisce HTML del menu utente con dati sessione"""
    
    # Mappa ruoli aggiornata per 3 livelli
    role_names = {
        'admin': 'Amministratore',
        'user_manager': 'Gestore Utenti', 
        'viewer': 'Visualizzatore'
    }
    
    user_role = session.get('role', 'viewer')
    user_role_name = role_names.get(user_role, 'Utente')
    username = session.get('username', 'user')
    
    # Template del menu inline
    menu_html = f'''
    <div class="user-menu-container">
        <!-- Trigger Menu -->
        <div class="user-menu-trigger">
            <div class="user-avatar">
                {username[0].upper()}
            </div>
            <div class="user-menu-info">
                <div class="user-menu-name">{username}</div>
                <div class="user-menu-role">{user_role_name}</div>
            </div>
            <i class="fas fa-chevron-down" style="color: white; font-size: 0.8rem;"></i>
        </div>
        
        <!-- Dropdown Menu -->
        <div class="user-menu-dropdown">
            <div class="user-menu-header">
                <div class="avatar-large">
                    {username[0].upper()}
                </div>
                <div class="user-name">{username}</div>
                <div class="user-email">{user_role_name}</div>
            </div>
            
            <div class="user-menu-items">
                <a href="#" class="user-menu-item" data-action="profile">
                    <i class="fas fa-user-circle"></i>
                    <span class="user-menu-item-text">Il Mio Profilo</span>
                </a>
                
                <a href="#" class="user-menu-item" data-action="change-password">
                    <i class="fas fa-key"></i>
                    <span class="user-menu-item-text">Cambio Password</span>
                </a>
                
                <div class="user-menu-divider"></div>
                
                <a href="/logout" class="user-menu-item logout">
                    <i class="fas fa-sign-out-alt"></i>
                    <span class="user-menu-item-text">Logout</span>
                </a>
            </div>
        </div>
    </div>
    
    <!-- Overlay -->
    <div class="user-menu-overlay"></div>
    '''
    
    return menu_html

# ===============================
# STATIC FILES
# ===============================

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'static'), path)

# ===============================
# API ENDPOINTS - AUTORIZZAZIONE
# ===============================

@app.route('/api/authorize', methods=['POST'])
def authorize():
    """Gestisce l'autorizzazione dell'accesso quando viene passato il codice fiscale"""
    try:
        data = request.get_json()
        if not data or 'codice_fiscale' not in data:
            return jsonify({'success': False, 'error': 'Codice fiscale mancante'}), 400

        codice_fiscale = data['codice_fiscale']
        logger.info(f"Richiesta autorizzazione per CF: {codice_fiscale}")

        # Processa il codice fiscale con la stessa logica usata per la lettura da Omnikey
        result = process_codice_fiscale(codice_fiscale)
        
        if result['authorized']:
            return jsonify({
                'success': True,
                'message': 'Accesso autorizzato',
                'user': result['user_name']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error_message']
            }), 403

    except Exception as e:
        logger.error(f"Errore generico autorizzazione: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def process_codice_fiscale(codice_fiscale):
    """
    Processa un codice fiscale per autorizzazione accesso.
    Questa funzione è usata sia dall'endpoint API che dal lettore Omnikey.
    """
    start_time = time.time()
    result = {
        'authorized': False,
        'user_name': None,
        'error_message': None
    }
    
    # Maschera il CF per i log
    masked_cf = f"{codice_fiscale[:4]}***{codice_fiscale[-4:]}"
    logger.info(f"Elaborazione CF: {masked_cf}")
    
    try:
        # 1. Verifica orario
        if not verifica_orario():
            error_msg = 'Accesso non consentito in questo orario'
            logger.warning(f"Accesso negato per CF {masked_cf}: fuori orario")
            result['error_message'] = error_msg
            return result

        # 2. Verifica utente nel database
        conn = get_db_connection()
        if not conn:
            result['error_message'] = 'Database non disponibile'
            return result

        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, codice_fiscale, nome, attivo
                FROM utenti_autorizzati 
                WHERE codice_fiscale = ?
            ''', (codice_fiscale,))
            
            user = cursor.fetchone()
            if not user:
                error_msg = 'Utente non trovato'
                logger.warning(f"Accesso negato per CF {masked_cf}: utente non trovato")
                result['error_message'] = error_msg
                return result
            
            if not user[3]:  # not attivo
                error_msg = 'Utente disattivato'
                logger.warning(f"Accesso negato per CF {masked_cf}: utente disattivato")
                result['error_message'] = error_msg
                return result

            # 3. Verifica limite mensile
            if not verifica_limite_mensile(codice_fiscale):
                error_msg = 'Limite mensile accessi superato'
                logger.warning(f"Accesso negato per CF {masked_cf}: limite mensile superato")
                result['error_message'] = error_msg
                return result

            # 4. Incrementa contatore accessi
            oggi = datetime.now()
            cursor.execute('''
                INSERT OR REPLACE INTO conteggio_ingressi_mensili 
                (codice_fiscale, mese, anno, numero_ingressi, ultimo_ingresso)
                VALUES (
                    ?,
                    ?,
                    ?,
                    COALESCE(
                        (SELECT numero_ingressi + 1 
                         FROM conteggio_ingressi_mensili 
                         WHERE codice_fiscale = ? AND mese = ? AND anno = ?),
                        1
                    ),
                    CURRENT_TIMESTAMP
                )
            ''', (codice_fiscale, oggi.month, oggi.year, codice_fiscale, oggi.month, oggi.year))

            # 5. Log accesso
            processing_time = time.time() - start_time
            cursor.execute('''
                INSERT INTO log_accessi 
                (timestamp, codice_fiscale, autorizzato, durata_elaborazione, terminale_id)
                VALUES (CURRENT_TIMESTAMP, ?, 1, ?, ?)
            ''', (codice_fiscale, processing_time, "WEB_API"))

            conn.commit()

            # 6. Imposta risultato positivo
            result['authorized'] = True
            result['user_name'] = user[2]  # nome utente
            logger.info(f"Accesso autorizzato per {result['user_name']} (CF: {masked_cf})")
            
            # 7. Apri cancello (solo se chiamato dal lettore Omnikey, non dall'API)
            # Questa parte viene gestita separatamente nella funzione handle_card_read
            
            return result

        except Exception as e:
            logger.error(f"Errore durante autorizzazione per CF {masked_cf}: {str(e)}")
            result['error_message'] = str(e)
            return result
        finally:
            conn.close()

    except Exception as e:
        logger.error(f"Errore generico autorizzazione: {str(e)}")
        result['error_message'] = str(e)
        return result

# ===============================
# API ENDPOINTS - DATI
# ===============================

@app.route('/api/stats')
@require_auth()
def api_stats():
    """Statistiche usando schema database_manager.py"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Oggi
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Accessi oggi
        cursor.execute("""
            SELECT COUNT(*) 
            FROM log_accessi 
            WHERE DATE(timestamp) = ?
        """, (today,))
        accessi_oggi = cursor.fetchone()[0]
        
        # Accessi autorizzati oggi
        cursor.execute("""
            SELECT COUNT(*) 
            FROM log_accessi 
            WHERE DATE(timestamp) = ? AND autorizzato = 1
        """, (today,))
        autorizzati_oggi = cursor.fetchone()[0]
        
        return jsonify({
            'accessi_oggi': accessi_oggi,
            'autorizzati_oggi': autorizzati_oggi
        })
        
    except Exception as e:
        print(f"Errore API stats: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/users/count')
@require_auth()
def api_users_count():
    """Count utenti usando schema database_manager.py"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM utenti_autorizzati WHERE attivo = 1")
        count = cursor.fetchone()[0]
        return jsonify({'count': count})
    except Exception as e:
        print(f"Errore API users count: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/recent-accesses')
@require_auth()
def api_recent_accesses():
    """Accessi recenti usando schema database_manager.py"""
    limit = request.args.get('limit', 10, type=int)
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                la.timestamp, 
                la.codice_fiscale, 
                la.autorizzato,
                COALESCE(ua.nome, 'Utente sconosciuto') as nome_completo
            FROM log_accessi la
            LEFT JOIN utenti_autorizzati ua ON la.codice_fiscale = ua.codice_fiscale
            ORDER BY la.timestamp DESC
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        accesses = []
        
        for row in results:
            accesses.append({
                'timestamp': row[0],
                'codice_fiscale': row[1],
                'autorizzato': bool(row[2]),
                'nome': row[3]
            })
        
        return jsonify({'accesses': accesses})
        
    except Exception as e:
        print(f"Errore API recent accesses: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# ===============================
# API ENDPOINTS - TEST HARDWARE
# ===============================

@app.route('/api/test/gate')
@require_auth()
def api_test_gate():
    """Test cancello"""
    return hardware_tests.test_gate(get_db_connection)

@app.route('/api/test_relay', methods=['POST'])
@require_auth()
def api_test_relay():
    """Test USB-RLY08"""
    return hardware_tests.test_relay()

@app.route('/api/test/integrated', methods=['POST'])
@require_auth()
def api_test_integrated():
    """Test integrato completo"""
    return hardware_tests.test_integrated(get_db_connection)

@app.route('/api/hardware/test-reader', methods=['POST'])
@require_auth()
def api_hardware_test_reader():
    """Test lettore tessere - CORRETTA CHIAMATA A hardware_tests"""
    return hardware_tests.test_reader()

# ===============================
# API ENDPOINTS - ODOO SYNC
# ===============================

@app.route('/api/odoo/sync', methods=['POST'])
@require_auth()
@require_permission('all')
def api_odoo_sync():
    """Forza la sincronizzazione con Odoo"""
    try:
        success, stats = perform_odoo_sync()
        
        if success:
            return jsonify({
                'success': True,
                'message': f"Sincronizzazione completata: {stats['added']} cittadini aggiunti",
                'stats': stats
            })
        else:
            return jsonify({
                'success': False,
                'error': "Sincronizzazione fallita",
                'stats': stats
            }), 500
            
    except Exception as e:
        logger.error(f"Errore API sync Odoo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/odoo/status')
@require_auth()
def api_odoo_status():
    """Stato connessione Odoo"""
    try:
        if not odoo_connector:
            return jsonify({
                'success': False,
                'error': "Connettore Odoo non configurato"
            }), 404
        
        status = odoo_connector.get_sync_status()
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"Errore API status Odoo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===============================
# API ENDPOINTS - STATI
# ===============================

@app.route('/api/relay_status')
@require_auth()
def api_relay_status():
    """Stato test relay"""
    return hardware_tests.get_relay_status()

@app.route('/api/integrated_status')
@require_auth()
def api_integrated_status():
    """Stato test integrato"""
    return hardware_tests.get_integrated_status()

@app.route('/api/hardware/status')
@require_auth()
def api_hardware_status():
    """Stato test hardware"""
    test_id = request.args.get('test_id')
    return hardware_tests.get_hardware_status(test_id)

# ===============================
# API ENDPOINTS - RILEVAMENTO HARDWARE
# ===============================

@app.route('/api/hardware/detect')
@require_auth()
@require_permission('all')
def api_hardware_detect():
    """Rileva automaticamente l'hardware collegato"""
    return jsonify(hardware_detection.detect_hardware())

@app.route('/api/hardware/test-connection', methods=['POST'])
@require_auth()
@require_permission('all')
def api_hardware_test_connection():
    """Testa la connessione a un dispositivo hardware"""
    if not request.is_json:
        return jsonify({'success': False, 'error': 'Richiesta non valida, JSON richiesto'})
    
    data = request.get_json()
    hardware_type = data.get('type')
    device_path = data.get('device_path', data.get('port'))  # Supporta sia 'device_path' che 'port' per retrocompatibilità
    
    if not hardware_type or not device_path:
        return jsonify({
            'success': False,
            'error': 'Tipo di hardware e porta sono richiesti'
        })
    
    # Estrai parametri aggiuntivi specifici per tipo di hardware
    kwargs = {}
    
    # Per lettore tessere
    if hardware_type == 'card_reader':
        if 'reader_type' in data:
            kwargs['reader_type'] = data['reader_type']
    
    # Per controller relè
    elif hardware_type == 'relay':
        if 'baud_rate' in data:
            kwargs['baud_rate'] = data['baud_rate']
    
    # Log parametri
    logger.info(f"Test connessione hardware: tipo={hardware_type}, device_path={device_path}, kwargs={kwargs}")
    
    # Esegui test connessione con parametri aggiuntivi
    return jsonify(hardware_detection.test_hardware_connection(hardware_type, device_path, **kwargs))

@app.route('/api/hardware/config')
@require_auth()
@require_permission('all')
def api_hardware_config():
    """Carica la configurazione dell'hardware"""
    return jsonify(hardware_detection.load_hardware_config(get_db_connection))

@app.route('/api/hardware/config/save', methods=['POST'])
@require_auth()
@require_permission('all')
def api_hardware_config_save():
    """Salva la configurazione dell'hardware"""
    data = request.get_json()
    return jsonify(hardware_detection.save_hardware_config(data, get_db_connection))

@app.route('/api/hardware/test-read-card', methods=['POST'])
@require_auth()
@require_permission('all')
def api_test_read_card():
    """Test lettura tessera sanitaria"""
    try:
        data = request.get_json()
        reader_type = data.get('reader_type', 'CRT285')
        
        # Usa ReaderFactory per creare il lettore giusto
        from hardware.reader_factory import ReaderFactory
        
        if reader_type == 'CRT285':
            device_key = 'usb:23d8:0285'
        else:
            device_key = 'usb:076b:5427'
            
        reader = ReaderFactory.create_reader_by_key(device_key)
        
        if not reader:
            return jsonify({'success': False, 'message': 'Impossibile inizializzare il lettore'})
        
        # Prova a leggere una tessera con timeout
        import threading
        result = {'success': False, 'timeout': True}
        
        def read_card():
            try:
                # Prova a leggere per 10 secondi
                import time
                start_time = time.time()
                while time.time() - start_time < 10:
                    if hasattr(reader, 'read_card_once'):
                        cf = reader.read_card_once()
                    else:
                        # Fallback per altri lettori
                        cf = None
                        
                    if cf:
                        result['success'] = True
                        result['timeout'] = False
                        result['codice_fiscale'] = cf
                        break
                    time.sleep(0.5)
            except Exception as e:
                result['message'] = str(e)
            finally:
                try:
                    reader.stop()
                except:
                    pass
        
        thread = threading.Thread(target=read_card)
        thread.start()
        thread.join(timeout=11)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Errore test lettura tessera: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/test-gate-dashboard', methods=['POST'])
@require_auth()
def api_test_gate_dashboard():
    """Test apertura cancello dalla dashboard"""
    try:
        # Usa il controller relè per aprire il cancello
        relay_controller = USBRLY08Controller()
        
        # Apri relè 1 per 3 secondi (cancello)
        relay_controller.open_gate(duration=3)
        
        return jsonify({'success': True, 'message': 'Cancello aperto per 3 secondi'})
        
    except Exception as e:
        logger.error(f"Errore test cancello: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ===============================
# ROUTES GESTIONE SISTEMA ADMIN
# ===============================

@app.route('/admin/users')
@require_auth()
@require_permission('all')  # Solo admin
def admin_users():
    """Gestione completa utenti - Solo Admin"""
    with open(os.path.join(os.path.dirname(__file__), 'static', 'html', 'user-management.html'), 'r') as f:
        template = f.read()
    return render_template_string(template, session=session)

@app.route('/admin/config')
@require_auth()
@require_permission('all')  # Solo admin
def admin_config():
    """Configurazioni sistema - Solo Admin"""
    return render_template_string(ADMIN_CONFIG_TEMPLATE, session=session)

@app.route('/admin/backup')
@require_auth()
@require_permission('all')  # Solo admin
def admin_backup():
    """Backup & Restore - Solo Admin"""
    return render_template_string(ADMIN_BACKUP_TEMPLATE, session=session)

@app.route('/configurazione-orari')
@require_auth()
@require_permission('all')
def configurazione_orari():
    """Pagina configurazione orari accesso"""
    with open(os.path.join(os.path.dirname(__file__), 'templates', 'configurazione_orari.html'), 'r') as f:
        template = f.read()
    return render_template_string(template, session=session)

@app.route('/test-accessi')
@require_auth()
@require_permission('all')
def test_accessi():
    """Pagina test funzionalità accessi"""
    with open(os.path.join(os.path.dirname(__file__), 'static', 'html', 'test-accessi.html'), 'r') as f:
        template = f.read()
    return render_template_string(template, session=session)
# ===============================
# API ENDPOINTS BACKUP (utilizzando backup_module esistente)
# ===============================

@app.route('/api/backup/status')
@require_auth()
@require_permission('all')
def api_backup_status():
    return backup_module.get_backup_status()

@app.route('/api/backup/create', methods=['POST'])
@require_auth()
@require_permission('all')
def api_backup_create():
    data = request.get_json()
    backup_type = data.get('type', 'complete')
    return backup_module.create_backup(backup_type)

@app.route('/api/backup/cleanup', methods=['POST'])
@require_auth()
@require_permission('all')
def api_backup_cleanup():
    return backup_module.cleanup_old_backups()

@app.route('/api/backup/schedule', methods=['POST'])
@require_auth()
@require_permission('all')
def api_backup_schedule():
    """Salva configurazione schedulazione backup"""
    try:
        data = request.get_json()
        scheduling = data.get('scheduling', 'daily')
        retention = int(data.get('retention', 7))
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO system_settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', ('backup.scheduling', scheduling))
            cursor.execute('''
                INSERT OR REPLACE INTO system_settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', ('backup.retention', str(retention)))
            conn.commit()
            return jsonify({'success': True, 'message': 'Schedulazione backup salvata'})
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/backup/schedule')
@require_auth()
@require_permission('all')
def api_get_backup_schedule():
    """Restituisce configurazione schedulazione backup"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM system_settings WHERE key LIKE 'backup.%'")
            settings = dict(cursor.fetchall())
            return jsonify({'success': True, 'schedule': settings})
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/backup/config', methods=['GET', 'POST'])
@require_auth()
@require_permission('all')
def api_backup_config():
    if request.method == 'GET':
        return backup_module.load_config()
    else:
        config = request.get_json()
        return backup_module.save_config(config)

# ===============================
# API ENDPOINTS CONFIGURAZIONI SISTEMA
# ===============================

@app.route('/api/system/config/save', methods=['POST'])
@require_auth()
@require_permission('all')
def api_save_system_config():
    """Salva configurazioni sistema"""
    try:
        data = request.get_json()
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
        try:
            cursor = conn.cursor()
            for section, values in data.items():
                for key, value in values.items():
                    # Forza il prefisso 'sistema.' per tutte le chiavi di sistema
                    if not section.startswith('sistema'):
                        config_key = f"sistema.{key}"
                    else:
                        config_key = f"{section}.{key}"
                    if isinstance(value, (dict, list)):
                        import json
                        json_value = json.dumps(value)
                    else:
                        json_value = str(value)
                    cursor.execute('''
                        INSERT OR REPLACE INTO system_settings (key, value, updated_at)
                        VALUES (?, ?, CURRENT_TIMESTAMP)
                    ''', (config_key, json_value))
            conn.commit()
            # Log evento
            cursor.execute('''
                INSERT INTO eventi_sistema (tipo_evento, livello, messaggio, componente)
                VALUES (?, ?, ?, ?)
            ''', ('CONFIG_UPDATE', 'INFO', 'Configurazioni sistema aggiornate', 'SYSTEM'))
            conn.commit()
            return jsonify({
                'success': True, 
                'message': 'Configurazioni salvate con successo'
            })
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 3. AGGIUNGI il nuovo endpoint per il reset (dopo api_system_restart, circa riga 620)
@app.route('/api/system/config/reset', methods=['POST'])
@require_auth()
@require_permission('all')
def api_reset_system_config():
    """Ripristina configurazioni ai valori default"""
    try:
        # Ottieni configurazioni default
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
        
        try:
            cursor = conn.cursor()
            
            # Crea tabella se non esiste
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Elimina tutte le configurazioni personalizzate
            cursor.execute('DELETE FROM system_settings')
            
            # Inserisci valori default
            default_values = {
                'sistema.nome_installazione': 'Isola Ecologica RAEE - Rende',
                'sistema.versione': '1.0.0',
                'sistema.ambiente': 'production',
                'sistema.debug_mode': 'false',
                'sistema.porta_web': '5000',
                'sistema.timeout_sessione': '1800',
                
                'hardware.lettore_porta': '/dev/ttyACM0',
                'hardware.relay_porta': '/dev/ttyUSB0',
                'hardware.relay_baudrate': '19200',
                'hardware.gate_duration': '8.0',
                
                'sicurezza.max_tentativi_login': '5',
                'sicurezza.durata_blocco_minuti': '15',
                'sicurezza.rotazione_password_giorni': '90',
                'sicurezza.log_audit_abilitato': 'true',
                
                'email.smtp_server': '',
                'email.smtp_porta': '587',
                'email.mittente': '',
                'email.report_automatici': 'false',
                'email.frequenza_report': 'weekly'
            }
            
            for key, value in default_values.items():
                cursor.execute('''
                    INSERT INTO system_settings (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (key, value))
            
            conn.commit()
            
            # Log evento
            cursor.execute('''
                INSERT INTO eventi_sistema (tipo_evento, livello, messaggio, componente)
                VALUES (?, ?, ?, ?)
            ''', ('CONFIG_RESET', 'WARNING', 'Configurazioni ripristinate ai valori default', 'SYSTEM'))
            
            conn.commit();
            
            return jsonify({
                'success': True,
                'message': 'Configurazioni ripristinate ai valori default'
            })
            
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/system/restart', methods=['POST'])
@require_auth()
@require_permission('all')
def api_system_restart():
    """Riavvia realmente il sistema tramite systemd"""
    try:
        import subprocess
        # Riavvia il servizio systemd (modifica il nome se necessario)
        subprocess.Popen(['sudo', 'systemctl', 'restart', 'access-control-system'])
        return jsonify({
            'success': True,
            'message': 'Sistema in riavvio...'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===============================
# API ENDPOINTS CONFIGURAZIONI - USANDO CONFIG ESISTENTE
# ===============================



@app.route('/api/email/config')
@require_auth()
def api_get_email_config():
    """Ottieni configurazione email"""
    try:
        # Carica da database temporaneo
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM system_settings WHERE key LIKE 'email.%'")
            settings = cursor.fetchall()
            
            config = {
                'smtp_server': '',
                'smtp_port': 587,
                'mittente': '',
                'frequenza_report': 'weekly',
                'orario_invio': '08:00',
                'includi_statistiche': True,
                'includi_errori': True
            }
            
            # Popola con valori salvati
            for key, value in settings:
                setting_name = key.replace('email.', '')
                if setting_name in config:
                    try:
                        # Prova a convertire numeri e boolean
                        if value.lower() in ('true', 'false'):
                            config[setting_name] = value.lower() == 'true'
                        elif value.isdigit():
                            config[setting_name] = int(value)
                        else:
                            config[setting_name] = value
                    except:
                        config[setting_name] = value
            
            return jsonify({'success': True, 'config': config})
            
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/email/save-smtp', methods=['POST'])
@require_auth()
@require_permission('all')
def api_save_smtp_config():
    """Salva configurazione SMTP"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
        
        try:
            cursor = conn.cursor()
            
            # Crea tabella se non esiste
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Salva configurazioni email
            email_settings = {
                'smtp_server': data.get('smtp_server', ''),
                'smtp_port': str(data.get('smtp_port', 587)),
                'mittente': data.get('mittente', '')
            }
            
            for key, value in email_settings.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO system_settings (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (f'email.{key}', value))
            
            # Non salvare password per sicurezza
            if data.get('password'):
                cursor.execute('''
                    INSERT OR REPLACE INTO system_settings (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', ('email.password_set', 'true'))
            
            conn.commit()
            
            return jsonify({'success': True, 'message': 'Configurazione SMTP salvata'})
            
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/devices/config')
@require_auth()
def api_get_devices_config():
    """Ottieni configurazione dispositivi"""
    try:
        # Carica da database temporaneo
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM system_settings WHERE key LIKE 'dispositivi.%'")
            settings = cursor.fetchall()
            
            config = {
                'reader': {
                    'tipo': 'HID Omnikey 5427CK',
                    'porta': '/dev/ttyACM0',
                    'timeout': 30,
                    'retry_tentativi': 3
                },
                'relay': {
                    'porta': '/dev/ttyUSB0',
                    'baud_rate': 19200,
                    'modulo_id': 8
                }
            }
            
            # Popola con valori salvati
            for key, value in settings:
                parts = key.split('.')
                if len(parts) >= 3:
                    device = parts[1]  # lettore_cf o rele
                    setting = parts[2]
                    
                    if device == 'lettore_cf' and setting in config['reader']:
                        try:
                            if setting in ['timeout', 'retry_tentativi']:
                                config['reader'][setting] = int(value)
                            else:
                                config['reader'][setting] = value
                        except:
                            config['reader'][setting] = value
                    elif device == 'rele' and setting in config['relay']:
                        try:
                            if setting in ['baud_rate', 'modulo_id']:
                                config['relay'][setting] = int(value)
                            else:
                                config['relay'][setting] = value
                        except:
                            config['relay'][setting] = value
            
            return jsonify({'success': True, **config})
            
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/devices/config/reader', methods=['POST'])
@require_auth()
@require_permission('all')
def api_save_reader_config():
    """Salva configurazione lettore nel database"""
    try:
        data = request.get_json()
        if not data.get('tipo') or not data.get('porta'):
            return jsonify({'success': False, 'error': 'Configurazione incompleta'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database non disponibile'}), 500

        try:
            cursor = conn.cursor()
            settings = {
                'dispositivi.lettore_cf.tipo': data['tipo'],
                'dispositivi.lettore_cf.porta': data['porta'],
                'dispositivi.lettore_cf.timeout': str(data.get('timeout', 30)),
                'dispositivi.lettore_cf.retry_tentativi': str(data.get('retry_tentativi', 3))
            }
            for key, value in settings.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO system_settings (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (key, value))
            conn.commit()
            return jsonify({'success': True, 'message': 'Configurazione lettore salvata'})
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/devices/config/relay', methods=['POST'])
@require_auth()
@require_permission('all')
def api_save_relay_config():
    """Salva configurazione relè nel database"""
    try:
        data = request.get_json()
        if not data.get('porta') or not data.get('baud_rate'):
            return jsonify({'success': False, 'error': 'Configurazione incompleta'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database non disponibile'}), 500

        try:
            cursor = conn.cursor()
            settings = {
                'dispositivi.rele.porta': data['porta'],
                'dispositivi.rele.baud_rate': str(data['baud_rate']),
                'dispositivi.rele.modulo_id': str(data.get('modulo_id', 8))
            }
            for key, value in settings.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO system_settings (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (key, value))
            # Salva mapping se presente
            if 'mapping' in data:
                import json
                cursor.execute('''
                    INSERT OR REPLACE INTO system_settings (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', ('dispositivi.rele.mapping', json.dumps(data['mapping'])))
            conn.commit()
            return jsonify({'success': True, 'message': 'Configurazione relè salvata'})
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/system/config')
@require_auth()
def api_get_system_config():
    """Restituisce tutte le configurazioni di sistema dal database"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database non disponibile'}), 500

        try:
            cursor = conn.cursor()
            # Prendi tutte le chiavi di sistema, hardware, sicurezza, email
            cursor.execute("""
                SELECT key, value FROM system_settings
                WHERE key LIKE 'sistema.%'
                   OR key LIKE 'hardware.%'
                   OR key LIKE 'sicurezza.%'
                   OR key LIKE 'email.%'
            """)
            settings = cursor.fetchall()
            config = {}
            for key, value in settings:
                section, name = key.split('.', 1)
                if section not in config:
                    config[section] = {}
                config[section][name] = value
            return jsonify({'success': True, 'config': config})
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

BACKUP_DIR = os.path.join(project_root, 'backups')
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

def get_db_connection():
    """Connessione database come database_manager.py"""
    try:
        # Crea la directory se non esiste
        db_dir = os.path.dirname(DB_PATH)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        # Crea il database se non esiste
        if not os.path.exists(DB_PATH):
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            print(f"Database creato in: {DB_PATH}")
            return conn
            
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Errore connessione DB: {e}")
        return None

def ensure_system_settings_table():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        finally:
            conn.close()

def ensure_eventi_sistema_table():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS eventi_sistema (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo_evento TEXT,
                    livello TEXT,
                    messaggio TEXT,
                    componente TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        finally:
            conn.close()

# Ora puoi chiamarla!
config_manager = get_config_manager()
ensure_system_settings_table()
ensure_eventi_sistema_table()

def check_main_process():
    """Controlla se il processo main.py è in esecuzione"""
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            if proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline'])
                if 'python' in cmdline and 'main.py' in cmdline:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

def start_main_process():
    """Avvia il processo main.py in background"""
    try:
        main_path = os.path.join(project_root, 'src', 'main.py')
        subprocess.Popen(['python3', main_path], 
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
        logger.info("✅ Processo main.py avviato in background")
        return True
    except Exception as e:
        logger.error(f"❌ Errore avvio main.py: {e}")
        return False

# ===============================
# DEBUG ENDPOINTS
# ===============================

import collections
import threading

# Buffer circolare per i log
log_buffer = collections.deque(maxlen=100)
log_lock = threading.Lock()

# Custom log handler per catturare i log
class LogCapture(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            with log_lock:
                log_buffer.append(f"{datetime.now().strftime('%H:%M:%S')} - {msg}")
        except Exception:
            pass

# Aggiungi handler al logger
log_capture = LogCapture()
log_capture.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
logger.addHandler(log_capture)

@app.route('/api/system-logs')
@require_auth()
def get_system_logs():
    """Ottiene gli ultimi log del sistema"""
    try:
        with log_lock:
            logs = list(log_buffer)
        return jsonify({"success": True, "logs": logs})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/system-status')
@require_auth()
def get_system_status():
    """Ottiene lo stato del sistema"""
    try:
        global card_reader, card_reader_running
        
        # Controlla se il servizio è attivo
        service_running = True  # Siamo qui quindi il servizio è attivo
        
        # Controlla il lettore
        reader_connected = False
        reader_type = None
        
        if card_reader:
            try:
                # Prova a verificare la connessione
                reader_connected = card_reader.test_connection() if hasattr(card_reader, 'test_connection') else True
                reader_type = card_reader.__class__.__name__
            except:
                reader_connected = False
        
        return jsonify({
            "success": True,
            "service_running": service_running,
            "reader_connected": reader_connected,
            "reader_type": reader_type,
            "reader_running": card_reader_running,
            "uptime": str(datetime.now() - app.start_time) if hasattr(app, 'start_time') else "Unknown"
        })
    except Exception as e:
        logger.error(f"Errore controllo stato: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/restart-service', methods=['POST'])
@require_auth()
@require_permission('all')
def restart_service():
    """Riavvia il servizio (solo admin)"""
    try:
        logger.info("🔄 Richiesta riavvio servizio...")
        
        # Ferma il lettore tessere prima del restart
        stop_card_reader()
        
        # Schedula il restart dopo 1 secondo
        def do_restart():
            time.sleep(1)
            os.system('sudo systemctl restart access-control-web')
        
        threading.Thread(target=do_restart, daemon=True).start()
        
        return jsonify({"success": True, "message": "Riavvio in corso..."})
    except Exception as e:
        logger.error(f"Errore riavvio: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ===============================
# MAIN
# ===============================

# Aggiungi timestamp di avvio
app.start_time = datetime.now()

if __name__ == '__main__':
    print("🌐 Avvio dashboard web modulare")
    print(f"📄 Database: {DB_PATH}")
    print("🔗 URL: http://0.0.0.0:5000")
    
    # Controlla e avvia main.py se necessario
    if not check_main_process():
        print("⚠️ Processo main.py non trovato, avvio in background...")
        if start_main_process():
            print("✅ Processo main.py avviato correttamente")
        else:
            print("❌ Errore avvio main.py")
    
    # Crea directory static se non esiste
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
        print(f"📁 Creata directory static: {static_dir}")
    
        # Avvia il server sulla porta 5000 fissa
    print(f"🔌 Porta selezionata: 5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

print("=== ENDPOINTS REGISTRATI ===")
for rule in app.url_map.iter_rules():
    print(rule)
print("============================")

# Variabili globali per il lettore di tessere e Odoo
card_reader = None
card_reader_thread = None
card_reader_running = False
odoo_connector = None
odoo_sync_thread = None
odoo_sync_running = False

def handle_card_read(codice_fiscale):
    """
    Gestisce la lettura di una tessera dal lettore Omnikey.
    Questa funzione viene chiamata dal CardReader quando viene letta una tessera.
    """
    logger.info(f"Tessera letta dal lettore Omnikey: {codice_fiscale[:4]}***{codice_fiscale[-4:]}")
    
    # Processa il codice fiscale
    result = process_codice_fiscale(codice_fiscale)
    
    # Gestisci l'hardware solo se l'autorizzazione è stata processata
    try:
        controller = USBRLY08Controller()
        if controller.connect():
            try:
                if result['authorized']:
                    # Segnala accesso autorizzato (LED Verde + Buzzer)
                    controller.access_granted()
                    
                    # Apri cancello per 8 secondi
                    controller.open_gate(8.0)
                    
                    logger.info(f"Cancello aperto per accesso autorizzato")
                else:
                    # Segnala accesso negato (LED Rosso)
                    controller.access_denied()
                    logger.warning(f"Accesso negato: {result['error_message']}")
            finally:
                controller.disconnect()
        else:
            logger.error("Errore connessione controller USB-RLY08")
    except Exception as e:
        logger.error(f"Errore hardware durante gestione tessera: {str(e)}")

def start_card_reader():
    """Avvia il lettore di tessere in un thread separato"""
    global card_reader, card_reader_thread, card_reader_running
    
    if card_reader_running:
        logger.warning("Lettore tessere già in esecuzione")
        return
    
    try:
        # Carica configurazione hardware
        config = get_config_manager()
        device_assignments = config.get('device_assignments', {})
        
        reader_config = device_assignments.get('card_reader', {})
        device_key = reader_config.get('device_key', None)
        device_path = reader_config.get('device_path', None)
        
        logger.info(f"Avvio lettore tessere con configurazione: device_key={device_key}")
        
        # Usa ReaderFactory per creare il lettore corretto basato sulla configurazione
        card_reader = ReaderFactory.create_reader_by_key(device_key=device_key, device_path=device_path)
        
        if not card_reader:
            logger.error("Nessun lettore tessere trovato o configurato")
            return
            
        card_reader_running = True
        
        # Avvia il lettore in un thread separato
        card_reader_thread = threading.Thread(
            target=card_reader.start_continuous_reading,
            args=(handle_card_read,),
            daemon=True
        )
        card_reader_thread.start()
        
        logger.info("Lettore tessere Omnikey avviato con successo")
    except Exception as e:
        logger.error(f"Errore avvio lettore tessere: {str(e)}")
        card_reader_running = False

def stop_card_reader():
    """Ferma il lettore di tessere"""
    global card_reader, card_reader_running, card_reader_thread
    
    if not card_reader_running:
        return
    
    try:
        logger.info("Arresto lettore tessere...")
        card_reader_running = False
        
        if card_reader:
            try:
                card_reader.stop()
            except Exception as e:
                logger.warning(f"Errore durante stop del lettore: {e}")
        
        # Attendi che il thread termini
        if card_reader_thread and card_reader_thread.is_alive():
            card_reader_thread.join(timeout=2)
            
        # Pulisci le variabili globali
        card_reader = None
        card_reader_thread = None
        
        logger.info("Lettore tessere arrestato e risorse pulite")
    except Exception as e:
        logger.error(f"Errore arresto lettore tessere: {str(e)}")

# Funzioni per la sincronizzazione con Odoo
def configure_odoo_connector():
    """Configura il connettore Odoo"""
    global odoo_connector
    
    try:
        logger.info("Configurazione connettore Odoo...")
        
        # Crea un mock config manager per OdooPartnerConnector
        class MockConfigManager:
            def __init__(self):
                self.config = MockConfig()
            def get_config(self):
                return self.config
        
        class MockConfig:
            def __init__(self):
                self.odoo = None
        
        # Configurazione Odoo
        odoo_config = {
            'url': 'https://app.calabramaceri.it',
            'database': 'cmapp',
            'username': 'controllo-accessi@calabramaceri.it',
            'password': 'AcC3ss0C0ntr0l!2025#Rnd',
            'comune': 'Rende',
            'sync_interval_hours': 12
        }
        
        # Inizializza il connettore
        mock_config_manager = MockConfigManager()
        odoo_connector = OdooPartnerConnector(mock_config_manager)
        odoo_connector.configure_connection(
            url=odoo_config['url'],
            database=odoo_config['database'],
            username=odoo_config['username'],
            password=odoo_config['password'],
            comune=odoo_config['comune'],
            sync_interval=odoo_config['sync_interval_hours'] * 3600
        )
        
        # Test connessione
        success, message = odoo_connector.test_connection()
        if success:
            logger.info(f"Connessione Odoo stabilita: {message}")
            
            # Avvia sync automatica
            start_odoo_sync()
            return True
        else:
            logger.warning(f"Test connessione Odoo fallito: {message}")
            return False
            
    except Exception as e:
        logger.error(f"Errore configurazione Odoo: {e}")
        return False

def start_odoo_sync():
    """Avvia la sincronizzazione automatica con Odoo"""
    global odoo_connector, odoo_sync_thread, odoo_sync_running
    
    if odoo_sync_running:
        logger.warning("Sincronizzazione Odoo già in esecuzione")
        return
    
    try:
        logger.info("Avvio sincronizzazione automatica Odoo...")
        odoo_sync_running = True
        
        # Esegui sync iniziale
        perform_odoo_sync()
        
        # Avvia thread per sync periodica
        def sync_worker():
            while odoo_sync_running:
                try:
                    # Attendi intervallo configurato (default 12 ore)
                    sleep_hours = 12
                    logger.info(f"Prossima sync Odoo in {sleep_hours} ore")
                    time.sleep(sleep_hours * 3600)
                    
                    if odoo_sync_running:
                        perform_odoo_sync()
                        
                except Exception as e:
                    logger.error(f"Errore sync worker Odoo: {e}")
                    time.sleep(3600)  # Riprova tra un'ora in caso di errore
        
        odoo_sync_thread = threading.Thread(target=sync_worker, daemon=True)
        odoo_sync_thread.start()
        
        logger.info("Sincronizzazione automatica Odoo avviata")
        
    except Exception as e:
        logger.error(f"Errore avvio sync Odoo: {e}")
        odoo_sync_running = False

def stop_odoo_sync():
    """Ferma la sincronizzazione automatica con Odoo"""
    global odoo_sync_running
    
    if not odoo_sync_running:
        return
    
    try:
        logger.info("Arresto sincronizzazione Odoo...")
        odoo_sync_running = False
        
        if odoo_connector:
            odoo_connector.disconnect()
            
        logger.info("Sincronizzazione Odoo arrestata")
        
    except Exception as e:
        logger.error(f"Errore arresto sync Odoo: {e}")

def perform_odoo_sync():
    """Esegue la sincronizzazione con Odoo"""
    global odoo_connector
    
    if not odoo_connector:
        logger.warning("Connettore Odoo non configurato")
        return False, {"error": "Connettore Odoo non configurato"}
    
    try:
        logger.info("Esecuzione sincronizzazione Odoo...")
        
        # Ottieni connessione database
        conn = get_db_connection()
        if not conn:
            logger.error("Database non disponibile per sync Odoo")
            return False, {"error": "Database non disponibile"}
        
        # Crea un wrapper per DatabaseManager
        class DatabaseWrapper:
            def __init__(self, conn):
                self.conn = conn
            
            def verify_access(self, codice_fiscale):
                try:
                    cursor = self.conn.cursor()
                    cursor.execute('''
                        SELECT id, nome, note
                        FROM utenti_autorizzati 
                        WHERE codice_fiscale = ? AND attivo = 1
                    ''', (codice_fiscale.upper(),))
                    
                    result = cursor.fetchone()
                    
                    if result:
                        user_data = {
                            'id': result[0],
                            'nome': result[1],
                            'note': result[2]
                        }
                        return True, user_data
                    else:
                        return False, None
                except Exception as e:
                    logger.error(f"Errore verifica accesso: {e}")
                    return False, None
            
            def add_user(self, codice_fiscale, nome, note=None, creato_da=None, modificato_da=None):
                try:
                    cursor = self.conn.cursor()
                    cursor.execute('''
                        INSERT INTO utenti_autorizzati 
                        (codice_fiscale, nome, note, creato_da, modificato_da)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        codice_fiscale.upper(),
                        nome,
                        note,
                        creato_da,
                        modificato_da
                    ))
                    self.conn.commit()
                    
                    logger.info(f"Utente aggiunto: {nome} ({codice_fiscale})")
                    return True
                    
                except sqlite3.IntegrityError:
                    logger.warning(f"Utente già esistente: {codice_fiscale}")
                    return False
                except Exception as e:
                    logger.error(f"Errore aggiunta utente: {e}")
                    return False
        
        # Esegui sincronizzazione
        db_wrapper = DatabaseWrapper(conn)
        success, stats = odoo_connector.sync_to_database(db_wrapper)
        
        if success:
            logger.info(f"Sync Odoo completata: {stats['added']} cittadini aggiunti")
            return True, stats
        else:
            logger.warning("Sync Odoo fallita")
            return False, stats
            
    except Exception as e:
        logger.error(f"Errore sync Odoo: {e}")
        return False, {"error": str(e)}

# Avvia il lettore di tessere all'avvio dell'applicazione
start_card_reader()

# Configura e avvia la sincronizzazione con Odoo
configure_odoo_connector()

# Registra funzione di pulizia all'uscita
import atexit
atexit.register(stop_card_reader)
atexit.register(stop_odoo_sync)

def scheduled_backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'access_{timestamp}.db'
    src = DB_PATH
    dst = os.path.join(BACKUP_DIR, backup_filename)
    shutil.copy2(src, dst)
    print(f"[SCHEDULER] Backup creato: {backup_filename}")

    # Retention
    conn = get_db_connection()
    retention = 7
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM system_settings WHERE key='backup.retention'")
            row = cursor.fetchone()
            if row:
                retention = int(row[0])
        finally:
            conn.close()
    files = sorted(
        [os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if os.path.isfile(os.path.join(BACKUP_DIR, f))],
        key=lambda x: os.path.getmtime(x)
    )
    to_delete = files[:-retention]
    for f in to_delete:
        os.remove(f)
        print(f"[SCHEDULER] Backup eliminato per retention: {os.path.basename(f)}")

# Scarica backup
@app.route('/api/backup/download/<filename>')
@require_auth()
@require_permission('all')
def api_backup_download(filename: str) -> FlaskResponse:
    return backup_module.download_backup(filename)

# Elimina backup
@app.route('/api/backup/delete/<filename>', methods=['DELETE'])
@require_auth()
@require_permission('all')
def api_backup_delete(filename: str) -> FlaskResponse:
    return backup_module.delete_backup(filename)

# Ripristina backup (sovrascrive access.db)
@app.route('/api/backup/restore/<filename>', methods=['POST'])
@require_auth()
@require_permission('all')
def api_backup_restore(filename: str) -> FlaskResponse:
    return backup_module.restore_backup(filename)
