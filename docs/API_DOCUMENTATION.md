# 📡 API Documentation - Sistema Controllo Accessi

## Base URL
```
http://localhost:5000
```

## Authentication
Il sistema utilizza session-based authentication. Dopo il login, viene impostato un cookie di sessione che deve essere incluso in tutte le richieste successive.

---

## 🔐 Security & Configuration

### Password Field Handling
Tutti i campi password nel sistema seguono queste regole di sicurezza:

- **Backend**: Non restituisce mai password in chiaro (ritorna `'********'` se presente)
- **Frontend**: Mostra pallini `••••••••` quando password salvata
- **Interazione**: Click sul campo pulisce automaticamente per nuova password
- **Salvataggio**: Non invia i pallini se password non modificata

## 📊 System Monitoring Endpoints

### GET `/api/system-status`
Restituisce lo stato del sistema con metriche real-time.

**Requires:** Admin permission

**Response:**
```json
{
  "success": true,
  "service_running": true,
  "reader_connected": true,
  "reader_type": "CRT-285",
  "relay_connected": true,
  "database_ok": true,
  "uptime": "2h 34m",
  "ram_percent": 63.5,
  "version": "v2.9.3",
  "cpu_percent": 12.3
}
```

**Fields:**
- `uptime`: Tempo di attività formattato (s/m/h/g)
- `ram_percent`: Percentuale RAM utilizzata (0-100)
- `cpu_percent`: Percentuale CPU utilizzata (0-100)
- `version`: Versione corrente del sistema

### GET `/api/system-logs`
Recupera i log di sistema.

**Query Parameters:**
- `lines` (int, optional): Numero di righe da recuperare (default: 30, max: 2000)

**Response:**
```json
{
  "success": true,
  "logs": [
    "Sep 08 16:37:24 python[846268]: INFO:werkzeug:192.168.1.73 - - [08/Sep/2025 16:37:24] \"GET /api/system-logs?lines=2000 HTTP/1.1\" 200 -",
    "Sep 08 16:37:25 python[846268]: INFO:Access granted for user RSSMRA80A01H501Z"
  ]
}
```

**Note v2.9.2+:**
- Limite aumentato da 100 a 2000 righe per debug esteso
- Console debug potenziata con più informazioni di sistema

---

## 🔐 Authentication Endpoints

### POST `/login`
Effettua il login al sistema.

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
- **200 OK**: Login riuscito, redirect a dashboard
- **401 Unauthorized**: Credenziali errate

### GET `/logout`
Termina la sessione corrente.

**Response:**
- **302 Found**: Redirect a login page

### GET `/api/user-info`
Recupera informazioni utente corrente.

**Response:**
```json
{
  "username": "admin",
  "role": "admin",
  "permissions": ["all"],
  "last_login": "2025-09-05T10:30:00"
}
```

---

## 📊 Dashboard Endpoints

### GET `/api/recent-accesses`
Recupera gli accessi recenti per la dashboard.

**Query Parameters:**
- `limit` (int): Numero massimo di risultati (default: 10)

**Response:**
```json
{
  "accesses": [
    {
      "timestamp": "2025-09-06T10:30:00",
      "timestamp_formatted": "06/09/2025 10:30:00",
      "time_formatted": "10:30:00",
      "date_formatted": "06/09/2025",
      "codice_fiscale": "RSSMRA85M01H501Z",
      "nome": "Mario Rossi",
      "autorizzato": true,
      "motivo_rifiuto": null
    },
    {
      "timestamp": "2025-09-06T10:25:00",
      "codice_fiscale": "VRDGPP90A01H501A",
      "nome": "Giuseppe Verdi",
      "autorizzato": false,
      "motivo_rifiuto": "Limite mensile accessi superato"
    }
  ]
}
```

**Note v2.3.0+:**
- Il campo `time_formatted` usa il timezone configurato nel sistema
- Il formato ora rispetta la configurazione 24h/12h delle impostazioni
- Non più dipendente dal timezone del browser

## 📊 Log Accessi Endpoints

### GET `/api/log-accessi`
Recupera log accessi con filtri e paginazione.

**Query Parameters:**
- `page` (int): Numero pagina (default: 1)
- `periodo` (string): oggi|settimana|mese|custom (default: mese)
- `data_inizio` (date): Data inizio per periodo custom
- `data_fine` (date): Data fine per periodo custom
- `tipo` (string): Filtra per tipo_accesso
- `codice_fiscale` (string): Filtra per codice fiscale

