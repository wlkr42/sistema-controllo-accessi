# SCHEMA DATABASE ACCESS_CONTROL

## 📍 POSIZIONE DATABASE
`/opt/access_control/src/access.db`

## 📊 TABELLE PRINCIPALI

### 1. utenti_sistema
**Scopo**: Autenticazione amministratori dashboard
```sql
CREATE TABLE utenti_sistema (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    attivo INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    modified_at TIMESTAMP,
    modified_by TEXT,
    last_login TIMESTAMP
);
```

### 2. utenti_autorizzati
**Scopo**: Persone autorizzate ad accedere fisicamente
```sql
CREATE TABLE utenti_autorizzati (
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
```

### 3. utenti_autorizzati_backup
**Scopo**: Backup esteso dei dati utenti autorizzati
```sql
CREATE TABLE utenti_autorizzati_backup (
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
);
```

### 4. log_accessi
**Scopo**: Registro dettagliato degli accessi
```sql
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
    note TEXT
);
```

### 5. configurazione_accessi
**Scopo**: Configurazione generale degli accessi
```sql
CREATE TABLE configurazione_accessi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ora_apertura TIME NOT NULL,
    ora_chiusura TIME NOT NULL,
    max_ingressi_mensili INTEGER NOT NULL DEFAULT 10,
    modificato_da TEXT,
    data_modifica TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6. orari_settimanali
**Scopo**: Gestione orari per ogni giorno della settimana
```sql
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
);
```

### 7. orari_accesso
**Scopo**: Configurazione orari di accesso
```sql
CREATE TABLE orari_accesso (
    giorno TEXT PRIMARY KEY,
    aperto BOOLEAN DEFAULT true,
    mattina_inizio TIME,
    mattina_fine TIME,
    pomeriggio_inizio TIME,
    pomeriggio_fine TIME,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT
);
```

### 8. limiti_accesso
**Scopo**: Configurazione limiti di accesso
```sql
CREATE TABLE limiti_accesso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    max_ingressi_mensili INTEGER DEFAULT 3,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT
);
```

### 9. limiti_utenti
**Scopo**: Limiti personalizzati per utente
```sql
CREATE TABLE limiti_utenti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codice_fiscale TEXT NOT NULL,
    max_ingressi_mensili INTEGER NOT NULL DEFAULT 10,
    modificato_da TEXT,
    data_modifica TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(codice_fiscale)
);
```

### 10. conteggio_ingressi_mensili
**Scopo**: Conteggio accessi mensili per utente
```sql
CREATE TABLE conteggio_ingressi_mensili (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codice_fiscale TEXT NOT NULL,
    mese INTEGER NOT NULL,
    anno INTEGER NOT NULL,
    numero_ingressi INTEGER DEFAULT 0,
    ultimo_ingresso TIMESTAMP,
    UNIQUE(codice_fiscale, mese, anno)
);
```

### 11. conteggio_ingressi_mensili_archive
**Scopo**: Archivio storico conteggi mensili
```sql
CREATE TABLE conteggio_ingressi_mensili_archive (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codice_fiscale TEXT NOT NULL,
    mese INTEGER NOT NULL,
    anno INTEGER NOT NULL,
    numero_ingressi INTEGER,
    ultimo_ingresso TIMESTAMP,
    data_archiviazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 12. log_forzature
**Scopo**: Registro delle aperture forzate
```sql
CREATE TABLE log_forzature (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    utente TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dettagli TEXT
);
```

### 13. configurazioni
**Scopo**: Configurazioni generali del sistema
```sql
CREATE TABLE configurazioni (
    chiave TEXT PRIMARY KEY,
    valore TEXT NOT NULL,
    tipo TEXT DEFAULT 'string',
    descrizione TEXT,
    categoria TEXT,
    modificabile BOOLEAN DEFAULT 1,
    data_modifica TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificato_da TEXT
);
```

### 14. eventi_sistema
**Scopo**: Log eventi di sistema
```sql
CREATE TABLE eventi_sistema (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo_evento TEXT NOT NULL,
    livello TEXT DEFAULT 'INFO',
    messaggio TEXT NOT NULL,
    dettagli TEXT,
    componente TEXT,
    risolto BOOLEAN DEFAULT 0
);
```

### 15. statistiche
**Scopo**: Statistiche giornaliere del sistema
```sql
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
);
```

### 16. system_settings
**Scopo**: Impostazioni di sistema
```sql
CREATE TABLE system_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 📊 VISTE

### 1. authorized_people
```sql
CREATE VIEW authorized_people AS
SELECT
    codice_fiscale,
    nome,
    cognome,
    nome || ' ' || cognome as name,
    email,
    telefono as phone,
    attivo as active,
    data_inserimento as created_at
FROM "utenti_autorizzati_backup";
```

### 2. access_log
```sql
CREATE VIEW access_log AS
SELECT
    id,
    timestamp,
    codice_fiscale,
    autorizzato as authorized,
    durata_elaborazione as processing_time,
    errore as error_message,
    terminale_id as terminal_id
FROM log_accessi;
```

## 📑 INDICI

### utenti_autorizzati_backup
```sql
CREATE INDEX idx_cf ON utenti_autorizzati_backup(codice_fiscale);
CREATE INDEX idx_cf_attivo ON utenti_autorizzati_backup(codice_fiscale, attivo);
```

### log_accessi
```sql
CREATE INDEX idx_log_timestamp ON log_accessi(timestamp);
CREATE INDEX idx_log_sync ON log_accessi(sincronizzato);
CREATE INDEX idx_log_cf ON log_accessi(codice_fiscale);
```

### eventi_sistema
```sql
CREATE INDEX idx_eventi_timestamp ON eventi_sistema(timestamp);
```

### statistiche
```sql
CREATE INDEX idx_statistiche_data ON statistiche(data);
```

## 🔄 TRIGGERS

### update_utente_timestamp
```sql
CREATE TRIGGER update_utente_timestamp
AFTER UPDATE ON utenti_autorizzati_backup
FOR EACH ROW
BEGIN
    UPDATE utenti_autorizzati_backup
    SET data_aggiornamento = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;
```

## ⚠️ REGOLE CRITICHE DATABASE

1. **MAI** usare `utenti_autorizzati` per login dashboard
2. **MAI** usare `utenti_sistema` per accesso fisico
3. **SEMPRE** hashare password con bcrypt
4. **SEMPRE** validare `codice_fiscale` formato
5. **SEMPRE** loggare accessi in `log_accessi`
6. **SEMPRE** usare transazioni per operazioni multiple
7. **SEMPRE** mantenere sincronizzati `utenti_autorizzati` e `utenti_autorizzati_backup`
8. **SEMPRE** verificare i limiti di accesso prima di autorizzare

## 🔑 RELAZIONI CHIAVE

1. **log_accessi** → **codice_fiscale** di utenti_autorizzati
2. **limiti_utenti** → **codice_fiscale** di utenti_autorizzati
3. **conteggio_ingressi_mensili** → **codice_fiscale** di utenti_autorizzati

## 📋 TABELLE REALI NEL DATABASE
- utenti_autorizzati
- utenti_autorizzati_backup
- utenti_sistema
- log_accessi
- configurazioni
- eventi_sistema
- statistiche
- system_settings
- configurazione_accessi
- orari_settimanali
- limiti_utenti
- conteggio_ingressi_mensili
- conteggio_ingressi_mensili_archive
- orari_accesso
- limiti_accesso
- log_forzature
- sqlite_sequence
