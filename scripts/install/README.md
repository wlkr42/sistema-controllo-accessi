# Sistema Controllo Accessi - Installazione

## 📦 Contenuto Directory

Questa directory contiene tutti gli script necessari per l'installazione completa del Sistema Controllo Accessi su un nuovo sistema.

### Script Principali
- **`install_system.sh`** - Script installazione principale
- **`quick_install.sh`** - Download e installazione automatica one-liner

### Script di Supporto
- **`setup_database.py`** - Inizializza il database con struttura e dati di default
- **`setup_drivers.sh`** - Installa e configura i driver hardware (CRT-288K e USB-RLY08)
- **`setup_services.sh`** - Configura servizi systemd, logrotate e cron jobs
- **`setup_permissions.sh`** - Configura tutti i permessi file, directory e hardware
- **`verify_installation.sh`** - Verifica completezza installazione

## 🚀 Installazione Rapida

### Metodo 1: One-Liner (Raccomandato)
```bash
# Download e installazione automatica
curl -fsSL https://raw.githubusercontent.com/wlkr42/sistema-controllo-accessi/release/v3.0.0-RC1/scripts/install/quick_install.sh | sudo bash
```

### Metodo 2: Download Manuale
```bash
# 1. Scarica script
wget https://raw.githubusercontent.com/wlkr42/sistema-controllo-accessi/release/v3.0.0-RC1/scripts/install/install_system.sh
chmod +x install_system.sh

# 2. Esegui (sviluppo)
sudo bash install_system.sh

# 3. Oppure produzione
sudo bash install_system.sh production
```

### Metodo 3: Con Parametri
```bash
# Passa credenziali via environment
sudo GITHUB_USER="username" GITHUB_TOKEN="token" bash install_system.sh
```

## 🔧 Configurazione Repository GitHub

Prima di eseguire l'installazione, configurare il repository:

1. **Repository di default:**
   ```bash
   # Lo script usa di default:
   GITHUB_REPO="github.com/wlkr42/sistema-controllo-accessi"
   ```

2. **Per usare un fork o altro repository:**
   ```bash
   export GITHUB_REPO="github.com/tuo_username/tuo_fork"
   export GITHUB_BRANCH="main"
   sudo -E bash install_system.sh
   ```


## 📋 Prerequisiti

- Sistema operativo: Ubuntu 20.04+ / Debian 11+
- Python 3.10 o superiore
- Connessione internet attiva
- Accesso root/sudo
- Credenziali GitHub (per repository privato)

## 🔧 Processo di Installazione

L'installazione segue questi passi:

1. **Verifica credenziali GitHub** - Richiede username e token per repository privato
2. **Preparazione sistema** - Installa dipendenze sistema (python, git, sqlite3, etc.)
3. **Clone repository** - Scarica codice sorgente da GitHub
4. **Setup Python** - Crea virtual environment e installa dipendenze
5. **Driver hardware** - Configura driver CRT-288K e USB-RLY08
6. **Struttura directory** - Crea directory necessarie (data, logs, backups)
7. **Database** - Inizializza database con struttura completa
8. **Configurazione** - Crea file di configurazione
9. **Servizi** - Installa e configura systemd, logrotate, cron
10. **Test hardware** - Verifica presenza dispositivi
11. **Avvio sistema** - Avvia servizi e verifica funzionamento

## 🔌 Hardware Supportato

### Lettore Tessere
- **Modello**: CRT-288K / CRT-285
- **USB ID**: 23d8:0285
- **Documentazione**: `/src/drivers/288K/`

### Controller Relè
- **Modello**: USB-RLY08
- **USB ID**: 04d8:ffee
- **Canali**: 8 relè indipendenti

## 📁 Struttura Post-Installazione

```
/opt/access_control/
├── data/                 # Database SQLite
├── logs/                 # File di log
├── backups/              # Backup automatici
├── config/               # File configurazione
├── src/                  # Codice sorgente
│   ├── api/             # API Flask
│   ├── drivers/         # Driver hardware
│   └── modules/         # Moduli sistema
├── scripts/              # Script utilities
│   ├── install/         # Script installazione
│   └── system/          # Script sistema
└── venv/                # Virtual environment Python
```

## 🔐 Credenziali Default

- **Username**: admin
- **Password**: admin123

⚠️ **IMPORTANTE**: Cambiare la password al primo accesso!

## 🛠️ Comandi Utili Post-Installazione

```bash
# Stato servizi
systemctl status access-control-web
systemctl status access-monitor

# Log real-time
journalctl -fu access-control-web

# Health check
curl http://localhost:5000/api/health

# Restart sistema
./restart.sh

# Backup manuale
python3 scripts/auto_backup.py complete
```

## 🐛 Troubleshooting

### Servizio non si avvia
```bash
# Verifica log
journalctl -xeu access-control-web

# Verifica porta 5000
lsof -i :5000

# Verifica database
ls -la /opt/access_control/data/
```

### Hardware non rilevato
```bash
# Lista dispositivi USB
lsusb

# Verifica seriali
ls -la /dev/ttyUSB* /dev/ttyACM*

# Ricarica udev
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Permessi
```bash
# Aggiungi utente a gruppi
sudo usermod -a -G dialout $USER
sudo usermod -a -G tty $USER
```

## 📞 Supporto

Per problemi durante l'installazione:
1. Verificare i log in `/opt/access_control/logs/`
2. Controllare i requisiti di sistema
3. Verificare connessione hardware

## 📄 Licenza

Sistema proprietario - Tutti i diritti riservati