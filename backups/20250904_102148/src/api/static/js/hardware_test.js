
// File: /opt/access_control/src/api/static/hardware_test.js
// JavaScript per test hardware real-time

// Variabili per polling test
let testPollingIntervals = {};

// Funzione per avviare test lettore
async function startReaderTest() {
    const button = document.getElementById('test-reader-btn');
    const output = document.getElementById('reader-test-output');
    
    if (!button || !output) {
        console.error('Elementi test lettore non trovati');
        return;
    }
    
    // Disabilita pulsante
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Test in corso...';
    
    // Pulisci output
    output.innerHTML = '<div class="loading">Avvio test lettore...</div>';
    
    try {
        // Avvia test
        const response = await fetch('/api/test/reader', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Avvia polling per aggiornamenti
            startTestPolling('reader', output, button, 'Test Lettore');
        } else {
            output.innerHTML = `<div class="error">❌ ${data.error}</div>`;
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-play"></i> Test Lettore';
        }
    } catch (error) {
        output.innerHTML = `<div class="error">❌ Errore: ${error.message}</div>`;
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-play"></i> Test Lettore';
    }
}

// Funzione per avviare test USB-RLY08
async function startRelayTest() {
    const button = document.getElementById('test-relay-btn');
    const output = document.getElementById('relay-test-output');
    
    if (!button || !output) {
        console.error('Elementi test relay non trovati');
        return;
    }
    
    // Disabilita pulsante
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Test in corso...';
    
    // Pulisci output
    output.innerHTML = '<div class="loading">Avvio test USB-RLY08...</div>';
    
    try {
        // Avvia test
        const response = await fetch('/api/test/relay', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Avvia polling per aggiornamenti
            startTestPolling('relay', output, button, 'Test USB-RLY08');
        } else {
            output.innerHTML = `<div class="error">❌ ${data.error}</div>`;
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-play"></i> Test USB-RLY08';
        }
    } catch (error) {
        output.innerHTML = `<div class="error">❌ Errore: ${error.message}</div>`;
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-play"></i> Test USB-RLY08';
    }
}

// Polling per aggiornamenti test
function startTestPolling(testId, outputElement, buttonElement, buttonText) {
    // Ferma polling precedente se esiste
    if (testPollingIntervals[testId]) {
        clearInterval(testPollingIntervals[testId]);
    }
    
    testPollingIntervals[testId] = setInterval(async () => {
        try {
            const response = await fetch(`/api/test/status?test_id=${testId}`);
            const data = await response.json();
            
            if (data.success && data.test) {
                const test = data.test;
                
                // Aggiorna output
                let html = `<div class="test-status test-${test.status}">`;
                html += `<strong>Status:</strong> ${test.message}<br>`;
                html += `<strong>Tempo:</strong> ${new Date(test.timestamp * 1000).toLocaleTimeString()}<br><br>`;
                
                if (test.details && test.details.length > 0) {
                    html += '<strong>Dettagli:</strong><br>';
                    html += '<div class="test-details">';
                    test.details.forEach(detail => {
                        html += `${detail}<br>`;
                    });
                    html += '</div>';
                }
                
                html += '</div>';
                outputElement.innerHTML = html;
                
                // Se test completato, riabilita pulsante
                if (test.status !== 'running') {
                    clearInterval(testPollingIntervals[testId]);
                    delete testPollingIntervals[testId];
                    
                    buttonElement.disabled = false;
                    buttonElement.innerHTML = `<i class="fas fa-play"></i> ${buttonText}`;
                }
            }
        } catch (error) {
            console.error('Errore polling test:', error);
        }
    }, 1000); // Aggiorna ogni secondo
}

// Cleanup polling quando si cambia pagina
window.addEventListener('beforeunload', function() {
    Object.values(testPollingIntervals).forEach(interval => {
        clearInterval(interval);
    });
});

// Aggiungi CSS per styling test
function addTestStyles() {
    if (document.getElementById('test-hardware-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'test-hardware-styles';
    style.textContent = `
        .test-status {
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        .test-success {
            background: #d4edda;
            color: #155724;
            border-left: 4px solid #28a745;
        }
        .test-warning {
            background: #fff3cd;
            color: #856404;
            border-left: 4px solid #ffc107;
        }
        .test-error {
            background: #f8d7da;
            color: #721c24;
            border-left: 4px solid #dc3545;
        }
        .test-running {
            background: #d1ecf1;
            color: #0c5460;
            border-left: 4px solid #17a2b8;
        }
        .test-details {
            margin-top: 10px;
            padding: 10px;
            background: rgba(0,0,0,0.05);
            border-radius: 4px;
            white-space: pre-line;
            max-height: 300px;
            overflow-y: auto;
        }
        .test-output {
            min-height: 100px;
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 10px;
        }
        .loading {
            text-align: center;
            color: #666;
            font-style: italic;
        }
        .error {
            color: #dc3545;
            font-weight: bold;
        }
    `;
    document.head.appendChild(style);
}

// Inizializza quando DOM è pronto
document.addEventListener('DOMContentLoaded', function() {
    addTestStyles();
});
