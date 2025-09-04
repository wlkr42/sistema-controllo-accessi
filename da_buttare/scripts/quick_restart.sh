#!/bin/bash
# File: /opt/access_control/scripts/quick_restart.sh
# Riavvio rapido per uso quotidiano

PROJECT_ROOT="/opt/access_control"
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔄 Riavvio rapido sistema...${NC}"

# Stop e restart
systemctl stop access-control 2>/dev/null || true
pkill -f "/opt/access_control" 2>/dev/null || true
fuser -k 5000/tcp 2>/dev/null || true

# Hardware reset veloce
systemctl restart pcscd
chmod 666 /dev/ttyACM* /dev/ttyUSB* 2>/dev/null || true

# Avvio
systemctl start access-control
sleep 5

if systemctl is-active --quiet access-control; then
    echo -e "${GREEN}✅ Sistema riavviato!${NC}"
    echo -e "${GREEN}🌐 http://192.168.178.200:5000${NC}"
else
    echo "❌ Errore - controllare: journalctl -u access-control -f"
fi
