# 📚 DOCUMENTAZIONE COMPLETA SISTEMA CONTROLLO ACCESSI
## Sistema RAEE - Comune di Rende

---

## 🎯 PANORAMICA

Sistema di controllo accessi per isola ecologica RAEE con funzionalità avanzate:
- Lettore tessere sanitarie CRT-285/288K
- Controller relè USB-RLY08
- Web interface su porta 5000
- **Sistema Backup Enterprise** con cloud integration (v2.9.0+)
- **Email SMTP completo** con configurazione sicura (v2.9.1+)
- **Monitoraggio Real-Time** con metriche sistema (v2.9.2+)
- **Password Security** avanzata (v2.9.3)
- Integrazione Odoo per sincronizzazione utenti
- Database path dinamico con retrocompatibilità
- Sistema robusto con auto-recovery

---

## 🏗️ ARCHITETTURA

### Componenti Hardware
1. **CRT-285/288K** - Lettore tessere sanitarie (USB ID: 23d8:0285)
2. **USB-RLY08** - Controller 8 relè (USB ID: 04d8:ffee)

### Stack Software
- **Python 3.10** con virtual environment
- **Flask** - Web framework con Blueprint
- **SQLite** - Database locale
- **systemd** - Gestione servizio
- **Git** - Versioning (repo: github.com/wlkr42/sistema-controllo-accessi)
- **Backup System** - Sistema backup enterprise con cloud support

---

## 📁 STRUTTURA FILE

```
/opt/access_control/
├── venv/                     # Python virtual environment
├── src/
│   ├── api/
│   │   ├── web_api.py       # Server Flask principale
│   │   └── modules/         # Moduli web
│   ├── hardware/
│   │   ├── crt285_reader.py # Driver CRT-285
│   │   ├── card_reader.py   # Lettore generico smartcard
│   │   ├── reader_factory.py # Factory per selezione dinamica
│   │   └── usb_rly08_controller.py # Controller relè
│   ├── database/
│   │   └── database_manager.py
│   └── drivers/
│       └── 288K/            # Driver e documentazione CRT-285
├── config/
│   ├── device_assignments.json  # Configurazione hardware dinamica
│   └── admin_config.json       # Configurazione admin
├── access-control-web.service  # File servizio systemd
├── fix_and_restart.sh          # Script fix completo
└── start_system.sh            # Script avvio semplice
```

---

## ⚙️ CONFIGURAZIONE

### 1. Configurazione Hardware Dinamica

File: `/opt/access_control/config/device_assignments.json`

```json
{
  "assignments": {
    "card_reader": {
      "device_key": "usb:23d8:0285",
      "device_name": "CREATOR(CHINA)TECH CO.,LTD CRT-285",
      "device_path": "/dev/ttyACM0"
    },
    "relay_controller": {
      "device_key": "usb:04d8:ffee",
      "device_name": "USB-RLY08",
      "device_path": "/dev/ttyACM0"
    }
  }
}
```

**IMPORTANTE**: L'hardware è configurabile via web interface senza modificare codice!
URL: http://192.168.1.236:5000/admin/config (sezione Hardware)

### 2. Servizio systemd

File: `/etc/systemd/system/access-control-web.service`

**Caratteristiche chiave**:
- Gira come **root** per evitare problemi permessi USB
- Usa Python del **venv** (`/opt/access_control/venv/bin/python`)
- **Restart automatico** in caso di crash
- Path e environment corretti

---

## 🚀 AVVIO SISTEMA

### Metodo 1: Script Fix Completo (CONSIGLIATO)
```bash
sudo /opt/access_control/fix_and_restart.sh
```

Questo script:
1. Termina processi esistenti
2. Libera porta 5000
3. Verifica hardware
4. Configura permessi
5. Avvia servizio systemd
6. Verifica funzionamento

### Metodo 2: Avvio Semplice
```bash
sudo /opt/access_control/start_system.sh
```

### Metodo 3: Manuale
```bash
sudo systemctl restart access-control-web
```

---

## 🔍 TROUBLESHOOTING

### Problema: "Port 5000 is in use"

**Causa**: Un'altra istanza del web server è già in esecuzione

