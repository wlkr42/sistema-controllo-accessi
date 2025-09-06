# Changelog - Sistema Controllo Accessi

Tutte le modifiche importanti a questo progetto sono documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/),
e questo progetto aderisce al [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.8.0] - 2025-09-06

### ✨ Aggiunto
- **Test Accessi Avanzato**: Nuova interfaccia per test e gestione accessi nella configurazione orari
  - Progress bar read-only con gradiente colore per visualizzazione accessi/limite
  - Campo "Ingressi Aggiuntivi" abilitato solo quando utente raggiunge limite
  - Campo "Motivazione" opzionale per documentare concessioni extra
  - Caricamento automatico info accessi quando si seleziona utente

### 🔧 Modificato
- **Simulazione Accesso**: Non registra più nei log e non modifica contatori
  - Solo verifica accessibilità senza effetti collaterali
  - Mostra cosa succederebbe con un accesso reale
  - Mantiene integrità dati durante test

### 🔌 API
- `POST /api/configurazione/utente-info-accessi`: Recupera info accessi utente
- `POST /api/configurazione/test/aggiungi-ingressi`: Concede ingressi extra (solo a limite raggiunto)
- `POST /api/configurazione/test/simula-accesso`: Simula accesso senza modifiche

### 🗄️ Database
- Utilizza tabelle esistenti: `conteggio_ingressi_mensili`, `limiti_accesso`, `log_forzature`
- Logica reset contatore: limite - ingressi_extra = nuovo_contatore

## [2.7.1] - 2025-09-06

### 🎨 Migliorato
- Rimosso pulsante "Test Accessi" ridondante dalla dashboard admin
- Uniformati colori pulsanti dashboard con schema coerente
- Pulsante "Log Accessi" ora utilizza colore primary (blu) invece di warning (giallo)

### 🔧 Modificato
- `web_api.py`: Rimosso Test Accessi dai menu_items admin
- `dashboard_templates.py`: Aggiornati stili pulsanti per coerenza visiva

## [2.7.0] - 2025-09-06

### ✨ Aggiunto
- Sistema completo gestione profili utente con avatar
- Password management avanzato con validazione rigorosa
- Reset password via email con token sicuri
- Upload avatar con anteprima real-time
- Campi profilo estesi: nome, cognome, telefono, bio
- Storico password e politiche di sicurezza
- Modal profilo ridisegnato senza campo password
- Form creazione utente con campi nome e cognome

### 🗃️ Database
- Nuove colonne in `utenti_sistema`: nome, cognome, avatar_path, telefono, bio, data_nascita, indirizzo
- Nuove tabelle: password_reset_tokens, password_history, password_policies

### 📚 Documentazione
- Aggiornato DEVELOPER_GUIDE con sezione profili utente
- Documentati nuovi endpoint in API_DOCUMENTATION

## [2.6.0] - 2025-09-05

### 🔧 Modificato
- Database migrato da `/src` a `/data` per struttura corretta
- Configurazione centralizzata path database

### ✨ Aggiunto
- Nuovo sistema gestione path database unificato
- Script migrazione automatica database

## [2.5.0] - 2025-09-04

### ✨ Aggiunto
- Server Sync: Sincronizzazione automatica con server remoto
- Sistema paginazione utenti (30/50/100/tutti)
- Migliorata visualizzazione date con formato completo

### 🐛 Risolto
- Fix formato date con ora (DD/MM/YYYY HH:MM:SS)
- Corretta visualizzazione timestamp con timezone

## [2.4.0] - 2025-09-03

### ✨ Aggiunto
- Sistema Backup Enterprise multi-livello
- Supporto cloud storage (AWS S3, Google Cloud, Azure)
- Verifica integrità backup con checksum
- Retention policies automatiche
- Backup schedulati configurabili

## [2.3.0] - 2025-09-02

### 🐛 Risolto
- Allineamento timezone tra sistema e visualizzazione
- Fix conversione timestamp UTC → Local

### ✨ Aggiunto
- Configurazione timezone da interfaccia admin
- Test suite migliorata per gestione date

## [2.2.0] - 2025-09-01

### ✨ Aggiunto
- Test lettore tessere migliorato
- Diagnostica hardware avanzata
- Log dettagliati per debug

## [2.1.0] - 2025-08-31

### ✨ Aggiunto
- Export configurazioni in JSON
- Import configurazioni da backup
- Gestione permessi granulare per ruoli

## [2.0.0] - 2025-08-30

### 💥 Breaking Changes
- Migrazione da Python 2 a Python 3
- Nuovo schema database con migrazioni

### ✨ Aggiunto
- Sistema ruoli utente (admin, user_manager, viewer)
- Dashboard personalizzata per ruolo
- API RESTful completa

## [1.0.0] - 2025-08-01

### ✨ Prima Release
- Lettura tessera sanitaria con CRT-285
- Controllo 8 relè via USB-RLY08
- Dashboard web base
- Gestione utenti autorizzati
- Log accessi
- Configurazione fasce orarie