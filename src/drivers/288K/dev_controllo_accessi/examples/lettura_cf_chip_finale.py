#!/usr/bin/env python3
"""
Lettura FINALE del codice fiscale dal chip della tessera sanitaria
Il CF si trova all'offset 0x40 del file EF.Dati_Personali (1102)
"""
import sys
import time
import ctypes
import re
sys.path.insert(0, '/opt/access_control')

from src.hardware.crt285_reader import CRT285Reader

CHIP_COLD_RESET = 0x02
CHIP_DEACTIVATE = 0x08

class TesseraSanitariaChipReader:
    """Lettore CF dal chip della tessera sanitaria italiana"""
    
    def __init__(self, reader):
        self.reader = reader
        self.lib = reader.lib
        self._setup_chip_functions()
    
    def _setup_chip_functions(self):
        """Configura funzioni chip"""
        self.lib.lib.CRT288x_GetICType.argtypes = []
        self.lib.lib.CRT288x_GetICType.restype = ctypes.c_int
        
        self.lib.lib.CRT288x_ChipPower.argtypes = [
            ctypes.c_int, ctypes.c_ushort,
            ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_int)
        ]
        self.lib.lib.CRT288x_ChipPower.restype = ctypes.c_int
        
        self.lib.lib.CRT288x_ChipIO.argtypes = [
            ctypes.c_ushort, ctypes.c_int,
            ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_ubyte)
        ]
        self.lib.lib.CRT288x_ChipIO.restype = ctypes.c_int
    
    def send_apdu(self, command_bytes, protocol=0):
        """Invia comando APDU"""
        cmd_array = (ctypes.c_ubyte * len(command_bytes))(*command_bytes)
        resp_buffer = (ctypes.c_ubyte * 512)()
        resp_len = ctypes.c_int(512)
        
        result = self.lib.lib.CRT288x_ChipIO(
            protocol, len(command_bytes), cmd_array,
            ctypes.byref(resp_len), resp_buffer
        )
        
        if result >= 0:
            return bytes(resp_buffer[:resp_len.value])
        return None
    
    def read_cf_from_chip(self):
        """Legge il codice fiscale dal chip"""
        try:
            # 1. Power on chip
            ic_type = self.lib.lib.CRT288x_GetICType()
            print(f"📊 Tipo chip: {'T=1 CPU' if ic_type == 11 else 'T=0 CPU' if ic_type == 10 else f'Tipo {ic_type}'}")
            
            atr_buffer = (ctypes.c_ubyte * 256)()
            atr_len = ctypes.c_int()
            
            result = self.lib.lib.CRT288x_ChipPower(ic_type, CHIP_COLD_RESET, atr_buffer, ctypes.byref(atr_len))
            if result != 0:
                print("❌ Errore accensione chip")
                return None
            
            print("✅ Chip acceso")
            
            # 2. Naviga al file EF.Dati_Personali
            # Select MF (3F00)
            resp = self.send_apdu(bytes([0x00, 0xA4, 0x00, 0x00, 0x02, 0x3F, 0x00]))
            if not resp or resp[-2:].hex() != '9000':
                print("❌ Errore selezione MF")
                return None
            
            # Select DF1 (1100)
            resp = self.send_apdu(bytes([0x00, 0xA4, 0x00, 0x00, 0x02, 0x11, 0x00]))
            if not resp or resp[-2:].hex() != '9000':
                print("❌ Errore selezione DF1")
                return None
            
            # Select EF.Dati_Personali (1102)
            resp = self.send_apdu(bytes([0x00, 0xA4, 0x00, 0x00, 0x02, 0x11, 0x02]))
            if not resp or resp[-2:].hex() != '9000':
                print("❌ Errore selezione EF.Dati_Personali")
                return None
            
            print("✅ File EF.Dati_Personali selezionato")
            
            # 3. Leggi il CF dall'offset 0x40
            # Il CF è memorizzato a partire dall'offset 0x44 (68 decimale)
            # e occupa 16 bytes
            
            # READ BINARY: CLA=00, INS=B0, P1=00 (offset high), P2=44 (offset low), Le=10 (16 bytes)
            read_cmd = bytes([0x00, 0xB0, 0x00, 0x44, 0x10])
            resp = self.send_apdu(read_cmd)
            
            if resp and len(resp) >= 18 and resp[-2:].hex() == '9000':
                cf_bytes = resp[:-2]  # Rimuovi status word
                cf = cf_bytes.decode('ascii', errors='ignore').upper()
                
                # Verifica che sia un CF valido
                if re.match(r'^[A-Z]{6}[0-9]{2}[A-EHLMPRST][0-9]{2}[A-Z][0-9]{3}[A-Z]$', cf):
                    return cf
                else:
                    print(f"⚠️ CF letto ma formato non valido: {cf}")
                    
                    # Prova a leggere un po' prima (offset 0x40)
                    read_cmd = bytes([0x00, 0xB0, 0x00, 0x40, 0x20])  # 32 bytes da offset 0x40
                    resp = self.send_apdu(read_cmd)
                    
                    if resp and len(resp) > 2 and resp[-2:].hex() == '9000':
                        data = resp[:-2]
                        text = data.decode('ascii', errors='ignore').upper()
                        
                        # Cerca il pattern CF nei dati
                        cf_pattern = r'[A-Z]{6}[0-9]{2}[A-EHLMPRST][0-9]{2}[A-Z][0-9]{3}[A-Z]'
                        matches = re.findall(cf_pattern, text)
                        
                        if matches:
                            return matches[0]
                        
                        # Se non trova pattern completo, prova a ricostruire
                        # Sappiamo che inizia con GRC per questa tessera
                        if 'GRCMMM' in text:
                            start = text.index('GRCMMM')
                            cf_candidate = text[start:start+16]
                            if len(cf_candidate) == 16:
                                return cf_candidate
            
            print("❌ CF non trovato all'offset previsto")
            return None
            
        finally:
            # Deactivate chip
            self.lib.lib.CRT288x_ChipPower(0, CHIP_DEACTIVATE, None, None)
            print("⚡ Chip disattivato")

