// Hardware Manager per la pagina di configurazione

// Salva configurazione dispositivo selezionato
function saveDeviceAssignment(button) {
    const row = button.closest('tr');
    const deviceId = row.dataset.deviceId;
    const selectElement = row.querySelector('select');
    const hardwareType = selectElement.value;
    
    // Disabilita il pulsante durante il salvataggio
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    
    // Prepara i dati da salvare
    const assignments = {};
    
    // Ottieni tutte le assegnazioni correnti dalla tabella
    document.querySelectorAll('#hardware-list tr').forEach(tr => {
        const id = tr.dataset.deviceId;
        const type = tr.querySelector('select').value;
        
        if (type && type !== '') {
            // Estrai informazioni dal dataset
            const deviceName = tr.dataset.deviceName || '';
            const devicePath = tr.dataset.devicePath || null;
            
            // Assegna in base al tipo selezionato
            if (type === 'card_reader') {
                assignments.card_reader = {
                    device_key: id,
                    device_name: deviceName,
                    device_path: devicePath === 'null' || !devicePath ? null : devicePath,
                    note: id.includes('23d8:0285') ? 'CRT-285 usa comunicazione USB diretta, non seriale' : ''
                };
            } else if (type === 'relay_controller') {
                assignments.relay_controller = {
                    device_key: id,
                    device_name: deviceName,
                    device_path: devicePath === 'null' || !devicePath ? '/dev/ttyACM0' : devicePath,
                    note: 'USB-RLY08 usa porta seriale virtuale'
                };
            }
        }
    });
    
    // Salva su file JSON
    fetch('/api/config/device-assignments', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({assignments})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mostra successo
            button.classList.remove('btn-primary');
            button.classList.add('btn-success');
            button.innerHTML = '<i class="fas fa-check"></i>';
            
            // Dopo 2 secondi ripristina il pulsante
            setTimeout(() => {
                button.classList.remove('btn-success');
                button.classList.add('btn-primary');
                button.innerHTML = '<i class="fas fa-save"></i> Usa';
                button.disabled = false;
            }, 2000);
            
            // Aggiorna il badge di configurazione
            updateConfigurationBadge();
        } else {
            // Errore
            button.classList.add('btn-danger');
            button.innerHTML = '<i class="fas fa-times"></i>';
            alert('Errore salvataggio: ' + (data.error || 'Sconosciuto'));
            
            setTimeout(() => {
                button.classList.remove('btn-danger');
                button.classList.add('btn-primary');
                button.innerHTML = '<i class="fas fa-save"></i> Usa';
                button.disabled = false;
            }, 2000);
        }
    })
    .catch(error => {
        console.error('Errore:', error);
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-save"></i> Usa';
        alert('Errore di connessione');
    });
}

// Aggiorna badge configurazione
function updateConfigurationBadge() {
    fetch('/api/config/device-assignments')
        .then(response => response.json())
        .then(data => {
            const badge = document.querySelector('#configurazione-software-badge');
            if (badge) {
                const assignments = data.assignments || {};
                const hasReader = assignments.card_reader && assignments.card_reader.device_key;
                const hasRelay = assignments.relay_controller && assignments.relay_controller.device_key;
                
                if (hasReader && hasRelay) {
                    badge.innerHTML = '✅ Configurazione Software';
                    badge.classList.remove('text-warning');
                    badge.classList.add('text-success');
                } else {
                    badge.innerHTML = '⚠️ Configurazione Software';
                    badge.classList.remove('text-success');
                    badge.classList.add('text-warning');
                }
                
                // Aggiorna dettagli
                const readerInfo = document.querySelector('#selected-reader-info');
                const relayInfo = document.querySelector('#selected-relay-info');
                
                if (readerInfo) {
                    if (hasReader) {
                        let readerName = assignments.card_reader.device_name || 'Sconosciuto';
                        if (assignments.card_reader.device_key.includes('23d8:0285')) {
                            readerName = 'CRT-285/288K Tessera Sanitaria';
                        }
                        readerInfo.innerHTML = `<small class="text-success">Lettore: ${readerName}</small>`;
                    } else {
                        readerInfo.innerHTML = '<small class="text-warning">Lettore non configurato</small>';
                    }
                }
                
                if (relayInfo) {
                    if (hasRelay) {
                        relayInfo.innerHTML = `<small class="text-success">Relè: ${assignments.relay_controller.device_name || 'USB-RLY08'}</small>`;
                    } else {
                        relayInfo.innerHTML = '<small class="text-warning">Relè non configurato</small>';
                    }
                }
            }
        })
        .catch(error => {
            console.error('Errore aggiornamento badge:', error);
        });
}

// Test hardware dalla pagina config
function testHardwareFromConfig(button) {
    const row = button.closest('tr');
    const deviceId = row.dataset.deviceId;
    const deviceName = row.dataset.deviceName || 'Dispositivo';
    const devicePath = row.dataset.devicePath;
    const selectElement = row.querySelector('select');
    const hardwareType = selectElement.value;
    
    if (!hardwareType) {
        alert('Seleziona prima il tipo di dispositivo');
        return;
    }
    
    // Disabilita il pulsante
    button.disabled = true;
    const originalHtml = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    
    // Prepara dati per il test
    const testData = {
        type: hardwareType,
        device_path: devicePath === 'null' || !devicePath ? 'USB' : devicePath,
        port: devicePath === 'null' || !devicePath ? 'USB' : devicePath
    };
    
    // Aggiungi parametri specifici
    if (hardwareType === 'card_reader') {
        if (deviceId.includes('23d8:0285')) {
            testData.reader_type = 'CRT285';
        } else {
            testData.reader_type = 'OMNIKEY';
        }
    }
    
    // Esegui test
    fetch('/api/hardware/test-connection', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(testData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            button.classList.remove('btn-warning');
            button.classList.add('btn-success');
            button.innerHTML = '<i class="fas fa-check"></i>';
            
            // Mostra dettagli se disponibili
            if (data.message || data.details) {
                alert('✅ Test riuscito!\n\n' + (data.message || data.details || ''));
            }
        } else {
            button.classList.remove('btn-warning');
            button.classList.add('btn-danger');
            button.innerHTML = '<i class="fas fa-times"></i>';
            alert('❌ Test fallito:\n' + (data.message || data.error || 'Errore sconosciuto'));
        }
        
        // Ripristina dopo 3 secondi
        setTimeout(() => {
            button.disabled = false;
            button.classList.remove('btn-success', 'btn-danger');
            button.classList.add('btn-warning');
            button.innerHTML = originalHtml;
        }, 3000);
    })
    .catch(error => {
        console.error('Errore test:', error);
        button.disabled = false;
        button.innerHTML = originalHtml;
        alert('❌ Errore di connessione');
    });
}

// Inizializzazione al caricamento
document.addEventListener('DOMContentLoaded', function() {
    // Aggiorna badge configurazione all'avvio
    updateConfigurationBadge();
});