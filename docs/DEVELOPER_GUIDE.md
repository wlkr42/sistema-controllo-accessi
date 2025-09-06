# Guida Sviluppatore - Sistema Controllo Accessi

## 🏗️ Architettura del Sistema

### Stack Tecnologico
- **Backend**: Python 3.10 + Flask
- **Database**: SQLite
- **Frontend**: HTML5 + Bootstrap 5 + JavaScript vanilla
- **Hardware**: CRT-285 (lettore tessere) + USB-RLY08 (controller relè)
- **Deployment**: systemd service (root)

### Struttura Directory
```
/opt/access_control/
├── src/
│   ├── api/
│   │   ├── web_api.py              # API principale Flask
│   │   ├── dashboard_templates.py   # Template dashboard e admin
│   │   ├── log_accessi_template.py  # Template log accessi
│   │   ├── admin_templates.py       # Template backup (non usato per config)
│   │   └── modules/
│   │       ├── configurazione_accessi.py  # Logica verifica accessi
│   │       └── email_log_allerte_sistema.py
│   ├── core/
│   │   ├── database.py             # Gestione database
│   │   ├── config.py               # Configurazioni
│   │   └── db_config.py            # Configurazione centralizzata path DB
│   └── hardware/
│       ├── crt285_controller.py    # Controller lettore tessere
│       └── usb_rly08_controller.py # Controller relè
├── data/
│   ├── access.db                   # Database SQLite (migrato da /src)
│   ├── database.db                 # Database vecchio (deprecato)
│   ├── sync_config.json            # Configurazione sincronizzazione
│   └── partner_cache.json          # Cache partner
├── logs/
│   └── access_control.log          # Log applicazione
├── venv/                           # Virtual environment Python
└── requirements.txt                # Dipendenze Python
```

## 🔧 Configurazione Sviluppo

### 1. Setup Ambiente
```bash
cd /opt/access_control
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Database Schema
```sql
-- Tabelle principali
utenti_autorizzati       -- Utenti con tessera
log_accessi             -- Log tutti gli accessi
system_settings         -- Configurazioni sistema
relay_config           -- Configurazione 8 relè
fascie_orarie          -- Orari accesso consentiti
limiti_accesso_mensili -- Limiti mensili per utente
utenti_sistema         -- Utenti sistema con profili estesi (v2.7.0+)
password_reset_tokens  -- Token reset password (v2.7.0+)
password_history      -- Storico password (v2.7.0+)
```

### 3. Variabili Ambiente
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
export DATABASE_PATH=/opt/access_control/data/database.db
```

## 🕐 Sistema Timezone

### Configurazione
Il sistema gestisce i timezone attraverso la tabella `system_settings`:
- **Chiave**: `sistema.timezone`
- **Default**: `Europe/Rome`
- **UI**: Sezione "Orologio" in `/admin/config`

### Conversione Timestamp
```python
# Pattern standard per conversione UTC → Local
import pytz
from datetime import datetime

def convert_utc_to_local(timestamp_str, timezone_name='Europe/Rome'):
    """Converte timestamp UTC in timezone locale"""
    tz = pytz.timezone(timezone_name)
    utc = pytz.utc
    
    # Parse UTC timestamp
    dt_utc = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
    dt_utc = utc.localize(dt_utc)
    
    # Convert to local
    dt_local = dt_utc.astimezone(tz)
    return dt_local.strftime('%Y-%m-%d %H:%M:%S')
```

### Dashboard Ultimi Accessi (v2.3.0+)
La sezione "Ultimi Accessi" nella dashboard ora rispetta il timezone configurato:
- **API**: `/api/recent-accesses` legge timezone da `system_settings`
- **Frontend**: JavaScript usa `time_formatted` dal server (non più conversione lato client)
- **Formato**: Rispetta configurazione 24h/12h dalle impostazioni

