#!/usr/bin/env python3
"""
Script di analisi differenze tra cittadini sincronizzati da Odoo e conteggio Odoo web.

- Legge il file /opt/access_control/data/partner_cache.json (output sync Odoo)
- Stampa il numero di cittadini trovati nella cache
- Stampa i primi 10 CF e nomi per verifica
- Esporta la lista dei CF in un file di testo (cf_sync.txt)
- (Opzionale) Se fornito un file cf_odoo.txt (esportato da Odoo), mostra le differenze

USO:
    python scripts/check_odoo_sync_discrepancy.py [cf_odoo.txt]
"""

import json
import sys
from pathlib import Path

CACHE_PATH = "/opt/access_control/data/partner_cache.json"
EXPORT_SYNC_CF = "cf_sync.txt"

def load_cache(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    cittadini = data.get("cittadini", [])
    return cittadini

def export_cf_list(cittadini, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        for c in cittadini:
            cf = c.get("codice_fiscale", "").strip().upper()
            f.write(cf + "\n")

def load_cf_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return set(line.strip().upper() for line in f if line.strip())

def main():
    print("=== ANALISI DISCREPANZA SYNC ODOO ===")
    if not Path(CACHE_PATH).exists():
        print(f"ERRORE: File cache non trovato: {CACHE_PATH}")
        sys.exit(1)
    cittadini = load_cache(CACHE_PATH)
    print(f"Cittadini trovati in cache: {len(cittadini)}")
    print("Primi 10 cittadini:")
    for c in cittadini[:10]:
        print(f"  - {c.get('nome', 'N/A')} ({c.get('codice_fiscale', 'N/A')})")
    export_cf_list(cittadini, EXPORT_SYNC_CF)
    print(f"Lista CF sincronizzati esportata in: {EXPORT_SYNC_CF}")

    if len(sys.argv) > 1:
        cf_odoo_path = sys.argv[1]
        if not Path(cf_odoo_path).exists():
            print(f"File Odoo non trovato: {cf_odoo_path}")
            sys.exit(2)
        cf_sync = load_cf_file(EXPORT_SYNC_CF)
        cf_odoo = load_cf_file(cf_odoo_path)
        print(f"\nCF in Odoo (file): {len(cf_odoo)}")
        print(f"CF in Sync: {len(cf_sync)}")
        only_in_odoo = cf_odoo - cf_sync
        only_in_sync = cf_sync - cf_odoo
        print(f"\nCF presenti in Odoo ma NON in Sync: {len(only_in_odoo)}")
        if only_in_odoo:
            for cf in list(only_in_odoo)[:10]:
                print(f"  - {cf}")
            if len(only_in_odoo) > 10:
                print("  ...")
        print(f"\nCF presenti in Sync ma NON in Odoo: {len(only_in_sync)}")
        if only_in_sync:
            for cf in list(only_in_sync)[:10]:
                print(f"  - {cf}")
            if len(only_in_sync) > 10:
                print("  ...")
        print("\nAnalisi completata.")
    else:
        print("\nPer confronto automatico, esporta la lista CF da Odoo in un file txt (uno per riga) e lancia:")
        print("  python scripts/check_odoo_sync_discrepancy.py cf_odoo.txt")

if __name__ == "__main__":
    main()
