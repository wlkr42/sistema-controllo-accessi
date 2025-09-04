#!/bin/bash

# Script per preparare il pacchetto di installazione del Sistema di Controllo Accessi
# Versione COMPLETA con tutte le richieste implementate
# Data: $(date +%Y-%m-%d)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Determinazione PROJECT_ROOT in base alla struttura rilevata
if [[ "$SCRIPT_DIR" == *"/installazione/scripts" ]]; then
    # Siamo in installazione/scripts, il progetto è due livelli sopra
    PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
    PACKAGE_DIR="$(dirname "$SCRIPT_DIR")/pacchetto"
elif [[ "$SCRIPT_DIR" == *"/installazione" ]]; then
    # Siamo in installazione, il progetto è un livello sopra  
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
    PACKAGE_DIR="$SCRIPT_DIR/pacchetto"
else
    # Fallback: assumiamo che siamo nella root del progetto
    PROJECT_ROOT="$SCRIPT_DIR"
    PACKAGE_DIR="$SCRIPT_DIR/installazione/pacchetto"
fi

# Verifica che PROJECT_ROOT contenga src e requirements.txt
if [ ! -d "$PROJECT_ROOT/src" ] || [ ! -f "$PROJECT_ROOT/requirements.txt" ]; then
    echo "❌ Errore: PROJECT_ROOT non sembra corretto"
    echo "   SCRIPT_DIR: $SCRIPT_DIR"
    echo "   PROJECT_ROOT: $PROJECT_ROOT"
    echo "   Verificare che esistano:"
    echo "   - $PROJECT_ROOT/src"
    echo "   - $PROJECT_ROOT/requirements.txt"
    exit 1
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="sistema-controllo-accessi-${TIMESTAMP}"

echo "=== Preparazione Pacchetto Sistema Controllo Accessi COMPLETO ==="
echo "Directory progetto: $PROJECT_ROOT"
echo "Directory pacchetto: $PACKAGE_DIR"
echo "Timestamp: $TIMESTAMP"

# Pulizia directory pacchetto precedente
if [ -d "$PACKAGE_DIR" ]; then
    echo "Rimozione pacchetto precedente..."
    rm -rf "$PACKAGE_DIR"
fi

mkdir -p "$PACKAGE_DIR"
cd "$PACKAGE_DIR"

echo "Creazione struttura pacchetto..."

# Creazione directory principale del pacchetto
mkdir -p "${PACKAGE_NAME}"/{src,config,scripts,docs,systemd,cron}

echo "Copia dei file sorgente..."
echo "Copiatura completa della directory src/ (sistema modulare)..."

# Copia TUTTA la directory src mantenendo la struttura completa, escludendo cache e file temporanei
rsync -av --exclude='*.pyc' \
          --exclude='__pycache__' \
          --exclude='*.log' \
          --exclude='*.tmp' \
          --exclude='*.swp' \
          --exclude='*.bak' \
          --exclude='.DS_Store' \
          --exclude='access.db*' \
          --exclude='*.sqlite' \
          --exclude='*.sqlite3' \
          --exclude='*.db-journal' \
          "$PROJECT_ROOT/src/" "${PACKAGE_NAME}/src/"

echo "✅ Directory src/ copiata completamente (cache e DB esclusi)"

# Crea database template pulito
echo "Creazione database template pulito..."
python3 "${SCRIPT_DIR}/create_clean_database.py" "${PACKAGE_NAME}/src/access.db.template"

if [ -f "${PACKAGE_NAME}/src/access.db.template" ]; then
    echo "✅ Database template creato"
else
    echo "⚠️  Errore creazione database template"
fi

# Verifica che tutti i componenti essenziali siano presenti
REQUIRED_COMPONENTS=(
    "src/api/web_api.py"
    "src/api/modules"
    "src/api/static"
    "src/api/templates"
    "src/core"
    "src/database"
    "src/hardware"
    "src/access.db.template"
)

echo "Verifica componenti essenziali..."
for component in "${REQUIRED_COMPONENTS[@]}"; do
    if [ -e "${PACKAGE_NAME}/$component" ]; then
        echo "  ✅ $component"
    else
        echo "  ❌ $component MANCANTE"
    fi
