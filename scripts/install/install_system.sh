#!/bin/bash
# ============================================================================
# Sistema Controllo Accessi RAEE - Script Installazione Completo
# Version: 3.0.0-RC1
# Author: Sistema Automatico
# Date: 2025-09-08
# ============================================================================

set -e  # Exit on error

# Assicura che le variabili di ambiente essenziali siano definite
export HOME=${HOME:-/root}
export USER=${USER:-root}
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurazione
INSTALL_DIR="/opt/access_control"
GITHUB_REPO="${GITHUB_REPO:-github.com/wlkr42/sistema-controllo-accessi}"
BRANCH="${GITHUB_BRANCH:-main}"  # Branch da clonare
SERVICE_USER="root"
PYTHON_VERSION="3.10"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Funzioni utility
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Determina ambiente (development/production)
INSTALL_ENV="${1:-development}"

# Header
clear
echo "============================================================================"
echo "         SISTEMA CONTROLLO ACCESSI RAEE - INSTALLAZIONE v3.0.0"
echo "============================================================================"
echo "Ambiente: ${INSTALL_ENV^^}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    log_error "Questo script deve essere eseguito come root"
fi

# Validazione ambiente
if [ "$INSTALL_ENV" != "development" ] && [ "$INSTALL_ENV" != "production" ]; then
    log_error "Ambiente non valido. Usa: $0 [development|production]"
fi

# Funzione per URL encoding
urlencode() {
    local string="${1}"
    local strlen=${#string}
    local encoded=""
    local pos c o

    for (( pos=0 ; pos<strlen ; pos++ )); do
        c=${string:$pos:1}
        case "$c" in
            [-_.~a-zA-Z0-9] ) o="${c}" ;;
            * ) printf -v o '%%%02x' "'$c" ;;
        esac
        encoded+="${o}"
    done
    echo "${encoded}"
}

# 1. RICHIESTA CREDENZIALI GITHUB
echo "============================================================================"
echo "STEP 1: CREDENZIALI GITHUB"
echo "============================================================================"
echo ""

# Controlla se le credenziali sono già fornite tramite variabili d'ambiente
if [ -n "$GIT_USERNAME" ] && [ -n "$GIT_PASSWORD" ]; then
    log_info "Uso credenziali da variabili d'ambiente"
    GITHUB_USER="$GIT_USERNAME"
    GITHUB_TOKEN="$GIT_PASSWORD"
else
    echo "Il repository è privato. Inserire le credenziali GitHub:"
    echo ""
    read -p "GitHub Username: " GITHUB_USER
    read -s -p "GitHub Password/Token: " GITHUB_TOKEN
    echo ""
    echo ""
fi

# URL encode delle credenziali per gestire caratteri speciali
log_info "Elaborazione credenziali..."
ENCODED_USER=$(urlencode "$GITHUB_USER")
ENCODED_TOKEN=$(urlencode "$GITHUB_TOKEN")

# Test credenziali con le credenziali originali (non encoded)
log_info "Verifica credenziali GitHub..."
if curl -s -u "${GITHUB_USER}:${GITHUB_TOKEN}" https://api.github.com/user > /dev/null 2>&1; then
    log_success "Credenziali GitHub valide"
else
    log_error "Credenziali GitHub non valide. Usa un Personal Access Token se hai 2FA attivo."
fi

# 2. PREPARAZIONE SISTEMA
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
    libpcsclite-dev \
    pcscd \
    pcsc-tools \
    usbutils \
    lsof \
    logrotate \
    systemd \
    psmisc

log_success "Dipendenze sistema installate"

