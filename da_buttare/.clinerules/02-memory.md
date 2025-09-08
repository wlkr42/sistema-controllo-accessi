# MEMORIA PROGETTO ACCESS_CONTROL

## 📝 ULTIMO AGGIORNAMENTO
- Data: 2025-07-25 07:43
- Task: Tentativo risoluzione problema sincronizzazione Odoo
- Modifiche:
  - Corretto problema permessi file di log (chown wlkr42:wlkr42)
  - Modificato commento in src/external/odoo_partner_connector.py per chiarire parametro created_by
  - Problema sincronizzazione persiste con 25484 errori
  - Identificato potenziale problema nel passaggio parametri tra odoo_partner_connector.py e database_manager.py

## 🔄 MODIFICHE PRINCIPALI
- Aggiunto supporto fuso orario Europe/Rome per orari corretti
- Migliorata gestione intervalli che attraversano la mezzanotte
- Aggiunto logging dettagliato per debug
- Verifica orari configurati dall'interfaccia utente
- Test completi del sistema di controllo accessi

## 📁 STRUTTURA REALE DEL PROGETTO

```
/opt/access_control/
├── src/                    # Codice sorgente principale
│   ├── api/               # API Flask e interfaccia web
│   │   ├── modules/       # Moduli Blueprint
│   │   ├── static/        # File statici (CSS, JS, immagini)
│   │   ├── templates/     # Template HTML aggiuntivi
│   │   ├── utils/         # Utility API
│   │   ├── backup_module.py  # Modulo backup (Blueprint)
│   │   └── web_api.py     # API principale Flask
│   ├── core/              # Configurazioni core
│   │   └── config.py      # Config manager
│   ├── database/          # Layer database
│   │   └── database_manager.py
│   ├── drivers/           # Driver hardware
│   │   └── 288K/          # Driver lettore tessere 288K
│   │       ├── 288K-linux-sample/  # Esempi e test
│   │       ├── doc/       # Documentazione
│   │       ├── install/   # Script installazione
│   │       └── linux_crt_288x/  # Driver per x86/x64
│   ├── external/          # Integrazioni esterne
│   │   └── odoo_partner_connector.py
│   ├── hardware/          # Controller hardware
│   │   ├── card_reader.py # Controller generico lettore
│   │   ├── crt285_reader.py # Supporto lettore CRT285
│   │   ├── reader_factory.py # Factory per diversi lettori
│   │   ├── test_readers.py # Test lettori
│   │   └── usb_rly08_controller.py # Controller relè USB
│   ├── utils/             # Utility generali
│   ├── access.db          # Database SQLite
│   └── main.py            # Entry point applicazione
├── config/                # Configurazioni
│   ├── admin_config.json
│   ├── base.yml
│   └── dashboard_config.json
├── scripts/               # Script utilità e manutenzione
├── logs/                  # File di log
├── data/                  # Dati applicazione
├── backups/               # Backup automatici
├── tests/                 # Test suite
├── docs/                  # Documentazione
└── da_buttare/            # File obsoleti (non eliminare!)
```

## 🔌 API ENDPOINTS PRINCIPALI

### Autenticazione
- `POST /api/login` - Login utenti_sistema (admin)
- `POST /api/logout` - Logout
- `GET /api/check-auth` - Verifica autenticazione

### Gestione Utenti
- `GET /api/users` - Lista utenti sistema
- `POST /api/users` - Crea utente sistema
- `PUT /api/users/<id>` - Modifica utente sistema
- `DELETE /api/users/<id>` - Elimina utente sistema

### Utenti Autorizzati (Accesso Fisico)
- `GET /api/utenti-autorizzati` - Lista con filtri
- `POST /api/utenti-autorizzati` - Aggiungi utente
- `PUT /api/utenti-autorizzati/<id>` - Modifica
- `DELETE /api/utenti-autorizzati/<id>` - Elimina
- `POST /api/authorize` - Autorizza accesso con tessera

### Configurazione Accessi
- `GET /api/configurazione/orari` - Ottieni orari settimanali
- `POST /api/configurazione/orari` - Salva orari settimanali
- `GET /api/configurazione/limiti` - Ottieni limiti ingressi
- `POST /api/configurazione/limiti` - Salva limiti ingressi
- `GET /api/utenti-autorizzati/disattivati` - Lista utenti disattivati
- `POST /api/configurazione/test/set-ingressi` - Test conteggio ingressi
- `POST /api/configurazione/test/simula-accesso` - Simula accesso
- `POST /api/configurazione/test/reset-contatore` - Reset contatore
- `POST /api/configurazione/test/apri-cancello` - Apertura forzata
- `GET /api/configurazione/log-forzature` - Log forzature

### Hardware
- `POST /api/relay/open` - Apri relè
- `POST /api/relay/close` - Chiudi relè
- `GET /api/relay/status` - Stato relè
- `GET /api/hardware/test` - Test hardware
- `POST /api/test-card-reader` - Test lettore