**Response:**
```json
{
  "logs": [
    {
      "id": 1,
      "timestamp": "2025-09-05 12:30:00",
      "codice_fiscale": "RSSMRA85M01H501Z",
      "nome_utente": "Mario Rossi",
      "autorizzato": true,
      "tipo_accesso": "AUTORIZZATO",
      "terminale_id": "Isola Ecologica Rende",
      "durata_elaborazione": 0.125
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 10,
    "total_records": 500,
    "records_per_page": 50
  },
  "stats": {
    "autorizzati": 450,
    "negati": 50,
    "fuori_orario": 20,
    "limite_superato": 10
  }
}
```

### GET `/api/log-accessi/export`
Esporta log accessi in vari formati.

**Query Parameters:**
- `format` (string): csv|excel|pdf (required)
- Altri parametri come `/api/log-accessi`

**Response:**
- **CSV**: `Content-Type: text/csv`
- **Excel**: `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **PDF**: `Content-Type: application/pdf`

---

## ⚙️ Configuration Endpoints

### GET `/api/admin/clock-config`
Recupera configurazione orologio sistema.

**Response:**
```json
{
  "success": true,
  "config": {
    "timezone": "Europe/Rome",
    "formato_data": "DD/MM/YYYY",
    "formato_ora": "24",
    "ntp_enabled": true,
    "ntp_server": "pool.ntp.org"
  }
}
```

### POST `/api/admin/clock-config`
Salva configurazione orologio sistema.

**Request Body:**
```json
{
  "timezone": "Europe/Rome",
  "formato_data": "DD/MM/YYYY",
  "formato_ora": "24",
  "ntp_enabled": true,
  "ntp_server": "pool.ntp.org"
}
```

**Response:**
```json
{
  "success": true
}
```

### GET `/api/server-time`
Recupera ora corrente del server.

**Response:**
```json
{
  "time": "12:30:45",
  "date": "05/09/2025",
  "weekday": "Venerdì",
  "timestamp": "2025-09-05T12:30:45.123456+02:00",
  "timezone": "Europe/Rome"
}
```

---

## 📧 Email Configuration Endpoints

### GET `/api/email/config`
Recupera configurazione SMTP per invio email.

**Response:**
```json
{
  "success": true,
  "config": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": "587",
    "smtp_security": "STARTTLS",
    "username": "user@gmail.com",
    "password": "********",  // Mascherata per sicurezza
    "mittente": "noreply@sistema.local",
    "nome_mittente": "Sistema Controllo Accessi",
    "enabled": "1"
  }
}
```

### POST `/api/email/config`
Salva configurazione SMTP.

**Request Body:**
```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": "587",
  "smtp_security": "STARTTLS",  // STARTTLS, SSL, NONE
  "username": "user@gmail.com",
  "password": "password123",
  "mittente": "noreply@sistema.local",
  "enabled": "1"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Configurazione email salvata (7 campi aggiornati)"
}
```

### POST `/api/email/test`
Test invio email con configurazione SMTP.

**Request Body:**
```json
{
  "email": "destinatario@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email di test inviata a destinatario@example.com"
}
```

**Note v2.9.3+:**
- Il nome installazione nelle email viene preso da `sistema.nome_installazione`
- La password non viene restituita in chiaro nelle GET (ritorna `'********'`)
- Il frontend mostra pallini `••••••••` quando password è salvata
- Se la password viene inviata come `'********'` o `'••••••••'` non viene aggiornata
- Click sul campo password pulisce automaticamente i pallini per nuova password
- Supporto completo OAuth2 per provider moderni (Gmail, Outlook, ecc.)

---

## 🚦 Access Control Endpoints

### POST `/api/process-codice-fiscale`
Processa un codice fiscale per autorizzazione accesso.

**Request Body:**
```json
{
  "codice_fiscale": "RSSMRA85M01H501Z"
}
```

**Response:**
```json
{
  "autorizzato": true,
  "tipo_accesso": "AUTORIZZATO",
  "messaggio": "Accesso consentito",
  "utente": {
    "nome": "Mario Rossi",
    "gruppo": "dipendenti"
  },
  "relay_activated": [1, 2],
  "durata": 0.125
}
```

### GET `/api/verifica-autorizzazione/{codice_fiscale}`
Verifica se un utente è autorizzato senza attivare relè.

**Response:**
```json
{
  "autorizzato": true,
  "utente": {
    "nome": "Mario Rossi",
    "attivo": true,
    "gruppo": "dipendenti"
  },
  "orario_consentito": true,
  "limite_mensile": {
    "limite": 100,
    "utilizzati": 45,
    "rimanenti": 55
  }
}
```

---

## 🔧 Hardware Control Endpoints

### POST `/api/test-gate`
Test apertura cancello (attiva relè configurati).

**Response:**
```json
{
  "success": true,
  "message": "Test gate eseguito con successo",
  "relays_activated": [1, 2],
  "duration": 3
}
```

### POST `/api/hardware/test-reader`
Test del lettore tessere con monitoraggio database (v2.2.0+).

**Note v2.2.0+:**
- Il test NON interferisce con il lettore hardware principale
- Monitora il database `log_accessi` per nuovi inserimenti
- Mostra le motivazioni di rifiuto dal campo `motivo_rifiuto`

**Response:**
```json
{
  "success": true,
  "message": "Test lettore avviato"
}
```

### POST `/api/hardware/stop-reader`
Ferma il test del lettore tessere in esecuzione (v2.2.0+).

**Response (test in esecuzione):**
```json
{
  "success": true,
  "message": "Test lettore fermato"
}
```

**Response (nessun test attivo):**
```json
{
  "success": false,
  "message": "Nessun test in esecuzione"
}
```

### GET `/api/hardware/status?test_id=reader`
Ottiene lo stato del test lettore in esecuzione.

**Response:**
```json
{
  "success": true,
  "test": {
    "status": "running",
    "message": "Tessere lette: 2",
    "details": [
      "📊 MONITOR DATABASE ATTIVO",
      "🎯 [09:43:28] TESSERA RILEVATA #1",
      "📄 Codice Fiscale: GBRWTR72D20D086D",
      "👤 Utente: Gabriele Walter Test Isola Ecologica",
      "❌ ACCESSO NEGATO",
      "📝 Motivo: Limite mensile accessi superato"
    ],
    "timestamp": 1757144608.5
  }
}
```

### POST `/api/hardware/test-connection`
Test connessione hardware.

**Request Body:**
```json
{
  "hardware_type": "card_reader",
  "device_path": "/dev/ttyACM0",
  "reader_type": "CRT285"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Hardware connesso correttamente",
  "device_info": {
    "type": "CRT285",
    "port": "/dev/ttyACM0",
    "status": "ready"
  }
}
```

### GET `/api/relay-config`
Recupera configurazione relè.

**Response:**
```json
{
  "relay_1": {
    "description": "Cancello Principale",
    "valid_action": "PULSE",
    "valid_duration": 3,
    "invalid_action": "OFF",
    "invalid_duration": 0
  },
  "relay_2": { ... }
}
```

### POST `/api/relay-config`
Salva configurazione relè.

**Request Body:**
```json
{
  "relay_1": {
    "description": "Cancello Principale",
    "valid_action": "PULSE",
    "valid_duration": 3,
    "invalid_action": "OFF",
    "invalid_duration": 0
  }
}
```

---

## 👥 User Management Endpoints

### GET `/api/users`
Lista utenti autorizzati con paginazione.

**Query Parameters:**
- `page` (int): Numero pagina
- `search` (string): Ricerca per nome/CF
- `active` (boolean): Filtra per stato

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "codice_fiscale": "RSSMRA85M01H501Z",
      "nome": "Mario Rossi",
      "email": "mario.rossi@email.com",
      "telefono": "333-1234567",
      "attivo": true,
      "gruppi": "dipendenti",
      "accessi_mese": 45
    }
  ],
  "pagination": { ... }
}
```

