#!/bin/bash

# Script di installazione automatica Sistema Controllo Accessi
# Requisiti: Ubuntu 22.04 con accesso root
# Destinazione: /opt/access_control
# Utente: wlkr42

set -e

# Verifica privilegi root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Questo script deve essere eseguito come root (sudo)"
   exit 1
fi

# Configurazione
INSTALL_PATH="/opt/access_control"
USER="wlkr42"
GROUP="wlkr42"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Installazione Sistema Controllo Accessi ==="
echo "Percorso installazione: $INSTALL_PATH"
echo "Utente: $USER"
echo "Directory script: $SCRIPT_DIR"
echo ""

# Funzione per gestire errori
handle_error() {
    echo "❌ Errore durante l'installazione: $1"
    echo "Consultare i log per maggiori dettagli"
    exit 1
}

# Funzione per verificare comando
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "⚠️  Comando $1 non trovato, installazione in corso..."
        return 1
    fi
    return 0
}

echo "🔍 Verifica sistema operativo..."
if ! grep -q "Ubuntu 22.04" /etc/os-release; then
    echo "⚠️  Sistema operativo non testato (previsto Ubuntu 22.04). Continuare? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📦 Aggiornamento repository e installazione dipendenze..."

# Aggiornamento sistema
apt update -y || handle_error "Aggiornamento repository fallito"

# Analisi preventiva requirements.txt per dipendenze di sistema
echo "🔍 Analisi dipendenze necessarie..."
REQ_FILE=""
if [ -f "$PACKAGE_DIR/requirements.txt" ]; then
    REQ_FILE="$PACKAGE_DIR/requirements.txt"
elif [ -f "requirements.txt" ]; then
    REQ_FILE="requirements.txt"
fi

EXTRA_PACKAGES=()
if [ -n "$REQ_FILE" ]; then
    echo "Analisi di $REQ_FILE..."
    
    # Smart card dependencies
    if grep -q "pyscard" "$REQ_FILE"; then
        echo "  - Rilevato pyscard, aggiunta dipendenze smart card"
        EXTRA_PACKAGES+=("libpcsclite-dev" "pcscd" "swig" "libtool")
    fi
    
    # USB dependencies  
    if grep -q "pyusb" "$REQ_FILE"; then
        echo "  - Rilevato pyusb, aggiunta dipendenze USB"
        EXTRA_PACKAGES+=("libudev-dev")
    fi
    
    # Excel/office dependencies
    if grep -q -E "(openpyxl|xlrd|xlwt)" "$REQ_FILE"; then
        echo "  - Rilevate dipendenze Excel"
        EXTRA_PACKAGES+=("python3-openpyxl")
    fi
    
    # Crypto dependencies
    if grep -q -E "(cryptography|pycrypto)" "$REQ_FILE"; then
        echo "  - Rilevate dipendenze crypto"
        EXTRA_PACKAGES+=("libffi-dev" "libssl-dev")
    fi
fi

# Installazione pacchetti base + extra
ALL_PACKAGES=(
    "python3"
    "python3-pip" 
    "python3-dev"
    "python3-venv"
    "build-essential"
    "git"
    "sqlite3"
    "cron"
    "rsync"
    "tar"
    "gzip"
    "systemd"
    "ufw"
    "libusb-1.0-0"
    "libusb-1.0-0-dev"
    "pkg-config"
    "cmake"
    "${EXTRA_PACKAGES[@]}"
)

echo "Installazione pacchetti richiesti..."
for package in "${ALL_PACKAGES[@]}"; do
    if [ -n "$package" ]; then
        echo "  - Installazione $package..."
        apt install -y "$package" || echo "⚠️  Pacchetto $package non trovato, continuo..."
    fi
done

# Installazione dipendenze Python aggiuntivi per hardware
echo "Installazione dipendenze Python per hardware..."
python3 -m pip install --upgrade pip --break-system-packages 2>/dev/null || pip3 install --upgrade pip
python3 -m pip install pyserial pyusb --break-system-packages 2>/dev/null || pip3 install pyserial pyusb || echo "⚠️  Alcune dipendenze hardware potrebbero non essere disponibili"

echo "👤 Gestione utente $USER..."

