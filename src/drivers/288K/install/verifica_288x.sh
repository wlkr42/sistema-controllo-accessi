#!/bin/bash

# verifica_288x.sh - Script di verifica e installazione CRT288x
# Versione: 2.0
# Compatibile con qualsiasi posizione della cartella 288K/

set -e  # Exit on error

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzioni di utilità
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Determina la directory dello script e trova la cartella 288K/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_288K_DIR=""

# Funzione per trovare la cartella 288K
find_288k_directory() {
    log_info "Ricerca cartella 288K/ ..."
    
    # Lista delle possibili posizioni relative allo script
    local search_paths=(
        "$SCRIPT_DIR"                           # Stesso directory dello script
        "$SCRIPT_DIR/.."                        # Directory padre
        "$SCRIPT_DIR/../.."                     # Due livelli sopra
        "$SCRIPT_DIR/288K"                      # Sottodirectory
        "$(pwd)"                                # Directory corrente
        "$(pwd)/288K"                           # 288K nella directory corrente
        "/opt/access_control/src/drivers/288K"  # Posizione di destinazione
    )
    
    for path in "${search_paths[@]}"; do
        if [[ -d "$path/linux_crt_288x/drivers/x64" ]]; then
            BASE_288K_DIR="$(realpath "$path")"
            log_success "Cartella 288K trovata in: $BASE_288K_DIR"
            return 0
        elif [[ -d "$path/288K/linux_crt_288x/drivers/x64" ]]; then
            BASE_288K_DIR="$(realpath "$path/288K")"
            log_success "Cartella 288K trovata in: $BASE_288K_DIR"
            return 0
        fi
    done
    
    # Ricerca ricorsiva nell'albero delle directory
    log_info "Ricerca ricorsiva in corso..."
    local found_path
    found_path=$(find "$SCRIPT_DIR" -maxdepth 3 -type d -name "288K" 2>/dev/null | head -1)
    
    if [[ -n "$found_path" && -d "$found_path/linux_crt_288x/drivers/x64" ]]; then
        BASE_288K_DIR="$(realpath "$found_path")"
        log_success "Cartella 288K trovata ricorsivamente in: $BASE_288K_DIR"
        return 0
    fi
    
    log_error "Cartella 288K/ non trovata!"
    log_error "Assicurati che lo script sia posizionato correttamente rispetto alla struttura 288K/"
    return 1
}

# Verifica prerequisiti sistema
check_system_requirements() {
    log_info "Verifica prerequisiti sistema..."
    
    # Verifica architettura
    if [[ "$(uname -m)" != "x86_64" ]]; then
        log_error "Sistema non 64-bit ($(uname -m)). Richiesto x86_64."
        return 1
    fi
    log_success "Architettura x86_64 confermata"
    
    # Verifica Ubuntu/Debian
    if ! command -v lsb_release &> /dev/null; then
        log_warning "lsb_release non trovato, installo..."
        sudo apt update && sudo apt install -y lsb-release
    fi
    
    local os_info
    os_info=$(lsb_release -d 2>/dev/null || echo "Unknown")
    log_info "Sistema operativo: $os_info"
    
    # Verifica strumenti essenziali
    local required_tools=("gcc" "make" "lsusb" "ldconfig")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "Strumento richiesto non trovato: $tool"
            log_info "Installa con: sudo apt install build-essential usbutils"
            return 1
        fi
    done
    log_success "Strumenti essenziali presenti"
    
    return 0
}

# Verifica dispositivo CRT288x
check_device_connection() {
    log_info "Verifica connessione dispositivo CRT288x..."
    
    if lsusb | grep -q "23d8:0285"; then
        local device_info
        device_info=$(lsusb | grep "23d8:0285")
        log_success "Dispositivo CRT288x rilevato:"
        echo "    $device_info"
        return 0
    else
        log_warning "Dispositivo CRT288x non rilevato"
        log_info "Verifica che il dispositivo sia:"
        log_info "  - Collegato via USB (senza alimentazione esterna)"
        log_info "  - Porta USB funzionante" 
        log_info "  - LED rosso/blu accesi"
        return 1
    fi
}

