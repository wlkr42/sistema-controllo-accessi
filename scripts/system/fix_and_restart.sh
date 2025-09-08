#!/bin/bash
#
# Script di FIX e RESTART completo del sistema
# Documenta e risolve TUTTI i problemi
#

echo "🔧 FIX E RESTART SISTEMA CONTROLLO ACCESSI"
echo "==========================================="
echo ""

# 1. VERIFICA PERMESSI
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Questo script deve essere eseguito come root"
    echo "    Uso: sudo $0"
    exit 1
fi

echo "📋 STEP 1: Pulizia processi esistenti"
echo "--------------------------------------"

# 2. TROVA E TERMINA PROCESSI ESISTENTI
echo "🔍 Ricerca processi web_api in esecuzione..."

# Trova tutti i PID dei processi web_api
PIDS=$(ps aux | grep -E "python.*web_api" | grep -v grep | awk '{print $2}')

if [ -n "$PIDS" ]; then
    echo "⚠️  Trovati processi da terminare: $PIDS"
    for PID in $PIDS; do
        echo "   Termino processo $PID..."
        kill -TERM $PID 2>/dev/null || true
    done
    sleep 2
    
    # Force kill se ancora attivi
    for PID in $PIDS; do
        if kill -0 $PID 2>/dev/null; then
            echo "   Force kill processo $PID..."
            kill -KILL $PID 2>/dev/null || true
        fi
    done
else
    echo "✅ Nessun processo web_api attivo"
fi

# 3. VERIFICA PORTA 5000
echo ""
echo "📋 STEP 2: Verifica porta 5000"
echo "-------------------------------"

if lsof -i :5000 >/dev/null 2>&1; then
    echo "⚠️  Porta 5000 ancora occupata, pulizia..."
    fuser -k 5000/tcp 2>/dev/null || true
    sleep 1
fi

if ! lsof -i :5000 >/dev/null 2>&1; then
    echo "✅ Porta 5000 libera"
else
    echo "❌ ERRORE: Impossibile liberare porta 5000"
    lsof -i :5000
    exit 1
fi

# 4. FERMA SERVIZIO SYSTEMD SE ATTIVO
echo ""
echo "📋 STEP 3: Gestione servizio systemd"
echo "------------------------------------"

if systemctl is-active --quiet access-control-web; then
    echo "⚠️  Servizio systemd attivo, arresto..."
    systemctl stop access-control-web
    sleep 2
fi
echo "✅ Servizio systemd fermato"

# 5. VERIFICA HARDWARE
echo ""
echo "📋 STEP 4: Verifica hardware"
echo "----------------------------"

HARDWARE_OK=true

# CRT-285
if lsusb | grep -q "23d8:0285"; then
    echo "✅ CRT-285 rilevato"
    # Verifica permessi
    BUS=$(lsusb -d 23d8:0285 | sed 's/Bus \([0-9]*\).*/\1/')
    DEV=$(lsusb -d 23d8:0285 | sed 's/.*Device \([0-9]*\):.*/\1/')
    DEVICE_PATH="/dev/bus/usb/$BUS/$DEV"
    if [ -e "$DEVICE_PATH" ]; then
        PERMS=$(stat -c %a "$DEVICE_PATH")
        if [ "$PERMS" != "666" ]; then
            echo "   🔧 Correzione permessi dispositivo..."
            chmod 666 "$DEVICE_PATH" 2>/dev/null || true
        fi
        echo "   ✅ Permessi: $PERMS -> $(stat -c %a "$DEVICE_PATH")"
    fi
else
    echo "⚠️  CRT-285 non rilevato"
    HARDWARE_OK=false
fi

# USB-RLY08
if lsusb | grep -q "04d8:ffee"; then
    echo "✅ USB-RLY08 rilevato"
else
    echo "⚠️  USB-RLY08 non rilevato"
fi

# 6. VERIFICA CONFIGURAZIONE
echo ""
echo "📋 STEP 5: Verifica configurazione"
echo "----------------------------------"

CONFIG_FILE="/opt/access_control/config/device_assignments.json"
if [ -f "$CONFIG_FILE" ]; then
    echo "✅ File configurazione hardware presente"
    echo "   Contenuto:"
    cat "$CONFIG_FILE" | python3 -m json.tool | head -20
else
    echo "❌ File configurazione mancante!"
fi

