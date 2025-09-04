# File: /opt/access_control/scripts/super_tessera_test.py
# SUPER TEST TESSERA SANITARIA - TUTTI I METODI POSSIBILI
# Basato sulla ricerca approfondita e documentazione trovata

import sys
import time
import logging
import re
from datetime import datetime
from smartcard.System import readers
from smartcard.util import toHexString, toBytes
from smartcard.CardRequest import CardRequest
from smartcard.CardType import AnyCardType
from smartcard.Exceptions import CardRequestTimeoutException, NoCardException

# Setup logging dettagliato
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/opt/access_control/logs/super_card_test.log')
    ]
)
logger = logging.getLogger(__name__)

class SuperTesseraSanitariaReader:
    """Lettore avanzato tessera sanitaria - TUTTI I METODI POSSIBILI"""
    
    def __init__(self):
        self.connection = None
        self.last_atr = None
        self.readers = []
        
        self.init_readers()
        logger.info("🚀 SUPER TESSERA READER INIZIALIZZATO")
    
    def init_readers(self):
        """Inizializza lettori"""
        try:
            self.readers = readers()
            if not self.readers:
                raise Exception("Nessun lettore trovato")
            
            logger.info(f"📱 Lettori disponibili: {len(self.readers)}")
            for i, reader in enumerate(self.readers):
                logger.info(f"  {i}: {reader}")
        
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione: {e}")
            raise
    
    def connect_card(self, timeout=30):
        """Connessione tessera con analisi ATR"""
        logger.info(f"👆 Inserire tessera sanitaria (timeout: {timeout}s)...")
        
        try:
            cardrequest = CardRequest(timeout=timeout, cardType=AnyCardType())
            cardservice = cardrequest.waitforcard()
            
            cardservice.connection.connect()
            self.connection = cardservice.connection
            
            # Analisi ATR
            atr = cardservice.connection.getATR()
            atr_hex = toHexString(atr).replace(" ", "")
            self.last_atr = atr_hex
            
            logger.info(f"✅ TESSERA CONNESSA")
            logger.info(f"📋 ATR: {atr_hex}")
            
            # Identifica tipo tessera
            self.identify_card_type(atr_hex)
            
            return True
            
        except CardRequestTimeoutException:
            logger.warning("⏰ Timeout - nessuna tessera inserita")
            return False
        except Exception as e:
            logger.error(f"❌ Errore connessione: {e}")
            return False
    
    def identify_card_type(self, atr_hex):
        """Identifica tipo di tessera da ATR"""
        logger.info("🔍 IDENTIFICAZIONE TESSERA:")
        
        known_atrs = {
            "3B8B80010031C16408923354009000F3": "Tessera Sanitaria Italiana - Netlink",
            "3B8B80010031C1640892335400900073": "Tessera Sanitaria Italiana - Variante A", 
            "3B8B80010031C164089233540090007B": "Tessera Sanitaria Italiana - Variante B"
        }
        
        if atr_hex in known_atrs:
            logger.info(f"✅ {known_atrs[atr_hex]}")
            return known_atrs[atr_hex]
        else:
            logger.warning(f"⚠️ ATR sconosciuto: {atr_hex}")
            return "ATR sconosciuto"
    
    def test_all_methods(self):
        """TESTA TUTTI I METODI POSSIBILI PER LEGGERE CODICE FISCALE"""
        
        if not self.connection:
            logger.error("❌ Nessuna connessione tessera")
            return []
        
        results = []
        
        logger.info("🧪 INIZIO TEST METODI LETTURA CODICE FISCALE")
        logger.info("=" * 70)
        
        # METODO 1: Standard ISO7816 con filesystem tessera sanitaria
        results.append(self.method_1_standard_filesystem())
        
        # METODO 2: Lettura diretta settori memoria
        results.append(self.method_2_direct_memory())
        
        # METODO 3: Enumerazione file system completa
        results.append(self.method_3_filesystem_scan())
        
        # METODO 4: Comandi specifici tessera sanitaria
        results.append(self.method_4_specific_commands())
        
        # METODO 5: Lettura raw con offsets diversi
        results.append(self.method_5_raw_reading())
        
        # METODO 6: Comandi GET DATA alternativi
        results.append(self.method_6_get_data_commands())
        
        # METODO 7: Test comandi non standard
        results.append(self.method_7_nonstandard_commands())
        
        return results
    
    def method_1_standard_filesystem(self):
        """METODO 1: Filesystem standard tessera sanitaria (dalla ricerca)"""
        logger.info("🔧 METODO 1: Filesystem Standard Tessera Sanitaria")
        logger.info("-" * 50)
        
        try:
            # Step 1: Seleziona Master File (MF) - ID 0x3F00
            logger.info("📁 Step 1: Selezione Master File (MF)")
            select_mf = [0x00, 0xA4, 0x00, 0x00, 0x02, 0x3F, 0x00]
            response, sw1, sw2 = self.connection.transmit(select_mf)
            logger.info(f"   Comando: {toHexString(select_mf)}")
            logger.info(f"   Status: {sw1:02X}{sw2:02X}")
            
            if sw1 != 0x90 or sw2 != 0x00:
                raise Exception(f"SELECT MF failed: {sw1:02X}{sw2:02X}")
            
            # Step 2: Seleziona Directory DF1 - ID 0x1100
            logger.info("📁 Step 2: Selezione Directory DF1") 
            select_df1 = [0x00, 0xA4, 0x00, 0x00, 0x02, 0x11, 0x00]
            response, sw1, sw2 = self.connection.transmit(select_df1)
            logger.info(f"   Comando: {toHexString(select_df1)}")
            logger.info(f"   Status: {sw1:02X}{sw2:02X}")
            
            if sw1 != 0x90 or sw2 != 0x00:
                raise Exception(f"SELECT DF1 failed: {sw1:02X}{sw2:02X}")
            
            # Step 3: Seleziona EF_Dati_personali - ID 0x1102
            logger.info("📄 Step 3: Selezione EF_Dati_personali")
            select_ef = [0x00, 0xA4, 0x00, 0x00, 0x02, 0x11, 0x02]
            response, sw1, sw2 = self.connection.transmit(select_ef)
            logger.info(f"   Comando: {toHexString(select_ef)}")
            logger.info(f"   Status: {sw1:02X}{sw2:02X}")
            
            if sw1 != 0x90 or sw2 != 0x00:
                raise Exception(f"SELECT EF failed: {sw1:02X}{sw2:02X}")
            
            # Step 4: Leggi dati personali
            logger.info("📖 Step 4: Lettura dati personali")
            read_binary = [0x00, 0xB0, 0x00, 0x00, 0x9F]  # Leggi 159 bytes
            response, sw1, sw2 = self.connection.transmit(read_binary)
            logger.info(f"   Comando: {toHexString(read_binary)}")
            logger.info(f"   Status: {sw1:02X}{sw2:02X}")
            logger.info(f"   Dati ricevuti: {len(response)} bytes")
            
            if sw1 == 0x90 and sw2 == 0x00 and response:
                logger.info(f"   HEX: {toHexString(response)}")
                
                # Estrai codice fiscale
                codice_fiscale = self.extract_codice_fiscale(response)
                if codice_fiscale:
                    logger.info(f"🎯 SUCCESSO! Codice fiscale: {codice_fiscale}")
                    return {"method": "Standard Filesystem", "success": True, "cf": codice_fiscale}
                else:
                    logger.warning("⚠️ Codice fiscale non trovato nei dati")
            
            return {"method": "Standard Filesystem", "success": False, "error": f"Status: {sw1:02X}{sw2:02X}"}
            
        except Exception as e:
            logger.error(f"❌ METODO 1 FALLITO: {e}")
            return {"method": "Standard Filesystem", "success": False, "error": str(e)}
    
    def method_2_direct_memory(self):
        """METODO 2: Lettura diretta memoria con offset multipli"""
        logger.info("🔧 METODO 2: Lettura Diretta Memoria")
        logger.info("-" * 50)
        
        results = []
        
        # Test offsets diversi
        offsets = [0x0000, 0x0010, 0x0020, 0x0030, 0x0040, 0x0050, 0x0080, 0x0100, 0x0200]
        lengths = [0x20, 0x40, 0x80, 0x9F]
        
        for offset in offsets:
            for length in lengths:
                try:
                    logger.info(f"📖 Test offset 0x{offset:04X}, length 0x{length:02X}")
                    
                    read_cmd = [0x00, 0xB0, (offset >> 8) & 0xFF, offset & 0xFF, length]
                    response, sw1, sw2 = self.connection.transmit(read_cmd)
                    
                    logger.info(f"   Status: {sw1:02X}{sw2:02X}")
                    
                    if sw1 == 0x90 and sw2 == 0x00 and response:
                        logger.info(f"   Dati ({len(response)} bytes): {toHexString(response)}")
                        
                        codice_fiscale = self.extract_codice_fiscale(response)
                        if codice_fiscale:
                            logger.info(f"🎯 SUCCESSO! CF trovato: {codice_fiscale}")
                            return {"method": f"Direct Memory 0x{offset:04X}", "success": True, "cf": codice_fiscale}
                        
                        results.append({
                            "offset": f"0x{offset:04X}",
                            "length": f"0x{length:02X}",
                            "status": f"{sw1:02X}{sw2:02X}",
                            "data_found": len(response) > 0
                        })
                
                except Exception as e:
                    logger.debug(f"   Errore: {e}")
                    continue
        
        return {"method": "Direct Memory", "success": False, "tests": results}
    
    def method_3_filesystem_scan(self):
        """METODO 3: Scansione completa filesystem"""
        logger.info("🔧 METODO 3: Scansione Filesystem")
        logger.info("-" * 50)
        
        results = []
        
        # File IDs da testare (basati su ricerca)
        file_ids = [
            (0x3F00, "Master File"),
            (0x1100, "DF1 - Directory Principale"),
            (0x1102, "EF - Dati Personali"),
            (0x1103, "EF - Dati Aggiuntivi"),
            (0x1000, "DF0 - Directory Sistema"),
            (0x1001, "EF - Certificati"),
            (0x1200, "DF2 - Directory Alternativa"),
            (0x5000, "Directory Applicazioni"),
            (0x5001, "Applicazione Sanitaria")
        ]
        
        for file_id, description in file_ids:
            try:
                logger.info(f"📁 Test {description} (ID: 0x{file_id:04X})")
                
                # Seleziona file
                select_cmd = [0x00, 0xA4, 0x00, 0x00, 0x02, (file_id >> 8) & 0xFF, file_id & 0xFF]
                response, sw1, sw2 = self.connection.transmit(select_cmd)
                
                logger.info(f"   Status: {sw1:02X}{sw2:02X}")
                
                if sw1 == 0x90 and sw2 == 0x00:
                    logger.info(f"   ✅ File selezionato correttamente")
                    
                    # Prova a leggere
                    read_cmd = [0x00, 0xB0, 0x00, 0x00, 0x9F]
                    response, sw1, sw2 = self.connection.transmit(read_cmd)
                    
                    if sw1 == 0x90 and sw2 == 0x00 and response:
                        logger.info(f"   📖 Dati letti: {len(response)} bytes")
                        logger.info(f"   HEX: {toHexString(response)}")
                        
                        codice_fiscale = self.extract_codice_fiscale(response)
                        if codice_fiscale:
                            logger.info(f"🎯 SUCCESSO! CF: {codice_fiscale}")
                            return {"method": f"Filesystem Scan - {description}", "success": True, "cf": codice_fiscale}
                        
                        results.append({
                            "file_id": f"0x{file_id:04X}",
                            "description": description,
                            "accessible": True,
                            "data_length": len(response)
                        })
                    else:
                        results.append({
                            "file_id": f"0x{file_id:04X}",
                            "description": description,
                            "accessible": True,
                            "readable": False,
                            "read_status": f"{sw1:02X}{sw2:02X}"
                        })
                else:
                    results.append({
                        "file_id": f"0x{file_id:04X}",
                        "description": description,
                        "accessible": False,
                        "select_status": f"{sw1:02X}{sw2:02X}"
                    })
            
            except Exception as e:
                logger.debug(f"   Errore: {e}")
                continue
        
        return {"method": "Filesystem Scan", "success": False, "files_tested": results}
    
    def method_4_specific_commands(self):
        """METODO 4: Comandi specifici tessera sanitaria"""
        logger.info("🔧 METODO 4: Comandi Specifici Tessera Sanitaria")
        logger.info("-" * 50)
        
        commands = [
            # Comandi GET DATA
            ([0x00, 0xCA, 0x00, 0x81, 0x00], "GET DATA - Dati Carta"),
            ([0x00, 0xCA, 0x01, 0x00, 0x00], "GET DATA - Informazioni"),
            ([0x00, 0xCA, 0x9F, 0x7F, 0x00], "GET DATA - Template"),
            
            # Comandi READ RECORD
            ([0x00, 0xB2, 0x01, 0x04, 0x20], "READ RECORD 1"),
            ([0x00, 0xB2, 0x02, 0x04, 0x20], "READ RECORD 2"),
            ([0x00, 0xB2, 0x03, 0x04, 0x20], "READ RECORD 3"),
            
            # Comandi applicazione specifica
            ([0x00, 0xA4, 0x04, 0x00, 0x06, 0xA0, 0x00, 0x00, 0x00, 0x30, 0x89], "SELECT AID Tessera Sanitaria"),
            
            # Comandi alternativi
            ([0x80, 0xB0, 0x00, 0x00, 0x20], "READ BINARY (80 prefix)"),
            ([0x00, 0xB0, 0x80, 0x00, 0x20], "READ BINARY (offset 0x8000)"),
        ]
        
        for command, description in commands:
            try:
                logger.info(f"⚡ Test: {description}")
                logger.info(f"   Comando: {toHexString(command)}")
                
                response, sw1, sw2 = self.connection.transmit(command)
                logger.info(f"   Status: {sw1:02X}{sw2:02X}")
                
                if sw1 == 0x90 and sw2 == 0x00 and response:
                    logger.info(f"   Dati: {toHexString(response)}")
                    
                    codice_fiscale = self.extract_codice_fiscale(response)
                    if codice_fiscale:
                        logger.info(f"🎯 SUCCESSO! CF: {codice_fiscale}")
                        return {"method": f"Specific Command - {description}", "success": True, "cf": codice_fiscale}
                
                elif sw1 == 0x61:
                    # Più dati disponibili
                    logger.info(f"   📤 Più dati disponibili: {sw2} bytes")
                    get_response = [0x00, 0xC0, 0x00, 0x00, sw2]
                    response2, sw1_2, sw2_2 = self.connection.transmit(get_response)
                    
                    if sw1_2 == 0x90 and sw2_2 == 0x00 and response2:
                        logger.info(f"   GET RESPONSE: {toHexString(response2)}")
                        
                        codice_fiscale = self.extract_codice_fiscale(response2)
                        if codice_fiscale:
                            logger.info(f"🎯 SUCCESSO! CF: {codice_fiscale}")
                            return {"method": f"Specific Command - {description} + GET RESPONSE", "success": True, "cf": codice_fiscale}
                
            except Exception as e:
                logger.debug(f"   Errore: {e}")
                continue
        
        return {"method": "Specific Commands", "success": False}
    
    def method_5_raw_reading(self):
        """METODO 5: Lettura raw completa"""
        logger.info("🔧 METODO 5: Lettura Raw Completa")
        logger.info("-" * 50)
        
        try:
            # Prova a leggere tutta la memoria disponibile
            max_attempts = 10
            data_collected = []
            
            for offset in range(0, 0x1000, 0x100):  # Da 0x0000 a 0x0F00
                try:
                    read_cmd = [0x00, 0xB0, (offset >> 8) & 0xFF, offset & 0xFF, 0xFF]
                    response, sw1, sw2 = self.connection.transmit(read_cmd)
                    
                    if sw1 == 0x90 and sw2 == 0x00 and response:
                        logger.info(f"   Offset 0x{offset:04X}: {len(response)} bytes")
                        data_collected.extend(response)
                        
                        # Controlla se ci sono dati
                        codice_fiscale = self.extract_codice_fiscale(response)
                        if codice_fiscale:
                            logger.info(f"🎯 SUCCESSO! CF trovato a offset 0x{offset:04X}: {codice_fiscale}")
                            return {"method": f"Raw Reading 0x{offset:04X}", "success": True, "cf": codice_fiscale}
                
                except Exception as e:
                    logger.debug(f"   Errore offset 0x{offset:04X}: {e}")
                    continue
            
            # Analizza tutti i dati raccolti
            if data_collected:
                logger.info(f"📊 Dati totali raccolti: {len(data_collected)} bytes")
                codice_fiscale = self.extract_codice_fiscale(data_collected)
                if codice_fiscale:
                    logger.info(f"🎯 SUCCESSO! CF nei dati completi: {codice_fiscale}")
                    return {"method": "Raw Reading - Combined", "success": True, "cf": codice_fiscale}
            
            return {"method": "Raw Reading", "success": False, "data_collected": len(data_collected)}
            
        except Exception as e:
            logger.error(f"❌ METODO 5 FALLITO: {e}")
            return {"method": "Raw Reading", "success": False, "error": str(e)}
    
    def method_6_get_data_commands(self):
        """METODO 6: Comandi GET DATA estesi"""
        logger.info("🔧 METODO 6: Comandi GET DATA Estesi")
        logger.info("-" * 50)
        
        # Tag GET DATA da testare
        get_data_tags = [
            (0x0081, "Dati Applicazione"),
            (0x005A, "PAN"),
            (0x005F2D, "Codice Lingua"),
            (0x005F50, "URL Issuer"),
            (0x009F08, "Versione Applicazione"),
            (0x009F42, "Codice Valuta"),
            (0x009F4A, "Static Data Authentication Tag List"),
            (0x0070, "Template Response"),
            (0x0077, "Response Message Template Format 2"),
            (0x0080, "Response Message Template Format 1"),
        ]
        
        for tag, description in get_data_tags:
            try:
                logger.info(f"📋 GET DATA: {description} (Tag: 0x{tag:04X})")
                
                if tag <= 0xFF:
                    # Tag singolo byte
                    get_data_cmd = [0x00, 0xCA, 0x00, tag & 0xFF, 0x00]
                else:
                    # Tag multi-byte
                    get_data_cmd = [0x00, 0xCA, (tag >> 8) & 0xFF, tag & 0xFF, 0x00]
                
                logger.info(f"   Comando: {toHexString(get_data_cmd)}")
                
                response, sw1, sw2 = self.connection.transmit(get_data_cmd)
                logger.info(f"   Status: {sw1:02X}{sw2:02X}")
                
                if sw1 == 0x90 and sw2 == 0x00 and response:
                    logger.info(f"   Dati: {toHexString(response)}")
                    
                    codice_fiscale = self.extract_codice_fiscale(response)
                    if codice_fiscale:
                        logger.info(f"🎯 SUCCESSO! CF: {codice_fiscale}")
                        return {"method": f"GET DATA - {description}", "success": True, "cf": codice_fiscale}
                
            except Exception as e:
                logger.debug(f"   Errore: {e}")
                continue
        
        return {"method": "GET DATA Commands", "success": False}
    
    def method_7_nonstandard_commands(self):
        """METODO 7: Comandi non standard e sperimentali"""
        logger.info("🔧 METODO 7: Comandi Non Standard")
        logger.info("-" * 50)
        
        nonstandard_commands = [
            # Comandi proprietari possibili
            ([0x80, 0xA4, 0x00, 0x00, 0x02, 0x11, 0x02], "Proprietary SELECT"),
            ([0x80, 0xCA, 0x00, 0x00, 0x00], "Proprietary GET DATA"),
            ([0x00, 0x84, 0x00, 0x00, 0x08], "GET CHALLENGE"),
            ([0x00, 0x88, 0x00, 0x00, 0x10], "Internal Authenticate"),
            
            # Comandi debug
            ([0x00, 0xF0, 0x00, 0x00, 0x00], "Debug Command 1"),
            ([0x00, 0xF1, 0x00, 0x00, 0x00], "Debug Command 2"),
            
            # Comandi management
            ([0x80, 0x50, 0x00, 0x00, 0x08], "Management Command"),
        ]
        
        for command, description in nonstandard_commands:
            try:
                logger.info(f"🧪 Test: {description}")
                logger.info(f"   Comando: {toHexString(command)}")
                
                response, sw1, sw2 = self.connection.transmit(command)
                logger.info(f"   Status: {sw1:02X}{sw2:02X}")
                
                if sw1 == 0x90 and sw2 == 0x00 and response:
                    logger.info(f"   Dati: {toHexString(response)}")
                    
                    codice_fiscale = self.extract_codice_fiscale(response)
                    if codice_fiscale:
                        logger.info(f"🎯 SUCCESSO! CF: {codice_fiscale}")
                        return {"method": f"Nonstandard - {description}", "success": True, "cf": codice_fiscale}
                
            except Exception as e:
                logger.debug(f"   Errore: {e}")
                continue
        
        return {"method": "Nonstandard Commands", "success": False}
    
    def extract_codice_fiscale(self, data):
        """Estrazione codice fiscale avanzata"""
        try:
            # Converti in stringa ASCII
            ascii_data = ""
            for byte in data:
                if 32 <= byte <= 126:  # ASCII printable
                    ascii_data += chr(byte)
                else:
                    ascii_data += "."
            
            logger.debug(f"ASCII: '{ascii_data}'")
            
            # Pattern codice fiscale italiano
            cf_pattern = r'[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]'
            
            # Cerca in ASCII
            match = re.search(cf_pattern, ascii_data.upper())
            if match:
                cf = match.group()
                if self.validate_codice_fiscale(cf):
                    return cf
            
            # Prova diverse codifiche
            for encoding in ['ascii', 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    decoded = bytes(data).decode(encoding, errors='ignore')
                    match = re.search(cf_pattern, decoded.upper())
                    if match:
                        cf = match.group()
                        if self.validate_codice_fiscale(cf):
                            return cf
                except:
                    continue
            
            # Cerca pattern in HEX (UTF-16, etc.)
            hex_str = "".join([f"{b:02X}" for b in data])
            for i in range(0, len(hex_str) - 32, 2):
                try:
                    # Prova UTF-16
                    hex_chunk = hex_str[i:i+64]  # 32 caratteri = 16 bytes
                    if len(hex_chunk) >= 32:
                        bytes_chunk = bytes.fromhex(hex_chunk)
                        try:
                            decoded = bytes_chunk.decode('utf-16', errors='ignore')
                            match = re.search(cf_pattern, decoded.upper())
                            if match:
                                cf = match.group()
                                if self.validate_codice_fiscale(cf):
                                    return cf
                        except:
                            pass
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Errore estrazione CF: {e}")
            return None
    
    def validate_codice_fiscale(self, cf):
        """Validazione codice fiscale"""
        if len(cf) != 16:
            return False
        
        # Pattern standard
        pattern = r'^[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]$'
        if not re.match(pattern, cf):
            return False
        
        # Validazione checksum base (opzionale)
        return True
    
    def disconnect(self):
        """Disconnessione"""
        if self.connection:
            try:
                self.connection.disconnect()
                self.connection = None
                logger.info("📱 Disconnesso dalla tessera")
            except:
                pass

def main():
    """Funzione principale"""
    print("🏥 SUPER TEST TESSERA SANITARIA - METODI AVANZATI")
    print("=" * 70)
    print(f"⏰ Avvio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Inizializza reader
        reader = SuperTesseraSanitariaReader()
        
        # Connetti tessera
        if not reader.connect_card(timeout=30):
            print("❌ Impossibile connettersi alla tessera")
            return
        
        # Esegui tutti i test
        results = reader.test_all_methods()
        
        # Report finale
        print("\n" + "=" * 70)
        print("📊 REPORT FINALE - TUTTI I METODI TESTATI")
        print("=" * 70)
        
        success_count = 0
        for result in results:
            if result.get('success', False):
                print(f"✅ {result['method']}: SUCCESSO - CF: {result.get('cf', 'N/A')}")
                success_count += 1
            else:
                print(f"❌ {result['method']}: FALLITO")
        
        print(f"\n📈 RISULTATI: {success_count}/{len(results)} metodi riusciti")
        
        if success_count > 0:
            print("\n🎯 ALMENO UN METODO HA FUNZIONATO!")
            print("✅ Il lettore può leggere la tessera sanitaria")
        else:
            print("\n⚠️ NESSUN METODO È RIUSCITO")
            print("🔍 Possibili cause:")
            print("   - Tessera non supportata")
            print("   - PIN richiesto per tutti i dati")
            print("   - Lettore incompatibile")
            print("   - Tessera danneggiata")
            print("")
            print("💡 RACCOMANDAZIONE: Utilizzare lettore banda magnetica")
        
        # Disconnetti
        reader.disconnect()
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrotto dall'utente")
    except Exception as e:
        logger.error(f"❌ Errore critico: {e}")
        print(f"\n❌ Errore critico: {e}")

if __name__ == "__main__":
    main()