# Funzione per clone con retry e fallback
clone_with_retry() {
    local url="$1"
    local dest="$2"
    local branch="$3"
    local max_attempts=3
    local attempt=1
    
    # Crea directory temporanea per Git config se necessario
    local git_config_dir="/tmp/git_config_$$"
    mkdir -p "$git_config_dir"
    export GIT_CONFIG_GLOBAL="$git_config_dir/.gitconfig"
    
    while [ $attempt -le $max_attempts ]; do
        log_info "Tentativo clone $attempt di $max_attempts..."
        
        # Pulisci directory se esiste da tentativo precedente
        [ -d "$dest" ] && rm -rf "$dest"
        
        # Prova metodi diversi basati sul numero di tentativo
        if [ $attempt -eq 1 ]; then
            # Primo tentativo: normale
            log_info "Metodo: Clone standard HTTPS"
            if git clone -b "$branch" "$url" "$dest" 2>&1; then
                log_success "Clone completato con metodo standard"
                rm -rf "$git_config_dir"
                return 0
            fi
        elif [ $attempt -eq 2 ]; then
            # Secondo tentativo: HTTP/1.1 con configurazioni inline
            log_info "Metodo: HTTP/1.1 (fix per errori HTTP2)"
            if GIT_CURL_VERBOSE=0 \
               git -c http.version=HTTP/1.1 \
                   -c http.postBuffer=524288000 \
                   -c http.lowSpeedLimit=0 \
                   -c http.lowSpeedTime=999999 \
                   clone -b "$branch" "$url" "$dest" 2>&1; then
                log_success "Clone completato con HTTP/1.1"
                rm -rf "$git_config_dir"
                return 0
            fi
        else
            # Terzo tentativo: shallow clone
            log_info "Metodo: Shallow clone (minimo trasferimento dati)"
            if GIT_CURL_VERBOSE=0 \
               git -c http.version=HTTP/1.1 \
                   -c http.postBuffer=524288000 \
                   -c core.compression=0 \
                   clone --depth 1 -b "$branch" "$url" "$dest" 2>&1; then
                log_success "Clone completato con shallow clone"
                rm -rf "$git_config_dir"
                return 0
            fi
        fi
        
        log_warning "Tentativo $attempt fallito"
        if [ $attempt -lt $max_attempts ]; then
            log_info "Attesa 10 secondi prima del prossimo tentativo..."
            sleep 10
        fi
        ((attempt++))
    done
    
    # Cleanup
    rm -rf "$git_config_dir"
    return 1
}

# Funzione di verifica connettività GitHub
check_github_connectivity() {
    log_info "Verifica connettività GitHub..."
    
    # Test connessione base
    if ! ping -c 1 github.com >/dev/null 2>&1; then
        log_warning "GitHub non raggiungibile via ping (potrebbe essere normale)"
    fi
    
    # Test HTTPS
    if curl -s -o /dev/null -w "%{http_code}" https://github.com 2>/dev/null | grep -q "200\|301"; then
        log_success "Connessione HTTPS a GitHub: OK"
        return 0
    else
        log_error "Impossibile connettersi a GitHub via HTTPS"
        return 1
    fi
}

# 3. CLONE REPOSITORY
echo "============================================================================"
echo "STEP 3: DOWNLOAD CODICE SORGENTE"
echo "============================================================================"
echo ""

log_info "Rimozione directory esistente se presente..."
if [ -d "$INSTALL_DIR" ]; then
    log_warning "Directory $INSTALL_DIR esistente, backup in corso..."
    mv "$INSTALL_DIR" "${INSTALL_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
fi

# Verifica connettività prima di procedere
if ! check_github_connectivity; then
    log_error "Problemi di connettività con GitHub. Verificare la connessione internet."
    exit 1
fi

# Clone con retry
log_info "Avvio clone repository da GitHub..."
CLONE_URL="https://${ENCODED_USER}:${ENCODED_TOKEN}@${GITHUB_REPO}.git"

if clone_with_retry "$CLONE_URL" "$INSTALL_DIR" "$BRANCH"; then
    cd "$INSTALL_DIR"
    log_success "Repository clonato con successo"
    
    # Verifica clone
    if [ -f "requirements.txt" ]; then
        log_success "Verifica repository: OK (requirements.txt presente)"
    else
        log_warning "Verifica repository: file requirements.txt non trovato"
    fi
else
    log_error "Impossibile clonare repository dopo 3 tentativi. Verificare:"
    echo "  1. Connessione internet stabile"
    echo "  2. Credenziali GitHub corrette"
    echo "  3. Repository accessibile: https://github.com/wlkr42/sistema-controllo-accessi"
    echo "  4. Firewall/proxy non bloccano GitHub"
    exit 1
fi

# 4. SETUP PYTHON ENVIRONMENT
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
pip install -r requirements.txt -q

# Installa Gunicorn solo se richiesto ambiente produzione
if [ "${INSTALL_ENV:-development}" = "production" ]; then
    log_info "Installazione server WSGI di produzione (Gunicorn)..."
    pip install gunicorn gevent -q
