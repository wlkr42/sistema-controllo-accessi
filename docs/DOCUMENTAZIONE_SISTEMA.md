# 📚 DOCUMENTAZIONE COMPLETA SISTEMA CONTROLLO ACCESSI
## Sistema RAEE - Comune di Rende

---

## 🎯 PANORAMICA

Sistema di controllo accessi per isola ecologica RAEE con:
- Lettore tessere sanitarie CRT-285/288K
- Controller relè USB-RLY08
- Web interface su porta 5000
- Integrazione Odoo per sincronizzazione utenti
- Sistema robusto con auto-recovery

---

## 🏗️ ARCHITETTURA

### Componenti Hardware
1. **CRT-285/288K** - Lettore tessere sanitarie (USB ID: 23d8:0285)
2. **USB-RLY08** - Controller 8 relè (USB ID: 04d8:ffee)

### Stack Software
- **Python 3.10** con virtual environment
- **Flask** - Web framework
- **SQLite** - Database locale
- **systemd** - Gestione servizio
- **Git** - Versioning (repo: github.com/wlkr42/sistema-controllo-accessi)

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

### Backup
```bash
# Backup completo
tar -czf backup_$(date +%Y%m%d).tar.gz /opt/access_control/

# Backup solo configurazione
tar -czf config_$(date +%Y%m%d).tar.gz /opt/access_control/config/
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
Ultimo aggiornamento: 04/09/2025