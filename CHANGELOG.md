# 📝 CHANGELOG - Sistema Controllo Accessi

## [2.9.1] - 2025-09-08

### ✨ Nuove Funzionalità
- **Configurazione Email SMTP Completa**
  - Nuovo modulo `email_config.py` per gestione centralizzata SMTP
  - Endpoint `/api/email/config` per GET/POST configurazioni
  - Test invio email con endpoint `/api/email/test`
  - UI integrata in Admin/Config con tab Email dedicato

### 🔧 Miglioramenti
- **Email con Nome Installazione Dinamico**
  - Rimosso testo hardcoded "Isola Ecologica RAEE - Rende"
  - Tutte le email usano ora `sistema.nome_installazione` dal database
  - Applicato a: email test, reset password, notifiche admin

- **Frontend Email Configuration**
  - Form completo con tutti i campi SMTP necessari
  - Supporto STARTTLS, SSL, autenticazione
  - Feedback visivo per salvataggio e test
  - Password mascherata per sicurezza

### 🐛 Bug Fix
- **Risolto problema salvataggio configurazione email**
  - Aggiunto blueprint `email_config_bp` mancante
  - Creata tabella `system_settings` se non esistente
  - Migliorata gestione sessioni con `credentials: 'include'`
  - Aggiunto controllo esistenza form prima del binding eventi

### 📚 Documentazione
- Aggiornati endpoint API email in `API_DOCUMENTATION.md`
- Documentate nuove funzionalità configurazione SMTP
- Aggiornata versione API a 2.9.1

## [2.9.0] - 2025-09-08

### ✨ Nuove Funzionalità
- **Sistema Backup & Restore Completo**
  - Backup completo (codice, DB, config, log) e solo database
  - Ripristino con verifica checksum MD5 obbligatoria
  - Download diretto dei backup dalla UI
  - Gestione backup mancanti con messaggi warning

- **Backup Automatici con Crontab**
  - Schedulazione giornaliera, settimanale, mensile e annuale
  - Configurazione via UI con salvataggio immediato
  - Script Python `auto_backup.py` per esecuzione automatica
  - Log automatici in `/opt/access_control/logs/auto_backup.log`

- **Verifica Integrità Backup**
  - Controllo checksum MD5 per tutti i backup
  - Report dettagliato: validi, corrotti, senza checksum
  - Operazioni asincrone con progress tracking

- **Gestione Retention Policy**
  - Pulizia automatica backup vecchi
  - Limiti configurabili per tipo (giornaliero, settimanale, mensile)
  - Controllo spazio disco massimo

- **Backup Database con Checksum**
  - Aggiunto checksum MD5 per backup database
  - Abilitato restore per database con verifica integrità
  - Backup automatico pre-ripristino

### 🔧 Miglioramenti
- **UI Backup Migliorata**
  - Tabella backup con icone stato checksum
  - Visualizzazione spazio disco reale (include spazio riservato)
  - Auto-refresh ogni 30 secondi
  - Alert Bootstrap invece di popup

- **Gestione Errori Avanzata**
  - Eliminazione file mancanti senza errori
  - Messaggi warning differenziati da errori
  - Validazione percorsi per sicurezza

- **JavaScript Completamente Riscritto**
  - `backup.js` v2.0 allineato con template HTML
  - Tutte le funzioni implementate e testate
  - Gestione operazioni asincrone
  - Sistema notifiche integrato

### 🐛 Bug Fix
- Corretto nome checksum (era `.tar.tar.gz.md5` ora `.tar.gz.md5`)
- Fix lettura parametro tipo backup dal JSON POST
- Corretto crontab con newline finale obbligatoria
- Fix percorsi sicuri per prevenire path traversal
- Gestione file orfani nella verifica integrità

### 📚 Documentazione
- Aggiornata API documentation con tutti gli endpoint backup
- Documentati tutti i parametri e response
- Aggiunti esempi cURL per testing

### 🔒 Sicurezza
- Checksum MD5 obbligatorio per ripristino
- Blocco ripristino in ambiente produzione
- Validazione percorsi file
- Backup automatico prima di ogni ripristino

---

## [2.8.1] - 2025-09-06
### ✨ Funzionalità
- Nome Installazione Dinamico

## [2.8.0] - 2025-09-06  
### ✨ Funzionalità
- Test Accessi Avanzato
- Gestione Ingressi Extra

## [2.7.1] - 2025-09-05
### 🔧 Miglioramenti
- Pulizia e uniformità UI Dashboard

---

## Note Tecniche

### File Modificati
- `/src/api/backup_module.py` - Modulo backup completo
- `/src/api/static/js/backup.js` - JavaScript UI backup
- `/src/api/admin_templates.py` - Template pagina backup
- `/scripts/auto_backup.py` - Script backup automatici
- `/scripts/fix_checksums.py` - Utility fix checksum
- `/scripts/add_db_checksums.py` - Utility checksum DB

### Configurazioni
- Backup config: `/opt/access_control/backups/backup_config.json`
- Log automatici: `/opt/access_control/logs/auto_backup.log`
- Directory backup: `/opt/access_control/backups/`

### Crontab Esempio
```bash
00 02 * * * cd /opt/access_control && /usr/bin/python3 scripts/auto_backup.py database
00 03 * * 0 cd /opt/access_control && /usr/bin/python3 scripts/auto_backup.py complete
00 04 1 * * cd /opt/access_control && /usr/bin/python3 scripts/auto_backup.py complete
```