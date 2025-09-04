#!/bin/bash
# Script ripristino backup backup_completo_20250719_135043.tar.gz
# Generato: 2025-07-19 13:50:43.817902

BACKUP_FILE="backup_completo_20250719_135043.tar.gz"
EXPECTED_MD5="3eeaeb084863dd1ef054f7f3589b40c0"
PROJECT_ROOT="/opt/access_control"

echo "=== RIPRISTINO BACKUP SISTEMA CONTROLLO ACCESSI ==="
echo "Backup: $BACKUP_FILE"
echo ""

# Verifica checksum
echo "Verifica integrità backup..."
ACTUAL_MD5=$(md5sum "$BACKUP_FILE" | cut -d' ' -f1)
if [ "$ACTUAL_MD5" != "$EXPECTED_MD5" ]; then
    echo "ERRORE: Checksum non corrispondente!"
    echo "Atteso: $EXPECTED_MD5"
    echo "Trovato: $ACTUAL_MD5"
    exit 1
fi
echo "✓ Checksum verificato"

# Conferma
read -p "Vuoi procedere con il ripristino? (s/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Ripristino annullato"
    exit 0
fi

# Stop servizi
echo "Arresto servizi..."
sudo systemctl stop access-control 2>/dev/null

# Backup attuale
echo "Backup configurazione attuale..."
sudo mv $PROJECT_ROOT $PROJECT_ROOT.old.$(date +%Y%m%d_%H%M%S)

# Estrazione
echo "Estrazione backup..."
sudo tar -xzf "$BACKUP_FILE" -C /opt/

# Ripristino permessi
echo "Ripristino permessi..."
sudo chown -R root:root $PROJECT_ROOT
sudo chmod +x $PROJECT_ROOT/scripts/*.py

# Restart servizi
echo "Riavvio servizi..."
sudo systemctl start access-control 2>/dev/null

echo ""
echo "✓ RIPRISTINO COMPLETATO"
echo "Backup precedente salvato con suffisso .old"