### Punti Critici
1. **Database**: SQLite salva sempre in UTC con `CURRENT_TIMESTAMP`
2. **API Log Accessi**: `/api/log-accessi` converte automaticamente
3. **API Recent Accesses**: `/api/recent-accesses` usa timezone configurato (v2.3.0+)
4. **Export**: Tutti i formati (CSV, Excel, PDF) usano timezone configurato

## 📊 Sistema Esportazioni

### Endpoint Unificato
```python
@app.route('/api/log-accessi/export')
@require_auth()
def api_export_log_accessi():
    format_type = request.args.get('format', 'csv')  # csv|excel|pdf
```

### Implementazione per Formato

#### CSV
```python
import csv
import io

output = io.StringIO()
writer = csv.writer(output)
writer.writerow(['Headers...'])
# Write data...
response = make_response(output.getvalue())
response.headers['Content-Type'] = 'text/csv'
```

#### Excel
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

wb = Workbook()
ws = wb.active
# Add data and styles...
excel_file = io.BytesIO()
wb.save(excel_file)
response = make_response(excel_file.getvalue())
response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
```

#### PDF
```python
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4, landscape

pdf_file = io.BytesIO()
doc = SimpleDocTemplate(pdf_file, pagesize=landscape(A4))
# Create table...
doc.build([table])
response = make_response(pdf_file.getvalue())
response.headers['Content-Type'] = 'application/pdf'
```

## 🔐 Sistema Autenticazione

### Login Flow
1. POST `/login` con username/password
2. Verifica in `utenti_autorizzati` table
3. Set session cookie
4. Decorator `@require_auth()` per proteggere route

### Permessi
- `@require_permission('all')` - Solo admin
- `@require_permission('read')` - Utenti normali

## 🚦 Logica Controllo Accessi

### Ordine Verifiche (IMPORTANTE!)
```python
# In process_codice_fiscale() - web_api.py
1. Verifica esistenza utente
2. Verifica attivazione utente  
3. Verifica orari accesso
4. Verifica limiti mensili
5. Autorizza o nega
```

### Tipi Accesso
- `AUTORIZZATO` - Accesso consentito
- `UTENTE_NON_TROVATO` - CF non in database
- `UTENTE_DISATTIVATO` - Utente disabilitato
- `FUORI_ORARIO` - Fuori fascia oraria
- `LIMITE_SUPERATO` - Superato limite mensile

## 🔌 Hardware Integration

### Lettore Tessere CRT-285
```python
from hardware.crt285_controller import CRT285Controller

controller = CRT285Controller()
controller.connect('/dev/ttyACM0')
codice_fiscale = controller.read_card()  # Blocking
controller.disconnect()
```

### Test Lettore senza Interferenze (v2.2.0+)
Il test del lettore ora funziona monitorando il database invece di accedere all'hardware:

```python
# hardware_tests.py - test_reader()
# NON inizializza il lettore hardware
# Monitora la tabella log_accessi per nuovi inserimenti
cursor.execute("""
    SELECT id, codice_fiscale, autorizzato, motivo_rifiuto, nome_utente 
    FROM log_accessi 
    WHERE id > ? 
    ORDER BY id
""", (last_access_id,))
```

**Campi database utilizzati:**
- `motivo_rifiuto`: Contiene la motivazione del rifiuto
- `nome_utente`: Nome dell'utente se disponibile
- `autorizzato`: Flag booleano per accesso autorizzato/negato

**Funzione Stop Test:**
- Endpoint: `POST /api/hardware/stop-reader`
- Funzione: `stop_reader()` in `hardware_tests.py`
- Interrompe il test senza interferire con il sistema principale

### Test Completo Sistema (v2.3.0+)
Il test integrato ora legge la configurazione relay dal database:

```python
# hardware_tests.py - test_integrated()
# Legge configurazione relay dinamicamente
cursor.execute("SELECT * FROM relay_config")
relay_config = cursor.fetchall()

