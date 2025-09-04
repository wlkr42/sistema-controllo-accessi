// Dashboard JavaScript Functions

// Test lettore dalla dashboard principale
function testReader() {
    // Usa la configurazione corrente salvata
    showTestModal('card_reader', 'Test Lettore Tessere');
}

// Test relay dalla dashboard principale
function testRelay() {
    // Usa la configurazione corrente salvata
    showTestModal('relay_controller', 'Test Controller Relè USB-RLY08');
}

// Test cancello dalla dashboard principale
function testGate() {
    // Test apertura cancello
    if (confirm('Vuoi testare l\'apertura del cancello?')) {
        fetch('/api/test-gate-dashboard', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('✅ Cancello aperto con successo!');
            } else {
                alert('❌ Errore: ' + (data.error || 'Test fallito'));
            }
        })
        .catch(error => {
            alert('❌ Errore di connessione');
        });
    }
}

// Mostra modal di test hardware
function showTestModal(hardwareType, title) {
    // Ottieni la configurazione corrente
    fetch('/api/config/device-assignments')
        .then(response => response.json())
        .then(config => {
            const assignments = config.assignments || {};
            let deviceConfig = {};
            
            if (hardwareType === 'card_reader') {
                deviceConfig = assignments.card_reader || {};
            } else if (hardwareType === 'relay_controller') {
                deviceConfig = assignments.relay_controller || {};
            }
            
            // Crea e mostra il modal
            const modal = createTestModal(hardwareType, title, deviceConfig);
            document.body.appendChild(modal);
            
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
            
            // Rimuovi modal dopo chiusura
            modal.addEventListener('hidden.bs.modal', () => {
                modal.remove();
            });
            
            // Avvia test automaticamente
            setTimeout(() => {
                runHardwareTest(hardwareType, deviceConfig, modal);
            }, 500);
        })
        .catch(error => {
            alert('❌ Errore caricamento configurazione');
        });
}

