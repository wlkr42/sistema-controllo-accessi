#!/bin/bash

echo "🔧 FIX PERMESSI USB CRT-285/288"
echo "================================"

# 1. Crea regole udev corrette
echo "📝 Creazione regole udev..."
sudo tee /etc/udev/rules.d/99-crt288x.rules > /dev/null << 'EOF'
# CRT288x Smart Card Reader Rules
# Vendor ID: 23d8, Product ID: 0285

# USB device rules
SUBSYSTEM=="usb", ATTR{idVendor}=="23d8", ATTR{idProduct}=="0285", MODE="0666", GROUP="plugdev", TAG+="uaccess"
SUBSYSTEM=="usb_device", ATTR{idVendor}=="23d8", ATTR{idProduct}=="0285", MODE="0666", GROUP="plugdev"

# TTY device rules (for serial communication)
KERNEL=="ttyUSB*", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", MODE="0666", GROUP="plugdev", TAG+="uaccess"
KERNEL=="ttyACM*", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", MODE="0666", GROUP="plugdev", TAG+="uaccess"

# HID device rules (if applicable)
KERNEL=="hidraw*", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", MODE="0666", GROUP="plugdev", TAG+="uaccess"

# Alternative rules for different subsystems
SUBSYSTEMS=="usb", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", MODE="0666", GROUP="plugdev"

# Disable autosuspend for better performance
SUBSYSTEM=="usb", ATTR{idVendor}=="23d8", ATTR{idProduct}=="0285", ATTR{power/autosuspend}="-1"
EOF

echo "✅ Regole udev create"

# 2. Ricarica regole udev
echo "🔄 Ricarica regole udev..."
sudo udevadm control --reload-rules
sudo udevadm trigger

# 3. Aggiungi utente ai gruppi necessari
echo "👤 Aggiunta utente ai gruppi..."
sudo usermod -a -G plugdev,dialout $USER

# 4. Verifica dispositivo
echo ""
echo "🔍 Verifica dispositivo..."
if lsusb | grep -q "23d8:0285"; then
    echo "✅ Dispositivo CRT-285 rilevato:"
    lsusb | grep "23d8:0285"
else
    echo "⚠️ Dispositivo non rilevato. Assicurarsi che sia collegato."
fi

# 5. Verifica gruppi
echo ""
echo "👥 Gruppi utente corrente:"
groups $USER

echo ""
echo "================================"
echo "✅ CONFIGURAZIONE COMPLETATA!"
echo ""
echo "⚠️ IMPORTANTE:"
echo "1. Scollegare e ricollegare il lettore CRT-285"
echo "2. Se il problema persiste, fare logout e login"
echo "3. Ora prova di nuovo i test con sudo"
echo ""