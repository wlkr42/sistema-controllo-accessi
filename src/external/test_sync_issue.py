#!/usr/bin/env python3
"""
Test per verificare il problema di sincronizzazione dell'utente con CF CLBMTR66S65D086I
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

# Percorso database - importato dalla configurazione centralizzata
sys.path.insert(0, '/opt/access_control/src')
from core.db_config import CURRENT_DB_PATH as DB_PATH

# Codice fiscale da verificare
CODICE_FISCALE = "CLBMTR66S65D086I"

def main():
    """Funzione principale"""
    print(f"🔍 Test problema sincronizzazione per CF: {CODICE_FISCALE}")
    
    # 1. Verifica se l'utente esiste nel database locale
    print("\n1️⃣ VERIFICA ESISTENZA NEL DATABASE LOCALE")
    exists_in_db, user_data = check_user_in_db(CODICE_FISCALE)
    
    if exists_in_db:
        print(f"✅ Utente trovato nel database locale: {user_data}")
    else:
        print(f"❌ Utente NON trovato nel database locale")
    
    # 2. Verifica se l'utente esiste nella cache
    print("\n2️⃣ VERIFICA ESISTENZA NELLA CACHE")
    exists_in_cache, cache_data = check_user_in_cache(CODICE_FISCALE)
    
    if exists_in_cache:
        print(f"✅ Utente trovato nella cache: {cache_data}")
    else:
        print(f"❌ Utente NON trovato nella cache")
    
    # 3. Verifica se verify_access restituisce il risultato corretto
    print("\n3️⃣ TEST VERIFY_ACCESS")
    verify_result, verify_data = test_verify_access(CODICE_FISCALE)
    
    if verify_result:
        print(f"✅ verify_access restituisce True: {verify_data}")
    else:
        print(f"❌ verify_access restituisce False")
        
    # 4. Verifica se verifica_orario() restituisce True
    print("\n4️⃣ TEST VERIFICA_ORARIO")
    orario_result = test_verifica_orario()
    
    if orario_result:
        print(f"✅ verifica_orario restituisce True")
    else:
        print(f"❌ verifica_orario restituisce False - QUESTO BLOCCA LA SINCRONIZZAZIONE!")
    
    # 5. Verifica se verifica_limite_mensile() restituisce True
    print("\n5️⃣ TEST VERIFICA_LIMITE_MENSILE")
    limite_result = test_verifica_limite_mensile(CODICE_FISCALE)
    
    if limite_result:
        print(f"✅ verifica_limite_mensile restituisce True")
    else:
        print(f"❌ verifica_limite_mensile restituisce False - QUESTO BLOCCA LA SINCRONIZZAZIONE!")
    
    # 6. Test inserimento manuale
    print("\n6️⃣ TEST INSERIMENTO MANUALE")
    insert_result = test_insert_user(CODICE_FISCALE)
    
    if insert_result:
        print(f"✅ Inserimento manuale riuscito")
    else:
        print(f"❌ Inserimento manuale fallito")
    
    # Conclusione
    print("\n🔍 CONCLUSIONE ANALISI:")
    if not exists_in_db:
        if not orario_result:
            print("❌ PROBLEMA: verifica_orario() restituisce False, bloccando la sincronizzazione")
            print("   Soluzione: Modificare gli orari di accesso o bypassare la verifica durante la sincronizzazione")
        elif not limite_result:
            print("❌ PROBLEMA: verifica_limite_mensile() restituisce False, bloccando la sincronizzazione")
            print("   Soluzione: Aumentare il limite mensile o bypassare la verifica durante la sincronizzazione")
        elif not exists_in_cache:
            print("❌ PROBLEMA: L'utente non è presente nella cache")
            print("   Soluzione: Aggiornare la cache o forzare il recupero da Odoo")
        else:
            print("❌ PROBLEMA: Causa non identificata")
            print("   Soluzione: Verificare i log di sistema per ulteriori dettagli")
    else:
        print("✅ L'utente è presente nel database locale")

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

def test_verify_access(codice_fiscale):
    """Test del metodo verify_access"""
    try:
        # Importa il modulo database_manager
        sys.path.append("/opt/access_control")
        from src.database.database_manager import DatabaseManager
        
        # Crea un'istanza di DatabaseManager
        db_manager = DatabaseManager(DB_PATH)
        
        # Chiama verify_access
        result, user_data = db_manager.verify_access(codice_fiscale)
        
        return result, user_data
    except Exception as e:
        print(f"❌ Errore test verify_access: {e}")
        return False, None

def test_verifica_orario():
    """Test del metodo verifica_orario"""
    try:
        # Importa il modulo configurazione_accessi
        sys.path.append("/opt/access_control")
        from src.api.modules.configurazione_accessi import verifica_orario
        
        # Chiama verifica_orario
        result = verifica_orario()
        
        return result
    except Exception as e:
        print(f"❌ Errore test verifica_orario: {e}")
        return False

def test_verifica_limite_mensile(codice_fiscale):
    """Test del metodo verifica_limite_mensile"""
    try:
        # Importa il modulo configurazione_accessi
        sys.path.append("/opt/access_control")
        from src.api.modules.configurazione_accessi import verifica_limite_mensile
        
        # Chiama verifica_limite_mensile
        result = verifica_limite_mensile(codice_fiscale)
        
        return result
    except Exception as e:
        print(f"❌ Errore test verifica_limite_mensile: {e}")
        return False

def test_insert_user(codice_fiscale):
    """Test inserimento manuale utente"""
    try:
        # Verifica se l'utente esiste già
        exists, _ = check_user_in_db(codice_fiscale)
        
        if exists:
            print("⚠️ Utente già presente nel database")
            return True
        
        # Inserisci l'utente manualmente
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO utenti_autorizzati 
                (codice_fiscale, nome, note, creato_da, modificato_da)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                codice_fiscale.upper(),
                "Mariateresa Celebre Test Rende",
                f"Inserito manualmente {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "TEST_SCRIPT",
                "TEST_SCRIPT"
            ))
            conn.commit()
            
            # Verifica se l'inserimento è riuscito
            exists, _ = check_user_in_db(codice_fiscale)
            return exists
    except sqlite3.IntegrityError:
        print("⚠️ Errore integrità database (utente già esistente?)")
        return False
    except Exception as e:
        print(f"❌ Errore inserimento manuale: {e}")
        return False

if __name__ == "__main__":
    main()