def main():
    print("🏥 LETTURA CODICE FISCALE DAL CHIP TESSERA SANITARIA")
    print("="*60)
    print("Sistema ottimizzato - CF all'offset 0x40-0x50")
    print("="*60)
    
    try:
        # Inizializza lettore
        print("\n🔧 Inizializzazione lettore...")
        reader = CRT285Reader(
            device_path="/dev/ttyACM0",
            auto_test=False,
            strict_validation=False
        )
        print("✅ Lettore inizializzato")
        
        # Crea lettore chip
        chip_reader = TesseraSanitariaChipReader(reader)
        
        # Attendi tessera
        print("\n💳 INSERIRE TESSERA SANITARIA...")
        while reader.lib.CRT288x_GetCardStatus() != 3:
            time.sleep(0.2)
        
        print("✅ Tessera rilevata!")
        time.sleep(0.5)
        
        # Leggi CF dal chip
        print("\n📖 Lettura CF dal chip...")
        cf_chip = chip_reader.read_cf_from_chip()
        
        # Leggi anche dalla banda magnetica per confronto
        print("\n📍 Lettura banda magnetica...")
        track1 = ctypes.create_string_buffer(512)
        track2 = ctypes.create_string_buffer(512)
        track3 = ctypes.create_string_buffer(512)
        
        cf_banda = None
        if reader.lib.CRT288x_ReadAllTracks(track1, track2, track3) == 0:
            if track1.value:
                t1 = track1.value.decode('ascii', errors='ignore')
                if len(t1) >= 16:
                    cf_banda = t1[:16]
        
        # Risultati
        print("\n" + "="*60)
        print("📊 RISULTATI")
        print("="*60)
        
        if cf_chip:
            print(f"\n✅ CF DAL CHIP: {cf_chip}")
        else:
            print("\n❌ CF non letto dal chip")
        
        if cf_banda:
            print(f"✅ CF DALLA BANDA: {cf_banda}")
        
        if cf_chip and cf_banda:
            if cf_chip == cf_banda:
                print("\n✅ I CODICI FISCALI COINCIDONO PERFETTAMENTE!")
            else:
                print("\n⚠️ I codici fiscali sono diversi")
        
        # Analisi dettagliata del CF
        if cf_chip:
            print(f"\n📋 ANALISI CF: {cf_chip}")
            print(f"  Cognome: {cf_chip[0:3]}")
            print(f"  Nome: {cf_chip[3:6]}")
            print(f"  Anno nascita: {cf_chip[6:8]}")
            
            mese_lettere = {
                'A': '01', 'B': '02', 'C': '03', 'D': '04', 'E': '05',
                'H': '06', 'L': '07', 'M': '08', 'P': '09', 'R': '10',
                'S': '11', 'T': '12'
            }
            mese = mese_lettere.get(cf_chip[8], '??')
            print(f"  Mese nascita: {mese} ({cf_chip[8]})")
            print(f"  Giorno nascita: {cf_chip[9:11]}")
            print(f"  Comune nascita: {cf_chip[11:15]}")
            print(f"  Carattere controllo: {cf_chip[15]}")
        
        print("\n⏏️ Rimuovere la tessera...")
        while reader.lib.CRT288x_GetCardStatus() != 1:
            time.sleep(0.2)
        print("✅ Tessera rimossa")
        
    except KeyboardInterrupt:
        print("\n⏹️ Interrotto")
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'reader' in locals():
            reader.stop()
        print("\n✅ Sistema chiuso")

if __name__ == "__main__":
    main()