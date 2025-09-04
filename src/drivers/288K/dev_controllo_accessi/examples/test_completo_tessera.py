#!/usr/bin/env python3
"""
Test completo lettore CRT-285: Chip IC + Banda Magnetica
"""
import sys
import time
import logging
sys.path.insert(0, '/opt/access_control')

from src.hardware.crt285_reader import CRT285Reader
import ctypes

# Setup logging dettagliato
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_chip_ic(reader):
    """Test lettura chip IC della tessera sanitaria"""
    print("\n" + "="*60)
    print("🔬 TEST CHIP IC (Smart Card)")
    print("="*60)
    
    try:
        # Tentativo di lettura chip usando comandi APDU
        print("\n📡 Tentativo accesso chip IC...")
        
        # Verifica se la libreria supporta funzioni chip
        if hasattr(reader.lib, 'CRT288x_GetICType'):
            print("✅ Funzioni chip IC disponibili")
            
            # Prova a ottenere tipo di chip
            ic_type = reader.lib.CRT288x_GetICType()
            print(f"📊 Tipo chip rilevato: {ic_type}")
            
            ic_types = {
                0: "Nessun chip/sconosciuto",
                10: "T=0 CPU Card", 
                11: "T=1 CPU Card",
                20: "SL4442 Memory Card",
                21: "SL4428 Memory Card",
                30: "AT24C01 EEPROM",
                31: "AT24C02 EEPROM",
                32: "AT24C04 EEPROM"
            }
            
            chip_name = ic_types.get(ic_type, f"Tipo sconosciuto ({ic_type})")
            print(f"💳 Chip identificato come: {chip_name}")
            
            if ic_type > 0:
                # Tentativo power on chip
                if hasattr(reader.lib, 'CRT288x_ChipPower'):
                    print("\n⚡ Tentativo accensione chip...")
                    atr_buffer = ctypes.create_string_buffer(256)
                    result = reader.lib.CRT288x_ChipPower(atr_buffer)
                    
                    if result == 0:
                        atr = atr_buffer.value.hex()
                        print(f"✅ Chip attivato!")
                        print(f"📋 ATR (Answer To Reset): {atr}")
                        
                        # Analizza ATR per info sulla carta
                        if atr:
                            print(f"   Lunghezza ATR: {len(atr)//2} bytes")
                            if atr.startswith('3b'):
                                print("   Formato: Direct convention")
                            elif atr.startswith('3f'):
                                print("   Formato: Inverse convention")
                    else:
                        print(f"⚠️ Impossibile attivare chip (errore: {result})")
                
                # Test lettura dati da chip
                if hasattr(reader.lib, 'CRT288x_ChipIO'):
                    print("\n📖 Tentativo lettura dati chip...")
                    
                    # Comando SELECT per tessera sanitaria italiana
                    # AID tessera sanitaria: A0 00 00 00 77 01 08 00 07 00 00 FE 00 00 01
                    select_cmd = bytes([0x00, 0xA4, 0x04, 0x00, 0x0F, 
                                       0xA0, 0x00, 0x00, 0x00, 0x77, 0x01, 0x08, 
                                       0x00, 0x07, 0x00, 0x00, 0xFE, 0x00, 0x00, 0x01])
                    
                    send_buffer = ctypes.create_string_buffer(bytes(select_cmd))
                    recv_buffer = ctypes.create_string_buffer(256)
                    
                    result = reader.lib.CRT288x_ChipIO(
                        send_buffer, 
                        len(select_cmd),
                        recv_buffer, 
                        256
                    )
                    
                    if result > 0:
                        response = recv_buffer.raw[:result].hex()
                        print(f"✅ Risposta chip: {response}")
                        
                        # Se risposta OK (90 00), prova a leggere CF
                        if response.endswith('9000'):
                            print("   ✅ Applicazione tessera sanitaria selezionata!")
                            
                            # Comando READ per leggere CF (file EF.Dati_Personali)
                            read_cmd = bytes([0x00, 0xB0, 0x81, 0x00, 0x00])
                            # ... ulteriori comandi per leggere il CF dal chip
                    else:
                        print(f"⚠️ Nessuna risposta dal chip")
            else:
                print("❌ Nessun chip IC rilevato nella carta")
                print("ℹ️ Le tessere sanitarie più vecchie potrebbero non avere chip")
                
        else:
            print("⚠️ Funzioni chip IC non disponibili nella libreria")
            print("ℹ️ Necessaria versione completa della libreria CRT288x")
            
    except Exception as e:
        print(f"❌ Errore test chip: {e}")
        import traceback
        traceback.print_exc()