# Applica configurazione per ogni dispositivo
for relay in relay_config:
    relay_num = relay[0]  # numero relay
    device = relay[1]      # dispositivo
    command = relay[3]     # comando attivazione
```

## Test Accessi e Gestione Ingressi Aggiuntivi (v2.8.0+)

### Nuove Funzionalità Test Accessi
La sezione Test Accessi nella configurazione orari ora include:

#### Visualizzazione Progress Bar
- Campo read-only con progress bar gradiente (verde→giallo→rosso)
- Mostra automaticamente accessi/limite quando si seleziona un utente
- Endpoint: `POST /api/configurazione/utente-info-accessi`

```javascript
// Caricamento automatico info utente
await this.caricaInfoAccessi(codice_fiscale);
// Aggiorna progress bar con colori gradiente
this.aggiornaProgressBar(data);
```

#### Concessione Ingressi Aggiuntivi
- Campo abilitato SOLO quando l'utente raggiunge il limite
- Resetta il contatore per permettere N accessi extra
- Endpoint: `POST /api/configurazione/test/aggiungi-ingressi`

```python
# Se limite=5 e utente ha 5 accessi, concedendo +2:
nuovo_contatore = max(0, limite - ingressi_aggiuntivi)  # 5-2=3
# L'utente potrà fare altri 2 accessi prima di raggiungere nuovamente il limite
```

#### Simulazione Accesso (NO LOG)
- Verifica accessibilità senza modificare contatori
- Non registra nei log_accessi
- Endpoint: `POST /api/configurazione/test/simula-accesso`

```python
# Solo verifica, non modifica:
if ingressi_attuali >= limite:
    return jsonify({
        'accesso_consentito': False,
        'motivo_rifiuto': f'Limite mensile di {limite} ingressi raggiunto'
    })
# NON incrementa contatore, NON registra log
```

### Database - Tabelle Utilizzate
- `conteggio_ingressi_mensili`: Contatore accessi mensili
- `limiti_accesso`: Limite massimo ingressi mensili  
- `log_forzature`: Log concessioni ingressi extra con motivazione

### Controller Relè USB-RLY08
```python
from hardware.usb_rly08_controller import USBRLY08Controller

controller = USBRLY08Controller()
controller.connect('/dev/ttyUSB0')
controller.activate_relay(1, duration=3)  # Relay 1, 3 secondi
controller.disconnect()
```

## 🐛 Debug e Testing

### Console Log Real-time
- Disponibile in `/admin/config` → tab "Debug"
- WebSocket streaming dei log di sistema
- Pulsante riavvio servizio integrato

### Test Hardware
```bash
# Test lettore tessere
python3 src/hardware/test_crt285.py

# Test relè
python3 src/hardware/test_usb_rly08.py

# Test gate completo
curl -X POST http://localhost:5000/api/test-gate
```

### Log Files
```bash
# Log applicazione
tail -f /opt/access_control/logs/access_control.log

# Log systemd service
journalctl -u access-control-web -f
```

## 📦 Deployment

### Service systemd
```bash
# File: /etc/systemd/system/access-control-web.service
# Gira come root per accesso USB

sudo systemctl daemon-reload
sudo systemctl restart access-control-web
sudo systemctl status access-control-web
```

### Backup Database
```bash
# Backup manuale
cp data/database.db data/backup_$(date +%Y%m%d_%H%M%S).db

# Via API
curl -X POST http://localhost:5000/api/backup/create
```

## 🎯 Best Practices

### 1. Modifiche Database
- Sempre usare `get_db_connection()` 
- Chiudere sempre le connessioni
- Usare parametri preparati (no SQL injection)

### 2. Modifiche UI
- Template in `dashboard_templates.py` per admin
- CSS in `/static/css/dashboard.css`
- JS modulare in `/static/js/`

### 3. Nuove Feature
- Aggiungere route in `web_api.py`
- Documentare in CHANGELOG.md
- Testare con script in `/tmp/`
- Per modifiche ai template, forzare reload con `sudo systemctl restart access-control-web`

### 4. Git Workflow
```bash
# Branch sviluppo
git checkout -b feature/nome-feature

