#!/usr/bin/env python3
"""
Fix per il problema di sincronizzazione dell'utente con CF CLBMTR66S65D086I
"""
import sqlite3
import sys
import os
from pathlib import Path
import logging
import json
from datetime import datetime

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Percorso database
DB_PATH = "/opt/access_control/src/access.db"

# Codice fiscale da verificare
CODICE_FISCALE = "CLBMTR66S65D086I"

def main():
    """Funzione principale"""
    print(f"🔧 Fix problema sincronizzazione per CF: {CODICE_FISCALE}")
    
    # 1. Verifica se l'utente esiste nel database locale
    print("\n1️⃣ VERIFICA ESISTENZA NEL DATABASE LOCALE")
    exists_in_db, user_data = check_user_in_db(CODICE_FISCALE)
    
    if exists_in_db:
        print(f"✅ Utente già presente nel database locale: {user_data}")
        return
    
    # 2. Verifica se l'utente esiste nella cache
    print("\n2️⃣ VERIFICA ESISTENZA NELLA CACHE")
    exists_in_cache, cache_data = check_user_in_cache(CODICE_FISCALE)
    
    if not exists_in_cache:
        print(f"❌ Utente non trovato nella cache, impossibile procedere")
        return
    
    print(f"✅ Utente trovato nella cache: {cache_data}")
    
    # 3. Inserisci l'utente nel database
    print("\n3️⃣ INSERIMENTO UTENTE NEL DATABASE")
    insert_result = insert_user_from_cache(cache_data)
    
    if insert_result:
        print(f"✅ Utente inserito con successo nel database")
    else:
        print(f"❌ Errore durante l'inserimento dell'utente nel database")
    
    # 4. Verifica finale
    print("\n4️⃣ VERIFICA FINALE")
    exists_in_db, user_data = check_user_in_db(CODICE_FISCALE)
    
    if exists_in_db:
        print(f"✅ Utente presente nel database locale: {user_data}")
    else:
        print(f"❌ Utente NON presente nel database locale")

def check_user_in_db(codice_fiscale):
    """Verifica se l'utente esiste nel database locale"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, nome, note, attivo
                FROM utenti_autorizzati 
                WHERE codice_fiscale = ?
            ''', (codice_fiscale.upper(),))
            
            result = cursor.fetchone()
            
            if result:
                user_data = {
                    'id': result[0],
                    'nome': result[1],
                    'note': result[2],
                    'attivo': bool(result[3])
                }
                return True, user_data
            else:
                return False, None
    except Exception as e:
        print(f"❌ Errore verifica database: {e}")
        return False, None

def check_user_in_cache(codice_fiscale):
    """Verifica se l'utente esiste nella cache"""
    try:
        cache_file = Path("/opt/access_control/data/partner_cache.json")
        
        if not cache_file.exists():
            print("⚠️ File cache non trovato")
            return False, None
        
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        cittadini = cache_data.get('cittadini', [])
        
        for cittadino in cittadini:
            if cittadino.get('codice_fiscale', '').upper() == codice_fiscale.upper():
                return True, cittadino
        
        return False, None
    except Exception as e:
        print(f"❌ Errore verifica cache: {e}")
        return False, None

def insert_user_from_cache(cache_data):
    """Inserisci l'utente nel database usando i dati della cache"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO utenti_autorizzati 
                (codice_fiscale, nome, note, creato_da, modificato_da)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                cache_data.get('codice_fiscale', '').upper(),
                cache_data.get('nome', 'Utente Sconosciuto'),
                cache_data.get('note', f"Inserito manualmente {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"),
                cache_data.get('creato_da', 'FIX_SCRIPT'),
                cache_data.get('modificato_da', 'FIX_SCRIPT')
            ))
            conn.commit()
            
            # Verifica se l'inserimento è riuscito
            exists, _ = check_user_in_db(cache_data.get('codice_fiscale', ''))
            return exists
    except sqlite3.IntegrityError:
        print("⚠️ Errore integrità database (utente già esistente?)")
        return False
    except Exception as e:
        print(f"❌ Errore inserimento utente: {e}")
        return False

if __name__ == "__main__":
    main()
