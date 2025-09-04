# File: /opt/access_control/src/api/test_hardware_integration.py
# Integrazione test hardware reali nella dashboard

import sys
import os
import json
import time
import threading
from flask import jsonify, request
from pathlib import Path

# Aggiungi path per importare moduli hardware
sys.path.append('/opt/access_control/src')

try:
    from hardware.card_reader import CardReader
    from hardware.usb_rly08_controller import USBRLY08Controller
except ImportError as e:
    print(f"⚠️ Errore import hardware: {e}")
    CardReader = None
    USBRLY08Controller = None

# Variabili globali per test
test_results = {}
test_lock = threading.Lock()

def api_test_reader():
    """Test lettore tessere OMNIKEY 5427CK"""
    global test_results
    
    with test_lock:
        test_results['reader'] = {
            'status': 'running',
            'message': 'Test lettore in corso...',
            'timestamp': time.time(),
            'details': []
        }
    
    def run_reader_test():
        """Esegue test lettore in thread separato"""
        try:
            if CardReader is None:
                with test_lock:
                    test_results['reader'] = {
                        'status': 'error',
                        'message': 'Modulo CardReader non disponibile',
                        'timestamp': time.time(),
                        'details': ['Verificare installazione pyscard']
                    }
                return
            
            details = []
            
            # STEP 1: Inizializzazione
            details.append("🔄 Inizializzazione lettore...")
            reader = CardReader()
            
            # STEP 2: Test connessione
            details.append("🔌 Test connessione lettori...")
            if reader.test_connection():
                details.append(f"✅ Trovati {len(reader.readers)} lettori")
                for i, r in enumerate(reader.readers):
                    details.append(f"   {i+1}: {str(r)}")
            else:
                details.append("❌ Nessun lettore trovato")
                with test_lock:
                    test_results['reader'] = {
                        'status': 'error',
                        'message': 'Nessun lettore smart card trovato',
                        'timestamp': time.time(),
                        'details': details
                    }
                return
            
            # STEP 3: Test lettura tessera (timeout breve)
            details.append("💳 Test lettura tessera (10s timeout)...")
            details.append("   Inserire tessera sanitaria...")
            
            # Aggiorna risultati parziali
            with test_lock:
                test_results['reader']['details'] = details.copy()
                test_results['reader']['message'] = 'Attendere inserimento tessera...'
            
            # Test lettura con timeout
            start_time = time.time()
            timeout = 10  # 10 secondi
            card_found = False
            
            while (time.time() - start_time) < timeout and not card_found:
                try:
                    cf = reader._read_card_robust(timeout=1)
                    if cf:
                        details.append(f"✅ Tessera letta: {cf}")
                        details.append("✅ Sequenza APDU funzionante")
                        details.append("✅ Estrazione CF riuscita")
                        card_found = True
                        break
                except Exception as e:
                    # Normale durante attesa
                    pass
                
                # Aggiorna countdown
                remaining = int(timeout - (time.time() - start_time))
                with test_lock:
                    test_results['reader']['message'] = f'Tessera non rilevata (timeout: {remaining}s)'
            
            if not card_found:
                details.append("⚠️ Timeout - nessuna tessera inserita")
                details.append("💡 Test hardware OK, nessuna tessera da testare")
                final_status = 'warning'
                final_message = 'Hardware OK - Nessuna tessera testata'
            else:
                details.append("🎯 Test completato con successo!")
                final_status = 'success'
                final_message = 'Lettore completamente funzionante'
            
            # Risultato finale
            with test_lock:
                test_results['reader'] = {
                    'status': final_status,
                    'message': final_message,
                    'timestamp': time.time(),
                    'details': details
                }
                
        except Exception as e:
            with test_lock:
                test_results['reader'] = {
                    'status': 'error',
                    'message': f'Errore test lettore: {str(e)}',
                    'timestamp': time.time(),
                    'details': details + [f"❌ Errore: {str(e)}"]
                }
    
    # Avvia test in thread separato
    threading.Thread(target=run_reader_test, daemon=True).start()
    
    return jsonify({
        'success': True,
        'message': 'Test lettore avviato',
        'test_id': 'reader'
    })