# Creazione utente se non esiste
if ! id "$USER" &>/dev/null; then
    echo "Creazione utente $USER..."
    useradd -r -s /bin/bash -d "$INSTALL_PATH" -m "$USER" || handle_error "Creazione utente fallita"
    
    # Aggiunta ai gruppi necessari per accesso hardware
    usermod -a -G dialout,plugdev "$USER" 2>/dev/null || echo "⚠️  Alcuni gruppi hardware non disponibili"
else
    echo "✅ Utente $USER già esistente"
fi

echo "📁 Preparazione directory di installazione..."

# Backup installazione esistente
if [ -d "$INSTALL_PATH" ]; then
    BACKUP_DIR="${INSTALL_PATH}_backup_$(date +%Y%m%d_%H%M%S)"
    echo "Backup installazione esistente in $BACKUP_DIR..."
    mv "$INSTALL_PATH" "$BACKUP_DIR"
fi

# Creazione directory
mkdir -p "$INSTALL_PATH"/{src,config,scripts,backups,logs,cron,systemd}
mkdir -p /var/log/access_control

echo "📋 Copia file di installazione..."

# Verifica presenza file sorgente nel pacchetto estratto
PACKAGE_DIR=""

# Prima controlla se siamo già nella directory del pacchetto
if [ -d "src" ] && [ -d "config" ] && [ -d "scripts" ]; then
    PACKAGE_DIR="."
    echo "Rilevata directory pacchetto corrente: $(pwd)"
else
    # Cerca directory del pacchetto nella directory corrente
    for dir in sistema-controllo-accessi-*; do
        if [ -d "$dir" ] && [ -d "$dir/src" ]; then
            PACKAGE_DIR="$dir"
            break
        fi
    done
fi

if [ -z "$PACKAGE_DIR" ]; then
    echo "❌ Directory del pacchetto non trovata!"
    echo "Assicurarsi di:"
    echo "1. Aver estratto il file .tar.gz: tar -xzf sistema-controllo-accessi-*.tar.gz"
    echo "2. Essere nella directory corretta"
    echo "3. Eseguire: cd sistema-controllo-accessi-* && sudo bash install.sh"
    echo ""
    echo "Directory corrente: $(pwd)"
    echo "Contenuto:"
    ls -la
    handle_error "Directory del pacchetto non trovata"
fi

echo "Trovata directory pacchetto: $PACKAGE_DIR"

