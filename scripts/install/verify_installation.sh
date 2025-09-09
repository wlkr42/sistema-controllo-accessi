#!/bin/bash
#
# Script di Verifica Installazione Sistema Controllo Accessi
# Controlla che tutti i componenti siano installati correttamente
#

set -e

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_ok() { echo -e "${GREEN}✓${NC} $1"; }
log_fail() { echo -e "${RED}✗${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }

echo "============================================================================"
echo "             VERIFICA INSTALLAZIONE SISTEMA CONTROLLO ACCESSI"
echo "============================================================================"
echo ""

ERRORS=0
WARNINGS=0

# 1. Verifica Python e venv
echo "1. AMBIENTE PYTHON"
echo "-----------------"
if command -v python3 &> /dev/null; then
    VERSION=$(python3 --version | cut -d' ' -f2)
    log_ok "Python installato: $VERSION"
else
    log_fail "Python non trovato"
    ((ERRORS++))
fi

if [ -d "/opt/access_control/venv" ]; then
    log_ok "Virtual environment presente"
    
    # Verifica Gunicorn
    if /opt/access_control/venv/bin/python -c "import gunicorn" 2>/dev/null; then
        log_ok "Gunicorn (WSGI server) installato"
    else
        log_fail "Gunicorn non installato"
        ((ERRORS++))
    fi
    
    # Verifica Flask
    if /opt/access_control/venv/bin/python -c "import flask" 2>/dev/null; then
        log_ok "Flask installato"
    else
        log_fail "Flask non installato"
        ((ERRORS++))
    fi
else
    log_fail "Virtual environment non trovato"
    ((ERRORS++))
fi
echo ""

# 2. Verifica Database
echo "2. DATABASE"
echo "-----------"
# Cerca database con nomi possibili
DB_PATH=""
if [ -f "/opt/access_control/data/access_control.db" ]; then
    DB_PATH="/opt/access_control/data/access_control.db"
elif [ -f "/opt/access_control/data/access.db" ]; then
    DB_PATH="/opt/access_control/data/access.db"
fi

if [ -n "$DB_PATH" ]; then
    log_ok "Database presente: $(basename $DB_PATH)"
    
    # Verifica tabelle
    TABLES=$(sqlite3 "$DB_PATH" ".tables" 2>/dev/null | wc -w)
    if [ "$TABLES" -gt 10 ]; then
        log_ok "Database inizializzato ($TABLES tabelle)"
    else
        log_warn "Database potrebbe non essere completo ($TABLES tabelle)"
        ((WARNINGS++))
    fi
else
    log_fail "Database non trovato"
    ((ERRORS++))
fi
echo ""

# 3. Verifica Servizi Systemd
echo "3. SERVIZI SYSTEMD"
echo "------------------"
if systemctl list-unit-files | grep -q "access-control-web.service"; then
    log_ok "Servizio web installato"
    
    if systemctl is-active --quiet access-control-web.service; then
        log_ok "Servizio web attivo"
    else
        log_warn "Servizio web non attivo"
        ((WARNINGS++))
    fi
    
    if systemctl is-enabled --quiet access-control-web.service; then
        log_ok "Servizio web abilitato all'avvio"
    else
        log_warn "Servizio web non abilitato all'avvio"
        ((WARNINGS++))
    fi
else
    log_fail "Servizio web non installato"
    ((ERRORS++))
fi

if systemctl list-unit-files | grep -q "access-monitor.service"; then
    log_ok "Servizio monitor installato"
    
    if systemctl is-active --quiet access-monitor.service; then
        log_ok "Servizio monitor attivo"
    else
        log_warn "Servizio monitor non attivo"
        ((WARNINGS++))
    fi
else
    log_warn "Servizio monitor non installato"
    ((WARNINGS++))
fi
echo ""

# 4. Verifica Hardware
echo "4. HARDWARE"
echo "-----------"
if lsusb | grep -q "23d8:0285"; then
    log_ok "Lettore tessere CRT-285/288K rilevato"
else
    log_warn "Lettore tessere non rilevato"
    ((WARNINGS++))
fi

if lsusb | grep -q "04d8:ffee"; then
    log_ok "Controller relè USB-RLY08 rilevato"
else
    log_warn "Controller relè non rilevato"
    ((WARNINGS++))
fi

# Verifica regole udev
if [ -f "/etc/udev/rules.d/99-card-reader.rules" ]; then
    log_ok "Regole udev lettore installate"
else
    log_warn "Regole udev lettore non trovate"
    ((WARNINGS++))
fi

if [ -f "/etc/udev/rules.d/99-usb-relay.rules" ]; then
    log_ok "Regole udev relè installate"
else
    log_warn "Regole udev relè non trovate"
    ((WARNINGS++))
fi
echo ""

# 5. Verifica Directory
echo "5. STRUTTURA DIRECTORY"
echo "----------------------"
DIRS=("/opt/access_control/data" "/opt/access_control/logs" "/opt/access_control/backups" "/opt/access_control/config")
for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        log_ok "Directory $(basename $dir) presente"
    else
        log_fail "Directory $dir mancante"
        ((ERRORS++))
    fi
done
echo ""

# 6. Verifica Cron Jobs
echo "6. CRON JOBS"
echo "------------"
if crontab -l 2>/dev/null | grep -q "auto_backup"; then
    log_ok "Backup automatico configurato"
else
    log_warn "Backup automatico non configurato"
    ((WARNINGS++))
fi

if crontab -l 2>/dev/null | grep -q "Access Control System"; then
    log_ok "Cron jobs sistema configurati"
else
    log_warn "Cron jobs sistema non configurati"
    ((WARNINGS++))
fi
echo ""

# 7. Verifica Logrotate
echo "7. LOGROTATE"
echo "------------"
if [ -f "/etc/logrotate.d/access-control" ]; then
    log_ok "Logrotate configurato"
else
    log_warn "Logrotate non configurato"
    ((WARNINGS++))
fi
echo ""

# 8. Verifica API Health
echo "8. API HEALTH CHECK"
echo "-------------------"
if curl -s -f http://localhost:5000/api/health > /dev/null 2>&1; then
    log_ok "API raggiungibile"
    
    HEALTH=$(curl -s http://localhost:5000/api/health | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null || echo "error")
    if [ "$HEALTH" = "healthy" ]; then
        log_ok "Sistema healthy"
    else
        log_warn "Sistema non healthy: $HEALTH"
        ((WARNINGS++))
    fi
else
    log_fail "API non raggiungibile"
    ((ERRORS++))
fi
echo ""

# 9. Verifica Requirements
echo "9. DIPENDENZE PYTHON"
echo "--------------------"
REQUIRED_PACKAGES=("flask" "sqlalchemy" "pyserial" "requests" "cryptography")
for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if /opt/access_control/venv/bin/python -c "import $pkg" 2>/dev/null; then
        log_ok "Pacchetto $pkg installato"
    else
        log_fail "Pacchetto $pkg mancante"
        ((ERRORS++))
    fi
done
echo ""

# 10. Report Finale
echo "============================================================================"
echo "                              REPORT FINALE"
echo "============================================================================"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ INSTALLAZIONE COMPLETATA CON SUCCESSO!${NC}"
    echo ""
    echo "Il sistema è pronto all'uso."
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  INSTALLAZIONE COMPLETATA CON $WARNINGS AVVISI${NC}"
    echo ""
    echo "Il sistema è funzionante ma alcuni componenti opzionali non sono configurati."
else
    echo -e "${RED}❌ INSTALLAZIONE INCOMPLETA: $ERRORS ERRORI, $WARNINGS AVVISI${NC}"
    echo ""
    echo "Correggere gli errori prima di utilizzare il sistema."
fi

echo ""
echo "Accesso web interface: http://$(hostname -I | awk '{print $1}'):5000"
echo "Username: admin"
echo "Password: admin123"
echo ""
echo "============================================================================"

exit $ERRORS