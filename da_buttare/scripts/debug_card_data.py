# File: /opt/access_control/scripts/debug_card_data.py
# Debug completo dati tessera sanitaria

import sys
import time
import logging
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.CardRequest import CardRequest
from smartcard.CardType import AnyCardType
from smartcard.Exceptions import CardRequestTimeoutException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_card_data():
    """Debug completo dati tessera"""
    
    print("🔍 DEBUG TESSERA SANITARIA - ANALISI COMPLETA")
    print("=" * 60)
    
    try:
        # Attendi tessera
        print("👆 Inserire tessera sanitaria...")
        cardrequest = CardRequest(timeout=30, cardType=AnyCardType())
        cardservice = cardrequest.waitforcard()
        cardservice.connection.connect()
        
        connection = cardservice.connection
        atr = connection.getATR()
        
        print(f"✅ Tessera connessa")
        print(f"📋 ATR: {toHexString(atr)}")
        print()
        
        # Test vari comandi per trovare dove sono i dati
        test_commands = [
            # Comandi standard
            ([0x00, 0xA4, 0x04, 0x00, 0x06, 0xA0, 0x00, 0x00, 0x00, 0x30, 0x89], "SELECT AID Tessera Sanitaria"),
            ([0x00, 0xA4, 0x02, 0x0C, 0x02, 0x11, 0x02], "SELECT FILE ID_Servizi"),
            ([0x00, 0xB0, 0x00, 0x00, 0x00], "READ BINARY (auto-length)"),
            ([0x00, 0xB0, 0x00, 0x00, 0x20], "READ BINARY 32 bytes"),
            ([0x00, 0xB0, 0x00, 0x00, 0x50], "READ BINARY 80 bytes"),
            
            # Comandi alternativi
            ([0x00, 0xB2, 0x01, 0x04, 0x20], "READ RECORD 1"),
            ([0x00, 0xB2, 0x02, 0x04, 0x20], "READ RECORD 2"),
            ([0x00, 0xB2, 0x03, 0x04, 0x20], "READ RECORD 3"),
            
            # Lettura diretta offset diversi
            ([0x00, 0xB0, 0x00, 0x10, 0x20], "READ BINARY offset 0x10"),
            ([0x00, 0xB0, 0x00, 0x20, 0x20], "READ BINARY offset 0x20"),
            ([0x00, 0xB0, 0x00, 0x30, 0x20], "READ BINARY offset 0x30"),
            ([0x00, 0xB0, 0x00, 0x40, 0x20], "READ BINARY offset 0x40"),
            
            # Altri comandi
            ([0x00, 0xCA, 0x01, 0x00, 0x00], "GET DATA"),
            ([0x80, 0xB0, 0x00, 0x00, 0x20], "READ BINARY (80 prefix)"),
        ]
        
        successful_reads = []
        
        for i, (command, description) in enumerate(test_commands):
            try:
                print(f"\n🔍 Test {i+1}: {description}")
                print(f"   Comando: {toHexString(command)}")
                
                response, sw1, sw2 = connection.transmit(command)
                status = f"{sw1:02X}{sw2:02X}"
                
                print(f"   Status: {status}")
                
                if sw1 == 0x90 and sw2 == 0x00 and response:
                    print(f"   ✅ SUCCESSO - {len(response)} bytes ricevuti")
                    print(f"   HEX: {toHexString(response)}")
                    
                    # Converti in ASCII leggibile
                    ascii_data = ""
                    for byte in response:
                        if 32 <= byte <= 126:
                            ascii_data += chr(byte)
                        else:
                            ascii_data += "."
                    
                    print(f"   ASCII: '{ascii_data}'")
                    
                    # Cerca pattern codice fiscale
                    import re
                    cf_pattern = r'[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]'
                    
                    # Cerca in ASCII
                    match = re.search(cf_pattern, ascii_data.upper())
                    if match:
                        cf = match.group()
                        print(f"   🎯 CODICE FISCALE TROVATO: {cf}")
                        successful_reads.append((description, cf, command))
                    else:
                        # Prova diverse codifiche
                        for encoding in ['utf-8', 'latin-1', 'cp1252']:
                            try:
                                decoded = bytes(response).decode(encoding, errors='ignore')
                                match = re.search(cf_pattern, decoded.upper())
                                if match:
                                    cf = match.group()
                                    print(f"   🎯 CODICE FISCALE TROVATO ({encoding}): {cf}")
                                    successful_reads.append((description, cf, command))
                                    break
                            except:
                                continue
                
                elif sw1 == 0x61:
                    print(f"   📤 Più dati disponibili: {sw2} bytes")
                    # Prova GET RESPONSE
                    get_response = [0x00, 0xC0, 0x00, 0x00, sw2]
                    response2, sw1_2, sw2_2 = connection.transmit(get_response)
                    if sw1_2 == 0x90 and sw2_2 == 0x00:
                        print(f"   GET RESPONSE: {toHexString(response2)}")
                
                else:
                    print(f"   ❌ Errore: {status}")
                    
            except Exception as e:
                print(f"   ❌ Eccezione: {e}")
        
        # Riassunto
        print("\n" + "=" * 60)
        print("📊 RIASSUNTO RISULTATI")
        print("=" * 60)
        
        if successful_reads:
            print("✅ METODI CHE HANNO FUNZIONATO:")
            for i, (desc, cf, cmd) in enumerate(successful_reads):
                print(f"   {i+1}. {desc}")
                print(f"      Codice Fiscale: {cf}")
                print(f"      Comando: {toHexString(cmd)}")
                print()
        else:
            print("❌ NESSUN METODO HA ESTRATTO IL CODICE FISCALE")
            print()
            print("🔍 POSSIBILI CAUSE:")
            print("   1. La tessera non contiene il CF in formato leggibile")
            print("   2. Il CF è crittografato/codificato")
            print("   3. Serve PIN/autenticazione")
            print("   4. Struttura tessera diversa dal previsto")
        
        connection.disconnect()
        
    except CardRequestTimeoutException:
        print("❌ Timeout - nessuna tessera inserita")
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    debug_card_data()