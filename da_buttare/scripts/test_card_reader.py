# File: /opt/access_control/scripts/test_card_reader.py
# Script test funzionalità lettore tessera sanitaria con pyscard

import sys
import time
import logging
from datetime import datetime
from smartcard.System import readers
from smartcard.util import toHexString, toBytes
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.CardRequest import CardRequest
from smartcard.CardType import AnyCardType
from smartcard.CardConnection import CardConnection
from smartcard.Exceptions import CardRequestTimeoutException, NoCardException

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TesseraSanitariaReader:
    """Lettore tessera sanitaria italiana"""
    
    def __init__(self):
        self.readers = []
        self.connection = None
        self.init_readers()
    
    def init_readers(self):
        """Inizializza lettori disponibili"""
        try:
            self.readers = readers()
            if not self.readers:
                raise Exception("Nessun lettore smart card trovato")
            
            logger.info(f"Lettori trovati: {len(self.readers)}")
            for i, reader in enumerate(self.readers):
                logger.info(f"  {i}: {reader}")
                
        except Exception as e:
            logger.error(f"Errore inizializzazione lettori: {e}")
            raise
    
    def wait_for_card(self, timeout=30):
        """Attende inserimento tessera"""
        logger.info(f"In attesa di tessera per {timeout} secondi...")
        
        try:
            cardrequest = CardRequest(timeout=timeout, cardType=AnyCardType())
            cardservice = cardrequest.waitforcard()
            
            # Connessione alla tessera
            cardservice.connection.connect()
            self.connection = cardservice.connection
            
            # Leggi ATR
            atr = cardservice.connection.getATR()
            atr_hex = toHexString(atr)
            
            logger.info(f"✅ Tessera inserita!")
            logger.info(f"ATR: {atr_hex}")
            
            # Verifica se è tessera sanitaria italiana
            if self.is_italian_health_card(atr):
                logger.info("🏥 Tessera Sanitaria Italiana identificata")
                return True
            else:
                logger.warning("⚠️ Tessera non riconosciuta come Tessera Sanitaria")
                return False
                
        except CardRequestTimeoutException:
            logger.warning("⏰ Timeout: nessuna tessera inserita")
            return False
        except Exception as e:
            logger.error(f"❌ Errore lettura tessera: {e}")
            return False
    
    def is_italian_health_card(self, atr):
        """Verifica se ATR corrisponde a tessera sanitaria italiana"""
        # ATR tessera sanitaria italiana
        known_atrs = [
            "3B8B80010031C16408923354009000F3",  # ATR del test
            "3B8B80010031C1640892335400900073",  # Variante comune
        ]
        
        atr_hex = toHexString(atr).replace(" ", "")
        return atr_hex in known_atrs
    
    def read_codice_fiscale(self):
        """Legge codice fiscale dalla tessera sanitaria"""
        if not self.connection:
            logger.error("Nessuna connessione alla tessera")
            return None
        
        try:
            logger.info("🔍 Lettura codice fiscale...")
            
            # Seleziona applicazione tessera sanitaria
            # Comando SELECT AID per tessera sanitaria
            select_aid = [0x00, 0xA4, 0x04, 0x00, 0x06, 0xA0, 0x00, 0x00, 0x00, 0x30, 0x89]
            
            response, sw1, sw2 = self.connection.transmit(select_aid)
            logger.info(f"SELECT AID: SW={sw1:02X}{sw2:02X}")
            
            if sw1 == 0x90 and sw2 == 0x00:
                logger.info("✅ Applicazione selezionata correttamente")
                
                # Leggi file EF.ID_Servizi (contiene codice fiscale)
                # Comando SELECT FILE
                select_file = [0x00, 0xA4, 0x02, 0x0C, 0x02, 0x11, 0x02]
                response, sw1, sw2 = self.connection.transmit(select_file)
                logger.info(f"SELECT FILE: SW={sw1:02X}{sw2:02X}")
                
                if sw1 == 0x90 and sw2 == 0x00:
                    # Leggi dati file
                    read_binary = [0x00, 0xB0, 0x00, 0x00, 0x00]
                    response, sw1, sw2 = self.connection.transmit(read_binary)
                    logger.info(f"READ BINARY: SW={sw1:02X}{sw2:02X}")
                    
                    if sw1 == 0x90 and sw2 == 0x00:
                        # Estrai codice fiscale dai dati
                        codice_fiscale = self.extract_codice_fiscale(response)
                        return codice_fiscale
                    else:
                        logger.error(f"Errore lettura dati: {sw1:02X}{sw2:02X}")
                else:
                    logger.error(f"Errore selezione file: {sw1:02X}{sw2:02X}")
            else:
                logger.error(f"Errore selezione applicazione: {sw1:02X}{sw2:02X}")
                
                # Prova metodo alternativo - lettura diretta
                logger.info("🔄 Tentativo metodo alternativo...")
                return self.read_codice_fiscale_alternative()
            
        except Exception as e:
            logger.error(f"❌ Errore lettura codice fiscale: {e}")
            return None
    
    def read_codice_fiscale_alternative(self):
        """Metodo alternativo per leggere codice fiscale"""
        try:
            # Prova lettura diretta con comandi diversi
            commands = [
                [0x00, 0xB0, 0x00, 0x00, 0x16],  # Leggi 22 bytes
                [0x00, 0xB0, 0x00, 0x80, 0x16],  # Offset diverso
                [0x00, 0xB2, 0x01, 0x04, 0x16],  # READ RECORD
            ]
            
            for i, cmd in enumerate(commands):
                logger.info(f"Tentativo comando {i+1}: {toHexString(cmd)}")
                response, sw1, sw2 = self.connection.transmit(cmd)
                logger.info(f"Risposta: SW={sw1:02X}{sw2:02X}, Data={toHexString(response)}")
                
                if sw1 == 0x90 and sw2 == 0x00 and response:
                    codice_fiscale = self.extract_codice_fiscale(response)
                    if codice_fiscale:
                        return codice_fiscale
            
            logger.warning("⚠️ Nessun metodo ha prodotto risultati")
            return None
            
        except Exception as e:
            logger.error(f"❌ Errore metodo alternativo: {e}")
            return None
    
    def extract_codice_fiscale(self, data):
        """Estrae codice fiscale dai dati binari"""
        try:
            # Converti in stringa
            data_str = ""
            for byte in data:
                if 32 <= byte <= 126:  # ASCII stampabile
                    data_str += chr(byte)
                else:
                    data_str += "."
            
            logger.info(f"Dati ASCII: '{data_str}'")
            logger.info(f"Dati HEX: {toHexString(data)}")
            
            # Pattern codice fiscale italiano (16 caratteri alfanumerici)
            import re
            cf_pattern = r'[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]'
            
            # Cerca pattern in dati ASCII
            match = re.search(cf_pattern, data_str.upper())
            if match:
                codice_fiscale = match.group()
                logger.info(f"✅ Codice fiscale trovato: {codice_fiscale}")
                return codice_fiscale
            
            # Se non trovato, prova a cercare in HEX convertito
            hex_str = "".join([f"{b:02X}" for b in data])
            logger.info(f"Ricerca in HEX: {hex_str}")
            
            # Prova diverse codifiche
            for encoding in ['ascii', 'utf-8', 'latin-1']:
                try:
                    decoded = bytes(data).decode(encoding, errors='ignore')
                    match = re.search(cf_pattern, decoded.upper())
                    if match:
                        codice_fiscale = match.group()
                        logger.info(f"✅ Codice fiscale trovato ({encoding}): {codice_fiscale}")
                        return codice_fiscale
                except:
                    continue
            
            logger.warning("⚠️ Codice fiscale non trovato nei dati")
            return None
            
        except Exception as e:
            logger.error(f"❌ Errore estrazione codice fiscale: {e}")
            return None
    
    def disconnect(self):
        """Disconnette dalla tessera"""
        if self.connection:
            try:
                self.connection.disconnect()
                self.connection = None
                logger.info("Disconnesso dalla tessera")
            except:
                pass

