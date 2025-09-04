#!/bin/bash
# File: /opt/access_control/scripts/quick_backup.sh
# Script backup rapido Sistema Controllo Accessi

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configurazione
PROJECT_ROOT="/opt/access_control"
BACKUP_DIR="$PROJECT_ROOT/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="quick_backup_$TIMESTAMP"

echo -e "${GREEN}=== BACKUP RAPIDO SISTEMA CONTROLLO ACCESSI ===${NC}"
echo "Data: $(date '+%d/%m/%Y %H:%M:%S')"
echo ""

# Crea directory backup
mkdir -p "$BACKUP_DIR"

# 1. Backup database
echo -e "${YELLOW}Backup database...${NC}"
if [ -f "$PROJECT_ROOT/src/access.db" ]; then
    cp "$PROJECT_ROOT/src/access.db" "$BACKUP_DIR/access_$TIMESTAMP.db"
    echo -e "${GREEN}✓${NC} Database salvato: access_$TIMESTAMP.db"
else
    echo -e "${RED}✗${NC} Database non trovato!"
fi

# 2. Backup configurazioni
echo -e "\n${YELLOW}Backup configurazioni...${NC}"
if [ -d "$PROJECT_ROOT/config" ]; then
    tar -czf "$BACKUP_DIR/config_$TIMESTAMP.tar.gz" -C "$PROJECT_ROOT" config/
    echo -e "${GREEN}✓${NC} Configurazioni salvate: config_$TIMESTAMP.tar.gz"
fi

# 3. Backup codice API modificato oggi
echo -e "\n${YELLOW}Backup file modificati oggi...${NC}"
MODIFIED_FILES=$(find "$PROJECT_ROOT/src" -type f -name "*.py" -mtime -1)
if [ -n "$MODIFIED_FILES" ]; then
    tar -czf "$BACKUP_DIR/src_modified_$TIMESTAMP.tar.gz" -C "$PROJECT_ROOT" \
        $(find src -type f -name "*.py" -mtime -1 | sed 's|^/opt/access_control/||')
    echo -e "${GREEN}✓${NC} File modificati salvati: src_modified_$TIMESTAMP.tar.gz"
fi

# 4. Crea file info backup
INFO_FILE="$BACKUP_DIR/backup_info_$TIMESTAMP.txt"
cat > "$INFO_FILE" << EOF
=== BACKUP RAPIDO INFO ===
Data: $(date)
Host: $(hostname)
Utente: $(whoami)

File backuppati:
- Database: access_$TIMESTAMP.db
- Config: config_$TIMESTAMP.tar.gz
- Src modificati: src_modified_$TIMESTAMP.tar.gz

Spazio utilizzato:
$(du -sh "$BACKUP_DIR"/* | grep "$TIMESTAMP")

Processi attivi:
$(ps aux | grep python | grep access_control | grep -v grep)
EOF

echo -e "${GREEN}✓${NC} Info backup salvate"

# 5. Pulizia backup vecchi (mantieni ultimi 10 backup rapidi)
echo -e "\n${YELLOW}Pulizia backup vecchi...${NC}"
QUICK_BACKUPS=$(ls -t "$BACKUP_DIR"/quick_backup_* 2>/dev/null | wc -l)
if [ "$QUICK_BACKUPS" -gt 30 ]; then
    ls -t "$BACKUP_DIR"/quick_backup_* | tail -n +31 | xargs rm -f
    echo -e "${GREEN}✓${NC} Rimossi backup rapidi vecchi"
fi

# 6. Report finale
echo -e "\n${GREEN}=== BACKUP RAPIDO COMPLETATO ===${NC}"
echo "Directory: $BACKUP_DIR"
echo "Timestamp: $TIMESTAMP"
echo ""
echo "File creati:"
ls -lh "$BACKUP_DIR"/*"$TIMESTAMP"* | awk '{print "- " $9 " (" $5 ")"}'

# 7. Crea link all'ultimo backup
ln -sf "$BACKUP_DIR/access_$TIMESTAMP.db" "$BACKUP_DIR/latest_database.db"
echo -e "\n${GREEN}✓${NC} Link 'latest_database.db' aggiornato"

