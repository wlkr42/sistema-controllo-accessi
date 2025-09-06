#!/usr/bin/env python3
# Test per la nuova funzionalità profilo utente

import requests
import json

BASE_URL = "http://192.168.1.236:5000"

# Login come admin
session = requests.Session()
login_response = session.post(f"{BASE_URL}/login", data={"username": "admin", "password": "admin123"})
print("✓ Login come admin")

# Test 1: Ottieni lista utenti con nuovi campi
response = session.get(f"{BASE_URL}/api/users/list")
if response.status_code == 200:
    users = response.json().get('users', [])
    print(f"\n✅ Lista utenti recuperata - {len(users)} utenti trovati")
    
    # Mostra primo utente con nuovi campi
    if users:
        user = users[0]
        print(f"\nPrimo utente: {user.get('username')}")
        print(f"  Nome: {user.get('nome') or 'Non impostato'}")
        print(f"  Cognome: {user.get('cognome') or 'Non impostato'}")
        print(f"  Avatar: {user.get('avatar_path') or 'Default'}")
        print(f"  Telefono: {user.get('telefono') or 'Non impostato'}")
        print(f"  Bio: {user.get('bio') or 'Non impostata'}")
else:
    print(f"❌ Errore nel recupero lista utenti: {response.status_code}")

# Test 2: Aggiorna profilo utente (senza avatar)
print("\n" + "="*60)
print("TEST AGGIORNAMENTO PROFILO")
print("="*60)

profile_data = {
    'username': 'wlkr42',
    'nome': 'Walter',
    'cognome': 'White',
    'email': 'walter.white@example.com',
    'telefono': '+39 333 1234567',
    'bio': 'Chimico esperto e insegnante di scienze',
    'role': 'viewer'
}

response = session.post(f"{BASE_URL}/api/users/update-profile", data=profile_data)

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        print("✅ Profilo aggiornato con successo!")
        user = data.get('user', {})
        print(f"\nDati aggiornati:")
        print(f"  Nome completo: {user.get('nome')} {user.get('cognome')}")
        print(f"  Email: {user.get('email')}")
        print(f"  Telefono: {user.get('telefono')}")
        print(f"  Bio: {user.get('bio')}")
        print(f"  Avatar: {user.get('avatar_path') or 'Default'}")
    else:
        print(f"❌ Errore: {data.get('error')}")
else:
    print(f"❌ Errore HTTP: {response.status_code}")
    print(f"   Risposta: {response.text}")

print("\n✅ Test completato!")
print("\nNOTA: Per testare l'upload avatar, usa l'interfaccia web")
print("      Vai su http://192.168.1.236:5000 e clicca su 'Modifica Profilo'")