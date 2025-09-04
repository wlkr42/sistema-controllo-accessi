# Flussi Principali - Sistema Controllo Accessi

## 1. Login Amministratore Dashboard
- L’utente accede a `/login` con username/password (tabella `utenti_sistema`)
- Se autenticato, viene aggiornata la sessione e il campo `last_login`
- Log evento in `eventi_sistema`
- Accesso alle pagine protette e menu in base al ruolo

## 2. Accesso Fisico con Tessera
- L’utente presenta la tessera al lettore USB
- Il codice fiscale viene letto e passato a `/api/authorize` o gestito da CardReader
- Flusso:
  1. Verifica orario (`verifica_orario`)
  2. Verifica utente attivo in `utenti_autorizzati`
  3. Verifica limiti mensili (`verifica_limite_mensile`)
  4. Incrementa contatore accessi
  5. Log in `log_accessi`
  6. Se autorizzato: apertura cancello tramite USB-RLY08, feedback LED/Buzzer

## 3. Gestione Utenti e Configurazione
- Admin può gestire utenti sistema e utenti autorizzati via dashboard
- Configurazione orari, limiti, test accessi tramite API e interfaccia web
- Tutte le modifiche sono tracciate in `eventi_sistema`

## 4. Backup e Restore
- Backup automatici e manuali tramite API e cron
- File backup in `/opt/access_control/backups/`
- Restore tramite API o script, con sovrascrittura `access.db`
- Retention configurabile

## 5. Sincronizzazione Odoo
- Sincronizzazione utenti autorizzati da Odoo via `/api/odoo/sync`
- Connettore Odoo configurato all’avvio, sync periodica ogni 12h
- Log dettagliato in caso di errori o mismatch

## 6. Test e Diagnostica Hardware
- Test hardware via `/api/hardware/test`, `/api/test-card-reader`, `/api/test_relay`
- Diagnostica permessi, connessione dispositivi, stato relè e lettore
- Script dedicati: `test_hardware.py`, `check_system.sh`

## 7. Gestione Configurazione Sistema
- Configurazioni salvate in `system_settings`
- API per salvataggio, reset, e caricamento configurazioni
- Configurazione hardware, sicurezza, email, backup

## 8. Logging e Statistiche
- Tutte le azioni critiche loggate in `eventi_sistema` e `log_accessi`
- Statistiche accessi via `/api/stats`, `/api/recent-accesses`
- Log accessibili via dashboard e API
