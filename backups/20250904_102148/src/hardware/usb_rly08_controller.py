# File: /opt/access_control/src/hardware/usb_rly08_controller.py
# Controller USB-RLY08 per sistema controllo accessi

import serial
import time
import logging
import threading
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)

class RelayChannel(Enum):
    """Mapping canali relè per funzionalità specifiche"""
    LED_GREEN = 1      # LED Verde - Accesso autorizzato
    LED_RED = 2        # LED Rosso - Accesso negato
    BUZZER = 3         # Buzzer - Segnalazioni acustiche
    GATE_MOTOR = 4     # Motore cancello - Apertura/Chiusura
    MAGNETIC_LOCK = 5  # Blocco elettromagnetico
    AREA_LIGHT = 6     # Illuminazione area RAEE
    SPARE_1 = 7        # Relè di riserva 1
    SPARE_2 = 8        # Relè di riserva 2

class USBRLY08Controller:
    """Controller USB-RLY08 per sistema controllo accessi RAEE"""
    
    def __init__(self, port: str = "/dev/ttyACM0", baudrate: int = 19200, device_path: Optional[str] = None, baud_rate: Optional[int] = None):
        # Supporto per parametri alternativi (device_path/baud_rate)
        self.port = device_path if device_path is not None else port
        self.baudrate = baud_rate if baud_rate is not None else baudrate
        self.serial_connection = None
        self.is_connected = False
        self.last_state = 0
        
        # Lock per thread safety
        self._lock = threading.Lock()
        
        # Configurazione relè
        self.relay_config = {
            RelayChannel.LED_GREEN: {"name": "LED Verde", "auto_off_delay": 3.0},
            RelayChannel.LED_RED: {"name": "LED Rosso", "auto_off_delay": 3.0},
            RelayChannel.BUZZER: {"name": "Buzzer", "auto_off_delay": 0.5},
            RelayChannel.GATE_MOTOR: {"name": "Motore Cancello", "auto_off_delay": 5.0},
            RelayChannel.MAGNETIC_LOCK: {"name": "Blocco Magnetico", "auto_off_delay": None},
            RelayChannel.AREA_LIGHT: {"name": "Illuminazione", "auto_off_delay": None}
        }
        
        # Timer per auto-spegnimento
        self.auto_off_timers = {}
        
        logger.info("🔧 USBRelay08Controller inizializzato")
    
    def connect(self) -> bool:
        """Stabilisce connessione con USB-RLY08"""
        try:
            with self._lock:
                if self.is_connected:
                    return True
                
                logger.info(f"🔌 Connessione a USB-RLY08 su {self.port}...")
                
                self.serial_connection = serial.Serial(
                    port=self.port,
                    baudrate=self.baudrate,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_TWO,
                    timeout=2
                )
                
                time.sleep(0.5)  # Stabilizzazione
                
                # Test connessione - Get software version
                self.serial_connection.write(bytes([90]))  # 0x5A
                time.sleep(0.1)
                response = self.serial_connection.read(2)
                
                if len(response) == 2 and response[0] == 8:
                    module_id = response[0]
                    sw_version = response[1]
                    logger.info(f"✅ USB-RLY08 connesso - ID: {module_id}, SW: {sw_version}")
                    
                    # Spegni tutti i relè all'avvio
                    self._all_relays_off()
                    
                    self.is_connected = True
                    return True
                else:
                    logger.error(f"❌ Risposta modulo inaspettata: {response}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Errore connessione USB-RLY08: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Disconnessione sicura"""
        try:
            with self._lock:
                if self.is_connected and self.serial_connection:
                    # Spegni tutti i relè prima di disconnettere
                    self._all_relays_off()
                    self.serial_connection.close()
                    
                self.is_connected = False
                self.serial_connection = None
                
                # Cancella timer attivi
                for timer in self.auto_off_timers.values():
                    timer.cancel()
                self.auto_off_timers.clear()
                
                logger.info("🔌 USB-RLY08 disconnesso")
        except Exception as e:
            logger.error(f"❌ Errore disconnessione: {e}")
    
    def _send_command(self, command: int) -> bool:
        """Invia comando al modulo"""
        try:
            if not self.is_connected or not self.serial_connection:
                logger.warning("⚠️ USB-RLY08 non connesso")
                return False
            
            self.serial_connection.write(bytes([command]))
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore invio comando {command}: {e}")
            return False
    
    def _all_relays_off(self):
        """Spegne tutti i relè"""
        self._send_command(110)  # 0x6E - All relays OFF
        self.last_state = 0
        logger.debug("💡 Tutti i relè spenti")
    
    def _set_relay_state(self, channel: RelayChannel, state: bool) -> bool:
        """Imposta stato singolo relè"""
        try:
            with self._lock:
                if not self.is_connected:
                    logger.warning(f"⚠️ Cannot control {channel.name} - USB-RLY08 not connected")
                    return False
                
                relay_num = channel.value
                config = self.relay_config.get(channel, {})
                relay_name = config.get("name", f"Relè {relay_num}")
                
                if state:
                    # Accendi relè (comandi 101-108)
                    command = 100 + relay_num
                    self._send_command(command)
                    
                    # Aggiorna stato locale
                    self.last_state |= (1 << (relay_num - 1))
                    
                    logger.info(f"🔆 {relay_name} ACCESO")
                    
                    # Auto-spegnimento se configurato
                    auto_off_delay = config.get("auto_off_delay")
                    if auto_off_delay is not None:
                        self._schedule_auto_off(channel, auto_off_delay)
                        
                else:
                    # Spegni relè (comandi 111-118)
                    command = 110 + relay_num
                    self._send_command(command)
                    
                    # Aggiorna stato locale
                    self.last_state &= ~(1 << (relay_num - 1))
                    
                    logger.info(f"💡 {relay_name} SPENTO")
                    
                    # Cancella timer auto-off se presente
                    if channel in self.auto_off_timers:
                        self.auto_off_timers[channel].cancel()
                        del self.auto_off_timers[channel]
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Errore controllo {channel.name}: {e}")
            return False
    
    def _schedule_auto_off(self, channel: RelayChannel, delay: float):
        """Programma spegnimento automatico"""
        # Cancella timer precedente se esiste
        if channel in self.auto_off_timers:
            self.auto_off_timers[channel].cancel()
        
        # Programma nuovo timer
        timer = threading.Timer(delay, lambda: self._set_relay_state(channel, False))
        timer.start()
        self.auto_off_timers[channel] = timer
        
        logger.debug(f"⏰ Auto-off programmato per {channel.name} in {delay}s")
    
    # ===== INTERFACCIA PUBBLICA CONTROLLO ACCESSI =====
    
    def access_granted(self):
        """Segnala accesso autorizzato"""
        logger.info("✅ ACCESSO AUTORIZZATO")
        
        # LED Verde ON (auto-off 3s)
        self._set_relay_state(RelayChannel.LED_GREEN, True)
        
        # Buzzer breve (auto-off 500ms)
        self._set_relay_state(RelayChannel.BUZZER, True)
    
    def access_denied(self):
        """Segnala accesso negato"""
        logger.info("❌ ACCESSO NEGATO")
        
        # LED Rosso ON (auto-off 3s)
        self._set_relay_state(RelayChannel.LED_RED, True)
        
        # Pattern buzzer: 3 beep
        self._buzzer_pattern_denied()
    
    def _buzzer_pattern_denied(self):
        """Pattern buzzer per accesso negato (3 beep)"""
        def beep_sequence():
            for i in range(3):
                self._set_relay_state(RelayChannel.BUZZER, True)
                time.sleep(0.2)
                self._set_relay_state(RelayChannel.BUZZER, False)
                time.sleep(0.3)
        
        # Esegui in thread separato per non bloccare
        threading.Thread(target=beep_sequence, daemon=True).start()
    
    def open_gate(self, duration: float = 5.0):
        """Apre cancello per durata specificata"""
        logger.info(f"🚪 APERTURA CANCELLO per {duration}s")
        
        # Disattiva blocco magnetico
        self._set_relay_state(RelayChannel.MAGNETIC_LOCK, False)
        
        # Attiva motore cancello (auto-off dopo duration)
        config = self.relay_config[RelayChannel.GATE_MOTOR]
        config["auto_off_delay"] = duration
        self._set_relay_state(RelayChannel.GATE_MOTOR, True)
        
        # Riattiva blocco dopo apertura + 1s di sicurezza
        def relock():
            time.sleep(duration + 1.0)
            self._set_relay_state(RelayChannel.MAGNETIC_LOCK, True)
            logger.info("🔒 Blocco magnetico riattivato")
        
        threading.Thread(target=relock, daemon=True).start()
    
    def processing(self, active: bool):
        """Segnala elaborazione in corso"""
        if active:
            logger.info("🟡 ELABORAZIONE IN CORSO...")
            # Illuminazione area durante elaborazione
            self._set_relay_state(RelayChannel.AREA_LIGHT, True)
        else:
            logger.info("💡 Elaborazione completata")
            # Spegni illuminazione area
            self._set_relay_state(RelayChannel.AREA_LIGHT, False)
    
    def emergency_stop(self):
        """Stop di emergenza - spegne tutto"""
        logger.critical("🚨 EMERGENCY STOP - Spegnimento tutti i relè")
        
        with self._lock:
            # Cancella tutti i timer
            for timer in self.auto_off_timers.values():
                timer.cancel()
            self.auto_off_timers.clear()
            
            # Spegni tutti i relè
            self._all_relays_off()
    
    def set_area_lighting(self, state: bool):
        """Controllo illuminazione area RAEE"""
        action = "ACCESA" if state else "SPENTA"
        logger.info(f"💡 Illuminazione area RAEE {action}")
        self._set_relay_state(RelayChannel.AREA_LIGHT, state)
    
    def get_relay_states(self) -> Dict[str, bool]:
        """Ottieni stato attuale di tutti i relè"""
        try:
            with self._lock:
                if not self.is_connected:
                    return {}
                
                # Richiedi stato dal modulo
                self._send_command(91)  # 0x5B - Get relay states
                time.sleep(0.1)
                response = self.serial_connection.read(1)
                
                if len(response) == 1:
                    current_state = response[0]
                    self.last_state = current_state
                    
                    # Decodifica stato per ogni canale
                    states = {}
                    for channel in RelayChannel:
                        bit_position = channel.value - 1
                        is_on = bool(current_state & (1 << bit_position))
                        config = self.relay_config.get(channel, {})
                        name = config.get("name", f"Relè {channel.value}")
                        states[name] = is_on
                    
                    return states
                
                return {}
                
        except Exception as e:
            logger.error(f"❌ Errore lettura stati relè: {e}")
            return {}
    
    def health_check(self) -> bool:
        """Verifica salute del modulo"""
        try:
            if not self.is_connected:
                return self.connect()
            
            # Test comunicazione
            self._send_command(90)  # Get version
            time.sleep(0.1)
            response = self.serial_connection.read(2)
            
            return len(response) == 2 and response[0] == 8
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

# Alias per compatibilità
USBRelay08Controller = USBRLY08Controller

# Compatibilità con MockRelay esistente
class RelayController:
    """Alias per compatibilità con il sistema esistente"""
    
    def __init__(self, port: str = "/dev/ttyACM0", baudrate: int = 19200):
        self.usb_relay = USBRLY08Controller(port, baudrate)
        self.usb_relay.connect()
    
    def open_gate(self, duration: float = 5.0):
        """Compatibilità con interfaccia MockRelay"""
        self.usb_relay.open_gate(duration)
    
    def disconnect(self):
        """Disconnessione"""
        self.usb_relay.disconnect()

# Test del controller
if __name__ == "__main__":
    import signal
    import sys
    
    def signal_handler(signum, frame):
        print(f"\n🛑 Arresto test...")
        if 'controller' in globals():
            controller.emergency_stop()
            controller.disconnect()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🔧 TEST CONTROLLER USB-RLY08")
    print("=" * 50)
    
    # Setup logging per test
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        controller = USBRLY08Controller()
        
        if controller.connect():
            print("✅ Controller connesso")
            
            # Test sequenza controllo accessi
            print("\n🧪 Test sequenza controllo accessi...")
            
            print("1. Elaborazione...")
            controller.processing(True)
            time.sleep(2)
            
            print("2. Accesso autorizzato...")
            controller.processing(False)
            controller.access_granted()
            time.sleep(1)
            
            print("3. Apertura cancello...")
            controller.open_gate(3)
            time.sleep(4)
            
            print("4. Test accesso negato...")
            controller.access_denied()
            time.sleep(3)
            
            print("5. Illuminazione area...")
            controller.set_area_lighting(True)
            time.sleep(2)
            controller.set_area_lighting(False)
            
            # Mostra stati finali
            print("\n📊 Stati finali relè:")
            states = controller.get_relay_states()
            for name, state in states.items():
                print(f"   {name}: {'ON' if state else 'OFF'}")
            
            print("\n✅ Test completato")
            
        else:
            print("❌ Impossibile connettersi al controller")
    
    except Exception as e:
        print(f"❌ Errore: {e}")
    
    finally:
        if 'controller' in locals():
            controller.disconnect()
