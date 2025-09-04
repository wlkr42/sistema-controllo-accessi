#!/bin/bash

# Script di verifica sistema per Sistema Controllo Accessi
# Verifica stato generale, servizi, database e hardware

set -e

INSTALL_PATH="/opt/access_control"
USER="wlkr42"
SERVICE_NAME="access-control"

echo "=== Verifica Sistema Controllo Accessi ==="
echo "Data: $(date)"
echo "Percorso: $INSTALL_PATH"
echo ""

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzioni di utilità
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "OK" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "WARNING" ]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    else
        echo -e "${RED}❌ $message${NC}"
    fi
}

check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# 1. Verifica file system e permessi
echo "🔍 1. Verifica File System e Permessi"
echo "----------------------------------------"

if [ -d "$INSTALL_PATH" ]; then
    print_status "OK" "Directory installazione presente: $INSTALL_PATH"
    
    # Verifica permessi directory principale
    OWNER=$(stat -c %U "$INSTALL_PATH")
    if [ "$OWNER" = "$USER" ]; then
        print_status "OK" "Proprietario directory corretto: $USER"
    else
        print_status "ERROR" "Proprietario directory errato: $OWNER (dovrebbe essere $USER)"
    fi
    
    # Verifica sottodirectory essenziali
    REQUIRED_DIRS=("src" "config" "scripts" "backups")
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [ -d "$INSTALL_PATH/$dir" ]; then
            print_status "OK" "Directory $dir presente"
        else
            print_status "ERROR" "Directory $dir mancante"
        fi
    done
    
else
    print_status "ERROR" "Directory installazione non trovata: $INSTALL_PATH"
fi

echo ""

# 2. Verifica utente sistema
echo "👤 2. Verifica Utente Sistema"
echo "------------------------------"

if id "$USER" &>/dev/null; then
    print_status "OK" "Utente $USER presente nel sistema"
    
    # Verifica gruppi
    GROUPS=$(groups "$USER")
    if [[ $GROUPS == *"dialout"* ]]; then
        print_status "OK" "Utente nel gruppo dialout (accesso seriale)"
    else
        print_status "WARNING" "Utente non nel gruppo dialout"
    fi
    
    if [[ $GROUPS == *"plugdev"* ]]; then
        print_status "OK" "Utente nel gruppo plugdev (accesso USB)"
    else
        print_status "WARNING" "Utente non nel gruppo plugdev"
    fi
else
    print_status "ERROR" "Utente $USER non presente nel sistema"
fi

echo ""

# 3. Verifica servizio systemd
echo "⚙️  3. Verifica Servizio SystemD"
echo "--------------------------------"

if systemctl list-unit-files | grep -q "$SERVICE_NAME.service"; then
    print_status "OK" "Servizio $SERVICE_NAME installato"
    
    # Stato servizio
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_status "OK" "Servizio attivo"
    else
        print_status "ERROR" "Servizio non attivo"
        echo "   Stato: $(systemctl is-active $SERVICE_NAME)"
    fi
    
    # Abilitazione servizio
    if systemctl is-enabled --quiet "$SERVICE_NAME"; then
        print_status "OK" "Servizio abilitato all'avvio"
    else
        print_status "WARNING" "Servizio non abilitato all'avvio"
    fi
    
    # Tempo di avvio
    START_TIME=$(systemctl show "$SERVICE_NAME" --property=ActiveEnterTimestamp --value)
    if [ -n "$START_TIME" ] && [ "$START_TIME" != "n/a" ]; then
        print_status "OK" "Ultimo avvio: $START_TIME"
    fi
    
else
    print_status "ERROR" "Servizio $SERVICE_NAME non installato"
fi

echo ""

# 4. Verifica dipendenze Python
echo "🐍 4. Verifica Dipendenze Python"
echo "--------------------------------"

