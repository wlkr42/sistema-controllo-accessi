#!/bin/bash

echo "🔄 Riavvio servizio Access Control..."

# Trova e termina i processi esistenti
echo "Terminando processi esistenti..."
pkill -f "web_api.py" 2>/dev/null
sleep 2

# Avvia il nuovo processo
echo "Avviando nuovo processo..."
cd /opt/access_control
/opt/access_control/venv/bin/python src/api/web_api.py &

echo "✅ Servizio riavviato!"
echo ""
echo "La sezione Debug dovrebbe ora essere visibile su:"
echo "http://192.168.1.236:5000/admin/config"
echo ""
echo "Clicca sulla tab 'Debug' (icona bug 🐛) per vedere:"
echo "- Console log in tempo reale"
echo "- Stato sistema"
echo "- Pulsante riavvio servizio"