else
    log_info "Ambiente sviluppo - usando Flask development server"
fi

log_success "Ambiente Python configurato"

# 5. SETUP DRIVERS HARDWARE
echo "============================================================================"
echo "STEP 5: INSTALLAZIONE DRIVERS HARDWARE"
echo "============================================================================"
echo ""

log_info "Esecuzione script setup drivers..."
if [ -f "$SCRIPT_DIR/setup_drivers.sh" ]; then
    # Passa il path di installazione allo script
    INSTALL_DIR="$INSTALL_DIR" bash "$SCRIPT_DIR/setup_drivers.sh"
else
    log_warning "Script setup_drivers.sh non trovato, configurazione manuale richiesta"
fi

# 6. CREAZIONE STRUTTURA DIRECTORY
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

# Permessi base
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

# 7. INIZIALIZZAZIONE DATABASE
echo "============================================================================"
echo "STEP 7: INIZIALIZZAZIONE DATABASE"
echo "============================================================================"
echo ""

# Assicura che la directory data esista
mkdir -p "$INSTALL_DIR/data"
chmod 755 "$INSTALL_DIR/data"

log_info "Inizializzazione database..."
if [ -f "$SCRIPT_DIR/setup_database.py" ]; then
    python3 "$SCRIPT_DIR/setup_database.py" "$INSTALL_DIR/data/access.db"
else
    log_warning "Script setup_database.py non trovato, creazione database manuale"
    # Fallback: crea script temporaneo
    cat > /tmp/init_database.py << 'EOF'
#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime
import hashlib

# Assicura che la directory data esista
os.makedirs('/opt/access_control/data', exist_ok=True)
db_path = '/opt/access_control/data/access.db'

# Crea connessione
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crea tabelle
cursor.executescript('''
-- Tabella utenti autorizzati (tessere)
CREATE TABLE IF NOT EXISTS utenti_autorizzati (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codice_fiscale TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    email TEXT,
    telefono TEXT,
    attivo BOOLEAN DEFAULT 1,
    gruppi TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    created_by TEXT,
    updated_by TEXT
);

-- Tabella log accessi
CREATE TABLE IF NOT EXISTS log_accessi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    codice_fiscale TEXT NOT NULL,
    autorizzato BOOLEAN,
    durata_elaborazione REAL,
    terminale_id TEXT,
    nome_utente TEXT,
    motivo_rifiuto TEXT,
    tipo_accesso TEXT
);

-- Tabella configurazione sistema
CREATE TABLE IF NOT EXISTS system_settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella utenti sistema (login web)
CREATE TABLE IF NOT EXISTS utenti_sistema (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT,
    role TEXT DEFAULT 'viewer',
    attivo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    must_change_password BOOLEAN DEFAULT 0,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    created_by TEXT,
    modified_at TIMESTAMP,
    modified_by TEXT,
    nome TEXT,
    cognome TEXT,
    avatar_path TEXT,
    telefono TEXT,
    bio TEXT,
    data_nascita DATE,
    indirizzo TEXT
);

-- Tabella configurazione relè
CREATE TABLE IF NOT EXISTS relay_config (
    relay_id INTEGER PRIMARY KEY,
    nome TEXT,
    descrizione TEXT,
    azione_accesso_valido TEXT DEFAULT 'pulse',
    durata_impulso_valido INTEGER DEFAULT 3,
    azione_accesso_invalido TEXT DEFAULT 'off',
    durata_impulso_invalido INTEGER DEFAULT 0,
    attivo BOOLEAN DEFAULT 1
);

-- Tabella fasce orarie
CREATE TABLE IF NOT EXISTS fascie_orarie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    giorno_settimana INTEGER,
    ora_inizio TEXT,
    ora_fine TEXT,
    attivo BOOLEAN DEFAULT 1,
    descrizione TEXT
);

-- Tabella conteggio mensile
CREATE TABLE IF NOT EXISTS conteggio_ingressi_mensili (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codice_fiscale TEXT NOT NULL,
    mese INTEGER NOT NULL,
    anno INTEGER NOT NULL,
    numero_ingressi INTEGER DEFAULT 0,
    ultimo_ingresso TIMESTAMP,
    UNIQUE(codice_fiscale, mese, anno)
);

-- Tabella limiti accesso
CREATE TABLE IF NOT EXISTS limiti_accesso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT DEFAULT 'mensile',
    limite INTEGER DEFAULT 10,
    attivo BOOLEAN DEFAULT 1
);

-- Tabella eventi sistema
CREATE TABLE IF NOT EXISTS eventi_sistema (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo_evento TEXT,
    livello TEXT,
    messaggio TEXT,
    componente TEXT,
    utente TEXT
);

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_log_accessi_timestamp ON log_accessi(timestamp);
CREATE INDEX IF NOT EXISTS idx_log_accessi_cf ON log_accessi(codice_fiscale);
CREATE INDEX IF NOT EXISTS idx_utenti_cf ON utenti_autorizzati(codice_fiscale);
CREATE INDEX IF NOT EXISTS idx_eventi_timestamp ON eventi_sistema(timestamp);
''')

