#!/usr/bin/env python3
# Script per inizializzare le tabelle di gestione password

import sqlite3
import sys
import os

# Aggiungi il percorso per gli import
sys.path.insert(0, '/opt/access_control/src')
from core.db_config import CURRENT_DB_PATH as DB_PATH

def init_password_tables():
    """Inizializza tutte le tabelle necessarie per la gestione password"""
    
    print(f"Connessione al database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Crea tabella password_reset_tokens
        print("Creando tabella password_reset_tokens...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at DATETIME NOT NULL,
                used BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                used_at DATETIME,
                ip_address TEXT
            )
        ''')
        print("✓ Tabella password_reset_tokens creata")
        
        # 2. Crea tabella password_history
        print("Creando tabella password_history...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                changed_by TEXT,
                reason TEXT
            )
        ''')
        print("✓ Tabella password_history creata")
        
        # 3. Crea tabella password_policies
        print("Creando tabella password_policies...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_policies (
                id INTEGER PRIMARY KEY,
                min_length INTEGER DEFAULT 8,
                require_uppercase BOOLEAN DEFAULT 1,
                require_lowercase BOOLEAN DEFAULT 1,
                require_numbers BOOLEAN DEFAULT 1,
                require_special BOOLEAN DEFAULT 1,
                max_age_days INTEGER DEFAULT 90,
                min_age_hours INTEGER DEFAULT 24,
                history_count INTEGER DEFAULT 5,
                max_attempts INTEGER DEFAULT 5,
                lockout_minutes INTEGER DEFAULT 30,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_by TEXT
            )
        ''')
        print("✓ Tabella password_policies creata")
        
        # 4. Inserisci policy default se non esistono
        cursor.execute('SELECT COUNT(*) FROM password_policies')
        if cursor.fetchone()[0] == 0:
            print("Inserendo policy password di default...")
            cursor.execute('''
                INSERT INTO password_policies (
                    id, min_length, require_uppercase, require_lowercase,
                    require_numbers, require_special, max_age_days,
                    min_age_hours, history_count, max_attempts, lockout_minutes
                ) VALUES (1, 8, 1, 1, 1, 1, 90, 24, 5, 5, 30)
            ''')
            print("✓ Policy password di default inserite")
        
        # 5. Aggiungi colonne mancanti a utenti_sistema
        print("Verificando colonne utenti_sistema...")
        cursor.execute("PRAGMA table_info(utenti_sistema)")
        columns = [col[1] for col in cursor.fetchall()]
        
        columns_to_add = [
            ('email', 'TEXT'),
            ('password_changed_at', 'DATETIME'),
            ('password_expires_at', 'DATETIME'),
            ('failed_attempts', 'INTEGER DEFAULT 0'),
            ('locked_until', 'DATETIME'),
            ('must_change_password', 'BOOLEAN DEFAULT 0')
        ]
        
        for col_name, col_type in columns_to_add:
            if col_name not in columns:
                print(f"Aggiungendo colonna {col_name}...")
                cursor.execute(f'ALTER TABLE utenti_sistema ADD COLUMN {col_name} {col_type}')
                print(f"✓ Colonna {col_name} aggiunta")
        
        # 6. Crea tabella eventi_sistema se non esiste
        print("Verificando tabella eventi_sistema...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS eventi_sistema (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_evento TEXT NOT NULL,
                livello TEXT NOT NULL,
                messaggio TEXT,
                componente TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✓ Tabella eventi_sistema verificata")
        
        conn.commit()
        print("\n✅ TUTTE LE TABELLE SONO STATE INIZIALIZZATE CON SUCCESSO!")
        
        # Mostra statistiche
        cursor.execute("SELECT COUNT(*) FROM utenti_sistema")
        n_users = cursor.fetchone()[0]
        print(f"\nStatistiche database:")
        print(f"- Utenti sistema: {n_users}")
        
        cursor.execute("SELECT username, role, email FROM utenti_sistema ORDER BY username")
        users = cursor.fetchall()
        print("\nUtenti esistenti:")
        for user in users:
            email_status = user[2] if user[2] else "no email"
            print(f"  - {user[0]} ({user[1]}) - {email_status}")
        
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("INIZIALIZZAZIONE TABELLE GESTIONE PASSWORD")
    print("=" * 60)
    
    success = init_password_tables()
    
    if success:
        print("\n✅ Inizializzazione completata!")
        print("\nOra puoi riavviare il servizio con:")
        print("  sudo systemctl restart access-control-web")
    else:
        print("\n❌ Inizializzazione fallita!")
        sys.exit(1)