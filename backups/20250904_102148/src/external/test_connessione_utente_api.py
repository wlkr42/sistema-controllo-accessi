# Test rapido connessione
import xmlrpc.client

url = "https://app.calabramaceri.it"
db = "cmapp"
username = "controllo-accessi@calabramaceri.it"  # CORRETTO
password = "AcC3ss0C0ntr0l!2025#Rnd"

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if uid:
    print(f"✅ Connessione OK - UID: {uid}")
    
    # Test filtri corretti
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    count = models.execute_kw(
        db, uid, password,
        'res.partner', 'search_count',
        [[
            ('city', '=', 'Rende'),
            ('is_person', '=', True),
            ('is_company', '=', False),
            ('is_ente', '=', False),  # AGGIUNTO
            ('l10n_it_codice_fiscale', '!=', False)
        ]]
    )
    print(f"✅ Cittadini Rende (filtri corretti): {count}")
else:
    print("❌ Autenticazione fallita")