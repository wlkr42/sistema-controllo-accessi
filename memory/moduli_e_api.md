# Struttura Moduli e API - Sistema Controllo Accessi

## Architettura Flask Blueprint

- **profilo_bp**: gestione profilo utente corrente (`/api/profile/info`, `/api/user-menu-html`)
- **user_management_bp**: gestione utenti sistema (admin dashboard)
- **log_management_bp**: gestione e visualizzazione log
- **utenti_autorizzati_bp**: gestione utenti abilitati all’accesso fisico
- **system_users_bp**: gestione utenti di sistema
- **activities_bp**: log attività e azioni
- **configurazione_accessi_bp**: configurazione orari, limiti, test accessi
- **backup_bp**: gestione backup e restore

## Endpoint Principali

### Autenticazione e Sessione
- `POST /login` - Login utenti_sistema
- `GET /logout` - Logout
- `GET /api/profile/info` - Info profilo sessione
- `GET /api/user-menu-html` - HTML menu utente

### Gestione Utenti
- `GET /admin/users` - Gestione utenti sistema (pagina)
- `GET /api/users/count` - Numero utenti attivi
- `GET /utenti-autorizzati` - Gestione utenti autorizzati (pagina)
- `POST /api/authorize` - Autorizzazione accesso fisico (codice fiscale)

### Configurazione Accessi
- `GET/POST /api/configurazione/orari` - Orari settimanali
- `GET/POST /api/configurazione/limiti` - Limiti ingressi
- `POST /api/configurazione/test/set-ingressi` - Test conteggio
- `POST /api/configurazione/test/simula-accesso` - Simulazione accesso
- `POST /api/configurazione/test/reset-contatore` - Reset contatore
- `POST /api/configurazione/test/apri-cancello` - Apertura forzata
- `GET /api/configurazione/log-forzature` - Log forzature

### Hardware
- `POST /api/relay/open` - Apri relè
- `POST /api/relay/close` - Chiudi relè
- `GET /api/relay/status` - Stato relè
- `GET /api/hardware/test` - Test hardware
- `POST /api/test-card-reader` - Test lettore tessere
- `GET /api/hardware/detect` - Rilevamento hardware
- `POST /api/hardware/test-connection` - Test connessione hardware

### Backup e Restore
- `GET /api/backup/status` - Stato backup
- `POST /api/backup/create` - Crea backup
- `POST /api/backup/cleanup` - Pulizia backup vecchi
- `GET /api/backup/download/<filename>` - Download backup
- `POST /api/backup/restore/<filename>` - Ripristina backup
- `GET/POST /api/backup/schedule` - Configurazione schedulazione

### Odoo Sync
- `POST /api/odoo/sync` - Sincronizzazione Odoo
- `GET /api/odoo/status` - Stato connessione Odoo

### Sistema e Configurazione
- `GET /api/system/config` - Configurazioni sistema
- `POST /api/system/config/save` - Salva configurazioni
- `POST /api/system/config/reset` - Reset configurazioni default
- `POST /api/system/restart` - Riavvio sistema

### Statistiche e Log
- `GET /api/stats` - Statistiche accessi
- `GET /api/recent-accesses` - Accessi recenti
- `GET /api/logs` - Visualizza log

## Note

- Tutte le API protette da autenticazione e permessi (decorator @require_auth, @require_permission)
- Risposte JSON sempre `{success: bool, message: str, data: any, error: str?}`
- Modularità garantita tramite Flask Blueprint
- Entry point: `/opt/access_control/src/api/web_api.py`
- Tutti i moduli sono in `/opt/access_control/src/api/modules/`
