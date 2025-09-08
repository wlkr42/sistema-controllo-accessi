# Sistema Controllo Accessi - v2.9.3

Sistema completo per il controllo degli accessi tramite tessera sanitaria con gestione hardware, interfaccia web e funzionalità avanzate.

## ✨ Ultime Novità (v2.9.3)

- 🔒 **Fix Sicurezza Password SMTP**: Password ora nascosta con pallini (••••••••) invece di testo in chiaro
- 🎯 **Gestione Password Intelligente**: Click sul campo svuota automaticamente per nuova password
- 🛡️ **Sicurezza Migliorata**: Nessun invio di dati sensibili se password non modificata

## ✨ Novità v2.9.2

- 📊 **Statistiche Sistema Real-Time**: Metriche live CPU, RAM, uptime in dashboard admin
- 📝 **Console Debug Potenziata**: Visualizzazione estesa fino a 2000 righe di log
- 🎨 **Dashboard Dinamica**: Aggiornamento automatico ogni 5 secondi delle metriche
- 🔧 **Monitoraggio Sistema**: Integrazione psutil per metriche hardware accurate

## ✨ Novità v2.9.1

- 📧 **Configurazione Email SMTP**: Sistema completo per invio email con test integrato
- 🏷️ **Nome Installazione Dinamico**: Tutte le email usano il nome configurato in sistema
- 🔧 **Bug Fix Email**: Risolti problemi salvataggio configurazione SMTP
- 📚 **Documentazione Aggiornata**: API documentation completa per modulo email

## ✨ Novità v2.9.0 

- 💾 **Sistema Backup & Restore Completo**: Backup schedulati con verifica integrità
- 🔐 **Checksum MD5**: Verifica automatica integrità backup
- 📅 **Backup Automatici**: Schedulazione crontab configurabile da UI

## ✨ Novità v2.7.1

- 🎨 **UI Dashboard Migliorata**: Rimosso pulsante Test Accessi ridondante
- 🎨 **Colori Uniformati**: Tutti i pulsanti dashboard ora con schema colori coerente
- 🔧 **Pulizia Codice**: Rimossi elementi UI non necessari

## ✨ Novità v2.7.0

- 👤 **Profili Utente Estesi**: Sistema completo gestione profili con avatar
- 🔐 **Password Management Avanzato**: Validazione rigorosa, reset via email, storico password
- 📸 **Upload Avatar**: Supporto immagini profilo con anteprima real-time
- 📝 **Campi Profilo**: Nome, cognome, telefono, bio per ogni utente sistema
- 🎨 **UI Migliorata**: Modal profilo ridisegnato, form creazione utente ottimizzato

## ✨ Novità v2.6.0

- 🗄️ **Database Migrato**: Database spostato da `/src` a `/data` per struttura corretta
- 🔧 **Configurazione Centralizzata**: Nuovo sistema gestione path database unificato

## ✨ Novità v2.5.0

- 🔄 **Server Sync**: Sincronizzazione automatica con server remoto configurabile
- 📄 **Paginazione Utenti**: Sistema paginazione con selezione elementi (30/50/100/tutti)
- 🕐 **Fix Date Visualizzazione**: Formato date completo con ora (DD/MM/YYYY HH:MM:SS)
- 🗂️ **Interfaccia Ottimizzata**: Rimosse colonne non necessarie, migliore UX

## ✨ Funzionalità v2.4.0

- 📦 **Sistema Backup Enterprise**: Backup schedulati multi-livello con cloud
- 🔐 **Verifica Integrità**: Controllo automatico checksum backup
- ☁️ **Cloud Storage**: Supporto AWS S3, Google Cloud, Azure, FTP/SFTP
- 📊 **Retention Policies**: Gestione automatica spazio e pulizia

## 🚀 Quick Start

```bash
# Clone repository
cd /opt
git clone https://github.com/wlkr42/sistema-controllo-accessi.git access_control
cd access_control

# Setup ambiente
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Inizializza database
python3 scripts/init_database.py

# Avvia servizio
sudo systemctl start access-control-web
```

## 📋 Caratteristiche

- ✅ Lettura tessera sanitaria con CRT-285
- ✅ Controllo 8 relè via USB-RLY08
- ✅ Dashboard web completa
- ✅ Gestione utenti e permessi
- ✅ Configurazione fasce orarie
- ✅ Export dati in multipli formati
- ✅ Console debug real-time
- ✅ Backup automatici

## 📖 Documentazione

Tutta la documentazione è disponibile nella cartella [`/docs`](docs/):

- [Sistema Overview](docs/SISTEMA_OVERVIEW.md) - Panoramica architettura
- [API Documentation](docs/API_DOCUMENTATION.md) - Endpoint REST API
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Guida sviluppatore
- [Timezone Config](docs/TIMEZONE_CONFIG.md) - Gestione timezone
- [Export System](docs/EXPORT_SYSTEM.md) - Sistema esportazione
- [Changelog](docs/CHANGELOG.md) - Storico modifiche

## 🖥️ Interfaccia Web

Accedi a: `http://SERVER_IP:5000`

**Credenziali default:**
- Username: `admin`
- Password: `admin123`

⚠️ **Cambia la password al primo accesso!**

## 🔧 Requisiti Hardware

- Lettore tessere **CRT-285** (USB diretto - NON richiede porta seriale)
- Controller relè **USB-RLY08** (USB-Serial - richiede porta seriale es. /dev/ttyACM0)
- Ubuntu Server 20.04+ o Debian 11+
- 2GB RAM, 10GB disco

### ⚠️ IMPORTANTE: Configurazione Hardware
- **CRT-285**: Comunicazione USB diretta, NON configurare porta seriale
- **USB-RLY08**: DEVE essere configurato con la porta seriale corretta (verificare con `ls /dev/tty*`)

## 🌳 Branch Structure

- `main` - Versione stabile in produzione
- `release/v2.1.0-timezone-export` - Release corrente
- `debug-working-*` - Branch di sviluppo
- `feature/*` - Nuove funzionalità
- `hotfix/*` - Fix urgenti

## 📦 Versioni

- **v2.1.0** (2025-09-05) - Timezone e Export
- **v2.0.0** (2025-09-04) - Debug Console
- **v1.0.0** (2025-09-03) - Release iniziale

## 🤝 Contributing

1. Fork il repository
2. Crea branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit modifiche (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri Pull Request

## 📞 Supporto

Per problemi o domande:
1. Controlla la [documentazione](docs/)
2. Apri una [issue](https://github.com/wlkr42/sistema-controllo-accessi/issues)
3. Consulta il [changelog](docs/CHANGELOG.md)

## 📄 Licenza

Proprietario - Tutti i diritti riservati

---

**Sviluppato con ❤️ per la gestione dell'Isola Ecologica**