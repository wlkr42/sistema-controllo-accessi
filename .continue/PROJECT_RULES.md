# REGOLE PROGETTO ACCESS_CONTROL - CLINE EDITION

<!-- CLINE: ALWAYS READ THIS FILE FIRST -->
<!-- Critical project rules - MUST be followed -->

## 🚨 REGOLE TASSATIVE (OBBLIGATORIE)

### 1. METODOLOGIA DI LAVORO
- ✅ SEMPRE procedere passo passo
- ✅ Un task alla volta, completarlo prima di passare al successivo
- ✅ MAI modificare più di quello richiesto
- ✅ FOCUS esclusivo sul task corrente

### 2. INTEGRAZIONE CODICE
- ✅ Modificare ESCLUSIVAMENTE i file richiesti
- ✅ NON toccare altri file senza esplicita richiesta
- ✅ Mantenere la modularità Flask Blueprint
- ✅ Rispettare pattern esistenti

### 3. DATABASE - REGOLA CRITICA
- ⚠️ utenti_sistema = SOLO per login amministratori dashboard
- ⚠️ utenti_autorizzati = SOLO per accesso fisico con tessera
- ⚠️ MAI mescolare i due sistemi di autenticazione

### 4. STILE E CONSISTENZA
- ✅ Coerenza totale con codice esistente
- ✅ Stesso stile di indentazione (4 spazi)
- ✅ Naming convention consistente
- ✅ Pattern UI uguali per nuove pagine

### 5. GESTIONE FILE
- ✅ File obsoleti → sempre in da_buttare/
- ✅ Creare log: cleanup_log_[timestamp].txt
- ✅ MAI eliminare file direttamente
- ✅ Preservare struttura cartelle

### 6. COMUNICAZIONE
- ✅ Risposte SEMPRE in italiano
- ✅ Percorso completo dei file: /opt/access_control/src/...
- ✅ Spiegare ogni modifica
- ✅ Confermare completamento

## 📁 STRUTTURA PROGETTO

/opt/access_control/
├── src/
│   ├── api/
│   │   ├── web_api.py          # API Flask principale
│   │   ├── modules/            # Moduli Blueprint
│   │   ├── static/             # CSS, JS, HTML
│   │   └── templates/          # Template aggiuntivi
│   ├── hardware/
│   │   ├── card_reader.py      # Lettore tessere
│   │   └── usb_rly08_controller.py  # Controller relè
│   ├── database/
│   │   └── database_manager.py # Gestione DB
│   ├── external/
│   │   └── odoo_partner_connector.py # Integrazione Odoo
│   └── main.py                 # Entry point
├── config/                     # Configurazioni YAML/JSON
├── scripts/                    # Script utilità
├── tests/                      # Test suite
└── .continue/                  # Memoria Cline

## ❌ NON FARE MAI
- Modificare file non richiesti
- Rifattorizzare senza permesso
- Cambiare convenzioni
- Mescolare task diversi
- Eliminare file direttamente
- Ignorare la modularità

## ✅ FARE SEMPRE
- Leggere memoria prima di iniziare
- Procedere passo passo
- Mantenere stile esistente
- Documentare modifiche
- Aggiornare memoria dopo
- Rispondere in italiano