**Soluzione**:
```bash
# Trova processo
ps aux | grep web_api

# Termina processo
sudo kill -9 [PID]

# O usa script fix
sudo /opt/access_control/fix_and_restart.sh
```

### Problema: "libusb_detach_kernel_driver -5"

**Causa**: Permessi USB insufficienti

**Soluzione**: Il servizio DEVE girare come root (già configurato)

### Problema: Dispositivo USB non rilevato

**Verifica**:
```bash
# Lista dispositivi USB
lsusb | grep -E "23d8:0285|04d8:ffee"

# Verifica permessi
ls -la /dev/bus/usb/*/*
```

**Fix permessi**:
```bash
sudo /opt/access_control/setup_crt285_permissions.sh
```

### Problema: Moduli Python non trovati

**Verifica venv**:
```bash
/opt/access_control/venv/bin/python -c "import sys; print(sys.path)"
```

**Reinstalla dipendenze**:
```bash
cd /opt/access_control
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📊 MONITORAGGIO

### Log in tempo reale
```bash
sudo journalctl -u access-control-web -f
```

### Stato servizio
```bash
sudo systemctl status access-control-web
```

### Statistiche sistema
```bash
# CPU e memoria
systemctl status access-control-web --no-pager | grep Memory

# Uptime
systemctl show access-control-web --property=ActiveEnterTimestamp
```

---

## 🔧 MANUTENZIONE

### Backup Sistema (v2.9.0+)

#### Via Web Interface (CONSIGLIATO)
Accedi a http://192.168.1.236:5000/admin/config → Tab "Backup"

**Funzionalità disponibili:**
- Backup completi (.tar.gz) - Include tutto il sistema
- Backup database (.db) - Solo database SQLite
- Schedulazione automatica (giornaliera, settimanale, mensile)
- Cloud sync (AWS S3, Google Cloud, Azure, FTP/SFTP)
- Verifica integrità MD5
- Retention policies automatiche

#### Via Comando (Manuale)
```bash
# Backup completo via API
curl -X POST http://localhost:5000/api/backup/create \
  -H "Content-Type: application/json" \
  -d '{"type":"complete"}'

# Backup database via API  
curl -X POST http://localhost:5000/api/backup/create \
  -H "Content-Type: application/json" \
  -d '{"type":"database"}'

