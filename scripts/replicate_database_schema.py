#!/usr/bin/env python3
"""
Replica ESATTAMENTE lo schema del database dal sistema locale
"""

import sqlite3
import sys
import os

def get_exact_schema():
    """Ottiene lo schema ESATTO dal database locale"""
    
    # Schema ESATTO copiato dal sistema locale funzionante
    schema = """
    -- Tabella utenti_autorizzati CON LA COLONNA NOTE
    CREATE TABLE IF NOT EXISTS utenti_autorizzati (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codice_fiscale TEXT UNIQUE NOT NULL,
        nome TEXT,
        data_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_aggiornamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        attivo BOOLEAN DEFAULT 1,
        note TEXT,
        creato_da TEXT,
        modificato_da TEXT
    );
    
    CREATE INDEX IF NOT EXISTS idx_cf ON utenti_autorizzati(codice_fiscale);
    CREATE INDEX IF NOT EXISTS idx_cf_attivo ON utenti_autorizzati(codice_fiscale, attivo);
    
    CREATE TRIGGER IF NOT EXISTS update_utente_timestamp 
        AFTER UPDATE ON utenti_autorizzati
        FOR EACH ROW
        BEGIN
            UPDATE utenti_autorizzati 
            SET data_aggiornamento = CURRENT_TIMESTAMP 
            WHERE id = NEW.id;
        END;
    
    -- Tabella log_accessi
    CREATE TABLE IF NOT EXISTS log_accessi (
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
        tipo_accesso TEXT,
        motivo_rifiuto TEXT,
        nome_utente TEXT
    );
    
    CREATE INDEX IF NOT EXISTS idx_log_timestamp ON log_accessi(timestamp);
    CREATE INDEX IF NOT EXISTS idx_log_sync ON log_accessi(sincronizzato);
    CREATE INDEX IF NOT EXISTS idx_log_cf ON log_accessi(codice_fiscale);
    
    -- Tabella system_settings
    CREATE TABLE IF NOT EXISTS system_settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Tabella utenti_sistema
    CREATE TABLE IF NOT EXISTS utenti_sistema (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        attivo INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by TEXT,
        modified_at TIMESTAMP,
        modified_by TEXT,
        last_login TIMESTAMP,
        email TEXT,
        password_changed_at DATETIME,
        password_expires_at DATETIME,
        failed_attempts INTEGER DEFAULT 0,
        locked_until DATETIME,
        must_change_password BOOLEAN DEFAULT 0,
        nome TEXT DEFAULT '',
        cognome TEXT DEFAULT '',
        avatar_path TEXT DEFAULT '',
        telefono TEXT DEFAULT '',
        bio TEXT DEFAULT '',
        data_nascita DATE,
        indirizzo TEXT DEFAULT ''
    );
    
    -- Tabella orari_accesso CON COLONNA GIORNO
    CREATE TABLE IF NOT EXISTS orari_accesso (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        giorno INTEGER DEFAULT 1,
        ora_inizio TEXT,
        ora_fine TEXT,
        attivo BOOLEAN DEFAULT 1,
        descrizione TEXT
    );
    
    -- Tabella configurazioni
    CREATE TABLE IF NOT EXISTS configurazioni (
        chiave TEXT PRIMARY KEY,
        valore TEXT NOT NULL,
        tipo TEXT DEFAULT 'string',
        descrizione TEXT,
        categoria TEXT,
        modificabile BOOLEAN DEFAULT 1,
        data_modifica TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        modificato_da TEXT
    );
    
    -- Tabella eventi_sistema
    CREATE TABLE IF NOT EXISTS eventi_sistema (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        tipo_evento TEXT NOT NULL,
        livello TEXT DEFAULT 'INFO',
        messaggio TEXT NOT NULL,
        dettagli TEXT,
        componente TEXT,
        risolto BOOLEAN DEFAULT 0
    );
    
    CREATE INDEX IF NOT EXISTS idx_eventi_timestamp ON eventi_sistema(timestamp);
    
    -- Tabella conteggio_ingressi_mensili
    CREATE TABLE IF NOT EXISTS conteggio_ingressi_mensili (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codice_fiscale TEXT NOT NULL,
        mese INTEGER NOT NULL,
        anno INTEGER NOT NULL,
        numero_ingressi INTEGER DEFAULT 0,
        ultimo_ingresso TIMESTAMP,
        UNIQUE(codice_fiscale, mese, anno)
    );
    
    -- Altre tabelle necessarie
    CREATE TABLE IF NOT EXISTS relay_config (
        relay_number INTEGER PRIMARY KEY CHECK (relay_number BETWEEN 1 AND 8),
        description TEXT NOT NULL,
        valid_action TEXT CHECK (valid_action IN ('OFF', 'ON', 'PULSE')),
        valid_duration REAL DEFAULT 0,
        invalid_action TEXT CHECK (invalid_action IN ('OFF', 'ON', 'PULSE')),
        invalid_duration REAL DEFAULT 0
    );
    
    CREATE TABLE IF NOT EXISTS fascie_orarie (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        giorno_settimana INTEGER,
        ora_inizio TEXT,
        ora_fine TEXT,
        attivo BOOLEAN DEFAULT 1,
        descrizione TEXT
    );
    """
    
    return schema

