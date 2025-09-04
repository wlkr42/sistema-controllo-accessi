# Guida Installazione Sistema Controllo Accessi

## Requisiti Sistema
- Linux (Ubuntu/Debian consigliato)
- Python 3.8+
- systemd
- Utente con privilegi sudo

## Procedura Installazione

### 1. Preparazione
```bash
# Crea directory temporanea
mkdir ~/install_access_control
cd ~/install_access_control

# Copia il pacchetto di installazione
cp /path/to/sistema-controllo-accessi.tar.gz .
cp /path/to/sistema-controllo-accessi.tar.gz.md5 .  # se disponibile
```

### 2. Estrazione
```bash
# Estrai il pacchetto
tar xzf sistema-controllo-accessi.tar.gz
cd installazione
```

### 3. Installazione
```bash
# Rendi eseguibile lo script
chmod +x scripts/install.sh

# Esegui installazione come root
sudo ./scripts/install.sh
```

### 4. Verifica Installazione

Lo script eseguirà automaticamente:
- Verifica requisiti sistema
- Backup di eventuali installazioni precedenti
- Installazione dipendenze
- Configurazione hardware
- Setup database
- Configurazione cron jobs
- Creazione e avvio servizio systemd

Al termine dell'installazione:
1. Verifica che il servizio sia attivo:
```bash
sudo systemctl status access-control
```

2. Controlla i log:
```bash
tail -f /opt/access_control/install.log
```

3. Accedi all'interfaccia web:
```
http://localhost:5000
```

### 5. Risoluzione Problemi

Se riscontri problemi:

1. **Servizio non parte**:
```bash
sudo systemctl status access-control
sudo journalctl -u access-control -f
```

2. **Hardware non rilevato**:
```bash
# Verifica regole udev
ls -l /dev/ttyUSB*
sudo udevadm control --reload-rules
sudo udevadm trigger
```

3. **Database non accessibile**:
```bash
# Verifica permessi
ls -l /opt/access_control/src/access.db
sudo chown www-data:www-data /opt/access_control/src/access.db
sudo chmod 664 /opt/access_control/src/access.db
```

### 6. Backup e Ripristino

Per backup manuale:
```bash
sudo /opt/access_control/scripts/backup.sh
```

Per ripristino da backup:
```bash
sudo /opt/access_control/scripts/restore.sh /path/to/backup.db
```

## Note Importanti

1. **Sicurezza**:
   - Cambiare le password predefinite dopo l'installazione
   - Limitare l'accesso alla porta 5000 solo alla rete locale
   - Mantenere backup regolari del database

2. **Manutenzione**:
   - Controllare regolarmente i log in `/opt/access_control/logs/`
   - Verificare lo spazio su disco per i backup
   - Testare periodicamente il funzionamento dell'hardware

3. **Aggiornamenti**:
   - Backup prima di ogni aggiornamento
   - Seguire le note di rilascio per istruzioni specifiche
   - Testare in ambiente di sviluppo prima di aggiornare produzione

Per assistenza contattare il supporto tecnico.