### POST `/api/users`
Crea nuovo utente.

**Request Body:**
```json
{
  "codice_fiscale": "RSSMRA85M01H501Z",
  "nome": "Mario Rossi",
  "email": "mario.rossi@email.com",
  "telefono": "333-1234567",
  "gruppi": "dipendenti",
  "attivo": true
}
```

### PUT `/api/users/{codice_fiscale}`
Aggiorna utente esistente.

### DELETE `/api/users/{codice_fiscale}`
Elimina utente.

---

## ⚙️ System Configuration Endpoints

### GET `/api/admin/sistema-config`
Recupera le configurazioni del sistema.

**Response:**
```json
{
  "success": true,
  "config": {
    "nome_installazione": "Isola Ecologica RAEE - Rende",
    "porta_web": 5000,
    "debug_mode": false,
    "timeout_sessione": 1800,
    "ambiente": "production"
  }
}
```

### POST `/api/admin/sistema-config`
Salva le configurazioni del sistema.

**Request Body:**
```json
{
  "nome_installazione": "Nuovo Nome Installazione",
  "porta_web": 5000,
  "debug_mode": false,
  "timeout_sessione": 1800,
  "ambiente": "production"
}
```

**Response:**
```json
{
  "success": true
}
```

**Note:** Il nome installazione viene visualizzato nella navbar dell'applicazione.

