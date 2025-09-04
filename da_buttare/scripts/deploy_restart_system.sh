#!/bin/bash
# File: /opt/access_control/scripts/deploy_restart_system.sh
# Deploy completo sistema di riavvio

set -e

PROJECT_ROOT="/opt/access_control"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo "========================================"
    echo -e "${BLUE}$1${NC}"
    echo "========================================"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_status() {
    echo -e "${BLUE}�� $1${NC}"
}

print_header "DEPLOY SISTEMA RIAVVIO COMPLETO"

# 1. Verifica ambiente
print_status "Verifica ambiente..."
if [[ ! -d "$PROJECT_ROOT" ]]; then
    echo -e "${RED}❌ Directory progetto non trovata: $PROJECT_ROOT${NC}"
    exit 1
fi

if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}❌ Script deve essere eseguito come root${NC}"
    exit 1
fi

print_success "Ambiente verificato"

# 2. Crea directory scripts
print_status "Creazione directory scripts..."
mkdir -p "$SCRIPTS_DIR"
mkdir -p "$PROJECT_ROOT/logs"
print_success "Directory create"

# 3. Crea script restart_system.sh (completo)
print_status "Creazione script restart_system.sh..."
cat > "$SCRIPTS_DIR/restart_system.sh" << 'RESTART_EOF'
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
RESTART_EOF

chmod +x "$SCRIPTS_DIR/restart_system.sh"
print_success "Script restart_system.sh creato"

# 4. Crea script quick_restart.sh (rapido)
print_status "Creazione script quick_restart.sh..."
cat > "$SCRIPTS_DIR/quick_restart.sh" << 'QUICK_EOF'
#!/bin/bash
# File: /opt/access_control/scripts/quick_restart.sh
# Riavvio rapido per uso quotidiano

PROJECT_ROOT="/opt/access_control"
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔄 Riavvio rapido sistema...${NC}"

# Stop e restart
systemctl stop access-control 2>/dev/null || true
pkill -f "/opt/access_control" 2>/dev/null || true
fuser -k 5000/tcp 2>/dev/null || true

# Hardware reset veloce
systemctl restart pcscd
chmod 666 /dev/ttyACM* /dev/ttyUSB* 2>/dev/null || true

# Avvio
systemctl start access-control
sleep 5

if systemctl is-active --quiet access-control; then
    echo -e "${GREEN}✅ Sistema riavviato!${NC}"
    echo -e "${GREEN}🌐 http://192.168.178.200:5000${NC}"
else
    echo "❌ Errore - controllare: journalctl -u access-control -f"
fi
QUICK_EOF

chmod +x "$SCRIPTS_DIR/quick_restart.sh"
print_success "Script quick_restart.sh creato"

# 5. Crea script system_monitor.py
print_status "Creazione system_monitor.py..."
cat > "$SCRIPTS_DIR/system_monitor.py" << 'MONITOR_EOF'
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
MONITOR_EOF

chmod +x "$SCRIPTS_DIR/system_monitor.py"
print_success "Script system_monitor.py creato"

# 6. Crea script di verifica sistema
print_status "Creazione check_system.sh..."
cat > "$SCRIPTS_DIR/check_system.sh" << 'CHECK_EOF'
#!/bin/bash
# File: /opt/access_control/scripts/check_system.sh
# Verifica completa sistema

PROJECT_ROOT="/opt/access_control"
VENV_PATH="$PROJECT_ROOT/venv"

echo "🔍 VERIFICA COMPLETA SISTEMA"
echo "=" * 50

# 1. Verifica directory
echo "📁 Directory progetto:"
if [[ -d "$PROJECT_ROOT" ]]; then
    echo "  ✅ $PROJECT_ROOT esiste"
    echo "  📊 Dimensione: $(du -sh $PROJECT_ROOT | cut -f1)"
else
    echo "  ❌ $PROJECT_ROOT non trovata"
fi

# 2. Verifica virtual environment
echo ""
echo "🐍 Virtual Environment:"
if [[ -d "$VENV_PATH" ]]; then
    echo "  ✅ Virtual environment esiste"
    echo "  📦 Python: $($VENV_PATH/bin/python --version)"
else
    echo "  ❌ Virtual environment non trovato"
fi

