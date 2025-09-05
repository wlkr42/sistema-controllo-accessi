# Sistema Controllo Accessi - Overview Completo

## 🎯 Scopo del Sistema

Sistema integrato per il controllo degli accessi a un'isola ecologica mediante lettura di tessera sanitaria/codice fiscale. Il sistema gestisce l'apertura automatica di cancelli tramite relè, traccia tutti gli accessi e fornisce un'interfaccia web completa per l'amministrazione.

## 🏗️ Architettura Sistema

### Componenti Principali

```
┌──────────────────────────────────────────────────────┐
│                    Frontend Web                       │
│         (HTML5 + Bootstrap 5 + JavaScript)           │
└────────────────────┬─────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────┴─────────────────────────────────┐
│                  Backend Flask                        │
│              (Python 3.10 + Flask)                    │
├───────────────────────────────────────────────────────┤
│                  Business Logic                       │
│     (Autenticazione, Autorizzazioni, Logging)        │
├───────────────────┬──────────────┬───────────────────┤
│    Database       │              │    Hardware       │
│    (SQLite)       │              │   Controllers     │
└───────────────────┴──────────────┴───────────────────┘
         │                                  │
    ┌────┴────┐                      ┌─────┴─────┐
    │Database │                      │  Devices   │
    │  File   │                      │ CRT-285    │
    └─────────┘                      │ USB-RLY08  │
                                     └────────────┘
```

## 💾 Database Schema

### Tabelle Principali

#### `utenti_autorizzati`
- Gestisce gli utenti autorizzati all'accesso
- Campi: codice_fiscale, nome, email, telefono, attivo, gruppi

#### `log_accessi`
- Registra ogni tentativo di accesso
- Campi: timestamp, codice_fiscale, autorizzato, tipo_accesso, terminale

#### `system_settings`
- Configurazioni di sistema key-value
- Include: timezone, formati data/ora, configurazioni NTP

#### `relay_config`
- Configurazione degli 8 relè
- Azioni per accesso valido/invalido, durate impulsi

#### `fascie_orarie`
- Definisce gli orari di accesso consentiti
- Configurabile per giorno settimana e gruppi utenti

## 🔧 Componenti Software

### Backend (`/src/api/`)

#### `web_api.py`
- Core dell'applicazione Flask
- Gestisce tutti gli endpoint API
- Autenticazione e sessioni
- Process flow accessi

#### `dashboard_templates.py`
- Template HTML per dashboard e admin
- Include configurazione sistema
- Sezione Orologio per timezone
- Console debug integrata

#### `log_accessi_template.py`
- Interfaccia log accessi
- Filtri avanzati
- Sistema export (CSV, Excel, PDF)

### Moduli (`/src/api/modules/`)

#### `configurazione_accessi.py`
- Logica verifica autorizzazioni
- Controllo fasce orarie
- Verifica limiti mensili

### Hardware (`/src/hardware/`)

#### `crt285_controller.py`
- Driver lettore tessere CRT-285
- Lettura codice fiscale da tessera sanitaria
- Gestione timeout e errori

#### `usb_rly08_controller.py`
- Controller per scheda relè USB-RLY08
- Gestione 8 canali relè
- Impulsi temporizzati

## 🚀 Flusso Operativo

### Processo Accesso Standard

1. **Lettura Tessera**
   - Utente avvicina tessera al lettore CRT-285
   - Sistema estrae codice fiscale

2. **Verifica Autorizzazione**
   ```
   1. Esistenza utente in DB
   2. Stato attivazione utente
   3. Controllo fascia oraria
   4. Verifica limiti mensili
   ```

3. **Azione Hardware**
   - Se autorizzato: attiva relè cancello
   - Se negato: segnale acustico/visivo

4. **Logging**
   - Registra accesso in database
   - Timestamp con timezone configurato
   - Tipo accesso e motivazione

5. **Dashboard Update**
   - Aggiornamento real-time statistiche
   - Visualizzazione ultimi accessi

## 🌟 Funzionalità Avanzate

### 🕐 Gestione Timezone (v2.1.0)
- Configurazione timezone da UI
- Conversione automatica UTC → Local
- Supporto multi-timezone
- Display ora corrente sistema

### 📊 Sistema Export (v2.1.0)
- **CSV**: Dati raw per analisi
- **Excel**: Report formattato con stili
- **PDF**: Documento per archiviazione
- Filtri applicabili pre-export

### 🐛 Console Debug
- Log real-time via WebSocket
- Test hardware integrati
- Riavvio servizio da UI
- Monitoring stato sistema

### 📈 Dashboard Analytics
- Grafici accessi giornalieri/settimanali
- Statistiche per utente
- Report automatici
- Trend analysis

## 🔒 Sicurezza

### Autenticazione
- Login con username/password
- Session management
- Timeout configurabile
- Multi-livello permessi

### Autorizzazione
- Admin: accesso completo
- Operator: gestione utenti
- Viewer: solo consultazione

### Audit Trail
- Log completo di tutte le azioni
- Tracciamento modifiche configurazione
- Export log per compliance

## 📦 Deployment

### Ambiente Produzione
```
OS: Ubuntu Server 20.04 LTS
Python: 3.10+
Database: SQLite 3.31+
Service: systemd (root per USB)
Port: 5000 (configurabile)
```

### Requisiti Hardware
- CPU: 2 core minimo
- RAM: 2GB minimo
- Storage: 10GB (con spazio per log)
- USB: 2 porte (lettore + relè)

## 🔄 Manutenzione

### Backup Automatici
- Database: giornaliero
- Configurazioni: settimanale
- Log: rotazione mensile

### Monitoring
- Health check endpoint
- Log rotation automatica
- Alert email per errori critici

### Updates
- Git-based deployment
- Rollback capability
- Zero-downtime updates

## 📊 Performance

### Capacità Sistema
- Utenti simultanei: 50+
- Transazioni/secondo: 10+
- Database size: fino a 10GB
- Log retention: 12 mesi

### Ottimizzazioni
- Query caching
- Connection pooling
- Async I/O per hardware
- Compressione log automatica

## 🎯 Roadmap Futura

### Prossime Features
- [ ] Integrazione LDAP/AD
- [ ] App mobile companion
- [ ] Riconoscimento facciale
- [ ] Multi-site support
- [ ] Cloud backup
- [ ] API webhook
- [ ] Dashboard customizzabile
- [ ] Report scheduler

## 📝 Standards & Compliance

### Codice
- PEP 8 Python style
- ESLint JavaScript
- SQL best practices
- Git conventional commits

### Documentazione
- Markdown format
- Inline code comments
- API documentation
- Change logs

### Testing
- Unit tests (pytest)
- Integration tests
- Hardware mock tests
- Load testing

---

**Versione Documento**: 1.0.0  
**Ultimo Aggiornamento**: 2025-09-05  
**Sistema Versione**: 2.1.0