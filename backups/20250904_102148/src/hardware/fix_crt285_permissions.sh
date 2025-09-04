#!/bin/bash
#
# Script per risolvere problemi di permessi USB per lettore CRT-285
# 

echo "🔧 FIX PERMESSI LETTORE CRT-285"
echo "================================"

# Controlla se eseguito come root
if [ "$EUID" -eq 0 ]; then
   SUDO=""
else
   SUDO="sudo"
   echo "⚠️  Richiesti permessi amministratore"
fi

# 1. Verifica dispositivo
echo -e "\n1️⃣ Verifica dispositivo USB..."
if lsusb | grep -q "23d8:0285"; then
    echo "✅ Dispositivo CRT-285 trovato"
    DEVICE_INFO=$(lsusb | grep "23d8:0285")
    echo "   $DEVICE_INFO"
else
    echo "❌ Dispositivo non trovato! Verificare connessione USB"
    exit 1
fi

# 2. Crea regola udev
echo -e "\n2️⃣ Creazione regola udev..."
UDEV_RULE="/etc/udev/rules.d/99-crt285.rules"

# Crea la regola
echo "# Regola per lettore CRT-285
SUBSYSTEM==\"usb\", ATTRS{idVendor}==\"23d8\", ATTRS{idProduct}==\"0285\", MODE=\"0666\", GROUP=\"plugdev\"
# Permetti accesso diretto senza detach del kernel driver
SUBSYSTEM==\"usb\", ATTRS{idVendor}==\"23d8\", ATTRS{idProduct}==\"0285\", ENV{DEVTYPE}==\"usb_device\", MODE=\"0666\"" | $SUDO tee $UDEV_RULE > /dev/null

if [ -f "$UDEV_RULE" ]; then
    echo "✅ Regola udev creata: $UDEV_RULE"
else
    echo "❌ Errore creazione regola udev"
    exit 1
fi

# 3. Ricarica regole udev
echo -e "\n3️⃣ Ricaricamento regole udev..."
$SUDO udevadm control --reload-rules
$SUDO udevadm trigger --subsystem-match=usb
echo "✅ Regole udev ricaricate"

# 4. Verifica gruppi utente
echo -e "\n4️⃣ Verifica gruppi utente..."
CURRENT_USER=${USER:-$(whoami)}
echo "   Utente: $CURRENT_USER"

if groups $CURRENT_USER | grep -q plugdev; then
    echo "✅ Utente già nel gruppo plugdev"
else
    echo "⚠️  Aggiunta utente al gruppo plugdev..."
    $SUDO usermod -a -G plugdev $CURRENT_USER
    echo "✅ Utente aggiunto al gruppo plugdev"
    echo "⚠️  IMPORTANTE: Riloggare o eseguire: newgrp plugdev"
fi

if groups $CURRENT_USER | grep -q dialout; then
    echo "✅ Utente già nel gruppo dialout"
else
    echo "⚠️  Aggiunta utente al gruppo dialout..."
    $SUDO usermod -a -G dialout $CURRENT_USER
    echo "✅ Utente aggiunto al gruppo dialout"
fi

# 5. Verifica libreria
echo -e "\n5️⃣ Verifica libreria..."
LIB_PATH="/usr/local/lib/crt_288x_ur.so"
if [ -f "$LIB_PATH" ]; then
    echo "✅ Libreria trovata: $LIB_PATH"
    ls -la $LIB_PATH
else
    echo "❌ Libreria non trovata!"
    echo "   Verificare installazione in: $LIB_PATH"
fi

# 6. Fix permessi immediati
echo -e "\n6️⃣ Fix permessi dispositivo attuale..."
# Trova il device bus/number
BUS=$(lsusb | grep "23d8:0285" | awk '{print $2}')
DEVICE=$(lsusb | grep "23d8:0285" | awk '{print $4}' | tr -d ':')
if [ ! -z "$BUS" ] && [ ! -z "$DEVICE" ]; then
    DEVICE_PATH="/dev/bus/usb/$BUS/$DEVICE"
    if [ -e "$DEVICE_PATH" ]; then
        $SUDO chmod 666 $DEVICE_PATH
        echo "✅ Permessi aggiornati per: $DEVICE_PATH"
        ls -la $DEVICE_PATH
    fi
fi

# 7. Test rapido
echo -e "\n7️⃣ Test rapido connessione..."
python3 -c "
import ctypes
import sys

try:
    lib = ctypes.CDLL('/usr/local/lib/crt_288x_ur.so')
    print('✅ Libreria caricata correttamente')
    
    # Prova apertura connessione
    lib.CRT288x_OpenConnection.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_long]
    lib.CRT288x_OpenConnection.restype = ctypes.c_int
    
    result = lib.CRT288x_OpenConnection(0, 0, 9600)
    if result == 0:
        print('✅ Connessione riuscita!')
        lib.CRT288x_CloseConnection()
    else:
        print(f'⚠️ Connessione fallita con codice: {result}')
        print('   Potrebbe essere necessario riavviare o ricollegare il dispositivo')
except Exception as e:
    print(f'❌ Errore: {e}')
    sys.exit(1)
"

echo -e "\n✅ FIX COMPLETATO!"
echo "================================"
echo ""
echo "📝 PROSSIMI PASSI:"
echo "1. Se i gruppi sono stati modificati, eseguire:"
echo "   newgrp plugdev"
echo "   oppure riloggare"
echo ""
echo "2. Scollegare e ricollegare il dispositivo USB"
echo ""
echo "3. Testare il lettore:"
echo "   python3 src/hardware/crt285_reader.py"
echo ""
echo "4. Se il problema persiste, provare con sudo:"
echo "   sudo python3 src/hardware/crt285_reader.py"
echo ""