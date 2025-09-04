# File: /opt/access_control/scripts/cli_card_tools.sh
# STRUMENTI CLI PER TEST TESSERA SANITARIA

#!/bin/bash

echo "🏥 STRUMENTI CLI - TEST TESSERA SANITARIA"
echo "========================================="

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzione per stampa colorata
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Controlla se PCSCD è attivo
check_pcscd() {
    print_info "Controllo servizio PCSCD..."
    
    if systemctl is-active --quiet pcscd; then
        print_success "PCSCD è attivo"
        return 0
    else
        print_error "PCSCD non è attivo"
        print_info "Tentativo di avvio PCSCD..."
        sudo systemctl start pcscd
        sleep 2
        
        if systemctl is-active --quiet pcscd; then
            print_success "PCSCD avviato con successo"
            return 0
        else
            print_error "Impossibile avviare PCSCD"
            return 1
        fi
    fi
}

# Test con pcsc_scan
test_pcsc_scan() {
    print_info "Test con pcsc_scan..."
    
    if ! command -v pcsc_scan &> /dev/null; then
        print_error "pcsc_scan non installato"
        print_info "Installazione pcsc_scan..."
        sudo apt update && sudo apt install -y pcsc-tools
    fi
    
    print_info "Inserire tessera sanitaria e premere INVIO"
    read -p "Premere INVIO quando la tessera è inserita..."
    
    echo ""
    print_info "Esecuzione pcsc_scan per 10 secondi..."
    timeout 10 pcsc_scan 2>&1 | tee /tmp/pcsc_scan_output.txt
    
    # Analizza output
    if grep -q "ATR:" /tmp/pcsc_scan_output.txt; then
        ATR=$(grep "ATR:" /tmp/pcsc_scan_output.txt | head -1 | cut -d':' -f2 | tr -d ' ')
        print_success "ATR rilevato: $ATR"
        
        # Verifica se è tessera sanitaria
        case "$ATR" in
            *3B8B80010031C16408923354009000F3*)
                print_success "TESSERA SANITARIA ITALIANA RICONOSCIUTA!"
                ;;
            *3B8B80010031C164*)
                print_success "Probabile tessera sanitaria italiana (variante)"
                ;;
            *)
                print_warning "ATR non riconosciuto come tessera sanitaria standard"
                ;;
        esac
    else
        print_error "Nessun ATR rilevato"
    fi
}

# Test con opensc-tool
test_opensc_tool() {
    print_info "Test con opensc-tool..."
    
    if ! command -v opensc-tool &> /dev/null; then
        print_error "opensc-tool non installato"
        print_info "Installazione OpenSC..."
        sudo apt update && sudo apt install -y opensc
    fi
    
    print_info "Test connessione lettore..."
    opensc-tool -l 2>&1 | tee /tmp/opensc_output.txt
    
    if grep -q "Detected readers" /tmp/opensc_output.txt; then
        print_success "Lettori rilevati"
        
        print_info "Test lettura ATR..."
        opensc-tool -a 2>&1 | tee -a /tmp/opensc_output.txt
        
        print_info "Test info tessera..."
        opensc-tool -i 2>&1 | tee -a /tmp/opensc_output.txt
        
        print_info "Test dump dati pubblici..."
        opensc-tool -s 00:A4:04:00:06:A0:00:00:00:30:89 2>&1 | tee -a /tmp/opensc_output.txt
        
    else
        print_error "Nessun lettore rilevato da OpenSC"
    fi
}

# Test con pkcs15-tool
test_pkcs15_tool() {
    print_info "Test con pkcs15-tool..."
    
    if ! command -v pkcs15-tool &> /dev/null; then
        print_error "pkcs15-tool non disponibile (parte di OpenSC)"
        return 1
    fi
    
    print_info "Test lettura certificati..."
    pkcs15-tool -C 2>&1 | tee /tmp/pkcs15_output.txt
    
    print_info "Test info tessera..."
    pkcs15-tool -I 2>&1 | tee -a /tmp/pkcs15_output.txt
    
    print_info "Test dump oggetti..."
    pkcs15-tool -D 2>&1 | tee -a /tmp/pkcs15_output.txt
}

# Test con gp (GlobalPlatform)
test_gp_tool() {
    print_info "Test con GlobalPlatform tool..."
    
    if ! command -v gp &> /dev/null; then
        print_warning "gp tool non installato (opzionale)"
        return 1
    fi
    
    print_info "Test info tessera GlobalPlatform..."
    gp -i 2>&1 | tee /tmp/gp_output.txt
    
    print_info "Test lista applicazioni..."
    gp -l 2>&1 | tee -a /tmp/gp_output.txt
}

