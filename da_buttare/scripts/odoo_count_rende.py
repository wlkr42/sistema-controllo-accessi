#!/usr/bin/env python3
"""
Script esterno: conta cittadini Odoo con filtri come da dashboard (senza filtro CF).

Filtri:
- city contiene "rende"
- is_person = True
- is_company = False
- is_ente = False
- active = True

USO:
    python scripts/odoo_count_rende.py

Modifica le variabili ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASS se necessario.
"""

import xmlrpc.client

# CONFIGURAZIONE ODOO (modifica se necessario)
ODOO_URL = "https://app.calabramaceri.it"
ODOO_DB = "cmapp"
ODOO_USER = "controllo-accessi@calabramaceri.it"
ODOO_PASS = "AcC3ss0C0ntr0l!2025#Rnd"

def main():
    print("=== CONTA CITTADINI ODOO (filtri dashboard) ===")
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    object_proxy = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

    print("Autenticazione...")
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
    if not uid:
        print("ERRORE: autenticazione fallita")
        return

    print("Eseguo search_count con filtri:")
    domain = [
        ("city", "ilike", "rende"),
        ("is_person", "=", True),
        ("is_company", "=", False),
        ("is_ente", "=", False),
        ("active", "=", True)
    ]
    print(domain)

    count = object_proxy.execute_kw(
        ODOO_DB, uid, ODOO_PASS,
        "res.partner", "search_count", [domain]
    )
    print(f"\nTotale cittadini trovati: {count}")

    # Opzionale: stampa i primi 10 nomi/ID
    ids = object_proxy.execute_kw(
        ODOO_DB, uid, ODOO_PASS,
        "res.partner", "search", [domain], {"limit": 10}
    )
    if ids:
        partners = object_proxy.execute_kw(
            ODOO_DB, uid, ODOO_PASS,
            "res.partner", "read", [ids], {"fields": ["id", "name", "city"]}
        )
        print("\nPrimi 10 cittadini:")
        for p in partners:
            print(f"  - {p.get('name', 'N/A')} (ID: {p.get('id')}, città: {p.get('city', '')})")
    else:
        print("Nessun cittadino trovato.")

if __name__ == "__main__":
    main()
