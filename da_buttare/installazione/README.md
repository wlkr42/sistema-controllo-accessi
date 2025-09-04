# Sistema Controllo Accessi - Pacchetto di Installazione

## 📦 Contenuto del Pacchetto
```
installazione/
├── src/                    # Codice sorgente del sistema
├── config/                 # File di configurazione
├── scripts/               # Script di installazione e utility
├── docs/                  # Documentazione
├── backups/               # Backup e script di restore
└── cron/                  # Configurazioni cron jobs
```

## 📋 Requisiti di Sistema
- Linux (testato su Ubuntu/Debian)
- Python 3.8+
- USB ports per:
  - Lettore tessere
  - Relè USB

## 🚀 Installazione

1. Estrarre il pacchetto:
```bash
tar -xzf sistema-controllo-accessi.tar.gz
cd installazione
```

2. Eseguire l'installazione:
```bash
sudo ./scripts/install.sh
```

3. Verificare l'installazione:
```bash
./scripts/test_hardware.py
```

## 📁 Struttura Dettagliata

### /src
- Codice sorgente completo del sistema
- API Flask e interfaccia web
- Gestione hardware e database

### /config
- File di configurazione base
- Template configurazioni
- Configurazioni ambiente

### /scripts
- Script di installazione principale
- Utility di manutenzione
- Test hardware
- Script di backup/restore

### /docs
- Manuale di installazione
- Guida configurazione
- Troubleshooting

### /backups
- Script di backup automatico
- Utility di restore
- Configurazione backup

### /cron
- Configurazioni cron jobs
- Script per reset contatori
- Script manutenzione automatica

## ⚙️ Configurazione Post-Installazione

1. Configurare il database:
```bash
./scripts/setup_database.sh
```

2. Configurare i cron jobs:
```bash
./scripts/setup_cron.sh
```

3. Avviare il servizio:
```bash
sudo systemctl start access-control
```

## 🔧 Troubleshooting

Per problemi hardware:
```bash
./scripts/test_hardware.py --verbose
```

Per log del sistema:
```bash
./scripts/check_logs.sh
```

## 📞 Supporto

Per assistenza consultare la documentazione in /docs o contattare il supporto tecnico.