# Backup manuale tradizionale
tar -czf backup_$(date +%Y%m%d).tar.gz /opt/access_control/
```

#### Configurazione Cloud Backup
```bash
# File: /opt/access_control/backups/backup_config.json
{
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

### Aggiornamenti Git
```bash
cd /opt/access_control
git status
git add -A
git commit -m "Descrizione modifiche"
git push
```

### Restart dopo modifiche
```bash
sudo systemctl restart access-control-web
```

---

## 🛡️ SICUREZZA

1. **Servizio gira come root**: Necessario per accesso USB
2. **Binding su 0.0.0.0:5000**: Accessibile da rete
3. **Database SQLite**: File locale, backup regolari
4. **Git privato**: Repository GitHub privato

---

## 📝 COMANDI RAPIDI

```bash
# Avvio
sudo /opt/access_control/fix_and_restart.sh

# Stop
sudo systemctl stop access-control-web

# Restart
sudo systemctl restart access-control-web

# Log
sudo journalctl -u access-control-web -f

# Test manuale
sudo /opt/access_control/venv/bin/python /opt/access_control/src/api/web_api.py
```

---

## 🌐 URL SISTEMA

- **Dashboard**: http://192.168.1.236:5000
- **Admin Config**: http://192.168.1.236:5000/admin/config
- **Test Hardware**: http://192.168.1.236:5000/admin/config#hardware
- **Sistema Backup**: http://192.168.1.236:5000/admin/config → Tab "Backup"
- **Email Configuration**: http://192.168.1.236:5000/admin/config → Tab "Email"
- **Server Sync**: http://192.168.1.236:5000/admin/config → Tab "Server Sync"
- **Real-Time Monitoring**: http://192.168.1.236:5000/admin/config → Sezione "Stato Sistema"

---

## 🆕 NUOVE FUNZIONALITÀ (v2.9.0 - v2.9.3)

### 💾 Sistema Backup Enterprise (v2.9.0)
**Accesso**: http://192.168.1.236:5000/admin/config → Tab "Backup"

#### Caratteristiche principali:
- **Backup schedulati multi-livello**: Giornalieri, settimanali, mensili, annuali
- **Cloud integration**: AWS S3, Google Cloud, Azure, FTP/SFTP
- **Verifica integrità**: Controllo checksum MD5 automatico
- **Retention policies**: Cleanup automatico per spazio disco
- **UI completa**: Gestione backup da interfaccia web

#### Configurazione rapida:
1. Accedi al tab "Backup" nelle configurazioni admin
2. Abilita backup automatici
3. Configura schedulazione (raccomandato: daily database + weekly complete)
4. Opzionale: configura cloud sync per backup remoti
5. Imposta retention (raccomandato: 7 giorni daily, 4 settimane weekly)

### 📧 Sistema Email SMTP Completo (v2.9.1)
**Accesso**: http://192.168.1.236:5000/admin/config → Tab "Email"

#### Configurazione supportata:
- **Provider comuni**: Gmail, Outlook, SMTP personalizzati
- **Sicurezza**: STARTTLS, SSL, OAuth2
- **Test integrato**: Invio email di test dalla UI
- **Nome dinamico**: Usa nome installazione nelle email

#### Setup Gmail/Outlook:
1. Server: smtp.gmail.com / smtp.office365.com
2. Porta: 587 (STARTTLS) o 465 (SSL)
3. Username: tuo_email@gmail.com
4. Password: App Password (non password principale)
5. Test invio per verificare configurazione

### 📊 Monitoraggio Real-Time (v2.9.2)
**Accesso**: http://192.168.1.236:5000/admin/config → Sezione "Stato Sistema"

#### Metriche live:
- **Stato sistema**: Online/Offline con indicatore colorato
- **Uptime**: Tempo di attività formattato automaticamente
- **RAM**: Percentuale utilizzo con colori (blu<60%, giallo 60-80%, rosso>80%)
- **CPU**: Percentuale utilizzo real-time
- **Versione**: Sistema sempre aggiornato
- **Console debug**: 2000 righe log per troubleshooting avanzato

### 🔐 Password Security Avanzata (v2.9.3)
Implementato in tutti i form con campi password:

#### Caratteristiche:
- **Visualizzazione sicura**: Password salvate mostrate come pallini (••••••••)
- **Interazione intelligente**: Click su campo pulisce automaticamente per nuova password
- **Backend sicuro**: Mai password in chiaro nelle risposte API
- **UX migliorata**: Chiara distinzione tra campo vuoto e password salvata

### 🗃️ Database Path Dinamico (v2.6.0)
Sistema migrato con compatibilità completa:

#### Percorsi supportati:
- **Nuovo**: `/opt/access_control/data/access.db` (raccomandato)
- **Vecchio**: `/opt/access_control/src/access.db` (retrocompatibilità)
- **Rilevamento automatico**: Sistema sceglie il path corretto

### 🔄 Sincronizzazione Server Avanzata (v2.5.0)
**Accesso**: http://192.168.1.236:5000/admin/config → Tab "Server Sync"

#### Miglioramenti:
- **Configurazione database**: Storage sicuro in system_settings
- **Status intelligente**: "Connected" se sincronizzato < 24h
- **Sync programmata**: Configurabile da 1h a intervalli custom
- **OdooPartnerConnector**: Metodo `connect()` (rinominato da `authenticate()`)

---

---

## ⚠️ NOTE IMPORTANTI

1. **MAI** modificare direttamente i file in produzione senza Git
2. **SEMPRE** usare il venv per eseguire Python
3. **Il servizio DEVE girare come root** per l'accesso USB
4. **Hardware configurabile da web** senza toccare codice
5. **Auto-restart attivo**: il sistema si riavvia da solo se crasha

---

## 📞 SUPPORTO

Repository: https://github.com/wlkr42/sistema-controllo-accessi
**Ultimo aggiornamento: 08/09/2025 - Versione 2.9.3**

**Principali novità v2.9.3:**
- Password SMTP security fix completa
- Monitoraggio sistema real-time
- Backup enterprise con cloud integration
- Email SMTP configuration completa
- Database path dinamico con retrocompatibilità