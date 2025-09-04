#!/bin/bash
#
# Script di avvio sistema completo controllo accessi
# Esegue tutto come root per evitare problemi di permessi
#

echo "🚀 AVVIO SISTEMA CONTROLLO ACCESSI"
echo "=================================="
echo ""

# 1. Verifica che siamo root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Questo script deve essere eseguito come root"
    echo "    Uso: sudo $0"
    exit 1
fi

# 2. Verifica dispositivi hardware
echo "🔍 Verifica hardware..."

# CRT-285
if lsusb | grep -q "23d8:0285"; then
    echo "✅ CRT-285 rilevato"
else
    echo "⚠️  CRT-285 non rilevato (continuo comunque)"
fi

# USB-RLY08
if lsusb | grep -q "04d8:ffee"; then
    echo "✅ USB-RLY08 rilevato"
else
    echo "⚠️  USB-RLY08 non rilevato (continuo comunque)"
fi

# 3. Installa/aggiorna servizio systemd
echo ""
echo "📦 Installazione servizio systemd..."
cp /opt/access_control/access-control-web.service /etc/systemd/system/
systemctl daemon-reload
echo "✅ Servizio installato"

# 4. Avvia il servizio
echo ""
echo "🚀 Avvio servizio..."
systemctl restart access-control-web
sleep 2

# 5. Verifica stato
if systemctl is-active --quiet access-control-web; then
    echo "✅ Servizio avviato correttamente!"
else
    echo "❌ Errore avvio servizio!"
    echo ""
    echo "Debug:"
    systemctl status access-control-web --no-pager
    exit 1
fi

# 6. Abilita avvio automatico
systemctl enable access-control-web 2>/dev/null

echo ""
echo "=================================="
echo "✅ SISTEMA AVVIATO CON SUCCESSO!"
echo ""
echo "📊 Info:"
echo "   Web Interface: http://$(hostname -I | awk '{print $1}'):5000"
echo "   Admin: http://$(hostname -I | awk '{print $1}'):5000/admin/config"
echo ""
echo "📝 Comandi utili:"
echo "   Stato:    systemctl status access-control-web"
echo "   Log:      journalctl -u access-control-web -f"
echo "   Restart:  systemctl restart access-control-web"
echo "   Stop:     systemctl stop access-control-web"
echo ""