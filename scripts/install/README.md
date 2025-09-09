# 📦 Sistema di Installazione Automatica

## 🎯 Panoramica

Sistema di installazione completamente automatizzato per il deployment del Sistema Controllo Accessi RAEE su sistemi Ubuntu/Debian.

## 🚀 Installazione Rapida

### One-Liner Installation
```bash
export GIT_USERNAME="your_github_username"
export GIT_PASSWORD="your_github_token"
curl -sL https://raw.githubusercontent.com/wlkr42/sistema-controllo-accessi/main/scripts/install/install_system.sh | sudo bash -s production
```

## 📂 Struttura Script

### `install_system.sh`
Script principale di installazione che gestisce l'intero processo:
- Verifica credenziali GitHub
- Clona repository con retry automatico (HTTP2 fallback)
- Installa dipendenze sistema
- Configura ambiente Python
- Inizializza database
- Installa driver hardware
- Configura servizi systemd
- Avvia sistema

### `auto_install.sh`
Wrapper per installazioni non presidiate:
- Gestione credenziali salvate
- Deployment multipli
- Logging automatico
- Configurazione remota

### `setup_database.py`
Inizializzazione database SQLite:
- Crea struttura tabelle
- Inserisce dati iniziali
- Configura utente admin
- Imposta permessi

### `setup_drivers.sh`
Installazione driver hardware:
- CRT-285 (lettore tessere)
- USB-RLY08 (controller relè)
- Regole udev
- Permessi seriali

### `setup_services.sh`
Configurazione servizi sistema:
- Servizio systemd principale
- Monitor 24/7
- Logrotate
- Cron jobs backup

### `setup_permissions.sh`
Gestione permessi:
- Utente servizio (www-data)
- Gruppi hardware (dialout, tty)
- Directory permessi
- File sensibili

### `verify_installation.sh`
Verifica post-installazione:
- Test connettività
- Verifica servizi
- Check hardware
- Report finale

## 🔧 Requisiti Sistema

- **OS**: Ubuntu 20.04+ / Debian 11+
- **Python**: 3.10+
- **RAM**: Minimo 2GB
- **Disco**: Minimo 10GB
- **Rete**: Accesso GitHub

## 📝 Variabili d'Ambiente

| Variabile | Descrizione | Default |
|-----------|-------------|---------|
| `GIT_USERNAME` | Username GitHub | Richiesto |
| `GIT_PASSWORD` | Token/Password GitHub | Richiesto |
| `GITHUB_BRANCH` | Branch da installare | main |
| `INSTALL_ENV` | Ambiente (development/production) | development |
| `GITHUB_REPO` | Repository GitHub | github.com/wlkr42/sistema-controllo-accessi |

## 🛠️ Modalità Installazione

### Development
```bash
sudo bash scripts/install/install_system.sh development
```
- Flask development server
- Debug abilitato
- Hot reload

### Production
```bash
sudo bash scripts/install/install_system.sh production
```
- Gunicorn con workers
- Ottimizzazioni performance
- Logging production

## 🔍 Troubleshooting

### Errore HTTP2
Lo script gestisce automaticamente errori HTTP2 con fallback a HTTP/1.1

### Credenziali con caratteri speciali
Le credenziali vengono automaticamente URL-encoded

### Database non trovato
Lo script crea automaticamente `/opt/access_control/data/access.db`

### Driver mancanti
I driver `.so` sono inclusi nel repository in `src/drivers/288K/`

## 📊 Log e Debug

### Log installazione
```bash
journalctl -u access-control-web -f
```

### Verifica servizi
```bash
systemctl status access-control-web
systemctl status access-monitor
```

### Test manuale
```bash
curl http://localhost:5000/api/health
```

## 🔄 Aggiornamento

```bash
cd /opt/access_control
git pull origin main
sudo systemctl restart access-control-web
```

## 🗑️ Disinstallazione

```bash
# Stop servizi
sudo systemctl stop access-control-web
sudo systemctl stop access-monitor

# Disabilita servizi
sudo systemctl disable access-control-web
sudo systemctl disable access-monitor

# Rimuovi file servizio
sudo rm /etc/systemd/system/access-control*.service

# Rimuovi installazione (opzionale - ATTENZIONE: cancella dati!)
sudo rm -rf /opt/access_control
```

## 📞 Supporto

Per problemi durante l'installazione:
1. Verifica i log: `journalctl -xe`
2. Controlla connessione GitHub
3. Verifica credenziali
4. Apri issue su GitHub

## 🔒 Note Sicurezza

- Le credenziali GitHub non vengono mai salvate in chiaro
- Il database viene creato con permessi 644
- I servizi girano come utente `www-data`
- Le password sono hashate con bcrypt

## 📈 Performance

L'installazione completa richiede:
- **Tempo**: 3-5 minuti (dipende dalla connessione)
- **Banda**: ~100MB download
- **CPU**: Minimo durante installazione
- **RAM**: ~500MB durante setup

## 🎯 Best Practices

1. **Usa sempre token GitHub** invece della password
2. **Esegui backup** prima di aggiornamenti
3. **Testa in development** prima di production
4. **Monitora i log** dopo l'installazione
5. **Cambia password admin** dopo primo accesso

---

**Versione**: 3.0.0-RC1  
**Ultimo Aggiornamento**: 2025-09-09  
**Maintainer**: Sistema Controllo Accessi Team