#!/bin/bash
echo "🔄 Forzando reload completo del sistema..."

# 1. Ferma il servizio
echo "⏹️  Fermando servizio..."
sudo systemctl stop access-control-web

# 2. Elimina TUTTI i file Python compilati
echo "🧹 Pulizia cache Python..."
find /opt/access_control -type f -name "*.pyc" -delete 2>/dev/null
find /opt/access_control -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# 3. Killa eventuali processi zombie
echo "☠️  Terminando processi residui..."
sudo pkill -9 -f "python.*web_api" 2>/dev/null
sudo pkill -9 -f "python.*src.api" 2>/dev/null
sleep 2

# 4. Verifica che il template sia corretto
echo "✅ Verifica template..."
python3 -c "
import sys
sys.path.insert(0, '/opt/access_control')
from src.api.admin_templates import ADMIN_BACKUP_TEMPLATE
if 'Cloud Backup' in ADMIN_BACKUP_TEMPLATE:
    print('   Template contiene Cloud Backup ✓')
else:
    print('   ⚠️  Template NON contiene Cloud Backup!')
"

# 5. Riavvia il servizio
echo "🚀 Riavvio servizio..."
sudo systemctl start access-control-web
sleep 3

# 6. Verifica stato
if systemctl is-active --quiet access-control-web; then
    echo "✅ Servizio attivo!"
    echo ""
    echo "📝 Istruzioni:"
    echo "1. Apri il browser"
    echo "2. Premi CTRL+SHIFT+R per forzare reload completo"
    echo "3. Vai su http://192.168.1.236:5000/admin/backup"
    echo "4. Login con admin/admin123"
else
    echo "❌ Errore avvio servizio"
    sudo journalctl -u access-control-web -n 20
fi