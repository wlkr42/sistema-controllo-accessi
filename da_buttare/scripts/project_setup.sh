#!/bin/bash
# File: /opt/access_control/scripts/setup_project.sh
# Setup completo progetto Sistema Controllo Accessi

set -e  # Exit on any error

echo "🚀 SETUP SISTEMA CONTROLLO ACCESSI"
echo "================================="

# Variabili configurazione
PROJECT_DIR="/opt/access_control"
PROJECT_USER="access-control"
PYTHON_VERSION="3.10"

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verifica permessi root
if [[ $EUID -ne 0 ]]; then
   print_error "Questo script deve essere eseguito come root (sudo)"
   exit 1
fi

print_status "Creazione struttura progetto..."

# Crea directory progetto
mkdir -p $PROJECT_DIR/{src,config,logs,scripts,docs,tests,backups,venv}
mkdir -p $PROJECT_DIR/src/{core,hardware,database,api,utils}
mkdir -p $PROJECT_DIR/config/{environments,templates}
mkdir -p $PROJECT_DIR/tests/{unit,integration,hardware}

print_success "Directory create"

# Crea utente sistema dedicato
if ! id "$PROJECT_USER" &>/dev/null; then
    print_status "Creazione utente sistema $PROJECT_USER..."
    useradd -r -m -s /bin/bash -d $PROJECT_DIR $PROJECT_USER
    usermod -a -G dialout,plugdev $PROJECT_USER
    print_success "Utente $PROJECT_USER creato"
else
    print_warning "Utente $PROJECT_USER già esistente"
fi

# Imposta permessi
chown -R $PROJECT_USER:$PROJECT_USER $PROJECT_DIR
chmod -R 755 $PROJECT_DIR
chmod -R 644 $PROJECT_DIR/config
chmod 750 $PROJECT_DIR/scripts
chmod 700 $PROJECT_DIR/logs

print_success "Permessi impostati"

# Crea virtual environment Python
print_status "Creazione virtual environment Python..."
sudo -u $PROJECT_USER python3 -m venv $PROJECT_DIR/venv

print_success "Virtual environment creato"

# Attiva venv e installa pip base
sudo -u $PROJECT_USER bash -c "
source $PROJECT_DIR/venv/bin/activate
pip install --upgrade pip setuptools wheel
"

print_success "Virtual environment configurato"

print_status "Configurazione sistemd..."

# Crea servizio systemd
cat > /etc/systemd/system/access-control.service << EOF
[Unit]
Description=Sistema Controllo Accessi con Tessera Sanitaria
Documentation=file://$PROJECT_DIR/docs/documentazione_tecnica.md
After=network.target pcscd.service
Wants=network.target
Requires=pcscd.service

[Service]
Type=simple
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=$PROJECT_DIR/src
ExecStart=$PROJECT_DIR/venv/bin/python -m src.main
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=$PROJECT_DIR /var/log
CapabilityBoundingSet=CAP_DAC_OVERRIDE
AmbientCapabilities=CAP_DAC_OVERRIDE

[Install]
WantedBy=multi-user.target
EOF

print_success "Servizio systemd creato"

# Ricarica systemd
systemctl daemon-reload

print_status "Configurazione logrotate..."

# Configura logrotate
cat > /etc/logrotate.d/access-control << EOF
$PROJECT_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $PROJECT_USER $PROJECT_USER
    postrotate
        systemctl reload access-control.service > /dev/null 2>&1 || true
    endscript
}
EOF

print_success "Logrotate configurato"

print_status "Configurazione backup automatico..."

# Script backup automatico
cat > $PROJECT_DIR/scripts/backup.sh << 'EOF'
#!/bin/bash
# File: /opt/access_control/scripts/backup.sh
# Backup automatico database e configurazioni

BACKUP_DIR="/opt/access_control/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE="/opt/access_control/src/access.db"
CONFIG_DIR="/opt/access_control/config"

# Crea backup database se esistente
if [ -f "$DB_FILE" ]; then
    sqlite3 "$DB_FILE" ".backup '$BACKUP_DIR/access_db_$DATE.db'"
    echo "Database backup: access_db_$DATE.db"
fi

# Backup configurazioni
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" -C "$CONFIG_DIR" .
echo "Config backup: config_$DATE.tar.gz"

# Rimuovi backup vecchi (>30 giorni)
find "$BACKUP_DIR" -name "*.db" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "Backup completato: $DATE"
EOF

chmod +x $PROJECT_DIR/scripts/backup.sh
chown $PROJECT_USER:$PROJECT_USER $PROJECT_DIR/scripts/backup.sh

# Crontab per backup
(crontab -u $PROJECT_USER -l 2>/dev/null; echo "0 2 * * * $PROJECT_DIR/scripts/backup.sh >> $PROJECT_DIR/logs/backup.log 2>&1") | crontab -u $PROJECT_USER -

print_success "Backup automatico configurato"

print_status "Setup completato!"
echo ""
echo "📁 Directory progetto: $PROJECT_DIR"
echo "👤 Utente sistema: $PROJECT_USER"
echo "🐍 Virtual environment: $PROJECT_DIR/venv"
echo "📋 Servizio: access-control.service"
echo ""
echo "🔧 Prossimi passi:"
echo "1. Configurare requirements.txt"
echo "2. Installare dipendenze Python"
echo "3. Configurare database"
echo "4. Testare componenti hardware"
echo ""
echo "✅ Setup base completato!"
