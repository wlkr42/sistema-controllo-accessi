#!/bin/bash

# Script completo per fix hardware su sistemi remoti
# Deve funzionare al primo colpo senza intervento manuale

set -e

echo "========================================="
echo "FIX HARDWARE SISTEMA REMOTO v1.0"
echo "========================================="

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Stop servizio per evitare conflitti
echo -e "${YELLOW}1. Arresto servizio...${NC}"
sudo systemctl stop access-control-web 2>/dev/null || true
sudo systemctl stop access-monitor 2>/dev/null || true
sleep 2

# 2. Fix permessi USB per CRT-285
echo -e "${YELLOW}2. Configurazione permessi USB...${NC}"

# Crea regole udev complete
sudo tee /etc/udev/rules.d/99-crt285.rules > /dev/null << 'EOF'
# CRT-285 Card Reader - Permessi completi
SUBSYSTEM=="usb", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", MODE="0666"
SUBSYSTEM=="usb", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", OWNER="root", GROUP="plugdev"

# Previeni binding driver kernel
SUBSYSTEM=="usb", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", RUN+="/bin/sh -c 'echo -n $kernel > /sys/bus/usb/drivers/usb/unbind'"
EOF

# Regole per USB-RLY08 (relè)
sudo tee /etc/udev/rules.d/99-usb-relay.rules > /dev/null << 'EOF'
# USB-RLY08 Relay Controller
SUBSYSTEM=="tty", ATTRS{idVendor}=="04d8", MODE="0666", GROUP="dialout"
KERNEL=="ttyACM[0-9]*", MODE="0666", GROUP="dialout"
EOF

# Reload udev
sudo udevadm control --reload-rules
sudo udevadm trigger

# 3. Reset dispositivi USB
echo -e "${YELLOW}3. Reset dispositivi USB...${NC}"

# Reset CRT-285 se presente
if lsusb | grep -q "23d8:0285"; then
    echo "   CRT-285 trovato, reset in corso..."
    for dev in /sys/bus/usb/devices/*/idVendor; do
        if [ -f "$dev" ] && [ "$(cat $dev 2>/dev/null)" = "23d8" ]; then
            device_path=$(dirname "$dev")
            if [ -f "$device_path/idProduct" ] && [ "$(cat $device_path/idProduct)" = "0285" ]; then
                echo "   Unbind device..."
                echo "$(basename $device_path)" | sudo tee /sys/bus/usb/drivers/usb/unbind > /dev/null 2>&1 || true
                sleep 2
                echo "   Rebind device..."
                echo "$(basename $device_path)" | sudo tee /sys/bus/usb/drivers/usb/bind > /dev/null 2>&1 || true
            fi
        fi
    done
else
    echo -e "   ${RED}CRT-285 non trovato${NC}"
fi

# 4. Fix libreria driver
echo -e "${YELLOW}4. Fix libreria driver...${NC}"
LIB_PATH="/opt/access_control/src/drivers/288K/linux_crt_288x/drivers/x64/crt_288x_ur.so"
if [ -f "$LIB_PATH" ]; then
    sudo chmod 755 "$LIB_PATH"
    echo -e "   ${GREEN}✓ Permessi libreria corretti${NC}"
else
    echo -e "   ${RED}✗ Libreria non trovata!${NC}"
fi

# 5. Installazione dipendenze libusb se mancanti
echo -e "${YELLOW}5. Verifica dipendenze libusb...${NC}"
if ! dpkg -l | grep -q "libusb-1.0-0-dev"; then
    echo "   Installazione libusb-dev..."
    sudo apt-get update > /dev/null 2>&1
    sudo apt-get install -y libusb-1.0-0-dev > /dev/null 2>&1
fi

# 6. Configurazione servizio come root
echo -e "${YELLOW}6. Configurazione servizio...${NC}"
sudo tee /etc/systemd/system/access-control-web.service > /dev/null << 'EOF'
[Unit]
Description=Access Control Web API Service
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/access_control
Environment="PATH=/opt/access_control/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="PYTHONPATH=/opt/access_control/src"
Environment="PYTHONUNBUFFERED=1"

ExecStart=/opt/access_control/venv/bin/python /opt/access_control/src/api/web_api.py

PrivateDevices=no
PrivilegedAccess=yes

StartLimitInterval=0
StartLimitBurst=10

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload

# 7. Creazione script test hardware
echo -e "${YELLOW}7. Creazione script test...${NC}"
cat > /tmp/test_hardware.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
import time
import ctypes
import serial
import serial.tools.list_ports

print("\n=== TEST HARDWARE ===\n")

# Test CRT-285
print("1. Test CRT-285 Card Reader:")
lib_path = "/opt/access_control/src/drivers/288K/linux_crt_288x/drivers/x64/crt_288x_ur.so"
try:
    lib = ctypes.CDLL(lib_path)
    result = lib.CRT288x_OpenConnection(0, 0, 9600)
    if result == 0:
        print("   ✓ CRT-285 connesso correttamente")
        lib.CRT288x_CloseConnection()
    else:
        print(f"   ✗ CRT-285 errore connessione: {result}")
except Exception as e:
    print(f"   ✗ CRT-285 errore: {e}")

# Test Relè
print("\n2. Test USB-RLY08 Relay:")
ports = list(serial.tools.list_ports.comports())
relay_found = False
for port in ports:
    if "ACM" in port.device:
        print(f"   Trovata porta: {port.device}")
        try:
            ser = serial.Serial(port.device, 19200, timeout=1)
            ser.write(b'\x5A')  # Get module ID
            response = ser.read(1)
            if response:
                print(f"   ✓ Relè risponde su {port.device}")
                relay_found = True
            ser.close()
        except:
            pass

if not relay_found:
    print("   ✗ Relè non trovato su porte ACM")

print("\n=== FINE TEST ===\n")
EOF

chmod +x /tmp/test_hardware.py

# 8. Avvio servizi
echo -e "${YELLOW}8. Avvio servizi...${NC}"
sudo systemctl start access-control-web
sleep 3

# 9. Verifica stato
echo -e "${YELLOW}9. Verifica stato servizio...${NC}"
if systemctl is-active --quiet access-control-web; then
    echo -e "   ${GREEN}✓ Servizio attivo${NC}"
else
    echo -e "   ${RED}✗ Servizio non attivo${NC}"
    sudo journalctl -u access-control-web --no-pager -n 20
fi

# 10. Test hardware
echo -e "${YELLOW}10. Test hardware...${NC}"
sudo python3 /tmp/test_hardware.py

# 11. Test API
echo -e "${YELLOW}11. Test API...${NC}"
if curl -s http://localhost:5000/api/health | grep -q "healthy"; then
    echo -e "   ${GREEN}✓ API risponde correttamente${NC}"
else
    echo -e "   ${RED}✗ API non risponde${NC}"
fi

echo ""
echo "========================================="
echo -e "${GREEN}FIX COMPLETATO${NC}"
echo "========================================="
echo ""
echo "Hardware status:"
lsusb | grep -E "(23d8|0285|Devantech|04d8)" || echo "Nessun hardware USB trovato"
ls -la /dev/ttyACM* 2>/dev/null || echo "Nessuna porta ACM trovata"

echo ""
echo "Per verificare i log:"
echo "  sudo journalctl -u access-control-web -f"