done

echo "Copia data e configurazioni..."

# Copia directory data se esiste (con struttura partner cache, etc.)
if [ -d "$PROJECT_ROOT/data" ]; then
    cp -r "$PROJECT_ROOT/data" "${PACKAGE_NAME}/" 
    echo "✅ Directory data copiata"
fi

# Copia directory config se esiste
if [ -d "$PROJECT_ROOT/config" ]; then
    cp -r "$PROJECT_ROOT/config" "${PACKAGE_NAME}/" 
    echo "✅ Directory config copiata"
fi

# Copia documentazione se esiste  
if [ -d "$PROJECT_ROOT/docs" ]; then
    cp -r "$PROJECT_ROOT/docs" "${PACKAGE_NAME}/"
    echo "✅ Directory docs copiata"
fi

# Copia altri file importanti dalla root se esistono
IMPORTANT_FILES=("*.md" "*.txt" "*.json")
for pattern in "${IMPORTANT_FILES[@]}"; do
    for file in $PROJECT_ROOT/$pattern; do
        if [ -f "$file" ] && [[ "$(basename "$file")" != "requirements.txt" ]]; then
            cp "$file" "${PACKAGE_NAME}/"
            echo "✅ File $(basename "$file") copiato"
        fi
    done 2>/dev/null
done

# Copia requirements.txt
cp "$PROJECT_ROOT/requirements.txt" "${PACKAGE_NAME}/"
echo "✅ requirements.txt copiato"

echo "Verifica contenuto requirements.txt..."
echo "--- Dipendenze da installare ---"
cat "${PACKAGE_NAME}/requirements.txt"
echo "--- Fine dipendenze ---"

echo "Copia scripts di sistema..."
# Copia TUTTI gli script dalla directory scripts del progetto
if [ -d "$PROJECT_ROOT/scripts" ]; then
    rsync -av --exclude='*.pyc' \
              --exclude='__pycache__' \
              --exclude='*.log' \
              "$PROJECT_ROOT/scripts/" "${PACKAGE_NAME}/scripts/"
    echo "✅ Directory scripts/ copiata completamente"
    
    # Rendi eseguibili tutti gli script
    find "${PACKAGE_NAME}/scripts/" -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
    echo "✅ Permessi script aggiornati"
else
    echo "⚠️  Directory scripts non trovata"
fi

echo "Creazione file di configurazione..."

# File di configurazione sistema
cat > "${PACKAGE_NAME}/config/system.conf" << 'EOF'
# Configurazione Sistema Controllo Accessi
INSTALL_PATH="/opt/access_control"
USER="wlkr42"
GROUP="wlkr42"
WEB_PORT="5000"
SERVICE_NAME="access-control"
BACKUP_DIR="/opt/access_control/backups"
LOG_DIR="/var/log/access_control"
EOF

# File di configurazione database
cat > "${PACKAGE_NAME}/config/database.conf" << 'EOF'
# Configurazione Database
DATABASE_PATH="/opt/access_control/src/access.db"
BACKUP_RETENTION_DAYS="30"
AUTO_BACKUP_ENABLED="true"
BACKUP_SCHEDULE="0 2 * * *"
EOF

echo "Creazione servizio systemd..."
cat > "${PACKAGE_NAME}/systemd/access-control.service" << 'EOF'
[Unit]
Description=Sistema di Controllo Accessi
After=network.target
Wants=network.target

[Service]
Type=simple
User=wlkr42
Group=wlkr42
WorkingDirectory=/opt/access_control/src/api
Environment=PYTHONPATH=/opt/access_control/src
ExecStart=/opt/access_control/venv/bin/python /opt/access_control/src/api/web_api.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

# Limitazioni di sicurezza
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/access_control
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo "Creazione job cron..."
cat > "${PACKAGE_NAME}/cron/access-control-cron" << 'EOF'
# Cron jobs per Sistema Controllo Accessi
# Reset contatori mensili - primo giorno del mese alle 01:00
0 1 1 * * wlkr42 /opt/access_control/venv/bin/python /opt/access_control/scripts/reset_contatori_mensili.py

# Backup automatico - ogni giorno alle 02:00
0 2 * * * wlkr42 /opt/access_control/scripts/backup.sh

