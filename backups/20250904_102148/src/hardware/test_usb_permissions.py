#!/usr/bin/env python3
"""
Script per testare e diagnosticare problemi di permessi USB per CRT-285
"""
import ctypes
import subprocess
import sys
import os

def check_device():
    """Verifica presenza dispositivo"""
    print("1. VERIFICA DISPOSITIVO")
    print("-" * 40)
    
    result = subprocess.run(['lsusb'], capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if '23d8:0285' in line or 'CRT-285' in line:
            print(f"✅ Dispositivo trovato: {line}")
            
            # Estrai bus e device
            parts = line.split()
            bus = parts[1]
            device = parts[3].rstrip(':')
            device_path = f"/dev/bus/usb/{bus}/{device}"
            
            # Verifica permessi
            if os.path.exists(device_path):
                import stat
                st = os.stat(device_path)
                mode = oct(st.st_mode)[-3:]
                print(f"   Path: {device_path}")
                print(f"   Permessi: {mode}")
                
                if mode == '666':
                    print("   ✅ Permessi corretti (666)")
                else:
                    print(f"   ⚠️ Permessi insufficienti ({mode}), servono 666")
            
            return True
    
    print("❌ Dispositivo non trovato!")
    return False

def check_library():
    """Verifica libreria"""
    print("\n2. VERIFICA LIBRERIA")
    print("-" * 40)
    
    lib_path = '/usr/local/lib/crt_288x_ur.so'
    if os.path.exists(lib_path):
        print(f"✅ Libreria trovata: {lib_path}")
        
        # Verifica permessi
        st = os.stat(lib_path)
        mode = oct(st.st_mode)[-3:]
        print(f"   Permessi: {mode}")
        return True
    else:
        print(f"❌ Libreria non trovata: {lib_path}")
        return False

def test_connection():
    """Test connessione con diverse modalità"""
    print("\n3. TEST CONNESSIONE")
    print("-" * 40)
    
    try:
        # Carica libreria
        lib = ctypes.CDLL('/usr/local/lib/crt_288x_ur.so')
        print("✅ Libreria caricata")
        
        # Setup funzione
        lib.CRT288x_OpenConnection.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_long]
        lib.CRT288x_OpenConnection.restype = ctypes.c_int
        
        # Test connessione standard
        print("\nTest 1: Connessione standard (0, 0, 9600)...")
        result = lib.CRT288x_OpenConnection(0, 0, 9600)
        print(f"   Risultato: {result}")
        
        if result == 0:
            print("   ✅ Connessione riuscita!")
            lib.CRT288x_CloseConnection()
            return True
        elif result == -2:
            print("   ❌ Errore -2: Device not found o permission denied")
            print("   Suggerimento: Provare con sudo o verificare regole udev")
        elif result == -5:
            print("   ❌ Errore -5: Permission denied")
            print("   Suggerimento: Aggiungere regola udev o eseguire con sudo")
        else:
            print(f"   ❌ Errore sconosciuto: {result}")
        
        # Test con altri parametri
        print("\nTest 2: Connessione USB mode (1, 0, 0)...")
        result = lib.CRT288x_OpenConnection(1, 0, 0)
        print(f"   Risultato: {result}")
        
        if result == 0:
            print("   ✅ Connessione riuscita con USB mode!")
            lib.CRT288x_CloseConnection()
            return True
            
    except Exception as e:
        print(f"❌ Errore caricamento/esecuzione: {e}")
        return False
    
    return False

def check_user_groups():
    """Verifica gruppi utente"""
    print("\n4. VERIFICA GRUPPI UTENTE")
    print("-" * 40)
    
    import grp
    import pwd
    
    user = os.environ.get('USER', pwd.getpwuid(os.getuid()).pw_name)
    print(f"Utente: {user}")
    
    groups = [g.gr_name for g in grp.getgrall() if user in g.gr_mem]
    gid = pwd.getpwnam(user).pw_gid
    groups.append(grp.getgrgid(gid).gr_name)
    
    required_groups = ['plugdev', 'dialout']
    for req_group in required_groups:
        if req_group in groups:
            print(f"✅ Utente nel gruppo {req_group}")
        else:
            print(f"❌ Utente NON nel gruppo {req_group}")
            print(f"   Eseguire: sudo usermod -a -G {req_group} $USER")

def suggest_fixes():
    """Suggerimenti per risolvere i problemi"""
    print("\n5. SUGGERIMENTI FIX")
    print("-" * 40)
    
    print("""
1. REGOLA UDEV (richiede sudo):
   Creare file /etc/udev/rules.d/99-crt285.rules con:
   
   SUBSYSTEM=="usb", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", MODE="0666", GROUP="plugdev"
   
   Poi eseguire:
   sudo udevadm control --reload-rules
   sudo udevadm trigger

2. FIX TEMPORANEO (richiede sudo):
   Trovare il device e cambiare permessi:
   
   sudo chmod 666 /dev/bus/usb/001/003  # Sostituire con path corretto
   
3. ESECUZIONE CON SUDO:
   Come workaround temporaneo:
   
   sudo python3 src/hardware/crt285_reader.py
   
4. ALTERNATIVE LIBRARY PATH:
   Se la libreria ha problemi, provare:
   
   export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
   python3 src/hardware/crt285_reader.py
""")

def main():
    print("="*50)
    print("DIAGNOSTICA PERMESSI CRT-285")
    print("="*50)
    
    # Esegui tutti i test
    device_ok = check_device()
    library_ok = check_library()
    check_user_groups()
    
    if device_ok and library_ok:
        connection_ok = test_connection()
        
        if connection_ok:
            print("\n✅ TUTTO OK! Il lettore dovrebbe funzionare.")
        else:
            print("\n⚠️ PROBLEMA DI PERMESSI RILEVATO")
            suggest_fixes()
    else:
        print("\n❌ PROBLEMI HARDWARE/SOFTWARE RILEVATI")
        if not device_ok:
            print("   - Verificare connessione USB del dispositivo")
        if not library_ok:
            print("   - Installare la libreria crt_288x_ur.so")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    main()