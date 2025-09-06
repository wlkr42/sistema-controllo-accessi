#!/usr/bin/env python3
# Script per aggiungere campi profilo utente al database

import sqlite3
import sys
import os

sys.path.insert(0, '/opt/access_control/src')
from core.db_config import CURRENT_DB_PATH as DB_PATH

def update_user_profile_fields():
    """Aggiunge campi nome, cognome e avatar alla tabella utenti_sistema"""
    
    print(f"Connessione al database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verifica colonne esistenti
        cursor.execute("PRAGMA table_info(utenti_sistema)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        print(f"Colonne esistenti: {existing_columns}")
        
        # Aggiungi nuove colonne se non esistono
        new_columns = [
            ('nome', 'TEXT', ''),
            ('cognome', 'TEXT', ''),
            ('avatar_path', 'TEXT', ''),
            ('telefono', 'TEXT', ''),
            ('bio', 'TEXT', ''),
            ('data_nascita', 'DATE', None),
            ('indirizzo', 'TEXT', '')
        ]
        
        for col_name, col_type, default_value in new_columns:
            if col_name not in existing_columns:
                print(f"Aggiungendo colonna {col_name}...")
                if default_value is not None:
                    cursor.execute(f"ALTER TABLE utenti_sistema ADD COLUMN {col_name} {col_type} DEFAULT '{default_value}'")
                else:
                    cursor.execute(f"ALTER TABLE utenti_sistema ADD COLUMN {col_name} {col_type}")
                print(f"✓ Colonna {col_name} aggiunta")
            else:
                print(f"- Colonna {col_name} già esistente")
        
        # Crea directory per gli avatar se non esiste
        avatar_dir = '/opt/access_control/src/api/static/avatars'
        if not os.path.exists(avatar_dir):
            os.makedirs(avatar_dir)
            print(f"✓ Directory avatar creata: {avatar_dir}")
        
        # Copia avatar di default
        default_avatar_path = '/opt/access_control/src/api/static/img/default-avatar.png'
        if not os.path.exists(default_avatar_path):
            # Crea un avatar di default semplice (useremo un placeholder)
            os.makedirs(os.path.dirname(default_avatar_path), exist_ok=True)
            print(f"✓ Directory immagini creata")
        
        conn.commit()
        print("\n✅ Database aggiornato con successo!")
        
        # Mostra utenti attuali
        cursor.execute("SELECT username, nome, cognome, email, avatar_path FROM utenti_sistema")
        users = cursor.fetchall()
        
        print("\nUtenti nel sistema:")
        for user in users:
            nome_completo = f"{user[1] or ''} {user[2] or ''}".strip() or "Nome non impostato"
            print(f"  - {user[0]}: {nome_completo} ({user[3] or 'no email'})")
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("AGGIORNAMENTO CAMPI PROFILO UTENTE")
    print("=" * 60)
    
    if update_user_profile_fields():
        print("\n✅ Aggiornamento completato!")
    else:
        print("\n❌ Aggiornamento fallito!")
        sys.exit(1)