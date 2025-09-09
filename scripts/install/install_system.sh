#!/bin/bash
# ============================================================================
# Sistema Controllo Accessi RAEE - Script Installazione Completo
# Version: 3.0.0-RC1
# Author: Sistema Automatico
# Date: 2025-09-08
# ============================================================================

set -e  # Exit on error

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

# 1. RICHIESTA CREDENZIALI GITHUB
echo "============================================================================"
echo "STEP 1: CREDENZIALI GITHUB"
echo "============================================================================"
echo ""
echo "Il repository è privato. Inserire le credenziali GitHub:"
echo ""

read -p "GitHub Username: " GITHUB_USER
read -s -p "GitHub Password/Token: " GITHUB_TOKEN
echo ""
echo ""

# Test credenziali
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

log_info "Clone repository da GitHub..."
git clone -b "$BRANCH" "https://${GITHUB_USER}:${GITHUB_TOKEN}@${GITHUB_REPO}.git" "$INSTALL_DIR"

cd "$INSTALL_DIR"
log_success "Repository clonato con successo"

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
    bash "$SCRIPT_DIR/setup_drivers.sh"
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

log_info "Inizializzazione database..."
if [ -f "$SCRIPT_DIR/setup_database.py" ]; then
    python3 "$SCRIPT_DIR/setup_database.py" "$INSTALL_DIR/data/access_control.db"
else
    log_warning "Script setup_database.py non trovato, creazione database manuale"
    # Fallback: crea script temporaneo
    cat > /tmp/init_database.py << 'EOF'
#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime
import hashlib

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

# Admin user (password: admin123)
admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
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