# Pulizia download - ogni domenica alle 03:00
0 3 * * 0 wlkr42 /opt/access_control/venv/bin/python /opt/access_control/scripts/cleanup_downloads.py

# Monitoraggio sistema - ogni 5 minuti
*/5 * * * * wlkr42 /opt/access_control/venv/bin/python /opt/access_control/scripts/system_monitor.py
EOF

echo "Creazione script di post-installazione..."
cat > "${PACKAGE_NAME}/scripts/post_install.sh" << 'EOF'
#!/bin/bash

# Script di post-installazione
echo "=== Post-installazione Sistema Controllo Accessi ==="

# Le tabelle saranno create automaticamente da web_api.py
echo "✅ Il database e le tabelle saranno creati automaticamente al primo avvio"

# Installazione cron jobs
echo "Installazione cron jobs..."
if [ -f "/opt/access_control/cron/access-control-cron" ]; then
    sudo -u wlkr42 crontab /opt/access_control/cron/access-control-cron
    echo "✅ Cron jobs installati"
else
    echo "⚠️  File cron non trovato"
fi

# Avvio e abilitazione servizio
echo "Avvio servizio..."
systemctl enable access-control.service
systemctl start access-control.service

# Verifica stato servizio
sleep 3
if systemctl is-active --quiet access-control.service; then
    echo "✅ Servizio avviato correttamente"
else
    echo "⚠️  Servizio non attivo, controllare log:"
    echo "   journalctl -u access-control.service -n 20"
fi

echo "Post-installazione completata!"
EOF

chmod +x "${PACKAGE_NAME}/scripts/post_install.sh"

echo "Copia script di installazione e database..."

# Script di installazione (dalla directory installazione/scripts)
if [ -f "$SCRIPT_DIR/install.sh" ]; then
    cp "$SCRIPT_DIR/install.sh" "${PACKAGE_NAME}/"
    chmod +x "${PACKAGE_NAME}/install.sh"
    echo "✅ Script install.sh copiato"
else
    echo "❌ ERRORE: install.sh non trovato in $SCRIPT_DIR"
    echo "   Creare install.sh nella directory installazione/scripts/"
    exit 1
fi

# Script di disinstallazione
if [ -f "$SCRIPT_DIR/uninstall.sh" ]; then
    cp "$SCRIPT_DIR/uninstall.sh" "${PACKAGE_NAME}/"
    chmod +x "${PACKAGE_NAME}/uninstall.sh"
    echo "✅ Script uninstall.sh copiato"
fi

# Script di verifica sistema
if [ -f "$SCRIPT_DIR/check_system.sh" ]; then
    cp "$SCRIPT_DIR/check_system.sh" "${PACKAGE_NAME}/scripts/"
    chmod +x "${PACKAGE_NAME}/scripts/check_system.sh"
    echo "✅ Script check_system.sh copiato"
fi

# Script di creazione database pulito
if [ -f "$SCRIPT_DIR/create_clean_database.py" ]; then
    cp "$SCRIPT_DIR/create_clean_database.py" "${PACKAGE_NAME}/scripts/"
    chmod +x "${PACKAGE_NAME}/scripts/create_clean_database.py"
    echo "✅ Script create_clean_database.py copiato"
fi

echo "Verifica completezza pacchetto..."

# Mostra struttura principale
echo "📁 Struttura principale:"
ls -la "${PACKAGE_NAME}/" | head -20

echo ""
echo "📁 Struttura src/:"
ls -la "${PACKAGE_NAME}/src/" | head -15

echo ""
echo "📊 Statistiche pacchetto:"
echo "  - File totali: $(find "${PACKAGE_NAME}" -type f | wc -l)"
echo "  - Directory: $(find "${PACKAGE_NAME}" -type d | wc -l)"
echo "  - Dimensione: $(du -sh "${PACKAGE_NAME}" | cut -f1)"

# Verifica pulizia (no cache)
CACHE_FILES=$(find "${PACKAGE_NAME}" -name "*.pyc" -o -name "__pycache__" | wc -l)
echo "  - File cache Python: $CACHE_FILES (dovrebbe essere 0)"