if check_command python3; then
    print_status "OK" "Python3 installato: $(python3 --version)"
    
    # Verifica pip
    if check_command pip3; then
        print_status "OK" "pip3 disponibile"
    else
        print_status "WARNING" "pip3 non disponibile"
    fi
    
    # Verifica dipendenze principali
    PYTHON_DEPS=("flask" "sqlite3" "requests")
    for dep in "${PYTHON_DEPS[@]}"; do
        if python3 -c "import $dep" 2>/dev/null; then
            print_status "OK" "Modulo Python $dep disponibile"
        else
            print_status "WARNING" "Modulo Python $dep non disponibile"
        fi
    done
    
    # Verifica requirements.txt se presente
    if [ -f "$INSTALL_PATH/requirements.txt" ]; then
        print_status "OK" "File requirements.txt presente"
        echo "   Dipendenze elencate:"
        while IFS= read -r line; do
            echo "     - $line"
        done < "$INSTALL_PATH/requirements.txt"
    else
        print_status "WARNING" "File requirements.txt non trovato"
    fi
    
else
    print_status "ERROR" "Python3 non installato"
fi

echo ""

# 5. Verifica database
echo "🗄️  5. Verifica Database"
echo "------------------------"

DATABASE_PATH="$INSTALL_PATH/src/access.db"
if [ -f "$DATABASE_PATH" ]; then
    print_status "OK" "Database presente: $DATABASE_PATH"
    
    # Verifica permessi database
    DB_OWNER=$(stat -c %U "$DATABASE_PATH")
    if [ "$DB_OWNER" = "$USER" ]; then
        print_status "OK" "Proprietario database corretto: $USER"
    else
        print_status "WARNING" "Proprietario database: $DB_OWNER"
    fi
    
    # Dimensione database
    DB_SIZE=$(du -h "$DATABASE_PATH" | cut -f1)
    print_status "OK" "Dimensione database: $DB_SIZE"
    
    # Test connessione database
    if python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('$DATABASE_PATH')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\";')
    tables = cursor.fetchall()
    print(f'Tabelle trovate: {len(tables)}')
    conn.close()
    exit(0)
except Exception as e:
    print(f'Errore: {e}')
    exit(1)
" 2>/dev/null; then
        print_status "OK" "Database accessibile"
    else
        print_status "ERROR" "Errore accesso database"
    fi
    
else
    print_status "WARNING" "Database non presente (sarà creato al primo avvio)"
fi

echo ""

# 6. Verifica connettività di rete
echo "🌐 6. Verifica Connettività"
echo "---------------------------"

# Test porta del servizio web
WEB_PORT="5000"
if netstat -tuln 2>/dev/null | grep -q ":$WEB_PORT "; then
    print_status "OK" "Porta $WEB_PORT in ascolto"
    
    # Test HTTP se curl disponibile
    if check_command curl; then
        if curl -s --max-time 5 http://localhost:$WEB_PORT &> /dev/null; then
            print_status "OK" "Server web risponde"
        else
            print_status "WARNING" "Server web non risponde"
        fi
    else
        print_status "WARNING" "curl non disponibile per test HTTP"
    fi
else
    print_status "WARNING" "Porta $WEB_PORT non in ascolto"
fi

# Verifica firewall
if systemctl is-active --quiet firewalld; then
    if firewall-cmd --query-port="$WEB_PORT/tcp" 2>/dev/null; then
        print_status "OK" "Firewall: porta $WEB_PORT aperta"
    else
        print_status "WARNING" "Firewall: porta $WEB_PORT non configurata"
    fi
else
    print_status "OK" "Firewall non attivo"
fi

echo ""

# 7. Verifica hardware (se disponibile)
echo "🔌 7. Verifica Hardware"
echo "----------------------"

# Test dispositivi USB
if check_command lsusb; then
    USB_DEVICES=$(lsusb | wc -l)
    print_status "OK" "Dispositivi USB rilevati: $USB_DEVICES"
    
    # Cerca dispositivi specifici
    if lsusb | grep -i "relay\|rly" &>/dev/null; then
        print_status "OK" "Dispositivo relay USB rilevato"
    else
        print_status "WARNING" "Nessun dispositivo relay USB rilevato"
    fi
else
    print_status "WARNING" "Comando lsusb non disponibile"
fi

