# MANUALE COMPLETO
## Lettore Smart Card CRT288x
### Installazione e Configurazione su Ubuntu 22.04 LTS

---

**Versione Documento:** 1.0  
**Data:** Luglio 2025  
**Dispositivo:** CREATOR(CHINA)TECH CO.,LTD CRT-285/288x  
**Sistema Operativo:** Ubuntu 22.04 LTS (64-bit)  
**Autore:** Guida Tecnica Professionale  

---

## INDICE

1. [Panoramica del Sistema](#1-panoramica-del-sistema)
2. [Requisiti e Preparazione](#2-requisiti-e-preparazione)
3. [Identificazione Dispositivo](#3-identificazione-dispositivo)
4. [Struttura Driver e File](#4-struttura-driver-e-file)
5. [Procedura di Installazione](#5-procedura-di-installazione)
6. [Configurazione Sistema](#6-configurazione-sistema)
7. [Compilazione e Test](#7-compilazione-e-test)
8. [Sviluppo Applicazioni](#8-sviluppo-applicazioni)
9. [Wrapper Python](#9-wrapper-python)
10. [Risoluzione Problemi](#10-risoluzione-problemi)
11. [Manutenzione](#11-manutenzione)
12. [Appendici](#12-appendici)

---

## 1. PANORAMICA DEL SISTEMA

### 1.1 Specifiche Dispositivo

**Modello:** CRT-288-K001  
**Identificatori USB:**
- **Vendor ID:** `23d8` (CREATOR(CHINA)TECH CO.,LTD)
- **Product ID:** `0285`
- **Nome Dispositivo:** CRT-285

**Caratteristiche Tecniche:**
- Alimentazione USB: Bus-powered (5V dalla porta USB)
- Alimentazione RS232: DC 5V ±5% esterno obbligatorio
- Consumo: <200 mA
- Interfacce: USB 2.0/3.0 (bus-powered), RS232 (alimentazione esterna)
- Supporto carte: Magnetiche, IC Contact, RFID/NFC
- LED indicatori: Rosso, Blu
- Dimensioni: 118.5 x 99 x 35.1 mm
- Peso: ~240g

**Tipi di Carte Supportate:**
- **Magnetiche:** Track 1, 2, 3 (ISO 7811)
- **IC Contact:** T=0, T=1 CPU Cards, SL4442, SL4428, AT24Cxx
- **RFID/NFC:** Mifare S50/S70, Ultralight, TypeA/B CPU

### 1.2 Architettura Software

```
┌─────────────────────────────────────────┐
│           APPLICAZIONE UTENTE           │
├─────────────────────────────────────────┤
│     Wrapper Python / API C/C++         │
├─────────────────────────────────────────┤
│        libcrt_288x_ur.so (x64)         │
├─────────────────────────────────────────┤
│            libusb-1.0.x                 │
├─────────────────────────────────────────┤
│         Driver USB del Kernel           │
├─────────────────────────────────────────┤
│            Hardware CRT288x             │
└─────────────────────────────────────────┘
```

---

## 2. REQUISITI E PREPARAZIONE

### 2.1 Requisiti Sistema

**Sistema Operativo:**
- Ubuntu 22.04 LTS (64-bit) - **Raccomandato**
- Ubuntu 20.04 LTS (64-bit) - Compatibile
- Debian 11+ (64-bit) - Compatibile

**Hardware:**
- Porta USB 2.0 o superiore
- RAM: minimo 1GB disponibile
- Spazio disco: 50MB per driver e librerie

**Permessi Utente:**
- Accesso sudo per installazione
- Membership nei gruppi `plugdev` e `dialout`

### 2.2 Preparazione Ambiente

```bash
# Aggiorna il sistema
sudo apt update && sudo apt upgrade -y

# Installa dipendenze essenziali
sudo apt install -y \
    build-essential \
    autoconf \
    libtool \
    pkg-config \
    libusb-1.0-0-dev \
    libudev-dev \
    git \
    wget \
    unzip \
    python3 \
    python3-pip

# Installa headers del kernel (se necessario)
sudo apt install -y linux-headers-$(uname -r)
```

### 2.3 Verifica Sistema

```bash
# Verifica architettura (deve essere x86_64)
uname -m

# Verifica versione Ubuntu
lsb_release -a

# Verifica spazio disco
df -h /usr/local

# Verifica permessi USB
ls -la /dev/bus/usb/
```

---

## 3. IDENTIFICAZIONE DISPOSITIVO

### 3.1 Connessione Fisica

**⚠️ IMPORTANTE - Modalità di Alimentazione:**

1. **Modalità USB (Raccomandato):**
   - Collegare **SOLO** il cavo USB
   - Il dispositivo si alimenta direttamente dalla porta USB
   - **NON collegare alimentazione esterna** (causa errori di sistema)

2. **Modalità RS232:**
   - Collegare prima l'alimentatore DC 5V esterno
   - Verificare accensione LED rosso/blu
   - Poi collegare il cavo seriale RS232

**⚠️ ATTENZIONE**: Non mescolare mai le due modalità. Con connessione USB non usare mai alimentazione esterna, il sistema andrà in errore.

### 3.2 Verifica Riconoscimento

```bash
# Prima della connessione
lsusb > /tmp/usb_before.txt

# Collegare il dispositivo
echo "Collega ora il dispositivo CRT288x..."

# Dopo la connessione (attendere 5 secondi)
sleep 5
lsusb > /tmp/usb_after.txt

# Mostra nuovo dispositivo
echo "=== DISPOSITIVO RILEVATO ==="
diff /tmp/usb_before.txt /tmp/usb_after.txt

# Verifica specifica CRT288x
lsusb | grep -i "23d8:0285\|creator\|crt"

# Pulisci file temporanei
rm /tmp/usb_before.txt /tmp/usb_after.txt
```

**Output Atteso:**
```
Bus 001 Device 026: ID 23d8:0285 CREATOR(CHINA)TECH CO.,LTD CRT-285
```

### 3.3 Analisi Dettagliata Dispositivo

```bash
# Informazioni dettagliate dispositivo
lsusb -v -d 23d8:0285

# Controllo endpoints USB
sudo lsusb -v -d 23d8:0285 | grep -A 5 -B 5 "bEndpointAddress"

# Verifica configurazione USB
dmesg | tail -20
```

---

## 4. STRUTTURA DRIVER E FILE

### 4.1 Panoramica Pacchetti

Il software CRT288x viene distribuito nella struttura:

**Struttura directory principale:**
```
288K/
├── 288K-linux-sample/
│   └── 288K/                           # Codice esempio e test
│       ├── crt_288_test                # Eseguibile precompilato
│       ├── crt_288_test.c              # Programma di test
│       ├── crt_288_test.o              # File oggetto
│       ├── crt_288x_ur.h               # Header API
│       ├── crt_288x_ur.so              # Libreria locale
│       ├── libLoadCrt288lib.so         # Libreria caricamento dinamico
│       ├── LoadCrt288lib.c             # Caricatore dinamico
│       ├── LoadCrt288lib.h             # Header caricatore
│       ├── LoadCrt288lib.o             # File oggetto
│       ├── Makefile                    # Script compilazione x64
│       └── Makefile-arm                # Script compilazione ARM
├── linux_crt_288x/
│   └── drivers/                        # ← CARTELLA DRIVER PRINCIPALE
│       ├── libusb/
│       │   └── libusb-1.0.9.tar.bz2    # Dipendenza libusb
│       ├── x64/                        # ← DRIVER x64 (Ubuntu 22.04)
│       │   ├── crt_288x_ur.h           # Header API produzione
│       │   ├── crt_288x_ur.h(EN).txt   # Documentazione inglese
│       │   └── crt_288x_ur.so          # Libreria produzione 64-bit
│       └── x86/                        # Driver 32-bit (non usare)
│           ├── crt_288x_ur.h
│           ├── crt_288x_ur.h(EN).txt
│           └── crt_288x_ur.so
└── verifica_288x.sh                    # Script di verifica automatica
```

**Destinazione finale nel progetto:**
```
/opt/access_control/src/drivers/288K/
```

### 4.2 Identificazione Cartella Corrette

**Per Ubuntu 22.04 (64-bit) usare SEMPRE:**
```
📁 linux_crt_288x/drivers/x64/
```

**⚠️ NON usare:**
- Cartella `x86/` (architettura 32-bit)
- File dalla cartella `288K-linux-sample/288K/` per installazione sistema (solo per sviluppo/test)

### 4.3 File Essenziali

| File | Descrizione | Destinazione |
|------|-------------|--------------|
| `crt_288x_ur.so` | Libreria principale | `/usr/local/lib/` |
| `crt_288x_ur.h` | Header API | `/usr/local/include/` |
| `crt_288_test.c` | Codice test | Sviluppo |
| `LoadCrt288lib.c/h` | Caricamento dinamico | Sviluppo |

---

## 5. PROCEDURA DI INSTALLAZIONE

### 5.1 Installazione nel Progetto

```bash
# Installare nella directory del progetto
sudo mkdir -p /opt/access_control/src/drivers
sudo cp -r 288K/ /opt/access_control/src/drivers/

# Impostare proprietario e permessi
sudo chown -R $USER:$USER /opt/access_control/src/drivers/288K/
sudo chmod +x /opt/access_control/src/drivers/288K/verifica_288x.sh
```

### 5.2 Installazione Libreria Sistema

```bash
# Navigare nella cartella driver x64
cd linux_crt_288x/drivers/x64/

# Verificare presenza file
ls -la
# Output atteso:
# crt_288x_ur.h
# crt_288x_ur.h(EN).txt
# crt_288x_ur.so

# Installare libreria nel sistema
sudo cp crt_288x_ur.so /usr/local/lib/
sudo cp crt_288x_ur.h /usr/local/include/

# Impostare permessi corretti
sudo chmod 644 /usr/local/lib/crt_288x_ur.so
sudo chmod 644 /usr/local/include/crt_288x_ur.h

# Aggiornare cache librerie condivise
sudo ldconfig

# Verificare installazione
echo "=== VERIFICA INSTALLAZIONE ==="
ls -la /usr/local/lib/crt_288x_ur.so
ls -la /usr/local/include/crt_288x_ur.h
ldconfig -p | grep crt || echo "Libreria non nel cache (normale)"
```

### 5.3 Installazione Dipendenze libusb

**Opzione A: Usare versione sistema (Raccomandato)**
```bash
# Installare libusb dalla repository Ubuntu
sudo apt install -y libusb-1.0-0-dev

# Verificare installazione
pkg-config --modversion libusb-1.0
pkg-config --libs libusb-1.0
```

**Opzione B: Compilare versione specifica (Se necessario)**
```bash
# Solo se la versione sistema non funziona
cd "../libusb/libusb-1.0.9"

# Configurare e compilare
./configure --prefix=/usr/local
make
sudo make install
sudo ldconfig
```

### 5.4 Script di Installazione Automatica

```bash
#!/bin/bash
# install_crt288x.sh - Script di installazione automatica

set -e  # Exit on error

echo "=== INSTALLAZIONE CRT288x per Ubuntu 22.04 ==="
echo ""

# Verifica prerequisiti
echo "1. Verifica sistema..."
if [ "$(uname -m)" != "x86_64" ]; then
    echo "❌ ERRORE: Sistema non 64-bit"
    exit 1
fi

if ! command -v gcc &> /dev/null; then
    echo "❌ ERRORE: gcc non installato"
    echo "Esegui: sudo apt install build-essential"
    exit 1
fi

# Trova directory SDK
SDK_DIR=""
for dir in "CRT-288-K001 Linux SDK" "CRT-288-K001_Linux_SDK"; do
    if [ -d "$dir" ]; then
        SDK_DIR="$dir"
        break
    fi
done

if [ -z "$SDK_DIR" ]; then
    echo "❌ ERRORE: Directory SDK non trovata"
    echo "Estrai l'archivio CRT-288-K001 Linux SDK.zip"
    exit 1
fi

echo "✅ SDK trovato in: $SDK_DIR"

# Installazione libreria x64
echo ""
echo "2. Installazione libreria x64..."
X64_DIR="$SDK_DIR/linux-crt_288x_ur-09052016(RS232&USB)/x64"

if [ ! -d "$X64_DIR" ]; then
    echo "❌ ERRORE: Directory x64 non trovata"
    exit 1
fi

cd "$X64_DIR"

if [ ! -f "crt_288x_ur.so" ] || [ ! -f "crt_288x_ur.h" ]; then
    echo "❌ ERRORE: File essenziali mancanti in x64/"
    exit 1
fi

# Backup file esistenti
if [ -f "/usr/local/lib/crt_288x_ur.so" ]; then
    echo "⚠️  Backup libreria esistente..."
    sudo cp /usr/local/lib/crt_288x_ur.so /usr/local/lib/crt_288x_ur.so.backup
fi

# Installazione
sudo cp crt_288x_ur.so /usr/local/lib/
sudo cp crt_288x_ur.h /usr/local/include/
sudo chmod 644 /usr/local/lib/crt_288x_ur.so
sudo chmod 644 /usr/local/include/crt_288x_ur.h
sudo ldconfig

echo "✅ Libreria installata"

# Installazione dipendenze
echo ""
echo "3. Installazione dipendenze..."
sudo apt update
sudo apt install -y libusb-1.0-0-dev libudev-dev

echo "✅ Dipendenze installate"

# Configurazione utente
echo ""
echo "4. Configurazione utente..."
sudo usermod -a -G plugdev,dialout $USER

echo "✅ Utente aggiunto ai gruppi necessari"

# Configurazione udev
echo ""
echo "5. Configurazione regole udev..."
sudo tee /etc/udev/rules.d/99-crt288x.rules > /dev/null << EOF
# CRT288x Smart Card Reader
SUBSYSTEM=="usb", ATTR{idVendor}=="23d8", ATTR{idProduct}=="0285", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb_device", ATTR{idVendor}=="23d8", ATTR{idProduct}=="0285", MODE="0666", GROUP="plugdev"
KERNEL=="ttyUSB*", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", MODE="0666", GROUP="plugdev"
KERNEL=="ttyACM*", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", MODE="0666", GROUP="plugdev"
EOF

sudo udevadm control --reload-rules
sudo udevadm trigger

echo "✅ Regole udev configurate"

# Preparazione ambiente test
echo ""
echo "6. Preparazione ambiente test..."
cd ../../
SAMPLE_DIR="288K-linux-sample source code"

if [ -d "$SAMPLE_DIR" ]; then
    # Crea directory test utente
    mkdir -p ~/crt288x-test
    cp "$SAMPLE_DIR"/* ~/crt288x-test/ 2>/dev/null || true
    cd ~/crt288x-test
    
    # Compila programma test
    if [ -f "Makefile" ]; then
        make clean 2>/dev/null || true
        if make; then
            echo "✅ Programma test compilato"
        else
            echo "⚠️  Compilazione test fallita"
        fi
    fi
else
    echo "⚠️  Directory sample non trovata"
fi

# Verifica finale
echo ""
echo "=== VERIFICA INSTALLAZIONE ==="
echo "Libreria installata:"
ls -la /usr/local/lib/crt_288x_ur.so 2>/dev/null && echo "✅ Libreria OK" || echo "❌ Libreria mancante"

echo "Header installato:"
ls -la /usr/local/include/crt_288x_ur.h 2>/dev/null && echo "✅ Header OK" || echo "❌ Header mancante"

echo "Dispositivo collegato:"
if lsusb | grep -q "23d8:0285"; then
    echo "✅ Dispositivo rilevato"
    lsusb | grep "23d8:0285"
else
    echo "⚠️  Dispositivo non rilevato (collegarlo se necessario)"
fi

echo ""
echo "=== INSTALLAZIONE COMPLETATA ==="
echo ""
echo "PROSSIMI PASSI:"
echo "1. Logout e login per applicare i gruppi utente"
echo "2. Collegare il dispositivo CRT288x"
echo "3. Testare con: cd ~/crt288x-test && ./crt_288_test"
echo ""
echo "Per sviluppo:"
echo "- Header API: /usr/local/include/crt_288x_ur.h"
echo "- Libreria: /usr/local/lib/crt_288x_ur.so"
echo "- Link con: -lcrt_288x_ur -L/usr/local/lib"
echo ""
```

---

## 6. CONFIGURAZIONE SISTEMA

### 6.1 Permessi Utente

```bash
# Aggiungere utente ai gruppi necessari
sudo usermod -a -G plugdev,dialout $USER

# Verificare appartenenza gruppi
groups $USER

# Applicare modifiche (logout/login richiesto)
echo "⚠️  IMPORTANTE: Eseguire logout/login per applicare i gruppi"
```

### 6.2 Regole udev

```bash
# Creare file regole udev
sudo nano /etc/udev/rules.d/99-crt288x.rules
```

**Contenuto file:**
```bash
# CRT288x Smart Card Reader Rules
# Vendor ID: 23d8, Product ID: 0285

# USB device rules
SUBSYSTEM=="usb", ATTR{idVendor}=="23d8", ATTR{idProduct}=="0285", MODE="0666", GROUP="plugdev", TAG+="uaccess"
SUBSYSTEM=="usb_device", ATTR{idVendor}=="23d8", ATTR{idProduct}=="0285", MODE="0666", GROUP="plugdev"

# TTY device rules (for serial communication)
KERNEL=="ttyUSB*", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", MODE="0666", GROUP="plugdev", TAG+="uaccess"
KERNEL=="ttyACM*", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", MODE="0666", GROUP="plugdev", TAG+="uaccess"

# HID device rules (if applicable)
KERNEL=="hidraw*", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", MODE="0666", GROUP="plugdev", TAG+="uaccess"

# Alternative rules for different subsystems
SUBSYSTEMS=="usb", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", MODE="0666", GROUP="plugdev"
```

```bash
# Ricaricare regole udev
sudo udevadm control --reload-rules
sudo udevadm trigger

# Verificare regole
udevadm info -a -p $(udevadm info -q path -n /dev/bus/usb/001/026) | grep -i "23d8\|0285"
```

### 6.3 Configurazione Variabili Ambiente

```bash
# Aggiungere al ~/.bashrc
echo '# CRT288x Environment' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
echo 'export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH' >> ~/.bashrc
echo 'export C_INCLUDE_PATH=/usr/local/include:$C_INCLUDE_PATH' >> ~/.bashrc

# Ricaricare configurazione
source ~/.bashrc
```

### 6.4 Configurazione Sistemd (Opzionale)

Per applicazioni che richiedono avvio automatico:

```bash
# Creare servizio systemd
sudo nano /etc/systemd/system/crt288x-monitor.service
```

**Contenuto:**
```ini
[Unit]
Description=CRT288x Card Reader Monitor
After=multi-user.target
Wants=multi-user.target

[Service]
Type=simple
User=your_username
ExecStart=/usr/local/bin/crt288x-monitor
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## 7. COMPILAZIONE E TEST

### 7.1 Preparazione Area Test

```bash
# Creare directory test
mkdir -p ~/crt288x-development
cd ~/crt288x-development

# Copiare file di esempio
cp "~/crt288x-install/CRT-288-K001 Linux SDK/288K-linux-sample source code"/* .

# Verificare file
ls -la
```

### 7.2 Compilazione Programma Test

```bash
# Pulire compilazioni precedenti
make clean 2>/dev/null || rm -f *.o crt_288_test 2>/dev/null

# Compilare usando Makefile
make

# Verificare eseguibile
ls -la crt_288_test
file crt_288_test
```

**Se make fallisce, compilazione manuale:**
```bash
# Compilare file oggetto
gcc -c crt_288_test.c -o crt_288_test.o -I/usr/local/include
gcc -c LoadCrt288lib.c -o LoadCrt288lib.o -I/usr/local/include

# Linkare eseguibile
gcc -o crt_288_test crt_288_test.o LoadCrt288lib.o -ldl -L/usr/local/lib

# Oppure compilazione diretta
gcc -o crt_288_test crt_288_test.c LoadCrt288lib.c -ldl -I/usr/local/include -L/usr/local/lib
```

### 7.3 Test Completo Dispositivo

#### 7.3.1 Preparazione Test

```bash
# Verificare dispositivo collegato
lsusb | grep "23d8:0285"
# Output atteso: Bus 001 Device XXX: ID 23d8:0285 CREATOR(CHINA)TECH CO.,LTD CRT-285

# Navigare nella directory test
cd 288K-linux-sample/288K/

# Verificare eseguibile compilato
ls -la crt_288_test
file crt_288_test

# Eseguire il programma di test
./crt_288_test
```

#### 7.3.2 Menu Programma Test

Il programma presenta questo menu interattivo:

```
==========Welcome to using crt_603_vx_test==========
	0:  quit.
	1:  Show menu .
	2:  Turn on the device .
	3:  Initialize and unlock .
	4:  Check status .
	5:  Lock card status .
	6:  Lock card .
	7:  Indicator operation .
	8:  Read all tracks .
	9:  Clear track information .
	10: Test contact IC card .
	11: Test contactless IC card .
Please select a test option :
```

#### 7.3.3 Sequenza Test Consigliata

**STEP 1: Connessione Dispositivo**
```bash
# Selezionare opzione: 2
Please select a test option : 2

# Selezionare modalità USB: 0
Please enter the open type, 0 to open in USB mode, 1 to open in COM port mode: 0

# Output atteso:
CRT288U_Open 
iGetLen:22
TempRecvBuf[2]:12
CRT288x_OpenConnection success!
```

**STEP 2: Inizializzazione**
```bash
# Selezionare opzione: 3
Please select a test option : 3

# Output atteso:
CRT288x_InitDev success!
```

**STEP 3: Test Status Carta**
```bash
# Selezionare opzione: 4 (ripetere per testare inserimento/rimozione carte)
Please select a test option : 4

# Output possibili:
No card                    # Nessuna carta
have card                  # Carta presente
```

**STEP 4: Test LED**
```bash
# Selezionare opzione: 7
Please select a test option : 7

# Output atteso:
CRT288x_LEDProcess success!
# I LED rosso e blu dovrebbero lampeggiare
```

**STEP 5: Test Carta Magnetica** (inserire carta con banda magnetica)
```bash
# Selezionare opzione: 8
Please select a test option : 8

# Output esempio:
CRT288x_ReadAllTracks success! 
	Track1: GRCMMM75D43C437UGRECO  MARIA EMMA
	Track2: 1234567890123456789
	Track3: 
```

**STEP 6: Test Carta IC/Chip** (inserire carta con chip)
```bash
# Selezionare opzione: 10
Please select a test option : 10

# Output esempio:
T=1 CPU Card
CRT288x_ChipPower success! 
ATR: 3b ff 18 00 00 81 31 fe 45 00 6b 05 05 91 20 01 f1 01 43 4e 53 10 31 80 38 03 d6 
CRT288x_ChipIO success! [00A4040007A0000000031010] 
Recv: 6a 82 03 25
```

**STEP 7: Test Carta Contactless** (avvicinare carta RFID/NFC)
```bash
# Selezionare opzione: 11
Please select a test option : 11

# Output varia in base al tipo di carta contactless
```

#### 7.3.4 Interpretazione Output

**Connessione Riuscita:**
- `CRT288x_OpenConnection success!`
- `iGetLen:22` - Lunghezza risposta dispositivo
- `TempRecvBuf[2]:12` - Codice risposta (esadecimale)

**Stati Carta:**
- `No card` - Nessuna carta nel lettore
- `have card` - Carta inserita correttamente

**Tipi Carte IC:**
- `T=0 CPU Card` - Carta CPU protocollo T=0
- `T=1 CPU Card` - Carta CPU protocollo T=1  
- `SL4442 Card` - Memory card SL4442
- `AT24C01 Card` - EEPROM AT24C01
- `Unknow IC Card` - Tipo non riconosciuto

**ATR (Answer To Reset):**
- Stringa esadecimale che identifica il tipo di carta chip
- Esempio: `3b ff 18 00 00...` 

**Comandi APDU:**
- `[00A4040007A0000000031010]` - Comando inviato alla carta
- `Recv: 6a 82 03 25` - Risposta della carta

#### 7.3.5 Risoluzione Problemi Test

**Errore Connessione:**
```bash
# Se ottieni errori di connessione:
CRT288x_OpenConnection Error iRet: -204

# Soluzioni:
1. Verificare dispositivo collegato: lsusb | grep "23d8:0285"
2. Controllare permessi utente: groups $USER
3. Verificare regole udev: cat /etc/udev/rules.d/99-crt288x.rules
4. Ricaricare regole: sudo udevadm control --reload-rules
```

**Problemi Lettura Carte:**
```bash
# Errori comuni lettura:
CRT288x_ReadAllTracks Error iRet: -221

# Soluzioni:
1. Pulire banda magnetica carta
2. Inserire carta completamente
3. Provare con carta diversa
4. Verificare che carta abbia banda magnetica
```

**Test Fallimento LED:**
```bash
# Se LED non si accendono:
1. Verificare alimentazione USB
2. Controllare connessione cavo
3. Verificare stato dispositivo con opzione 4
```

#### 7.3.6 Script Test Automatico

Per test automatizzati, creare script:

```bash
cat > test_automatico_crt288x.sh << 'EOF'
#!/bin/bash

echo "=== TEST AUTOMATICO CRT288x ==="

# Test connessione
echo "2" | timeout 10 ./crt_288_test | grep -q "success" && echo "✓ Connessione OK" || echo "✗ Connessione FAIL"

# Test inizializzazione  
echo -e "3\n0" | timeout 5 ./crt_288_test | grep -q "success" && echo "✓ Inizializzazione OK" || echo "✗ Inizializzazione FAIL"

# Test status
status_output=$(echo -e "4\n0" | timeout 5 ./crt_288_test)
if echo "$status_output" | grep -q "No card\|have card"; then
    echo "✓ Status check OK"
else
    echo "✗ Status check FAIL"
fi

echo "=== TEST COMPLETATO ==="
EOF

chmod +x test_automatico_crt288x.sh
./test_automatico_crt288x.sh
```

### 7.4 Test Avanzati

```bash
# Test con debugging
strace -e trace=openat,read,write ./crt_288_test

# Test memoria
valgrind ./crt_288_test

# Test prestazioni
time ./crt_288_test
```

---

## 8. SVILUPPO APPLICAZIONI

### 8.1 Template Applicazione C

```c
// crt288x_app_template.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "crt_288x_ur.h"

int main() {
    int result;
    
    printf("=== Applicazione CRT288x ===\n");
    
    // 1. Connessione dispositivo
    result = CRT288x_OpenConnection(0, 0, 9600);  // USB mode
    if (result != 0) {
        fprintf(stderr, "Errore connessione: %d\n", result);
        return 1;
    }
    printf("Dispositivo connesso\n");
    
    // 2. Inizializzazione
    result = CRT288x_InitDev(1);  // Unlock
    if (result != 0) {
        fprintf(stderr, "Errore inizializzazione: %d\n", result);
        CRT288x_CloseConnection();
        return 1;
    }
    printf("Dispositivo inizializzato\n");
    
    // 3. Loop principale applicazione
    while (1) {
        int card_status = CRT288x_GetCardStatus();
        
        switch (card_status) {
            case 1:  // No card
                break;
            case 2:  // Card at entrance
                printf("Carta rilevata all'ingresso\n");
                break;
            case 3:  // Card inside
                printf("Carta inserita\n");
                
                // Esempio lettura carta magnetica
                char track1[512], track2[512], track3[512];
                if (CRT288x_ReadAllTracks(track1, track2, track3) == 0) {
                    printf("Track 1: %s\n", track1);
                    printf("Track 2: %s\n", track2);
                    printf("Track 3: %s\n", track3);
                }
                
                // Esempio test carta IC
                int ic_type = CRT288x_GetICType();
                if (ic_type > 0) {
                    printf("Carta IC tipo: %d\n", ic_type);
                }
                
                break;
        }
        
        usleep(200000);  // 200ms delay
    }
    
    // 4. Cleanup
    CRT288x_CloseConnection();
    return 0;
}
```

### 8.2 Compilazione Template

```bash
# Compilare template
gcc -o crt288x_app crt288x_app_template.c -lcrt_288x_ur -L/usr/local/lib -I/usr/local/include

# Eseguire
./crt288x_app
```

### 8.3 Makefile per Sviluppo

```makefile
# Makefile per applicazioni CRT288x

CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -g
LDFLAGS = -L/usr/local/lib
LDLIBS = -lcrt_288x_ur -ldl
INCLUDES = -I/usr/local/include

# Targets
TARGETS = crt288x_app crt288x_test_simple

all: $(TARGETS)

crt288x_app: crt288x_app_template.o
	$(CC) $(LDFLAGS) -o $@ $^ $(LDLIBS)

crt288x_test_simple: crt288x_test_simple.o
	$(CC) $(LDFLAGS) -o $@ $^ $(LDLIBS)

%.o: %.c
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

clean:
	rm -f *.o $(TARGETS)

install: all
	sudo cp $(TARGETS) /usr/local/bin/

.PHONY: all clean install
```

### 8.4 Gestione Errori

```c
// Codici errore comuni
#define CRT_SUCCESS                  0
#define CRT_ERR_CMD                  -201
#define CRT_ERR_CMDPARAM             -202
#define CRT_ERR_DEVNOTSUP            -204
#define CRT_ERR_COMMTIMEOUT          -280

const char* crt_error_string(int error_code) {
    switch (error_code) {
        case CRT_SUCCESS: return "Success";
        case CRT_ERR_CMD: return "Command error";
        case CRT_ERR_CMDPARAM: return "Command parameter error";
        case CRT_ERR_DEVNOTSUP: return "Device not supported";
        case CRT_ERR_COMMTIMEOUT: return "Communication timeout";
        default: return "Unknown error";
    }
}

// Uso:
int result = CRT288x_OpenConnection(0, 0, 9600);
if (result != 0) {
    printf("Errore: %s (%d)\n", crt_error_string(result), result);
}
```

---

## 9. WRAPPER PYTHON

### 9.1 Installazione Wrapper

```bash
# Salvare wrapper Python
cd ~/crt288x-development
cat > crt288x_python.py << 'EOF'
#!/usr/bin/env python3
"""
CRT288x Python Wrapper - Versione Professionale
"""

import ctypes
import ctypes.util
import os
import sys
import time
from typing import Tuple, Optional, List, Union
from enum import IntEnum

class CardStatus(IntEnum):
    """Stati della carta"""
    NO_CARD = 1
    CARD_AT_ENTRANCE = 2
    CARD_INSIDE = 3
    DEVICE_OFFLINE = 9

class ICType(IntEnum):
    """Tipi di carte IC"""
    UNKNOWN = 0
    T0_CPU = 10
    T1_CPU = 11
    SL4442 = 20
    SL4428 = 21
    AT24C01 = 30
    AT24C02 = 31
    AT24C04 = 32
    AT24C08 = 33
    AT24C16 = 34
    AT24C32 = 35
    AT24C64 = 36

class LEDType(IntEnum):
    """Tipi LED"""
    RED = 0
    BLUE = 1
    ALL = 2

class LEDState(IntEnum):
    """Stati LED"""
    OFF = 0
    ON = 1
    FLASHING = 2

class CRT288xError(Exception):
    """Eccezione specifica per errori CRT288x"""
    pass

class CRT288x:
    """
    Wrapper Python professionale per CRT288x
    
    Esempio d'uso:
        with CRT288x() as device:
            if device.connect():
                status = device.get_card_status()
                if status == CardStatus.CARD_INSIDE:
                    tracks = device.read_magnetic_tracks()
    """
    
    def __init__(self, library_path: Optional[str] = None, debug: bool = False):
        self.lib = None
        self.is_connected = False
        self.debug = debug
        
        if library_path is None:
            library_path = self._find_library()
        
        self._load_library(library_path)
        self._setup_function_prototypes()
    
    def _find_library(self) -> str:
        """Trova la libreria CRT288x nel sistema"""
        search_paths = [
            '/usr/local/lib/libcrt_288x_ur.so',
            '/usr/lib/libcrt_288x_ur.so',
            './libcrt_288x_ur.so',
            './crt_288x_ur.so'
        ]
        
        for path in search_paths:
            if os.path.exists(path):
                if self.debug:
                    print(f"Libreria trovata: {path}")
                return path
        
        raise CRT288xError("Libreria CRT288x non trovata")
    
    def _load_library(self, path: str) -> None:
        """Carica la libreria condivisa"""
        try:
            self.lib = ctypes.CDLL(path)
            if self.debug:
                print(f"Libreria caricata: {path}")
        except OSError as e:
            raise CRT288xError(f"Errore caricamento libreria {path}: {e}")
    
    def _setup_function_prototypes(self) -> None:
        """Configura i prototipi delle funzioni C"""
        
        # CRT288x_OpenConnection
        self.lib.CRT288x_OpenConnection.argtypes = [
            ctypes.c_int, ctypes.c_int, ctypes.c_long
        ]
        self.lib.CRT288x_OpenConnection.restype = ctypes.c_int
        
        # CRT288x_CloseConnection
        self.lib.CRT288x_CloseConnection.argtypes = []
        self.lib.CRT288x_CloseConnection.restype = ctypes.c_int
        
        # CRT288x_InitDev
        self.lib.CRT288x_InitDev.argtypes = [ctypes.c_int]
        self.lib.CRT288x_InitDev.restype = ctypes.c_int
        
        # CRT288x_GetCardStatus
        self.lib.CRT288x_GetCardStatus.argtypes = []
        self.lib.CRT288x_GetCardStatus.restype = ctypes.c_int
        
        # CRT288x_GetICType
        self.lib.CRT288x_GetICType.argtypes = []
        self.lib.CRT288x_GetICType.restype = ctypes.c_int
        
        # CRT288x_LEDProcess
        self.lib.CRT288x_LEDProcess.argtypes = [ctypes.c_int, ctypes.c_int]
        self.lib.CRT288x_LEDProcess.restype = ctypes.c_int
        
        # CRT288x_ReadAllTracks
        self.lib.CRT288x_ReadAllTracks.argtypes = [
            ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p
        ]
        self.lib.CRT288x_ReadAllTracks.restype = ctypes.c_int
    
    def connect(self, mode: int = 0, com_port: int = 0, baud_rate: int = 9600) -> bool:
        """
        Connette al dispositivo CRT288x
        
        Args:
            mode: 0 per USB, 1 per RS232
            com_port: Porta seriale (ignorata per USB)
            baud_rate: Velocità comunicazione
            
        Returns:
            True se connessione riuscita
            
        Raises:
            CRT288xError: Se connessione fallisce
        """
        result = self.lib.CRT288x_OpenConnection(mode, com_port, baud_rate)
        self.is_connected = (result == 0)
        
        if not self.is_connected:
            raise CRT288xError(f"Connessione fallita: codice errore {result}")
        
        if self.debug:
            print("Connessione stabilita")
        
        return True
    
    def disconnect(self) -> bool:
        """Disconnette dal dispositivo"""
        if not self.is_connected:
            return True
        
        result = self.lib.CRT288x_CloseConnection()
        self.is_connected = False
        
        if self.debug:
            print("Connessione chiusa")
        
        return result == 0
    
    def initialize(self, unlock: bool = True) -> bool:
        """
        Inizializza il dispositivo
        
        Args:
            unlock: True per sbloccare il meccanismo carte
            
        Returns:
            True se inizializzazione riuscita
        """
        if not self.is_connected:
            raise CRT288xError("Dispositivo non connesso")
        
        mode = 1 if unlock else 0
        result = self.lib.CRT288x_InitDev(mode)
        
        if result != 0:
            raise CRT288xError(f"Inizializzazione fallita: codice {result}")
        
        if self.debug:
            print("Dispositivo inizializzato")
        
        return True
    
    def get_card_status(self) -> CardStatus:
        """
        Ottiene lo stato della carta
        
        Returns:
            CardStatus enum value
        """
        if not self.is_connected:
            return CardStatus.DEVICE_OFFLINE
        
        status = self.lib.CRT288x_GetCardStatus()
        return CardStatus(status)
    
    def get_ic_type(self) -> ICType:
        """
        Ottiene il tipo di carta IC inserita
        
        Returns:
            ICType enum value
        """
        if not self.is_connected:
            raise CRT288xError("Dispositivo non connesso")
        
        ic_type = self.lib.CRT288x_GetICType()
        try:
            return ICType(ic_type)
        except ValueError:
            return ICType.UNKNOWN
    
    def control_led(self, led_type: LEDType, state: LEDState) -> bool:
        """
        Controlla i LED del dispositivo
        
        Args:
            led_type: Tipo di LED da controllare
            state: Stato desiderato del LED
            
        Returns:
            True se comando riuscito
        """
        if not self.is_connected:
            raise CRT288xError("Dispositivo non connesso")
        
        result = self.lib.CRT288x_LEDProcess(int(led_type), int(state))
        return result == 0
    
    def read_magnetic_tracks(self) -> Tuple[str, str, str]:
        """
        Legge tutte le tracce magnetiche
        
        Returns:
            Tupla (track1, track2, track3)
            
        Raises:
            CRT288xError: Se lettura fallisce
        """
        if not self.is_connected:
            raise CRT288xError("Dispositivo non connesso")
        
        # Crea buffer per le tracce
        track1_buf = ctypes.create_string_buffer(1024)
        track2_buf = ctypes.create_string_buffer(1024)
        track3_buf = ctypes.create_string_buffer(1024)
        
        result = self.lib.CRT288x_ReadAllTracks(
            track1_buf, track2_buf, track3_buf
        )
        
        if result != 0:
            raise CRT288xError(f"Lettura tracce fallita: codice {result}")
        
        # Decodifica dati
        track1 = track1_buf.value.decode('utf-8', errors='ignore').strip()
        track2 = track2_buf.value.decode('utf-8', errors='ignore').strip()
        track3 = track3_buf.value.decode('utf-8', errors='ignore').strip()
        
        return track1, track2, track3
    
    def wait_for_card(self, timeout: float = 30.0) -> bool:
        """
        Attende inserimento carta
        
        Args:
            timeout: Timeout in secondi
            
        Returns:
            True se carta inserita entro il timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.get_card_status() == CardStatus.CARD_INSIDE:
                return True
            time.sleep(0.1)
        
        return False
    
    def wait_for_card_removal(self, timeout: float = 30.0) -> bool:
        """
        Attende rimozione carta
        
        Args:
            timeout: Timeout in secondi
            
        Returns:
            True se carta rimossa entro il timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.get_card_status() == CardStatus.NO_CARD:
                return True
            time.sleep(0.1)
        
        return False
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

# Funzioni di utilità
def scan_for_devices() -> List[str]:
    """Scansiona dispositivi CRT288x collegati"""
    import subprocess
    
    try:
        result = subprocess.run(
            ['lsusb'], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        devices = []
        for line in result.stdout.split('\n'):
            if '23d8:0285' in line:
                devices.append(line.strip())
        
        return devices
    except subprocess.CalledProcessError:
        return []

def test_device_basic():
    """Test base del dispositivo"""
    print("=== Test Base CRT288x ===")
    
    # Cerca dispositivi
    devices = scan_for_devices()
    if not devices:
        print("❌ Nessun dispositivo CRT288x trovato")
        return False
    
    print(f"✅ Dispositivo trovato: {devices[0]}")
    
    try:
        with CRT288x(debug=True) as device:
            # Connetti
            device.connect()
            device.initialize()
            
            # Test LED
            print("Test LED...")
            device.control_led(LEDType.RED, LEDState.ON)
            time.sleep(1)
            device.control_led(LEDType.BLUE, LEDState.ON)
            time.sleep(1)
            device.control_led(LEDType.ALL, LEDState.OFF)
            
            # Test stato carta
            print("Controllo stato carta...")
            status = device.get_card_status()
            print(f"Stato: {status.name}")
            
            if status == CardStatus.CARD_INSIDE:
                print("Lettura carta...")
                try:
                    tracks = device.read_magnetic_tracks()
                    for i, track in enumerate(tracks, 1):
                        if track:
                            print(f"Track {i}: {track[:50]}...")
                except CRT288xError as e:
                    print(f"Errore lettura: {e}")
                
                # Test carta IC
                try:
                    ic_type = device.get_ic_type()
                    print(f"Tipo IC: {ic_type.name}")
                except CRT288xError as e:
                    print(f"Errore IC: {e}")
            
            print("✅ Test completato con successo")
            return True
            
    except CRT288xError as e:
        print(f"❌ Errore test: {e}")
        return False
    except Exception as e:
        print(f"❌ Errore imprevisto: {e}")
        return False

if __name__ == "__main__":
    test_device_basic()
EOF

# Rendere eseguibile
chmod +x crt288x_python.py
```

### 9.2 Test Wrapper Python

```bash
# Test base
python3 crt288x_python.py

# Test interattivo
python3 -c "
from crt288x_python import CRT288x
with CRT288x() as device:
    device.connect()
    device.initialize()
    print('Stato carta:', device.get_card_status().name)
"
```

---

## 10. RISOLUZIONE PROBLEMI

### 10.1 Problemi Comuni

**Problema: Dispositivo non riconosciuto**
```bash
# Verifica connessione fisica
lsusb | grep -i "23d8\|creator\|crt"

# Se non appare, verificare:
# 1. Cavo USB funzionante
# 2. Porta USB funzionante  
# 3. NON usare alimentazione esterna con USB (causa conflitti)
# 4. Per RS232: verificare alimentazione esterna 5V

# Test con dmesg
dmesg | tail -20

# Riprova connessione USB
sudo rmmod usbcore
sudo modprobe usbcore
```

**Problema: Permessi negati**
```bash
# Verificare gruppi utente
groups $USER

# Aggiungere ai gruppi mancanti
sudo usermod -a -G plugdev,dialout $USER

# Logout/login richiesto
# oppure
newgrp plugdev
```

**Problema: Libreria non trovata**
```bash
# Verificare installazione
ls -la /usr/local/lib/crt_288x_ur.so
ls -la /usr/local/include/crt_288x_ur.h

# Aggiornare cache
sudo ldconfig

# Verificare cache
ldconfig -p | grep crt

# Se mancante, reinstallare
sudo cp crt_288x_ur.so /usr/local/lib/
sudo ldconfig
```

**Problema: Compilazione fallisce**
```bash
# Verificare dipendenze
pkg-config --libs libusb-1.0
pkg-config --cflags libusb-1.0

# Installare se mancanti
sudo apt install libusb-1.0-0-dev

# Compilazione verbose
gcc -v -o test test.c -lcrt_288x_ur -L/usr/local/lib
```

### 10.2 Debug Avanzato

**Analisi comunicazione USB**
```bash
# Installare wireshark per USB
sudo apt install wireshark tshark

# Catturare traffico USB
sudo tshark -i usbmon1 -f "usb.device_address == 26"

# Oppure usare usbmon
sudo cat /sys/kernel/debug/usb/usbmon/1u
```

**Analisi chiamate sistema**
```bash
# Tracciare chiamate sistema
strace -e trace=openat,read,write,ioctl ./crt_288_test

# Tracciare solo USB
strace -e trace=ioctl ./crt_288_test 2>&1 | grep -i usb
```

**Test isolato libreria**
```bash
# Creare test minimo
cat > test_minimal.c << 'EOF'
#include <stdio.h>
#include <dlfcn.h>

int main() {
    void *lib = dlopen("/usr/local/lib/crt_288x_ur.so", RTLD_LAZY);
    if (!lib) {
        printf("Errore caricamento: %s\n", dlerror());
        return 1;
    }
    
    printf("Libreria caricata correttamente\n");
    dlclose(lib);
    return 0;
}
EOF

gcc -o test_minimal test_minimal.c -ldl
./test_minimal
```

### 10.3 Log e Diagnostica

**Abilitare log dettagliati**
```bash
# Creare script di diagnostica
cat > crt288x_diag.sh << 'EOF'
#!/bin/bash

echo "=== DIAGNOSTICA CRT288x ==="
echo "Data: $(date)"
echo "Sistema: $(uname -a)"
echo ""

echo "1. Dispositivi USB:"
lsusb | grep -E "(23d8|creator|crt|card|reader)" || echo "Nessun dispositivo trovato"
echo ""

echo "2. Moduli kernel USB:"
lsmod | grep usb
echo ""

echo "3. File dispositivo:"
ls -la /dev/bus/usb/001/ | grep -v "001"
echo ""

echo "4. Librerie installate:"
ls -la /usr/local/lib/crt*
ls -la /usr/local/include/crt*
echo ""

echo "5. Regole udev:"
cat /etc/udev/rules.d/99-crt288x.rules 2>/dev/null || echo "Regole non trovate"
echo ""

echo "6. Gruppi utente:"
groups $USER
echo ""

echo "7. Variabili ambiente:"
echo "LD_LIBRARY_PATH: $LD_LIBRARY_PATH"
echo "PKG_CONFIG_PATH: $PKG_CONFIG_PATH"
echo ""

echo "8. Test libreria:"
if python3 -c "import ctypes; ctypes.CDLL('/usr/local/lib/crt_288x_ur.so')" 2>/dev/null; then
    echo "✅ Libreria caricabile"
else
    echo "❌ Problema caricamento libreria"
fi
echo ""

echo "=== FINE DIAGNOSTICA ==="
EOF

chmod +x crt288x_diag.sh
./crt288x_diag.sh
```

---

## 11. MANUTENZIONE

### 11.1 Aggiornamenti

**Backup configurazione corrente**
```bash
# Creare backup
mkdir -p ~/crt288x-backup/$(date +%Y%m%d)
cp /usr/local/lib/crt_288x_ur.so ~/crt288x-backup/$(date +%Y%m%d)/
cp /usr/local/include/crt_288x_ur.h ~/crt288x-backup/$(date +%Y%m%d)/
cp /etc/udev/rules.d/99-crt288x.rules ~/crt288x-backup/$(date +%Y%m%d)/
```

**Verifica integrità**
```bash
# Checksum file
md5sum /usr/local/lib/crt_288x_ur.so
sha256sum /usr/local/lib/crt_288x_ur.so

# Test funzionalità
python3 crt288x_python.py
```

### 11.2 Monitoraggio Sistema

**Script monitoraggio**
```bash
cat > crt288x_monitor.sh << 'EOF'
#!/bin/bash

LOG_FILE="/var/log/crt288x.log"
DEVICE_ID="23d8:0285"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

while true; do
    if lsusb | grep -q "$DEVICE_ID"; then
        if [ ! -f "/tmp/crt288x_connected" ]; then
            log_message "Dispositivo CRT288x connesso"
            touch "/tmp/crt288x_connected"
        fi
    else
        if [ -f "/tmp/crt288x_connected" ]; then
            log_message "Dispositivo CRT288x disconnesso"
            rm -f "/tmp/crt288x_connected"
        fi
    fi
    
    sleep 5
done
EOF

chmod +x crt288x_monitor.sh
```

### 11.3 Performance

**Ottimizzazioni sistema**
```bash
# Disabilitare autosuspend USB per il dispositivo
echo '23d8:0285' | sudo tee /sys/bus/usb/drivers/usb/new_id

# Aumentare priorità processo
nice -n -10 ./crt_288_test

# Configurazione udev per prestazioni
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="23d8", ATTR{idProduct}=="0285", ATTR{power/autosuspend}="-1"' | \
sudo tee -a /etc/udev/rules.d/99-crt288x.rules
```

---

## 12. APPENDICI

### Appendice A: Codici Errore

| Codice | Descrizione | Soluzione |
|--------|-------------|-----------|
| -201 | Command error | Verificare formato comando |
| -202 | Command parameter error | Controllare parametri |
| -203 | Command cannot be executed | Verificare stato dispositivo |
| -204 | Hardware not supported | Controllare compatibilità |
| -280 | Communication timeout | Verificare connessione |

### Appendice B: Mapping GPIO (Se Applicabile)

| Pin | Funzione | Direzione |
|-----|----------|-----------|
| 1 | +5V | Alimentazione |
| 2 | GND | Massa |
| 3 | Data+ | I/O |
| 4 | Data- | I/O |

### Appendice C: Protocolli Supportati

**Carte Magnetiche:**
- ISO 7811-1/2/3
- Track 1: 76 caratteri max
- Track 2: 37 caratteri max  
- Track 3: 104 caratteri max

**Carte IC:**
- ISO 7816-1/2/3/4
- T=0, T=1 protocols
- Voltage: 1.8V, 3V, 5V
- Clock: 1-5 MHz

**RFID/NFC:**
- ISO 14443 Type A/B
- ISO 15693
- Frequency: 13.56 MHz

### Appendice D: Comandi APDU Comuni

```c
// Select Application
BYTE select_cmd[] = {0x00, 0xA4, 0x04, 0x00, 0x07, 0xA0, 0x00, 0x00, 0x00, 0x03, 0x10, 0x10};

// Get Response
BYTE get_response[] = {0x00, 0xC0, 0x00, 0x00, 0x00};

// Read Binary
BYTE read_binary[] = {0x00, 0xB0, 0x00, 0x00, 0x00};
```

### Appendice E: Risorse e Supporto

**Documentazione Ufficiale:**
- CRT288K001 V1.0 Specification.pdf
- CRT288K001 Communication Protocol.pdf

**Siti Web:**
- [CREATOR Tech Official](http://www.creator-china.com)
- [Ubuntu Documentation](https://help.ubuntu.com/)
- [libusb Documentation](https://libusb.sourceforge.io/)

**Community e Forum:**
- Stack Overflow: tag `smart-card`, `libusb`
- Ubuntu Forums: Hardware sezione
- GitHub: progetti open source correlati

---

**© 2025 - Manuale Tecnico CRT288x**  
**Versione 1.0 - Tutti i diritti riservati**

---

*Questo documento è stato creato per fornire una guida completa e professionale per l'installazione e configurazione del lettore smart card CRT288x su sistemi Ubuntu 22.04 LTS. Per aggiornamenti e supporto, consultare la documentazione ufficiale del produttore.*
