# File: /opt/access_control/src/api/hardware_tests.py
# Endpoint per test hardware

from flask import jsonify
import time
import threading
from datetime import datetime
import sys
sys.path.insert(0, '/opt/access_control/src')

# Stato globale per test
relay_test_state = {'status': 'idle'}
integrated_test_state = {'status': 'idle'}
hardware_test_results = {}
hardware_test_lock = threading.Lock()

# Import hardware con gestione errori
try:
    from hardware.card_reader import CardReader
    HARDWARE_READER_OK = True
except:
    HARDWARE_READER_OK = False

try:
    from hardware.usb_rly08_controller import USBRLY08Controller  
    HARDWARE_RELAY_OK = True
except:
    HARDWARE_RELAY_OK = False

def test_gate(get_db_connection):
    """Test cancello semplice"""
    try:
        controller = USBRLY08Controller()
        if controller.connect():
            # Apri cancello per 5 secondi
            controller._send_command(101)  # Relay 1 ON (Cancello)
            time.sleep(5)
            controller._send_command(111)  # Relay 1 OFF
            controller.disconnect()
            return jsonify({'success': True, 'message': 'Cancello aperto per test'})
        else:
            return jsonify({'success': False, 'error': 'Impossibile connettersi al controller'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Errore test cancello: {str(e)}'})

def test_relay():
    """Test USB-RLY08 con feedback real-time"""
    try:
        # Reset stato test globale
        global relay_test_state
        relay_test_state = {
            'status': 'running',
            'current_relay': 0,
            'log': [],
            'relay_states': {i: False for i in range(1, 9)}
        }
        
        def run_relay_test():
            global relay_test_state
            controller = USBRLY08Controller()
            
            relay_test_state['log'].append("=== TEST USB-RLY08 ===")
            relay_test_state['log'].append(f"Porta: {controller.port}")
            
            if not controller.connect():
                relay_test_state['log'].append("✗ Impossibile connettersi")
                relay_test_state['status'] = 'error'
                return
            
            relay_test_state['log'].append("✓ Connessione stabilita")
            
            # Test sequenziale di ogni relè
            for i in range(1, 9):
                relay_test_state['current_relay'] = i
                relay_test_state['log'].append(f"\nTest Relè {i}:")
                
                # Accendi relè - comando diretto
                command_on = 100 + i  # Comandi 101-108 per ON
                if controller._send_command(command_on):
                    relay_test_state['relay_states'][i] = True
                    relay_test_state['log'].append(f"  ✓ Relè {i} acceso")
                    time.sleep(0.5)
                    
                    # Spegni relè - comando diretto
                    command_off = 110 + i  # Comandi 111-118 per OFF
                    if controller._send_command(command_off):
                        relay_test_state['relay_states'][i] = False
                        relay_test_state['log'].append(f"  ✓ Relè {i} spento")
                
                time.sleep(0.5)
            
            # Test pattern finale - accendi tutti
            relay_test_state['log'].append("\nTest pattern finale...")
            controller._send_command(100)  # All ON
            for i in range(1, 9):
                relay_test_state['relay_states'][i] = True
            time.sleep(1)
            
            # Spegni tutti
            controller._send_command(110)  # All OFF
            for i in range(1, 9):
                relay_test_state['relay_states'][i] = False
            
            controller.disconnect()
            relay_test_state['log'].append("\n✓ Test completato!")
            relay_test_state['status'] = 'completed'
            relay_test_state['current_relay'] = 0
        
        # Avvia test in thread separato
        test_thread = threading.Thread(target=run_relay_test)
        test_thread.daemon = True
        test_thread.start()
        
        return jsonify({'success': True, 'message': 'Test avviato'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def test_integrated(get_db_connection):
    """Test integrato REALE: lettura tessera fisica e azioni conseguenti"""
    try:
        # Reset stato test globale
        global integrated_test_state
        integrated_test_state = {
            'status': 'running',
            'phase': 'init',
            'log': [],
            'cf': None,
            'authorized': None,
            'user_name': None,
            'timeout': 60  # 60 secondi di timeout
        }
        
        def run_integrated_test():
            global integrated_test_state
            controller = None
            reader = None
            
            try:
                # FASE 1: Inizializzazione hardware
                integrated_test_state['phase'] = 'connecting'
                integrated_test_state['log'].append("🔄 AVVIO TEST INTEGRATO ACCESSO REALE")
                integrated_test_state['log'].append("━" * 50)
                integrated_test_state['log'].append("📡 Connessione hardware...")
                
                # Connetti USB-RLY08
                controller = USBRLY08Controller()
                if not controller.connect():
                    integrated_test_state['log'].append("❌ Errore connessione USB-RLY08")
                    integrated_test_state['status'] = 'error'
                    return
                
                integrated_test_state['log'].append("✅ USB-RLY08 connesso")
                
                # Inizializza lettore tessere
                reader = CardReader()
                if not reader.test_connection():
                    integrated_test_state['log'].append("❌ Errore connessione lettore OMNIKEY")
                    integrated_test_state['status'] = 'error'
                    return
                
                integrated_test_state['log'].append("✅ Lettore OMNIKEY connesso")
                time.sleep(0.5)
                
                # FASE 2: Attesa tessera REALE
                integrated_test_state['phase'] = 'waiting_card'
                integrated_test_state['log'].append("\n💳 INSERIRE TESSERA SANITARIA NEL LETTORE...")
                integrated_test_state['log'].append("⏱️ Timeout: 60 secondi")
                
                # LED giallo lampeggiante (attesa)
                start_time = time.time()
                cf = None
                
                while (time.time() - start_time) < integrated_test_state['timeout']:
                    # Lampeggio LED giallo
                    controller._send_command(104)  # Relay 4 ON (LED Giallo)
                    time.sleep(0.3)
                    controller._send_command(114)  # Relay 4 OFF
                    time.sleep(0.3)
                    
                    # Prova a leggere tessera
                    try:
                        cf = reader._read_card_robust(timeout=0.5)
                        if cf and len(cf) == 16:
                            break
                    except:
                        pass
                
                if not cf:
                    integrated_test_state['phase'] = 'timeout'
                    integrated_test_state['log'].append("\n⏱️ TIMEOUT - Nessuna tessera rilevata")
                    integrated_test_state['status'] = 'completed'
                    return
                
                # FASE 3: Tessera rilevata!
                integrated_test_state['phase'] = 'reading_card'
                integrated_test_state['log'].append(f"\n🎯 TESSERA RILEVATA!")
                integrated_test_state['log'].append(f"📄 Codice Fiscale: {cf}")
                integrated_test_state['cf'] = cf
                
                # Spegni LED giallo
                controller._send_command(114)
                
                # FASE 4: Verifica autorizzazione nel database
                integrated_test_state['log'].append("🔍 Verifica autorizzazione nel database...")
                time.sleep(0.5)
                
                conn = get_db_connection()
                authorized = False
                user_name = "Sconosciuto"
                
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT nome, attivo 
                        FROM utenti_autorizzati 
                        WHERE codice_fiscale = ?
                    """, (cf,))
                    user = cursor.fetchone()
                    
                    if user:
                        nome = user[0] or "Utente"
                        attivo = user[1]
                        user_name = nome
                        authorized = bool(attivo)
                        
                        if not authorized:
                            integrated_test_state['log'].append(f"⚠️ Utente disattivato: {user_name}")
                    else:
                        integrated_test_state['log'].append("❓ Codice fiscale non trovato nel database")
                    
                    conn.close()
                
                integrated_test_state['authorized'] = authorized
                integrated_test_state['user_name'] = user_name
                
                # FASE 5: Esegui azioni in base all'autorizzazione
                if authorized:
                    integrated_test_state['phase'] = 'access_granted'
                    integrated_test_state['log'].append(f"\n✅ ACCESSO AUTORIZZATO")
                    integrated_test_state['log'].append(f"👤 Utente: {user_name}")
                    integrated_test_state['log'].append("🚪 Apertura cancello...")
                    
                    # Sequenza accesso autorizzato
                    controller._send_command(103)  # LED Verde ON
                    controller._send_command(105)  # Buzzer ON
                    time.sleep(0.2)
                    controller._send_command(115)  # Buzzer OFF
                    time.sleep(0.3)
                    
                    # Apri cancello
                    controller._send_command(101)  # Cancello ON
                    integrated_test_state['log'].append("✅ Cancello APERTO (8 secondi)")
                    
                    # Attendi 8 secondi (tempo reale apertura)
                    time.sleep(8)
                    
                    # Chiudi cancello
                    controller._send_command(111)  # Cancello OFF
                    integrated_test_state['log'].append("🔒 Cancello CHIUSO")
                    
                    time.sleep(1)
                    controller._send_command(113)  # LED Verde OFF
                    
                else:
                    integrated_test_state['phase'] = 'access_denied'
                    integrated_test_state['log'].append(f"\n❌ ACCESSO NEGATO")
                    integrated_test_state['log'].append(f"👤 Utente: {user_name}")
                    if user_name == "Sconosciuto":
                        integrated_test_state['log'].append("�� Tessera non registrata nel sistema")
                    else:
                        integrated_test_state['log'].append("🚫 Utente non autorizzato")
                    
                    # Sequenza accesso negato
                    controller._send_command(102)  # LED Rosso ON
                    
                    # Pattern buzzer negato (3 beep)
                    for i in range(3):
                        controller._send_command(105)  # Buzzer ON
                        time.sleep(0.1)
                        controller._send_command(115)  # Buzzer OFF
                        time.sleep(0.2)
                    
                    time.sleep(2)
                    controller._send_command(112)  # LED Rosso OFF
                
                # FASE 6: Log nel database
                integrated_test_state['phase'] = 'logging'
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO log_accessi (codice_fiscale, timestamp, autorizzato) 
                        VALUES (?, ?, ?)
                    """, (cf, datetime.now(), 1 if authorized else 0))
                    conn.commit()
                    conn.close()
                    integrated_test_state['log'].append("\n📝 Accesso registrato nel database")
                
                # FASE 7: Completamento
                integrated_test_state['phase'] = 'completed'
                integrated_test_state['log'].append("\n━" * 50)
                integrated_test_state['log'].append("✅ TEST COMPLETATO")
                integrated_test_state['log'].append("💡 Puoi rimuovere la tessera")
                
            except Exception as e:
                integrated_test_state['log'].append(f"\n❌ ERRORE: {str(e)}")
                integrated_test_state['status'] = 'error'
                integrated_test_state['phase'] = 'error'
            finally:
                # Cleanup
                if controller:
                    # Spegni tutti i LED
                    controller._send_command(110)  # All OFF
                    controller.disconnect()
                integrated_test_state['status'] = 'completed'
        
        # Avvia test in thread separato
        test_thread = threading.Thread(target=run_integrated_test)
        test_thread.daemon = True
        test_thread.start()
        
        return jsonify({'success': True, 'message': 'Test integrato avviato - inserire tessera'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def test_reader():
    """Test hardware lettore tessere - Solo monitoraggio database"""

    def test_reader_thread():
        global hardware_test_results

        # Reset risultati
        with hardware_test_lock:
            hardware_test_results['reader'] = {
                'status': 'running',
                'message': 'Inizializzazione...',
                'details': [],
                'timestamp': time.time()
            }

        try:
            details = []

            # SOLO MONITOR DATABASE - NON TOCCA IL LETTORE HARDWARE
            details.append("📊 MONITOR DATABASE ATTIVO")
            details.append("ℹ️ Il lettore hardware NON viene toccato")
            details.append("✅ Sistema principale resta operativo")
            details.append("💳 IN ATTESA TESSERA SANITARIA...")
            details.append("━" * 50)
            
            # Aggiorna stato iniziale
            with hardware_test_lock:
                hardware_test_results['reader']['details'] = details.copy()
                hardware_test_results['reader']['message'] = 'In attesa tessera...'
            
            # Loop principale - 60 secondi
            timeout = 60
            start_time = time.time()
            cards_read = 0
            last_access_id = 0
            
            # Ottieni ultimo ID dal database per monitoraggio
            import sqlite3
            db_path = '/opt/access_control/src/access.db'
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(id) FROM log_accessi")
                result = cursor.fetchone()
                last_access_id = result[0] if result and result[0] else 0
                conn.close()
                details.append(f"📍 Monitoraggio database da ID: {last_access_id + 1}")
            except:
                last_access_id = 0
            
            while (time.time() - start_time) < timeout:
                # Controlla se il test è stato fermato
                with hardware_test_lock:
                    if hardware_test_results.get('reader', {}).get('status') == 'stopped':
                        details.append("")
                        details.append("⏹️ TEST FERMATO DALL'UTENTE")
                        break
                
                try:
                    # Monitora database invece di leggere direttamente
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT id, codice_fiscale, autorizzato, motivo_rifiuto, nome_utente 
                        FROM log_accessi 
                        WHERE id > ? 
                        ORDER BY id
                    """, (last_access_id,))
                    new_accesses = cursor.fetchall()
                    
                    for access_id, cf, autorizzato, motivo_rifiuto, nome_utente in new_accesses:
                        if access_id > last_access_id:
                            # NUOVA TESSERA DAL DATABASE!
                            last_access_id = access_id
                            cards_read += 1
                            read_time = datetime.now().strftime('%H:%M:%S')
                            
                            # Log dettagliato per questa tessera
                            details.append(f"")
                            details.append(f"🎯 [{read_time}] TESSERA RILEVATA #{cards_read}")
                            details.append(f"📄 Codice Fiscale: {cf}")
                            
                            # Mostra nome utente se disponibile
                            if nome_utente:
                                details.append(f"👤 Utente: {nome_utente}")
                            
                            # Mostra stato autorizzazione con motivazione dal database
                            if autorizzato:
                                details.append(f"✅ ACCESSO AUTORIZZATO")
                            else:
                                details.append(f"❌ ACCESSO NEGATO")
                                # Mostra il motivo del rifiuto se disponibile
                                if motivo_rifiuto:
                                    details.append(f"📝 Motivo: {motivo_rifiuto}")
                            
                            details.append(f"✅ Log salvato nel database")
                            details.append("━" * 50)
                    
                    conn.close()
                    
                    # Aggiorna risultati dopo ogni check
                    if cards_read > 0:
                        with hardware_test_lock:
                            hardware_test_results['reader']['details'] = details.copy()
                            hardware_test_results['reader']['message'] = f'Tessere lette: {cards_read}'
                        
                except Exception as e:
                    # Ignora errori temporanei
                    pass
                
                time.sleep(0.1)  # Check veloce
            
            # Fine test
            details.append("")
            details.append("⏱️ TEST COMPLETATO")
            details.append(f"📊 Tessere lette: {cards_read}")
            details.append(f"⏱️ Durata: {int(time.time() - start_time)} secondi")
            
            with hardware_test_lock:
                hardware_test_results['reader'] = {
                    'status': 'success' if cards_read > 0 else 'warning',
                    'message': f'Test completato - {cards_read} tessere lette',
                    'details': details,
                    'timestamp': time.time()
                }
                
        except Exception as e:
            details.append(f"❌ ERRORE: {str(e)}")
            with hardware_test_lock:
                hardware_test_results['reader'] = {
                    'status': 'error',
                    'message': f'Errore: {str(e)}',
                    'details': details,
                    'timestamp': time.time()
                }
    
    # Avvia test in background
    threading.Thread(target=test_reader_thread, daemon=True).start()
    return jsonify({'success': True, 'message': 'Test lettore avviato'})

def stop_reader():
    """Ferma il test del lettore"""
    global hardware_test_results
    
    with hardware_test_lock:
        if 'reader' in hardware_test_results and hardware_test_results['reader'].get('status') == 'running':
            hardware_test_results['reader']['status'] = 'stopped'
            hardware_test_results['reader']['message'] = 'Test fermato dall\'utente'
            return jsonify({'success': True, 'message': 'Test lettore fermato'})
        else:
            return jsonify({'success': False, 'message': 'Nessun test in esecuzione'})

# Funzioni di stato
def get_relay_status():
    """Restituisce stato test relay"""
    global relay_test_state
    return jsonify(relay_test_state)

def get_integrated_status():
    """Restituisce stato test integrato"""
    global integrated_test_state
    return jsonify(integrated_test_state)

def get_hardware_status(test_id=None):
    """Restituisce stato test hardware"""
    with hardware_test_lock:
        if test_id and test_id in hardware_test_results:
            return jsonify({'success': True, 'test': hardware_test_results[test_id]})
        return jsonify({'success': True, 'tests': hardware_test_results})
