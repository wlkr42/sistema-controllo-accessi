# File: /opt/access_control/scripts/test_usb_rly08.py
# Test base comunicazione USB-RLY08

import serial
import time
import sys

def test_usb_rly08():
    """Test comunicazione base USB-RLY08"""
    
    print("🔧 TEST USB-RLY08 BASIC COMMUNICATION")
    print("=" * 50)
    
    try:
        # Connessione seriale
        # Nota: Baudrate 19200 come da documentazione
        port = "/dev/ttyACM0"
        baudrate = 19200
        
        print(f"🔌 Connessione a {port} @ {baudrate} baud...")
        
        relay = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_TWO,  # 2 stop bits come da manuale
            timeout=2
        )
        
        print("✅ Connessione seriale OK")
        time.sleep(0.5)  # Stabilizzazione
        
        # Test 1: Get Software Version (comando 90 = 0x5A)
        print("\n📋 Test 1: Get Software Version")
        relay.write(bytes([90]))  # Comando 0x5A
        time.sleep(0.1)
        
        response = relay.read(2)  # Aspetta 2 bytes
        if len(response) == 2:
            module_id = response[0]
            software_version = response[1]
            print(f"✅ Module ID: {module_id}")
            print(f"✅ Software Version: {software_version}")
            
            if module_id == 8:
                print("🎯 CONFERMATO: Modulo USB-RLY08 riconosciuto!")
            else:
                print(f"⚠️ Module ID inaspettato: {module_id} (atteso: 8)")
        else:
            print(f"❌ Risposta inaspettata: {len(response)} bytes (attesi: 2)")
            print(f"   Dati: {response.hex() if response else 'None'}")
        
        # Test 2: Get Relay States (comando 91 = 0x5B)
        print("\n📋 Test 2: Get Relay States")
        relay.write(bytes([91]))  # Comando 0x5B
        time.sleep(0.1)
        
        response = relay.read(1)  # Aspetta 1 byte
        if len(response) == 1:
            state = response[0]
            print(f"✅ Stato relè (byte): {state} (0x{state:02X})")
            print(f"✅ Stato relè (binario): {state:08b}")
            
            # Decodifica stato singoli relè
            for i in range(8):
                relay_on = bool(state & (1 << i))
                print(f"   Relè {i+1}: {'ON' if relay_on else 'OFF'}")
        else:
            print(f"❌ Risposta inaspettata: {len(response)} bytes")
        
        # Test 3: Test sicuro - Accendi/spegni Relè 1 brevemente
        print("\n📋 Test 3: Test Relè 1 (ON/OFF)")
        print("⚠️ ATTENZIONE: Test relè per 2 secondi")
        
        # Accendi Relè 1 (comando 101 = 0x65)
        print("🔆 Accendo Relè 1...")
        relay.write(bytes([101]))
        time.sleep(2)
        
        # Spegni Relè 1 (comando 111 = 0x6F)
        print("💡 Spengo Relè 1...")
        relay.write(bytes([111]))
        
        # Verifica stato finale
        print("\n📋 Test 4: Verifica stato finale")
        relay.write(bytes([91]))  # Get states
        time.sleep(0.1)
        response = relay.read(1)
        if len(response) == 1:
            final_state = response[0]
            print(f"✅ Stato finale: {final_state:08b}")
            
            if final_state == 0:
                print("🎯 PERFETTO: Tutti i relè sono spenti")
            else:
                print(f"⚠️ Alcuni relè ancora accesi: 0x{final_state:02X}")
        
        # Chiudi connessione
        relay.close()
        print("\n✅ Test completato con successo!")
        print("🎯 USB-RLY08 è operativo e pronto per integrazione")
        
        return True
        
    except serial.SerialException as e:
        print(f"❌ Errore seriale: {e}")
        print("💡 Soluzioni:")
        print("   1. Verifica connessione USB")
        print("   2. Aggiungi utente al gruppo dialout:")
        print("      sudo usermod -a -G dialout $USER")
        print("   3. Riavvia sessione (logout/login)")
        return False
        
    except Exception as e:
        print(f"❌ Errore generico: {e}")
        return False

def test_all_relays_safe():
    """Test sicuro di tutti i relè (lampeggio veloce)"""
    
    print("\n🔧 TEST SICURO TUTTI I RELÈ")
    print("=" * 50)
    
    try:
        relay = serial.Serial(
            port="/dev/ttyACM0",
            baudrate=19200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_TWO,
            timeout=2
        )
        
        # Prima spegni tutto
        print("💡 Spegnimento tutti i relè...")
        relay.write(bytes([110]))  # All relays OFF
        time.sleep(0.5)
        
        # Test sequenziale rapido di ogni relè
        for relay_num in range(1, 9):
            print(f"🔆 Test Relè {relay_num}...")
            
            # Accendi relè
            on_command = 100 + relay_num  # 101-108
            relay.write(bytes([on_command]))
            time.sleep(0.3)  # Solo 300ms acceso
            
            # Spegni relè  
            off_command = 110 + relay_num  # 111-118
            relay.write(bytes([off_command]))
            time.sleep(0.2)
        
        print("✅ Test tutti i relè completato")
        relay.close()
        return True
        
    except Exception as e:
        print(f"❌ Errore test relè: {e}")
        return False

if __name__ == "__main__":
    print("🏗️ SISTEMA CONTROLLO ACCESSI - TEST USB-RLY08")
    print(f"⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test base
    if test_usb_rly08():
        print("\n" + "=" * 50)
        
        # Chiedi se fare test tutti i relè
        response = input("🔧 Vuoi testare tutti i relè? (y/n): ").lower().strip()
        if response in ['y', 'yes', 's', 'si']:
            test_all_relays_safe()
    
    print("\n🏁 Test terminato")