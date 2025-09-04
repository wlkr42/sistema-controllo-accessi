#!/bin/bash

echo "🚀 AVVIO SERVIZIO ACCESS CONTROL"
echo "================================="

# Vai nella directory del progetto
cd /opt/access_control

# 1. Termina TUTTI i processi che potrebbero usare la porta 5000
echo "1. Pulizia processi esistenti..."
pkill -f "python.*web_api.py" 2>/dev/null
pkill -f "python.*main.py" 2>/dev/null
pkill -f "flask" 2>/dev/null

# Attendi che i processi si chiudano
sleep 2

# 2. Verifica che la porta 5000 sia libera
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Porta 5000 ancora occupata, terminazione forzata..."
    kill -9 $(lsof -t -i:5000) 2>/dev/null
    sleep 2
fi

# 3. Attiva virtual environment e avvia il servizio
echo "2. Avvio servizio web..."
source venv/bin/activate
python src/api/web_api.py &

# Salva il PID
echo $! > /tmp/web_api.pid

# 4. Attendi che il servizio sia pronto
echo "3. Attesa avvio servizio..."
for i in {1..10}; do
    if curl -s http://localhost:5000 > /dev/null 2>&1; then
        echo ""
        echo "✅ SERVIZIO AVVIATO CON SUCCESSO!"
        echo ""
        echo "📌 Accedi a: http://192.168.1.236:5000"
        echo ""
        echo "🔧 Modifiche applicate:"
        echo "   ✅ Fix duplicazione funzione api_test_gate"
        echo "   ✅ Test hardware dalla dashboard funzionanti"
        echo "   ✅ Test mostra CRT-285 invece di OMNIKEY"
        echo "   ✅ Salvataggio configurazioni hardware"
        echo "   ✅ Sezione Debug in /admin/config"
        echo ""
        echo "📝 Per vedere i log in tempo reale:"
        echo "   tail -f /tmp/web_api.log"
        echo ""
        echo "🛑 Per fermare il servizio:"
        echo "   kill \$(cat /tmp/web_api.pid)"
        exit 0
    fi
    echo -n "."
    sleep 1
done

echo ""
echo "❌ ERRORE: Il servizio non si è avviato correttamente"
echo "Controlla i log con: tail -f /tmp/web_api.log"
exit 1