def test_banda_magnetica_completa(reader):
    """Test lettura completa di tutti i dati banda magnetica"""
    print("\n" + "="*60)
    print("🔍 TEST BANDA MAGNETICA COMPLETA")
    print("="*60)
    
    try:
        # Crea buffer per le 3 tracce
        track1 = ctypes.create_string_buffer(512)
        track2 = ctypes.create_string_buffer(512)
        track3 = ctypes.create_string_buffer(512)
        
        print("\n📖 Lettura di tutte le tracce magnetiche...")
        result = reader.lib.CRT288x_ReadAllTracks(track1, track2, track3)
        
        if result == 0:
            # Decodifica dati grezzi
            t1_raw = track1.value
            t2_raw = track2.value
            t3_raw = track3.value
            
            print("\n✅ DATI GREZZI LETTI:")
            print(f"\n📍 Track 1 (IATA - Alfanumerico):")
            print(f"   Raw: {t1_raw}")
            print(f"   Hex: {t1_raw.hex() if t1_raw else 'vuoto'}")
            print(f"   Lunghezza: {len(t1_raw)} bytes")
            
            # Analisi Track 1
            if t1_raw:
                t1_str = t1_raw.decode('ascii', errors='ignore')
                print(f"   Decodificato: {t1_str}")
                
                # Estrazione CF da Track 1
                if len(t1_str) >= 16:
                    cf_candidate = t1_str[:16]
                    print(f"   🔍 Possibile CF: {cf_candidate}")
                    
                    # Verifica se è un CF valido
                    if reader._validate_cf(cf_candidate):
                        print(f"   ✅ CF VALIDO: {cf_candidate}")
                    
                # Estrazione nome
                if len(t1_str) > 16:
                    nome = t1_str[16:].strip()
                    print(f"   👤 Nome: {nome}")
            
            print(f"\n📍 Track 2 (ABA - Numerico):")
            print(f"   Raw: {t2_raw}")
            print(f"   Hex: {t2_raw.hex() if t2_raw else 'vuoto'}")
            print(f"   Lunghezza: {len(t2_raw)} bytes")
            
            # Analisi Track 2
            if t2_raw:
                t2_str = t2_raw.decode('ascii', errors='ignore')
                print(f"   Decodificato: {t2_str}")
                
                # Se è il numero tessera mappato
                if t2_str == "80380001800322426041":
                    print(f"   ℹ️ Numero tessera di test riconosciuto")
                    print(f"   🔄 Mappato a CF: RSSMRA80A01H501Z")
                else:
                    # Tentativo decodifica ABA
                    if len(t2_str) >= 32 and t2_str.isdigit():
                        print(f"   🔄 Tentativo decodifica ABA->CF...")
                        cf_decoded = reader._decode_aba_to_cf(t2_str)
                        if cf_decoded:
                            print(f"   ✅ CF decodificato: {cf_decoded}")
            
            print(f"\n📍 Track 3 (Riservata):")
            print(f"   Raw: {t3_raw}")
            print(f"   Hex: {t3_raw.hex() if t3_raw else 'vuoto'}")
            print(f"   Lunghezza: {len(t3_raw)} bytes")
            
            if t3_raw:
                t3_str = t3_raw.decode('ascii', errors='ignore')
                print(f"   Decodificato: {t3_str}")
                print(f"   ℹ️ Track 3 normalmente non utilizzata")
            
            # Riepilogo
            print("\n" + "="*60)
            print("📊 RIEPILOGO DATI TESSERA:")
            print("="*60)
            
            # Dati estratti
            cf_track1 = None
            nome_track1 = None
            
            if t1_raw:
                t1_str = t1_raw.decode('ascii', errors='ignore')
                if len(t1_str) >= 16:
                    cf_track1 = t1_str[:16]
                    if len(t1_str) > 16:
                        nome_track1 = t1_str[16:].strip()
            
            if cf_track1 and reader._validate_cf(cf_track1):
                print(f"✅ Codice Fiscale: {cf_track1}")
                if nome_track1:
                    print(f"👤 Intestatario: {nome_track1}")
            
            if t2_raw:
                t2_str = t2_raw.decode('ascii', errors='ignore')
                print(f"🔢 Numero Tessera: {t2_str}")
                
                # Check mapping
                if t2_str in reader.tessera_cf_mapping:
                    cf_mapped = reader.tessera_cf_mapping[t2_str]
                    print(f"🔄 CF da mapping: {cf_mapped}")
            
            print("\n📝 FORMATO TESSERA RILEVATO:")
            if cf_track1 and reader._validate_cf(cf_track1):
                print("   ✅ Tessera sanitaria italiana standard")
                print("   ✅ CF leggibile da banda magnetica Track 1")
            elif t2_str == "80380001800322426041":
                print("   ⚠️ Tessera con solo numero identificativo")
                print("   ℹ️ CF probabilmente nel chip IC")
                print("   🔄 Usando mapping temporaneo per test")
            else:
                print("   ❓ Formato tessera non standard")
                
        else:
            print(f"❌ Errore lettura tracce: {result}")
            
    except Exception as e:
        print(f"❌ Errore test banda: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🏥 TEST COMPLETO LETTORE CRT-285")
    print("="*60)
    print("📋 Test di tutte le modalità di lettura tessera sanitaria")
    print("="*60)
    
    try:
        # Inizializza lettore
        print("\n🔧 Inizializzazione lettore...")
        reader = CRT285Reader(
            device_path="/dev/ttyACM0",
            auto_test=False,  # Skip test automatici
            strict_validation=False
        )
        
        # Abilita debug
        reader.set_debug(True)
        
        print("✅ Lettore inizializzato")
        
        # Attendi carta
        print("\n" + "="*60)
        print("💳 INSERIRE UNA TESSERA SANITARIA NEL LETTORE")
        print("="*60)
        
        # Attendi inserimento carta
        print("\n⏳ Attendo inserimento tessera...")
        while reader.lib.CRT288x_GetCardStatus() != 3:
            time.sleep(0.2)
        
        print("✅ Tessera rilevata!")
        time.sleep(0.5)  # Stabilizzazione
        
        # Test 1: Banda magnetica
        test_banda_magnetica_completa(reader)
        
        # Test 2: Chip IC
        test_chip_ic(reader)
        
        # Conclusioni
        print("\n" + "="*60)
        print("✅ TEST COMPLETATO")
        print("="*60)
        
        print("\n💡 SUGGERIMENTI:")
        print("1. Per leggere CF dal chip IC serve implementazione completa APDU")
        print("2. La mappatura numero->CF è una soluzione temporanea efficace")
        print("3. Track 1 contiene il CF in chiaro nelle tessere più vecchie")
        print("4. Track 2 contiene solo il numero tessera nelle tessere moderne")
        
        print("\n⏏️ Rimuovere la tessera...")
        while reader.lib.CRT288x_GetCardStatus() != 1:
            time.sleep(0.2)
        print("✅ Tessera rimossa")
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrotto")
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'reader' in locals():
            reader.stop()
        print("\n✅ Lettore fermato")

if __name__ == "__main__":
    main()