# Verifica struttura file 288K
verify_288k_structure() {
    log_info "Verifica struttura cartella 288K..."
    
    local required_files=(
        "linux_crt_288x/drivers/x64/crt_288x_ur.so"
        "linux_crt_288x/drivers/x64/crt_288x_ur.h"
        "288K-linux-sample/288K/crt_288_test.c"
        "288K-linux-sample/288K/Makefile"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$BASE_288K_DIR/$file" ]]; then
            log_error "File mancante: $file"
            return 1
        fi
    done
    
    log_success "Struttura 288K verificata"
    
    # Mostra informazioni sui file principali
    log_info "File driver x64:"
    ls -la "$BASE_288K_DIR/linux_crt_288x/drivers/x64/"
    
    return 0
}

# Installa libreria nel sistema
install_system_library() {
    log_info "Installazione libreria sistema..."
    
    local x64_dir="$BASE_288K_DIR/linux_crt_288x/drivers/x64"
    
    # Backup file esistenti
    if [[ -f "/usr/local/lib/crt_288x_ur.so" ]]; then
        log_warning "Backup libreria esistente..."
        sudo cp "/usr/local/lib/crt_288x_ur.so" "/usr/local/lib/crt_288x_ur.so.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Installa file
    sudo cp "$x64_dir/crt_288x_ur.so" /usr/local/lib/
    sudo cp "$x64_dir/crt_288x_ur.h" /usr/local/include/
    
    # Imposta permessi
    sudo chmod 644 /usr/local/lib/crt_288x_ur.so
    sudo chmod 644 /usr/local/include/crt_288x_ur.h
    
    # Aggiorna cache librerie
    sudo ldconfig
    
    log_success "Libreria installata nel sistema"
    
    # Verifica installazione
    if [[ -f "/usr/local/lib/crt_288x_ur.so" ]] && [[ -f "/usr/local/include/crt_288x_ur.h" ]]; then
        log_success "Installazione verificata:"
        ls -la /usr/local/lib/crt_288x_ur.so
        ls -la /usr/local/include/crt_288x_ur.h
    else
        log_error "Installazione fallita"
        return 1
    fi
    
    return 0
}

# Configura permessi utente
configure_user_permissions() {
    log_info "Configurazione permessi utente..."
    
    # Verifica gruppi attuali
    local current_groups
    current_groups=$(groups "$USER")
    log_info "Gruppi attuali: $current_groups"
    
    # Aggiunge ai gruppi necessari se mancanti
    local groups_added=false
    
    if ! echo "$current_groups" | grep -q "plugdev"; then
        sudo usermod -a -G plugdev "$USER"
        groups_added=true
        log_success "Aggiunto al gruppo plugdev"
    fi
    
    if ! echo "$current_groups" | grep -q "dialout"; then
        sudo usermod -a -G dialout "$USER"
        groups_added=true
        log_success "Aggiunto al gruppo dialout"
    fi
    
    if $groups_added; then
        log_warning "IMPORTANTE: Eseguire logout/login per applicare i nuovi gruppi"
        log_info "Oppure eseguire: newgrp plugdev"
    else
        log_success "Permessi utente già configurati"
    fi
    
    return 0
}

# Configura regole udev
configure_udev_rules() {
    log_info "Configurazione regole udev..."
    
    local udev_file="/etc/udev/rules.d/99-crt288x.rules"
    
    if [[ -f "$udev_file" ]]; then
        log_info "Regole udev esistenti trovate, creo backup..."
        sudo cp "$udev_file" "${udev_file}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Crea regole udev
    sudo tee "$udev_file" > /dev/null << 'EOF'
# CRT288x Smart Card Reader - Auto-generated by verifica_288x.sh
# Vendor ID: 23d8, Product ID: 0285

# USB device rules
SUBSYSTEM=="usb", ATTR{idVendor}=="23d8", ATTR{idProduct}=="0285", MODE="0666", GROUP="plugdev", TAG+="uaccess"
SUBSYSTEM=="usb_device", ATTR{idVendor}=="23d8", ATTR{idProduct}=="0285", MODE="0666", GROUP="plugdev"

# TTY device rules (for serial communication)
KERNEL=="ttyUSB*", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", MODE="0666", GROUP="plugdev", TAG+="uaccess"
KERNEL=="ttyACM*", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", MODE="0666", GROUP="plugdev", TAG+="uaccess"

# HID device rules (if applicable)  
KERNEL=="hidraw*", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", MODE="0666", GROUP="plugdev", TAG+="uaccess"

# Power management - disable autosuspend
SUBSYSTEM=="usb", ATTR{idVendor}=="23d8", ATTR{idProduct}=="0285", ATTR{power/autosuspend}="-1"
EOF
    
    # Ricarica regole udev
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    
    log_success "Regole udev configurate e ricaricate"
    
    return 0
}

# Installa dipendenze
install_dependencies() {
    log_info "Installazione dipendenze..."
    
    # Aggiorna repository
    sudo apt update
    
    # Lista dipendenze
    local dependencies=(
        "build-essential"
        "libusb-1.0-0-dev"
        "libudev-dev"
        "pkg-config"
        "python3"
        "python3-pip"
    )
    
    # Installa dipendenze mancanti
    local to_install=()
    for dep in "${dependencies[@]}"; do
        if ! dpkg -l | grep -q "^ii  $dep "; then
            to_install+=("$dep")
        fi
    done
    
    if [[ ${#to_install[@]} -gt 0 ]]; then
        log_info "Installazione dipendenze mancanti: ${to_install[*]}"
        sudo apt install -y "${to_install[@]}"
        log_success "Dipendenze installate"
    else
        log_success "Tutte le dipendenze già presenti"
    fi
    
    return 0
}

# Compila programma di test
compile_test_program() {
    log_info "Compilazione programma di test..."
    
    local sample_dir="$BASE_288K_DIR/288K-linux-sample/288K"
    
    if [[ ! -d "$sample_dir" ]]; then
        log_error "Directory sample non trovata: $sample_dir"
        return 1
    fi
    
    cd "$sample_dir"
    
    # Pulisci compilazioni precedenti
    make clean 2>/dev/null || rm -f *.o crt_288_test 2>/dev/null || true
    
    # Compila
    if make; then
        log_success "Programma test compilato con successo"
        
        # Verifica eseguibile
        if [[ -x "./crt_288_test" ]]; then
            log_success "Eseguibile crt_288_test pronto"
            ls -la ./crt_288_test
        else
            log_error "Eseguibile non trovato dopo compilazione"
            return 1
        fi
    else
        log_error "Compilazione fallita"
        log_info "Provo compilazione manuale..."
        
        # Compilazione manuale fallback
        if gcc -o crt_288_test crt_288_test.c LoadCrt288lib.c -ldl -I/usr/local/include -L/usr/local/lib; then
            log_success "Compilazione manuale riuscita"
        else
            log_error "Anche la compilazione manuale è fallita"
            return 1
        fi
    fi
    
    return 0
}

# Test funzionalità base
test_basic_functionality() {
    log_info "Test funzionalità base..."
    
    # Test caricamento libreria Python
    if python3 -c "
import ctypes
import sys
try:
    lib = ctypes.CDLL('/usr/local/lib/crt_288x_ur.so')
    print('✓ Libreria caricabile da Python')
    sys.exit(0)
except Exception as e:
    print(f'✗ Errore caricamento libreria: {e}')
    sys.exit(1)
" 2>/dev/null; then
        log_success "Libreria compatibile con Python"
    else
        log_warning "Problema caricamento libreria da Python"
    fi
    
    # Test simboli libreria
    if command -v nm &> /dev/null; then
        local symbol_count
        symbol_count=$(nm -D /usr/local/lib/crt_288x_ur.so 2>/dev/null | grep -c "CRT288x_" || echo "0")
        if [[ $symbol_count -gt 0 ]]; then
            log_success "Simboli CRT288x trovati nella libreria: $symbol_count"
        else
            log_warning "Nessun simbolo CRT288x trovato"
        fi
    fi
    
    return 0
}

# Genera report finale
generate_final_report() {
    log_info "Generazione report finale..."
    
    local report_file="/tmp/crt288x_verification_report_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$report_file" << EOF
=================================================================
REPORT VERIFICA CRT288x
=================================================================
Data: $(date)
Script: $0
Directory 288K: $BASE_288K_DIR
Sistema: $(uname -a)
OS: $(lsb_release -d 2>/dev/null || echo "Sconosciuto")

DISPOSITIVO:
$(lsusb | grep "23d8:0285" || echo "Dispositivo non rilevato")

FILE INSTALLATI:
$(ls -la /usr/local/lib/crt_288x_ur.so 2>/dev/null || echo "Libreria non installata")
$(ls -la /usr/local/include/crt_288x_ur.h 2>/dev/null || echo "Header non installato")

REGOLE UDEV:
$(ls -la /etc/udev/rules.d/99-crt288x.rules 2>/dev/null || echo "Regole non configurate")

GRUPPI UTENTE:
$(groups "$USER")

LIBRERIE SISTEMA:
$(ldconfig -p | grep crt || echo "Nessuna libreria CRT nel cache")

DIPENDENZE:
$(pkg-config --modversion libusb-1.0 2>/dev/null || echo "libusb non configurata")

TEST COMPILAZIONE:
$(ls -la "$BASE_288K_DIR/288K-linux-sample/288K/crt_288_test" 2>/dev/null || echo "Test non compilato")

=================================================================
EOF
    
    log_success "Report salvato in: $report_file"
    log_info "Mostra contenuto con: cat $report_file"
    
    return 0
}

# Funzione principale
main() {
    echo -e "${BLUE}"
    echo "================================================================="
    echo "    SCRIPT VERIFICA E INSTALLAZIONE CRT288x v2.0"
    echo "    Compatible con qualsiasi posizione cartella 288K/"
    echo "================================================================="
    echo -e "${NC}"
    
    # Trova cartella 288K
    if ! find_288k_directory; then
        log_error "Impossibile continuare senza cartella 288K"
        exit 1
    fi
    
    # Menu opzioni
    if [[ $# -eq 0 ]]; then
        echo ""
        echo "Opzioni disponibili:"
        echo "  --check       : Solo verifica sistema e dispositivo"
        echo "  --install     : Installazione completa"
        echo "  --test        : Solo test funzionalità"
        echo "  --compile     : Solo compilazione programma test"
        echo "  --report      : Genera report dettagliato"
        echo "  --auto        : Installazione automatica completa"
        echo ""
        read -p "Seleziona opzione (o Enter per --auto): " option
        [[ -z "$option" ]] && option="--auto"
    else
        option="$1"
    fi
    
    case "$option" in
        --check)
            check_system_requirements
            verify_288k_structure
            check_device_connection
            ;;
        --install)
            check_system_requirements || exit 1
            verify_288k_structure || exit 1
            install_dependencies || exit 1
            install_system_library || exit 1
            configure_user_permissions
            configure_udev_rules || exit 1
            log_success "Installazione completata"
            ;;
        --test)
            test_basic_functionality
            check_device_connection
            ;;
        --compile)
            compile_test_program || exit 1
            ;;
        --report)
            generate_final_report
            ;;
        --auto)
            log_info "Installazione automatica completa..."
            check_system_requirements || exit 1
            verify_288k_structure || exit 1
            install_dependencies || exit 1
            install_system_library || exit 1
            configure_user_permissions
            configure_udev_rules || exit 1
            compile_test_program || exit 1
            test_basic_functionality
            check_device_connection
            generate_final_report
            
            echo ""
            log_success "=== INSTALLAZIONE COMPLETATA ==="
            echo ""
            log_info "PROSSIMI PASSI:"
            log_info "1. Logout/login se sono stati aggiunti gruppi utente"
            log_info "2. Collegare dispositivo CRT288x via USB (senza alimentazione esterna)"
            log_info "3. Testare con: cd $BASE_288K_DIR/288K-linux-sample/288K && ./crt_288_test"
            echo ""
            log_info "Per sviluppo:"
            log_info "- Header: /usr/local/include/crt_288x_ur.h"  
            log_info "- Libreria: /usr/local/lib/crt_288x_ur.so"
            log_info "- Link con: -lcrt_288x_ur -L/usr/local/lib -I/usr/local/include"
            ;;
        *)
            log_error "Opzione non riconosciuta: $option"
            exit 1
            ;;
    esac
    
    echo ""
    log_success "Script completato!"
}

# Esegui funzione principale
main "$@"
