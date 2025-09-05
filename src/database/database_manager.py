# File: /opt/access_control/src/database/database_manager.py
# Database manager per sistema controllo accessi

import sqlite3
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestore database SQLite per sistema controllo accessi"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.ensure_database_exists()
        self.init_database()
        logger.info(f"🗄️ Database manager inizializzato: {db_path}")
    
    def ensure_database_exists(self):
        """Assicura che la directory del database esista"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def init_database(self):
        """Inizializza database e tabelle"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Abilita foreign keys
                cursor.execute("PRAGMA foreign_keys = ON")
                
                # Tabella utenti autorizzati
                cursor.execute('''
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
                    )
                ''')
                
                # Tabella log accessi
                cursor.execute('''
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
                        note TEXT
                    )
                ''')
                
                # Tabella configurazioni
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS configurazioni (
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
                
                # Tabella eventi sistema
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS eventi_sistema (
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
                
                # Tabella statistiche giornaliere
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS statistiche (
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
                
                # Tabella configurazione relè
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS relay_config (
                        relay_number INTEGER PRIMARY KEY CHECK (relay_number BETWEEN 1 AND 8),
                        description TEXT NOT NULL,
                        valid_action TEXT CHECK (valid_action IN ('OFF', 'ON', 'PULSE')),
                        valid_duration REAL DEFAULT 0,
                        invalid_action TEXT CHECK (invalid_action IN ('OFF', 'ON', 'PULSE')),
                        invalid_duration REAL DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_by TEXT
                    )
                ''')
                
                # Inserisci configurazione di default se la tabella è vuota
                cursor.execute('SELECT COUNT(*) FROM relay_config')
                if cursor.fetchone()[0] == 0:
                    default_configs = [
                        (1, 'Motore Cancello', 'PULSE', 5.0, 'OFF', 0),
                        (2, 'LED Rosso', 'OFF', 0, 'PULSE', 3.0),
                        (3, 'Buzzer', 'PULSE', 0.5, 'PULSE', 2.0),
                        (4, 'LED Verde', 'PULSE', 3.0, 'OFF', 0),
                        (5, 'Blocco Magnetico', 'OFF', 5.0, 'ON', 0),
                        (6, 'Illuminazione', 'ON', 10.0, 'OFF', 0),
                        (7, 'Riserva 1', 'OFF', 0, 'OFF', 0),
                        (8, 'Riserva 2', 'OFF', 0, 'OFF', 0)
                    ]
                    cursor.executemany('''
                        INSERT INTO relay_config 
                        (relay_number, description, valid_action, valid_duration, invalid_action, invalid_duration) 
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', default_configs)
                
                # Indici per performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_cf ON utenti_autorizzati(codice_fiscale)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_cf_attivo ON utenti_autorizzati(codice_fiscale, attivo)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_log_timestamp ON log_accessi(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_log_sync ON log_accessi(sincronizzato)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_log_cf ON log_accessi(codice_fiscale)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_eventi_timestamp ON eventi_sistema(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_statistiche_data ON statistiche(data)')
                
                # Trigger per aggiornamento timestamp
                cursor.execute('''
                    CREATE TRIGGER IF NOT EXISTS update_utente_timestamp 
                    AFTER UPDATE ON utenti_autorizzati
                    FOR EACH ROW
                    BEGIN
                        UPDATE utenti_autorizzati 
                        SET data_aggiornamento = CURRENT_TIMESTAMP 
                        WHERE id = NEW.id;
                    END;
                ''')
                
                conn.commit()
                
                # Inserisci dati di test se database vuoto
                self._insert_test_data_if_empty(cursor)
                conn.commit()
                
                logger.info("✅ Database inizializzato correttamente")
                
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione database: {e}")
            raise
    
    def _insert_test_data_if_empty(self, cursor):
        """Inserisce dati di test se il database è vuoto"""
        # Controlla se ci sono utenti
        cursor.execute("SELECT COUNT(*) FROM utenti_autorizzati")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            logger.info("📝 Inserimento dati di test...")
            
            # Utenti di test
            test_users = [
                {
                    'codice_fiscale': 'RSSMRA80A01H501Z',
                    'nome': 'Mario Rossi',
                    'email': 'mario.rossi@test.com',
                    'reparto': 'Amministrazione',
                    'ruolo': 'Impiegato',
                    'note': 'Utente di test - Autorizzato'
                },
                {
                    'codice_fiscale': 'BNCGVN75L15F205X',
                    'nome': 'Giovanni Bianchi',
                    'email': 'giovanni.bianchi@test.com',
                    'reparto': 'IT',
                    'ruolo': 'Tecnico',
                    'note': 'Utente di test - Autorizzato'
                },
                {
                    'codice_fiscale': 'VRDLCA85T45Z404Y',
                    'nome': 'Luca Verdi',
                    'email': 'luca.verdi@test.com',
                    'reparto': 'Sicurezza',
                    'ruolo': 'Responsabile',
                    'note': 'Utente di test - Autorizzato'
                }
            ]
            
            for user in test_users:
                cursor.execute('''
                    INSERT INTO utenti_autorizzati 
                    (codice_fiscale, nome, note, creato_da, modificato_da)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    user['codice_fiscale'],
                    user['nome'],
                    user['note'],
                    'SYSTEM_INIT',
                    'SYSTEM_INIT'
                ))
            
            # Configurazioni iniziali
            cursor.execute('''
                INSERT OR IGNORE INTO configurazioni (chiave, valore, descrizione, categoria)
                VALUES ('db_version', '1.0.0', 'Versione schema database', 'sistema')
            ''')
            
            cursor.execute('''
                INSERT OR IGNORE INTO configurazioni (chiave, valore, descrizione, categoria)
                VALUES ('installation_date', ?, 'Data installazione sistema', 'sistema')
            ''', (datetime.now().isoformat(),))
            
            logger.info(f"✅ Inseriti {len(test_users)} utenti di test")
    
    def health_check(self) -> bool:
        """Controlla salute del database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Test connessione
                cursor.execute("SELECT 1")
                
                # Test integrità
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()[0]
                
                if result != "ok":
                    logger.error(f"❌ Database integrity check failed: {result}")
                    return False
                
                # Test tabelle principali
                cursor.execute("SELECT COUNT(*) FROM utenti_autorizzati")
                user_count = cursor.fetchone()[0]
                
                logger.debug(f"Database OK - {user_count} utenti autorizzati")
                return True
                
        except Exception as e:
            logger.error(f"❌ Database health check failed: {e}")
            return False
    
    def verify_access(self, codice_fiscale: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Verifica se un codice fiscale è autorizzato"""
        try:
            from api.modules.configurazione_accessi import verifica_orario, verifica_limite_mensile
            
            # Verifica orario prima di tutto
            if not verifica_orario():
                logger.warning(f"Accesso negato per {codice_fiscale}: fuori orario consentito")
                return False, None
                
            # Verifica limite mensile
            if not verifica_limite_mensile(codice_fiscale):
                logger.warning(f"Accesso negato per {codice_fiscale}: limite mensile superato")
                return False, None
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, nome, note
                    FROM utenti_autorizzati 
                    WHERE codice_fiscale = ? AND attivo = 1
                ''', (codice_fiscale.upper(),))
                
                result = cursor.fetchone()
                
                if result:
                    user_data = {
                        'id': result[0],
                        'nome': result[1],
                        'note': result[2]
                    }
                    logger.debug(f"✅ Accesso autorizzato per {user_data['nome']}")
                    return True, user_data
                else:
                    logger.debug(f"❌ Accesso negato per {codice_fiscale}")
                    return False, None
                    
        except Exception as e:
            logger.error(f"❌ Errore verifica accesso: {e}")
            return False, None
    
    def log_access(self, codice_fiscale: str, authorized: bool, processing_time: float = None, 
                   user_data: Dict = None, error: str = None, terminal_id: str = None):
        """Registra tentativo di accesso"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO log_accessi 
                    (timestamp, codice_fiscale, autorizzato, durata_elaborazione, errore, terminale_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now(),
                    codice_fiscale.upper(),
                    authorized,
                    processing_time,
                    error,
                    terminal_id
                ))
                conn.commit()
                
                # Log dettagliato
                status = "AUTORIZZATO" if authorized else "NEGATO"
                user_info = ""
                if user_data:
                    user_info = f" - {user_data.get('nome', '')}"
                
                logger.info(f"📝 Accesso {status}: {codice_fiscale}{user_info}")
                
        except Exception as e:
            logger.error(f"❌ Errore registrazione accesso: {e}")
    
    def get_user_list(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Ottiene lista utenti autorizzati (LOG ESTESO SU RICERCA)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT codice_fiscale, nome, data_inserimento, 
                           data_aggiornamento, attivo, note, creato_da, modificato_da
                    FROM utenti_autorizzati
                '''
                
                if active_only:
                    query += " WHERE attivo = 1"
                
                query += " ORDER BY nome"
                
                logger.info(f"🔎 [LOG SYNC] Esecuzione ricerca lista utenti autorizzati (active_only={active_only})")
                cursor.execute(query)
                results = cursor.fetchall()
                logger.info(f"🔎 [LOG SYNC] Trovati {len(results)} utenti autorizzati (active_only={active_only})")
                
                users = []
                for row in results:
                    users.append({
                        'codice_fiscale': row[0],
                        'nome': row[1],
                        'data_inserimento': row[2],
                        'data_aggiornamento': row[3],
                        'attivo': bool(row[4]),
                        'note': row[5],
                        'creato_da': row[6],
                        'modificato_da': row[7]
                    })
                
                return users
                
        except Exception as e:
            logger.error(f"❌ Errore recupero lista utenti: {e}")
            return []
    
    def user_exists(self, codice_fiscale: str) -> bool:
        """Controlla se un utente esiste già nel database (CF case-insensitive)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM utenti_autorizzati WHERE codice_fiscale = ?", (codice_fiscale.upper(),))
                result = cursor.fetchone()
                # Log solo in caso di errore, non per ogni chiamata
                return result is not None
        except Exception as e:
            logger.error(f"❌ Errore in user_exists: {e}")
            return False

    def add_user(self, codice_fiscale: str, nome: str,
                 email: str = None, reparto: str = None, ruolo: str = None,
                 data_scadenza: str = None, note: str = None, created_by: str = None) -> bool:
        """Aggiunge nuovo utente autorizzato"""
        logger.info(f"🔍 DEBUG add_user - CF: {codice_fiscale}, Nome: {nome}, Created_by: {created_by}")
        print(f"CRITICAL-DEBUG: add_user chiamato con CF={codice_fiscale}, nome={nome}, note={note}, creato_da={created_by}")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verifica se l'utente esiste già (LOG ESTESO)
                logger.info(f"🔎 [LOG SYNC] Ricerca utente per CF: {codice_fiscale.upper()}")
                cursor.execute("SELECT id FROM utenti_autorizzati WHERE codice_fiscale = ?", (codice_fiscale.upper(),))
                result_exist = cursor.fetchone()
                logger.info(f"🔎 [LOG SYNC] Esito ricerca CF {codice_fiscale.upper()}: {'TROVATO' if result_exist else 'NON TROVATO'}")
                print(f"CRITICAL-DEBUG: Ricerca utente CF={codice_fiscale.upper()} -> {'TROVATO' if result_exist else 'NON TROVATO'}")
                if result_exist:
                    logger.warning(f"⚠️ Utente già esistente: {codice_fiscale}")
                    print(f"CRITICAL-DEBUG: Utente già esistente: {codice_fiscale}")
                    return False
                
                # Inserisci nuovo utente
                logger.info(f"➕ [LOG SYNC] Tentativo inserimento utente: {codice_fiscale}, nome={nome}, note={note}, creato_da={created_by}")
                print(f"CRITICAL-DEBUG: Tentativo inserimento utente: {codice_fiscale}, nome={nome}, note={note}, creato_da={created_by}")
                try:
                    cursor.execute('''
                        INSERT INTO utenti_autorizzati 
                        (codice_fiscale, nome, note, creato_da, modificato_da)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        codice_fiscale.upper(),
                        nome,
                        note,
                        created_by,
                        created_by
                    ))
                    conn.commit()
                    logger.info(f"✅ [LOG SYNC] Inserimento utente riuscito per CF: {codice_fiscale.upper()}")
                except Exception as insert_exc:
                    logger.critical(f"❌ ERRORE CRITICO SQL inserimento utente {codice_fiscale}: {insert_exc} | DATI: nome={nome}, note={note}, creato_da={created_by}")
                    print(f"CRITICAL-DEBUG: ERRORE SQL inserimento utente {codice_fiscale}: {insert_exc} | DATI: nome={nome}, note={note}, creato_da={created_by}")
                    raise

                # Verifica inserimento (LOG ESTESO)
                logger.info(f"🔎 [LOG SYNC] Verifica post-inserimento per CF: {codice_fiscale.upper()}")
                cursor.execute("SELECT id FROM utenti_autorizzati WHERE codice_fiscale = ?", (codice_fiscale.upper(),))
                result = cursor.fetchone()
                logger.info(f"🔎 [LOG SYNC] Esito verifica post-inserimento CF {codice_fiscale.upper()}: {'TROVATO' if result else 'NON TROVATO'}")
                print(f"CRITICAL-DEBUG: Verifica post-inserimento CF={codice_fiscale.upper()} -> {'TROVATO' if result else 'NON TROVATO'}")
                if result:
                    logger.info(f"✅ Utente aggiunto con ID {result[0]}: {nome} ({codice_fiscale})")
                    print(f"CRITICAL-DEBUG: Utente aggiunto con ID {result[0]}: {nome} ({codice_fiscale})")
                    return True
                else:
                    logger.critical(f"❌ ERRORE CRITICO: Utente non trovato dopo inserimento: {codice_fiscale}")
                    print(f"CRITICAL-DEBUG: Utente non trovato dopo inserimento: {codice_fiscale}")
                    return False
                
        except sqlite3.IntegrityError as ie:
            logger.warning(f"⚠️ Errore integrità database: {ie} - CF: {codice_fiscale}")
            return False
        except Exception as e:
            logger.error(f"❌ Errore aggiunta utente: {e} - CF: {codice_fiscale} | DATI: nome={nome}, note={note}, creato_da={created_by}")
            return False
    
    def remove_user(self, codice_fiscale: str, soft_delete: bool = True) -> bool:
        """Rimuove utente (soft delete o hard delete) - LOG ESTESO SU UPDATE/DELETE"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                logger.info(f"🔎 [LOG SYNC] Ricerca utente per rimozione CF: {codice_fiscale.upper()}")
                cursor.execute("SELECT id FROM utenti_autorizzati WHERE codice_fiscale = ?", (codice_fiscale.upper(),))
                result_exist = cursor.fetchone()
                logger.info(f"🔎 [LOG SYNC] Esito ricerca per rimozione CF {codice_fiscale.upper()}: {'TROVATO' if result_exist else 'NON TROVATO'}")
                
                if soft_delete:
                    # Soft delete - disattiva utente
                    logger.info(f"📝 [LOG SYNC] Soft delete (disattivazione) utente CF: {codice_fiscale.upper()}")
                    cursor.execute('''
                        UPDATE utenti_autorizzati 
                        SET attivo = 0, data_aggiornamento = CURRENT_TIMESTAMP
                        WHERE codice_fiscale = ?
                    ''', (codice_fiscale.upper(),))
                    action = "disattivato"
                else:
                    # Hard delete - elimina record
                    logger.info(f"📝 [LOG SYNC] Hard delete (eliminazione) utente CF: {codice_fiscale.upper()}")
                    cursor.execute('''
                        DELETE FROM utenti_autorizzati 
                        WHERE codice_fiscale = ?
                    ''', (codice_fiscale.upper(),))
                    action = "eliminato"
                
                logger.info(f"📝 [LOG SYNC] Esito update/delete CF {codice_fiscale.upper()}: {cursor.rowcount} record modificati")
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"✅ Utente {action}: {codice_fiscale}")
                    return True
                else:
                    logger.warning(f"⚠️ Utente non trovato: {codice_fiscale}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Errore rimozione utente: {e}")
            return False
    
    def get_access_logs(self, limit: int = 100, codice_fiscale: str = None) -> List[Dict[str, Any]]:
        """Ottiene log accessi"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT timestamp, codice_fiscale, autorizzato, durata_elaborazione, 
                           errore, terminale_id
                    FROM log_accessi
                '''
                params = []
                
                if codice_fiscale:
                    query += " WHERE codice_fiscale = ?"
                    params.append(codice_fiscale.upper())
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                logs = []
                for row in results:
                    logs.append({
                        'timestamp': row[0],
                        'codice_fiscale': row[1],
                        'autorizzato': bool(row[2]),
                        'durata_elaborazione': row[3],
                        'errore': row[4],
                        'terminale_id': row[5]
                    })
                
                return logs
                
        except Exception as e:
            logger.error(f"❌ Errore recupero log: {e}")
            return []
    
    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Ottiene statistiche accessi"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Statistiche ultimi N giorni
                cursor.execute('''
                    SELECT 
                        COUNT(*) as totale,
                        SUM(CASE WHEN autorizzato = 1 THEN 1 ELSE 0 END) as autorizzati,
                        SUM(CASE WHEN autorizzato = 0 THEN 1 ELSE 0 END) as negati,
                        AVG(durata_elaborazione) as tempo_medio
                    FROM log_accessi 
                    WHERE timestamp >= datetime('now', '-{} days')
                '''.format(days))
                
                result = cursor.fetchone()
                
                stats = {
                    'periodo_giorni': days,
                    'totale_accessi': result[0] or 0,
                    'accessi_autorizzati': result[1] or 0,
                    'accessi_negati': result[2] or 0,
                    'tempo_medio_elaborazione': result[3] or 0,
                    'tasso_successo': 0
                }
                
                if stats['totale_accessi'] > 0:
                    stats['tasso_successo'] = (stats['accessi_autorizzati'] / stats['totale_accessi']) * 100
                
                return stats
                
        except Exception as e:
            logger.error(f"❌ Errore calcolo statistiche: {e}")
            return {}
    
    def backup_database(self, backup_path: str = None) -> bool:
        """Crea backup del database"""
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = Path(self.db_path).parent / "backups"
                backup_dir.mkdir(exist_ok=True)
                backup_path = backup_dir / f"access_backup_{timestamp}.db"
            
            # Backup usando SQLite VACUUM INTO
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(f"VACUUM INTO '{backup_path}'")
            
            logger.info(f"✅ Backup creato: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore backup database: {e}")
            return False
    
    def close(self):
        """Chiude connessioni database"""
        # SQLite non richiede chiusura esplicita con context manager
        logger.debug("Database manager chiuso")
