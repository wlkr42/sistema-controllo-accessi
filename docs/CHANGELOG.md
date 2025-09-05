# Changelog - Sistema Controllo Accessi

## [2.1.0] - 2025-09-05

### 🎉 Nuove Funzionalità

#### 🕐 Configurazione Orologio e Timezone
- **Nuova sezione "Orologio"** nella pagina di configurazione admin (`/admin/config`)
- Gestione completa del timezone del sistema:
  - Selezione timezone (Europe/Rome di default)
  - Formato data (DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD)  
  - Formato ora (24 ore o 12 ore AM/PM)
  - Configurazione server NTP
  - Display ora corrente del sistema in tempo reale
- **API Endpoints** per configurazione orologio:
  - `GET /api/admin/clock-config` - recupera configurazione
  - `POST /api/admin/clock-config` - salva configurazione
  - `GET /api/server-time` - ora server con timezone configurato

#### 📊 Sistema Esportazioni Log Accessi
- **Esportazione in 3 formati** dalla pagina Log Accessi:
  - **CSV**: File di testo con valori separati da virgola
  - **Excel (.xlsx)**: File Excel nativo con formattazione professionale
  - **PDF**: Documento PDF con tabella formattata in landscape
- **Endpoint unificato**: `/api/log-accessi/export?format={csv|excel|pdf}`
- Conversione automatica timestamp da UTC a timezone configurato
- Gestione intelligente dei dati mancanti

### 🐛 Bug Fix

#### Correzione Timestamp Log Accessi
- **Problema**: I log mostravano l'ora UTC invece dell'ora locale (2 ore indietro)
- **Soluzione**: 
  - Implementata conversione automatica da UTC a timezone configurato
  - Tutti i timestamp ora mostrano l'ora corretta secondo il timezone impostato
  - La conversione avviene sia nella visualizzazione che nelle esportazioni

#### Correzione Display Log Accessi
- **Nome Utente**: Ora mostra correttamente il nome dalla tabella utenti_autorizzati
- **Durata**: Visualizzazione corretta del tempo di elaborazione in millisecondi
- **Tipo Accesso**: Mapping corretto dei tipi (AUTORIZZATO, UTENTE_NON_TROVATO, etc.)
- **Terminale**: Utilizza il nome configurato in "Nome Installazione"

### 🔧 Miglioramenti Tecnici

#### Database
- Nuove chiavi in `system_settings`:
  - `sistema.timezone` - Timezone del sistema
  - `sistema.formato_data` - Formato visualizzazione data
  - `sistema.formato_ora` - Formato visualizzazione ora (12/24)
  - `sistema.ntp_enabled` - Abilitazione sincronizzazione NTP
  - `sistema.ntp_server` - Server NTP da utilizzare

#### Dipendenze
- Aggiunto `reportlab==4.0.4` per generazione PDF
- `openpyxl` già presente per Excel
- `pandas` disponibile per elaborazione dati

### 📝 Note per gli Sviluppatori

#### Gestione Timezone
```python
# Pattern per conversione timestamp da UTC a timezone configurato
import pytz
from datetime import datetime

# Recupera timezone configurato
timezone_name = 'Europe/Rome'  # Default
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT value FROM system_settings WHERE key = 'sistema.timezone'")
result = cursor.fetchone()
if result:
    timezone_name = result[0]

# Converti timestamp
tz = pytz.timezone(timezone_name)
utc = pytz.utc
dt_utc = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
dt_utc = utc.localize(dt_utc)
dt_local = dt_utc.astimezone(tz)
timestamp_converted = dt_local.strftime('%Y-%m-%d %H:%M:%S')
```

#### Esportazioni
- CSV: Usa `io.StringIO()` e `csv.writer`
- Excel: Usa `openpyxl.Workbook` con stili
- PDF: Usa `reportlab` con `SimpleDocTemplate` e `Table`

### 🚀 Deployment

1. **Installare dipendenze**:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Riavviare servizio**:
   ```bash
   sudo systemctl restart controllo-accessi
   ```

3. **Verificare configurazione**:
   - Accedere a `/admin/config`
   - Verificare sezione "Orologio"
   - Testare esportazioni da Log Accessi

## [2.0.0] - 2025-09-04

### Sistema Debug Completo
- Console log in tempo reale
- Stato sistema con monitoring servizi
- Riavvio servizio da interfaccia web
- WebSocket per streaming log

### Servizio Systemd Root
- Operazione come root per accesso USB
- Gestione automatica permessi
- Restart automatico in caso di errore

### Test Hardware Migliorati  
- Test connessione lettore tessere
- Test controller relè USB-RLY08
- Diagnostica completa hardware

## [1.0.0] - 2025-09-03

### Release Iniziale
- Sistema base controllo accessi
- Lettore tessere CRT-285  
- Controller relè USB-RLY08
- Database SQLite
- Interfaccia web Flask
- Autenticazione utenti
- Configurazione orari accesso