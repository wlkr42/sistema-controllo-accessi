#!/bin/bash
#
# Setup Drivers per Sistema Controllo Accessi
# Installa driver hardware CRT-288K e USB-RLY08
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
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
    
    # Verifica esistenza documentazione driver
    if [ -d "$DRIVERS_DIR/288K" ]; then
        log_info "Trovata documentazione driver in $DRIVERS_DIR/288K"
        
        # Copia librerie se presenti
        if [ -f "$DRIVERS_DIR/288K/libcrt_288_k.so" ]; then
            sudo cp "$DRIVERS_DIR/288K/libcrt_288_k.so" /usr/local/lib/
            sudo ldconfig
            log_info "✓ Libreria CRT-288K installata"
        fi
        
        # Installa dipendenze Python per driver
        pip3 install pyserial 2>/dev/null || true
        
    else
        log_warn "Documentazione driver 288K non trovata in $DRIVERS_DIR/288K"
        log_info "Il driver dovrà essere configurato manualmente"
    fi
    
    # Crea regole udev per lettore tessere
    cat > /tmp/99-card-reader.rules << 'EOF'
# Regole udev per lettore tessere CRT-288K/285
# Permessi per dispositivi seriali USB
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="067b", ATTRS{idProduct}=="2303", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="dialout"

# Alias per lettore tessere
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", SYMLINK+="card_reader"
EOF
    
    sudo mv /tmp/99-card-reader.rules /etc/udev/rules.d/
    log_info "✓ Regole udev per lettore tessere create"
}

# Installa driver USB-RLY08
install_usbrly08() {
    log_info "Installazione driver USB-RLY08..."
    
    # Crea regole udev per relay controller
    cat > /tmp/99-usb-relay.rules << 'EOF'
# Regole udev per USB-RLY08
# Devantech USB-RLY08 relay controller
SUBSYSTEM=="tty", ATTRS{idVendor}=="04d8", ATTRS{idProduct}=="ffee", MODE="0666", GROUP="dialout"
SUBSYSTEM=="usb", ATTRS{idVendor}=="04d8", ATTRS{idProduct}=="ffee", MODE="0666", GROUP="dialout"

# Alias per relay controller
SUBSYSTEM=="tty", ATTRS{idVendor}=="04d8", ATTRS{idProduct}=="ffee", SYMLINK+="relay_controller"
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
    
    # Verifica presenza dispositivi seriali
    if ls /dev/ttyUSB* 2>/dev/null || ls /dev/ttyACM* 2>/dev/null; then
        log_info "✓ Trovati dispositivi seriali:"
        ls -la /dev/ttyUSB* 2>/dev/null || true
        ls -la /dev/ttyACM* 2>/dev/null || true
    else
        log_warn "Nessun dispositivo seriale rilevato"
        log_warn "Verificare che l'hardware sia collegato"
    fi
    
    # Verifica symlink
    if [ -L /dev/card_reader ]; then
        log_info "✓ Symlink card_reader presente"
    fi
    
    if [ -L /dev/relay_controller ]; then
        log_info "✓ Symlink relay_controller presente"
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