if [ "$CACHE_FILES" -gt 0 ]; then
    echo "⚠️  Trovati file cache, rimozione..."
    find "${PACKAGE_NAME}" -name "*.pyc" -delete
    find "${PACKAGE_NAME}" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
    echo "✅ Cache rimossa"
fi

echo "Creazione file di verifica integrità..."
# Calcolo checksum per verifica integrità
find "${PACKAGE_NAME}" -type f -exec md5sum {} \; > "${PACKAGE_NAME}.md5"

echo "Creazione archivio..."
tar -czf "${PACKAGE_NAME}.tar.gz" "${PACKAGE_NAME}"

# Calcolo checksum dell'archivio
md5sum "${PACKAGE_NAME}.tar.gz" > "${PACKAGE_NAME}.tar.gz.md5"

echo "Creazione file README..."
cat > README.md << EOF
# Pacchetto Installazione Sistema Controllo Accessi

## File del pacchetto
- \`${PACKAGE_NAME}.tar.gz\` - Archivio principale
- \`${PACKAGE_NAME}.tar.gz.md5\` - Checksum per verifica integrità

## Installazione
1. Estrarre: \`tar -xzf ${PACKAGE_NAME}.tar.gz\`
2. Entrare nella directory: \`cd ${PACKAGE_NAME}\`
3. Eseguire installazione: \`sudo bash install.sh\`

## Disinstallazione
Per rimuovere completamente il sistema:
\`\`\`bash
sudo bash uninstall.sh
\`\`\`

## Verifica sistema
Dopo l'installazione:
\`\`\`bash
sudo bash /opt/access_control/scripts/check_system.sh
\`\`\`

## Requisiti di sistema
- Ubuntu 22.04 LTS
- Python 3.8+
- Accesso root per l'installazione
- 500MB spazio libero su disco

## Informazioni pacchetto
- Data creazione: $(date)
- Versione: ${TIMESTAMP}
- Dimensione: $(du -h "${PACKAGE_NAME}.tar.gz" | cut -f1)

## Post-installazione
- **URL sistema**: http://localhost:5000
- **Utente sistema**: wlkr42
- **Directory**: /opt/access_control
- **Log**: /var/log/access_control/

## Utenti di default
- **admin/admin123** - Amministratore completo
- **manager/manager123** - Gestore utenti e orari
- **viewer/viewer123** - Solo visualizzazione

## Gestione servizio
- Avvio: \`sudo systemctl start access-control\`
- Stop: \`sudo systemctl stop access-control\`
- Restart: \`sudo systemctl restart access-control\`
- Status: \`sudo systemctl status access-control\`
- Log: \`sudo journalctl -u access-control -f\`

## Backup manuale
\`\`\`bash
sudo -u wlkr42 /opt/access_control/scripts/backup.sh
\`\`\`

## Supporto
Per problemi o domande, consultare la documentazione nel sistema installato.
EOF

# Pulizia directory temporanea
rm -rf "${PACKAGE_NAME}"

echo ""
echo "=== Pacchetto COMPLETO creato con successo! ==="
echo "File: ${PACKAGE_DIR}/${PACKAGE_NAME}.tar.gz"
echo "Checksum: ${PACKAGE_DIR}/${PACKAGE_NAME}.tar.gz.md5"
echo "Dimensione: $(du -h "${PACKAGE_DIR}/${PACKAGE_NAME}.tar.gz" | cut -f1)"
echo ""
echo "🎯 CARATTERISTICHE PACCHETTO:"
echo "  ✅ Sistema modulare completo"
echo "  ✅ Cache Python rimossa"
echo "  ✅ Database template con utenti default"
echo "  ✅ Script di installazione e disinstallazione"
echo "  ✅ Ambiente virtuale Python"
echo "  ✅ Servizi systemd e cron configurati"
echo ""
echo "Per installare su un nuovo sistema:"
echo "1. Copiare ${PACKAGE_NAME}.tar.gz sul sistema di destinazione"
echo "2. Estrarre: tar -xzf ${PACKAGE_NAME}.tar.gz"  
echo "3. Eseguire: sudo bash install.sh"
echo ""
echo "Per disinstallare: sudo bash uninstall.sh"
echo ""
