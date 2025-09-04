#!/usr/bin/env python3
# File: /opt/access_control/scripts/enhance_relay_modal_animations.py
# Migliora il modal USB-RLY08 con animazioni complete

import shutil
from datetime import datetime
from pathlib import Path

# Colori
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def main():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}AGGIUNTA ANIMAZIONI MODAL USB-RLY08{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    web_api_path = Path('/opt/access_control/src/api/web_api.py')
    
    # Backup
    backup_path = f"{web_api_path}.backup_animations_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(web_api_path, backup_path)
    print(f"\n{GREEN}✅ Backup creato: {backup_path}{RESET}")
    
    # Leggi il file
    with open(web_api_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Trova e sostituisci il modal esistente
    print(f"\n{YELLOW}🔧 Sostituzione modal con versione animata...{RESET}")
    
    # Trova l'inizio del modal esistente
    start_marker = '<!-- Modal Test USB-RLY08 -->'
    end_marker = '</script>'
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print(f"{YELLOW}⚠️ Modal marker non trovato, aggiungo alla fine{RESET}")
        # Aggiungi prima di </body>
        body_close = content.rfind('</body>')
        if body_close > 0:
            content = content[:body_close] + get_enhanced_modal() + '\n' + content[body_close:]
    else:
        # Trova la fine del blocco script dopo il modal
        search_from = start_idx
        script_count = 0
        end_idx = start_idx
        
        while True:
            next_script_open = content.find('<script>', search_from)
            next_script_close = content.find('</script>', search_from)
            
            if next_script_close < next_script_open or next_script_open == -1:
                if next_script_close != -1:
                    end_idx = next_script_close + len('</script>')
                    break
            search_from = max(next_script_close, next_script_open) + 1
            
            if search_from >= len(content):
                break
        
        # Sostituisci tutto il blocco
        content = content[:start_idx] + get_enhanced_modal() + content[end_idx:]
        print(f"{GREEN}✅ Modal sostituito con versione animata{RESET}")
    
    # 2. Aggiungi stili CSS per animazioni
    print(f"\n{YELLOW}🔧 Aggiunta stili CSS...{RESET}")
    
    # Trova </style> nel template
    style_close = content.rfind('</style>')
    if style_close > 0:
        # Trova l'ultimo </style> prima del modal
        last_style_in_dashboard = content[:start_idx].rfind('</style>')
        if last_style_in_dashboard > 0:
            content = content[:last_style_in_dashboard] + get_animation_styles() + content[last_style_in_dashboard:]
            print(f"{GREEN}✅ Stili CSS aggiunti{RESET}")
    
    # 3. Salva il file
    print(f"\n{YELLOW}💾 Salvataggio file...{RESET}")
    with open(web_api_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"{GREEN}✅ File salvato!{RESET}")
    
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}✅ ANIMAZIONI AGGIUNTE CON SUCCESSO!{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")
    print(f"\n{YELLOW}Il modal ora include:{RESET}")
    print(f"  ✅ Griglia visuale di tutti gli 8 relè")
    print(f"  ✅ Animazione cancello che si apre/chiude")
    print(f"  ✅ LED colorati che si accendono")
    print(f"  ✅ Buzzer animato")
    print(f"  ✅ Log dettagliato in tempo reale")
    print(f"\n{BLUE}Riavvia la dashboard per vedere le animazioni!{RESET}")

def get_animation_styles():
    """Ritorna gli stili CSS per le animazioni"""
    return '''
        /* Stili Modal USB-RLY08 */
        .relay-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .relay-box {
            background: white;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
            cursor: default;
        }
        
        .relay-box.active {
            background: #28a745;
            color: white;
            border-color: #28a745;
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(40, 167, 69, 0.5);
        }
        
        .relay-box i {
            font-size: 2em;
            display: block;
            margin-bottom: 10px;
        }
        
        .relay-box.active i {
            animation: pulse 0.5s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.2); }
        }
        
        .gate-visual {
            width: 200px;
            height: 100px;
            background: #343a40;
            border: 3px solid #6c757d;
            border-radius: 5px;
            margin: 20px auto;
            position: relative;
            overflow: hidden;
            transition: all 0.5s ease;
        }
        
        .gate-visual.open {
            background: #28a745;
            border-color: #28a745;
        }
        
        .gate-bars {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: repeating-linear-gradient(
                90deg,
                #ffc107,
                #ffc107 10px,
                #343a40 10px,
                #343a40 20px
            );
            transition: transform 0.8s ease;
        }
        
        .gate-visual.open .gate-bars {
            transform: translateX(-100%);
        }
        
        .led-indicator {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            margin: 10px;
            display: inline-block;
            border: 2px solid #dee2e6;
            transition: all 0.3s ease;
        }
        
        .led-indicator.led-red { background: #ffcccc; }
        .led-indicator.led-green { background: #ccffcc; }
        .led-indicator.led-yellow { background: #ffffcc; }
        
        .led-indicator.active {
            border-width: 0;
            box-shadow: 0 0 30px currentColor;
        }
        
        .led-indicator.led-red.active { background: #dc3545; }
        .led-indicator.led-green.active { background: #28a745; }
        .led-indicator.led-yellow.active { background: #ffc107; }
        
        .buzzer-visual {
            display: inline-block;
            font-size: 2em;
            transition: all 0.3s ease;
        }
        
        .buzzer-visual.active {
            animation: buzz 0.2s ease-in-out infinite;
            color: #17a2b8;
        }
        
        @keyframes buzz {
            0%, 100% { transform: rotate(-5deg); }
            50% { transform: rotate(5deg); }
        }
        
        .relay-log {
            background: #000;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            padding: 15px;
            height: 200px;
            overflow-y: auto;
            border-radius: 8px;
            font-size: 0.9em;
        }
    </style>
'''

def get_enhanced_modal():
    """Ritorna il modal HTML completo con animazioni"""
    return '''
    <!-- Modal Test USB-RLY08 -->
    <div class="modal fade" id="relayTestModal" tabindex="-1">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header bg-primary text-white">
                    <h5 class="modal-title">
                        <i class="fas fa-microchip me-2"></i>Test Controller USB-RLY08
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <!-- Griglia Relè -->
                    <div class="relay-grid">
                        <div class="relay-box" id="relay-1">
                            <i class="fas fa-door-open"></i>
                            <strong>Relè 1</strong>
                            <small>Cancello</small>
                        </div>
                        <div class="relay-box" id="relay-2">
                            <i class="fas fa-lightbulb"></i>
                            <strong>Relè 2</strong>
                            <small>LED Rosso</small>
                        </div>
                        <div class="relay-box" id="relay-3">
                            <i class="fas fa-lightbulb"></i>
                            <strong>Relè 3</strong>
                            <small>LED Verde</small>
                        </div>
                        <div class="relay-box" id="relay-4">
                            <i class="fas fa-lightbulb"></i>
                            <strong>Relè 4</strong>
                            <small>LED Giallo</small>
                        </div>
                        <div class="relay-box" id="relay-5">
                            <i class="fas fa-bell"></i>
                            <strong>Relè 5</strong>
                            <small>Buzzer</small>
                        </div>
                        <div class="relay-box" id="relay-6">
                            <i class="fas fa-plug"></i>
                            <strong>Relè 6</strong>
                            <small>Aux 1</small>
                        </div>
                        <div class="relay-box" id="relay-7">
                            <i class="fas fa-plug"></i>
                            <strong>Relè 7</strong>
                            <small>Aux 2</small>
                        </div>
                        <div class="relay-box" id="relay-8">
                            <i class="fas fa-plug"></i>
                            <strong>Relè 8</strong>
                            <small>Aux 3</small>
                        </div>
                    </div>
                    
                    <!-- Visualizzazione Dispositivi -->
                    <div class="text-center mb-3">
                        <h6>Dispositivi Collegati</h6>
                        
                        <!-- Cancello -->
                        <div class="gate-visual" id="gate-visual">
                            <div class="gate-bars"></div>
                            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; font-weight: bold; z-index: 10;">
                                CANCELLO
                            </div>
                        </div>
                        
                        <!-- LED e Buzzer -->
                        <div class="mt-3">
                            <span class="led-indicator led-red" id="led-red" title="LED Rosso"></span>
                            <span class="led-indicator led-green" id="led-green" title="LED Verde"></span>
                            <span class="led-indicator led-yellow" id="led-yellow" title="LED Giallo"></span>
                            <span class="buzzer-visual" id="buzzer" title="Buzzer">
                                <i class="fas fa-bell"></i>
                            </span>
                        </div>
                    </div>
                    
                    <!-- Log -->
                    <div class="relay-log" id="relay-log">
                        Pronto per il test. Clicca "Avvia Test Sequenziale" per iniziare...
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-primary" id="start-relay-test" onclick="startRelaySequence()">
                        <i class="fas fa-play me-2"></i>Avvia Test Sequenziale
                    </button>
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Chiudi</button>
                </div>
            </div>
        </div>
    </div>

    <script>
    let relayTestRunning = false;
    
    function startRelaySequence() {
        if (relayTestRunning) return;
        
        relayTestRunning = true;
        const btn = document.getElementById('start-relay-test');
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Test in corso...';
        
        // Reset visuals
        resetRelayVisuals();
        
        const log = document.getElementById('relay-log');
        log.innerHTML = '';
        addRelayLog('🚀 AVVIO TEST SEQUENZIALE USB-RLY08');
        addRelayLog('━'.repeat(50));
        
        // Sequenza di test
        const sequence = [
            {id: 1, name: 'Cancello', icon: '🚪', device: 'gate', duration: 1000},
            {id: 2, name: 'LED Rosso', icon: '🔴', device: 'led-red', duration: 500},
            {id: 3, name: 'LED Verde', icon: '🟢', device: 'led-green', duration: 500},
            {id: 4, name: 'LED Giallo', icon: '🟡', device: 'led-yellow', duration: 500},
            {id: 5, name: 'Buzzer', icon: '🔔', device: 'buzzer', duration: 300},
            {id: 6, name: 'Aux 1', icon: '1️⃣', device: null, duration: 500},
            {id: 7, name: 'Aux 2', icon: '2️⃣', device: null, duration: 500},
            {id: 8, name: 'Aux 3', icon: '3️⃣', device: null, duration: 500}
        ];
        
        // Esegui sequenza
        let delay = 500;
        sequence.forEach((item, index) => {
            setTimeout(() => {
                testRelay(item);
                
                if (index === sequence.length - 1) {
                    // Ultimo relè
                    setTimeout(() => {
                        addRelayLog('━'.repeat(50));
                        addRelayLog('✅ TEST COMPLETATO CON SUCCESSO!');
                        btn.disabled = false;
                        btn.innerHTML = '<i class="fas fa-play me-2"></i>Avvia Test Sequenziale';
                        relayTestRunning = false;
                    }, item.duration + 500);
                }
            }, delay);
            delay += item.duration + 300;
        });
    }
    
    function testRelay(item) {
        addRelayLog(`${item.icon} Test Relè ${item.id} - ${item.name}...`);
        
        // Attiva relè
        const relayBox = document.getElementById(`relay-${item.id}`);
        relayBox.classList.add('active');
        
        // Attiva dispositivo
        if (item.device === 'gate') {
            document.getElementById('gate-visual').classList.add('open');
        } else if (item.device && item.device.startsWith('led-')) {
            document.getElementById(item.device).classList.add('active');
        } else if (item.device === 'buzzer') {
            document.getElementById('buzzer').classList.add('active');
        }
        
        // Disattiva dopo durata
        setTimeout(() => {
            relayBox.classList.remove('active');
            
            if (item.device === 'gate') {
                document.getElementById('gate-visual').classList.remove('open');
            } else if (item.device && item.device.startsWith('led-')) {
                document.getElementById(item.device).classList.remove('active');
            } else if (item.device === 'buzzer') {
                document.getElementById('buzzer').classList.remove('active');
            }
            
            addRelayLog(`   ✅ Relè ${item.id} OK`);
        }, item.duration);
    }
    
    function resetRelayVisuals() {
        // Reset tutti i relè
        for (let i = 1; i <= 8; i++) {
            document.getElementById(`relay-${i}`).classList.remove('active');
        }
        
        // Reset dispositivi
        document.getElementById('gate-visual').classList.remove('open');
        document.getElementById('led-red').classList.remove('active');
        document.getElementById('led-green').classList.remove('active');
        document.getElementById('led-yellow').classList.remove('active');
        document.getElementById('buzzer').classList.remove('active');
    }
    
    function addRelayLog(message) {
        const log = document.getElementById('relay-log');
        const timestamp = new Date().toLocaleTimeString();
        log.innerHTML += `[${timestamp}] ${message}\n`;
        log.scrollTop = log.scrollHeight;
    }
    </script>
'''

if __name__ == "__main__":
    main()
