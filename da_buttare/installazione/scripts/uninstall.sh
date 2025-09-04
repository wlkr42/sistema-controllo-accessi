#!/bin/bash

# Script di disinstallazione Sistema Controllo Accessi
# Rimuove completamente il sistema dal server

set -e

# Verifica privilegi root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Questo script deve essere eseguito come root (sudo)"
   exit 1
fi

# Configurazione
INSTALL_PATH="/opt/access_control"
USER="wlkr42"
SERVICE_NAME="access-control"

echo "=== Disinstallazione Sistema Controllo Accessi ==="
echo "⚠️  ATTENZIONE: Questa operazione rimuoverà completamente il sistema!"
echo "📁 Directory: $INSTALL_PATH"
echo "👤 Utente: $USER"
echo "🔧 Servizio: $SERVICE_NAME"
echo ""

# Chiedi conferma
read -p "Continuare con la disinstallazione? (digita 'RIMUOVI' per confermare): " confirm
if [ "$confirm" != "RIMUOVI" ]; then
    echo "❌ Disinstallazione annullata"
    exit 1
fi

echo "🗑️  Inizio disinstallazione..."

# Funzione per logging
log_action() {
    echo "  $1"
}

# 1. Ferma e disabilita servizio
echo "1️⃣  Gestione servizio systemd..."
if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    log_action "Arresto servizio..."
    systemctl stop "$SERVICE_NAME" || echo "   ⚠️  Errore nell'arresto del servizio"
else
    log_action "Servizio già fermo"
fi

if systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null; then
    log_action "Disabilitazione servizio..."
    systemctl disable "$SERVICE_NAME" || echo "   ⚠️  Errore nella disabilitazione"
fi

