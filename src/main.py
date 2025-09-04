# File: /opt/access_control/src/main.py
# APPLICAZIONE PRINCIPALE CON INTEGRAZIONE ODOO + USB-RLY08 REALE
# Versione con gestione robusta logging

import sys
import os
import time
import signal
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path

# Aggiungi moduli al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'hardware'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'database'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'external'))

# Import moduli
try:
    from card_reader import CardReader
    from database_manager import DatabaseManager
    from odoo_partner_connector import OdooPartnerConnector
    from usb_rly08_controller import USBRLY08Controller  # NUOVO CONTROLLER REALE
    from core.config import get_config_manager
    from hardware.reader_factory import ReaderFactory
    print("✅ Moduli importati correttamente (incluso USB-RLY08)")
except ImportError as e:
    print(f"⚠️ Import warning: {e}")

# Setup logging ROBUSTO con fallback
project_root = Path(__file__).parent.parent
log_dir = project_root / "logs"

# Crea directory log se non esiste (con gestione errori)
try:
    log_dir.mkdir(exist_ok=True)
    log_access_ok = True
    # Test scrittura
    test_file = log_dir / "test_write.tmp"
    test_file.write_text("test")
    test_file.unlink()
except (PermissionError, OSError) as e:
    print(f"⚠️ Impossibile accedere a {log_dir}: {e}")
    print("📝 Log verranno scritti solo su console")
    log_access_ok = False

# Configurazione logging con fallback
log_handlers = [logging.StreamHandler(sys.stdout)]

if log_access_ok:
    try:
        log_handlers.append(logging.FileHandler(log_dir / 'access_control.log'))
        print(f"📝 Log file: {log_dir / 'access_control.log'}")
    except Exception as e:
        print(f"⚠️ Impossibile creare log file: {e}")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=log_handlers
)
logger = logging.getLogger(__name__)

# Setup logger specifici con gestione errori
def setup_secure_logger(name: str, filename: str):
    """Setup logger sicuro con fallback"""
    logger_instance = logging.getLogger(name)
    
    if log_access_ok:
        try:
            handler = logging.FileHandler(log_dir / filename)
            handler.setFormatter(logging.Formatter(
                f'%(asctime)s - {name.upper()} - %(levelname)s - %(message)s'
            ))
            logger_instance.addHandler(handler)
            logger_instance.setLevel(logging.INFO)
        except Exception as e:
            print(f"⚠️ Impossibile creare logger {name}: {e}")
            # Fallback a console
            logger_instance.addHandler(logging.StreamHandler(sys.stdout))
    else:
        # Solo console
        logger_instance.addHandler(logging.StreamHandler(sys.stdout))
    
    return logger_instance

# Logger specializzati
security_logger = setup_secure_logger('security_audit', 'security_audit.log')
raee_logger = setup_secure_logger('raee_audit', 'raee_access.log')

# Mock components solo per Arduino (USB-RLY08 sostituisce tutto il resto)
class MockArduino:
    """Mock Arduino - ora solo per compatibilità, USB-RLY08 gestisce tutto"""
    def access_granted(self):
        print("🟢 [Compatibilità] Arduino: LED VERDE")
        logger.info("Hardware: Segnale accesso autorizzato (compatibilità)")
    
    def access_denied(self):
        print("🔴 [Compatibilità] Arduino: LED ROSSO") 
        logger.warning("Hardware: Segnale accesso negato (compatibilità)")
    
    def processing(self, active):
        status = "ON" if active else "OFF"
        print(f"🟡 [Compatibilità] Arduino: Processing {status}")

class MockConfigManager:
    """Config Manager mock per OdooPartnerConnector"""
    
    def __init__(self):
        self.config = MockConfig()
    
    def get_config(self):
        return self.config

class MockConfig:
    """Config mock che simula la struttura richiesta"""
    
    def __init__(self):
        self.odoo = None

