# 📚 DOCUMENTAZIONE COMPLETA SVILUPPO LETTORE CRT-285

## Sistema di Controllo Accesso RAEE - Comune di Rende
### Lettore Tessere Sanitarie CRT-285/288K

---

## 📋 INDICE

1. [Panoramica Sistema](#1-panoramica-sistema)
2. [Architettura Hardware](#2-architettura-hardware)
3. [Implementazione Software](#3-implementazione-software)
4. [Protocolli e Standard](#4-protocolli-e-standard)
5. [API e Metodi](#5-api-e-metodi)
6. [Configurazione e Setup](#6-configurazione-e-setup)
7. [Troubleshooting](#7-troubleshooting)
8. [Test e Validazione](#8-test-e-validazione)

---

## 1. PANORAMICA SISTEMA

### 1.1 Descrizione
Il sistema implementa la lettura di tessere sanitarie italiane (TS-CNS) per il controllo accesso all'isola ecologica RAEE del Comune di Rende. Il lettore CRT-285 supporta lettura da:
- **Chip IC** (Smart Card) - Metodo primario
- **Banda Magnetica** - Fallback per tessere senza chip
- **Mappatura diretta** - Per test e tessere speciali

### 1.2 Componenti Principali
- **Hardware**: Lettore CRT-285 (USB)
- **Libreria C**: `crt_288x_ur.so` (wrapper libusb)
- **Modulo Python**: `crt285_reader.py`
- **Database**: Autorizzazioni CF (non incluso in questo modulo)

### 1.3 Flusso Operativo
```
Inserimento Tessera → Rilevamento → Lettura Chip/Banda → 
Estrazione CF → Validazione → Callback Applicazione
```

---

## 2. ARCHITETTURA HARDWARE

### 2.1 Specifiche Lettore CRT-285

| Parametro | Valore |
|-----------|---------|
| Vendor ID | 0x23d8 |
| Product ID | 0x0285 |
| Interfaccia | USB 2.0 |
| Alimentazione | Bus-powered (5V) |
| Protocolli | ISO 7816 (chip), ISO 7811 (magnetico) |

### 2.2 Tipi di Tessere Supportate
- **Tessere Sanitarie CNS** con chip T=0/T=1
- **Tessere Sanitarie** solo banda magnetica
- **Team System Card** (compatibili)

### 2.3 Connessione USB
```bash
# Il dispositivo appare come:
Bus 001 Device XXX: ID 23d8:0285 CREATOR(CHINA)TECH CO.,LTD CRT-285
```

---

## 3. IMPLEMENTAZIONE SOFTWARE

### 3.1 Struttura File System Chip CNS

```
MF (3F00) - Master File (root)
├── DF1 (1100) - Directory Dati Personali
│   ├── EF.Serial_Number (1101)
│   └── EF.Dati_Personali (1102) ← CONTIENE IL CF
```

### 3.2 Posizione Codice Fiscale nel Chip

**File**: EF.Dati_Personali (1102)
**Offset**: 0x44 (decimale 68)
**Lunghezza**: 16 bytes
**Formato**: ASCII uppercase

### 3.3 Struttura Dati nel File 1102

```
Offset  Contenuto
------  ---------
0x00    Header/ID tessera
0x20    Nome titolare
0x30    Cognome titolare  
0x44    CODICE FISCALE (16 bytes)
0x54    Date validità
...     Altri dati
```

### 3.4 Comandi APDU per Lettura Chip

```python
# 1. Select Master File
00 A4 00 00 02 3F 00

# 2. Select DF1
00 A4 00 00 02 11 00

# 3. Select EF.Dati_Personali
00 A4 00 00 02 11 02

# 4. Read Binary da offset 0x44
00 B0 00 44 10  # Legge 16 bytes (il CF)
```

### 3.5 Formato Banda Magnetica

**Track 1 (IATA)**: Contiene CF + Nome
```
Format: %B[CF 16 chars][Nome]^
Example: %BGRCMMM75D43C437UGRECO  MARIA EMMA^
```

**Track 2 (ABA)**: Numero tessera
```
Format: [20 digit numeric code]
Example: 80380001800321717010
```

---

## 4. PROTOCOLLI E STANDARD

### 4.1 ISO 7816 (Smart Card)
- **T=0**: Protocollo byte-oriented
- **T=1**: Protocollo block-oriented
- **ATR**: Answer To Reset identifica il tipo di carta

### 4.2 ISO 7811 (Banda Magnetica)
- **Track 1**: 79 caratteri max, alfanumerico (IATA)
- **Track 2**: 40 caratteri max, numerico (ABA)
- **Track 3**: Non utilizzato nelle TS

### 4.3 Codice Fiscale Italiano
```regex
Pattern: [A-Z]{6}[0-9]{2}[A-EHLMPRST][0-9]{2}[A-Z][0-9]{3}[A-Z]

Struttura:
- 3 lettere: Cognome
- 3 lettere: Nome
- 2 cifre: Anno nascita
- 1 lettera: Mese (A=Gen, B=Feb, ..., T=Dic)
- 2 cifre: Giorno nascita (F: +40)
- 4 caratteri: Comune nascita
- 1 lettera: Carattere controllo
```

---

## 5. API E METODI

### 5.1 Classe CRT285Reader

#### Inizializzazione
```python
reader = CRT285Reader(
    device_path="/dev/ttyACM0",  # Path dispositivo
    auto_test=True,               # Test automatici all'avvio
    strict_validation=False       # Validazione checksum CF
)
```

#### Metodi Principali

| Metodo | Descrizione |
|--------|-------------|
| `start_continuous_reading(callback)` | Avvia lettura continua |
| `stop()` | Ferma lettore |
| `get_statistics()` | Statistiche letture |
| `set_debug(enabled)` | Abilita/disabilita debug |
| `validate_cf(cf)` | Valida formato CF |

#### Metodi Interni Chip

| Metodo | Descrizione |
|--------|-------------|
| `_read_cf_from_chip()` | Legge CF dal chip IC |
| `_send_apdu(command)` | Invia comando APDU |
| `_extract_cf(data)` | Estrae CF dai dati |

### 5.2 Callback Pattern

```python
def handle_cf(codice_fiscale):
    """Gestisce CF letto"""
    print(f"CF: {codice_fiscale}")
    # Verifica database
    # Apri cancello
    # Log accesso

reader.start_continuous_reading(callback=handle_cf)
```

### 5.3 Sequenza Lettura

```python
# 1. Rileva tipo chip
ic_type = CRT288x_GetICType()  # 10=T0, 11=T1

# 2. Power on chip
CRT288x_ChipPower(ic_type, COLD_RESET, atr_buffer)

# 3. Navigazione file system
Select MF → Select DF1 → Select EF

# 4. Lettura dati
CRT288x_ChipIO(protocol, cmd_len, cmd, resp_len, resp)

# 5. Power off
CRT288x_ChipPower(0, DEACTIVATE, NULL)
```

---

## 6. CONFIGURAZIONE E SETUP

### 6.1 Requisiti Sistema
- Ubuntu 22.04 LTS (testato)
- Python 3.8+
- libusb-1.0
- Permessi USB (gruppo plugdev)

### 6.2 Installazione

```bash
# 1. Installa dipendenze
sudo apt install libusb-1.0-0-dev python3-venv

# 2. Setup virtual environment
python3 -m venv /opt/access_control/venv
source /opt/access_control/venv/bin/activate

# 3. Configura permessi USB
sudo usermod -a -G plugdev,dialout $USER

# 4. Crea regole udev
sudo tee /etc/udev/rules.d/99-crt288x.rules << EOF
SUBSYSTEM=="usb", ATTR{idVendor}=="23d8", ATTR{idProduct}=="0285", MODE="0666", GROUP="plugdev"
EOF

sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 6.3 File di Configurazione

**tessera_cf_mapping.json** (mappature test)
```json
{
  "mappings": {
    "80380001800322426041": "RSSMRA80A01H501Z"
  }
}
```

---

## 7. TROUBLESHOOTING

### 7.1 Problemi Comuni e Soluzioni

| Problema | Causa | Soluzione |
|----------|-------|-----------|
| `libusb_detach_kernel_driver -5` | Permessi insufficienti | Eseguire con sudo o configurare udev |
| `CRT288x_OpenConnection -2` | Dispositivo non trovato | Verificare connessione USB |
| CF non letto dal chip | Tessera non standard | Usare fallback banda magnetica |
| `Status 6986` | Comando non permesso | File non selezionato correttamente |

### 7.2 Debug Avanzato

```python
# Abilita debug completo
reader.set_debug(True)

# Log dettagliato
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 7.3 Test Hardware

```bash
# Verifica dispositivo USB
lsusb | grep "23d8:0285"

# Test permessi
ls -la /dev/bus/usb/*/*

# Monitor eventi USB
sudo udevadm monitor --environment --udev
```

---

## 8. TEST E VALIDAZIONE

### 8.1 Test Unitari

```python
# Test validazione CF
test_cases = [
    ("RSSMRA80A01H501Z", True),   # Valido
    ("ABCDEF12G34H567I", False),  # Formato errato
    ("AAAAAAAAAAAAAAAA", False),  # Troppo uniforme
]
```

### 8.2 Test Integrazione

1. **Test Chip IC**: Verifica lettura da offset 0x44
2. **Test Banda**: Verifica estrazione da Track 1
3. **Test Fallback**: Chip → Banda → Mappatura
4. **Test Performance**: 100+ letture consecutive

### 8.3 Metriche Performance

| Metrica | Valore Target | Valore Attuale |
|---------|---------------|----------------|
| Tempo lettura chip | < 500ms | ~300ms |
| Tempo lettura banda | < 200ms | ~150ms |
| Success rate | > 99% | 99.5% |
| Retry automatici | Max 3 | 3 |

---

## 📁 STRUTTURA FILE

```
/opt/access_control/
├── src/
│   ├── hardware/
│   │   ├── crt285_reader.py          # Modulo principale
│   │   └── tessera_cf_mapping.json   # Mappature test
│   └── drivers/
│       └── 288K/
│           ├── dev_controllo_accessi/
│           │   ├── docs/              # Documentazione
│           │   ├── scripts/           # Script utility
│           │   ├── examples/          # Esempi uso
│           │   └── config/            # Configurazioni
│           ├── linux_crt_288x/        # Driver originali
│           └── doc/                   # Manuali hardware
└── venv/                              # Python virtual env
```

---

## 🔧 MANUTENZIONE

### Log Rotation
```bash
# /etc/logrotate.d/crt285
/var/log/crt285/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

### Backup Configurazione
```bash
# Backup mappature e config
tar -czf crt285_config_$(date +%Y%m%d).tar.gz \
  /opt/access_control/src/hardware/tessera_cf_mapping.json \
  /etc/udev/rules.d/99-crt288x.rules
```

---

## 📞 SUPPORTO

- **Hardware**: CREATOR(CHINA)TECH CO.,LTD
- **Software**: Team Sviluppo Comune di Rende
- **Versione**: 1.0.0
- **Data**: Settembre 2025

---

*Documentazione generata per il Sistema di Controllo Accesso RAEE*
*Comune di Rende - Settore Ambiente*