#!/bin/bash

echo "🔴 RIAVVIO FORZATO DEL SERVIZIO"
echo "================================"

# Termina TUTTI i processi Python correlati
echo "1. Terminando processi esistenti..."
sudo pkill -9 -f "python.*web_api.py" 2>/dev/null
sudo pkill -9 -f "python.*main.py" 2>/dev/null
sleep 2

# Verifica che siano terminati
if pgrep -f "web_api.py" > /dev/null; then
    echo "⚠️  Alcuni processi ancora attivi, terminazione forzata..."
    sudo killall -9 python 2>/dev/null
    sudo killall -9 python3 2>/dev/null
    sleep 2
fi

# Riavvia il servizio systemd
echo "2. Riavviando servizio systemd..."
sudo systemctl restart access-control-web

# Attendi che il servizio si avvii
echo "3. Attendendo avvio servizio..."
sleep 3

# Verifica stato
echo "4. Verifica stato servizio:"
sudo systemctl status access-control-web --no-pager | head -15

echo ""
echo "✅ RIAVVIO COMPLETATO!"
echo ""
echo "📌 Le modifiche applicate includono:"
echo "   - Test hardware dalla dashboard funzionanti"
echo "   - Test mostra CRT-285 invece di OMNIKEY"
echo "   - Salvataggio configurazioni hardware"
echo "   - Sezione Debug in /admin/config"
echo "   - Rimossa sezione hardware duplicata"
echo ""
echo "🌐 Accedi a: http://192.168.1.236:5000"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "🐛 Vai su Configurazioni → tab Debug per vedere i log"