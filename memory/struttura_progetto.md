# Struttura Reale del Progetto - Access Control

```
/opt/access_control/
├── src/                    # Codice sorgente principale
│   ├── api/                # API Flask e interfaccia web
│   │   ├── modules/        # Moduli Blueprint (gestione utenti, accessi, log, configurazione)
│   │   ├── static/         # File statici (CSS, JS, HTML)
│   │   ├── templates/      # Template HTML aggiuntivi
│   │   ├── utils/          # Utility API
│   │   ├── backup/         # Modulo backup (Blueprint)
│   │   ├── admin_templates.py
│   │   ├── auth.py
│   │   ├── backup_module.py
│   │   ├── dashboard_templates.py
│   │   ├── hardware_detection.py
│   │   ├── hardware_tests.py
│   │   ├── test_hardware_integration.py
│   │   ├── user_menu.py
│   │   ├── utils.py
│   │   └── web_api.py      # Entry point API Flask
│   ├── core/               # Configurazioni core
│   │   └── config.py
│   ├── database/           # Layer database
│   │   └── database_manager.py
│   ├── drivers/            # Driver hardware (lettori tessere, relè)
│   │   └── 288K/
│   ├── external/           # Integrazioni esterne (Odoo, test, fix)
│   │   ├── odoo_partner_connector.py
│   ├── hardware/           # Controller hardware (lettori, relè, factory)
│   │   ├── card_reader.py
│   │   ├── crt285_reader.py
│   │   ├── reader_factory.py
│   │   ├── test_readers.py
│   │   └── usb_rly08_controller.py
│   ├── utils/              # Utility generali
│   ├── access.db           # Database SQLite
│   ├── database_schema.sql # Schema database
│   ├── documentazione_access_control_*.md # Documentazione generata
│   ├── genera_documentazione.py
│   └── main.py             # Entry point applicazione
├── config/                 # Configurazioni (admin, base, dashboard, device)
├── installazione/          # Pacchetto e script di installazione
│   ├── scripts/            # Script installazione, test hardware, check system
│   ├── docs/               # Manuale installazione
│   ├── pacchetto/          # Pacchetti distribuzione
│   └── README.md           # Guida installazione rapida
├── scripts/                # Script utility e manutenzione
├── logs/                   # File di log sistema
├── backups/                # Backup automatici e manuali
├── data/                   # Dati applicazione (cache, json)
├── tests/                  # Test suite (unit, integration, hardware)
├── docs/                   # Documentazione progetto
├── da_buttare/             # File obsoleti (non eliminare!)
├── memory/                 # Knowledge base generata (questa cartella)
├── requirements.txt        # Dipendenze Python
├── setup_cline_complete.py # Script setup Cline
└── venv/                   # Ambiente virtuale Python
```

## Note sui Componenti Principali

- **src/api/modules/**: Tutti i moduli logici (utenti, accessi, configurazione, log, backup)
- **src/api/web_api.py**: Entry point API Flask, registra tutti i blueprint e gestisce le route principali. Usa il ConfigManager centralizzato per propagare la configurazione hardware/software.
- **src/core/config.py**: ConfigManager centralizzato (singleton) che gestisce sia la configurazione statica (YAML) sia quella dinamica hardware (device_assignments.json). Tutti i moduli e main.py usano questo manager per accedere alla configurazione aggiornata.
- **src/hardware/**: Gestione diretta hardware (lettori tessere, relè USB). I costruttori di CardReader e USBRLY08Controller ora accettano device_path dinamico dalla configurazione.
- **src/main.py**: Entry point applicazione, ora integra la configurazione hardware dinamica tramite ConfigManager e propaga i parametri a CardReader e USBRLY08Controller.
- **src/external/**: Integrazione Odoo e script di test/fix esterni
- **config/device_assignments.json**: File di configurazione dinamica hardware, aggiornato dall’interfaccia admin/config e letto da tutto il software tramite ConfigManager.
- **installazione/scripts/**: Script di installazione, test hardware, check system, uninstall
- **logs/**: Log di sistema, sicurezza, accessi
- **backups/**: Backup database e configurazioni
- **memory/**: Documentazione generata automatica (knowledge base)
- **tests/**: Test unitari, integrazione, hardware
- **da_buttare/**: File obsoleti, mai eliminare direttamente
