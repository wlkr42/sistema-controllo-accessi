#!/bin/bash
#
# Setup Permissions per Sistema Controllo Accessi
# Configura tutti i permessi necessari per file, directory e hardware
#

set -e

PROJECT_ROOT="${1:-/opt/access_control}"
SERVICE_USER="${2:-www-data}"  # Utente che esegue il servizio

# Colori output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "=== Setup Permessi Sistema ==="
echo ""

# Verifica root
if [ "$EUID" -ne 0 ]; then 
    log_error "Questo script deve essere eseguito come root"
    exit 1
fi

# 1. CREAZIONE UTENTE SISTEMA (se non esiste)
log_info "Verifica utente sistema..."
if ! id "$SERVICE_USER" &>/dev/null; then
    log_info "Creazione utente $SERVICE_USER..."
    useradd -r -s /bin/false -d /nonexistent -c "Access Control Service" $SERVICE_USER
fi

# 2. PERMESSI DIRECTORY PRINCIPALI
log_info "Impostazione permessi directory..."

# Directory root del progetto
chown -R $SERVICE_USER:$SERVICE_USER "$PROJECT_ROOT"
chmod 755 "$PROJECT_ROOT"

# Directory dati (database) - scrittura necessaria
if [ -d "$PROJECT_ROOT/data" ]; then
    chmod 770 "$PROJECT_ROOT/data"
    chown -R $SERVICE_USER:$SERVICE_USER "$PROJECT_ROOT/data"
    
    # Database files - permessi stretti
    find "$PROJECT_ROOT/data" -name "*.db" -exec chmod 660 {} \;
    find "$PROJECT_ROOT/data" -name "*.db-journal" -exec chmod 660 {} \;
fi

# Directory logs - scrittura necessaria
if [ -d "$PROJECT_ROOT/logs" ]; then
    chmod 770 "$PROJECT_ROOT/logs"
    chown -R $SERVICE_USER:$SERVICE_USER "$PROJECT_ROOT/logs"
    
    # Permessi per file di log esistenti
    find "$PROJECT_ROOT/logs" -type f -name "*.log*" -exec chmod 664 {} \;
fi

# Directory backups - scrittura necessaria
if [ -d "$PROJECT_ROOT/backups" ]; then
    chmod 770 "$PROJECT_ROOT/backups"
    chown -R $SERVICE_USER:$SERVICE_USER "$PROJECT_ROOT/backups"
    
    # Backup files
    find "$PROJECT_ROOT/backups" -type f -name "*.tar.gz" -exec chmod 640 {} \;
fi

# Directory config - solo lettura per servizio
if [ -d "$PROJECT_ROOT/config" ]; then
    chmod 755 "$PROJECT_ROOT/config"
    chown -R root:$SERVICE_USER "$PROJECT_ROOT/config"
    
    # File di configurazione - solo lettura per gruppo
    find "$PROJECT_ROOT/config" -type f -exec chmod 640 {} \;
fi

# Directory codice sorgente - solo lettura
if [ -d "$PROJECT_ROOT/src" ]; then
    chmod -R 755 "$PROJECT_ROOT/src"
    chown -R root:$SERVICE_USER "$PROJECT_ROOT/src"
    
    # Python files - esecuzione non necessaria
    find "$PROJECT_ROOT/src" -name "*.py" -exec chmod 644 {} \;
fi

# Directory static/uploads per avatar e file caricati
if [ -d "$PROJECT_ROOT/src/api/static" ]; then
    chmod 755 "$PROJECT_ROOT/src/api/static"
    
    # Directory avatars - scrittura necessaria
    if [ -d "$PROJECT_ROOT/src/api/static/avatars" ]; then
        chmod 770 "$PROJECT_ROOT/src/api/static/avatars"
        chown -R $SERVICE_USER:$SERVICE_USER "$PROJECT_ROOT/src/api/static/avatars"
    fi
    
    # Altri file statici - solo lettura
    find "$PROJECT_ROOT/src/api/static" -type f \( -name "*.css" -o -name "*.js" -o -name "*.html" \) -exec chmod 644 {} \;
fi

# Directory virtual environment
if [ -d "$PROJECT_ROOT/venv" ]; then
    chmod -R 755 "$PROJECT_ROOT/venv"
    chown -R root:$SERVICE_USER "$PROJECT_ROOT/venv"
fi

# 3. PERMESSI SCRIPT ESEGUIBILI
log_info "Impostazione permessi script..."

# Script nella root
find "$PROJECT_ROOT" -maxdepth 1 -name "*.sh" -exec chmod 755 {} \;
find "$PROJECT_ROOT" -maxdepth 1 -name "*.sh" -exec chown root:$SERVICE_USER {} \;

# Script in scripts/
if [ -d "$PROJECT_ROOT/scripts" ]; then
    find "$PROJECT_ROOT/scripts" -name "*.sh" -exec chmod 755 {} \;
    find "$PROJECT_ROOT/scripts" -name "*.py" -exec chmod 755 {} \;
    chown -R root:$SERVICE_USER "$PROJECT_ROOT/scripts"
fi

# Main.py eseguibile
if [ -f "$PROJECT_ROOT/main.py" ]; then
    chmod 755 "$PROJECT_ROOT/main.py"
    chown root:$SERVICE_USER "$PROJECT_ROOT/main.py"
fi

# 4. PERMESSI HARDWARE E SERIALI
log_info "Configurazione permessi hardware..."

