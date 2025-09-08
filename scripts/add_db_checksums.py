#!/usr/bin/env python3
"""
Aggiungi checksum MD5 ai backup database esistenti che non ce l'hanno
"""
import hashlib
from pathlib import Path

BACKUP_DIR = Path("/opt/access_control/backups")

def add_checksums_to_databases():
    """Crea checksum per database senza"""
    added = 0
    
    for db_file in BACKUP_DIR.glob("access_*.db"):
        checksum_file = BACKUP_DIR / f"{db_file.name}.md5"
        
        if not checksum_file.exists():
            print(f"Calcolo checksum per {db_file.name}...")
            
            # Calcola MD5
            hash_md5 = hashlib.md5()
            with open(db_file, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            
            checksum = hash_md5.hexdigest()
            
            # Scrivi checksum
            with open(checksum_file, 'w') as f:
                f.write(f"{checksum}  {db_file.name}\n")
            
            print(f"  ✓ Checksum creato: {checksum}")
            added += 1
        else:
            print(f"  {db_file.name} ha già checksum")
    
    print(f"\nAggiunti {added} checksum")
    return added

if __name__ == "__main__":
    add_checksums_to_databases()