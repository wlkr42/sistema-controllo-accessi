#!/bin/bash
#
# Fix Permissions Script per Sistema Controllo Accessi
# Sistema tutti i permessi necessari per il funzionamento
#

set -e

# Colori output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

PROJECT_ROOT="/opt/access_control"

log_info "🔧 Sistemazione permessi Sistema Controllo Accessi..."

# Verifica di essere root
if [ "$EUID" -ne 0 ]; then 
    log_error "Questo script deve essere eseguito come root"
    exit 1
fi

# Crea tutte le directory necessarie
log_info "📁 Creazione directory necessarie..."
mkdir -p "$PROJECT_ROOT/data"
mkdir -p "$PROJECT_ROOT/config"
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/backups"
mkdir -p "$PROJECT_ROOT/uploads"
mkdir -p "$PROJECT_ROOT/static"
mkdir -p "$PROJECT_ROOT/src/api/static"

# Assegna proprietario www-data a tutte le directory che necessitano scrittura
log_info "👤 Assegnazione proprietario www-data..."
chown -R www-data:www-data "$PROJECT_ROOT/data"
chown -R www-data:www-data "$PROJECT_ROOT/config"
chown -R www-data:www-data "$PROJECT_ROOT/logs"
chown -R www-data:www-data "$PROJECT_ROOT/backups"
chown -R www-data:www-data "$PROJECT_ROOT/uploads"
chown -R www-data:www-data "$PROJECT_ROOT/static"
chown -R www-data:www-data "$PROJECT_ROOT/src/api/static"

# Imposta permessi directory
log_info "🔐 Impostazione permessi directory..."
chmod 755 "$PROJECT_ROOT/data"
chmod 755 "$PROJECT_ROOT/config"
chmod 755 "$PROJECT_ROOT/logs"
chmod 755 "$PROJECT_ROOT/backups"
chmod 755 "$PROJECT_ROOT/uploads"
chmod 755 "$PROJECT_ROOT/static"
chmod 755 "$PROJECT_ROOT/src/api/static"

# Permessi speciali per il database
if [ -f "$PROJECT_ROOT/data/access.db" ]; then
    log_info "🗄️ Sistemazione permessi database..."
    chown www-data:www-data "$PROJECT_ROOT/data/access.db"
    chmod 664 "$PROJECT_ROOT/data/access.db"
fi

# Crea file di configurazione vuoti se non esistono
log_info "📝 Creazione file configurazione..."
touch "$PROJECT_ROOT/config/device_assignments.json"
touch "$PROJECT_ROOT/config/odoo_sync.json"
touch "$PROJECT_ROOT/config/system_settings.json"

# Assegna permessi ai file di configurazione
chown www-data:www-data "$PROJECT_ROOT/config/"*.json 2>/dev/null || true
chmod 664 "$PROJECT_ROOT/config/"*.json 2>/dev/null || true

# Aggiungi utente www-data ai gruppi necessari per hardware
log_info "🔌 Aggiunta www-data ai gruppi hardware..."
usermod -a -G dialout www-data 2>/dev/null || true
usermod -a -G tty www-data 2>/dev/null || true
usermod -a -G plugdev www-data 2>/dev/null || true

# Permessi per i driver
if [ -d "$PROJECT_ROOT/src/drivers" ]; then
    log_info "💿 Sistemazione permessi driver..."
    find "$PROJECT_ROOT/src/drivers" -name "*.so" -exec chmod 755 {} \;
fi

# Crea directory per i PID files
mkdir -p /var/run/access_control
chown www-data:www-data /var/run/access_control
chmod 755 /var/run/access_control

# Verifica e mostra risultati
log_info "📊 Verifica permessi applicati..."
echo ""
echo "Directory con permessi www-data:"
ls -ld "$PROJECT_ROOT/data" | grep www-data && log_info "  ✓ data"
ls -ld "$PROJECT_ROOT/config" | grep www-data && log_info "  ✓ config"
ls -ld "$PROJECT_ROOT/logs" | grep www-data && log_info "  ✓ logs"
ls -ld "$PROJECT_ROOT/backups" | grep www-data && log_info "  ✓ backups"

echo ""
echo "Gruppi utente www-data:"
groups www-data

echo ""
log_info "✅ Permessi sistemati con successo!"
log_info "🔄 Riavvia il servizio con: sudo systemctl restart access-control-web"