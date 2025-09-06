#!/usr/bin/env python3
import sys
sys.path.insert(0, '/opt/access_control')

from src.api.admin_templates import ADMIN_BACKUP_TEMPLATE

# Verifica presenza nuove sezioni
sections = [
    "Cloud Backup",
    "Verifica Integrità", 
    "Giornaliero",
    "Settimanale",
    "Mensile",
    "Annuale",
    "FTP/SFTP",
    "Amazon S3"
]

print("Verifica template ADMIN_BACKUP_TEMPLATE:")
print(f"Lunghezza totale: {len(ADMIN_BACKUP_TEMPLATE)} caratteri")
print("\nSezioni trovate:")
for section in sections:
    if section in ADMIN_BACKUP_TEMPLATE:
        print(f"✅ {section}")
    else:
        print(f"❌ {section} NON TROVATO")

# Mostra prime righe con Cloud Backup
lines = ADMIN_BACKUP_TEMPLATE.split('\n')
for i, line in enumerate(lines):
    if 'Cloud Backup' in line:
        print(f"\nLinea {i}: {line}")
        # Mostra 5 righe successive
        for j in range(i+1, min(i+6, len(lines))):
            print(f"Linea {j}: {lines[j]}")
        break