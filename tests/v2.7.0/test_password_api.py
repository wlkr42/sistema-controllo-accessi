#!/usr/bin/env python3
# Test diretto dell'API di cambio password

import requests
import json

# URL base
BASE_URL = "http://192.168.1.236:5000"

# Step 1: Login
print("1. Login come admin...")
login_data = {
    "username": "admin",
    "password": "admin123"
}

session = requests.Session()
response = session.post(f"{BASE_URL}/login", data=login_data)
if response.status_code == 200 or response.status_code == 302:
    print("✓ Login riuscito")
else:
    print(f"✗ Login fallito: {response.status_code}")
    print(response.text[:200])
    exit(1)

# Step 2: Test cambio password
print("\n2. Test cambio password per wlkr42...")
password_data = {
    "username": "wlkr42",
    "password": "NuovaPassword123!",
    "must_change_password": True
}

response = session.post(
    f"{BASE_URL}/api/users/admin-set-password",
    json=password_data,
    headers={"Content-Type": "application/json"}
)

print(f"Status Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")

if response.status_code == 200:
    try:
        data = response.json()
        print("✓ Risposta JSON ricevuta:")
        print(json.dumps(data, indent=2))
    except:
        print("✗ Errore parsing JSON:")
        print(response.text[:500])
else:
    print(f"✗ Errore {response.status_code}:")
    print(response.text[:500])

# Step 3: Verifica lista utenti
print("\n3. Verifica lista utenti...")
response = session.get(f"{BASE_URL}/api/users/list")
if response.status_code == 200:
    users = response.json()
    if users.get('success'):
        print("✓ Lista utenti recuperata")
        for user in users.get('users', []):
            if user['username'] == 'wlkr42':
                print(f"  - wlkr42: email={user.get('email')}, must_change={user.get('must_change_password')}")
else:
    print(f"✗ Errore recupero utenti: {response.status_code}")