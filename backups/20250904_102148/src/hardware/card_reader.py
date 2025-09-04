# File: /opt/access_control/src/hardware/card_reader.py
# LETTORE TESSERA SANITARIA * OMNIKEY 5427 G2
import time
import logging
import re
from typing import Optional
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.CardRequest import CardRequest
from smartcard.CardType import AnyCardType
from smartcard.Exceptions import CardRequestTimeoutException, NoCardException

logger = logging.getLogger(__name__)

class CardReader:
    """LETTORE TESSERA SANITARIA ROBUSTO - Retry automatici e gestione errori"""
    
    def __init__(self, device_path=None, reader_type=None):
        self.readers = []
        self.running = False
        self.last_cf = None
        self.debug = False  # Ridotto logging per prestazioni
        self.device_path = device_path  # Supporto per device_path specifico
        self.reader_type = reader_type  # Supporto per tipo lettore specifico
        
        # Configurazione retry
        self.max_retries = 3
        self.retry_delay = 0.5
        self.read_timeout = 3
        
        # Cache per evitare letture duplicate
        self.last_read_time = 0
        self.duplicate_threshold = 1.0  # Secondi
        
        self.init_readers()
        logger.info("💳 CardReader ROBUSTO inizializzato")
    
    def init_readers(self):
        """Inizializza lettori smart card"""
        try:
            self.readers = readers()
            if not self.readers:
                raise Exception("Nessun lettore smart card trovato")
            
            logger.info(f"📱 Lettori trovati: {len(self.readers)}")
            for i, reader in enumerate(self.readers):
                logger.info(f"  {i}: {reader}")
                
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione lettori: {e}")
            raise
    
    def start_continuous_reading(self, callback=None):
        """Avvia lettura continua ROBUSTA con retry automatici"""
        self.running = True
        logger.info("🚀 AVVIO LETTURA CONTINUA ROBUSTA")
        logger.info("💳 Inserire tessere sanitarie...")
        
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.running:
            try:
                # Attendi tessera con timeout breve
                cf = self._read_card_robust(timeout=2)
                
                if cf:
                    # CF letto con successo
                    current_time = time.time()
                    
                    # Evita duplicati ravvicinati
                    if (current_time - self.last_read_time) < self.duplicate_threshold and cf == self.last_cf:
                        if self.debug:
                            logger.debug(f"🔄 CF duplicato ignorato: {cf}")
                        continue
                    
                    # Nuovo CF valido
                    logger.info(f"🎯 CODICE FISCALE: {cf}")
                    self.last_cf = cf
                    self.last_read_time = current_time
                    consecutive_errors = 0  # Reset errori
                    
                    # Chiama callback
                    if callback:
                        try:
                            callback(cf)
                        except Exception as e:
                            logger.error(f"❌ Errore callback: {e}")
                    
                    # Attendi rimozione tessera ROBUSTA
                    self._wait_card_removal_robust()
                
                else:
                    # Nessun CF letto - normale se nessuna tessera
                    consecutive_errors = 0
                
                # Breve pausa per CPU
                time.sleep(0.2)
                
            except KeyboardInterrupt:
                logger.info("⏹️ Interruzione richiesta")
                break
            except Exception as e:
                consecutive_errors += 1
                
                if consecutive_errors <= max_consecutive_errors:
                    if self.debug:
                        logger.debug(f"⚠️ Errore {consecutive_errors}/{max_consecutive_errors}: {e}")
                else:
                    logger.error(f"❌ Troppi errori consecutivi: {e}")
                
                # Pausa più lunga dopo errori
                time.sleep(1)
        
        self.running = False
        logger.info("🛑 Lettura continua FERMATA")
    
    def _read_card_robust(self, timeout=3) -> Optional[str]:
        """Lettura tessera ROBUSTA con retry automatici"""
        
        for attempt in range(self.max_retries):
            try:
                # Attendi tessera
                cardrequest = CardRequest(timeout=timeout, cardType=AnyCardType())
                cardservice = cardrequest.waitforcard()
                
                if not cardservice:
                    return None
                
                # Connetti con retry
                connection_success = False
                for conn_attempt in range(2):
                    try:
                        cardservice.connection.connect()
                        connection_success = True
                        break
                    except Exception as e:
                        if conn_attempt == 0:
                            time.sleep(0.2)
                            continue
                        else:
                            raise e
                
                if not connection_success:
                    continue
                
                # Leggi ATR
                atr = cardservice.connection.getATR()
                atr_hex = toHexString(atr).replace(" ", "")
                
                if self.debug:
                    logger.debug(f"ATR: {atr_hex}")
                
                # SEQUENZA APDU ROBUSTA con retry
                cf = self._read_apdu_robust(cardservice.connection)
                
                # Disconnetti sempre
                try:
                    cardservice.connection.disconnect()
                except:
                    pass
                
                if cf:
                    return cf
                
                # Se non ha letto CF, retry
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                
            except CardRequestTimeoutException:
                # Normale - nessuna tessera
                return None
            except Exception as e:
                if self.debug:
                    logger.debug(f"⚠️ Errore tentativo {attempt + 1}: {e}")
                
                # Retry con pausa crescente
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
        
        # Tutti i tentativi falliti
        return None
    
    def _read_apdu_robust(self, connection) -> Optional[str]:
        """Sequenza APDU ROBUSTA con error handling"""
        
        try:
            # STEP 1: SELECT MF con retry
            for retry in range(2):
                try:
                    response, sw1, sw2 = connection.transmit([0x00, 0xA4, 0x00, 0x00, 0x02, 0x3F, 0x00])
                    if sw1 == 0x90 and sw2 == 0x00:
                        break
                    elif retry == 0:
                        time.sleep(0.1)
                        continue
                    else:
                        raise Exception(f"SELECT MF failed: {sw1:02X}{sw2:02X}")
                except Exception as e:
                    if retry == 0:
                        time.sleep(0.1)
                        continue
                    else:
                        raise e
            
            # STEP 2: SELECT DF1 con retry
            for retry in range(2):
                try:
                    response, sw1, sw2 = connection.transmit([0x00, 0xA4, 0x00, 0x00, 0x02, 0x11, 0x00])
                    if sw1 == 0x90 and sw2 == 0x00:
                        break
                    elif retry == 0:
                        time.sleep(0.1)
                        continue
                    else:
                        raise Exception(f"SELECT DF1 failed: {sw1:02X}{sw2:02X}")
                except Exception as e:
                    if retry == 0:
                        time.sleep(0.1)
                        continue
                    else:
                        raise e
            
            # STEP 3: SELECT EF con retry
            for retry in range(2):
                try:
                    response, sw1, sw2 = connection.transmit([0x00, 0xA4, 0x00, 0x00, 0x02, 0x11, 0x02])
                    if sw1 == 0x90 and sw2 == 0x00:
                        break
                    elif retry == 0:
                        time.sleep(0.1)
                        continue
                    else:
                        raise Exception(f"SELECT EF failed: {sw1:02X}{sw2:02X}")
                except Exception as e:
                    if retry == 0:
                        time.sleep(0.1)
                        continue
                    else:
                        raise e
            
            # STEP 4: READ BINARY con retry
            for retry in range(2):
                try:
                    response, sw1, sw2 = connection.transmit([0x00, 0xB0, 0x00, 0x00, 0x9F])
                    if sw1 == 0x90 and sw2 == 0x00 and response:
                        break
                    elif retry == 0:
                        time.sleep(0.1)
                        continue
                    else:
                        raise Exception(f"READ BINARY failed: {sw1:02X}{sw2:02X}")
                except Exception as e:
                    if retry == 0:
                        time.sleep(0.1)
                        continue
                    else:
                        raise e
            
            if self.debug:
                logger.debug(f"Data: {toHexString(response)}")
            
            # Estrai CF
            return self._extract_cf_optimized(response)
            
        except Exception as e:
            if self.debug:
                logger.debug(f"❌ Errore APDU: {e}")
            return None
    
    def _extract_cf_optimized(self, data: list) -> Optional[str]:
        """Estrazione CF ottimizzata per performance"""
        try:
            # Pattern CF
            cf_pattern = r'[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]'
            
            # METODO 1: Scansione diretta (più veloce)
            for i in range(len(data) - 15):
                candidate = ""
                valid_chars = True
                
                for j in range(16):
                    byte = data[i + j]
                    if (65 <= byte <= 90) or (48 <= byte <= 57):  # A-Z o 0-9
                        candidate += chr(byte)
                    else:
                        valid_chars = False
                        break
                
                if valid_chars and len(candidate) == 16:
                    if re.match(cf_pattern, candidate) and self._validate_cf_fast(candidate):
                        return candidate
            
            # METODO 2: ASCII fallback
            ascii_data = ''.join([chr(b) if 32 <= b <= 126 else '.' for b in data])
            matches = re.findall(cf_pattern, ascii_data.upper())
            
            for match in matches:
                if self._validate_cf_fast(match):
                    return match
            
            return None
            
        except Exception as e:
            if self.debug:
                logger.debug(f"❌ Errore estrazione CF: {e}")
            return None
    
    def _validate_cf_fast(self, cf: str) -> bool:
        """Validazione CF veloce"""
        if not cf or len(cf) != 16:
            return False
        
        # Verifica pattern base
        pattern = r'^[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]$'
        if not re.match(pattern, cf):
            return False
        
        # Evita pattern troppo uniformi
        if len(set(cf)) < 4:
            return False
        
        return True
    
    def _wait_card_removal_robust(self):
        """Attesa rimozione tessera ROBUSTA"""
        removal_timeout = 30  # Max 30 secondi di attesa
        start_time = time.time()
        
        while (time.time() - start_time) < removal_timeout:
            try:
                # Test presenza tessera con timeout molto breve
                cardrequest = CardRequest(timeout=0.2, cardType=AnyCardType())
                cardservice = cardrequest.waitforcard()
                
                if cardservice:
                    # Tessera ancora presente
                    time.sleep(0.3)
                    continue
                else:
                    # Tessera rimossa
                    break
                    
            except CardRequestTimeoutException:
                # Tessera rimossa - normale
                break
            except Exception:
                # Errore generico = probabilmente tessera rimossa
                break
        
        # Pausa breve dopo rimozione per stabilizzare
        time.sleep(0.2)
    
    def stop(self):
        """Ferma lettura continua"""
        self.running = False
    
    def get_last_cf(self) -> Optional[str]:
        """Ultimo CF letto"""
        return self.last_cf
    
    def test_connection(self) -> bool:
        """Test connessione"""
        return len(self.readers) > 0
    
    def set_debug(self, debug: bool):
        """Abilita/disabilita debug logging"""
        self.debug = debug
        if debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

# Test e utilizzo
if __name__ == "__main__":
    import signal
    import sys
    
    def handle_cf(cf: str):
        """Callback per CF letti"""
        print(f"\n🎯 ACCESSO RILEVATO!")
        print(f"📋 Codice Fiscale: {cf}")
        print(f"⏰ {time.strftime('%H:%M:%S')}")
        print("💳 Pronto per prossima tessera...\n")
    
    def signal_handler(signum, frame):
        print(f"\n🛑 Arresto...")
        if 'reader' in globals():
            reader.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🏥 SISTEMA CONTROLLO ACCESSI ROBUSTO")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        reader = CardReader()
        
        # Abilita debug se necessario
        # reader.set_debug(True)
        
        print("✅ Sistema ROBUSTO inizializzato")
        print("💳 Inserire tessere sanitarie...")
        print("🔄 Retry automatici attivi")
        print("⚠️ Gestione errori robusta")
        print("⏹️ Ctrl+C per fermare")
        
        # Avvia lettura continua
        reader.start_continuous_reading(callback=handle_cf)
        
    except Exception as e:
        print(f"❌ Errore: {e}")
    finally:
        print("✅ Sistema fermato")
