#!/bin/bash
#
# Setup Services per Sistema Controllo Accessi
# Configura systemd services, cron jobs e logrotate
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# PROJECT_ROOT è SEMPRE /opt/access_control su qualsiasi sistema
PROJECT_ROOT="/opt/access_control"
FLASK_ENV="${1:-development}"

# Colori output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Installa servizio systemd principale
install_main_service() {
    log_info "Installazione servizio systemd principale..."
    
    # Crea file service
    cat > /tmp/access-control-web.service << EOF
[Unit]
Description=Access Control Web Service - Enterprise 24/7/365
After=network.target network-online.target
Wants=network-online.target
Documentation=file://$PROJECT_ROOT/docs/DOCUMENTAZIONE_SISTEMA.md

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_ROOT
Environment="PYTHONPATH=$PROJECT_ROOT"
Environment="PYTHONUNBUFFERED=1"
Environment="FLASK_APP=src.api.web_api:app"
Environment="FLASK_ENV=$FLASK_ENV"

# Pre-check database
ExecStartPre=/bin/bash -c 'if [ ! -f "$PROJECT_ROOT/data/access_control.db" ]; then echo "Database not found!"; exit 1; fi'

# Kill processo su porta se esiste
ExecStartPre=/bin/bash -c 'fuser -k 5000/tcp || true'
ExecStartPre=/bin/sleep 2

# Start applicazione 
# In sviluppo usa Flask development server, in produzione usa Gunicorn
# Determinato dalla variabile d'ambiente FLASK_ENV
ExecStart=/bin/bash -c 'if [ "$FLASK_ENV" = "production" ] && [ -f "$PROJECT_ROOT/venv/bin/gunicorn" ]; then \
    exec $PROJECT_ROOT/venv/bin/gunicorn \
        --workers 4 \
        --worker-class gevent \
        --bind 0.0.0.0:5000 \
        --timeout 120 \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        src.api.web_api:app; \
else \
    exec /usr/bin/python3 $PROJECT_ROOT/main.py; \
fi'

# Restart policy
Restart=always
RestartSec=10
StartLimitIntervalSec=0
StartLimitBurst=0

# Process management
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096
Nice=-10

# Security
PrivateTmp=yes
NoNewPrivileges=yes

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=access-control

[Install]
WantedBy=multi-user.target
EOF

    sudo mv /tmp/access-control-web.service /etc/systemd/system/
    sudo systemctl daemon-reload
    log_info "✓ Servizio systemd installato"
}

# Installa servizio monitor
install_monitor_service() {
    log_info "Installazione servizio monitor 24/7..."
    
    cat > /tmp/access-monitor.service << EOF
[Unit]
Description=Access Control Monitor Service - 24/7 Watchdog
After=access-control-web.service
Requires=access-control-web.service
Documentation=file://$PROJECT_ROOT/docs/DOCUMENTAZIONE_SISTEMA.md

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_ROOT
ExecStart=/bin/bash $PROJECT_ROOT/scripts/system/monitor_24_7.sh
Restart=always
RestartSec=60
StandardOutput=journal
StandardError=journal
SyslogIdentifier=access-monitor

[Install]
WantedBy=multi-user.target
EOF

    sudo mv /tmp/access-monitor.service /etc/systemd/system/
    sudo systemctl daemon-reload
    log_info "✓ Servizio monitor installato"
}

# Configura logrotate
setup_logrotate() {
    log_info "Configurazione logrotate..."
    
    cat > /tmp/access-control << EOF
# Logrotate configuration for Access Control System
$PROJECT_ROOT/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
    sharedscripts
    postrotate
        # Invia segnale per riaprire log files
        systemctl reload access-control-web 2>/dev/null || true
    endscript
}

# Log speciali con retention più lunga
$PROJECT_ROOT/logs/security_audit.log
$PROJECT_ROOT/logs/access_audit.log {
    weekly
    rotate 52
    compress
    delaycompress
    missingok
    notifempty
    create 0600 root root
}

# Backup logs
$PROJECT_ROOT/logs/backup.log
$PROJECT_ROOT/logs/auto_backup.log {
    monthly
    rotate 12
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
EOF

    sudo mv /tmp/access-control /etc/logrotate.d/
    log_info "✓ Logrotate configurato"
}

