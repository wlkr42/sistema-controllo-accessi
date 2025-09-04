#!/usr/bin/env python3
"""
Script per analisi discrepanza conteggio cittadini Odoo (dashboard vs API).

- Scarica tutti gli ID con city contiene "rende" e active=True (come da filtro Odoo web)
- Scarica tutti gli ID con filtri API (is_person, is_company, is_ente, city, active)
- Mostra la differenza (ID presenti solo in Odoo web)
- Stampa i dettagli (name, id, is_person, is_company, is_ente, active, city, internal_type, etc) dei primi 20 record "extra"

USO:
    python scripts/odoo_count_rende_discrepancy.py

Modifica le variabili ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASS se necessario.
"""

import xmlrpc.client

# CONFIGURAZIONE ODOO (modifica se necessario)
ODOO_URL = "https://app.calabramaceri.it"
ODOO_DB = "cmapp"
ODOO_USER = "controllo-accessi@calabramaceri.it"
ODOO_PASS = "AcC3ss0C0ntr0l!2025#Rnd"

def main():
    print("=== ANALISI DISCREPANZA CITTADINI ODOO ===")
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    object_proxy = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

    print("Autenticazione...")
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
    if not uid:
        print("ERRORE: autenticazione fallita")
        return

    # 1. Filtro come da dashboard Odoo web (city contiene "rende", active=True)
    domain_web = [
        ("city", "ilike", "rende"),
        ("active", "=", True)
    ]
    ids_web = object_proxy.execute_kw(
        ODOO_DB, uid, ODOO_PASS,
        "res.partner", "search", [domain_web], {"limit": 30000}
    )
    print(f"Totale ID trovati (filtro Odoo web): {len(ids_web)}")

    # 2. Filtro API (is_person, is_company, is_ente, city, active)
    domain_api = [
        ("city", "ilike", "rende"),
        ("is_person", "=", True),
        ("is_company", "=", False),
        ("is_ente", "=", False),
        ("active", "=", True)
    ]
    ids_api = object_proxy.execute_kw(
        ODOO_DB, uid, ODOO_PASS,
        "res.partner", "search", [domain_api], {"limit": 30000}
    )
    print(f"Totale ID trovati (filtro API): {len(ids_api)}")

    # 3. Differenza: ID presenti solo in web (possibili "utenti interni" o record speciali)
    extra_ids = set(ids_web) - set(ids_api)
    print(f"\nRecord presenti SOLO in Odoo web (non in API): {len(extra_ids)}")
    if extra_ids:
        details = object_proxy.execute_kw(
            ODOO_DB, uid, ODOO_PASS,
            "res.partner", "read", [list(extra_ids)[:20]],
            {"fields": [
                "id", "name", "city", "active", "is_person", "is_company", "is_ente",
                "company_type", "user_id", "customer_rank", "supplier_rank"
            ]}
        )
        print("\nPrimi 20 record 'extra':")
        for d in details:
            tipo = []
            if d.get("is_company"):
                tipo.append("AZIENDA")
            if d.get("is_ente"):
                tipo.append("ENTE")
            if d.get("user_id"):
                tipo.append("UTENTE INTERNO")
            if d.get("company_type") and d.get("company_type") != "person":
                tipo.append(f"company_type={d.get('company_type')}")
            if not tipo and not d.get("is_person"):
                tipo.append("ALTRO")
            tipo_str = ", ".join(tipo) if tipo else "PERSONA"

            print(f"- ID: {d.get('id')}, name: {d.get('name')}, city: {d.get('city')}, active: {d.get('active')}, "
                  f"is_person: {d.get('is_person')}, is_company: {d.get('is_company')}, is_ente: {d.get('is_ente')}, "
                  f"company_type: {d.get('company_type')}, user_id: {d.get('user_id')}, "
                  f"customer_rank: {d.get('customer_rank')}, supplier_rank: {d.get('supplier_rank')}  --> {tipo_str}")
    else:
        print("Nessun record extra trovato.")

    print("\nAnalisi completata.")

if __name__ == "__main__":
    main()