class AccessControlSystem:
    """Sistema controllo accessi ISOLA RAEE con integrazione Odoo + USB-RLY08"""
    
    def __init__(self):
        self.running = False
        self.last_sync_time = None
        self.sync_in_progress = False
        
        # Statistiche con sicurezza ISOLA RAEE
        self.stats = {
            'total': 0, 'authorized': 0, 'denied': 0,
            'sync_operations': 0, 'failed_connections': 0,
            'last_security_check': None,
            'raee_sessions': 0, 'avg_session_duration': 0
        }
        
        # Rate limiting sicurezza
        self.rate_limiter = {
            'max_attempts_per_minute': 60,
            'attempts_log': [],
            'blocked_until': None
        }

        # Debounce e blocco CF ripetuti
        self.cf_last_read = {}  # {cf: timestamp ultima lettura}
        self.cf_blocked = {}    # {cf: timestamp sblocco}
        
        # Componenti
        self.card_reader = None
        self.arduino = MockArduino()  # Solo compatibilità
        self.usb_relay_controller = None  # CONTROLLER REALE USB-RLY08
        self.database = None
        self.odoo_connector = None
        
        # Configurazione Odoo CORRETTA
        self.odoo_config = {
            'url': 'https://app.calabramaceri.it',
            'database': 'cmapp',
            'username': 'controllo-accessi@calabramaceri.it',
            'password': 'AcC3ss0C0ntr0l!2025#Rnd',
            'comune': 'Rende',
            'sync_interval_hours': 12
        }
        
        # Configurazione ISOLA RAEE
        self.raee_config = {
            'location': 'Isola Ecologica RAEE - Rende',
            'gate_open_duration': 8.0,  # 8 secondi per isola RAEE
            'auto_lighting': True,
            'security_lock': True
        }
        
        print("🏗️ Sistema ISOLA RAEE con USB-RLY08 inizializzato")
        security_logger.info("SYSTEM_INIT - RAEE access control system started")
        raee_logger.info("RAEE_SYSTEM_INIT - Isola Ecologica control system started")
    
    def security_check(self) -> bool:
        """Controlli sicurezza avanzati ISOLA RAEE"""
        try:
            current_time = datetime.now()
            
            # Rate limiting check
            if self.rate_limiter['blocked_until']:
                if current_time < self.rate_limiter['blocked_until']:
                    return False
                else:
                    self.rate_limiter['blocked_until'] = None
            
            # Pulizia rate limiter
            one_minute_ago = current_time - timedelta(minutes=1)
            self.rate_limiter['attempts_log'] = [
                t for t in self.rate_limiter['attempts_log'] if t > one_minute_ago
            ]
            
            # Rate limit check
            if len(self.rate_limiter['attempts_log']) >= self.rate_limiter['max_attempts_per_minute']:
                self.rate_limiter['blocked_until'] = current_time + timedelta(minutes=5)
                security_logger.critical("RATE_LIMIT_EXCEEDED - Sistema bloccato")
                return False
            
            self.stats['last_security_check'] = current_time
            return True
            
        except Exception as e:
            security_logger.error(f"SECURITY_CHECK_FAILED - {e}")
            return False
    
    def log_raee_access(self, cf: str, authorized: bool, user_data: dict = None):
        """Log specifico per accessi ISOLA RAEE"""
        timestamp = datetime.now()
        self.rate_limiter['attempts_log'].append(timestamp)
        
        # CF mascherato per log sicurezza
        masked_cf = f"{cf[:4]}***{cf[-4:]}"
        
        # Log RAEE specifico
        user_name = "Cittadino Sconosciuto"
        if user_data:
            user_name = user_data.get('nome', 'Utente')
        
        raee_logger.info(
            f"RAEE_ACCESS - CF: {masked_cf} - "
            f"User: {user_name} - "
            f"Authorized: {authorized} - "
            f"Location: {self.raee_config['location']} - "
            f"Timestamp: {timestamp.isoformat()}"
        )
        
        # Log sicurezza generale
        security_logger.info(
            f"ACCESS_ATTEMPT - CF: {masked_cf} - "
            f"Authorized: {authorized} - Timestamp: {timestamp.isoformat()}"
        )
    
    def initialize(self):
        """Inizializza componenti con Odoo + USB-RLY08"""
        print("🔧 Inizializzazione ISOLA RAEE con USB-RLY08...")
        
        try:
            # Security check
            if not self.security_check():
                logger.error("❌ Security check fallito")
                return False
            
            # USB-RLY08 Controller (REALE)
            print("🔌 Inizializzazione USB-RLY08...")
            config_manager = get_config_manager()
            relay_cfg = config_manager.get_hardware_assignment("relay_controller")
            relay_port = relay_cfg.get("device_key", "/dev/ttyUSB0")
            # device_key può essere tipo "usb:04d8:ffee" oppure direttamente la porta, gestiamo entrambi
            if relay_port.startswith("/dev/"):
                relay_device_path = relay_port
            else:
                # Mappatura device_key → porta reale (da implementare se serve)
                relay_device_path = "/dev/ttyUSB0"
            self.usb_relay_controller = USBRLY08Controller(device_path=relay_device_path)
            
            if not self.usb_relay_controller.connect():
                logger.error("❌ USB-RLY08 non connesso")
                print("⚠️ Impossibile connettersi a USB-RLY08")
                print("💡 Verifica:")
                print("   1. Dispositivo collegato USB")
                print("   2. Permessi gruppo dialout (newgrp dialout)")
                print("   3. Porta /dev/ttyACM0 disponibile")
                
                # Chiedi se continuare senza hardware
                response = input("\n🔧 Continuare senza USB-RLY08? (y/n): ").lower().strip()
                if response not in ['y', 'yes', 's', 'si']:
                    return False
                
                print("⚠️ Modalità DEMO attivata - solo mock hardware")
                self.usb_relay_controller = None
            else:
                logger.info("✅ USB-RLY08 Controller inizializzato")
                print("✅ USB-RLY08 Controller operativo")
                
                # Test iniziale relè
                print("🧪 Test iniziale sistema...")
                self.usb_relay_controller.set_area_lighting(True)
                time.sleep(1)
                self.usb_relay_controller.set_area_lighting(False)
            
            # CardReader
            card_cfg = config_manager.get_hardware_assignment("card_reader")
            card_device_key = card_cfg.get("device_key", None)
            card_device_path = card_cfg.get("device_path", None)
            self.card_reader = ReaderFactory.create_reader_by_key(device_key=card_device_key, device_path=card_device_path)
            logger.info(f"✅ Lettore inizializzato: {self.card_reader.__class__.__name__ if self.card_reader else 'Nessun lettore'}")
            
            # Database
            db_path = project_root / "src" / "access.db"
            self.database = DatabaseManager(str(db_path))
            
            if not self.database.health_check():
                logger.error("❌ Database non funzionante")
                return False
            
            logger.info("✅ Database inizializzato")
            
            # Odoo Connector con configurazione CORRETTA
            mock_config_manager = MockConfigManager()
            self.odoo_connector = OdooPartnerConnector(mock_config_manager)
            self.odoo_connector.configure_connection(
                url=self.odoo_config['url'],
                database=self.odoo_config['database'],
                username=self.odoo_config['username'],
                password=self.odoo_config['password'],
                comune=self.odoo_config['comune'],
                sync_interval=self.odoo_config['sync_interval_hours'] * 3600
            )
            
            # Test connessione
            success, message = self.odoo_connector.test_connection()
            if success:
                logger.info("✅ Connessione Odoo sicura stabilita")
                security_logger.info(f"ODOO_CONNECTION_SUCCESS - {message}")
                
                # SYNC COMPLETA PRIMA DELL'AVVIO
                print("🔄 Sincronizzazione database ISOLA RAEE...")
                print("⏳ Attendere completamento sync cittadini Rende...")
                logger.info("🔄 Esecuzione sync completa OBBLIGATORIA...")
                
                sync_success, sync_stats = self.odoo_connector.sync_to_database(self.database)
                
                if sync_success:
                    citizens_added = sync_stats.get('added', 0)
                    citizens_fetched = sync_stats.get('fetched', 0)
                    print(f"✅ Sincronizzazione ISOLA RAEE completata!")
                    print(f"📊 {citizens_fetched} cittadini Rende, {citizens_added} aggiunti")
                    logger.info(f"✅ Sync iniziale completata: {citizens_added} cittadini")
                    self.stats['sync_operations'] += 1
                    self.last_sync_time = datetime.now()
                else:
                    print("❌ ERRORE: Sincronizzazione fallita!")
                    logger.error("❌ Sync iniziale fallita - sistema continuerà con database locale")
                    print("⚠️ Sistema continuerà con database locale")
                
                # Avvia sync automatica periodica
                self.start_auto_sync()
                
            else:
                logger.warning(f"⚠️ Test Odoo fallito: {message}")
                security_logger.warning(f"ODOO_CONNECTION_FAILED - {message}")
                logger.info("🔄 Sistema continuerà con database locale")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione: {e}")
            security_logger.error(f"INIT_FAILED - {e}")
            return False
    
    def start_auto_sync(self):
        """Avvia sincronizzazione automatica"""
        def sync_worker():
            while self.running:
                try:
                    sleep_hours = self.odoo_config['sync_interval_hours']
                    logger.info(f"⏰ Prossima sync automatica in {sleep_hours} ore")
                    time.sleep(sleep_hours * 3600)
                    
                    if self.running:
                        self.perform_sync()
                    
                except Exception as e:
                    logger.error(f"❌ Errore sync worker: {e}")
                    time.sleep(3600)
        
        sync_thread = threading.Thread(target=sync_worker, daemon=True)
        sync_thread.start()
        logger.info("🔄 Auto-sync Odoo avviata")
    
    def perform_sync(self):
        """Esegue sincronizzazione sicura"""
        if self.sync_in_progress:
            return
        
        self.sync_in_progress = True
        sync_start = datetime.now()
        
        try:
            logger.info("🔄 Inizio sincronizzazione Odoo ISOLA RAEE")
            security_logger.info("SYNC_START - Odoo synchronization initiated")
            
            success, stats = self.odoo_connector.sync_to_database(self.database)
            
            if success:
                self.last_sync_time = datetime.now()
                self.stats['sync_operations'] += 1
                
                duration = (datetime.now() - sync_start).total_seconds()
                logger.info(f"✅ Sync completata in {duration:.2f}s - Stats: {stats}")
                
                security_logger.info(
                    f"SYNC_SUCCESS - Duration: {duration:.2f}s - "
                    f"Citizens: {stats['fetched']} - Added: {stats['added']}"
                )
            else:
                self.stats['failed_connections'] += 1
                logger.warning("⚠️ Sincronizzazione fallita")
                
        except Exception as e:
            logger.error(f"❌ Errore sync: {e}")
            security_logger.error(f"SYNC_ERROR - {e}")
        finally:
            self.sync_in_progress = False
    
    def handle_cf(self, codice_fiscale):
        """Gestisce CF ISOLA RAEE con hardware USB-RLY08, debounce e blocco ripetizioni (autorizzati e non)"""
        now = time.time()
        debounce_time = 10  # secondi
        block_time = 60     # secondi

        # Normalizza il codice fiscale per il tracking (upper/strip)
        cf_norm = codice_fiscale.strip().upper()

        # Gestione blocco temporaneo per CF ripetuti (autorizzati e non)
        last_read = self.cf_last_read.get(cf_norm)
        blocked_until = self.cf_blocked.get(cf_norm)

        # Se il CF è bloccato, inibisci relè e logga
        if blocked_until and now < blocked_until:
            logger.warning(f"⛔ CF {cf_norm} bloccato fino a {datetime.fromtimestamp(blocked_until)}: azionamento relè inibito per sicurezza")
            print(f"⛔ CF {cf_norm} bloccato: azionamento relè inibito per 1 minuto")
            if self.usb_relay_controller:
                self.usb_relay_controller.access_denied()
            else:
                print("❌ [MOCK] Accesso bloccato per sicurezza (blocco ripetizione)")
            return

        # Se il CF è stato letto meno di 10s fa, ignora la lettura (debounce)
        if last_read and (now - last_read) < debounce_time:
            logger.info(f"⏳ CF {cf_norm} letto troppo presto: debounce attivo ({now - last_read:.1f}s)")
            print(f"⏳ CF {cf_norm} ignorato (debounce <10s)")
            return

        # Se il CF è stato letto tra 10s e 60s fa, attiva blocco per 1 minuto
        if last_read and debounce_time <= (now - last_read) < block_time:
            self.cf_blocked[cf_norm] = now + block_time
            logger.warning(f"⛔ CF {cf_norm} letto due volte in meno di 1 minuto: attivo blocco per 1 minuto")
            print(f"⛔ CF {cf_norm} bloccato per 1 minuto per ripetizione")
            if self.usb_relay_controller:
                self.usb_relay_controller.access_denied()
            else:
                print("❌ [MOCK] Accesso bloccato per sicurezza (blocco ripetizione)")
            return

        # Aggiorna timestamp ultima lettura (sia autorizzati che non)
        self.cf_last_read[cf_norm] = now

        # Prosegui con la normale gestione accesso
        if not self.security_check():
            logger.warning("⚠️ Security check fallito - accesso bloccato")
            if self.usb_relay_controller:
                self.usb_relay_controller.access_denied()
            else:
                print("❌ [MOCK] Accesso bloccato per sicurezza")
            return
        
        start_time = time.time()
        masked_cf = f"{codice_fiscale[:4]}***{codice_fiscale[-4:]}"
        
        logger.info(f"🎯 CF ricevuto ISOLA RAEE: {masked_cf}")
        
        # Processing con illuminazione area
        if self.usb_relay_controller:
            self.usb_relay_controller.processing(True)
        else:
            print("🟡 [MOCK] Elaborazione in corso...")
        
        print(f"\n🟡 ELABORAZIONE ACCESSO ISOLA RAEE...")
        print(f"🆔 CF: {masked_cf}")
        
        try:
            # Verifica accesso
            authorized, user_data = self.database.verify_access(codice_fiscale)
            
            # Log accesso RAEE
            self.log_raee_access(codice_fiscale, authorized, user_data)
            
            # Statistiche
            self.stats['total'] += 1
            if authorized:
                self.stats['authorized'] += 1
                self.stats['raee_sessions'] += 1
            else:
                self.stats['denied'] += 1
            
            # Log database
            processing_time = time.time() - start_time
            self.database.log_access(
                codice_fiscale=codice_fiscale,
                authorized=authorized,
                processing_time=processing_time,
                user_data=user_data,
                terminal_id="RAEE_ISOLA_RENDE_001"
            )
            
            # Fine processing
            if self.usb_relay_controller:
                self.usb_relay_controller.processing(False)
            
            if authorized:
                # ACCESSO AUTORIZZATO ISOLA RAEE
                user_name = user_data.get('nome', 'Cittadino') if user_data else 'Cittadino'
                
                print(f"\n✅ ACCESSO AUTORIZZATO - ISOLA ECOLOGICA RAEE")
                print(f"🏘️ Comune: {self.odoo_config['comune']}")
                print(f"👤 Cittadino: {user_name}")
                print(f"🆔 CF: {masked_cf}")
                print(f"📍 Ubicazione: {self.raee_config['location']}")
                print(f"⏱️ Tempo elaborazione: {processing_time:.2f}s")
                
                # Segnalazioni hardware USB-RLY08
                if self.usb_relay_controller:
                    self.usb_relay_controller.access_granted()  # LED Verde + Buzzer
                    gate_duration = self.raee_config['gate_open_duration']
                    self.usb_relay_controller.open_gate(gate_duration)
                    print(f"🚪 Cancello aperto per {gate_duration} secondi")
                else:
                    print("🟢 [MOCK] LED Verde + Buzzer OK")
                    print("🚪 [MOCK] Cancello aperto per 8 secondi")
                
                print("♻️ Accesso consentito per conferimento RAEE")
                
                # Log RAEE specifico
                raee_logger.info(f"RAEE_ACCESS_GRANTED - User: {user_name} - Gate: {self.raee_config['gate_open_duration']}s")
                
            else:
                # ACCESSO NEGATO
                print(f"\n❌ ACCESSO NEGATO - ISOLA RAEE")
                print(f"⚠️ CF non autorizzato: {masked_cf}")
                print(f"🏘️ Solo cittadini {self.odoo_config['comune']} autorizzati")
                print("📞 Per informazioni contattare ufficio ambiente")
                
                # Segnalazioni hardware USB-RLY08
                if self.usb_relay_controller:
                    self.usb_relay_controller.access_denied()  # LED Rosso + Buzzer x3
                else:
                    print("🔴 [MOCK] LED Rosso + 3 Buzzer")
                
                # Log RAEE negato
                raee_logger.warning(f"RAEE_ACCESS_DENIED - CF: {masked_cf}")
            
            # Statistiche
            self.print_raee_stats()
            print("-" * 60)
            
        except Exception as e:
            logger.error(f"❌ Errore gestione CF: {e}")
            security_logger.error(f"CF_HANDLING_ERROR - {e}")
            if self.usb_relay_controller:
                self.usb_relay_controller.access_denied()
        finally:
            if self.usb_relay_controller:
                self.usb_relay_controller.processing(False)
    
    def print_raee_stats(self):
        """Stampa statistiche ISOLA RAEE"""
        total = self.stats['total']
        success_rate = (self.stats['authorized'] / total * 100) if total > 0 else 0
        
        print(f"📊 Stats RAEE: {self.stats['authorized']}/{total} autorizzati ({success_rate:.1f}%)")
        print(f"♻️ Sessioni RAEE: {self.stats['raee_sessions']}")
        print(f"🔄 Sync Odoo: {self.stats['sync_operations']} completate")
        
        if self.last_sync_time:
            hours_ago = (datetime.now() - self.last_sync_time).total_seconds() / 3600
            print(f"⏰ Ultima sync: {hours_ago:.1f}h fa")
    
    def run(self):
        """Avvia sistema ISOLA RAEE"""
        print("🚀 AVVIO SISTEMA CONTROLLO ACCESSI ISOLA RAEE")
        print("=" * 60)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"♻️ Ubicazione: {self.raee_config['location']}")
        print(f"🏘️ Comune: {self.odoo_config['comune']}")
        print(f"🔗 Server: {self.odoo_config['url']}")
        print(f"👤 Utente: {self.odoo_config['username']}")
        hardware_status = "USB-RLY08 Controller" if self.usb_relay_controller else "MOCK Mode"
        print(f"🔌 Hardware: {hardware_status}")
        print()
        print("🔧 Inizializzazione sistema...")
        
        if not self.initialize():
            print("❌ Inizializzazione fallita")
            return False
        
        print(f"\n♻️ SISTEMA ISOLA RAEE ATTIVO")
        print("=" * 60)
        print("💳 Inserire tessere sanitarie cittadini Rende")
        print("♻️ Per conferimento RAEE, oli esausti, vestiti")
        print("🔐 Controlli sicurezza attivi")
        print("🔄 Sincronizzazione automatica ogni 12h")
        print("📝 Audit log completo")
        print(f"🔌 Hardware: {hardware_status}")
        print("⏹️ Ctrl+C per fermare")
        print("=" * 60)
        
        try:
            self.running = True
            
            # Illuminazione area all'avvio
            if self.usb_relay_controller:
                self.usb_relay_controller.set_area_lighting(True)
                print("💡 Illuminazione area RAEE attivata")
            
            # Avvia CardReader
            self.card_reader.start_continuous_reading(self.handle_cf)
            
        except KeyboardInterrupt:
            print("\n⏹️ Arresto richiesto")
        except Exception as e:
            logger.error(f"\n❌ Errore: {e}")
            security_logger.critical(f"SYSTEM_ERROR - {e}")
        finally:
            self.shutdown()
        
        return True
    
    def shutdown(self):
        """Arresto sicuro sistema ISOLA RAEE"""
        print("\n🛑 Arresto sicuro ISOLA RAEE...")
        security_logger.info("SYSTEM_SHUTDOWN - Secure RAEE shutdown initiated")
        raee_logger.info("RAEE_SYSTEM_SHUTDOWN - Sistema spento")
        
        self.running = False
        
        if self.card_reader:
            self.card_reader.stop()
        
        if self.usb_relay_controller:
            print("🔌 Spegnimento USB-RLY08...")
            self.usb_relay_controller.emergency_stop()
            self.usb_relay_controller.disconnect()
        
        if self.odoo_connector:
            self.odoo_connector.disconnect()
        
        # Statistiche finali
        print(f"\n📊 STATISTICHE FINALI ISOLA RAEE:")
        print(f"   Accessi totali: {self.stats['total']}")
        print(f"   Autorizzati: {self.stats['authorized']}")
        print(f"   Negati: {self.stats['denied']}")
        print(f"   Sessioni RAEE: {self.stats['raee_sessions']}")
        print(f"   Sync completate: {self.stats['sync_operations']}")
        
        if self.last_sync_time:
            print(f"   Ultima sync: {self.last_sync_time.strftime('%H:%M:%S')}")
        
        security_logger.info(
            f"SYSTEM_SHUTDOWN_COMPLETE - Total: {self.stats['total']} - "
            f"Authorized: {self.stats['authorized']} - Denied: {self.stats['denied']} - "
            f"RAEE_Sessions: {self.stats['raee_sessions']}"
        )
        
        print("✅ Sistema ISOLA RAEE arrestato in sicurezza")

# Gestione segnali
system = None

def signal_handler(signum, frame):
    print(f"\n🛑 Segnale {signum}...")
    global system
    if system:
        system.running = False
    sys.exit(0)

def main():
    """Main applicazione ISOLA RAEE"""
    print("♻️ SISTEMA CONTROLLO ACCESSI ISOLA ECOLOGICA RAEE")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("💳 CardReader OMNIKEY 5427 CK ✅")
    print("🔗 Integrazione Odoo SICURA ✅")
    print("🏘️ Configurato per Comune di RENDE ✅")
    print("🔌 Hardware USB-RLY08 Controller ✅")
    print("♻️ ISOLA ECOLOGICA per RAEE, oli, vestiti ✅")
    print()
    
    # Signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        global system
        system = AccessControlSystem()
        
        if system.run():
            print("✅ Sistema ISOLA RAEE terminato OK")
            sys.exit(0)
        else:
            print("❌ Sistema terminato con errori")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"❌ Errore critico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
