#!/bin/bash
# ============================================================================
# Sistema Controllo Accessi RAEE - Script Installazione Automatica/Interattiva
# Version: 3.0.0-RC1
# 
# Uso interattivo:
#   sudo bash install_auto.sh
#
# Uso non interattivo (con config file):
#   source install_config.sh && sudo bash install_auto.sh
#
# Uso non interattivo (parametri):
#   sudo GITHUB_REPO="github.com/user/repo" GITHUB_USER="user" GITHUB_TOKEN="token" bash install_auto.sh
# ============================================================================

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Funzioni utility
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Configurazione con valori di default
INSTALL_DIR="${INSTALL_DIR:-/opt/access_control}"
GITHUB_REPO="${GITHUB_REPO:-}"
GITHUB_BRANCH="${GITHUB_BRANCH:-main}"
GITHUB_USER="${GITHUB_USER:-}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
INSTALL_ENV="${INSTALL_ENV:-development}"
PYTHON_VERSION="${PYTHON_VERSION:-3.10}"
DB_NAME="${DB_NAME:-access_control.db}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INTERACTIVE="${INTERACTIVE:-auto}"  # auto, yes, no

# Header
clear
echo "============================================================================"
echo "         SISTEMA CONTROLLO ACCESSI RAEE - INSTALLAZIONE v3.0.0"
echo "============================================================================"
echo "Ambiente: ${INSTALL_ENV^^}"
echo "Directory: $INSTALL_DIR"
echo ""

# Check root
if [ "$EUID" -ne 0 ]; then 
    log_error "Questo script deve essere eseguito come root"
fi

# Determina modalità interattiva
if [ "$INTERACTIVE" = "auto" ]; then
    # Auto-detect: interattivo se mancano parametri essenziali
    if [ -z "$GITHUB_REPO" ] || [ -z "$GITHUB_USER" ] || [ -z "$GITHUB_TOKEN" ]; then
        INTERACTIVE="yes"
    else
        INTERACTIVE="no"
    fi
fi

# 1. CONFIGURAZIONE GITHUB
echo "============================================================================"
echo "STEP 1: CONFIGURAZIONE GITHUB"
echo "============================================================================"
echo ""

# Repository
if [ -z "$GITHUB_REPO" ]; then
    if [ "$INTERACTIVE" = "yes" ]; then
        read -p "Repository GitHub (es: github.com/user/repo): " GITHUB_REPO
    else
        log_error "GITHUB_REPO non configurato. Impostare la variabile o usare modalità interattiva"
    fi
fi

# Credenziali
if [ -z "$GITHUB_USER" ] || [ -z "$GITHUB_TOKEN" ]; then
    if [ "$INTERACTIVE" = "yes" ]; then
        echo "Il repository è privato. Inserire le credenziali GitHub:"
        [ -z "$GITHUB_USER" ] && read -p "GitHub Username: " GITHUB_USER
        [ -z "$GITHUB_TOKEN" ] && read -s -p "GitHub Password/Token: " GITHUB_TOKEN && echo ""
    else
        log_warning "Tentativo clone senza autenticazione (funziona solo per repo pubblici)"
    fi
fi

# Test credenziali se fornite
if [ -n "$GITHUB_USER" ] && [ -n "$GITHUB_TOKEN" ]; then
    log_info "Verifica credenziali GitHub..."
    if curl -s -u "${GITHUB_USER}:${GITHUB_TOKEN}" https://api.github.com/user > /dev/null 2>&1; then
        log_success "Credenziali GitHub valide"
    else
        log_error "Credenziali GitHub non valide"
    fi
fi

# 2. PREPARAZIONE SISTEMA
echo ""
echo "============================================================================"
echo "STEP 2: PREPARAZIONE SISTEMA"
echo "============================================================================"
echo ""

log_info "Aggiornamento sistema..."
apt-get update -qq

log_info "Installazione dipendenze sistema..."
apt-get install -y -qq \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-venv \
    python3-pip \
    git \
    sqlite3 \
    curl \
    wget \
    build-essential \
    python${PYTHON_VERSION}-dev \
    libusb-1.0-0 \
    libusb-1.0-0-dev \
    libudev-dev \
    usbutils \
    lsof \
    logrotate \
    systemd \
    psmisc

log_success "Dipendenze sistema installate"

# 3. CLONE REPOSITORY
echo ""
echo "============================================================================"
echo "STEP 3: DOWNLOAD CODICE SORGENTE"
echo "============================================================================"
echo ""

# Backup directory esistente
if [ -d "$INSTALL_DIR" ]; then
    if [ "$INTERACTIVE" = "yes" ]; then
        read -p "Directory $INSTALL_DIR esistente. Fare backup? (s/n): " DO_BACKUP
        if [ "$DO_BACKUP" = "s" ]; then
            BACKUP_DIR="${INSTALL_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
            log_info "Backup in $BACKUP_DIR..."
            mv "$INSTALL_DIR" "$BACKUP_DIR"
        else
            log_warning "Sovrascrittura directory esistente..."
            rm -rf "$INSTALL_DIR"
        fi
    else
        BACKUP_DIR="${INSTALL_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
        log_info "Backup automatico in $BACKUP_DIR..."
        mv "$INSTALL_DIR" "$BACKUP_DIR"
    fi
fi

