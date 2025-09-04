#!/bin/bash
# File: /opt/access_control/scripts/restart_system.sh
# Sistema Controllo Accessi - Script Riavvio Completo

set -e

# Configurazioni
PROJECT_ROOT="/opt/access_control"
VENV_PATH="$PROJECT_ROOT/venv"
SERVICE_NAME="access-control"

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_header() {
    echo ""
    echo "========================================"
    echo -e "${BLUE}🔄 $1${NC}"
    echo "========================================"
}

print_header "RIAVVIO COMPLETO SISTEMA"

# Stop tutto
print_status "Stop servizi esistenti..."
systemctl stop access-control 2>/dev/null || true
pkill -f "/opt/access_control" 2>/dev/null || true
fuser -k 5000/tcp 2>/dev/null || true

# Cleanup
print_status "Pulizia sistema..."
rm -f /var/lock/LCK..tty* 2>/dev/null || true
rm -f "$PROJECT_ROOT"/*.lock 2>/dev/null || true
find "$PROJECT_ROOT" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Reset hardware
print_status "Reset hardware..."
systemctl restart pcscd
chmod 666 /dev/ttyACM* /dev/ttyUSB* 2>/dev/null || true

# Test sistema
print_status "Test virtual environment..."
cd "$PROJECT_ROOT"
"$VENV_PATH/bin/python" -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT/src')
import smartcard, flask, sqlite3
print('✅ Dipendenze OK')
"

# Avvio servizio
print_status "Avvio servizio..."
systemctl daemon-reload
systemctl start access-control

# Verifica
sleep 10
if systemctl is-active --quiet access-control; then
    print_success "Sistema riavviato correttamente!"
    print_success "Dashboard: http://192.168.178.200:5000"
else
    echo -e "${RED}❌ Errore riavvio${NC}"
    systemctl status access-control --no-pager
    exit 1
fi