# Test dispositivi seriali
if [ -d "/dev/serial" ]; then
    SERIAL_COUNT=$(ls /dev/serial/by-id/ 2>/dev/null | wc -l)
    print_status "OK" "Dispositivi seriali: $SERIAL_COUNT"
else
    print_status "WARNING" "Nessun dispositivo seriale rilevato"
fi

echo ""

# 8. Verifica cron jobs
echo "⏰ 8. Verifica Cron Jobs"
echo "-----------------------"

if check_command crontab; then
    if sudo -u "$USER" crontab -l 2>/dev/null | grep -q "access_control\|access-control"; then
        print_status "OK" "Cron jobs configurati per $USER"
        
        # Mostra i job configurati
        echo "   Job configurati:"
        sudo -u "$USER" crontab -l 2>/dev/null | grep -v "^#" | while read -r line; do
            [ -n "$line" ] && echo "     - $line"
        done
    else
        print_status "WARNING" "Nessun cron job configurato"
    fi
    
    # Verifica servizio crond
    if systemctl is-active --quiet crond; then
        print_status "OK" "Servizio cron attivo"
    else
        print_status "WARNING" "Servizio cron non attivo"
    fi
else
    print_status "ERROR" "Crontab non disponibile"
fi

echo ""

# 9. Verifica log
echo "📝 9. Verifica Log"
echo "------------------"

LOG_DIR="/var/log/access_control"
if [ -d "$LOG_DIR" ]; then
    print_status "OK" "Directory log presente: $LOG_DIR"
    
    LOG_COUNT=$(find "$LOG_DIR" -name "*.log" 2>/dev/null | wc -l)
    print_status "OK" "File di log trovati: $LOG_COUNT"
else
    print_status "WARNING" "Directory log non presente"
fi

# Log systemd
if journalctl -u "$SERVICE_NAME" --since "1 hour ago" --quiet 2>/dev/null; then
    print_status "OK" "Log systemd disponibili"
    
    # Cerca errori recenti
    ERROR_COUNT=$(journalctl -u "$SERVICE_NAME" --since "1 hour ago" --priority=err --no-pager -q 2>/dev/null | wc -l)
    if [ "$ERROR_COUNT" -eq 0 ]; then
        print_status "OK" "Nessun errore nell'ultima ora"
    else
        print_status "WARNING" "Errori trovati nell'ultima ora: $ERROR_COUNT"
    fi
else
    print_status "WARNING" "Log systemd non accessibili"
fi

echo ""

# 10. Riepilogo finale
echo "📊 10. Riepilogo Sistema"
echo "------------------------"

# Calcola health score
TOTAL_CHECKS=0
PASSED_CHECKS=0

# Conteggio semplificato basato sui controlli principali
if [ -d "$INSTALL_PATH" ]; then ((PASSED_CHECKS++)); fi; ((TOTAL_CHECKS++))
if id "$USER" &>/dev/null; then ((PASSED_CHECKS++)); fi; ((TOTAL_CHECKS++))
if systemctl is-active --quiet "$SERVICE_NAME"; then ((PASSED_CHECKS++)); fi; ((TOTAL_CHECKS++))
if check_command python3; then ((PASSED_CHECKS++)); fi; ((TOTAL_CHECKS++))

HEALTH_SCORE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))

echo "🎯 Health Score: $HEALTH_SCORE% ($PASSED_CHECKS/$TOTAL_CHECKS controlli passati)"

if [ "$HEALTH_SCORE" -ge 80 ]; then
    print_status "OK" "Sistema in buone condizioni"
elif [ "$HEALTH_SCORE" -ge 60 ]; then
    print_status "WARNING" "Sistema funzionante con alcuni avvisi"
else
    print_status "ERROR" "Sistema con problemi significativi"
fi

echo ""
echo "🔧 Comandi utili:"
echo "  - Restart servizio: sudo systemctl restart $SERVICE_NAME"
echo "  - Log in tempo reale: sudo journalctl -u $SERVICE_NAME -f"
echo "  - Stato dettagliato: sudo systemctl status $SERVICE_NAME"
echo "  - Test hardware: sudo -u $USER python3 $INSTALL_PATH/scripts/test_hardware.py"
echo ""
echo "Verifica completata: $(date)"
