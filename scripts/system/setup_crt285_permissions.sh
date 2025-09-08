#!/bin/bash

# Script per configurare i permessi del lettore CRT-285
# Risolve il problema libusb_detach_kernel_driver -5

echo "🔧 CONFIGURAZIONE PERMESSI CRT-285/288K"
echo "========================================"

# 1. Verifica se siamo root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Questo script deve essere eseguito con sudo"
    echo "    Uso: sudo $0"
    exit 1
fi

# 2. Aggiungi utente ai gruppi necessari
CURRENT_USER=${SUDO_USER:-$USER}
echo "👤 Configurazione utente: $CURRENT_USER"

usermod -a -G plugdev,dialout $CURRENT_USER 2>/dev/null
echo "   ✅ Aggiunto ai gruppi plugdev e dialout"

# 3. Crea regole udev per CRT-285
echo "📝 Creazione regole udev..."

cat > /etc/udev/rules.d/99-crt285.rules << 'EOF'
# CRT-285/288K Smart Card Reader USB Rules
# Permette accesso senza sudo al dispositivo

# USB device rules - CREATOR(CHINA)TECH CRT-285
SUBSYSTEM=="usb", ATTR{idVendor}=="23d8", ATTR{idProduct}=="0285", MODE="0666", GROUP="plugdev", TAG+="uaccess"
SUBSYSTEM=="usb_device", ATTR{idVendor}=="23d8", ATTR{idProduct}=="0285", MODE="0666", GROUP="plugdev"

# HID raw device (if applicable)
KERNEL=="hidraw*", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", MODE="0666", GROUP="plugdev", TAG+="uaccess"

# Disable autosuspend for better stability
SUBSYSTEM=="usb", ATTR{idVendor}=="23d8", ATTR{idProduct}=="0285", ATTR{power/autosuspend}="-1"

# Alternative rules for all subsystems
SUBSYSTEMS=="usb", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", MODE="0666", GROUP="plugdev"

# Unbind from HID driver if needed (prevents detach_kernel_driver errors)
ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="23d8", ATTR{idProduct}=="0285", RUN+="/bin/sh -c 'echo -n $kernel > /sys/bus/usb/drivers/usbhid/unbind || true'"
EOF

echo "   ✅ Regole udev create"

# 4. Ricarica regole udev
echo "🔄 Ricarica regole udev..."
udevadm control --reload-rules
udevadm trigger --subsystem-match=usb
echo "   ✅ Regole ricaricate"

# 5. Trova e configura il dispositivo CRT-285
echo "🔍 Ricerca dispositivo CRT-285..."

DEVICE_INFO=$(lsusb -d 23d8:0285 2>/dev/null)
if [ -n "$DEVICE_INFO" ]; then
    echo "   ✅ Dispositivo trovato: $DEVICE_INFO"
    
    # Estrai bus e device number
    BUS=$(echo $DEVICE_INFO | sed 's/Bus \([0-9]*\).*/\1/')
    DEV=$(echo $DEVICE_INFO | sed 's/.*Device \([0-9]*\):.*/\1/')
    
    # Imposta permessi immediati
    DEVICE_PATH="/dev/bus/usb/$BUS/$DEV"
    if [ -e "$DEVICE_PATH" ]; then
        chmod 666 "$DEVICE_PATH"
        chown root:plugdev "$DEVICE_PATH"
        echo "   ✅ Permessi impostati su $DEVICE_PATH"
    fi
    
    # Unbind da HID driver se necessario
    for SYSFS_DEV in /sys/bus/usb/devices/*; do
        if [ -f "$SYSFS_DEV/idVendor" ] && [ -f "$SYSFS_DEV/idProduct" ]; then
            VENDOR=$(cat "$SYSFS_DEV/idVendor" 2>/dev/null)
            PRODUCT=$(cat "$SYSFS_DEV/idProduct" 2>/dev/null)
            
            if [ "$VENDOR" = "23d8" ] && [ "$PRODUCT" = "0285" ]; then
                DEV_NAME=$(basename "$SYSFS_DEV")
                
                # Controlla se è bindato a usbhid
                if [ -L "$SYSFS_DEV/driver" ]; then
                    DRIVER=$(readlink "$SYSFS_DEV/driver" | xargs basename)
                    if [ "$DRIVER" = "usbhid" ]; then
                        echo "   🔧 Unbinding da driver HID..."
                        echo "$DEV_NAME" > /sys/bus/usb/drivers/usbhid/unbind 2>/dev/null || true
                        echo "   ✅ Driver HID unbindato"
                    fi
                fi
            fi
        fi
    done
else
    echo "   ⚠️  Dispositivo CRT-285 non trovato (collegarlo e riprovare)"
fi

# 6. Crea link simbolico se necessario
if [ ! -e /dev/ttyACM0 ] && [ -e /dev/bus/usb ]; then
    echo "🔗 Creazione link simbolico /dev/ttyACM0..."
    # Questo è solo un placeholder - il device reale potrebbe non essere ttyACM0
    echo "   ℹ️  Link simbolico non necessario per dispositivo USB diretto"
fi

# 7. Installa servizio systemd (opzionale)
if [ -f /opt/access_control/access-control-web.service ]; then
    echo "🚀 Installazione servizio systemd..."
    cp /opt/access_control/access-control-web.service /etc/systemd/system/
    systemctl daemon-reload
    echo "   ✅ Servizio installato (usare 'systemctl start access-control-web' per avviare)"
fi

echo ""
echo "========================================"
echo "✅ CONFIGURAZIONE COMPLETATA!"
echo ""
echo "⚠️  IMPORTANTE:"
echo "1. Logout e login per applicare i gruppi all'utente"
echo "2. O eseguire: newgrp plugdev"
echo "3. Riavviare il web server dopo il logout/login"
echo ""
echo "🧪 Per testare:"
echo "   python /opt/access_control/src/hardware/crt285_reader.py"
echo ""
echo "🌐 Per avviare il web server:"
echo "   cd /opt/access_control"
echo "   python src/api/web_api.py"
echo ""