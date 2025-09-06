#!/usr/bin/env python3
# Test creazione utente con campi profilo

import requests
import json

BASE_URL = "http://192.168.1.236:5000"

# Login come admin
session = requests.Session()
login_response = session.post(f"{BASE_URL}/login", data={"username": "admin", "password": "admin123"})
print("✓ Login come admin")

# Crea nuovo utente con tutti i campi profilo
new_user = {
    "username": "luigi_bianchi",
    "nome": "Luigi",
    "cognome": "Bianchi",
    "email": "luigi.bianchi@example.com",
    "password": "SecurePass123!",
    "role": "viewer"
}

print("\n" + "="*60)
print("CREAZIONE NUOVO UTENTE CON PROFILO")
print("="*60)

response = session.post(f"{BASE_URL}/api/users/create", 
                        headers={'Content-Type': 'application/json'},
                        json=new_user)

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        print(f"✅ Utente '{new_user['username']}' creato con successo!")
        print(f"   Nome: {new_user['nome']} {new_user['cognome']}")
        print(f"   Email: {new_user['email']}")
        print(f"   Ruolo: {new_user['role']}")
    else:
        print(f"❌ Errore: {data.get('error')}")
else:
    print(f"❌ Errore HTTP: {response.status_code}")

# Verifica che l'utente sia stato creato con i campi profilo
print("\n" + "="*60)
print("VERIFICA UTENTE CREATO")
print("="*60)

response = session.get(f"{BASE_URL}/api/users/list")
if response.status_code == 200:
    users = response.json().get('users', [])
    luigi = next((u for u in users if u['username'] == 'luigi_bianchi'), None)
    
    if luigi:
        print(f"✅ Utente trovato nella lista!")
        print(f"   Username: {luigi['username']}")
        print(f"   Nome: {luigi.get('nome') or 'Non impostato'}")
        print(f"   Cognome: {luigi.get('cognome') or 'Non impostato'}")
        print(f"   Email: {luigi.get('email') or 'Non impostata'}")
        print(f"   Ruolo: {luigi.get('role_name')}")
    else:
        print("❌ Utente non trovato nella lista")
else:
    print(f"❌ Errore nel recupero lista: {response.status_code}")

print("\n✅ Test completato!")