# 3. Verifica database
echo ""
echo "🗄️  Database:"
DB_PATH="$PROJECT_ROOT/src/access.db"
if [[ -f "$DB_PATH" ]]; then
    echo "  ✅ Database esiste"
    echo "  📊 Dimensione: $(ls -lh $DB_PATH | awk '{print $5}')"
    
    # Count records se possibile
    if command -v sqlite3 >/dev/null; then
        USERS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM authorized_people;" 2>/dev/null || echo "N/A")
        LOGS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM access_log;" 2>/dev/null || echo "N/A")
        echo "  👥 Utenti autorizzati: $USERS"
        echo "  📋 Log accessi: $LOGS"
    fi
else
    echo "  ⚠️  Database non trovato (verrà creato al primo avvio)"
fi

# 4. Verifica servizi
echo ""
echo "🔧 Servizi:"
services=("access-control" "pcscd")
for service in "${services[@]}"; do
    if systemctl is-active --quiet "$service"; then
        echo "  ✅ $service: ATTIVO"
    else
        echo "  ❌ $service: INATTIVO"
    fi
done

# 5. Verifica hardware
echo ""
echo "🔌 Hardware:"
if ls /dev/ttyACM* >/dev/null 2>&1; then
    echo "  ✅ Lettore tessere: $(ls /dev/ttyACM*)"
else
    echo "  ⚠️  Lettore tessere non rilevato"
fi

if ls /dev/ttyUSB* >/dev/null 2>&1; then
    echo "  ✅ USB-RLY08: $(ls /dev/ttyUSB*)"
else
    echo "  ⚠️  USB-RLY08 non rilevato"
fi

# 6. Verifica rete
echo ""
echo "🌐 Rete:"
if netstat -tuln 2>/dev/null | grep -q ":5000 "; then
    echo "  ✅ Dashboard web: ATTIVA su porta 5000"
    echo "  🔗 URL: http://192.168.178.200:5000"
else
    echo "  ❌ Dashboard web: NON ATTIVA"
fi

# 7. Verifica log
echo ""
echo "📋 Log Recenti:"
if journalctl -u access-control --no-pager -n 3 >/dev/null 2>&1; then
    journalctl -u access-control --no-pager -n 3 | tail -3
else
    echo "  ⚠️  Log non disponibili"
fi

echo ""
echo "=" * 50
CHECK_EOF

chmod +x "$SCRIPTS_DIR/check_system.sh"
print_success "Script check_system.sh creato"

# 7. Crea link simbolici per facilità d'uso
print_status "Creazione comandi globali..."

# Link simbolici in /usr/local/bin
ln -sf "$SCRIPTS_DIR/restart_system.sh" /usr/local/bin/restart-access-control
ln -sf "$SCRIPTS_DIR/quick_restart.sh" /usr/local/bin/quick-restart-access-control
ln -sf "$SCRIPTS_DIR/system_monitor.py" /usr/local/bin/monitor-access-control
ln -sf "$SCRIPTS_DIR/check_system.sh" /usr/local/bin/check-access-control

print_success "Comandi globali creati"

# 8. Verifica installazione
print_status "Verifica installazione..."
if [[ -x "$SCRIPTS_DIR/restart_system.sh" ]] && [[ -x /usr/local/bin/restart-access-control ]]; then
    print_success "Installazione completata correttamente"
else
    echo -e "${RED}❌ Errore installazione${NC}"
    exit 1
fi

# 9. Mostra summary finale
print_header "INSTALLAZIONE COMPLETATA"

echo -e "${GREEN}✅ Script di riavvio installati correttamente!${NC}"
echo ""
echo "📋 COMANDI DISPONIBILI:"
echo "  restart-access-control       # Riavvio completo sistema"
echo "  quick-restart-access-control # Riavvio rapido"
echo "  monitor-access-control       # Monitor sistema"
echo "  check-access-control         # Verifica stato"
echo ""
echo "📋 COMANDI SYSTEMCTL:"
echo "  systemctl start access-control    # Avvia servizio"
echo "  systemctl stop access-control     # Ferma servizio"
echo "  systemctl restart access-control  # Riavvia servizio"
echo "  systemctl status access-control   # Stato servizio"
echo ""
echo "📋 MONITORING:"
echo "  journalctl -u access-control -f   # Log in tempo reale"
echo "  journalctl -u access-control -n 50 # Ultimi 50 log"
echo ""
echo "🎯 READY TO USE!"
echo "Per testare: quick-restart-access-control"
