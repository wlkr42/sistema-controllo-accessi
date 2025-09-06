# Changelog - Sistema Controllo Accessi

## [2.5.0] - 2025-09-06

### 🎉 Nuove Funzionalità

#### 🔄 Sistema Server Sync
- **Configurazione Dinamica Server**:
  - Gestione parametri connessione da interfaccia web
  - Salvataggio configurazione in database (system_settings)
  - Test connessione integrato
  - Log real-time delle operazioni

- **Sincronizzazione Automatica**:
  - Schedulazione configurabile (ore personalizzabili)
  - Sincronizzazione manuale on-demand
  - Import automatico cittadini autorizzati
  - Statistiche dettagliate sincronizzazione

- **Interfaccia Dedicata**:
  - Tab "Server Sync" in configurazione admin
  - Dashboard stato connessione
  - Visualizzazione log sincronizzazione
  - Controlli abilitazione/disabilitazione

#### 👥 Miglioramenti Gestione Utenti Autorizzati
- **Sistema Paginazione**:
  - Dropdown selezione elementi (30, 50, 100, tutti)
  - Navigazione pagine con controlli avanzati
  - Indicatore elementi visualizzati
  - Mantenimento stato ricerca

- **Visualizzazione Date Corretta**:
  - Formato italiano completo (DD/MM/YYYY HH:MM:SS)
  - Visualizzazione data e ora inserimento reale
  - Aggiornamento timestamp consistente

- **Interfaccia Ottimizzata**:
  - Rimosse colonne non necessarie (Modificato Da, Stato)
  - Evidenziazione righe utenti inattivi
  - Migliorata responsività tabella

### 🐛 Bug Fix
- Corretta visualizzazione date inserimento utenti
- Fix formato timestamp in formato italiano
- Risolto problema colonne duplicate non necessarie
- Corretto salvataggio configurazione Server Sync in database

### 🔧 Miglioramenti Tecnici
- Migrazione configurazione sync da JSON a database
- Nuovo modulo `sync_module.py` con gestione database
- JavaScript ottimizzato per paginazione (`utenti_autorizzati.js`)
- API endpoint con supporto paginazione nativo
- Blueprint Flask per modularità codice

## [2.4.0] - 2025-09-06

### 🎉 Nuove Funzionalità

#### 📦 Sistema Backup Enterprise Completo
- **Schedulazione Multi-livello**:
  - Backup giornalieri, settimanali, mensili e annuali
  - Configurazione indipendente per ogni livello
  - Tipo di backup configurabile (database/completo)
  - Retention personalizzata per ogni schedulazione

- **Cloud Backup Integrato**:
  - Supporto AWS S3, Google Cloud Storage, Azure, FTP/SFTP
  - Sincronizzazione automatica post-backup
  - Configurazione credenziali sicura
  - Upload incrementale

- **Verifica Integrità Automatica**:
  - Controllo checksum MD5 periodico
  - Alert automatici per backup corrotti
  - Report dettagliato integrità
  - Schedulazione configurabile

- **Politiche Retention Avanzate**:
  - Cleanup automatico basato su età
  - Limite spazio disco configurabile
  - Retention differenziata per tipo
  - Applicazione manuale o automatica

- **Interfaccia Migliorata**:
  - Dashboard con schede per ogni tipo di schedulazione
  - Configurazione cloud provider visuale
  - Monitoraggio integrità in tempo reale
  - Gestione backup con eliminazione funzionante

### 🐛 Bug Fix
- Corretto endpoint `/api/backup/delete` mancante
- Aggiunto endpoint `/api/backup/restore` mancante
- Fix gestione errori eliminazione backup
- Migliorata gestione permessi file backup
- Aggiunto reload forzato template per sviluppo

### 🔧 Miglioramenti Tecnici
- Nuovo modulo `backup_module.py` con Blueprint Flask
- Template `ADMIN_BACKUP_TEMPLATE` completamente ridisegnato
- Funzioni JavaScript per gestione cloud e integrità
- Logging dettagliato per debug operazioni
- Supporto operazioni asincrone in background

### 📚 Documentazione
- Aggiunta sezione completa Sistema Backup in DEVELOPER_GUIDE.md
- Documentati tutti gli endpoint API backup
- Esempi configurazione cloud providers
- Guide troubleshooting specifiche

## [2.3.0] - 2025-09-06

### 🎉 Nuove Funzionalità

#### 🕐 Allineamento Timezone Ultimi Accessi
- **Dashboard Ultimi Accessi** ora usa il timezone configurato nel sistema
- Gli orari visualizzati rispettano la configurazione "Orologio" nelle impostazioni admin
- Rimossa conversione timezone lato client che causava discrepanze

#### 🔧 Test Completo Sistema Migliorato
- **Configurazione dinamica relay** letta dal database
- Il test ora usa la mappatura relay configurata nel sistema
- Supporto completo per configurazioni personalizzate hardware

### 🐛 Bug Fix
- Corretto errore `get_clock_config` non definito nell'API recent-accesses
- Sistemato allineamento orari tra dashboard e configurazione sistema
- Fix formattazione timestamp secondo configurazione sistema (24h/12h)

### 🔧 Miglioramenti Tecnici
- API `/api/recent-accesses` ora legge configurazione timezone da `system_settings`
- JavaScript dashboard usa campo `time_formatted` dal server
- Eliminata dipendenza da timezone del browser per visualizzazione orari

## [2.2.0] - 2025-09-06

### 🎉 Nuove Funzionalità

#### 🔍 Test Lettore Tessere Migliorato
- **Monitoraggio database real-time** senza interferire con il lettore hardware
- **Visualizzazione dettagliata motivazioni rifiuto**:
  - "Limite mensile accessi superato"
  - "Utente disattivato"
  - "Tessera non registrata"
  - "Accesso non consentito in questo orario"
- **Pulsante Stop funzionante** per interrompere il test
- **Nessuna interferenza** con il sistema principale operativo
- Il test ora legge direttamente dalla tabella `log_accessi` i campi:
  - `motivo_rifiuto`: per la motivazione del rifiuto
  - `nome_utente`: per il nome dell'utente

### 🐛 Bug Fix
- Corretto errore JSON parsing nel pulsante Stop del test lettore
- Rimossa inizializzazione hardware nel test lettore che disattivava il sistema principale
- Aggiunto header Content-Type nelle chiamate API JavaScript
- Corretto endpoint `/api/hardware/stop-reader` che chiamava funzione inesistente

### 🔧 Miglioramenti Tecnici
- Refactoring completo della funzione `test_reader()` in `hardware_tests.py`
- Aggiunta funzione `stop_reader()` per gestire interruzione test
- Migliorata gestione errori nel JavaScript del dashboard
- Aggiunto logging dettagliato nella console per debug

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
   sudo systemctl restart access-control-web
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