// Crea modal per test hardware
function createTestModal(hardwareType, title, deviceConfig) {
    const modalId = 'testModal_' + Date.now();
    const deviceName = deviceConfig.device_name || 'Dispositivo';
    
    // Determina il nome corretto del dispositivo
    let displayName = deviceName;
    if (hardwareType === 'card_reader' && deviceConfig.device_key) {
        if (deviceConfig.device_key.includes('23d8:0285')) {
            displayName = 'CRT-285/288K Tessera Sanitaria';
        } else if (deviceConfig.device_key.includes('076b:5427')) {
            displayName = 'OMNIKEY 5427 CK';
        }
    }
    
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = modalId;
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header bg-primary text-white">
                    <h5 class="modal-title">
                        <i class="fas fa-vial me-2"></i>${title}
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <strong>Dispositivo:</strong> ${displayName}
                    </div>
                    <div class="test-output" style="background: #1e1e1e; color: #0f0; font-family: monospace; padding: 15px; min-height: 200px; max-height: 400px; overflow-y: auto; border-radius: 5px;">
                        <div class="test-log">Inizializzazione test...</div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Chiudi</button>
                </div>
            </div>
        </div>
    `;
    
    return modal;
}

// Esegui test hardware
function runHardwareTest(hardwareType, deviceConfig, modal) {
    const logDiv = modal.querySelector('.test-log');
    
    // Log iniziale
    addTestLog(logDiv, 'INFO', `Avvio test ${hardwareType}...`);
    addTestLog(logDiv, 'INFO', `Device key: ${deviceConfig.device_key || 'non configurato'}`);
    
    if (deviceConfig.device_path) {
        addTestLog(logDiv, 'INFO', `Device path: ${deviceConfig.device_path}`);
    }
    
    // Prepara i parametri per il test
    const testData = {
        type: hardwareType  // L'API usa 'type' non 'hardware_type'
    };
    
    // Aggiungi parametri specifici in base al tipo
    if (hardwareType === 'card_reader') {
        // Determina il tipo di lettore dal device_key
        if (deviceConfig.device_key && deviceConfig.device_key.includes('23d8:0285')) {
            testData.reader_type = 'CRT285';
        } else {
            testData.reader_type = 'OMNIKEY';
        }
        testData.device_key = deviceConfig.device_key;
        // Aggiungi device_path che l'API si aspetta
        testData.device_path = deviceConfig.device_path || 'USB';
        testData.port = deviceConfig.device_path || 'USB'; // retrocompatibilità
    } else if (hardwareType === 'relay_controller' || hardwareType === 'relay') {
        testData.type = 'relay'; // L'API si aspetta 'relay' non 'relay_controller'
        testData.device_path = deviceConfig.device_path || '/dev/ttyACM0';
        testData.port = deviceConfig.device_path || '/dev/ttyACM0';
    }
    
    addTestLog(logDiv, 'INFO', 'Connessione al dispositivo...');
    
    // Chiamata API per test
    fetch('/api/hardware/test-connection', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(testData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addTestLog(logDiv, 'SUCCESS', '✅ TEST COMPLETATO CON SUCCESSO');
            
            // Log dettagli risultato
            if (data.details) {
                if (typeof data.details === 'string') {
                    data.details.split('\n').forEach(line => {
                        if (line.trim()) {
                            addTestLog(logDiv, 'INFO', line);
                        }
                    });
                } else if (Array.isArray(data.details)) {
                    data.details.forEach(line => {
                        addTestLog(logDiv, 'INFO', line);
                    });
                }
            }
            
            // Per il lettore tessere, mostra istruzioni
            if (hardwareType === 'card_reader') {
                addTestLog(logDiv, 'INFO', '');
                addTestLog(logDiv, 'WARNING', '⚠️ Inserire una tessera sanitaria per testare la lettura');
                addTestLog(logDiv, 'INFO', 'Attesa tessera (timeout 10 secondi)...');
                
                // Test lettura tessera
                testCardReading(logDiv, testData);
            }
        } else {
            addTestLog(logDiv, 'ERROR', '❌ TEST FALLITO');
            addTestLog(logDiv, 'ERROR', data.message || data.error || 'Errore sconosciuto');
            
            if (data.details) {
                addTestLog(logDiv, 'ERROR', data.details);
            }
        }
    })
    .catch(error => {
        addTestLog(logDiv, 'ERROR', '❌ ERRORE DI CONNESSIONE');
        addTestLog(logDiv, 'ERROR', error.toString());
    });
}

// Test lettura tessera
function testCardReading(logDiv, readerConfig) {
    fetch('/api/hardware/test-read-card', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(readerConfig)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addTestLog(logDiv, 'SUCCESS', '✅ Tessera letta con successo!');
            if (data.codice_fiscale) {
                // Mostra solo parte del CF per privacy
                const cf = data.codice_fiscale;
                const cfMasked = cf.substring(0, 4) + '****' + cf.substring(cf.length - 4);
                addTestLog(logDiv, 'INFO', `Codice Fiscale: ${cfMasked}`);
            }
        } else if (data.timeout) {
            addTestLog(logDiv, 'WARNING', '⏱️ Timeout - Nessuna tessera inserita');
        } else {
            addTestLog(logDiv, 'ERROR', '❌ Errore lettura tessera');
            addTestLog(logDiv, 'ERROR', data.message || 'Errore sconosciuto');
        }
    })
    .catch(error => {
        addTestLog(logDiv, 'ERROR', '❌ Errore test lettura');
    });
}

// Aggiungi log al test output
function addTestLog(logDiv, level, message) {
    const line = document.createElement('div');
    line.style.marginBottom = '2px';
    
    const timestamp = new Date().toLocaleTimeString();
    
    // Colore in base al livello
    switch(level) {
        case 'ERROR':
            line.style.color = '#ff6b6b';
            break;
        case 'WARNING':
            line.style.color = '#ffd93d';
            break;
        case 'SUCCESS':
            line.style.color = '#6bcf7f';
            break;
        case 'INFO':
        default:
            line.style.color = '#0f0';
            break;
    }
    
    line.textContent = `[${timestamp}] ${message}`;
    logDiv.appendChild(line);
    
    // Auto-scroll
    logDiv.parentElement.scrollTop = logDiv.parentElement.scrollHeight;
}

// Carica attività recenti
function loadRecentActivities() {
    fetch('/api/recent-activities')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('recent-accesses');
            if (container && data.activities) {
                if (data.activities.length === 0) {
                    container.innerHTML = '<div class="text-center text-muted">Nessun accesso recente</div>';
                } else {
                    let html = '<div class="table-responsive"><table class="table table-sm">';
                    html += '<thead><tr><th>Data/Ora</th><th>Utente</th><th>Stato</th></tr></thead><tbody>';
                    
                    data.activities.forEach(activity => {
                        const statusBadge = activity.authorized === 1 ? 
                            '<span class="badge bg-success">Autorizzato</span>' : 
                            '<span class="badge bg-danger">Negato</span>';
                        
                        html += `<tr>
                            <td>${new Date(activity.timestamp).toLocaleString()}</td>
                            <td>${activity.name || activity.codice_fiscale || 'Sconosciuto'}</td>
                            <td>${statusBadge}</td>
                        </tr>`;
                    });
                    
                    html += '</tbody></table></div>';
                    container.innerHTML = html;
                }
            }
        })
        .catch(error => {
            console.error('Errore caricamento attività:', error);
        });
}

// Inizializzazione al caricamento pagina
document.addEventListener('DOMContentLoaded', function() {
    // Carica attività recenti
    loadRecentActivities();
    
    // Aggiorna ogni 30 secondi
    setInterval(loadRecentActivities, 30000);
});