# Test APDU personalizzati con opensc-tool
test_custom_apdu() {
    print_info "Test comandi APDU personalizzati..."
    
    if ! command -v opensc-tool &> /dev/null; then
        print_error "opensc-tool necessario per test APDU"
        return 1
    fi
    
    # Array di comandi APDU da testare
    declare -a apdu_commands=(
        "00:A4:00:00:02:3F:00"           # SELECT MF
        "00:A4:00:00:02:11:00"           # SELECT DF1
        "00:A4:00:00:02:11:02"           # SELECT EF_Dati_personali
        "00:B0:00:00:9F"                 # READ BINARY
        "00:CA:00:81:00"                 # GET DATA
        "00:CA:01:00:00"                 # GET DATA alternative
        "00:B2:01:04:20"                 # READ RECORD 1
        "00:A4:04:00:06:A0:00:00:00:30:89"  # SELECT AID tessera sanitaria
    )
    
    declare -a apdu_descriptions=(
        "SELECT Master File"
        "SELECT Directory DF1"
        "SELECT EF Dati Personali"
        "READ BINARY"
        "GET DATA - Dati Carta"
        "GET DATA - Alternative"
        "READ RECORD 1"
        "SELECT AID Tessera Sanitaria"
    )
    
    echo ""
    print_info "Esecuzione comandi APDU personalizzati..."
    
    for i in "${!apdu_commands[@]}"; do
        cmd="${apdu_commands[$i]}"
        desc="${apdu_descriptions[$i]}"
        
        echo ""
        print_info "Test $((i+1)): $desc"
        print_info "Comando: $cmd"
        
        # Esegui comando APDU
        result=$(opensc-tool -s "$cmd" 2>&1)
        echo "$result" | tee -a /tmp/apdu_test_output.txt
        
        # Analizza risultato
        if echo "$result" | grep -q "90 00"; then
            print_success "Comando riuscito (90 00)"
            
            # Cerca pattern codice fiscale nella risposta
            if echo "$result" | grep -E "[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]"; then
                cf=$(echo "$result" | grep -oE "[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]")
                print_success "🎯 CODICE FISCALE TROVATO: $cf"
                echo "SUCCESSO: $desc -> $cf" >> /tmp/cf_found.txt
            fi
        else
            # Controlla altri codici di stato
            if echo "$result" | grep -q "6F 00"; then
                print_warning "File non selezionato (6F 00)"
            elif echo "$result" | grep -q "6A 82"; then
                print_warning "File non trovato (6A 82)"
            elif echo "$result" | grep -q "69 82"; then
                print_warning "Sicurezza: PIN richiesto (69 82)"
            else
                print_error "Comando fallito"
            fi
        fi
        
        sleep 0.5  # Pausa tra comandi
    done
}

# Test con cardpeek (se disponibile)
test_cardpeek() {
    print_info "Test con Cardpeek..."
    
    if ! command -v cardpeek &> /dev/null; then
        print_warning "Cardpeek non installato"
        print_info "Per installare: sudo apt install cardpeek"
        return 1
    fi
    
    print_info "Avvio Cardpeek per analisi tessera..."
    print_warning "Chiudere Cardpeek quando l'analisi è completa"
    
    # Avvia cardpeek in background
    cardpeek > /tmp/cardpeek_output.txt 2>&1 &
    CARDPEEK_PID=$!
    
    # Attendi che l'utente chiuda cardpeek
    wait $CARDPEEK_PID
    
    print_info "Cardpeek chiuso, controllo output..."
    if [ -f /tmp/cardpeek_output.txt ]; then
        cat /tmp/cardpeek_output.txt
    fi
}

# Analisi finale dei risultati
analyze_results() {
    print_info "Analisi risultati finali..."
    
    echo ""
    print_info "=== RIEPILOGO TEST ==="
    
    # Controlla se è stato trovato un codice fiscale
    if [ -f /tmp/cf_found.txt ]; then
        print_success "CODICE FISCALE TROVATO!"
        cat /tmp/cf_found.txt
        
        echo ""
        print_success "🎯 ALMENO UN METODO HA FUNZIONATO!"
        print_info "Implementare il metodo riuscito nell'applicazione principale"
    else
        print_warning "Nessun codice fiscale estratto dai test CLI"
        
        echo ""
        print_info "File di output generati:"
        ls -la /tmp/*output.txt /tmp/cf_found.txt 2>/dev/null || print_info "Nessun file di output"
        
        echo ""
        print_info "Prossimi step raccomandati:"
        print_info "1. Verificare che la tessera sia inserita correttamente"
        print_info "2. Testare con script Python avanzato"
        print_info "3. Considerare lettore banda magnetica"
    fi
    
    echo ""
    print_info "Log salvati in /tmp/*output.txt"
}

# Menu principale
show_menu() {
    echo ""
    print_info "=== MENU TEST TESSERA SANITARIA ==="
    echo "1. Test completo automatico"
    echo "2. Test PCSCD"
    echo "3. Test pcsc_scan"
    echo "4. Test OpenSC"
    echo "5. Test PKCS#15"
    echo "6. Test APDU personalizzati"
    echo "7. Test Cardpeek"
    echo "8. Analisi risultati"
    echo "9. Pulizia file temporanei"
    echo "0. Esci"
    echo ""
}

# Pulizia file temporanei
cleanup_temp() {
    print_info "Pulizia file temporanei..."
    rm -f /tmp/*output.txt /tmp/cf_found.txt
    print_success "File temporanei puliti"
}

# Test completo automatico
run_full_test() {
    print_info "ESECUZIONE TEST COMPLETO AUTOMATICO"
    print_info "===================================="
    
    # Pulizia iniziale
    cleanup_temp
    
    # Sequenza di test
    check_pcscd || return 1
    
    echo ""
    test_pcsc_scan
    
    echo ""
    test_opensc_tool
    
    echo ""
    test_pkcs15_tool
    
    echo ""
    test_custom_apdu
    
    echo ""
    analyze_results
}

# Main
main() {
    echo ""
    print_info "Inserire tessera sanitaria nel lettore prima di iniziare"
    
    if [ "$1" = "auto" ]; then
        run_full_test
        exit 0
    fi
    
    while true; do
        show_menu
        read -p "Scegli opzione (0-9): " choice
        
        case $choice in
            1) run_full_test ;;
            2) check_pcscd ;;
            3) test_pcsc_scan ;;
            4) test_opensc_tool ;;
            5) test_pkcs15_tool ;;
            6) test_custom_apdu ;;
            7) test_cardpeek ;;
            8) analyze_results ;;
            9) cleanup_temp ;;
            0) print_info "Uscita..."; exit 0 ;;
            *) print_error "Opzione non valida" ;;
        esac
        
        echo ""
        read -p "Premere INVIO per continuare..."
    done
}

# Avvio
main "$@"