# Rimuovi file servizio
if [ -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
    log_action "Rimozione file servizio..."
    rm -f "/etc/systemd/system/$SERVICE_NAME.service"
    systemctl daemon-reload
else
    log_action "File servizio non presente"
fi

# 2. Rimuovi cron jobs
echo "2️⃣  Rimozione cron jobs..."
if command -v crontab &> /dev/null; then
    if sudo -u "$USER" crontab -l 2>/dev/null | grep -q "access_control\|access-control"; then
        log_action "Backup crontab esistente..."
        sudo -u "$USER" crontab -l > "/tmp/crontab_backup_$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
        
        log_action "Rimozione job cron..."
        # Rimuovi solo le righe relative al sistema di controllo accessi
        sudo -u "$USER" crontab -l 2>/dev/null | grep -v "access_control\|access-control" | sudo -u "$USER" crontab - 2>/dev/null || true
    else
        log_action "Nessun cron job trovato"
    fi
else
    log_action "Crontab non disponibile"
fi

# 3. Backup dati (opzionale)
echo "3️⃣  Backup dati..."
BACKUP_DIR="/tmp/access_control_uninstall_backup_$(date +%Y%m%d_%H%M%S)"

read -p "Creare backup dei dati prima della rimozione? (y/N): " backup_choice
if [[ "$backup_choice" =~ ^[Yy]$ ]]; then
    log_action "Creazione backup in $BACKUP_DIR..."
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    if [ -f "$INSTALL_PATH/src/access.db" ]; then
        cp "$INSTALL_PATH/src/access.db" "$BACKUP_DIR/"
        log_action "Database salvato"
    fi
    
    # Backup configurazioni
    if [ -d "$INSTALL_PATH/config" ]; then
        cp -r "$INSTALL_PATH/config" "$BACKUP_DIR/"
        log_action "Configurazioni salvate"
    fi
    
    # Backup log
    if [ -d "/var/log/access_control" ]; then
        cp -r "/var/log/access_control" "$BACKUP_DIR/"
        log_action "Log salvati"
    fi
    
    # Backup scripts personalizzati
    if [ -d "$INSTALL_PATH/scripts" ]; then
        cp -r "$INSTALL_PATH/scripts" "$BACKUP_DIR/"
        log_action "Script salvati"
    fi
    
    chown -R "$USER:$USER" "$BACKUP_DIR" 2>/dev/null || true
    echo "   ✅ Backup creato in: $BACKUP_DIR"
else
    log_action "Backup saltato"
fi

# 4. Rimozione directory principale
echo "4️⃣  Rimozione directory di installazione..."
if [ -d "$INSTALL_PATH" ]; then
    log_action "Rimozione $INSTALL_PATH..."
    rm -rf "$INSTALL_PATH"
    log_action "Directory principale rimossa"
else
    log_action "Directory di installazione non presente"
fi

# 5. Rimozione log di sistema
echo "5️⃣  Rimozione log di sistema..."
if [ -d "/var/log/access_control" ]; then
    log_action "Rimozione /var/log/access_control..."
    rm -rf "/var/log/access_control"
    log_action "Log di sistema rimossi"
else
    log_action "Directory log non presente"
fi

# 6. Gestione utente (opzionale)
echo "6️⃣  Gestione utente di sistema..."
if id "$USER" &>/dev/null; then
    read -p "Rimuovere anche l'utente $USER? (y/N): " remove_user
    if [[ "$remove_user" =~ ^[Yy]$ ]]; then
        log_action "Rimozione utente $USER..."
        userdel -r "$USER" 2>/dev/null || userdel "$USER" 2>/dev/null || log_action "Errore rimozione utente"
        log_action "Utente rimosso"
    else
        log_action "Utente $USER mantenuto"
    fi
else
    log_action "Utente $USER non presente"
fi

# 7. Pulizia firewall
echo "7️⃣  Pulizia configurazioni firewall..."
if command -v ufw &> /dev/null; then
    if ufw status | grep -q "5000/tcp"; then
        log_action "Rimozione regola firewall porta 5000..."
        ufw delete allow 5000/tcp 2>/dev/null || log_action "Errore rimozione regola firewall"
    else
        log_action "Nessuna regola firewall trovata"
    fi
else
    log_action "UFW non disponibile"
fi

# 8. Pulizia pacchetti Python (opzionale)
echo "8️⃣  Pulizia pacchetti Python..."
read -p "Rimuovere le dipendenze Python installate? (y/N): " remove_deps
if [[ "$remove_deps" =~ ^[Yy]$ ]]; then
    log_action "Rimozione dipendenze Python specifiche..."
    
    PYTHON_PACKAGES=("flask" "flask-cors" "pyserial" "pyusb" "pyscard")
    for package in "${PYTHON_PACKAGES[@]}"; do
        if pip3 show "$package" &>/dev/null; then
            log_action "Rimozione $package..."
            pip3 uninstall -y "$package" 2>/dev/null || log_action "Errore rimozione $package"
        fi
    done
else
    log_action "Dipendenze Python mantenute"
fi

# 9. Verifica finale
echo "9️⃣  Verifica finale..."
ISSUES=()

if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    ISSUES+=("Servizio ancora attivo")
fi

if [ -d "$INSTALL_PATH" ]; then
    ISSUES+=("Directory di installazione ancora presente")
fi

if [ -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
    ISSUES+=("File servizio ancora presente")
fi

if [ ${#ISSUES[@]} -eq 0 ]; then
    log_action "✅ Disinstallazione completata con successo"
else
    log_action "⚠️  Problemi rilevati:"
    for issue in "${ISSUES[@]}"; do
        log_action "   - $issue"
    done
fi

echo ""
echo "=== Disinstallazione Completata ==="
echo "🗑️  Sistema di Controllo Accessi rimosso"

if [[ "$backup_choice" =~ ^[Yy]$ ]]; then
    echo "💾 Backup disponibile in: $BACKUP_DIR"
fi

echo "📋 Azioni eseguite:"
echo "   - Servizio systemd fermato e rimosso"
echo "   - Cron jobs rimossi"
echo "   - Directory /opt/access_control rimossa"
echo "   - Log di sistema rimossi"
echo "   - Configurazioni firewall pulite"

if [[ "$remove_user" =~ ^[Yy]$ ]]; then
    echo "   - Utente $USER rimosso"
fi

if [[ "$remove_deps" =~ ^[Yy]$ ]]; then
    echo "   - Dipendenze Python rimosse"
fi

echo ""
echo "ℹ️  Per reinstallare il sistema, utilizzare nuovamente install.sh"
echo "🔄 Per ripristinare i dati, utilizzare i file di backup creati"