# Aggiungi utente servizio ai gruppi necessari
usermod -a -G dialout $SERVICE_USER 2>/dev/null || true
usermod -a -G tty $SERVICE_USER 2>/dev/null || true
usermod -a -G plugdev $SERVICE_USER 2>/dev/null || true
usermod -a -G gpio $SERVICE_USER 2>/dev/null || true

# Se c'è un utente sudo, aggiungi anche lui
if [ -n "$SUDO_USER" ] && [ "$SUDO_USER" != "root" ]; then
    log_info "Aggiunta utente $SUDO_USER ai gruppi hardware..."
    usermod -a -G dialout $SUDO_USER 2>/dev/null || true
    usermod -a -G tty $SUDO_USER 2>/dev/null || true
    usermod -a -G plugdev $SUDO_USER 2>/dev/null || true
fi

# 5. PERMESSI DISPOSITIVI SERIALI
log_info "Verifica permessi dispositivi seriali..."

# Imposta permessi per dispositivi esistenti
for device in /dev/ttyUSB* /dev/ttyACM*; do
    if [ -e "$device" ]; then
        chmod 666 "$device"
        chgrp dialout "$device"
        log_info "✓ Permessi impostati per $device"
    fi
done

# 6. PERMESSI FILE SENSIBILI
log_info "Protezione file sensibili..."

# File con credenziali o configurazioni sensibili
SENSITIVE_FILES=(
    "$PROJECT_ROOT/.env"
    "$PROJECT_ROOT/config/secrets.json"
    "$PROJECT_ROOT/config/device_assignments.json"
    "$PROJECT_ROOT/data/*.db"
)

for pattern in "${SENSITIVE_FILES[@]}"; do
    for file in $pattern; do
        if [ -f "$file" ]; then
            chmod 600 "$file"
            chown $SERVICE_USER:$SERVICE_USER "$file"
            log_info "✓ Protetto: $(basename $file)"
        fi
    done
done

# 7. PERMESSI SYSTEMD SERVICE FILES
log_info "Verifica permessi servizi systemd..."

if [ -f "/etc/systemd/system/access-control-web.service" ]; then
    chmod 644 /etc/systemd/system/access-control-web.service
    chown root:root /etc/systemd/system/access-control-web.service
fi

if [ -f "/etc/systemd/system/access-monitor.service" ]; then
    chmod 644 /etc/systemd/system/access-monitor.service
    chown root:root /etc/systemd/system/access-monitor.service
fi

# 8. CREAZIONE DIRECTORY TEMPORANEE CON PERMESSI
log_info "Creazione directory temporanee..."

# Directory per PID files
if [ ! -d "/var/run/access-control" ]; then
    mkdir -p /var/run/access-control
    chown $SERVICE_USER:$SERVICE_USER /var/run/access-control
    chmod 755 /var/run/access-control
fi

# Directory per socket files (se necessario)
if [ ! -d "/var/lib/access-control" ]; then
    mkdir -p /var/lib/access-control
    chown $SERVICE_USER:$SERVICE_USER /var/lib/access-control
    chmod 750 /var/lib/access-control
fi

# 9. FIX PERMESSI RICORSIVI FINALI
log_info "Applicazione permessi ricorsivi finali..."

# Assicura che tutti i file siano leggibili dal gruppo
find "$PROJECT_ROOT" -type f -exec chmod g+r {} \;

# Assicura che tutte le directory siano attraversabili
find "$PROJECT_ROOT" -type d -exec chmod g+rx {} \;

# Rimuovi permessi world-write ovunque (sicurezza)
find "$PROJECT_ROOT" -type f -exec chmod o-w {} \;
find "$PROJECT_ROOT" -type d -exec chmod o-w {} \;

# 10. VERIFICA SELINUX (se attivo)
if command -v getenforce &> /dev/null && [ "$(getenforce)" != "Disabled" ]; then
    log_warn "SELinux attivo, configurazione contesto..."
    
    # Imposta contesto per directory web
    chcon -R -t httpd_sys_content_t "$PROJECT_ROOT/src/api/static" 2>/dev/null || true
    
    # Permetti scrittura per upload
    chcon -R -t httpd_sys_rw_content_t "$PROJECT_ROOT/src/api/static/avatars" 2>/dev/null || true
    chcon -R -t httpd_sys_rw_content_t "$PROJECT_ROOT/data" 2>/dev/null || true
    chcon -R -t httpd_sys_rw_content_t "$PROJECT_ROOT/logs" 2>/dev/null || true
    
    # Permetti connessioni seriali
    setsebool -P httpd_can_network_connect 1 2>/dev/null || true
fi

# REPORT FINALE
echo ""
log_info "=== Report Permessi ==="
echo ""

echo "Directory principali:"
ls -ld "$PROJECT_ROOT"
ls -ld "$PROJECT_ROOT"/data 2>/dev/null || true
ls -ld "$PROJECT_ROOT"/logs 2>/dev/null || true
ls -ld "$PROJECT_ROOT"/backups 2>/dev/null || true

echo ""
echo "Utente servizio: $SERVICE_USER"
echo "Gruppi utente servizio: $(groups $SERVICE_USER 2>/dev/null || echo 'N/A')"

if [ -n "$SUDO_USER" ] && [ "$SUDO_USER" != "root" ]; then
    echo "Gruppi utente $SUDO_USER: $(groups $SUDO_USER 2>/dev/null || echo 'N/A')"
fi

echo ""
log_info "✅ Setup permessi completato!"
log_info ""
log_info "Note importanti:"
log_info "- Il servizio girerà come utente: $SERVICE_USER"
log_info "- Riavviare il sistema o fare logout/login per applicare i gruppi"
log_info "- Verificare i dispositivi seriali dopo il riavvio"

exit 0