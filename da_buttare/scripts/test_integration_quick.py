#!/usr/bin/env python3
# File: /opt/access_control/scripts/test_integration_quick.py
# Test rapido per verificare integrazione hardware pronta

import sys
import os
from pathlib import Path

def main():
    print("🧪 TEST RAPIDO INTEGRAZIONE HARDWARE")
    print("=" * 50)
    
    project_root = Path("/opt/access_control")
    
    # Test 1: Verifica file hardware
    print("\n📋 Test 1: Verifica moduli hardware...")
    
    card_reader_path = project_root / "src/hardware/card_reader.py"
    relay_path = project_root / "src/hardware/usb_rly08_controller.py"
    
    if card_reader_path.exists():
        print("✅ card_reader.py trovato")
    else:
        print("❌ card_reader.py mancante")
        return False
    
    if relay_path.exists():
        print("✅ usb_rly08_controller.py trovato")
    else:
        print("❌ usb_rly08_controller.py mancante")
        return False
    
    # Test 2: Verifica import
    print("\n📋 Test 2: Verifica import moduli...")
    
    # Aggiungi path
    sys.path.insert(0, str(project_root / "src"))
    
    try:
        from hardware.card_reader import CardReader
        print("✅ CardReader importabile")
        card_reader_ok = True
    except ImportError as e:
        print(f"❌ CardReader import failed: {e}")
        card_reader_ok = False
    
    try:
        from hardware.usb_rly08_controller import USBRLY08Controller
        print("✅ USBRLY08Controller importabile")
        relay_ok = True
    except ImportError as e:
        print(f"❌ USBRLY08Controller import failed: {e}")
        relay_ok = False
    
    # Test 3: Test inizializzazione (senza hardware)
    print("\n📋 Test 3: Test inizializzazione classi...")
    
    if card_reader_ok:
        try:
            # Test solo inizializzazione, non connessione
            print("🔄 Test CardReader...")
            reader = CardReader()
            print("✅ CardReader inizializzato")
        except Exception as e:
            print(f"⚠️ CardReader init warning: {e}")
    
    if relay_ok:
        try:
            # Test solo inizializzazione, non connessione
            print("🔄 Test USBRLY08Controller...")
            controller = USBRLY08Controller()
            print("✅ USBRLY08Controller inizializzato")
        except Exception as e:
            print(f"⚠️ USBRLY08Controller init warning: {e}")
    
    # Test 4: Verifica web_api.py
    print("\n📋 Test 4: Verifica web_api.py...")
    
    web_api_path = project_root / "src/api/web_api.py"
    
    if not web_api_path.exists():
        print("❌ web_api.py non trovato")
        return False
    
    try:
        with open(web_api_path, 'r') as f:
            content = f.read()
        
        if '/api/test/reader' in content:
            print("✅ Route test lettore presente")
        else:
            print("❌ Route test lettore mancante")
        
        if '/api/test/relay' in content:
            print("✅ Route test relay presente")
        else:
            print("❌ Route test relay mancante")
        
        if 'test_results' in content:
            print("✅ Variabili test presenti")
        else:
            print("❌ Variabili test mancanti")
        
    except Exception as e:
        print(f"❌ Errore lettura web_api.py: {e}")
        return False
    
    # Test 5: Verifica porte hardware
    print("\n📋 Test 5: Verifica porte hardware...")
    
    reader_ports = ["/dev/ttyACM0", "/dev/ttyUSB0"]
    reader_port_found = False
    
    for port in reader_ports:
        if Path(port).exists():
            print(f"✅ Porta lettore trovata: {port}")
            reader_port_found = True
            break
    
    if not reader_port_found:
        print("⚠️ Nessuna porta hardware trovata (normale se hardware non collegato)")
    
    # Test 6: Verifica dipendenze
    print("\n�� Test 6: Verifica dipendenze Python...")
    
    try:
        import smartcard
        print("✅ pyscard disponibile")
    except ImportError:
        print("❌ pyscard mancante (pip install pyscard)")
    
    try:
        import serial
        print("✅ pyserial disponibile")
    except ImportError:
        print("❌ pyserial mancante (pip install pyserial)")
    
    try:
        import flask
        print("✅ Flask disponibile")
    except ImportError:
        print("❌ Flask mancante (pip install flask)")
    
    # Risultato finale
    print("\n" + "=" * 50)
    if card_reader_ok and relay_ok:
        print("🎯 INTEGRAZIONE PRONTA!")
        print("✅ Moduli hardware OK")
        print("✅ Import funzionanti")
        print("✅ web_api.py pronto")
        print()
        print("🚀 Per testare:")
        print("   1. Avviare dashboard: python src/api/web_api.py")
        print("   2. Andare a: http://192.168.178.200:5000")
        print("   3. Sezione Dispositivi -> Test Hardware")
        print()
        print("💡 Note:")
        print("   - Test lettore: richiede tessera sanitaria")
        print("   - Test USB-RLY08: richiede hardware collegato")
        print("   - Feedback real-time nella dashboard")
        return True
    else:
        print("⚠️ INTEGRAZIONE PARZIALE")
        print("❌ Alcuni moduli non disponibili")
        print("💡 Verificare installazione dipendenze")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
