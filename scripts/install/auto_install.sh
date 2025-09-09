#!/bin/bash
# ============================================================================
# Auto Install Wrapper - Sistema Controllo Accessi RAEE
# Version: 1.0.0
# 
# Questo script permette installazioni automatiche non presidiate
# su multiple macchine usando credenziali salvate in modo sicuro
# ============================================================================

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# File di configurazione credenziali (da creare separatamente)
CREDS_FILE="/root/.git_credentials_raee"

# Funzioni utility
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Header
clear
echo "============================================================================"
echo "         AUTO INSTALLER - SISTEMA CONTROLLO ACCESSI RAEE"
echo "============================================================================"
echo ""

# Verifica se eseguito come root
if [ "$EUID" -ne 0 ]; then 
    log_error "Questo script deve essere eseguito come root"
fi

# Metodo 1: Leggi credenziali da file sicuro
if [ -f "$CREDS_FILE" ]; then
    log_info "Caricamento credenziali da file sicuro..."
    source "$CREDS_FILE"
    if [ -z "$GIT_USERNAME" ] || [ -z "$GIT_PASSWORD" ]; then
        log_error "File credenziali incompleto. Richiesti GIT_USERNAME e GIT_PASSWORD"
    fi
    log_success "Credenziali caricate"

# Metodo 2: Usa variabili d'ambiente se già settate
elif [ -n "$GIT_USERNAME" ] && [ -n "$GIT_PASSWORD" ]; then
    log_info "Uso credenziali da variabili d'ambiente"

# Metodo 3: Richiedi credenziali e salvale per usi futuri
else
    echo "Nessuna credenziale trovata. Configurazione iniziale richiesta."
    echo ""
    read -p "GitHub Username: " GIT_USERNAME
    read -s -p "GitHub Password/Token: " GIT_PASSWORD
    echo ""
    echo ""
    
    # Chiedi se salvare le credenziali
    read -p "Salvare le credenziali per installazioni future? (y/n): " SAVE_CREDS
    if [ "$SAVE_CREDS" = "y" ] || [ "$SAVE_CREDS" = "Y" ]; then
        cat > "$CREDS_FILE" << EOF
# Credenziali Git per Sistema Controllo Accessi RAEE
# ATTENZIONE: File contiene credenziali sensibili
export GIT_USERNAME='$GIT_USERNAME'
export GIT_PASSWORD='$GIT_PASSWORD'
EOF
        chmod 600 "$CREDS_FILE"
        log_success "Credenziali salvate in $CREDS_FILE (permessi 600)"
    fi
fi

# Determina ambiente (default: development)
INSTALL_ENV="${1:-development}"

# Opzioni aggiuntive
GITHUB_BRANCH="${2:-main}"
AUTO_START="${3:-yes}"

log_info "Configurazione installazione:"
log_info "  - Ambiente: $INSTALL_ENV"
log_info "  - Branch: $GITHUB_BRANCH"
log_info "  - Auto-start servizi: $AUTO_START"
log_info "  - Username: $GIT_USERNAME"
echo ""

# Download script di installazione principale se non esiste
if [ ! -f "/tmp/install_system.sh" ]; then
    log_info "Download script installazione..."
    
    # Crea script temporaneo per download
    cat > /tmp/download_installer.sh << 'SCRIPT'
#!/bin/bash
# Scarica l'installer dal repository
REPO_URL="https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/wlkr42/sistema-controllo-accessi.git"
TEMP_DIR="/tmp/raee_installer_$$"

# Clone solo la directory scripts/install
git clone --depth 1 --filter=blob:none --sparse "$REPO_URL" "$TEMP_DIR" 2>/dev/null
cd "$TEMP_DIR"
git sparse-checkout set scripts/install

# Copia installer
cp scripts/install/install_system.sh /tmp/
chmod +x /tmp/install_system.sh

# Cleanup
cd /
rm -rf "$TEMP_DIR"
SCRIPT

    # Esegui download con credenziali
    export GIT_USERNAME GIT_PASSWORD
    bash /tmp/download_installer.sh
    rm /tmp/download_installer.sh
    
    if [ ! -f "/tmp/install_system.sh" ]; then
        log_error "Impossibile scaricare script di installazione"
    fi
    log_success "Script installazione scaricato"
fi

# Esporta variabili per lo script principale
export GIT_USERNAME
export GIT_PASSWORD
export GITHUB_BRANCH
export INSTALL_ENV

# Esegui installazione principale
log_info "Avvio installazione sistema..."
echo ""
echo "============================================================================"

# Esegui con le variabili d'ambiente
bash /tmp/install_system.sh "$INSTALL_ENV"

# Verifica successo installazione
if [ $? -eq 0 ]; then
    log_success "Installazione completata con successo!"
    
    # Auto-start servizi se richiesto
    if [ "$AUTO_START" = "yes" ]; then
        log_info "Avvio servizi..."
        systemctl start access-control-web.service
        systemctl start access-monitor.service
        
        # Verifica stato
        sleep 5
        if systemctl is-active --quiet access-control-web.service; then
            log_success "Servizio web attivo"
        else
            log_error "Servizio web non attivo"
        fi
    fi
    
    # Mostra info accesso
    echo ""
    echo "============================================================================"
    echo "ACCESSO SISTEMA:"
    echo "URL: http://$(hostname -I | awk '{print $1}'):5000"
    echo "Username: admin"
    echo "Password: admin123"
    echo "============================================================================"
else
    log_error "Installazione fallita. Controllare i log."
fi

# Cleanup
rm -f /tmp/install_system.sh

log_success "Processo completato!"