# Copia file
echo "Copia sorgenti..."
cp -r "$PACKAGE_DIR/src"/* "$INSTALL_PATH/src/" || handle_error "Copia sorgenti fallita"

echo "Copia configurazioni..."
cp -r "$PACKAGE_DIR/config"/* "$INSTALL_PATH/config/" || handle_error "Copia configurazioni fallita"

echo "Copia script..."
cp -r "$PACKAGE_DIR/scripts"/* "$INSTALL_PATH/scripts/" || handle_error "Copia script fallita"

echo "Copia documentazione..."
cp -r "$PACKAGE_DIR/docs"/* "$INSTALL_PATH/docs/" 2>/dev/null || echo "⚠️  Documentazione non trovata"

# Copia requirements.txt se presente
if [ -f "$PACKAGE_DIR/requirements.txt" ]; then
    cp "$PACKAGE_DIR/requirements.txt" "$INSTALL_PATH/"
fi

echo "🐍 Installazione dipendenze Python..."

echo "🐍 Creazione ambiente virtuale Python..."

# Creazione ambiente virtuale
VENV_PATH="$INSTALL_PATH/venv"

if [ -d "$VENV_PATH" ]; then
    echo "Ambiente virtuale esistente trovato, rimozione..."
    rm -rf "$VENV_PATH"
fi

echo "Creazione nuovo ambiente virtuale in $VENV_PATH..."
python3 -m venv "$VENV_PATH" || handle_error "Creazione ambiente virtuale fallita"

# Attivazione ambiente virtuale
echo "Attivazione ambiente virtuale..."
source "$VENV_PATH/bin/activate" || handle_error "Attivazione ambiente virtuale fallita"

echo "✅ Ambiente virtuale creato e attivato"
echo "Python path: $(which python)"
echo "Pip path: $(which pip)"

# Aggiornamento pip nell'ambiente virtuale
echo "Aggiornamento pip nell'ambiente virtuale..."
pip install --upgrade pip

# Funzione per installazione Python nell'ambiente virtuale
install_python_deps() {
    echo "=== Installazione Dipendenze Python nell'Ambiente Virtuale ==="
    
    # Prima: installa dipendenze essenziali
    echo "1. Installazione pacchetti essenziali..."
    ESSENTIAL_PACKAGES=("wheel" "setuptools" "flask" "requests")
    
    for package in "${ESSENTIAL_PACKAGES[@]}"; do
        echo "  - Installazione $package..."
        pip install "$package" || echo "    ⚠️  Errore installazione $package"
    done
    
    # Seconda: installa da requirements.txt se disponibile
    if [ -f "$INSTALL_PATH/requirements.txt" ]; then
        echo "2. Installazione da requirements.txt..."
        echo "   Contenuto requirements.txt:"
        cat "$INSTALL_PATH/requirements.txt"
        echo ""
        
        # Installazione con gestione errori
        echo "   Tentativo installazione completa..."
        if ! pip install -r "$INSTALL_PATH/requirements.txt"; then
            echo "   ⚠️  Installazione completa fallita, installazione selettiva..."
            
            # Installazione riga per riga saltando errori
            while IFS= read -r line; do
                # Salta commenti e righe vuote
                if [[ "$line" =~ ^[[:space:]]*# ]] || [[ -z "$line" ]]; then
                    continue
                fi
                
                # Estrai nome pacchetto
                package=$(echo "$line" | sed 's/[<>=!].*//' | tr -d ' ')
                if [ -n "$package" ]; then
                    echo "     - Installazione $package..."
                    if ! pip install "$package"; then
                        echo "       ❌ Fallita installazione $package, continuo..."
                    else
                        echo "       ✅ Installato $package"
                    fi
                fi
            done < "$INSTALL_PATH/requirements.txt"
        else
            echo "   ✅ Installazione completa riuscita"
        fi
    else
        echo "2. File requirements.txt non trovato"
    fi
    
    # Terza: verifica dipendenze critiche
    echo "3. Verifica dipendenze critiche..."
    CRITICAL_MODULES=("flask" "requests")
    ALL_GOOD=true
    
    for module in "${CRITICAL_MODULES[@]}"; do
        if python -c "import $module" 2>/dev/null; then
            echo "  ✅ $module disponibile"
        else
            echo "  ❌ $module MANCANTE"
            ALL_GOOD=false
            
            # Tentativo installazione singola
            echo "    Tentativo installazione $module..."
            pip install "$module" || echo "    Installazione $module fallita"
        fi
    done
    
    if [ "$ALL_GOOD" = true ]; then
        echo "🎉 Tutte le dipendenze critiche sono installate!"
    else
        echo "⚠️  Verificare manualmente le dipendenze mancanti"
    fi
    
    # Lista pacchetti installati
    echo "4. Pacchetti installati nell'ambiente virtuale:"
    pip list
}

# Esegui installazione dipendenze nell'ambiente virtuale
install_python_deps

echo "🔐 Configurazione permessi..."

