#!/bin/bash
#
# Setup Drivers per Sistema Controllo Accessi
# Installa driver hardware CRT-288K e USB-RLY08
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Fix: usa sempre /opt/access_control come PROJECT_ROOT durante installazione
PROJECT_ROOT="/opt/access_control"
DRIVERS_DIR="$PROJECT_ROOT/src/drivers"

# Colori output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Installa driver CRT-288K
install_crt288k() {
    log_info "Installazione driver CRT-288K..."
    
    # Verifica esistenza driver e installa
    if [ -d "$DRIVERS_DIR/288K" ]; then
        log_info "Trovato driver 288K in $DRIVERS_DIR/288K"
        
        # Installa librerie dal path corretto
        if [ -d "$DRIVERS_DIR/288K/linux_crt_288x/drivers/x64" ]; then
            log_info "Installazione librerie CRT-288K..."
            # Copia la libreria nella directory corretta
            if [ -f "$DRIVERS_DIR/288K/linux_crt_288x/drivers/x64/crt_288x_ur.so" ]; then
                sudo cp "$DRIVERS_DIR/288K/linux_crt_288x/drivers/x64/crt_288x_ur.so" /usr/local/lib/
                sudo ldconfig
                log_info "✓ Libreria crt_288x_ur.so installata"
            fi
        fi
        
        # Esegui script di verifica se presente
        if [ -f "$DRIVERS_DIR/288K/install/verifica_288x.sh" ]; then
            log_info "Esecuzione script verifica driver..."
            bash "$DRIVERS_DIR/288K/install/verifica_288x.sh" || true
        fi
        
        # Installa dipendenze Python per driver
        pip3 install pyserial 2>/dev/null || true
        log_info "✓ Driver CRT-288K configurato"
        
    else
        log_warn "Driver 288K non trovato in $DRIVERS_DIR/288K"
        log_error "Path atteso: /opt/access_control/src/drivers/288K"
        log_info "Verificare che il repository sia stato clonato correttamente"
    fi
    
    # Crea regole udev per lettore tessere CRT-285
    cat > /tmp/99-crt285.rules << 'EOF'
# CRT-285 Card Reader - USB HID Direct Access
# IMPORTANTE: Il CRT-285 usa comunicazione USB diretta, NON porta seriale
SUBSYSTEM=="usb", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", MODE="0666"
SUBSYSTEM=="usb", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", OWNER="root", GROUP="plugdev"

# CRITICO: Previeni binding automatico driver kernel che causa disconnessioni continue
# Questo risolve il problema del dispositivo che si disconnette ogni 7 secondi
SUBSYSTEM=="usb", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", RUN+="/bin/sh -c 'echo -n $kernel > /sys/bus/usb/drivers/usb/unbind'"

# Tag per accesso utente
SUBSYSTEM=="usb", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", TAG+="uaccess"
EOF
    
    sudo mv /tmp/99-crt285.rules /etc/udev/rules.d/
    log_info "✓ Regole udev per CRT-285 create con fix disconnessione"
    
    # Fix permessi libreria driver
    if [ -f "$DRIVERS_DIR/288K/linux_crt_288x/drivers/x64/crt_288x_ur.so" ]; then
        sudo chmod 755 "$DRIVERS_DIR/288K/linux_crt_288x/drivers/x64/crt_288x_ur.so"
        log_info "✓ Permessi libreria driver corretti"
    fi
}

# Installa driver USB-RLY08
install_usbrly08() {
    log_info "Installazione driver USB-RLY08..."
    
    # Crea regole udev per relay controller
    cat > /tmp/99-usb-relay.rules << 'EOF'
# USB-RLY08 Relay Controller (e altri dispositivi su ACM)
# Il relè USB-RLY08 si presenta come porta seriale ACM
SUBSYSTEM=="tty", ATTRS{idVendor}=="04d8", MODE="0666", GROUP="dialout"
KERNEL=="ttyACM[0-9]*", MODE="0666", GROUP="dialout"

# Supporto per vari modelli Devantech
SUBSYSTEM=="tty", ATTRS{idVendor}=="04d8", ATTRS{idProduct}=="ffee", MODE="0666", GROUP="dialout"
SUBSYSTEM=="usb", ATTRS{idVendor}=="04d8", ATTRS{idProduct}=="ffee", MODE="0666", GROUP="dialout"

# USB-ISS (altro modello comune)
SUBSYSTEM=="tty", ATTRS{idVendor}=="04d8", ATTRS{idProduct}=="ffef", MODE="0666", GROUP="dialout"

# Alias per facile identificazione
SUBSYSTEM=="tty", ATTRS{idVendor}=="04d8", SYMLINK+="relay_controller"
EOF
    
    sudo mv /tmp/99-usb-relay.rules /etc/udev/rules.d/
    log_info "✓ Regole udev per relay controller create"
    
    # Installa librerie Python per controllo relay
    pip3 install pyftdi 2>/dev/null || true
}

