#!/usr/bin/env python3
# File: /opt/access_control/scripts/check_database_users.py
# Script per verificare utenti nel database locale

import sys
import sqlite3
from pathlib import Path

def check_database():
    """Verifica utenti nel database locale"""
    
    db_path = "/opt/access_control/src/access.db"
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            print("🗄️ VERIFICA DATABASE LOCALE")
            print("=" * 50)
            
            # Conta utenti totali
            cursor.execute("SELECT COUNT(*) FROM utenti_autorizzati")
            total_users = cursor.fetchone()[0]
            
            # Conta utenti attivi
            cursor.execute("SELECT COUNT(*) FROM utenti_autorizzati WHERE attivo = 1")
            active_users = cursor.fetchone()[0]
            
            print(f"👥 Utenti totali: {total_users}")
            print(f"✅ Utenti attivi: {active_users}")
            
            # Lista utenti con dettagli
            print(f"\n📋 LISTA UTENTI AUTORIZZATI:")
            print("-" * 50)
            
            cursor.execute("""
                SELECT codice_fiscale, nome, cognome, reparto, ruolo, note, creato_da
                FROM utenti_autorizzati 
                WHERE attivo = 1
                ORDER BY cognome, nome
            """)
            
            users = cursor.fetchall()
            
            if users:
                for i, user in enumerate(users, 1):
                    cf, nome, cognome, reparto, ruolo, note, creato_da = user
                    print(f"{i:2d}. {nome} {cognome}")
                    print(f"    CF: {cf}")
                    print(f"    Ruolo: {ruolo}")
                    print(f"    Fonte: {creato_da}")
                    if note:
                        print(f"    Note: {note}")
                    print()
            else:
                print("❌ NESSUN UTENTE AUTORIZZATO!")
                print("⚠️ Database contiene solo dati di test o è vuoto")
            
            # Verifica log accessi
            print("📊 LOG ACCESSI RECENTI:")
            print("-" * 50)
            
            cursor.execute("""
                SELECT timestamp, codice_fiscale, autorizzato
                FROM log_accessi 
                ORDER BY timestamp DESC 
                LIMIT 5
            """)
            
            logs = cursor.fetchall()
            for log in logs:
                timestamp, cf, authorized = log
                status = "✅ AUTORIZZATO" if authorized else "❌ NEGATO"
                masked_cf = f"{cf[:4]}***{cf[-4:]}"
                print(f"{timestamp} - {masked_cf} - {status}")
            
            # Raccomandazioni
            print(f"\n💡 RACCOMANDAZIONI:")
            if active_users == 0:
                print("🔄 Eseguire sincronizzazione Odoo per popolare database")
                print("🔧 Fix errore connessione Odoo (timeout parameter)")
            elif active_users < 1000:
                print("⚠️ Pochi utenti nel database - verificare sync Odoo")
            else:
                print("✅ Database ben popolato")
            
    except Exception as e:
        print(f"❌ Errore accesso database: {e}")

if __name__ == "__main__":
    check_database()