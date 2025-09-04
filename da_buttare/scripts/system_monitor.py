#!/usr/bin/env python3
# File: /opt/access_control/scripts/system_monitor.py
# Monitor sistema controllo accessi

import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path("/opt/access_control")

def check_service():
    """Verifica stato servizio"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'access-control'], 
                              capture_output=True, text=True)
        return result.stdout.strip() == 'active'
    except:
        return False

def check_web():
    """Verifica dashboard web"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        return result == 0
    except:
        return False

def main():
    print("🔍 STATO SISTEMA CONTROLLO ACCESSI")
    print("=" * 40)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Verifica servizio
    service_ok = check_service()
    print(f"🔧 Servizio: {'✅ ATTIVO' if service_ok else '❌ INATTIVO'}")
    
    # Verifica web
    web_ok = check_web()
    print(f"🌐 Dashboard: {'✅ DISPONIBILE' if web_ok else '❌ NON DISPONIBILE'}")
    
    # Verifica hardware
    pcscd_ok = subprocess.run(['systemctl', 'is-active', 'pcscd'], 
                            capture_output=True).returncode == 0
    print(f"🔌 PCSCD: {'✅ ATTIVO' if pcscd_ok else '❌ INATTIVO'}")
    
    # USB devices
    usb_devices = list(Path('/dev').glob('ttyACM*')) + list(Path('/dev').glob('ttyUSB*'))
    print(f"🔌 USB: {len(usb_devices)} dispositivi rilevati")
    
    print()
    
    if service_ok and web_ok:
        print("✅ SISTEMA OPERATIVO")
        print("🌐 URL: http://192.168.178.200:5000")
        print("👤 Login: admin/admin123")
    else:
        print("⚠️  SISTEMA NON COMPLETAMENTE OPERATIVO")
        print("🔧 Riavvia con: sudo restart-access-control")
    
    print("=" * 40)

if __name__ == "__main__":
    main()
