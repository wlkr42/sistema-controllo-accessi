#!/bin/bash
# ============================================================================
# QUICK INSTALL - Sistema Controllo Accessi
# Scarica e installa tutto automaticamente
# 
# Uso: curl -fsSL https://raw.githubusercontent.com/wlkr42/sistema-controllo-accessi/release/v3.0.0-RC1/scripts/install/quick_install.sh | sudo bash
# ============================================================================

set -e

echo "============================================================================"
echo "         SISTEMA CONTROLLO ACCESSI - QUICK INSTALL"
echo "============================================================================"
echo ""

# Verifica root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Questo script deve essere eseguito come root"
    echo "   Usa: curl -fsSL ... | sudo bash"
    exit 1
fi

# Directory temporanea
TEMP_DIR="/tmp/access_control_install_$$"
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

echo "📥 Download script installazione..."

# Base URL
BASE_URL="https://raw.githubusercontent.com/wlkr42/sistema-controllo-accessi/release/v3.0.0-RC1/scripts/install"

# Scarica tutti gli script necessari
wget -q "$BASE_URL/install_system.sh" || { echo "❌ Errore download install_system.sh"; exit 1; }
wget -q "$BASE_URL/setup_database.py" || { echo "❌ Errore download setup_database.py"; exit 1; }
wget -q "$BASE_URL/setup_drivers.sh" || { echo "❌ Errore download setup_drivers.sh"; exit 1; }
wget -q "$BASE_URL/setup_services.sh" || { echo "❌ Errore download setup_services.sh"; exit 1; }
wget -q "$BASE_URL/setup_permissions.sh" || { echo "❌ Errore download setup_permissions.sh"; exit 1; }
wget -q "$BASE_URL/verify_installation.sh" || { echo "❌ Errore download verify_installation.sh"; exit 1; }

# Rendi eseguibili
chmod +x *.sh

echo "✅ Script scaricati"
echo ""

# Determina ambiente
if [ -z "$INSTALL_ENV" ]; then
    echo "Seleziona ambiente di installazione:"
    echo "1) Sviluppo (Flask dev server)"
    echo "2) Produzione (Gunicorn WSGI)"
    read -p "Scelta [1]: " choice
    
    case $choice in
        2) INSTALL_ENV="production" ;;
        *) INSTALL_ENV="development" ;;
    esac
fi

echo ""
echo "🚀 Avvio installazione (ambiente: $INSTALL_ENV)"
echo "   Il sistema chiederà le credenziali GitHub..."
echo ""
sleep 2

# Esegui installazione
bash install_system.sh "$INSTALL_ENV"

# Cleanup
cd /
rm -rf "$TEMP_DIR"

echo ""
echo "============================================================================"
echo "✅ Installazione completata!"
echo ""
echo "Sistema disponibile su: http://$(hostname -I | awk '{print $1}'):5000"
echo "Username: admin"
echo "Password: admin123"
echo "============================================================================"