class CardMonitorTest(CardObserver):
    """Monitor per eventi tessera"""
    
    def update(self, observable, actions):
        for action in actions:
            if str(action[0]) == 'Card inserted':
                logger.info(f"🔍 Tessera inserita in: {action[1]}")
            elif str(action[0]) == 'Card removed':
                logger.info(f"📤 Tessera rimossa da: {action[1]}")

def test_reader_basic():
    """Test base del lettore"""
    logger.info("🔧 TEST BASE LETTORE")
    logger.info("=" * 50)
    
    try:
        reader = TesseraSanitariaReader()
        logger.info("✅ Lettore inizializzato correttamente")
        return True
    except Exception as e:
        logger.error(f"❌ Errore inizializzazione: {e}")
        return False

def test_card_detection():
    """Test rilevamento tessera"""
    logger.info("🔧 TEST RILEVAMENTO TESSERA")
    logger.info("=" * 50)
    
    try:
        reader = TesseraSanitariaReader()
        
        print("\n👆 Inserire la tessera sanitaria nel lettore...")
        if reader.wait_for_card(timeout=30):
            logger.info("✅ Tessera rilevata correttamente")
            
            # Tenta lettura codice fiscale
            codice_fiscale = reader.read_codice_fiscale()
            
            if codice_fiscale:
                logger.info(f"🎯 SUCCESSO! Codice fiscale: {codice_fiscale}")
                return codice_fiscale
            else:
                logger.warning("⚠️ Tessera rilevata ma codice fiscale non letto")
                return True
        else:
            logger.error("❌ Tessera non rilevata")
            return False
            
    except Exception as e:
        logger.error(f"❌ Errore test: {e}")
        return False
    finally:
        try:
            reader.disconnect()
        except:
            pass

