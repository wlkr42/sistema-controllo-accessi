#!/usr/bin/env python3
# Test validazione password rigorosa

import requests
import json

BASE_URL = "http://192.168.1.236:5000"

# Login
session = requests.Session()
login_response = session.post(f"{BASE_URL}/login", data={"username": "admin", "password": "admin123"})
print("✓ Login come admin")

# Test cases per password
test_cases = [
    {
        "password": "abc",
        "should_fail": True,
        "reason": "Troppo corta"
    },
    {
        "password": "abcdefgh",
        "should_fail": True,
        "reason": "Solo minuscole, no numeri, no speciali"
    },
    {
        "password": "Abcdefgh",
        "should_fail": True,
        "reason": "No numeri, no speciali"
    },
    {
        "password": "Abcdefg1",
        "should_fail": True,
        "reason": "No caratteri speciali"
    },
    {
        "password": "abcdefg1!",
        "should_fail": True,
        "reason": "No maiuscole"
    },
    {
        "password": "ABCDEFG1!",
        "should_fail": True,
        "reason": "No minuscole"
    },
    {
        "password": "Abc def1!",
        "should_fail": True,
        "reason": "Contiene spazi"
    },
    {
        "password": "Password123!",
        "should_fail": True,
        "reason": "Password troppo comune"
    },
    {
        "password": "ValidPass123!",
        "should_fail": False,
        "reason": "Password valida"
    },
    {
        "password": "S3cur3P@ssw0rd",
        "should_fail": False,
        "reason": "Password valida complessa"
    }
]

print("\n" + "="*60)
print("TEST VALIDAZIONE PASSWORD")
print("="*60)

for i, test in enumerate(test_cases, 1):
    print(f"\nTest {i}: {test['reason']}")
    print(f"Password: '{test['password']}'")
    
    response = session.post(
        f"{BASE_URL}/api/users/admin-set-password",
        json={
            "username": "wlkr42",
            "password": test['password'],
            "must_change_password": True
        }
    )
    
    data = response.json()
    
    if test['should_fail']:
        if response.status_code != 200:
            print(f"✅ CORRETTO: Rifiutata come previsto")
            if data.get('details'):
                print(f"   Dettagli: {', '.join(data['details'])}")
        else:
            print(f"❌ ERRORE: Dovrebbe essere rifiutata ma è stata accettata!")
    else:
        if response.status_code == 200:
            print(f"✅ CORRETTO: Accettata come previsto")
        else:
            print(f"❌ ERRORE: Dovrebbe essere accettata ma è stata rifiutata!")
            if data.get('details'):
                print(f"   Dettagli: {', '.join(data['details'])}")

print("\n" + "="*60)
print("TEST COMPLETATO")
print("="*60)