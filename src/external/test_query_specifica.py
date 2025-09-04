#!/usr/bin/env python3
"""
Test query specifica a Odoo per cercare un utente
"""
import xmlrpc.client
import sys
import re
from datetime import datetime

# Configurazione
url = "https://app.calabramaceri.it"
db = "cmapp"
username = "controllo-accessi@calabramaceri.it"
password = "AcC3ss0C0ntr0l!2025#Rnd"

# Codice fiscale da cercare
codice_fiscale = "CLBMTR66S65D086I"  # Corretto: 65 invece di 05

print(f"🔍 Test query specifica per CF: {codice_fiscale}")

# Funzione di validazione CF
def validate_codice_fiscale(cf):
    """Validazione CF ROBUSTA"""
    if not cf or len(cf) != 16:
        return False
    
    # Pattern CF italiano
    pattern = r'^[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]$'
    if not re.match(pattern, cf):
        return False
    
    # Evita pattern troppo uniformi (test data)
    if len(set(cf)) < 6:
        return False
    
    return True

# Connessione
try:
    print("\n1️⃣ CONNESSIONE ODOO")
    print(f"URL: {url}")
    print(f"Database: {db}")
    print(f"Username: {username}")
    
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})

    if not uid:
        print("❌ Autenticazione fallita")
        sys.exit(1)

    print(f"✅ Connessione OK - UID: {uid}")
    
    # Oggetto per chiamate API
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    # Test validazione CF
    print(f"\n2️⃣ VALIDAZIONE CODICE FISCALE")
    print(f"Codice fiscale: {codice_fiscale}")
    print(f"Validazione: {'✅ Valido' if validate_codice_fiscale(codice_fiscale) else '❌ Non valido'}")
    
    # Ricerca esatta con CF
    print(f"\n3️⃣ RICERCA ESATTA CON CODICE FISCALE")
    print(f"Query: ('l10n_it_codice_fiscale', '=', '{codice_fiscale}')")
    
    exact_ids = models.execute_kw(
        db, uid, password,
        'res.partner', 'search',
        [[
            ('l10n_it_codice_fiscale', '=', codice_fiscale)
        ]]
    )
    
    print(f"Risultati: {len(exact_ids)}")
    
    # Ricerca con filtri completi (come in odoo_partner_connector.py)
    print(f"\n4️⃣ RICERCA CON FILTRI COMPLETI (come in odoo_partner_connector.py)")
    print("Query:")
    print("  ('city', '=', 'Rende')")
    print("  ('is_person', '=', True)")
    print("  ('is_company', '=', False)")
    print("  ('is_ente', '=', False)")
    print("  ('l10n_it_codice_fiscale', '!=', False)")
    print("  ('l10n_it_codice_fiscale', '!=', '')")
    print("  ('active', '=', True)")
    
    full_domain = [
        ('city', '=', 'Rende'),
        ('is_person', '=', True),
        ('is_company', '=', False),
        ('is_ente', '=', False),
        ('l10n_it_codice_fiscale', '!=', False),
        ('l10n_it_codice_fiscale', '!=', ''),
        ('active', '=', True)
    ]
    
    full_count = models.execute_kw(
        db, uid, password,
        'res.partner', 'search_count',
        [full_domain]
    )
    
    print(f"Totale risultati: {full_count}")
    
    # Ricerca con filtri parziali
    print(f"\n5️⃣ RICERCA CON FILTRI PARZIALI")
    print("Query:")
    print("  ('l10n_it_codice_fiscale', 'ilike', 'CLB')")
    print("  ('city', '=', 'Rende')")
    
    partial_domain = [
        ('l10n_it_codice_fiscale', 'ilike', 'CLB'),
        ('city', '=', 'Rende')
    ]
    
    partial_ids = models.execute_kw(
        db, uid, password,
        'res.partner', 'search',
        [partial_domain],
        {'limit': 10}
    )
    
    print(f"Risultati parziali: {len(partial_ids)}")
    
    if partial_ids:
        # Campi da recuperare
        fields = [
            'l10n_it_codice_fiscale',
            'name',
            'city',
            'active',
            'is_person',
            'is_company',
            'is_ente'
        ]
        
        # Recupera dati
        partial_data = models.execute_kw(
            db, uid, password,
            'res.partner', 'read',
            [partial_ids],
            {'fields': fields}
        )
        
        print("\n📋 RISULTATI RICERCA PARZIALE:")
        for partner in partial_data:
            print(f"  ID: {partner['id']}")
            print(f"  Nome: {partner.get('name', 'N/A')}")
            print(f"  CF: {partner.get('l10n_it_codice_fiscale', 'N/A')}")
            print(f"  Città: {partner.get('city', 'N/A')}")
            print(f"  Attivo: {partner.get('active', False)}")
            print(f"  Persona: {partner.get('is_person', False)}")
            print(f"  Azienda: {partner.get('is_company', False)}")
            print(f"  Ente: {partner.get('is_ente', False)}")
            print("  ---")
    
    # Ricerca con filtri alternativi
    print(f"\n6️⃣ RICERCA CON FILTRI ALTERNATIVI")
    print("Query:")
    print("  ('name', 'ilike', 'CALABRO')")
    print("  ('city', '=', 'Rende')")
    
    name_domain = [
        ('name', 'ilike', 'CALABRO'),
        ('city', '=', 'Rende')
    ]
    
    name_count = models.execute_kw(
        db, uid, password,
        'res.partner', 'search_count',
        [name_domain]
    )
    
    print(f"Risultati per nome: {name_count}")
    
    # Verifica se il CF è presente in qualsiasi città
    print(f"\n7️⃣ VERIFICA CF IN QUALSIASI CITTÀ")
    print(f"Query: ('l10n_it_codice_fiscale', '=', '{codice_fiscale}')")
    
    any_city_ids = models.execute_kw(
        db, uid, password,
        'res.partner', 'search',
        [[
            ('l10n_it_codice_fiscale', '=', codice_fiscale)
        ]]
    )
    
    if any_city_ids:
        # Recupera TUTTI i campi per analisi completa
        all_fields = [
            'name', 'l10n_it_codice_fiscale', 'city', 'active',
            'is_person', 'is_company', 'is_ente', 'street', 'email',
            'phone', 'mobile', 'create_date', 'write_date', 'id'
        ]
        
        any_city_data = models.execute_kw(
            db, uid, password,
            'res.partner', 'read',
            [any_city_ids],
            {'fields': all_fields}
        )
        
        print("\n📋 UTENTE TROVATO IN ALTRA CITTÀ (DETTAGLI COMPLETI):")
        for partner in any_city_data:
            print(f"  ID: {partner.get('id', 'N/A')}")
            print(f"  Nome: {partner.get('name', 'N/A')}")
            print(f"  CF: {partner.get('l10n_it_codice_fiscale', 'N/A')}")
            print(f"  Città: {partner.get('city', 'N/A')}")
            print(f"  Attivo: {partner.get('active', False)}")
            print(f"  Persona: {partner.get('is_person', False)}")
            print(f"  Azienda: {partner.get('is_company', False)}")
            print(f"  Ente: {partner.get('is_ente', False)}")
            print(f"  Indirizzo: {partner.get('street', 'N/A')}")
            print(f"  Email: {partner.get('email', 'N/A')}")
            print(f"  Telefono: {partner.get('phone', 'N/A')}")
            print(f"  Cellulare: {partner.get('mobile', 'N/A')}")
            print(f"  Data creazione: {partner.get('create_date', 'N/A')}")
            print(f"  Data modifica: {partner.get('write_date', 'N/A')}")
            print("  ---")
            
        # Verifica se l'utente soddisfa i filtri completi
        print("\n8️⃣ VERIFICA SE L'UTENTE SODDISFA I FILTRI COMPLETI")
        for partner in any_city_data:
            print(f"  Utente: {partner.get('name', 'N/A')}")
            print(f"  Città = 'Rende': {partner.get('city') == 'Rende'}")
            print(f"  is_person = True: {partner.get('is_person') == True}")
            print(f"  is_company = False: {partner.get('is_company') == False}")
            print(f"  is_ente = False: {partner.get('is_ente') == False}")
            print(f"  CF non vuoto: {bool(partner.get('l10n_it_codice_fiscale'))}")
            print(f"  active = True: {partner.get('active') == True}")
            
            # Verifica se soddisfa TUTTI i filtri
            soddisfa_tutti = (
                partner.get('city') == 'Rende' and
                partner.get('is_person') == True and
                partner.get('is_company') == False and
                partner.get('is_ente') == False and
                bool(partner.get('l10n_it_codice_fiscale')) and
                partner.get('active') == True
            )
            
            print(f"  SODDISFA TUTTI I FILTRI: {'✅ SÌ' if soddisfa_tutti else '❌ NO'}")
            print("  ---")
    else:
        print(f"❌ CF {codice_fiscale} non trovato in nessuna città")
    
    # Conclusione
    print("\n🔍 CONCLUSIONE ANALISI:")
    if exact_ids:
        print(f"✅ Utente con CF {codice_fiscale} trovato in Odoo")
    else:
        print(f"❌ Utente con CF {codice_fiscale} NON trovato in Odoo")
        
        if full_count > 0:
            print(f"✅ Ci sono {full_count} cittadini di Rende in Odoo")
        else:
            print(f"❌ Nessun cittadino di Rende trovato in Odoo")
    
except Exception as e:
    print(f"❌ Errore: {e}")
    sys.exit(1)