def test_monitoring():
    """Test monitoring continuo"""
    logger.info("🔧 TEST MONITORING CONTINUO")
    logger.info("=" * 50)
    
    try:
        # Avvia monitoring
        cardmonitor = CardMonitor()
        cardobserver = CardMonitorTest()
        cardmonitor.addObserver(cardobserver)
        
        logger.info("📡 Monitoring attivo. Inserire/rimuovere tessera per 30 secondi...")
        logger.info("   Premi Ctrl+C per terminare")
        
        time.sleep(30)
        
        # Ferma monitoring
        cardmonitor.deleteObserver(cardobserver)
        logger.info("✅ Test monitoring completato")
        return True
        
    except KeyboardInterrupt:
        logger.info("⏹️ Test interrotto dall'utente")
        return True
    except Exception as e:
        logger.error(f"❌ Errore monitoring: {e}")
        return False

def main():
    """Funzione principale di test"""
    print("🏥 SISTEMA CONTROLLO ACCESSI - TEST LETTORE TESSERA SANITARIA")
    print("=" * 70)
    print(f"Data test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    risultati = {}
    
    # Test 1: Inizializzazione base
    risultati['init'] = test_reader_basic()
    print()
    
    if risultati['init']:
        # Test 2: Rilevamento tessera
        risultati['detection'] = test_card_detection()
        print()
        
        # Test 3: Monitoring (opzionale)
        print("Vuoi eseguire il test di monitoring continuo? (y/n): ", end="")
        try:
            choice = input().lower().strip()
            if choice in ['y', 'yes', 's', 'si']:
                risultati['monitoring'] = test_monitoring()
        except KeyboardInterrupt:
            print("\nTest interrotto")
    
    # Report finale
    print("\n" + "=" * 70)
    print("📊 REPORT FINALE TEST")
    print("=" * 70)
    
    for test_name, result in risultati.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.upper():<15}: {status}")
        
        if test_name == 'detection' and isinstance(result, str):
            print(f"{'CODICE FISCALE':<15}: {result}")
    
    print()
    
    # Raccomandazioni
    all_passed = all(risultati.values())
    if all_passed:
        print("🎯 TUTTI I TEST SUPERATI!")
        print("✅ Il lettore è pronto per l'uso con l'applicazione principale")
    else:
        print("⚠️ ALCUNI TEST FALLITI")
        print("🔧 Verificare connessioni hardware e driver")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Test interrotto dall'utente")
    except Exception as e:
        logger.error(f"❌ Errore critico: {e}")
        sys.exit(1)