# Inserisci dati iniziali

# Admin user (password: admin123) - usa bcrypt come il sistema reale
import bcrypt
admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
cursor.execute('''
    INSERT OR IGNORE INTO utenti_sistema (username, password, email, role, nome, cognome)
    VALUES (?, ?, ?, ?, ?, ?)
''', ('admin', admin_password, 'admin@example.com', 'admin', 'Admin', 'Sistema'))

# Configurazione sistema default
default_settings = [
    ('sistema.nome_installazione', 'Sistema Controllo Accessi RAEE'),
    ('sistema.timezone', 'Europe/Rome'),
    ('sistema.formato_data', 'DD/MM/YYYY'),
    ('sistema.formato_ora', '24'),
    ('sistema.ntp_server', 'pool.ntp.org'),
    ('sistema.versione', '3.0.0'),
    ('sync.sync_enabled', 'false'),
    ('sync.sync_interval_hours', '12'),
    ('backup.auto_backup_enabled', 'true'),
    ('backup.backup_interval', 'daily'),
    ('backup.retention_days', '30')
]

for key, value in default_settings:
    cursor.execute('INSERT OR IGNORE INTO system_settings (key, value) VALUES (?, ?)', (key, value))

# Configurazione relè default
for i in range(1, 9):
    cursor.execute('''
        INSERT OR IGNORE INTO relay_config (relay_id, nome, descrizione)
        VALUES (?, ?, ?)
    ''', (i, f'Relè {i}', f'Configurazione relè {i}'))

# Relè 1 per cancello
cursor.execute('''
    UPDATE relay_config 
    SET nome = 'Cancello Ingresso',
        descrizione = 'Controllo cancello principale',
        azione_accesso_valido = 'pulse',
        durata_impulso_valido = 5
    WHERE relay_id = 1
''')

# Fasce orarie default (Lun-Ven 8:00-18:00)
for day in range(1, 6):  # 1=Lunedì, 5=Venerdì
    cursor.execute('''
        INSERT INTO fascie_orarie (giorno_settimana, ora_inizio, ora_fine, descrizione)
        VALUES (?, ?, ?, ?)
    ''', (day, '08:00', '18:00', f'Orario standard giorno {day}'))

# Sabato mattina
cursor.execute('''
    INSERT INTO fascie_orarie (giorno_settimana, ora_inizio, ora_fine, descrizione)
    VALUES (?, ?, ?, ?)
''', (6, '08:00', '13:00', 'Sabato mattina'))

# Limite mensile default
cursor.execute('''
    INSERT INTO limiti_accesso (tipo, limite, attivo)
    VALUES ('mensile', 10, 1)
''')

conn.commit()
conn.close()

print("Database inizializzato con successo")
EOF

    python3 /tmp/init_database.py
    rm /tmp/init_database.py
fi

log_success "Database inizializzato"

# 8. CONFIGURAZIONE FILE
echo "============================================================================"
echo "STEP 8: CONFIGURAZIONE FILE SISTEMA"
echo "============================================================================"
echo ""

# Device assignments default
log_info "Creazione configurazione hardware..."
cat > "$INSTALL_DIR/config/device_assignments.json" << 'EOF'
{
  "assignments": {
    "card_reader": {
      "device_key": "usb:23d8:0285",
      "device_name": "CREATOR(CHINA)TECH CO.,LTD CRT-285",
      "device_path": "/dev/ttyACM0"
    },
    "relay_controller": {
      "device_key": "usb:04d8:ffee",
      "device_name": "USB-RLY08",
      "device_path": "/dev/ttyUSB0"
    }
  }
}
EOF