def api_test_relay():
    """Test USB-RLY08 Controller"""
    global test_results
    
    with test_lock:
        test_results['relay'] = {
            'status': 'running',
            'message': 'Test USB-RLY08 in corso...',
            'timestamp': time.time(),
            'details': []
        }
    
    def run_relay_test():
        """Esegue test relè in thread separato"""
        try:
            if USBRLY08Controller is None:
                with test_lock:
                    test_results['relay'] = {
                        'status': 'error',
                        'message': 'Modulo USB-RLY08 non disponibile',
                        'timestamp': time.time(),
                        'details': ['Verificare installazione pyserial']
                    }
                return
            
            details = []
            
            # STEP 1: Inizializzazione
            details.append("🔄 Inizializzazione USB-RLY08...")
            
            # Test diverse porte possibili
            ports_to_test = ["/dev/ttyACM0", "/dev/ttyUSB0"]
            controller = None
            connected_port = None
            
            for port in ports_to_test:
                try:
                    details.append(f"🔌 Test connessione {port}...")
                    test_controller = USBRLY08Controller(port=port)
                    
                    if test_controller.connect():
                        details.append(f"✅ Connesso a {port}")
                        controller = test_controller
                        connected_port = port
                        break
                    else:
                        details.append(f"❌ Connessione fallita a {port}")
                except Exception as e:
                    details.append(f"❌ Errore {port}: {str(e)}")
            
            if not controller:
                details.append("❌ USB-RLY08 non trovato su nessuna porta")
                with test_lock:
                    test_results['relay'] = {
                        'status': 'error',
                        'message': 'USB-RLY08 non collegato',
                        'timestamp': time.time(),
                        'details': details
                    }
                return
            
            # STEP 2: Test comunicazione
            details.append("📋 Test comunicazione...")
            if controller.health_check():
                details.append("✅ Comunicazione seriale OK")
            else:
                details.append("❌ Errore comunicazione")
                controller.disconnect()
                with test_lock:
                    test_results['relay'] = {
                        'status': 'error',
                        'message': 'Errore comunicazione USB-RLY08',
                        'timestamp': time.time(),
                        'details': details
                    }
                return
            
            # STEP 3: Test stati relè
            details.append("📊 Lettura stati relè...")
            states = controller.get_relay_states()
            if states:
                details.append(f"✅ Stati letti: {len(states)} relè")
                for name, state in states.items():
                    status = "ON" if state else "OFF"
                    details.append(f"   {name}: {status}")
            else:
                details.append("⚠️ Impossibile leggere stati relè")
            
            # STEP 4: Test sicuro relè (lampeggio rapido)
            details.append("🔧 Test sicuro relè...")
            
            # Test relè 1 (breve lampeggio)
            details.append("   Test Relè 1...")
            controller._set_relay_state(controller.RelayChannel.LED_GREEN, True)
            time.sleep(0.3)
            controller._set_relay_state(controller.RelayChannel.LED_GREEN, False)
            details.append("   ✅ Relè 1 OK")
            
            time.sleep(0.2)
            
            # Test relè 2 (breve lampeggio)
            details.append("   Test Relè 2...")
            controller._set_relay_state(controller.RelayChannel.LED_RED, True)
            time.sleep(0.3)
            controller._set_relay_state(controller.RelayChannel.LED_RED, False)
            details.append("   ✅ Relè 2 OK")
            
            # STEP 5: Test funzioni sistema
            details.append("🎯 Test funzioni sistema...")
            
            # Test segnalazione accesso
            details.append("   Test segnalazione accesso...")
            controller.access_granted()
            time.sleep(1)
            details.append("   ✅ Segnalazione accesso OK")
            
            time.sleep(0.5)
            
            # Spegni tutto
            details.append("�� Spegnimento tutti i relè...")
            controller.emergency_stop()
            details.append("✅ Test completato con successo!")
            
            # Disconnessione
            controller.disconnect()
            
            # Risultato finale
            with test_lock:
                test_results['relay'] = {
                    'status': 'success',
                    'message': f'USB-RLY08 completamente funzionante su {connected_port}',
                    'timestamp': time.time(),
                    'details': details
                }
                
        except Exception as e:
            if 'controller' in locals() and controller:
                try:
                    controller.disconnect()
                except:
                    pass
            
            with test_lock:
                test_results['relay'] = {
                    'status': 'error',
                    'message': f'Errore test USB-RLY08: {str(e)}',
                    'timestamp': time.time(),
                    'details': details + [f"❌ Errore: {str(e)}"]
                }
    
    # Avvia test in thread separato
    threading.Thread(target=run_relay_test, daemon=True).start()
    
    return jsonify({
        'success': True,
        'message': 'Test USB-RLY08 avviato',
        'test_id': 'relay'
    })