# Setup cron jobs
setup_cron_jobs() {
    log_info "Configurazione cron jobs..."
    
    # Backup automatici
    CRON_JOBS="
# Access Control System - Backup Automatici
00 02 * * * cd $PROJECT_ROOT && /usr/bin/python3 scripts/auto_backup.py database >> logs/auto_backup.log 2>&1
00 03 * * 0 cd $PROJECT_ROOT && /usr/bin/python3 scripts/auto_backup.py complete >> logs/auto_backup.log 2>&1
00 04 1 * * cd $PROJECT_ROOT && /usr/bin/python3 scripts/auto_backup.py complete >> logs/auto_backup.log 2>&1

# Pulizia log vecchi
00 05 * * * find $PROJECT_ROOT/logs -name '*.log.*' -mtime +90 -delete

# Health check giornaliero con report
30 06 * * * curl -s http://localhost:5000/api/health | python3 -m json.tool >> $PROJECT_ROOT/logs/health_check.log 2>&1
"
    
    # Aggiungi a crontab root
    (crontab -l 2>/dev/null | grep -v "Access Control System"; echo "$CRON_JOBS") | crontab -
    log_info "✓ Cron jobs configurati"
}

# Abilita e avvia servizi
enable_services() {
    log_info "Abilitazione servizi..."
    
    # Abilita servizi
    sudo systemctl enable access-control-web.service
    sudo systemctl enable access-monitor.service
    log_info "✓ Servizi abilitati per avvio automatico"
    
    # Avvia servizi
    log_info "Avvio servizi..."
    sudo systemctl start access-control-web.service
    sleep 5
    sudo systemctl start access-monitor.service
    
    # Verifica stato
    if sudo systemctl is-active --quiet access-control-web.service; then
        log_info "✓ Servizio web attivo"
    else
        log_warn "⚠ Servizio web non attivo - verificare con: systemctl status access-control-web"
    fi
    
    if sudo systemctl is-active --quiet access-monitor.service; then
        log_info "✓ Servizio monitor attivo"
    else
        log_warn "⚠ Servizio monitor non attivo - verificare con: systemctl status access-monitor"
    fi
}

# Crea script di gestione
create_management_scripts() {
    log_info "Creazione script di gestione..."
    
    # Script start
    cat > "$PROJECT_ROOT/start.sh" << 'EOF'
#!/bin/bash
echo "Avvio Sistema Controllo Accessi..."
sudo systemctl start access-control-web.service
sudo systemctl start access-monitor.service
echo "Sistema avviato. Verificare con: sudo systemctl status access-control-web"
EOF
    
    # Script stop
    cat > "$PROJECT_ROOT/stop.sh" << 'EOF'
#!/bin/bash
echo "Arresto Sistema Controllo Accessi..."
sudo systemctl stop access-monitor.service
sudo systemctl stop access-control-web.service
echo "Sistema arrestato."
EOF
    
    # Script restart
    cat > "$PROJECT_ROOT/restart.sh" << 'EOF'
#!/bin/bash
echo "Riavvio Sistema Controllo Accessi..."
sudo systemctl restart access-control-web.service
sleep 3
sudo systemctl restart access-monitor.service
echo "Sistema riavviato. Verificare con: sudo systemctl status access-control-web"
EOF
    
    # Script status
    cat > "$PROJECT_ROOT/status.sh" << 'EOF'
#!/bin/bash
echo "=== Stato Sistema Controllo Accessi ==="
echo ""
echo "Servizio Web:"
sudo systemctl status access-control-web.service --no-pager | head -n 10
echo ""
echo "Servizio Monitor:"
sudo systemctl status access-monitor.service --no-pager | head -n 10
echo ""
echo "Health Check:"
curl -s http://localhost:5000/api/health | python3 -m json.tool 2>/dev/null || echo "Sistema non raggiungibile"
EOF
    
    # Rendi eseguibili
    chmod +x "$PROJECT_ROOT"/*.sh
    log_info "✓ Script di gestione creati (start.sh, stop.sh, restart.sh, status.sh)"
}

# Main
main() {
    log_info "=== Setup Servizi Sistema ==="
    
    # Verifica root
    if [ "$EUID" -ne 0 ]; then 
        log_error "Questo script deve essere eseguito come root"
        exit 1
    fi
    
    # Installa servizi
    install_main_service
    install_monitor_service
    
    # Configura log
    setup_logrotate
    
    # Setup cron
    setup_cron_jobs
    
    # Crea script gestione
    create_management_scripts
    
    # Abilita e avvia
    enable_services
    
    log_info ""
    log_info "✅ Setup servizi completato!"
    log_info ""
    log_info "Comandi utili:"
    log_info "  ./start.sh    - Avvia il sistema"
    log_info "  ./stop.sh     - Ferma il sistema"
    log_info "  ./restart.sh  - Riavvia il sistema"
    log_info "  ./status.sh   - Verifica stato sistema"
    log_info ""
    log_info "Servizi systemd:"
    log_info "  systemctl status access-control-web  - Stato servizio web"
    log_info "  systemctl status access-monitor      - Stato monitor 24/7"
    log_info "  journalctl -fu access-control-web    - Log real-time"
    log_info ""
    log_info "Sistema disponibile su: http://localhost:5000"
    
    return 0
}

# Esegui main
main "$@"