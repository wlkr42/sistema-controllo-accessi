#!/usr/bin/env python3
# File: /opt/access_control/scripts/complete_relay_integration.py
# Script per completare l'integrazione del modal USB-RLY08 con il backend reale

import os
import re
import sys
import shutil
from datetime import datetime
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

def backup_file(filepath):
    """Crea backup del file"""
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    print(f"{GREEN}✅ Backup creato: {backup_path}{RESET}")
    return backup_path

def find_line_number(lines, pattern):
    """Trova numero di linea con pattern"""
    for i, line in enumerate(lines):
        if re.search(pattern, line):
            return i
    return -1

def insert_after_pattern(lines, pattern, new_content, description):
    """Inserisce contenuto dopo un pattern"""
    line_num = find_line_number(lines, pattern)
    if line_num >= 0:
        lines.insert(line_num + 1, new_content)
        print(f"{GREEN}✅ {description} inserito dopo linea {line_num}{RESET}")
        return True
    else:
        print(f"{RED}❌ Pattern non trovato per {description}: {pattern}{RESET}")
        return False

def fix_relay_visual_grid(content):
    """Aggiunge relay-visual-grid mancante nel modal HTML"""
    print(f"\n{YELLOW}🔧 Fix 1: Aggiunta relay-visual-grid{RESET}")
    
    # Cerca il div del modal body
    pattern = r'(<div class="modal-body">.*?)(</div>)'
    
    relay_grid_html = '''
                    <div id="relay-visual-grid" class="relay-grid mb-3">
                        <div class="row g-2">
                            <div class="col-3">
                                <div class="relay-box" id="relay-1">
                                    <i class="fas fa-door-open"></i>
                                    <small>Cancello</small>
                                </div>
                            </div>
                            <div class="col-3">
                                <div class="relay-box" id="relay-2">
                                    <i class="fas fa-lightbulb text-danger"></i>
                                    <small>LED Rosso</small>
                                </div>
                            </div>
                            <div class="col-3">
                                <div class="relay-box" id="relay-3">
                                    <i class="fas fa-lightbulb text-success"></i>
                                    <small>LED Verde</small>
                                </div>
                            </div>
                            <div class="col-3">
                                <div class="relay-box" id="relay-4">
                                    <i class="fas fa-lightbulb text-warning"></i>
                                    <small>LED Giallo</small>
                                </div>
                            </div>
                        </div>
                        <div class="row g-2 mt-2">
                            <div class="col-3">
                                <div class="relay-box" id="relay-5">
                                    <i class="fas fa-bell"></i>
                                    <small>Buzzer</small>
                                </div>
                            </div>
                            <div class="col-3">
                                <div class="relay-box" id="relay-6">
                                    <i class="fas fa-plug"></i>
                                    <small>Aux 1</small>
                                </div>
                            </div>
                            <div class="col-3">
                                <div class="relay-box" id="relay-7">
                                    <i class="fas fa-plug"></i>
                                    <small>Aux 2</small>
                                </div>
                            </div>
                            <div class="col-3">
                                <div class="relay-box" id="relay-8">
                                    <i class="fas fa-plug"></i>
                                    <small>Aux 3</small>
                                </div>
                            </div>
                        </div>
                    </div>
'''
    
    # Cerca il punto giusto per inserire la griglia
    relay_modal_match = re.search(r'id="relayTestModal".*?<div class="modal-body">', content, re.DOTALL)
    if relay_modal_match:
        insertion_point = relay_modal_match.end()
        # Verifica se relay-visual-grid già esiste
        if 'relay-visual-grid' not in content[insertion_point:insertion_point+2000]:
            content = content[:insertion_point] + relay_grid_html + content[insertion_point:]
            print(f"{GREEN}✅ relay-visual-grid aggiunto al modal{RESET}")
        else:
            print(f"{YELLOW}⚠️ relay-visual-grid già presente{RESET}")
    else:
        print(f"{RED}❌ Modal relay non trovato per inserimento grid{RESET}")
    
    return content