---

## 📅 Schedule Configuration Endpoints

### GET `/api/fasce-orarie`
Recupera configurazione fasce orarie.

**Response:**
```json
{
  "lunedi": [
    {"dalle": "08:00", "alle": "12:00"},
    {"dalle": "14:00", "alle": "18:00"}
  ],
  "martedi": [ ... ]
}
```

### POST `/api/fasce-orarie`
Salva configurazione fasce orarie.

### GET `/api/limiti-mensili`
Recupera limiti accesso mensili.

**Response:**
```json
{
  "default": 100,
  "per_gruppo": {
    "dipendenti": 200,
    "esterni": 50
  }
}
```

---

## 💾 Backup & Restore Endpoints

### GET `/api/backup/status`
Recupera stato generale dei backup e statistiche disco.

**Response:**
```json
{
  "success": true,
  "backups": [
    {
      "name": "backup_completo_20250908_092848.tar.gz",
      "type": "complete",
      "size": "8.33 MB",
      "date": "2025-09-08T09:28:48",
      "age_days": 0,
      "has_checksum": true,
      "can_download": true,
      "can_restore": true
    }
  ],
  "total_backups": 5,
  "total_size": "41.66 MB",
  "last_backup": "2025-09-08T10:04:24",
  "disk_used_percent": 19.1,
  "disk_free": "79.2 GB"
}
```

### POST `/api/backup/create`
Crea un nuovo backup del sistema.
- **Backup completo**: Include codice, database, configurazioni, log
- **Backup database**: Solo il database SQLite

**Request Body:**
```json
{
  "type": "complete"  // oppure "database"
}
```

### DELETE `/api/backup/delete/<filename>`
Elimina un backup esistente.
- Gestisce anche file mancanti dal filesystem
- Elimina automaticamente il checksum .md5 associato

### POST `/api/backup/restore/<filename>`
Ripristina un backup.
- Supporta sia backup completi (.tar.gz) che database (.db)
- Richiede checksum MD5 valido per sicurezza
- Crea backup automatico prima del ripristino

### GET `/api/backup/download/<filename>`
Scarica un file di backup.

### POST `/api/backup/config`
Aggiorna configurazione backup automatici.
- Salva in `/opt/access_control/backups/backup_config.json`
- Aggiorna automaticamente il crontab di sistema

### POST `/api/backup/cleanup`
Esegue pulizia manuale dei backup vecchi secondo policy retention.

### POST `/api/backup/integrity/check`
Avvia verifica integrità checksum MD5 di tutti i backup.

### POST `/api/backup/retention/apply`
Applica manualmente le politiche di retention.

---

## 🔄 System Management Endpoints

### POST `/api/restart-service`
Riavvia il servizio sistema.

**Response:**
```json
{
  "success": true,
  "message": "Servizio in riavvio..."
}
```

### GET `/api/system-status`
Stato sistema completo.

**Response:**
```json
{
  "status": "online",
  "uptime": "24h 35m",
  "database": {
    "status": "connected",
    "size": "125MB",
    "records": 50000
  },
  "hardware": {
    "card_reader": "connected",
    "relay_controller": "connected"
  },
  "version": "2.1.0"
}
```

---

## 💾 Backup & Restore Endpoints (v2.9.0+)

### GET `/api/backup/status`
Recupera stato generale dei backup e statistiche disco.

