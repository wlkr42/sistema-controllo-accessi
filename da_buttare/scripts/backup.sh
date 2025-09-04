#!/bin/bash
# File: /opt/access_control/scripts/backup.sh
# Backup automatico database e configurazioni

BACKUP_DIR="/opt/access_control/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE="/opt/access_control/src/access.db"
CONFIG_DIR="/opt/access_control/config"

# Crea backup database se esistente
if [ -f "$DB_FILE" ]; then
    sqlite3 "$DB_FILE" ".backup '$BACKUP_DIR/access_db_$DATE.db'"
    echo "Database backup: access_db_$DATE.db"
fi

# Backup configurazioni
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" -C "$CONFIG_DIR" .
echo "Config backup: config_$DATE.tar.gz"

# Rimuovi backup vecchi (>30 giorni)
find "$BACKUP_DIR" -name "*.db" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "Backup completato: $DATE"
