#!/usr/bin/env python3
"""
Script per creare database pulito con solo la struttura e gli utenti di sistema di default
Per il Sistema di Controllo Accessi
"""

import sqlite3
import os
import sys
from pathlib import Path

def create_clean_database(db_path: str):
    """Crea un database pulito con solo struttura e utenti default"""
    
    print(f"🗄️  Creazione database pulito: {db_path}")
    
    # Assicura che la directory esista
    db_dir = Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    
    # Rimuovi database esistente se presente
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"   Database esistente rimosso")
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            print("   Creazione struttura database...")
            
            # Abilita foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # === TABELLE PRINCIPALI ===
            
            # Tabella utenti sistema (login dashboard)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS "utenti_sistema" (
                    username TEXT PRIMARY KEY, 
                    password TEXT NOT NULL, 
                    role TEXT NOT NULL, 
                    attivo INTEGER DEFAULT 1, 
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                    created_by TEXT, 
                    modified_at TIMESTAMP, 
                    modified_by TEXT, 
                    last_login TIMESTAMP
                )
            ''')
            
            # Tabella utenti autorizzati (accesso fisico)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS "utenti_autorizzati" (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codice_fiscale TEXT UNIQUE NOT NULL,
                    nome TEXT,
                    data_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_aggiornamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    attivo BOOLEAN DEFAULT 1,
                    note TEXT,
                    creato_da TEXT,
                    modificato_da TEXT
                )
            ''')
            
            # Tabella backup utenti autorizzati
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS "utenti_autorizzati_backup" (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codice_fiscale TEXT UNIQUE NOT NULL,
                    nome TEXT,
                    cognome TEXT,
                    email TEXT,
                    telefono TEXT,
                    reparto TEXT,
                    ruolo TEXT,
                    data_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_aggiornamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_scadenza DATE,
                    attivo BOOLEAN DEFAULT 1,
                    note TEXT,
                    creato_da TEXT,
                    modificato_da TEXT
                )
            ''')
            
            # Log accessi
            cursor.execute('''
                CREATE TABLE log_accessi (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    codice_fiscale TEXT NOT NULL,
                    autorizzato BOOLEAN NOT NULL,
                    durata_elaborazione REAL,
                    ip_client TEXT,
                    user_agent TEXT,
                    terminale_id TEXT,
                    errore TEXT,
                    metodo_lettura TEXT,
                    qualita_lettura INTEGER,
                    sincronizzato BOOLEAN DEFAULT 0,
                    data_sincronizzazione TIMESTAMP,
                    note TEXT,
                    tipo_accesso TEXT
                )
            ''')
            
            # Configurazioni sistema
            cursor.execute('''
                CREATE TABLE configurazioni (
                    chiave TEXT PRIMARY KEY,
                    valore TEXT NOT NULL,
                    tipo TEXT DEFAULT 'string',
                    descrizione TEXT,
                    categoria TEXT,
                    modificabile BOOLEAN DEFAULT 1,
                    data_modifica TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    modificato_da TEXT
                )
            ''')
            
            # Eventi sistema
            cursor.execute('''
                CREATE TABLE eventi_sistema (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tipo_evento TEXT NOT NULL,
                    livello TEXT DEFAULT 'INFO',
                    messaggio TEXT NOT NULL,
                    dettagli TEXT,
                    componente TEXT,
                    risolto BOOLEAN DEFAULT 0
                )
            ''')
            
            # Statistiche
            cursor.execute('''
                CREATE TABLE statistiche (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data DATE NOT NULL,
                    totale_accessi INTEGER DEFAULT 0,
                    accessi_autorizzati INTEGER DEFAULT 0,
                    accessi_negati INTEGER DEFAULT 0,
                    tempo_medio_elaborazione REAL,
                    uptime_sistema REAL,
                    errori_hardware INTEGER DEFAULT 0,
                    UNIQUE(data)
                )
            ''')
            
            # System settings
            cursor.execute('''
                CREATE TABLE system_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # === TABELLE CONFIGURAZIONI ===
            
            # Configurazione accessi
            cursor.execute('''
                CREATE TABLE configurazione_accessi (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ora_apertura TIME NOT NULL,
                    ora_chiusura TIME NOT NULL,
                    max_ingressi_mensili INTEGER NOT NULL DEFAULT 10,
                    modificato_da TEXT,
                    data_modifica TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Orari settimanali
            cursor.execute('''
                CREATE TABLE orari_settimanali (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    giorno INTEGER NOT NULL CHECK (giorno BETWEEN 0 AND 6),
                    mattina_apertura TIME,
                    mattina_chiusura TIME,
                    pomeriggio_apertura TIME,
                    pomeriggio_chiusura TIME,
                    isola_aperta BOOLEAN DEFAULT 1,
                    modificato_da TEXT,
                    data_modifica TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(giorno)
                )
            ''')
            
            # Orari accesso
            cursor.execute('''
                CREATE TABLE orari_accesso (
                    giorno TEXT PRIMARY KEY,
                    aperto BOOLEAN DEFAULT true,
                    mattina_inizio TIME,
                    mattina_fine TIME,
                    pomeriggio_inizio TIME,
                    pomeriggio_fine TIME,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_by TEXT
                )
            ''')
            
            # Limiti utenti
            cursor.execute('''
                CREATE TABLE limiti_utenti (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codice_fiscale TEXT NOT NULL,
                    max_ingressi_mensili INTEGER NOT NULL DEFAULT 10,
                    modificato_da TEXT,
                    data_modifica TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(codice_fiscale)
                )
            ''')
            
            # Limiti accesso
            cursor.execute('''
                CREATE TABLE limiti_accesso (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    max_ingressi_mensili INTEGER DEFAULT 3,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_by TEXT
                )
            ''')
            
            # Conteggio ingressi mensili
            cursor.execute('''
                CREATE TABLE conteggio_ingressi_mensili (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codice_fiscale TEXT NOT NULL,
                    mese INTEGER NOT NULL,
                    anno INTEGER NOT NULL,
                    numero_ingressi INTEGER DEFAULT 0,
                    ultimo_ingresso TIMESTAMP,
                    UNIQUE(codice_fiscale, mese, anno)
                )
            ''')
            
            # Conteggio ingressi mensili archive
            cursor.execute('''
                CREATE TABLE conteggio_ingressi_mensili_archive (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codice_fiscale TEXT NOT NULL,
                    mese INTEGER NOT NULL,
                    anno INTEGER NOT NULL,
                    numero_ingressi INTEGER,
                    ultimo_ingresso TIMESTAMP,
                    data_archiviazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Log forzature
            cursor.execute('''
                CREATE TABLE log_forzature (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL,
                    utente TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    dettagli TEXT
                )
            ''')
            
            # === INDICI ===
            print("   Creazione indici...")
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cf ON "utenti_autorizzati_backup"(codice_fiscale)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cf_attivo ON "utenti_autorizzati_backup"(codice_fiscale, attivo)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_log_timestamp ON log_accessi(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_log_sync ON log_accessi(sincronizzato)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_log_cf ON log_accessi(codice_fiscale)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_eventi_timestamp ON eventi_sistema(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_statistiche_data ON statistiche(data)')
            
            # === TRIGGER ===
            print("   Creazione trigger...")
            
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS update_utente_timestamp 
                AFTER UPDATE ON "utenti_autorizzati_backup"
                FOR EACH ROW
                BEGIN
                    UPDATE "utenti_autorizzati_backup" 
                    SET data_aggiornamento = CURRENT_TIMESTAMP 
                    WHERE id = NEW.id;
                END
            ''')
            
            # === VISTE ===
            print("   Creazione viste...")
            
            cursor.execute('''
                CREATE VIEW IF NOT EXISTS authorized_people AS 
                SELECT 
                    codice_fiscale,
                    nome,
                    cognome,
                    nome || ' ' || cognome as name,
                    email,
                    telefono as phone,
                    attivo as active,
                    data_inserimento as created_at
                FROM "utenti_autorizzati_backup"
            ''')
            
            cursor.execute('''
                CREATE VIEW IF NOT EXISTS access_log AS
                SELECT 
                    id,
                    timestamp,
                    codice_fiscale,
                    autorizzato as authorized,
                    durata_elaborazione as processing_time,
                    errore as error_message,
                    terminale_id as terminal_id
                FROM log_accessi
            ''')
            
            # === DATI DI DEFAULT ===
            print("   Inserimento utenti sistema di default...")
            
            # Utenti sistema di default (password già hashate)
            default_users = [
                ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin', 1, 'CURRENT_TIMESTAMP', 'system'),
                ('manager', '866485796cfa8d7c0cf7111640205b83076433547577511d81f8030ae99ecea5', 'user_manager', 1, 'CURRENT_TIMESTAMP', 'system'),
                ('viewer', '65375049b9e4d7cad6c9ba286fdeb9394b28135a3e84136404cfccfdcc438894', 'viewer', 1, 'CURRENT_TIMESTAMP', 'system')
            ]
            
            for username, password_hash, role, attivo, created_at, created_by in default_users:
                cursor.execute('''
                    INSERT OR REPLACE INTO utenti_sistema 
                    (username, password, role, attivo, created_at, created_by, modified_at, modified_by)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?, CURRENT_TIMESTAMP, ?)
                ''', (username, password_hash, role, attivo, created_by, created_by))
                print(f"   ✅ Utente {username} ({role})")
            
            # Configurazioni di default
            cursor.execute('''
                INSERT OR REPLACE INTO limiti_accesso (max_ingressi_mensili, updated_by)
                VALUES (3, 'system')
            ''')
            
            # Evento di inizializzazione
            cursor.execute('''
                INSERT INTO eventi_sistema (tipo_evento, livello, messaggio, componente)
                VALUES ('INIT', 'INFO', 'Database inizializzato con struttura pulita', 'SYSTEM')
            ''')
            
            conn.commit()
            print("   ✅ Database creato con successo")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Errore creazione database: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Uso: python3 create_clean_database.py <percorso_database>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    success = create_clean_database(db_path)
    
    if success:
        print("🎉 Database pulito creato con successo!")
        print(f"📍 Percorso: {db_path}")
        print("👥 Utenti di default:")
        print("   - admin/admin123 (Amministratore)")
        print("   - manager/manager123 (Gestore Utenti e Orari)")
        print("   - viewer/viewer123 (Visualizzatore)")
    else:
        print("❌ Errore nella creazione del database")
        sys.exit(1)

if __name__ == "__main__":
    main()
