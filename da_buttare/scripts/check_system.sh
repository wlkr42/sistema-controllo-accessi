#!/bin/bash
# File: /opt/access_control/scripts/check_system.sh
# Verifica completa sistema

PROJECT_ROOT="/opt/access_control"
VENV_PATH="$PROJECT_ROOT/venv"

echo "🔍 VERIFICA COMPLETA SISTEMA"
echo "=" * 50

# 1. Verifica directory
echo "📁 Directory progetto:"
if [[ -d "$PROJECT_ROOT" ]]; then
    echo "  ✅ $PROJECT_ROOT esiste"
    echo "  📊 Dimensione: $(du -sh $PROJECT_ROOT | cut -f1)"
else
    echo "  ❌ $PROJECT_ROOT non trovata"
fi

# 2. Verifica virtual environment
echo ""
echo "🐍 Virtual Environment:"
if [[ -d "$VENV_PATH" ]]; then
    echo "  ✅ Virtual environment esiste"
    echo "  📦 Python: $($VENV_PATH/bin/python --version)"
else
    echo "  ❌ Virtual environment non trovato"
fi

# 3. Verifica database
echo ""
echo "🗄️  Database:"
DB_PATH="$PROJECT_ROOT/src/access.db"
if [[ -f "$DB_PATH" ]]; then
    echo "  ✅ Database esiste"
    echo "  📊 Dimensione: $(ls -lh $DB_PATH | awk '{print $5}')"
    
    # Count records se possibile
    if command -v sqlite3 >/dev/null; then
        USERS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM authorized_people;" 2>/dev/null || echo "N/A")
        LOGS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM access_log;" 2>/dev/null || echo "N/A")
        echo "  👥 Utenti autorizzati: $USERS"
        echo "  📋 Log accessi: $LOGS"
    fi
else
    echo "  ⚠️  Database non trovato (verrà creato al primo avvio)"
fi

# 4. Verifica servizi
echo ""
echo "🔧 Servizi:"
services=("access-control" "pcscd")
for service in "${services[@]}"; do
    if systemctl is-active --quiet "$service"; then
        echo "  ✅ $service: ATTIVO"
    else
        echo "  ❌ $service: INATTIVO"
    fi
done

# 5. Verifica hardware
echo ""
echo "🔌 Hardware:"
if ls /dev/ttyACM* >/dev/null 2>&1; then
    echo "  ✅ Lettore tessere: $(ls /dev/ttyACM*)"
else
    echo "  ⚠️  Lettore tessere non rilevato"
fi

if ls /dev/ttyUSB* >/dev/null 2>&1; then
    echo "  ✅ USB-RLY08: $(ls /dev/ttyUSB*)"
else
    echo "  ⚠️  USB-RLY08 non rilevato"
fi

# 6. Verifica rete
echo ""
echo "🌐 Rete:"
if netstat -tuln 2>/dev/null | grep -q ":5000 "; then
    echo "  ✅ Dashboard web: ATTIVA su porta 5000"
    echo "  🔗 URL: http://192.168.178.200:5000"
else
    echo "  ❌ Dashboard web: NON ATTIVA"
fi

# 7. Verifica log
echo ""
echo "📋 Log Recenti:"
if journalctl -u access-control --no-pager -n 3 >/dev/null 2>&1; then
    journalctl -u access-control --no-pager -n 3 | tail -3
else
    echo "  ⚠️  Log non disponibili"
fi

echo ""
echo "=" * 50
