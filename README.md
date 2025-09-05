# Sistema Controllo Accessi - v2.1.0

Sistema completo per il controllo degli accessi tramite tessera sanitaria con gestione hardware, interfaccia web e funzionalità avanzate.

## ✨ Ultime Novità (v2.1.0)

- 🕐 **Gestione Timezone Configurabile**: Nuova sezione Orologio per configurare fuso orario
- 📊 **Export Avanzato**: Esportazione log in CSV, Excel e PDF
- 🔧 **Fix Timestamp**: Correzione visualizzazione ora locale (era 2 ore indietro)
- 📚 **Documentazione Completa**: Nuova cartella `/docs` con guide dettagliate

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
sudo systemctl start controllo-accessi
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

- Lettore tessere **CRT-285** (USB)
- Controller relè **USB-RLY08** (USB-Serial)
- Ubuntu Server 20.04+ o Debian 11+
- 2GB RAM, 10GB disco

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