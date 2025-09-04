# Pacchetto Installazione Sistema Controllo Accessi

## File del pacchetto
- `sistema-controllo-accessi-20250725_053438.tar.gz` - Archivio principale
- `sistema-controllo-accessi-20250725_053438.tar.gz.md5` - Checksum per verifica integrità

## Installazione
1. Estrarre: `tar -xzf sistema-controllo-accessi-20250725_053438.tar.gz`
2. Entrare nella directory: `cd sistema-controllo-accessi-20250725_053438`
3. Eseguire installazione: `sudo bash install.sh`

## Disinstallazione
Per rimuovere completamente il sistema:
```bash
sudo bash uninstall.sh
```

## Verifica sistema
Dopo l'installazione:
```bash
sudo bash /opt/access_control/scripts/check_system.sh
```

## Requisiti di sistema
- Ubuntu 22.04 LTS
- Python 3.8+
- Accesso root per l'installazione
- 500MB spazio libero su disco

## Informazioni pacchetto
- Data creazione: Fri Jul 25 05:34:39 AM UTC 2025
- Versione: 20250725_053438
- Dimensione: 4.8M

## Post-installazione
- **URL sistema**: http://localhost:5000
- **Utente sistema**: wlkr42
- **Directory**: /opt/access_control
- **Log**: /var/log/access_control/

## Utenti di default
- **admin/admin123** - Amministratore completo
- **manager/manager123** - Gestore utenti e orari
- **viewer/viewer123** - Solo visualizzazione

## Gestione servizio
- Avvio: `sudo systemctl start access-control`
- Stop: `sudo systemctl stop access-control`
- Restart: `sudo systemctl restart access-control`
- Status: `sudo systemctl status access-control`
- Log: `sudo journalctl -u access-control -f`

## Backup manuale
```bash
sudo -u wlkr42 /opt/access_control/scripts/backup.sh
```

## Supporto
Per problemi o domande, consultare la documentazione nel sistema installato.
