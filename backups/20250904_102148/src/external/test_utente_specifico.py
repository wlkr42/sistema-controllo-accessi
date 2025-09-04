#!/usr/bin/env python3
"""
Test ricerca utente specifico in Odoo
"""
import xmlrpc.client
import sys

# Configurazione
url = "https://app.calabramaceri.it"
db = "cmapp"
username = "controllo-accessi@calabramaceri.it"
password = "AcC3ss0C0ntr0l!2025#Rnd"

# Codice fiscale da cercare
codice_fiscale = "CLBMTR66S05D086I"
nome_parziale = "CALABRO"  # Parte del nome da cercare

print(f"🔍 Ricerca utente con codice fiscale: {codice_fiscale}")
print(f"🔍 Ricerca alternativa con nome parziale: {nome_parziale}")

# Connessione
try:
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})

    if not uid:
        print("❌ Autenticazione fallita")
        sys.exit(1)

    print(f"✅ Connessione OK - UID: {uid}")

    # Ricerca utente specifico
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    # Ricerca con filtro codice fiscale
    user_ids = models.execute_kw(
        db, uid, password,
        'res.partner', 'search',
        [[
            ('l10n_it_codice_fiscale', '=', codice_fiscale)
        ]]
    )
    
    if not user_ids:
        print(f"❌ Utente con CF {codice_fiscale} NON trovato")
        
        # Ricerca per nome parziale
        print(f"🔍 Tentativo ricerca per nome parziale: {nome_parziale}")
        name_search_ids = models.execute_kw(
            db, uid, password,
            'res.partner', 'search',
            [[
                ('name', 'ilike', nome_parziale),
                ('city', '=', 'Rende'),
                ('is_person', '=', True),
                ('is_company', '=', False),
                ('is_ente', '=', False)
            ]]
        )
        
        if name_search_ids:
            print(f"✅ Trovati {len(name_search_ids)} utenti con nome simile a '{nome_parziale}'")
            
            # Recupera dati utenti trovati
            users_data = models.execute_kw(
                db, uid, password,
                'res.partner', 'read',
                [name_search_ids],
                {'fields': ['name', 'l10n_it_codice_fiscale', 'city', 'active']}
            )
            
            print("\n📋 UTENTI TROVATI PER NOME:")
            for user in users_data:
                print(f"  Nome: {user['name']}")
                print(f"  CF: {user.get('l10n_it_codice_fiscale', 'N/A')}")
                print(f"  Città: {user.get('city', 'N/A')}")
                print(f"  Attivo: {user.get('active', False)}")
                print("  ---")
        else:
            print(f"❌ Nessun utente trovato con nome simile a '{nome_parziale}'")
        
        # Verifica se esistono utenti con città Rende
        rende_count = models.execute_kw(
            db, uid, password,
            'res.partner', 'search_count',
            [[
                ('city', '=', 'Rende'),
                ('is_person', '=', True),
                ('is_company', '=', False),
                ('is_ente', '=', False),
                ('l10n_it_codice_fiscale', '!=', False)
            ]]
        )
        print(f"ℹ️ Cittadini Rende trovati: {rende_count}")
        
        # Ricerca per codice fiscale parziale
        print(f"🔍 Tentativo ricerca per codice fiscale parziale: CLB")
        cf_partial_ids = models.execute_kw(
            db, uid, password,
            'res.partner', 'search',
            [[
                ('l10n_it_codice_fiscale', 'ilike', 'CLB'),
                ('city', '=', 'Rende'),
                ('is_person', '=', True)
            ]],
            {'limit': 5}
        )
        
        if cf_partial_ids:
            print(f"✅ Trovati {len(cf_partial_ids)} utenti con CF che inizia con 'CLB'")
            
            # Recupera dati utenti trovati
            cf_users_data = models.execute_kw(
                db, uid, password,
                'res.partner', 'read',
                [cf_partial_ids],
                {'fields': ['name', 'l10n_it_codice_fiscale', 'city']}
            )
            
            print("\n📋 UTENTI TROVATI PER CF PARZIALE:")
            for user in cf_users_data:
                print(f"  Nome: {user['name']}")
                print(f"  CF: {user.get('l10n_it_codice_fiscale', 'N/A')}")
                print(f"  Città: {user.get('city', 'N/A')}")
                print("  ---")
        else:
            print(f"❌ Nessun utente trovato con CF che inizia con 'CLB'")
        
        sys.exit(1)
    
    # Recupera dati utente
    user_data = models.execute_kw(
        db, uid, password,
        'res.partner', 'read',
        [user_ids],
        {'fields': ['name', 'l10n_it_codice_fiscale', 'city', 'active', 'is_person', 'is_company']}
    )
    
    print("\n✅ UTENTE TROVATO:")
    for field in user_data[0]:
        print(f"  {field}: {user_data[0][field]}")
    
except Exception as e:
    print(f"❌ Errore: {e}")
    sys.exit(1)
