#!/usr/bin/env python3
"""
Setup Database Script per Sistema Controllo Accessi
Inizializza un database pulito con struttura completa
"""

import os
import sys
import sqlite3
import hashlib
from datetime import datetime

def create_database(db_path):
    """Crea database con struttura completa"""
    
    # Crea directory se non esiste
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        print(f"✓ Creata directory: {db_dir}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabella utenti
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT,
        role TEXT DEFAULT 'user',
        active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        reset_token TEXT,
        reset_token_expiry TIMESTAMP
    )
    ''')
    
    # Tabella tessere
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tessere (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cognome TEXT NOT NULL,
        codice_fiscale TEXT UNIQUE NOT NULL,
        numero_tessera TEXT UNIQUE NOT NULL,
        tipo_tessera TEXT DEFAULT 'standard',
        data_emissione DATE,
        data_scadenza DATE,
        active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    )
    ''')
    
    # Tabella accessi
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accessi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tessera_id INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        direzione TEXT CHECK(direzione IN ('ingresso', 'uscita')),
        varco INTEGER DEFAULT 1,
        esito TEXT DEFAULT 'autorizzato',
        note TEXT,
        FOREIGN KEY (tessera_id) REFERENCES tessere(id)
    )
    ''')
    
    # Tabella configurazione sistema
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sistema_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chiave TEXT UNIQUE NOT NULL,
        valore TEXT,
        tipo TEXT DEFAULT 'string',
        descrizione TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabella orari accesso
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orari_accesso (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tessera_id INTEGER,
        giorno_settimana INTEGER CHECK(giorno_settimana BETWEEN 0 AND 6),
        ora_inizio TIME,
        ora_fine TIME,
        active BOOLEAN DEFAULT 1,
        FOREIGN KEY (tessera_id) REFERENCES tessere(id)
    )
    ''')
    
    # Tabella blacklist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS blacklist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tessera_id INTEGER,
        motivo TEXT,
        data_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_rimozione TIMESTAMP,
        active BOOLEAN DEFAULT 1,
        FOREIGN KEY (tessera_id) REFERENCES tessere(id)
    )
    ''')
    
    # Tabella log eventi
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS log_eventi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_evento TEXT NOT NULL,
        descrizione TEXT,
        dettagli TEXT,
        livello TEXT DEFAULT 'info',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_id INTEGER,
        ip_address TEXT,
        user_agent TEXT
    )
    ''')
    
    # Tabella varchi
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS varchi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descrizione TEXT,
        tipo TEXT DEFAULT 'bidirezionale',
        pin_relay INTEGER,
        active BOOLEAN DEFAULT 1,
        tempo_apertura INTEGER DEFAULT 3
    )
    ''')
    
    # Tabella system_settings (per email config e altro)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS system_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        value TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabella odoo_sync
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS odoo_sync (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        partner_id INTEGER,
        barcode TEXT,
        name TEXT,
        vat TEXT,
        last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        sync_status TEXT DEFAULT 'success',
        error_message TEXT
    )
    ''')
    
    # Tabella utenti_autorizzati (compatibilità con sistema esistente)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS utenti_autorizzati (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codice_fiscale TEXT UNIQUE NOT NULL,
        nome TEXT NOT NULL,
        email TEXT,
        telefono TEXT,
        attivo BOOLEAN DEFAULT 1,
        gruppi TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP,
        created_by TEXT,
        updated_by TEXT
    )
    ''')
    
    # Tabella log_accessi (compatibilità)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS log_accessi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        codice_fiscale TEXT NOT NULL,
        autorizzato BOOLEAN,
        durata_elaborazione REAL,
        terminale_id TEXT,
        nome_utente TEXT,
        motivo_rifiuto TEXT,
        tipo_accesso TEXT
    )
    ''')
    
    # Tabella utenti_sistema (per login web)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS utenti_sistema (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT,
        role TEXT DEFAULT 'viewer',
        attivo BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        must_change_password BOOLEAN DEFAULT 0,
        failed_login_attempts INTEGER DEFAULT 0,
        locked_until TIMESTAMP,
        created_by TEXT,
        modified_at TIMESTAMP,
        modified_by TEXT,
        nome TEXT,
        cognome TEXT,
        avatar_path TEXT,
        telefono TEXT,
        bio TEXT,
        data_nascita DATE,
        indirizzo TEXT
    )
    ''')
    
    # Tabella relay_config
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS relay_config (
        relay_id INTEGER PRIMARY KEY,
        nome TEXT,
        descrizione TEXT,
        azione_accesso_valido TEXT DEFAULT 'pulse',
        durata_impulso_valido INTEGER DEFAULT 3,
        azione_accesso_invalido TEXT DEFAULT 'off',
        durata_impulso_invalido INTEGER DEFAULT 0,
        attivo BOOLEAN DEFAULT 1
    )
    ''')
    
    # Tabella fascie_orarie
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fascie_orarie (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        giorno_settimana INTEGER,
        ora_inizio TEXT,
        ora_fine TEXT,
        attivo BOOLEAN DEFAULT 1,
        descrizione TEXT
    )
    ''')
    
    # Tabella conteggio mensile
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conteggio_ingressi_mensili (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codice_fiscale TEXT NOT NULL,
        mese INTEGER NOT NULL,
        anno INTEGER NOT NULL,
        numero_ingressi INTEGER DEFAULT 0,
        ultimo_ingresso TIMESTAMP,
        UNIQUE(codice_fiscale, mese, anno)
    )
    ''')
    
    # Tabella limiti accesso
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS limiti_accesso (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT DEFAULT 'mensile',
        limite INTEGER DEFAULT 10,
        attivo BOOLEAN DEFAULT 1
    )
    ''')
    
    # Tabella eventi sistema
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS eventi_sistema (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        tipo_evento TEXT,
        livello TEXT,
        messaggio TEXT,
        componente TEXT,
        utente TEXT
    )
    ''')
    
    # Crea indici per performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tessere_codice ON tessere(codice_fiscale)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tessere_numero ON tessere(numero_tessera)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_accessi_timestamp ON accessi(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_accessi_tessera ON accessi(tessera_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_log_timestamp ON log_eventi(timestamp)')
    
    # Inserisci utente admin di default (in entrambe le tabelle per compatibilità)
    admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
    
    # Tabella users (sistema nuovo)
    cursor.execute('''
    INSERT OR IGNORE INTO users (username, password_hash, email, role, active)
    VALUES (?, ?, ?, ?, ?)
    ''', ('admin', admin_password, 'admin@sistema.local', 'admin', 1))
    
    # Tabella utenti_sistema (compatibilità)
    cursor.execute('''
    INSERT OR IGNORE INTO utenti_sistema (username, password, email, role, nome, cognome, attivo)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('admin', admin_password, 'admin@sistema.local', 'admin', 'Admin', 'Sistema', 1))
    
    # Inserisci configurazioni di default
    default_configs = [
        ('nome_installazione', 'Sistema Controllo Accessi', 'string', 'Nome del sistema'),
        ('versione', '3.0.0-RC1', 'string', 'Versione del sistema'),
        ('modalita_debug', '0', 'boolean', 'Modalità debug'),
        ('tempo_apertura_varco', '3', 'integer', 'Tempo apertura varco in secondi'),
        ('limite_accessi_giornaliero', '100', 'integer', 'Limite accessi giornalieri'),
        ('backup_automatico', '1', 'boolean', 'Backup automatico abilitato'),
        ('retention_log_giorni', '90', 'integer', 'Giorni di retention dei log'),
        ('odoo_sync_enabled', '0', 'boolean', 'Sincronizzazione Odoo abilitata'),
        ('card_reader_model', 'CRT-288K', 'string', 'Modello lettore tessere'),
        ('relay_controller_model', 'USB-RLY08', 'string', 'Modello controller relè')
    ]
    
    for chiave, valore, tipo, desc in default_configs:
        cursor.execute('''
        INSERT OR IGNORE INTO sistema_config (chiave, valore, tipo, descrizione)
        VALUES (?, ?, ?, ?)
        ''', (chiave, valore, tipo, desc))
    
    # Inserisci varco di default
    cursor.execute('''
    INSERT OR IGNORE INTO varchi (nome, descrizione, tipo, pin_relay, active, tempo_apertura)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', ('Varco Principale', 'Ingresso principale', 'bidirezionale', 1, 1, 3))
    
    # Configurazione relè (8 canali)
    for i in range(1, 9):
        cursor.execute('''
        INSERT OR IGNORE INTO relay_config (relay_id, nome, descrizione, attivo)
        VALUES (?, ?, ?, ?)
        ''', (i, f'Relè {i}', f'Canale relè {i}', 1 if i == 1 else 0))
    
    # Relè 1 per cancello principale
    cursor.execute('''
    UPDATE relay_config 
    SET nome = 'Cancello Ingresso',
        descrizione = 'Controllo cancello principale',
        azione_accesso_valido = 'pulse',
        durata_impulso_valido = 5,
        attivo = 1
    WHERE relay_id = 1
    ''')
    
    # Fasce orarie default (Lun-Ven 8:00-18:00, Sab 8:00-13:00)
    fasce_default = [
        (1, '08:00', '18:00', 'Lunedì'),
        (2, '08:00', '18:00', 'Martedì'),
        (3, '08:00', '18:00', 'Mercoledì'),
        (4, '08:00', '18:00', 'Giovedì'),
        (5, '08:00', '18:00', 'Venerdì'),
        (6, '08:00', '13:00', 'Sabato')
    ]
    
    for giorno, inizio, fine, desc in fasce_default:
        cursor.execute('''
        INSERT OR IGNORE INTO fascie_orarie (giorno_settimana, ora_inizio, ora_fine, descrizione, attivo)
        VALUES (?, ?, ?, ?, ?)
        ''', (giorno, inizio, fine, desc, 1))
    
    # Limite mensile default
    cursor.execute('''
    INSERT OR IGNORE INTO limiti_accesso (tipo, limite, attivo)
    VALUES ('mensile', 10, 1)
    ''')
    
    # Log inizializzazione sistema
    cursor.execute('''
    INSERT INTO log_eventi (tipo_evento, descrizione, livello)
    VALUES (?, ?, ?)
    ''', ('SYSTEM_INIT', 'Database inizializzato con successo', 'info'))
    
    conn.commit()
    conn.close()
    
    print(f"✓ Database creato: {db_path}")
    return True

def main():
    """Main function"""
    
    # Path database di default
    db_path = '/opt/access_control/data/access_control.db'
    
    # Se passato come parametro usa quello
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    # Crea directory se non esiste
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        print(f"✓ Directory creata: {db_dir}")
    
    # Backup database esistente se presente
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename(db_path, backup_path)
        print(f"✓ Backup database esistente: {backup_path}")
    
    # Crea nuovo database
    if create_database(db_path):
        print("\n✅ Database inizializzato con successo!")
        print(f"   Path: {db_path}")
        print(f"   User: admin")
        print(f"   Pass: admin123")
        return 0
    else:
        print("\n❌ Errore durante inizializzazione database")
        return 1

if __name__ == "__main__":
    sys.exit(main())