def fix_hardware_imports(lines):
    """Corregge gli import hardware e aggiunge variabile mancante"""
    print(f"\n{YELLOW}🔧 Fix 2: Correzione import hardware{RESET}")
    
    # Cerca la sezione degli import hardware
    hardware_import_idx = -1
    for i, line in enumerate(lines):
        if 'HARDWARE_RELAY_OK' in line:
            hardware_import_idx = i
            break
    
    if hardware_import_idx >= 0:
        # Aggiungi USB_RLY08_AVAILABLE dopo HARDWARE_RELAY_OK
        if not any('USB_RLY08_AVAILABLE' in line for line in lines):
            lines.insert(hardware_import_idx + 1, "USB_RLY08_AVAILABLE = HARDWARE_RELAY_OK  # Alias per compatibilità\n")
            print(f"{GREEN}✅ Aggiunta variabile USB_RLY08_AVAILABLE{RESET}")
    else:
        print(f"{RED}❌ HARDWARE_RELAY_OK non trovato{RESET}")
    
    return lines

def fix_relay_test_sequence(content):
    """Completa l'implementazione del test sequenziale"""
    print(f"\n{YELLOW}🔧 Fix 3: Completamento test sequenziale relè{RESET}")
    
    # Trova la funzione run_relay_test incompleta
    pattern = r'(def run_relay_test\(\):.*?# Sequenza test)(.*?)(except|finally|\n\s{0,8}\w)'
    
    complete_sequence = '''
              # Sequenza test
              with hardware_test_lock:
                  hardware_test_results['relay_sequence'] = {
                      'status': 'running',
                      'current_relay': 0,
                      'message': 'Test in corso...'
                  }
              
              # Test ogni relè
              relay_names = {
                  1: "Cancello",
                  2: "LED Rosso", 
                  3: "LED Verde",
                  4: "LED Giallo",
                  5: "Buzzer",
                  6: "Aux 1",
                  7: "Aux 2",
                  8: "Aux 3"
              }
              
              for relay_num in range(1, 9):
                  relay_name = relay_names.get(relay_num, f"Relè {relay_num}")
                  
                  # Aggiorna stato
                  with hardware_test_lock:
                      hardware_test_results['relay_sequence'] = {
                          'status': 'running',
                          'current_relay': relay_num,
                          'relay_name': relay_name,
                          'action': 'on',
                          'message': f'Test {relay_name}...'
                      }
                  
                  # Attiva relè
                  controller.activate_relay(relay_num)
                  time.sleep(0.5)  # Mezzo secondo ON
                  
                  # Aggiorna stato OFF
                  with hardware_test_lock:
                      hardware_test_results['relay_sequence']['action'] = 'off'
                  
                  # Disattiva relè
                  controller.deactivate_relay(relay_num)
                  time.sleep(0.3)  # Pausa tra relè
              
              # Test completato
              controller.disconnect()
              
              with hardware_test_lock:
                  hardware_test_results['relay_sequence'] = {
                      'status': 'completed',
                      'message': 'Test completato con successo!'
                  }
              
          '''
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        # Sostituisci con la sequenza completa
        new_content = match.group(1) + complete_sequence + match.group(3)
        content = content[:match.start()] + new_content + content[match.end():]
        print(f"{GREEN}✅ Test sequenziale completato{RESET}")
    else:
        print(f"{RED}❌ Pattern test sequenziale non trovato{RESET}")
    
    return content

def add_relay_status_route(content):
    """Verifica e corregge la route relay-status"""
    print(f"\n{YELLOW}🔧 Fix 4: Verifica route relay-status{RESET}")
    
    # Verifica se la route esiste già
    if '@app.route(\'/api/hardware/relay-status\')' in content:
        print(f"{GREEN}✅ Route relay-status già presente{RESET}")
    else:
        # Aggiungi la route dopo test-relay-sequence
        pattern = r'(@app\.route\(\'/api/hardware/test-relay-sequence\'.*?return jsonify.*?\))'
        
        relay_status_route = '''

@app.route('/api/hardware/relay-status')
@require_auth()
def api_relay_status():
    """Restituisce lo stato corrente del test relè"""
    with hardware_test_lock:
        if 'relay_sequence' in hardware_test_results:
            return jsonify({
                'success': True,
                'status': hardware_test_results['relay_sequence']
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Nessun test in corso'
            })
'''
        
        match = re.search(pattern, content, re.DOTALL)
        if match:
            insertion_point = match.end()
            content = content[:insertion_point] + relay_status_route + content[insertion_point:]
            print(f"{GREEN}✅ Route relay-status aggiunta{RESET}")
        else:
            print(f"{RED}❌ Punto inserimento route non trovato{RESET}")
    
    return content