### Sistema
- `GET /api/logs` - Visualizza log
- `GET /api/system/status` - Stato sistema

### Backup
- `GET /api/backup/status` - Stato backup
- `POST /api/backup/create` - Crea backup
- `POST /api/backup/cleanup` - Pulizia backup vecchi
- `GET /api/backup/download/<filename>` - Download backup
- `POST /api/backup/restore` - Ripristina backup
- `GET /api/backup/schedule` - Configurazione schedulazione
- `POST /api/backup/schedule` - Salva schedulazione

## 📦 MODULI PRINCIPALI

### src/api/modules/
- `utenti.py` - Gestione utenti sistema
- `utenti_autorizzati.py` - Gestione accesso fisico
  - GET /api/utenti-autorizzati - Lista utenti attivi
  - GET /api/utenti-autorizzati/disattivati - Lista utenti disattivati
  - POST /api/utenti-autorizzati/toggle-active - Attiva/disattiva utente
- `dispositivi.py` - Gestione dispositivi hardware
- `profilo.py` - Profilo utente corrente
- `log_management.py` - Gestione e visualizzazione log
- `email_log_allerte_sistema.py` - Email e allerte
- `user_management.py` - Utility gestione utenti
- `configurazione_accessi.py` - Configurazione accessi
  - GET/POST /api/configurazione/orari - Orari settimanali
  - GET/POST /api/configurazione/limiti - Limiti ingressi mensili
  - POST /api/configurazione/test/set-ingressi - Test conteggio
  - POST /api/configurazione/test/simula-accesso - Simulazione
  - POST /api/configurazione/test/reset-contatore - Reset contatore
  - POST /api/configurazione/test/apri-cancello - Apertura forzata
  - GET /api/configurazione/log-forzature - Log forzature

### src/api/static/
- `css/` - Stili
  - `dashboard.css` - Stile principale dashboard
  - `configurazione_orari.css` - Stili pagina configurazione orari
  - `user-menu.css` - Stili menu utente
  - `test-accessi.css` - Stili test accessi
  - `clock.css` - Stili orologio navbar
    - Orologio centrato con sfondo semi-trasparente
    - Font Roboto Mono per migliore leggibilità
    - Data e ora in italiano
    - Layout responsive con min-width
- `js/` - JavaScript
  - `configurazione_orari.js` - Gestione orari settimanali
    - Configurazione orari per ogni giorno
    - Orari mattina/pomeriggio configurabili
    - Copia configurazione su tutti i giorni
    - Salvataggio automatico
  - `test-accessi.js` - Test funzionalità accessi
  - `user-menu.js` - Menu utente e profilo
  - `alerts.js` - Sistema notifiche
- `html/` - Componenti HTML riutilizzabili

## 🗄️ STRUTTURA DATABASE

### Tabella utenti_autorizzati
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

### Tabelle Configurazione Accessi
```sql
-- Orari settimanali
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

-- Limiti accessi
CREATE TABLE limiti_accesso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    max_ingressi_mensili INTEGER DEFAULT 3,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT
);

-- Log forzature
CREATE TABLE log_forzature (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    utente TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dettagli TEXT
);

-- Conteggio ingressi mensili
CREATE TABLE conteggio_ingressi_mensili (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codice_fiscale TEXT NOT NULL,
    anno INTEGER NOT NULL,
    mese INTEGER NOT NULL,
    ingressi INTEGER DEFAULT 0,
    UNIQUE(codice_fiscale, anno, mese)
);

-- Archivio conteggi mensili
CREATE TABLE conteggio_ingressi_mensili_archive (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codice_fiscale TEXT NOT NULL,
    anno INTEGER NOT NULL,
    mese INTEGER NOT NULL,
    ingressi INTEGER,
    archiviato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 FILE CONFIGURAZIONE
- `config/base.yml` - Config principale applicazione
- `config/admin_config.json` - Config amministrazione
- `config/dashboard_config.json` - Config dashboard
- `.env` - Variabili ambiente (non in git)

## 📝 CONVENZIONI CODICE

### Python
- Indentazione: 4 spazi
- Naming: snake_case
- Docstring per ogni funzione pubblica
- Type hints dove possibile
- Import ordinati (standard, third-party, local)

### JavaScript
- Indentazione: 2 spazi
- Naming: camelCase
- Const/let invece di var
- Arrow function per callback
- Async/await invece di promise chains

### Layout Navbar
- Layout unificato in tutte le pagine
- Titolo e icona a sinistra
- Orologio centrato con data e ora
- Pulsanti e menu utente a destra
- Stile consistente con sfondo viola sfumato

### API Response
```python
{
    "success": bool,
    "message": str,
    "data": any,  # optional
    "error": str  # solo se success=False
}
```

## 🔐 AUTENTICAZIONE
- Basata su sessioni Flask
- Login con username/password da tabella `utenti_sistema`
- Decorator `@login_required` per endpoint protetti
- Sessione scade dopo 24 ore di inattività