# Commit atomici
git add -A
git commit -m "feat: descrizione feature"

# Push to GitHub
git push origin feature/nome-feature
```

## 📦 Sistema Backup

### Flask Blueprint Disponibili
- **profilo_bp**: Gestione profilo utente corrente
- **user_management_bp**: Gestione utenti sistema 
- **log_management_bp**: Gestione e visualizzazione log
- **utenti_autorizzati_bp**: Gestione utenti abilitati accesso fisico
- **system_users_bp**: Gestione utenti di sistema
- **activities_bp**: Log attività e azioni
- **configurazione_accessi_bp**: Configurazione orari, limiti, test
- **backup_bp**: Gestione backup e restore
- **sync_bp**: Gestione sincronizzazione server (Odoo)

### Architettura
Il sistema di backup è modulare e supporta:
- **Backup locali**: Completi (sistema + DB) o solo database
- **Backup cloud**: AWS S3, Google Cloud, Azure, FTP/SFTP
- **Schedulazione**: Giornaliera, settimanale, mensile, annuale
- **Retention policies**: Automatiche con cleanup configurabile
- **Verifica integrità**: Controllo checksum MD5 periodico

### File Principali
- `src/api/backup_module.py`: Core del sistema backup (Blueprint Flask)
- `src/api/admin_templates.py`: Template UI (sezione ADMIN_BACKUP_TEMPLATE)
- `backups/`: Directory backup locali
- `backups/backup_config.json`: Configurazione backup

### API Endpoints
```python
/api/backup/status              # GET - Stato generale
/api/backup/create               # POST - Crea backup
/api/backup/delete/<filename>    # DELETE - Elimina backup
/api/backup/restore/<filename>   # POST - Ripristina backup
/api/backup/download/<filename>  # GET - Download backup
/api/backup/config               # POST - Salva configurazione
/api/backup/cloud/sync           # POST - Sync cloud
/api/backup/integrity/check      # POST - Verifica integrità
/api/backup/retention/apply      # POST - Applica retention
```

### Configurazione Cloud Providers
```python
# FTP/SFTP
{
    "host": "ftp.example.com",
    "port": 21,
    "username": "user",
    "password": "pass",
    "path": "/backups"
}

# AWS S3
{
    "access_key": "AKIA...",
    "secret_key": "...",
    "bucket": "my-backups",
    "region": "eu-west-1"
}
```

### Testing Backup
```bash
# Test creazione backup
curl -X POST http://localhost:5000/api/backup/create

# Test verifica integrità
curl -X POST http://localhost:5000/api/backup/integrity/check