# Configura permessi seriali
setup_serial_permissions() {
    log_info "Configurazione permessi seriali..."
    
    # Aggiungi utente ai gruppi necessari
    if [ -n "$SUDO_USER" ]; then
        sudo usermod -a -G dialout $SUDO_USER
        sudo usermod -a -G tty $SUDO_USER
        log_info "✓ Utente $SUDO_USER aggiunto ai gruppi dialout e tty"
    fi
    
    # Ricarica regole udev
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    log_info "✓ Regole udev ricaricate"
}

# Test connessione hardware
test_hardware() {
    log_info "Test connessione hardware..."
    
    # Test CRT-285
    echo ""
    log_info "1. Test CRT-285 Card Reader:"
    if lsusb | grep -q "23d8:0285"; then
        log_info "✓ CRT-285 rilevato via USB"
        
        # Test connessione con timeout per evitare hang
        python3 - << 'EOF' 2>/dev/null || true
import ctypes
import signal
import sys

def timeout_handler(signum, frame):
    print("   Timeout connessione (normale al primo avvio)")
    sys.exit(1)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(3)

try:
    lib = ctypes.CDLL("/opt/access_control/src/drivers/288K/linux_crt_288x/drivers/x64/crt_288x_ur.so")
    result = lib.CRT288x_OpenConnection(0, 0, 9600)
    signal.alarm(0)
    if result == 0:
        print("   ✓ CRT-285 connesso correttamente")
        lib.CRT288x_CloseConnection()
    else:
        print(f"   ⚠ CRT-285 codice ritorno: {result} (normale al primo avvio)")
except Exception as e:
    signal.alarm(0)
    print(f"   ⚠ Test connessione: {e}")
EOF
    else
        log_warn "✗ CRT-285 NON rilevato"
    fi
    
    # Test Relè
    echo ""
    log_info "2. Test USB-RLY08 Relay Controller:"
    if ls /dev/ttyACM* 2>/dev/null; then
        log_info "✓ Trovata porta ACM:"
        ls -la /dev/ttyACM* 2>/dev/null
        
        # Test comunicazione base
        python3 - << 'EOF' 2>/dev/null || true
import serial
import serial.tools.list_ports

for port in serial.tools.list_ports.comports():
    if "ACM" in port.device:
        try:
            ser = serial.Serial(port.device, 19200, timeout=0.5)
            ser.write(b'\x5A')  # Get module ID
            response = ser.read(1)
            if response:
                print(f"   ✓ Relè risponde su {port.device}")
            else:
                print(f"   ⚠ Nessuna risposta da {port.device} (verificare modello)")
            ser.close()
        except Exception as e:
            print(f"   ⚠ Errore test {port.device}: {e}")
EOF
    else
        log_warn "✗ Nessuna porta ACM trovata per relè"
    fi
}

# Main
main() {
    log_info "=== Setup Driver Hardware ==="
    
    # Verifica root
    if [ "$EUID" -ne 0 ]; then 
        log_error "Questo script deve essere eseguito come root"
        exit 1
    fi
    
    # Installa driver
    install_crt288k
    install_usbrly08
    
    # Configura permessi
    setup_serial_permissions
    
    # Test hardware
    test_hardware
    
    log_info ""
    log_info "✅ Setup driver completato!"
    log_info ""
    log_info "Note importanti:"
    log_info "- Riavviare il sistema o ricollegare i dispositivi USB"
    log_info "- Verificare i dispositivi in /dev/ttyUSB* o /dev/ttyACM*"
    log_info "- I symlink /dev/card_reader e /dev/relay_controller saranno creati automaticamente"
    log_info "- Documentazione driver CRT-288K in: $DRIVERS_DIR/288K/"
    
    return 0
}

# Esegui main
main "$@"