# 🚀 Guida Installazione Sistema Controllo Accessi RAEE

## Prerequisiti

- **Sistema Operativo**: Ubuntu 20.04+ o Debian 11+
- **Accesso**: Root o sudo
- **Rete**: Connessione internet per download dipendenze
- **GitHub**: Account con accesso al repository privato

## Installazione Rapida (Raccomandato)

### 1. Prepara le Credenziali GitHub

Crea un Personal Access Token su GitHub:
1. Vai su GitHub → Settings → Developer settings → Personal access tokens
2. Genera nuovo token con permessi `repo`
3. Copia il token generato

### 2. Esegui l'Installazione

```bash
# Setta le credenziali
export GIT_USERNAME="tuo_username_github"
export GIT_PASSWORD="tuo_personal_access_token"

# Esegui installazione one-liner
curl -sL https://raw.githubusercontent.com/wlkr42/sistema-controllo-accessi/main/scripts/install/install_system.sh | sudo bash -s production
```

## Installazione Manuale

### 1. Clone Repository

```bash
# Clone con credenziali
git clone https://USERNAME:TOKEN@github.com/wlkr42/sistema-controllo-accessi.git /opt/access_control

# Entra nella directory
cd /opt/access_control
```

### 2. Esegui Script Installazione

```bash
# Per ambiente produzione
sudo bash scripts/install/install_system.sh production

# Per ambiente sviluppo
sudo bash scripts/install/install_system.sh development
```

## Installazione Non Presidiata (per Deploy Multipli)

### 1. Prepara File Credenziali

```bash
# Crea file credenziali sicuro
cat > ~/.git_credentials_raee << EOF
export GIT_USERNAME='tuo_username'
export GIT_PASSWORD='tuo_token'
EOF

# Proteggi il file
chmod 600 ~/.git_credentials_raee
```

### 2. Esegui Auto-Installer

```bash
# Download e esegui auto-installer
curl -sL https://raw.githubusercontent.com/wlkr42/sistema-controllo-accessi/main/scripts/install/auto_install.sh -o auto_install.sh
chmod +x auto_install.sh
sudo ./auto_install.sh production
```

## Cosa Fa l'Installazione

L'installer automatico esegue:

1. **Verifica Sistema**
   - Controlla OS compatibile
   - Verifica permessi root
   - Testa connessione GitHub

2. **Installazione Dipendenze**
   - Pacchetti sistema (Python, SQLite, USB libs)
   - Virtual environment Python
   - Pacchetti Python da requirements.txt

3. **Configurazione Hardware**
   - Driver CRT-285 (lettore tessere)
   - Driver USB-RLY08 (controller relè)
   - Regole udev per permessi USB
   - Gruppi utente (dialout, tty)

4. **Setup Database**
   - Crea `/opt/access_control/data/access.db`
   - Inizializza schema tabelle
   - Crea utente admin (admin/admin123)

5. **Configurazione Servizi**
   - Servizio systemd `access-control-web`
   - Monitor 24/7 `access-monitor`
   - Logrotate per rotazione log
   - Cron jobs per backup

6. **Avvio Sistema**
   - Start servizi systemd
   - Verifica stato servizi
   - Test endpoint health

## Post-Installazione

### 1. Verifica Installazione

```bash
# Controlla servizi
systemctl status access-control-web
systemctl status access-monitor

# Test API
curl http://localhost:5000/api/health

# Controlla log
journalctl -u access-control-web -f
```

### 2. Primo Accesso

1. Apri browser: `http://IP_SERVER:5000`
2. Login con:
   - Username: `admin`
   - Password: `admin123`
3. **IMPORTANTE**: Cambia subito la password admin!

### 3. Configurazione Hardware

Se l'hardware non viene rilevato automaticamente:

```bash
# Lista dispositivi USB
lsusb

# Verifica porte seriali
ls -la /dev/tty*

# Test manuale lettore
python3 /opt/access_control/src/hardware/test_reader.py
```

## Troubleshooting

### Errore: "Database not found"
```bash
# Crea manualmente il database
mkdir -p /opt/access_control/data
python3 /opt/access_control/scripts/install/setup_database.py /opt/access_control/data/access.db
```

### Errore: "HTTP2 framing layer"
Lo script gestisce automaticamente con retry e fallback HTTP/1.1

### Errore: Credenziali GitHub
- Usa Personal Access Token, non password
- Verifica che il token abbia permessi `repo`
- Per caratteri speciali, lo script fa URL encoding automatico

### Servizio non si avvia
```bash
# Verifica errori
journalctl -xe

# Riavvia servizio
systemctl restart access-control-web

# Reinstalla servizio
bash /opt/access_control/scripts/install/setup_services.sh production
```

## Aggiornamento

```bash
cd /opt/access_control
git pull origin main
pip install -r requirements.txt
systemctl restart access-control-web
```

## Disinstallazione

```bash
# Stop e disabilita servizi
systemctl stop access-control-web access-monitor
systemctl disable access-control-web access-monitor

# Rimuovi servizi
rm /etc/systemd/system/access-control*.service
systemctl daemon-reload

# Rimuovi installazione (ATTENZIONE: cancella tutto!)
rm -rf /opt/access_control
```

## Supporto

Per assistenza:
- Apri issue su GitHub
- Controlla log: `/opt/access_control/logs/`
- Documentazione: `/opt/access_control/docs/`

---

**Sistema Controllo Accessi RAEE v3.0.0**  
**© 2025 - Tutti i diritti riservati**