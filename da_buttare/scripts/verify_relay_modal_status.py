#!/usr/bin/env python3
# File: /opt/access_control/scripts/verify_relay_modal_status.py
# Script per verificare lo stato attuale del modal USB-RLY08 e identificare cosa manca

import os
import re
import sys
from pathlib import Path

# Colori per output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_section(title):
    """Stampa sezione formattata"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def check_file_exists(filepath):
    """Verifica se un file esiste"""
    if os.path.exists(filepath):
        print(f"{GREEN}✅ File trovato: {filepath}{RESET}")
        return True
    else:
        print(f"{RED}❌ File mancante: {filepath}{RESET}")
        return False

def search_in_file(filepath, patterns, description):
    """Cerca pattern in un file"""
    if not os.path.exists(filepath):
        print(f"{RED}❌ File non trovato per ricerca: {filepath}{RESET}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    found_all = True
    print(f"\n{YELLOW}🔍 Ricerca {description} in {filepath}:{RESET}")
    
    for pattern in patterns:
        if re.search(pattern, content, re.MULTILINE | re.DOTALL):
            print(f"  {GREEN}✅ Trovato: {pattern[:50]}...{RESET}")
        else:
            print(f"  {RED}❌ Mancante: {pattern[:50]}...{RESET}")
            found_all = False
    
    return found_all

def check_modal_html(web_api_path):
    """Verifica presenza modal HTML nel web_api.py"""
    patterns = [
        r'id="relayTestModal"',
        r'Modal Test USB-RLY08',
        r'relay-visual-grid',
        r'start-relay-test',
        r'relay-log'
    ]
    return search_in_file(web_api_path, patterns, "elementi HTML modal USB-RLY08")

def check_javascript_functions(web_api_path):
    """Verifica presenza funzioni JavaScript"""
    patterns = [
        r'function startRelayTest',
        r'function pollRelayStatus',
        r'function activateRelayVisual',
        r'function deactivateRelayVisual',
        r'fetch\(.*/api/hardware/test-relay-sequence'
    ]
    return search_in_file(web_api_path, patterns, "funzioni JavaScript")

def check_backend_routes(web_api_path):
    """Verifica presenza route backend"""
    patterns = [
        r"@app\.route\('/api/hardware/test-relay-sequence'",
        r"@app\.route\('/api/hardware/relay-status'",
        r"def api_test_relay_sequence",
        r"def api_relay_status"
    ]
    return search_in_file(web_api_path, patterns, "route backend API")

def check_hardware_imports(web_api_path):
    """Verifica import moduli hardware"""
    patterns = [
        r"from hardware\.usb_rly08_controller import USBRLY08Controller",
        r"USB_RLY08_AVAILABLE\s*=\s*True",
        r"hardware_test_results",
        r"hardware_test_lock"
    ]
    return search_in_file(web_api_path, patterns, "import e variabili hardware")

def analyze_relay_sequence_implementation(web_api_path):
    """Analizza implementazione test sequenziale"""
    print(f"\n{YELLOW}🔍 Analisi implementazione test sequenziale:{RESET}")
    
    if not os.path.exists(web_api_path):
        print(f"{RED}❌ File non trovato{RESET}")
        return
    
    with open(web_api_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Cerca la funzione api_test_relay_sequence
    match = re.search(r'def api_test_relay_sequence.*?(?=\n@app\.route|\nif __name__|$)', 
                      content, re.DOTALL)
    
    if match:
        func_content = match.group(0)
        lines = func_content.split('\n')[:20]  # Prime 20 righe
        print(f"{GREEN}✅ Funzione api_test_relay_sequence trovata:{RESET}")
        for line in lines:
            print(f"  {line}")
        
        # Verifica elementi chiave
        if 'run_relay_test' in func_content:
            print(f"{GREEN}✅ Thread di test presente{RESET}")
        else:
            print(f"{RED}❌ Thread di test mancante{RESET}")
            
        if 'for i in range(1, 7)' in func_content or 'for relay_num' in func_content:
            print(f"{GREEN}✅ Loop test relè presente{RESET}")
        else:
            print(f"{RED}❌ Loop test relè mancante{RESET}")
    else:
        print(f"{RED}❌ Funzione api_test_relay_sequence non trovata{RESET}")

def main():
    """Funzione principale"""
    print_section("VERIFICA STATO MODAL USB-RLY08")
    
    # Path principali
    project_root = Path('/opt/access_control')
    web_api_path = project_root / 'src/api/web_api.py'
    controller_path = project_root / 'src/hardware/usb_rly08_controller.py'
    
    # 1. Verifica file esistenti
    print_section("1. VERIFICA FILE")
    web_api_exists = check_file_exists(web_api_path)
    controller_exists = check_file_exists(controller_path)
    
    if not web_api_exists:
        print(f"{RED}⚠️ web_api.py non trovato! Il sistema non può funzionare.{RESET}")
        return
    
    # 2. Verifica componenti modal
    print_section("2. COMPONENTI MODAL HTML")
    modal_html_ok = check_modal_html(web_api_path)
    
    # 3. Verifica JavaScript
    print_section("3. FUNZIONI JAVASCRIPT")
    js_ok = check_javascript_functions(web_api_path)
    
    # 4. Verifica backend
    print_section("4. ROUTE BACKEND API")
    backend_ok = check_backend_routes(web_api_path)
    
    # 5. Verifica import hardware
    print_section("5. IMPORT HARDWARE")
    imports_ok = check_hardware_imports(web_api_path)
    
    # 6. Analisi dettagliata implementazione
    print_section("6. ANALISI IMPLEMENTAZIONE")
    analyze_relay_sequence_implementation(web_api_path)
    
    # 7. Riepilogo
    print_section("RIEPILOGO VERIFICA")
    
    total_checks = 5
    passed_checks = sum([modal_html_ok, js_ok, backend_ok, imports_ok, controller_exists])
    
    print(f"\nControlli superati: {passed_checks}/{total_checks}")
    
    if passed_checks == total_checks:
        print(f"{GREEN}✅ TUTTI I COMPONENTI PRESENTI!{RESET}")
        print(f"{YELLOW}⚠️ Verificare però che il backend comunichi realmente con l'hardware{RESET}")
    else:
        print(f"{RED}❌ COMPONENTI MANCANTI!{RESET}")
        print(f"\n{YELLOW}📋 AZIONI NECESSARIE:{RESET}")
        
        if not modal_html_ok:
            print(f"  1. Aggiungere HTML modal USB-RLY08")
        if not js_ok:
            print(f"  2. Aggiungere funzioni JavaScript per test")
        if not backend_ok:
            print(f"  3. Implementare route API backend complete")
        if not imports_ok:
            print(f"  4. Aggiungere import moduli hardware")
        if not controller_exists:
            print(f"  5. Verificare presenza usb_rly08_controller.py")
    
    # 8. Test connessione hardware
    print_section("8. TEST CONNESSIONE HARDWARE")
    print(f"{YELLOW}Per testare la connessione hardware reale:{RESET}")
    print(f"  cd /opt/access_control")
    print(f"  python3 scripts/test_usb_rly08.py")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}VERIFICA COMPLETATA{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

if __name__ == "__main__":
    main()
