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
│   │   └── config.py               # Configurazioni
│   └── hardware/
│       ├── crt285_controller.py    # Controller lettore tessere
│       └── usb_rly08_controller.py # Controller relè
├── data/
│   ├── database.db                 # Database SQLite
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
journalctl -u controllo-accessi -f
```

## 📦 Deployment

### Service systemd
```bash
# File: /etc/systemd/system/controllo-accessi.service
# Gira come root per accesso USB

sudo systemctl daemon-reload
sudo systemctl restart controllo-accessi
sudo systemctl status controllo-accessi
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
2. Verificare status servizio: `sudo systemctl status controllo-accessi`
3. Consultare CHANGELOG.md per ultime modifiche
4. GitHub Issues per segnalazioni

---

**Ultimo aggiornamento**: 2025-09-05 - Versione 2.1.0