log_success "Configurazione file creata"

# 9. INSTALLAZIONE SERVIZI E CONFIGURAZIONI
echo "============================================================================"
echo "STEP 9: INSTALLAZIONE SERVIZI SYSTEMD E CONFIGURAZIONI"
echo "============================================================================"
echo ""

log_info "Esecuzione script setup servizi (ambiente: $INSTALL_ENV)..."
if [ -f "$SCRIPT_DIR/setup_services.sh" ]; then
    bash "$SCRIPT_DIR/setup_services.sh" "$INSTALL_ENV"
else
    log_warning "Script setup_services.sh non trovato, configurazione manuale richiesta"
    # Fallback minimo
    if [ -f "$INSTALL_DIR/scripts/system/access-control-web.service" ]; then
        cp "$INSTALL_DIR/scripts/system/access-control-web.service" /etc/systemd/system/
        systemctl daemon-reload
        systemctl enable access-control-web.service
    fi
fi

# 10. TEST HARDWARE
echo "============================================================================"
echo "STEP 10: TEST HARDWARE"
echo "============================================================================"
echo ""

log_info "Ricerca hardware collegato..."

# Cerca CRT-285
if lsusb | grep -q "23d8:0285"; then
    log_success "✓ Lettore tessere CRT-285 rilevato"
else
    log_warning "✗ Lettore tessere CRT-285 NON rilevato"
fi

# Cerca USB-RLY08
if lsusb | grep -q "04d8:ffee"; then
    log_success "✓ Controller relè USB-RLY08 rilevato"
else
    log_warning "✗ Controller relè USB-RLY08 NON rilevato"
fi

# 11. AVVIO SERVIZI (se non già avviati da setup_services.sh)
echo "============================================================================"
echo "STEP 11: VERIFICA AVVIO SERVIZI"
echo "============================================================================"
echo ""

if ! systemctl is-active --quiet access-control-web.service; then
    log_info "Avvio servizio principale..."
    systemctl start access-control-web.service
    sleep 3
fi

if systemctl is-active --quiet access-control-web.service; then
    log_success "✓ Servizio principale attivo"
else
    log_warning "✗ Servizio principale non attivo, controllare i log"
fi

if ! systemctl is-active --quiet access-monitor.service; then
    log_info "Avvio monitor 24/7..."
    systemctl start access-monitor.service
fi

if systemctl is-active --quiet access-monitor.service; then
    log_success "✓ Monitor 24/7 attivo"
else
    log_warning "✗ Monitor non attivo, controllare i log"
fi

# 12. INFORMAZIONI FINALI
echo ""
echo "============================================================================"
echo "                    INSTALLAZIONE COMPLETATA CON SUCCESSO!"
echo "============================================================================"
echo ""
echo "INFORMAZIONI SISTEMA:"
echo "---------------------"
echo "Directory installazione: $INSTALL_DIR"
echo "Database: $INSTALL_DIR/data/access.db"
echo "Log: $INSTALL_DIR/logs/"
echo "Backup: $INSTALL_DIR/backups/"
echo ""
echo "ACCESSO WEB INTERFACE:"
echo "----------------------"
echo "URL: http://$(hostname -I | awk '{print $1}'):5000"
echo "Username: admin"
echo "Password: admin123"
echo ""
echo "SERVIZI SYSTEMD:"
echo "----------------"
echo "Principale: systemctl status access-control-web"
echo "Monitor: systemctl status access-monitor"
echo ""
echo "COMANDI UTILI:"
echo "--------------"
echo "Restart: sudo systemctl restart access-control-web"
echo "Log: sudo journalctl -u access-control-web -f"
echo "Health: curl http://localhost:5000/api/health"
echo ""
echo "IMPORTANTE:"
echo "-----------"
echo "1. Cambiare la password admin al primo accesso"
echo "2. Configurare il sistema da web interface"
echo "3. Verificare che l'hardware sia collegato"
echo ""
echo "============================================================================"
echo "                         SISTEMA PRONTO ALL'USO!"
echo "============================================================================"