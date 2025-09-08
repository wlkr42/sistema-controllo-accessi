#!/usr/bin/env python3
"""
Script per sistemare i nomi dei checksum esistenti
"""
import os
from pathlib import Path

BACKUP_DIR = Path("/opt/access_control/backups")

def fix_checksum_names():
    """Rinomina i checksum con nome sbagliato"""
    fixed = 0
    
    # Trova tutti i file .tar.tar.gz.md5
    for wrong_checksum in BACKUP_DIR.glob("*.tar.tar.gz.md5"):
        # Calcola il nome corretto
        base_name = wrong_checksum.name.replace('.tar.tar.gz.md5', '.tar.gz.md5')
        correct_path = BACKUP_DIR / base_name
        
        print(f"Rinomino: {wrong_checksum.name} -> {base_name}")
        wrong_checksum.rename(correct_path)
        fixed += 1
    
    print(f"\nCorretti {fixed} file checksum")
    return fixed

if __name__ == "__main__":
    fix_checksum_names()