**Response:**
```json
{
  "success": true,
  "backups": [
    {
      "name": "backup_completo_20250908_092848.tar.gz",
      "type": "complete",
      "size": "8.33 MB",
      "date": "2025-09-08T09:28:48",
      "age_days": 0,
      "has_checksum": true,
      "can_download": true,
      "can_restore": true
    }
  ],
  "total_backups": 5,
  "total_size": "41.66 MB",
  "last_backup": "2025-09-08T10:04:24",
  "disk_used_percent": 19.1,
  "disk_free": "79.2 GB"
}
```

### POST `/api/backup/create`
Crea un nuovo backup del sistema.
- **Backup completo**: Include codice, database, configurazioni, log
- **Backup database**: Solo il database SQLite

**Request Body:**
```json
{
  "type": "complete"  // oppure "database"
}
```

**Response:**
```json
{
  "success": true,
  "filename": "backup_completo_20250908_123000.tar.gz",
  "size": "8.33 MB",
  "checksum": "md5:abc123...",
  "backup_path": "/opt/access_control/backups/"
}
```

### DELETE `/api/backup/delete/<filename>`
Elimina un backup esistente.
- Gestisce anche file mancanti dal filesystem
- Elimina automaticamente il checksum .md5 associato

**Response:**
```json
{
  "success": true,
  "message": "Backup eliminato con successo"
}
```

### POST `/api/backup/restore/<filename>`
Ripristina un backup.
- Supporta sia backup completi (.tar.gz) che database (.db)
- Richiede checksum MD5 valido per sicurezza
- Crea backup automatico prima del ripristino

**Response:**
```json
{
  "success": true,
  "message": "Backup ripristinato con successo",
  "restored_files": ["database", "configs", "logs"],
  "backup_created": "backup_pre_restore_20250908_123456.tar.gz"
}
```

### GET `/api/backup/download/<filename>`
Scarica un file di backup.

**Response:**
- File attachment con nome corretto
- Content-Type appropriato (application/gzip, application/octet-stream)

### POST `/api/backup/config`
Aggiorna configurazione backup automatici.
- Salva in `/opt/access_control/backups/backup_config.json`
- Aggiorna automaticamente il crontab di sistema

**Request Body:**
```json
{
  "auto_backup": {
    "enabled": true,
    "daily": {
      "enabled": true,
      "time": "02:00",
      "type": "database",
      "retention_days": 7
    },
    "weekly": {
      "enabled": true,
      "time": "03:00",
      "day": "0",
      "type": "complete",
      "retention_weeks": 4
    }
  },
  "cloud_sync": {
    "enabled": true,
    "provider": "aws_s3",
    "config": {
      "access_key": "AKIA...",
      "secret_key": "...",
      "bucket": "my-backups",
      "region": "eu-west-1"
    }
  }
}
```

### POST `/api/backup/integrity/check`
Avvia verifica integrità checksum MD5 di tutti i backup.

**Response:**
```json
{
  "success": true,
  "checked_files": 5,
  "valid_files": 4,
  "corrupted_files": 1,
  "results": [
    {
      "filename": "backup_20250908.tar.gz",
      "status": "valid",
      "checksum": "abc123..."
    }
  ]
}
```

### POST `/api/backup/retention/apply`
Applica manualmente le politiche di retention.

**Response:**
```json
{
  "success": true,
  "deleted_files": 3,
  "freed_space": "25.6 MB",
  "retention_applied": ["daily", "weekly"]
}
```

---

## 🔄 Server Sync Endpoints (v2.5.0+)

### GET `/sync/config`
Recupera configurazione server di sincronizzazione.

**Response:**
```json
{
  "success": true,
  "config": {
    "url": "http://odoo.example.com",
    "database": "production_db",
    "username": "sync_user",
    "password": "********",
    "comune": "Rende",
    "sync_enabled": true,
    "sync_interval_hours": 24,
    "last_sync": "2025-09-08T10:30:00"
  }
}
```

### POST `/sync/config`
Salva configurazione server di sincronizzazione.

**Request Body:**
```json
{
  "url": "http://odoo.example.com:8069",
  "database": "production_db",
  "username": "sync_user",
  "password": "secure_password",
  "comune": "Rende",
  "sync_enabled": true,
  "sync_interval_hours": 24
}
```

### GET `/sync/status`
Ottiene stato connessione server.

