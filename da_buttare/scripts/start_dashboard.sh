#!/bin/bash
# File: /opt/access_control/scripts/start_dashboard.sh
# Script avvio Dashboard Web

echo "🚀 AVVIO DASHBOARD CONTROLLO ACCESSI"
echo "=" * 50

# Variabili
PROJECT_ROOT="/opt/access_control"
VENV_PATH="$PROJECT_ROOT/venv"
API_PATH="$PROJECT_ROOT/src/api/web_api.py"

# Controlla directory progetto
if [ ! -d "$PROJECT_ROOT" ]; then
    echo "❌ Directory progetto non trovata: $PROJECT_ROOT"
    exit 1
fi

cd "$PROJECT_ROOT"

# Attiva virtual environment
if [ -d "$VENV_PATH" ]; then
    echo "🐍 Attivazione virtual environment..."
    source "$VENV_PATH/bin/activate"
else
    echo "⚠️ Virtual environment non trovato in $VENV_PATH"
    echo "🔧 Creazione virtual environment..."
    python3 -m venv "$VENV_PATH"
    source "$VENV_PATH/bin/activate"
fi

# Installa dipendenze aggiuntive per dashboard
echo "📦 Installazione dipendenze dashboard..."

# Dipendenze base già presenti
pip install --quiet flask flask-cors pandas openpyxl

# Verifica dipendenze critiche
echo "🔍 Verifica dipendenze..."
python3 -c "
import flask
import pandas as pd
import openpyxl
print('✅ Dipendenze dashboard OK')
" || {
    echo "❌ Errore dipendenze dashboard"
    exit 1
}

# Crea directory API se non esiste
mkdir -p "$PROJECT_ROOT/src/api"
mkdir -p "$PROJECT_ROOT/temp"
mkdir -p "$PROJECT_ROOT/config"

# Verifica file API
if [ ! -f "$API_PATH" ]; then
    echo "❌ File API non trovato: $API_PATH"
    echo "💡 Copiare il codice Flask API in $API_PATH"
    exit 1
fi

# Verifica permessi
echo "🔧 Verifica permessi..."
if [ ! -w "$PROJECT_ROOT" ]; then
    echo "⚠️ Permessi scrittura mancanti su $PROJECT_ROOT"
    echo "🔧 Eseguire: sudo chown -R $USER:$USER $PROJECT_ROOT"
fi

# Verifica hardware
echo "🔌 Verifica hardware..."
if [ -e "/dev/ttyACM0" ]; then
    echo "✅ USB-RLY08 rilevato su /dev/ttyACM0"
else
    echo "⚠️ USB-RLY08 non rilevato"
fi

# Check gruppo dialout
if groups $USER | grep -q dialout; then
    echo "✅ Utente nel gruppo dialout"
else
    echo "⚠️ Utente non nel gruppo dialout"
    echo "🔧 Eseguire: sudo usermod -a -G dialout $USER && newgrp dialout"
fi

# Controlla se porta 5000 è libera
if netstat -tuln | grep -q ":5000 "; then
    echo "⚠️ Porta 5000 già in uso"
    echo "🔧 Fermare servizi sulla porta 5000 o modificare configurazione"
    
    # Chiedi se procedere comunque
    read -p "Continuare comunque? (y/n): " choice
    case "$choice" in 
        y|Y ) echo "Proceeding...";;
        * ) echo "Uscita."; exit 1;;
    esac
fi

# Avvia API Flask
echo ""
echo "🌐 AVVIO FLASK API DASHBOARD"
echo "=" * 50
echo "📍 URL: http://localhost:5000"
echo "�� Login: admin / admin"
echo "📊 Dashboard completa con:"
echo "   - Panoramica real-time"
echo "   - Gestione hardware"
echo "   - Log accessi live"
echo "   - Export Excel"
echo "   - Configurazione completa"
echo ""
echo "⏹️ Ctrl+C per fermare"
echo "=" * 50

# Esegui API Flask
python3 "$API_PATH"