def fix_database(db_path):
    """Applica lo schema esatto al database"""
    
    print(f"🔧 FIX DATABASE: {db_path}")
    print("=" * 50)
    
    if not os.path.exists(db_path):
        print(f"❌ Database non trovato: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Backup tabelle esistenti
        print("\n1. Backup dati esistenti...")
        
        # Salva dati utenti_autorizzati se esiste
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='utenti_autorizzati'")
        if cursor.fetchone():
            cursor.execute("SELECT codice_fiscale, nome, attivo FROM utenti_autorizzati")
            utenti_backup = cursor.fetchall()
            print(f"   Salvati {len(utenti_backup)} utenti")
        else:
            utenti_backup = []
        
        # 2. Ricrea tabelle con schema corretto
        print("\n2. Applicazione schema corretto...")
        
        # Drop e ricrea utenti_autorizzati
        cursor.execute("DROP TABLE IF EXISTS utenti_autorizzati")
        
        schema = get_exact_schema()
        cursor.executescript(schema)
        
        print("   ✅ Schema applicato")
        
        # 3. Ripristina dati
        if utenti_backup:
            print("\n3. Ripristino dati...")
            for cf, nome, attivo in utenti_backup:
                cursor.execute("""
                    INSERT OR IGNORE INTO utenti_autorizzati 
                    (codice_fiscale, nome, attivo, note) 
                    VALUES (?, ?, ?, '')
                """, (cf, nome, attivo))
            print(f"   ✅ Ripristinati {len(utenti_backup)} utenti")
        
        # 4. Verifica colonne critiche
        print("\n4. Verifica finale...")
        cursor.execute("PRAGMA table_info(utenti_autorizzati)")
        columns = [col[1] for col in cursor.fetchall()]
        
        required = ['codice_fiscale', 'nome', 'note', 'attivo']
        missing = [col for col in required if col not in columns]
        
        if missing:
            print(f"   ❌ Colonne mancanti: {missing}")
            return False
        else:
            print(f"   ✅ Tutte le colonne presenti: {', '.join(required)}")
        
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 50)
        print("✅ DATABASE SISTEMATO!")
        return True
        
    except Exception as e:
        print(f"❌ ERRORE: {e}")
        return False

if __name__ == "__main__":
    # Path database
    db_path = "/opt/access_control/data/access.db"
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    if fix_database(db_path):
        print("\n📝 Prossimi passi:")
        print("1. Riavvia il servizio:")
        print("   sudo systemctl restart access-control-web")
        print("\n2. Verifica log:")
        print("   sudo journalctl -u access-control-web -f")
        sys.exit(0)
    else:
        sys.exit(1)