**Response:**
```json
{
  "success": true,
  "connected": true,
  "last_sync": "2025-09-08T10:30:00",
  "next_sync": "2025-09-09T10:30:00",
  "sync_enabled": true,
  "records_synchronized": 1250,
  "connection_test": "success"
}
```

**Note:**
- `connected`: `true` se sincronizzato nelle ultime 24 ore
- `last_sync`: Timestamp ultima sincronizzazione riuscita
- `next_sync`: Prossima sincronizzazione schedulata

### POST `/sync/test`
Testa connessione al server remoto.

**Response:**
```json
{
  "success": true,
  "message": "Connessione al server riuscita",
  "server_info": {
    "version": "15.0",
    "database": "production_db",
    "records_available": 1250
  }
}
```

### POST `/sync/manual`
Avvia sincronizzazione manuale immediata.

**Response:**
```json
{
  "success": true,
  "message": "Sincronizzazione avviata",
  "sync_id": "sync_20250908_103045",
  "estimated_duration": "2-5 minuti"
}
```

### POST `/sync/schedule`
Configura schedulazione automatica.

**Request Body:**
```json
{
  "enabled": true,
  "interval_hours": 12,
  "start_time": "02:00"
}
```

### GET `/sync/logs`
Recupera log delle operazioni di sincronizzazione.

**Query Parameters:**
- `limit` (int): Numero massimo di log (default: 50)

**Response:**
```json
{
  "success": true,
  "logs": [
    {
      "timestamp": "2025-09-08T10:30:00",
      "type": "manual",
      "status": "success",
      "records_synced": 15,
      "duration": "45 seconds",
      "message": "Sincronizzazione completata con successo"
    }
  ]
}
```

---

## 🚨 Error Responses

Tutti gli endpoint possono ritornare i seguenti errori:

### 401 Unauthorized
```json
{
  "error": "Authentication required",
  "redirect": "/login"
}
```

### 403 Forbidden
```json
{
  "error": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "Detailed error message"
}
```

---

## 👤 System Users Management (v2.7.0)

### GET `/api/users/list`
Lista utenti di sistema con informazioni complete.

**Response:**
```json
{
  "success": true,
  "users": [
    {
      "username": "admin",
      "role": "admin",
      "role_name": "Amministratore",
      "attivo": true,
      "email": "admin@example.com",
      "nome": "Mario",
      "cognome": "Rossi",
      "avatar_path": "/api/static/avatars/admin_abc123.jpg",
      "telefono": "+39 333 1234567",
      "bio": "Amministratore del sistema",
      "last_login": "2025-09-06 16:00:00",
      "must_change_password": false,
      "failed_attempts": 0
    }
  ]
}
```

### POST `/api/users/create`
Crea nuovo utente di sistema con profilo esteso.

**Request Body:**
```json
{
  "username": "mario_rossi",
  "password": "SecurePass123!",
  "email": "mario.rossi@example.com",
  "nome": "Mario",
  "cognome": "Rossi",
  "role": "viewer"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Utente mario_rossi creato con ruolo Visualizzatore",
  "username": "mario_rossi"
}
```

### POST `/api/users/update-profile`
Aggiorna profilo utente con supporto upload avatar.

**Request:** `multipart/form-data`
- `username` (string): Username utente
- `nome` (string): Nome
- `cognome` (string): Cognome  
- `email` (string): Email
- `telefono` (string): Telefono
- `bio` (string): Biografia
- `role` (string): Ruolo (solo admin)
- `avatar` (file): Immagine profilo (jpg, png, gif, webp)

**Response:**
```json
{
  "success": true,
  "message": "Profilo aggiornato con successo",
  "user": {
    "username": "mario_rossi",
    "nome": "Mario",
    "cognome": "Rossi",
    "email": "mario.rossi@example.com",
    "telefono": "+39 333 1234567",
    "bio": "Descrizione utente",
    "avatar_path": "/api/static/avatars/mario_rossi_uuid.jpg",
    "role": "viewer"
  }
}
```

### POST `/api/users/admin-set-password`
Admin imposta direttamente una nuova password per un utente.

**Request Body:**
```json
{
  "username": "mario_rossi",
  "password": "NewSecurePass123!",
  "must_change_password": true
}
```