# 7. INSTALLA/AGGIORNA SERVIZIO
echo ""
echo "📋 STEP 6: Installazione servizio"
echo "---------------------------------"

SERVICE_FILE="/opt/access_control/access-control-web.service"
if [ -f "$SERVICE_FILE" ]; then
    echo "📦 Installazione servizio systemd..."
    cp "$SERVICE_FILE" /etc/systemd/system/
    systemctl daemon-reload
    echo "✅ Servizio installato/aggiornato"
else
    echo "❌ File servizio non trovato!"
    exit 1
fi

# 8. VERIFICA VIRTUAL ENVIRONMENT
echo ""
echo "📋 STEP 7: Verifica Python venv"
echo "-------------------------------"

VENV_PYTHON="/opt/access_control/venv/bin/python"
if [ -x "$VENV_PYTHON" ]; then
    echo "✅ Python venv trovato"
    $VENV_PYTHON --version
else
    echo "❌ Python venv non trovato o non eseguibile!"
    exit 1
fi

# 9. TEST IMPORTAZIONE MODULI
echo ""
echo "📋 STEP 8: Test moduli Python"
echo "-----------------------------"

echo "🧪 Test import moduli critici..."
$VENV_PYTHON -c "
import sys
sys.path.insert(0, '/opt/access_control/src')
try:
    from api.web_api import app
    print('   ✅ web_api importabile')
except Exception as e:
    print(f'   ❌ Errore import web_api: {e}')
    sys.exit(1)

try:
    from hardware.crt285_reader import CRT285Reader
    print('   ✅ CRT285Reader importabile')
except Exception as e:
    print(f'   ⚠️  CRT285Reader non importabile: {e}')

try:
    from hardware.usb_rly08_controller import UsbRly08Controller
    print('   ✅ UsbRly08Controller importabile')
except Exception as e:
    print(f'   ⚠️  UsbRly08Controller non importabile: {e}')
"

if [ $? -ne 0 ]; then
    echo "❌ Test import fallito!"
    exit 1
fi

# 10. AVVIA SERVIZIO
echo ""
echo "📋 STEP 9: Avvio servizio"
echo "------------------------"

echo "🚀 Avvio servizio systemd..."
systemctl start access-control-web

# Attendi avvio
sleep 3

# 11. VERIFICA STATO
echo ""
echo "📋 STEP 10: Verifica finale"
echo "---------------------------"

if systemctl is-active --quiet access-control-web; then
    echo "✅ Servizio ATTIVO e funzionante!"
    
    # Verifica che risponda su porta 5000
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 | grep -q "200\|302"; then
        echo "✅ Web interface risponde correttamente"
    else
        echo "⚠️  Web interface non risponde ancora (potrebbe essere in avvio)"
    fi
else
    echo "❌ ERRORE: Servizio non attivo!"
    echo ""
    echo "📝 Ultimi log del servizio:"
    echo "----------------------------"
    journalctl -u access-control-web -n 20 --no-pager
    exit 1
fi

# 12. ABILITA AVVIO AUTOMATICO
systemctl enable access-control-web 2>/dev/null

# 13. MOSTRA INFO FINALI
echo ""
echo "==========================================="
echo "✅ SISTEMA AVVIATO CON SUCCESSO!"
echo "==========================================="
echo ""
echo "📊 INFORMAZIONI SISTEMA:"
echo "  IP Sistema: $(hostname -I | awk '{print $1}')"
echo "  Web Interface: http://$(hostname -I | awk '{print $1}'):5000"
echo "  Admin Config: http://$(hostname -I | awk '{print $1}'):5000/admin/config"
echo ""
echo "📝 COMANDI UTILI:"
echo "  Stato servizio:  systemctl status access-control-web"
echo "  Log in tempo reale: journalctl -u access-control-web -f"
echo "  Restart: systemctl restart access-control-web"
echo "  Stop: systemctl stop access-control-web"
echo ""
echo "🔧 RISOLUZIONE PROBLEMI:"
echo "  Se il servizio non parte:"
echo "    1. journalctl -u access-control-web -n 50"
echo "    2. sudo $VENV_PYTHON /opt/access_control/src/api/web_api.py (test manuale)"
echo ""
echo "📦 HARDWARE RILEVATO:"
lsusb | grep -E "23d8:0285|04d8:ffee" || echo "  Nessun dispositivo supportato collegato"
echo ""