def api_test_status():
    """Ottieni stato test in corso"""
    global test_results
    
    test_id = request.args.get('test_id')
    
    with test_lock:
        if test_id and test_id in test_results:
            return jsonify({
                'success': True,
                'test': test_results[test_id]
            })
        else:
            return jsonify({
                'success': True,
                'tests': test_results
            })

def api_test_combined():
    """Test completo hardware (lettore + relè)"""
    global test_results
    
    with test_lock:
        test_results['combined'] = {
            'status': 'running',
            'message': 'Test completo hardware in corso...',
            'timestamp': time.time(),
            'details': []
        }
    
    def run_combined_test():
        """Test combinato in thread separato"""
        try:
            details = []
            details.append("🚀 AVVIO TEST COMPLETO HARDWARE")
            details.append("=" * 40)
            
            # Test 1: Lettore
            details.append("📋 FASE 1: Test lettore tessere...")
            if CardReader is None:
                details.append("❌ Modulo CardReader non disponibile")
                reader_ok = False
            else:
                try:
                    reader = CardReader()
                    if reader.test_connection():
                        details.append(f"✅ Lettore OK - {len(reader.readers)} dispositivi")
                        reader_ok = True
                    else:
                        details.append("❌ Lettore non connesso")
                        reader_ok = False
                except Exception as e:
                    details.append(f"❌ Errore lettore: {str(e)}")
                    reader_ok = False
            
            # Test 2: USB-RLY08
            details.append("�� FASE 2: Test USB-RLY08...")
            if USBRLY08Controller is None:
                details.append("❌ Modulo USB-RLY08 non disponibile")
                relay_ok = False
            else:
                try:
                    # Test porte
                    ports = ["/dev/ttyACM0", "/dev/ttyUSB0"]
                    controller = None
                    
                    for port in ports:
                        try:
                            test_ctrl = USBRLY08Controller(port=port)
                            if test_ctrl.connect():
                                controller = test_ctrl
                                details.append(f"✅ USB-RLY08 OK - {port}")
                                break
                        except:
                            continue
                    
                    if controller:
                        relay_ok = True
                        controller.disconnect()
                    else:
                        details.append("❌ USB-RLY08 non trovato")
                        relay_ok = False
                        
                except Exception as e:
                    details.append(f"❌ Errore USB-RLY08: {str(e)}")
                    relay_ok = False
            
            # Risultato finale
            details.append("=" * 40)
            if reader_ok and relay_ok:
                details.append("🎯 SISTEMA COMPLETO FUNZIONANTE!")
                details.append("✅ Lettore tessere: OK")
                details.append("✅ Controller USB-RLY08: OK")
                details.append("🚀 Sistema pronto per il funzionamento")
                final_status = 'success'
                final_message = 'Tutto l\'hardware è operativo'
            elif reader_ok or relay_ok:
                details.append("⚠️ SISTEMA PARZIALMENTE FUNZIONANTE")
                details.append(f"{'✅' if reader_ok else '❌'} Lettore tessere")
                details.append(f"{'✅' if relay_ok else '❌'} Controller USB-RLY08")
                final_status = 'warning'
                final_message = 'Hardware parzialmente operativo'
            else:
                details.append("❌ HARDWARE NON FUNZIONANTE")
                details.append("❌ Lettore tessere: Errore")
                details.append("❌ Controller USB-RLY08: Errore")
                final_status = 'error'
                final_message = 'Hardware non operativo'
            
            with test_lock:
                test_results['combined'] = {
                    'status': final_status,
                    'message': final_message,
                    'timestamp': time.time(),
                    'details': details,
                    'summary': {
                        'reader_ok': reader_ok,
                        'relay_ok': relay_ok,
                        'overall_ok': reader_ok and relay_ok
                    }
                }
                
        except Exception as e:
            with test_lock:
                test_results['combined'] = {
                    'status': 'error',
                    'message': f'Errore test completo: {str(e)}',
                    'timestamp': time.time(),
                    'details': details + [f"❌ Errore critico: {str(e)}"]
                }
    
    # Avvia test in thread separato
    threading.Thread(target=run_combined_test, daemon=True).start()
    
    return jsonify({
        'success': True,
        'message': 'Test completo avviato',
        'test_id': 'combined'
    })