def add_css_styles(content):
    """Aggiunge stili CSS per la griglia relè"""
    print(f"\n{YELLOW}🔧 Fix 5: Aggiunta stili CSS{RESET}")
    
    css_styles = '''
    .relay-grid {
        padding: 20px;
        background: #f8f9fa;
        border-radius: 8px;
    }
    .relay-box {
        text-align: center;
        padding: 15px;
        background: white;
        border: 2px solid #dee2e6;
        border-radius: 8px;
        transition: all 0.3s;
        cursor: default;
    }
    .relay-box i {
        font-size: 2em;
        margin-bottom: 5px;
        display: block;
    }
    .relay-box small {
        display: block;
        margin-top: 5px;
        font-size: 0.8em;
    }
    .relay-box.active {
        background: #28a745;
        color: white;
        border-color: #28a745;
        box-shadow: 0 0 15px rgba(40, 167, 69, 0.5);
        transform: scale(1.05);
    }
    .relay-box.active i {
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
'''
    
    # Cerca tag </style>
    style_end = content.rfind('</style>')
    if style_end > 0:
        content = content[:style_end] + css_styles + content[style_end:]
        print(f"{GREEN}✅ Stili CSS aggiunti{RESET}")
    else:
        print(f"{RED}❌ Tag </style> non trovato{RESET}")
    
    return content

def main():
    """Funzione principale"""
    print_section("COMPLETAMENTO INTEGRAZIONE MODAL USB-RLY08")
    
    # Path del file
    web_api_path = Path('/opt/access_control/src/api/web_api.py')
    
    if not web_api_path.exists():
        print(f"{RED}❌ File web_api.py non trovato!{RESET}")
        return False
    
    # Crea backup
    print_section("1. BACKUP FILE")
    backup_path = backup_file(web_api_path)
    
    # Leggi il file
    with open(web_api_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.splitlines(True)
    
    # Applica fix
    print_section("2. APPLICAZIONE FIX")
    
    # Fix 1: Aggiungi relay-visual-grid
    content = fix_relay_visual_grid(content)
    
    # Fix 2: Correggi import (lavora su lines)
    lines = content.splitlines(True)
    lines = fix_hardware_imports(lines)
    content = ''.join(lines)
    
    # Fix 3: Completa test sequenziale
    content = fix_relay_test_sequence(content)
    
    # Fix 4: Aggiungi/verifica route relay-status
    content = add_relay_status_route(content)
    
    # Fix 5: Aggiungi stili CSS
    content = add_css_styles(content)
    
    # Scrivi il file modificato
    print_section("3. SALVATAGGIO MODIFICHE")
    try:
        with open(web_api_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"{GREEN}✅ File web_api.py aggiornato con successo{RESET}")
    except Exception as e:
        print(f"{RED}❌ Errore salvataggio: {e}{RESET}")
        print(f"{YELLOW}Ripristino backup...{RESET}")
        shutil.copy2(backup_path, web_api_path)
        return False
    
    # Test finale
    print_section("4. VERIFICA FINALE")
    print(f"{YELLOW}Per verificare le modifiche:{RESET}")
    print(f"  1. Riavvia la dashboard:")
    print(f"     cd /opt/access_control")
    print(f"     pkill -f web_api.py")
    print(f"     python3 src/api/web_api.py")
    print(f"")
    print(f"  2. Accedi a: http://192.168.178.200:5000")
    print(f"  3. Vai nella sezione dispositivi")
    print(f"  4. Clicca 'Test USB-RLY08'")
    print(f"  5. Nel modal clicca 'Avvia Test Sequenziale'")
    print(f"")
    print(f"{GREEN}✅ I relè dovrebbero accendersi in sequenza con animazioni sincronizzate!{RESET}")
    
    print_section("COMPLETAMENTO RIUSCITO")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