**Password Requirements:**
- Minimo 8 caratteri
- Almeno una lettera maiuscola
- Almeno una lettera minuscola
- Almeno un numero
- Almeno un carattere speciale (!@#$%^&*(),.?":{}|<>)
- Non deve contenere spazi
- Non deve essere una password comune

**Response:**
```json
{
  "success": true,
  "message": "Password aggiornata con successo",
  "must_change": true
}
```

### POST `/api/users/send-reset-link`
Invia link di reset password via email.

**Request Body:**
```json
{
  "username": "mario_rossi",
  "custom_message": "Messaggio personalizzato opzionale"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Link di reset inviato a mario.rossi@example.com",
  "reset_url": "http://sistema.local/reset-password?token=abc123..."
}
```

### DELETE `/api/users/delete`
Elimina utente di sistema.

**Request Body:**
```json
{
  "username": "mario_rossi"
}
```

---

## 🎯 Test Accessi e Configurazione

### POST `/api/configurazione/utente-info-accessi`
Recupera informazioni sugli accessi di un utente specifico.

**Request Body:**
```json
{
  "codice_fiscale": "RSSMRA80A01H501Z"
}
```

**Response:**
```json
{
  "success": true,
  "nome_utente": "Mario Rossi",
  "numero_accessi_mese": 3,
  "limite_mensile": 5,
  "percentuale_utilizzo": 60.0,
  "ingressi_rimanenti": 2,
  "utente_attivo": true,
  "orario_consentito": true
}
```

### POST `/api/configurazione/test/aggiungi-ingressi`
Concede ingressi aggiuntivi a un utente che ha raggiunto il limite mensile.

**Request Body:**
```json
{
  "codice_fiscale": "RSSMRA80A01H501Z",
  "ingressi_aggiuntivi": 2,
  "motivazione": "Autorizzazione speciale per conferimento straordinario"
}
```

**Validazione:**
- L'utente deve aver raggiunto il limite mensile
- `ingressi_aggiuntivi` deve essere > 0
- La motivazione è opzionale ma consigliata

**Response:**
```json
{
  "success": true,
  "message": "Aggiunti 2 ingressi aggiuntivi. Contatore resettato.",
  "nuovo_contatore": 3,
  "ingressi_concessi": 2
}
```

**Logica Reset Contatore:**
- Se limite = 5 e utente ha 5 accessi
- Concedendo +2 ingressi extra
- Nuovo contatore = 5 - 2 = 3
- L'utente potrà fare altri 2 accessi

### POST `/api/configurazione/test/simula-accesso`
Simula un tentativo di accesso SENZA modificare contatori o registrare log.

**Request Body:**
```json
{
  "codice_fiscale": "RSSMRA80A01H501Z"
}
```

**Response (Accesso Consentito):**
```json
{
  "success": true,
  "accesso_consentito": true,
  "messaggio": "Accesso CONSENTITO",
  "nome_utente": "Mario Rossi",
  "numero_accessi_mese": 3,
  "limite_mensile": 5,
  "percentuale_utilizzo": 60.0,
  "ingressi_rimanenti": 2,
  "nota": "Se l'utente accedesse ora, sarebbe il suo ingresso n. 4 su 5 consentiti",
  "dispositivi_attivati": [
    {
      "dispositivo": "Motore Cancello",
      "azione": "ON",
      "durata": "1.0 secondi"
    }
  ]
}
```

**Response (Accesso Negato):**
```json
{
  "success": true,
  "accesso_consentito": false,
  "motivo_rifiuto": "Limite mensile di 5 ingressi raggiunto",
  "nome_utente": "Mario Rossi",
  "numero_accessi_mese": 5,
  "limite_mensile": 5,
  "percentuale_utilizzo": 100.0,
  "nota": "L'utente verrà automaticamente disattivato al prossimo accesso reale"
}
```

**Note Importanti:**
- NON incrementa il contatore accessi
- NON registra nei log_accessi
- NON disattiva utenti
- Solo verifica e mostra cosa succederebbe

---

## 📝 Notes

### Rate Limiting
- Max 100 richieste/minuto per IP
- Max 10 login attempts/ora

### CORS
- Abilitato per sviluppo locale
- Configurabile per domini specifici in produzione

### Versioning
- API version in header: `X-API-Version: 2.1.0`
- Backward compatibility mantenuta

---

**API Version**: 2.9.3  
**Last Updated**: 2025-09-08