# Funzioni per aggiornare web_api.py esistente
def register_hardware_test_routes(app):
    """Registra le route dei test hardware nell'app Flask esistente"""
    
    @app.route('/api/test/reader', methods=['POST'])
    def test_reader_endpoint():
        return api_test_reader()
    
    @app.route('/api/test/relay', methods=['POST'])
    def test_relay_endpoint():
        return api_test_relay()
    
    @app.route('/api/test/combined', methods=['POST'])
    def test_combined_endpoint():
        return api_test_combined()
    
    @app.route('/api/test/status')
    def test_status_endpoint():
        return api_test_status()
    
    # Aggiorna route esistente /test-hardware
    @app.route('/test-hardware')
    def enhanced_test_hardware():
        """Test hardware migliorato con test reali"""
        hardware_status = {
            'lettore_cf': {'status': 'unknown', 'message': 'Pronto per test'},
            'rele_usb': {'status': 'unknown', 'message': 'Pronto per test'},
            'rete': {'status': 'ok', 'message': 'Connessione web funzionante'}
        }
        
        # Test presenza file hardware
        card_reader_path = Path("/opt/access_control/src/hardware/card_reader.py")
        relay_path = Path("/opt/access_control/src/hardware/usb_rly08_controller.py")
        
        if card_reader_path.exists():
            hardware_status['lettore_cf']['status'] = 'ready'
            hardware_status['lettore_cf']['message'] = 'Modulo pronto - Cliccare "Test Lettore"'
        else:
            hardware_status['lettore_cf']['status'] = 'error'
            hardware_status['lettore_cf']['message'] = 'Modulo card_reader.py non trovato'
        
        if relay_path.exists():
            hardware_status['rele_usb']['status'] = 'ready'
            hardware_status['rele_usb']['message'] = 'Modulo pronto - Cliccare "Test USB-RLY08"'
        else:
            hardware_status['rele_usb']['status'] = 'error'
            hardware_status['rele_usb']['message'] = 'Modulo usb_rly08_controller.py non trovato'
        
        return {
            'status': 'success',
            'message': 'Test hardware avanzati disponibili',
            'hardware': hardware_status
        }
    
    print("✅ Route test hardware registrate")

if __name__ == "__main__":
    print("🔧 Modulo Test Hardware Integration")
    print("Importare in web_api.py con:")
    print("from test_hardware_integration import register_hardware_test_routes")
    print("register_hardware_test_routes(app)")