# Assegnazione permessi
chown -R "$USER:$GROUP" "$INSTALL_PATH"
chmod -R 755 "$INSTALL_PATH"
chmod +x "$INSTALL_PATH"/scripts/*.sh "$INSTALL_PATH"/scripts/*.py

# Permessi speciali per directory sensibili
chmod 700 "$INSTALL_PATH/config"
chmod 750 "$INSTALL_PATH/backups"
chown -R "$USER:$GROUP" /var/log/access_control
chmod 755 /var/log/access_control

echo "⚙️  Installazione servizio systemd..."

# Installazione servizio systemd
if [ -f "$PACKAGE_DIR/systemd/access-control.service" ]; then
    cp "$PACKAGE_DIR/systemd/access-control.service" /etc/systemd/system/
    systemctl daemon-reload
    echo "✅ Servizio systemd installato da pacchetto"
else
    echo "⚠️  File servizio systemd non trovato, creazione servizio con ambiente virtuale..."
    cat > /etc/systemd/system/access-control.service << EOF
[Unit]
Description=Sistema di Controllo Accessi
After=network.target

[Service]
Type=simple
User=$USER
Group=$GROUP
WorkingDirectory=$INSTALL_PATH/src/api
Environment=PYTHONPATH=$INSTALL_PATH/src
ExecStart=$INSTALL_PATH/venv/bin/python $INSTALL_PATH/src/api/web_api.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

# Limitazioni di sicurezza
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$INSTALL_PATH
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    echo "✅ Servizio systemd creato con ambiente virtuale"
fi

echo "⏰ Configurazione cron jobs..."

# Installazione cron jobs
if [ -f "$PACKAGE_DIR/cron/access-control-cron" ]; then
    # Copia file cron per l'utente
    sudo -u "$USER" crontab "$PACKAGE_DIR/cron/access-control-cron"
    echo "✅ Cron jobs installati"
else
    echo "⚠️  File cron non trovato"
fi

# Avvio servizio cron
systemctl enable cron
systemctl start cron

echo "🔥 Configurazione firewall..."

# Configurazione firewall (UFW su Ubuntu)
if command -v ufw &> /dev/null; then
    echo "Configurazione UFW per porta 5000..."
    ufw allow 5000/tcp
    echo "✅ UFW configurato"
else
    echo "⚠️  UFW non disponibile, configurazione firewall saltata"
fi

echo "🗄️  Inizializzazione database..."

# Copia database template e inizializza
DATABASE_PATH="$INSTALL_PATH/src/access.db"
TEMPLATE_PATH="$INSTALL_PATH/src/access.db.template"

if [ -f "$TEMPLATE_PATH" ]; then
    echo "Copia database template..."
    cp "$TEMPLATE_PATH" "$DATABASE_PATH"
    chown "$USER:$GROUP" "$DATABASE_PATH"
    chmod 664 "$DATABASE_PATH"
    echo "✅ Database inizializzato da template"
else
    echo "Database template non trovato, creazione database pulito..."
    if [ -f "$INSTALL_PATH/scripts/create_clean_database.py" ]; then
        python3 "$INSTALL_PATH/scripts/create_clean_database.py" "$DATABASE_PATH"
        chown "$USER:$GROUP" "$DATABASE_PATH"
        chmod 664 "$DATABASE_PATH"
        echo "✅ Database creato ex-novo"
    else
        echo "⚠️  Script creazione database non trovato, il database sarà creato al primo avvio"
    fi
fi

echo "🚀 Post-installazione..."

# Esecuzione script di post-installazione se presente
if [ -f "$INSTALL_PATH/scripts/post_install.sh" ]; then
    echo "Esecuzione script post-installazione..."
    bash "$INSTALL_PATH/scripts/post_install.sh" || echo "⚠️  Script post-installazione completato con avvisi"
fi

echo "🎯 Avvio sistema..."

# Abilitazione e avvio servizio
systemctl enable access-control.service
systemctl start access-control.service

# Attesa avvio servizio
sleep 5

# Verifica stato
echo ""
echo "=== Verifica Installazione ==="
if systemctl is-active --quiet access-control.service; then
    echo "✅ Servizio attivo e funzionante"
    echo "🌐 Il sistema è accessibile su: http://localhost:5000"
else
    echo "❌ Servizio non attivo"
    echo "📋 Stato servizio:"
    systemctl status access-control.service --no-pager
fi

echo ""
echo "📊 Riepilogo installazione:"
echo "  📁 Directory: $INSTALL_PATH"
echo "  👤 Utente: $USER"
echo "  🌐 URL: http://localhost:5000"
echo "  📝 Log: /var/log/access_control/"
echo "  🔧 Gestione: systemctl {start|stop|restart|status} access-control"
echo ""

# Test finale di connessione
echo "🧪 Test finale del sistema..."
if command -v curl &> /dev/null; then
    if curl -s http://localhost:5000 &> /dev/null; then
        echo "✅ Sistema risponde correttamente"
    else
        echo "⚠️  Sistema non risponde su porta 5000"
        echo "   Verificare log: journalctl -u access-control.service"
    fi
else
    echo "⚠️  curl non disponibile per test finale"
fi

echo ""
echo "🎉 Installazione completata!"
echo ""
echo "📖 Comandi utili:"
echo "  - Restart sistema: sudo systemctl restart access-control"
echo "  - Visualizza log: sudo journalctl -u access-control -f"
echo "  - Backup manuale: sudo -u $USER $INSTALL_PATH/scripts/backup.sh"
echo "  - Stato sistema: sudo -u $USER $INSTALL_PATH/scripts/check_system.sh"
echo ""