# Test retention
curl -X POST http://localhost:5000/api/backup/retention/apply
```

## 🔄 Sistema Server Sync

### Architettura
Il sistema di sincronizzazione server gestisce:
- **Connessione Server Remoto**: Configurazione dinamica dei parametri di connessione
- **Sincronizzazione automatica**: Schedulazione configurabile (1h, 6h, 12h, 24h, custom)
- **Database storage**: Configurazione salvata in `system_settings` invece che JSON
- **Log real-time**: Monitoraggio live delle operazioni di sincronizzazione

### File Principali
- `src/api/modules/sync_module.py`: Core della sincronizzazione (Blueprint Flask)
- `src/api/admin_templates.py`: Template UI (sezione ADMIN_SERVER_SYNC_TEMPLATE)
- `src/external/odoo_partner_connector.py`: Connettore per sincronizzazione cittadini
- Database: `system_settings` table con chiavi `sync.*`

### API Endpoints
```
/sync/config     # GET/POST - Configurazione server
/sync/status     # GET - Stato connessione
/sync/test       # POST - Test connessione
/sync/manual     # POST - Sincronizzazione manuale
/sync/schedule   # POST - Schedulazione automatica
/sync/logs       # GET - Log sincronizzazione
```

### Configurazione Database
Le configurazioni sono salvate nella tabella `system_settings`:
- `sync.url`: URL server remoto
- `sync.database`: Nome database
- `sync.username`: Username
- `sync.password`: Password (criptata)
- `sync.comune`: Filtro comune (default: Rende)
- `sync.sync_enabled`: Abilitazione sync automatica
- `sync.sync_interval_hours`: Intervallo in ore
- `sync.last_sync`: Timestamp ultima sincronizzazione

### Accesso UI
- **Tab in Configurazioni**: `/admin/config` → tab "Server Sync"
- **Pagina dedicata**: `/admin/sync`

## 🔍 Troubleshooting Comune

### Problema: Timestamp sbagliati nei log
**Soluzione**: Verificare configurazione timezone in `/admin/config` → "Orologio"

### Problema: Export non funziona
**Soluzione**: Verificare installazione `reportlab` per PDF:
```bash
source venv/bin/activate
pip install reportlab==4.0.4
```

### Problema: Lettore tessere non risponde
**Soluzione**: 
1. Verificare device `/dev/ttyACM0`
2. Controllare permessi (servizio deve girare come root)
3. Test manuale: `python3 src/hardware/test_crt285.py`

### Problema: Relè non si attivano
**Soluzione**:
1. Verificare device `/dev/ttyUSB0`
2. Controllare configurazione in database `relay_config`
3. Test via API: `/api/test-gate`

## 📞 Contatti e Supporto

Per problemi o domande sul sistema:
1. Controllare i log in `/opt/access_control/logs/`
2. Verificare status servizio: `sudo systemctl status access-control-web`
3. Consultare CHANGELOG.md per ultime modifiche
4. GitHub Issues per segnalazioni

---

## 👥 Sistema Gestione Utenti Autorizzati

### Architettura
Il sistema di gestione utenti autorizzati gestisce:
- **Visualizzazione utenti**: Lista completa con ricerca e filtri
- **Paginazione dinamica**: Supporto per 30, 50, 100 elementi o tutti
- **Gestione stato**: Attivazione/disattivazione utenti
- **Formato date**: Visualizzazione completa con data e ora

### File Principali
- `src/api/modules/utenti_autorizzati.py`: Blueprint Flask per gestione utenti
- `src/api/templates/utenti_autorizzati.html`: Template HTML della pagina
- `src/api/static/js/utenti_autorizzati.js`: Logica JavaScript frontend

### API Endpoints
```python
/api/utenti-autorizzati/list     # GET - Lista con paginazione e ricerca
/api/utenti-autorizzati/stats    # GET - Statistiche utenti
/api/utenti-autorizzati/toggle-active  # POST - Attiva/disattiva utente
```

### Paginazione
La paginazione supporta:
- Query parameter `page`: numero pagina (default: 1)
- Query parameter `per_page`: elementi per pagina (30, 50, 100, 'all')
- Query parameter `search`: filtro per nome o codice fiscale

### Formato Date
Le date vengono visualizzate in formato italiano completo:
```javascript
// Formato: DD/MM/YYYY HH:MM:SS
date.toLocaleString('it-IT', {
    day: '2-digit',
    month: '2-digit', 
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
});
```

---

## 🎨 Miglioramenti UI Dashboard (v2.7.1)

### Modifiche Dashboard
- **Rimosso pulsante Test Accessi**: Eliminato dalla sezione admin per ridurre ridondanza
- **Uniformati colori pulsanti**: Schema colori coerente per tutti i pulsanti dashboard
  - Blu (primary): Navigazione principale
  - Verde (success): Azioni positive (Backup, Export)
  - Rosso (danger): Azioni critiche

### File Modificati
- `/src/api/web_api.py`: Rimosso Test Accessi dai menu_items
- `/src/api/dashboard_templates.py`: Aggiornati stili pulsanti

---

## 👤 Sistema Profili Utente (v2.7.0)

### Campi Profilo Estesi
La tabella `utenti_sistema` è stata estesa con nuovi campi profilo:

```sql
-- Nuovi campi profilo
nome            TEXT    -- Nome utente
cognome         TEXT    -- Cognome utente  
avatar_path     TEXT    -- Path immagine profilo
telefono        TEXT    -- Numero telefono
bio             TEXT    -- Biografia/descrizione
data_nascita    DATE    -- Data di nascita
indirizzo       TEXT    -- Indirizzo
```

### Upload Avatar
Il sistema supporta l'upload di immagini profilo:
- **Formati supportati**: jpg, jpeg, png, gif, webp
- **Directory storage**: `/opt/access_control/src/api/static/avatars/`
- **Avatar default**: `/api/static/img/default-avatar.png`
- **Naming convention**: `{username}_{uuid}_{ext}`

### Endpoint API Profili

```javascript
// Aggiornamento profilo con FormData (supporta upload file)
POST /api/users/update-profile
Content-Type: multipart/form-data
{
    username: string,
    nome: string,
    cognome: string,
    email: string,
    telefono: string,
    bio: string,
    avatar: File (optional)
}
```

### Password Management
Sistema completo di gestione password con:
- **Validazione rigorosa**: min 8 caratteri, maiuscole, minuscole, numeri, caratteri speciali
- **Reset via email**: Token sicuri con scadenza 24h
- **Password history**: Previene riutilizzo password recenti
- **Cambio obbligatorio**: Flag per forzare cambio al prossimo login
- **Account lockout**: Blocco dopo tentativi falliti

#### Endpoint Password Management
```javascript
// Admin imposta password diretta
POST /api/users/admin-set-password
{
    username: string,
    password: string,
    must_change_password: boolean
}