# Clone repository
log_info "Clone repository da GitHub..."
if [ -n "$GITHUB_USER" ] && [ -n "$GITHUB_TOKEN" ]; then
    # Clone autenticato
    git clone -b "$GITHUB_BRANCH" "https://${GITHUB_USER}:${GITHUB_TOKEN}@${GITHUB_REPO}.git" "$INSTALL_DIR"
else
    # Clone pubblico
    git clone -b "$GITHUB_BRANCH" "https://${GITHUB_REPO}.git" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"
log_success "Repository clonato con successo"

# 4. SETUP PYTHON
echo ""
echo "============================================================================"
echo "STEP 4: CONFIGURAZIONE PYTHON"
echo "============================================================================"
echo ""

log_info "Creazione virtual environment..."
python${PYTHON_VERSION} -m venv venv

log_info "Attivazione virtual environment..."
source venv/bin/activate

log_info "Aggiornamento pip..."
pip install --upgrade pip setuptools wheel -q

log_info "Installazione dipendenze Python..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
else
    log_warning "requirements.txt non trovato, installazione dipendenze base..."
    pip install flask sqlalchemy pyserial requests cryptography -q
fi

# Installa Gunicorn solo in produzione
if [ "$INSTALL_ENV" = "production" ]; then
    log_info "Installazione server WSGI di produzione (Gunicorn)..."
    pip install gunicorn gevent -q
fi

log_success "Ambiente Python configurato"

# 5. SETUP DRIVERS
echo ""
echo "============================================================================"
echo "STEP 5: INSTALLAZIONE DRIVERS HARDWARE"
echo "============================================================================"
echo ""

if [ -f "$SCRIPT_DIR/setup_drivers.sh" ]; then
    bash "$SCRIPT_DIR/setup_drivers.sh"
else
    log_warning "Script setup_drivers.sh non trovato, configurazione driver manuale"
fi

# 6. CREAZIONE STRUTTURA
echo ""
echo "============================================================================"
echo "STEP 6: CREAZIONE STRUTTURA DIRECTORY"
echo "============================================================================"
echo ""

log_info "Creazione directory necessarie..."
mkdir -p "$INSTALL_DIR/data"
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "$INSTALL_DIR/backups"
mkdir -p "$INSTALL_DIR/config"
mkdir -p "$INSTALL_DIR/src/api/static/avatars"

chmod 755 "$INSTALL_DIR/data"
chmod 755 "$INSTALL_DIR/logs"
chmod 755 "$INSTALL_DIR/backups"

log_success "Struttura directory creata"

# Setup completo permessi
log_info "Configurazione permessi completa..."
if [ -f "$SCRIPT_DIR/setup_permissions.sh" ]; then
    bash "$SCRIPT_DIR/setup_permissions.sh" "$INSTALL_DIR"
else
    log_warning "Script setup_permissions.sh non trovato, permessi base applicati"
fi

# 7. DATABASE
echo ""
echo "============================================================================"
echo "STEP 7: INIZIALIZZAZIONE DATABASE"
echo "============================================================================"
echo ""

DB_PATH="$INSTALL_DIR/data/$DB_NAME"

if [ -f "$SCRIPT_DIR/setup_database.py" ]; then
    python3 "$SCRIPT_DIR/setup_database.py" "$DB_PATH"
else
    log_warning "Script setup_database.py non trovato, creazione database base..."
    # Database minimo
    sqlite3 "$DB_PATH" "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT);"
fi

log_success "Database inizializzato"

# 8. SERVIZI
echo ""
echo "============================================================================"
echo "STEP 8: INSTALLAZIONE SERVIZI"
echo "============================================================================"
echo ""

if [ -f "$SCRIPT_DIR/setup_services.sh" ]; then
    bash "$SCRIPT_DIR/setup_services.sh" "$INSTALL_ENV"
else
    log_warning "Script setup_services.sh non trovato, servizi non configurati"
fi

# 9. VERIFICA
echo ""
echo "============================================================================"
echo "STEP 9: VERIFICA INSTALLAZIONE"
echo "============================================================================"
echo ""

if [ -f "$SCRIPT_DIR/verify_installation.sh" ]; then
    bash "$SCRIPT_DIR/verify_installation.sh"
else
    # Verifica base
    if systemctl is-active --quiet access-control-web.service; then
        log_success "Sistema attivo"
    else
        log_warning "Sistema non attivo, avviare manualmente con: systemctl start access-control-web"
    fi
fi

# 10. INFORMAZIONI FINALI
echo ""
echo "============================================================================"
echo "                    INSTALLAZIONE COMPLETATA!"
echo "============================================================================"
echo ""
echo "INFORMAZIONI SISTEMA:"
echo "---------------------"
echo "Directory: $INSTALL_DIR"
echo "Database: $DB_PATH"
echo "Ambiente: $INSTALL_ENV"
echo "Repository: $GITHUB_REPO"
echo "Branch: $GITHUB_BRANCH"
echo ""
echo "ACCESSO WEB:"
echo "------------"
echo "URL: http://$(hostname -I | awk '{print $1}'):5000"
echo "Username: admin"
echo "Password: admin123"
echo ""
echo "COMANDI UTILI:"
echo "--------------"
echo "Start: systemctl start access-control-web"
echo "Stop: systemctl stop access-control-web"
echo "Status: systemctl status access-control-web"
echo "Logs: journalctl -fu access-control-web"
echo ""
echo "============================================================================"