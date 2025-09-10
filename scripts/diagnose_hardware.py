#!/usr/bin/env python3
"""
Script diagnostica hardware CRT-285
Analizza perché il lettore si disconnette continuamente
"""

import os
import sys
import time
import ctypes
import subprocess
import signal

def check_usb_device():
    """Verifica presenza dispositivo USB"""
    print("1. Controllo dispositivo USB...")
    result = subprocess.run(["lsusb"], capture_output=True, text=True)
    
    crt_found = False
    for line in result.stdout.split('\n'):
        if '23d8:0285' in line or 'CRT-285' in line:
            print(f"   ✓ Trovato: {line.strip()}")
            crt_found = True
            
    if not crt_found:
        print("   ✗ CRT-285 NON trovato via USB")
    return crt_found

def check_library():
    """Verifica presenza libreria .so"""
    print("\n2. Controllo libreria driver...")
    lib_paths = [
        "/opt/access_control/src/drivers/288K/linux_crt_288x/drivers/x64/crt_288x_ur.so",
        "/opt/access_control/src/drivers/crt_288x_ur.so",
        "./crt_288x_ur.so"
    ]
    
    found_lib = None
    for path in lib_paths:
        if os.path.exists(path):
            print(f"   ✓ Trovata: {path}")
            # Verifica permessi
            stat_info = os.stat(path)
            print(f"     - Dimensione: {stat_info.st_size} bytes")
            print(f"     - Permessi: {oct(stat_info.st_mode)[-3:]}")
            found_lib = path
            break
    
    if not found_lib:
        print("   ✗ Libreria NON trovata")
    return found_lib

def test_library_load(lib_path):
    """Test caricamento libreria"""
    print("\n3. Test caricamento libreria...")
    try:
        lib = ctypes.CDLL(lib_path)
        print("   ✓ Libreria caricata con successo")
        
        # Verifica funzioni disponibili
        functions = [
            "CRT288x_OpenConnection",
            "CRT288x_CloseConnection", 
            "CRT288x_InitDev",
            "CRT288x_GetCardStatus"
        ]
        
        for func_name in functions:
            try:
                func = getattr(lib, func_name)
                print(f"   ✓ Funzione {func_name} disponibile")
            except AttributeError:
                print(f"   ✗ Funzione {func_name} NON trovata")
                
        return lib
    except Exception as e:
        print(f"   ✗ Errore caricamento: {e}")
        return None

def test_connection_simple(lib):
    """Test connessione semplice senza loop"""
    print("\n4. Test connessione singola (NO LOOP)...")
    
    try:
        # Setup timeout per evitare hang
        signal.signal(signal.SIGALRM, lambda n, s: None)
        signal.alarm(5)  # Timeout 5 secondi
        
        print("   Tentativo apertura connessione...")
        result = lib.CRT288x_OpenConnection(0, 0, 9600)
        
        signal.alarm(0)  # Cancella timeout
        
        if result == 0:
            print("   ✓ Connessione aperta con successo!")
            
            # Chiudi subito
            print("   Chiusura connessione...")
            lib.CRT288x_CloseConnection()
            print("   ✓ Connessione chiusa")
            return True
        else:
            print(f"   ✗ Apertura fallita, codice: {result}")
            return False
            
    except Exception as e:
        signal.alarm(0)
        print(f"   ✗ Errore durante test: {e}")
        return False

def check_dmesg():
    """Controlla messaggi kernel recenti"""
    print("\n5. Controllo messaggi kernel (ultimi 20)...")
    result = subprocess.run(
        ["sudo", "dmesg", "-T"], 
        capture_output=True, 
        text=True
    )
    
    lines = result.stdout.split('\n')[-20:]
    usb_errors = []
    
    for line in lines:
        if any(x in line.lower() for x in ['usb', 'crt', '285', 'disconnect', 'error']):
            usb_errors.append(line.strip())
            
    if usb_errors:
        print("   Messaggi USB rilevanti:")
        for err in usb_errors[-5:]:  # Ultimi 5
            print(f"   - {err}")
    else:
        print("   Nessun errore USB recente")

def check_libusb():
    """Verifica versione libusb"""  
    print("\n6. Controllo libusb...")
    
    # Verifica pacchetti installati
    result = subprocess.run(
        ["dpkg", "-l", "|", "grep", "libusb"],
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        for line in result.stdout.split('\n'):
            if 'libusb' in line:
                print(f"   {line.strip()}")
    
    # Verifica file .so
    libusb_paths = [
        "/usr/lib/x86_64-linux-gnu/libusb-1.0.so",
        "/lib/x86_64-linux-gnu/libusb-1.0.so"
    ]
    
    for path in libusb_paths:
        if os.path.exists(path):
            print(f"   ✓ Trovato: {path}")

def main():
    print("=" * 60)
    print("DIAGNOSTICA HARDWARE CRT-285")
    print("=" * 60)
    
    # 1. Check USB
    usb_ok = check_usb_device()
    
    # 2. Check library
    lib_path = check_library()
    
    if lib_path:
        # 3. Load library
        lib = test_library_load(lib_path)
        
        if lib and usb_ok:
            # 4. Test connection (single, no loop)
            test_connection_simple(lib)
    
    # 5. Check dmesg
    check_dmesg()
    
    # 6. Check libusb
    check_libusb()
    
    print("\n" + "=" * 60)
    print("DIAGNOSTICA COMPLETATA")
    print("=" * 60)
    
    if not usb_ok:
        print("\n⚠️  PROBLEMA: Dispositivo USB non rilevato")
        print("   Soluzioni:")
        print("   - Verificare cavo USB")
        print("   - Provare altra porta USB")
        print("   - Controllare alimentazione dispositivo")
    
    if not lib_path:
        print("\n⚠️  PROBLEMA: Libreria driver non trovata")
        print("   Soluzioni:")
        print("   - Reinstallare con: bash scripts/install/install_system.sh")

if __name__ == "__main__":
    main()