// Invia link reset password
POST /api/users/send-reset-link
{
    username: string,
    custom_message: string (optional)
}
```

### Frontend Components

#### Modal Modifica Profilo
- Layout a due colonne con preview avatar
- Upload immagine con anteprima real-time
- Campi: nome, cognome, email, telefono, bio
- Rimosso campo password (gestito separatamente)

#### Form Creazione Utente
- Aggiunti campi nome e cognome
- Validazione password real-time
- Indicatore forza password
- Requisiti password visualizzati dinamicamente

---

## 🗄️ Gestione Database

### Migrazione Path Database (v2.6.0)
Il database è stato migrato dalla cartella `/src` alla cartella `/data` per una migliore organizzazione:

#### Configurazione Centralizzata
```python
# File: src/core/db_config.py
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = str(PROJECT_ROOT / "data" / "access.db")
OLD_DB_PATH = str(PROJECT_ROOT / "src" / "access.db")  # Per retrocompatibilità

def get_db_path():
    """Restituisce il percorso corretto del database"""
    if os.path.exists(DB_PATH):
        return DB_PATH
    elif os.path.exists(OLD_DB_PATH):
        return OLD_DB_PATH
    return DB_PATH

CURRENT_DB_PATH = get_db_path()
```

#### Utilizzo nei Moduli
```python
# Invece di hardcodare il path:
# DB_PATH = '/opt/access_control/src/access.db'

# Usa la configurazione centralizzata:
from core.db_config import CURRENT_DB_PATH as DB_PATH

conn = sqlite3.connect(DB_PATH)
```

#### Vantaggi della Migrazione
- **Separazione codice/dati**: Il codice sorgente non contiene più file di dati
- **Backup semplificato**: Tutti i dati sono in `/data`
- **Gestione centralizzata**: Un solo punto per configurare il path
- **Retrocompatibilità**: Supporta ancora il vecchio path se necessario

---

**Ultimo aggiornamento**: 2025-09-06 - Versione 2.6.0