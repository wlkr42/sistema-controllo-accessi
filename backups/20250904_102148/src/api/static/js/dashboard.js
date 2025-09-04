// File: /opt/access_control/src/api/static/js/dashboard.js
// JavaScript per Dashboard Sistema Controllo Accessi

// Variabili globali per evitare inizializzazioni multiple
let dashboardInitialized = false;
let refreshInterval = null;

// ===== FUNZIONI CARICAMENTO DATI =====

function loadDashboardData() {
    // Statistiche
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            if (!data.error) {
                document.getElementById('accessi-oggi').textContent = data.accessi_oggi || '0';
                document.getElementById('autorizzati').textContent = data.autorizzati_oggi || '0';
            }
        })
        .catch(error => console.error('Errore stats:', error));

    // Utenti totali
    fetch('/api/users/count')
        .then(response => response.json())
        .then(data => {
            if (!data.error) {
                document.getElementById('utenti-totali').textContent = data.count || '0';
            }
        })
        .catch(error => console.error('Errore users count:', error));

    // Accessi recenti
    fetch('/api/recent-accesses')
        .then(response => response.json())
        .then(data => {
            if (!data.error && data.accesses) {
                let html = '';
                data.accesses.slice(0, 5).forEach(access => {
                    const status = access.autorizzato ? 
                        '<span class="badge bg-success">Autorizzato</span>' : 
                        '<span class="badge bg-danger">Negato</span>';
                    const time = new Date(access.timestamp).toLocaleTimeString();
                    html += `
                        <div class="d-flex justify-content-between align-items-center border-bottom py-2">
                            <div>
                                <strong>${access.nome}</strong><br>
                                <small class="text-muted">${access.codice_fiscale}</small>
                            </div>
                            <div class="text-end">
                                ${status}<br>
                                <small class="text-muted">${time}</small>
                            </div>
                        </div>
                    `;
                });
                document.getElementById('recent-accesses').innerHTML = html || '<div class="text-muted">Nessun accesso recente</div>';
            }
        })
        .catch(error => console.error('Errore recent accesses:', error));
}

// ===== TEST HARDWARE =====

// Test cancello
function testGate() {
    const status = document.getElementById('hardware-status');
    status.innerHTML = '<div class="alert alert-info">Test cancello in corso...</div>';
    
    fetch('/api/test/gate')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                status.innerHTML = '<div class="alert alert-success">✅ Test cancello completato con successo</div>';
            } else {
                status.innerHTML = `<div class="alert alert-danger">❌ ${data.error}</div>`;
            }
        })
        .catch(error => {
            status.innerHTML = `<div class="alert alert-danger">❌ Errore comunicazione: ${error}</div>`;
        })
        .finally(() => {
            setTimeout(() => status.innerHTML = '', 5000);
        });
}

// Test lettore con modal real-time
function testReader() {
    const modal = new bootstrap.Modal(document.getElementById('readerTestModal'));
    modal.show();
    
    const logContent = document.getElementById('reader-log-content');
    logContent.innerHTML = 'Cliccare "Avvia Test" per iniziare...';
    window.continuousTestMode = false;
    window.testRestarting = false;
    
    document.getElementById('start-reader-test').onclick = function() {
        if (window.continuousTestMode) {
            window.continuousTestMode = false;
            this.innerHTML = '<i class="fas fa-play"></i> Avvia Test';
            addLogLine('⏹️ ARRESTO TEST RICHIESTO', 'warning');
            addLogLine('Il test verrà fermato al prossimo ciclo');
            return;
        }
        
        window.continuousTestMode = true;
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Test in corso...';
        
        logContent.innerHTML = '';
        addLogLine('🚀 AVVIO TEST LETTORE OMNIKEY 5427CK');
        addLogLine('═'.repeat(50));
        
        fetch('/api/hardware/test-reader', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    startReaderPolling();
                } else {
                    addLogLine(`❌ ERRORE: ${data.error}`, 'error');
                    resetTestButton();
                }
            });
    };
}

// Test USB-RLY08
function testRelay() {
    const modal = new bootstrap.Modal(document.getElementById('relayTestModal'));
    modal.show();
}

// Test integrato completo con tessera reale
function testIntegrated() {
    const modal = new bootstrap.Modal(document.getElementById('integratedTestModal'));
    modal.show();
    resetIntegratedTest();
    
    fetch('/api/test/integrated', {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                pollIntegratedStatus();
            } else {
                document.getElementById('integrated-log').innerHTML = 
                    `<div class="text-danger">Errore: ${data.error}</div>`;
            }
        });
}

// ===== FUNZIONI POLLING =====

// Polling real-time per test lettore
function startReaderPolling() {
    const pollInterval = setInterval(() => {
        fetch('/api/hardware/status?test_id=reader')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.test) {
                    const test = data.test;
                    
                    if (test.details && test.details.length > 0) {
                        const logContent = document.getElementById('reader-log-content');
                        const currentLines = logContent.querySelectorAll('.log-line').length;
                        
                        for (let i = currentLines - 2; i < test.details.length; i++) {
                            if (i >= 0 && test.details[i]) {
                                addLogLine(test.details[i]);
                            }
                        }
                    }
                    
                    if (test.status !== 'running') {
                        if (test.status === 'success') {
                            addLogLine('🎯 TEST COMPLETATO CON SUCCESSO!', 'success');
                        } else if (test.status === 'warning') {
                            addLogLine('⚠️ TEST COMPLETATO CON AVVISI', 'warning');
                        } else {
                            addLogLine('❌ TEST FALLITO', 'error');
                        }
                        
                        addLogLine('═'.repeat(50));
                        
                        if (window.continuousTestMode && !window.testRestarting) {
                            window.testRestarting = true;
                            clearInterval(pollInterval);
                            
                            setTimeout(() => {
                                addLogLine('');
                                addLogLine('⏳ ATTESA PROSSIMA TESSERA...', 'status');
                                addLogLine('Inserire tessera per continuare il test', 'normal');
                                addLogLine('');
                            }, 500);
                            
                            setTimeout(() => {
                                window.testRestarting = false;
                                if (window.continuousTestMode) {
                                    fetch('/api/hardware/test-reader', {method: 'POST'})
                                        .then(response => response.json())
                                        .then(data => {
                                            if (data.success) {
                                                startReaderPolling();
                                            }
                                        });
                                }
                            }, 2000);
                        } else {
                            clearInterval(pollInterval);
                        }
                        
                        resetTestButton();
                    }
                }
            })
            .catch(error => {
                clearInterval(pollInterval);
                addLogLine(`❌ Errore polling: ${error}`, 'error');
                resetTestButton();
            });
    }, 1000);
}

// Funzione per test sequenziale relay con animazioni real-time
function startRelaySequence() {
    const btn = document.getElementById('start-relay-test');
    const log = document.getElementById('relay-log');
    
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Test in corso...';
    
    log.innerHTML = 'Avvio test USB-RLY08...\n';
    
    for (let i = 1; i <= 8; i++) {
        document.getElementById(`relay-${i}`).classList.remove('active');
    }
    resetDevices();
    
    fetch('/api/test_relay', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            pollRelayStatus();
        } else {
            log.innerHTML = 'ERRORE: ' + (data.error || 'Errore sconosciuto');
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-play me-2"></i>Avvia Test Sequenziale';
        }
    })
    .catch(error => {
        log.innerHTML = 'ERRORE CONNESSIONE: ' + error.message;
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-play me-2"></i>Avvia Test Sequenziale';
    });
}

// Polling stato relay per animazioni real-time
function pollRelayStatus() {
    const pollInterval = setInterval(() => {
        fetch('/api/relay_status')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'idle') {
                    clearInterval(pollInterval);
                    return;
                }
                
                if (data.log) {
                    document.getElementById('relay-log').innerHTML = data.log.join('\n');
                    const logDiv = document.getElementById('relay-log');
                    logDiv.scrollTop = logDiv.scrollHeight;
                }
                
                if (data.relay_states) {
                    updateRelayVisuals(data.relay_states);
                }
                
                if (data.status === 'completed' || data.status === 'error') {
                    clearInterval(pollInterval);
                    const btn = document.getElementById('start-relay-test');
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-play me-2"></i>Avvia Test Sequenziale';
                    
                    setTimeout(() => {
                        for (let i = 1; i <= 8; i++) {
                            document.getElementById(`relay-${i}`).classList.remove('active');
                        }
                        resetDevices();
                    }, 2000);
                }
            })
            .catch(error => {
                console.error('Errore polling:', error);
                clearInterval(pollInterval);
            });
    }, 100);
}

// Polling stato test integrato
function pollIntegratedStatus() {
    const pollInterval = setInterval(() => {
        fetch('/api/integrated_status')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'idle') {
                    clearInterval(pollInterval);
                    return;
                }
                
                if (data.log) {
                    const logHtml = data.log.map(line => {
                        let className = 'log-line';
                        if (line.includes('✅')) className += ' text-success';
                        else if (line.includes('❌')) className += ' text-danger';
                        else if (line.includes('🟡') || line.includes('💳')) className += ' text-warning';
                        else if (line.includes('📄') || line.includes('👤')) className += ' text-info';
                        return `<div class="${className}">${line}</div>`;
                    }).join('');
                    
                    document.getElementById('integrated-log').innerHTML = logHtml;
                    
                    const logDiv = document.getElementById('integrated-log');
                    logDiv.scrollTop = logDiv.scrollHeight;
                }
                
                updateIntegratedAnimations(data);
                
                if (data.status === 'completed' || data.status === 'error') {
                    clearInterval(pollInterval);
                    document.getElementById('restart-integrated-test').disabled = false;
                }
            })
            .catch(error => {
                console.error('Errore polling:', error);
                clearInterval(pollInterval);
            });
    }, 100);
}

// ===== FUNZIONI HELPER =====

// Aggiungi linea al log con SCROLL FUNZIONANTE
function addLogLine(text, type = 'normal') {
    const logContent = document.getElementById('reader-log-content');
    const timestamp = new Date().toLocaleTimeString();
    
    let color = '#00ff00';
    if (type === 'error') color = '#ff4444';
    if (type === 'warning') color = '#ffaa00';
    if (type === 'success') color = '#44ff44';
    if (type === 'status') color = '#00aaff';
    
    const line = document.createElement('div');
    line.className = 'log-line';
    line.style.color = color;
    line.style.marginBottom = '2px';
    line.innerHTML = `[${timestamp}] ${text}`;
    
    logContent.appendChild(line);
    
    const logContainer = document.getElementById('reader-test-log');
    if (logContainer) {
        const isScrolledToBottom = logContainer.scrollHeight - logContainer.clientHeight <= logContainer.scrollTop + 50;
        
        if (isScrolledToBottom) {
            setTimeout(() => {
                logContainer.scrollTop = logContainer.scrollHeight;
            }, 10);
        }
    }
}

// Reset pulsante test
function resetTestButton() {
    const btn = document.getElementById('start-reader-test');
    btn.disabled = false;
    if (window.continuousTestMode) {
        btn.innerHTML = '<i class="fas fa-stop"></i> Ferma Test';
    } else {
        btn.innerHTML = '<i class="fas fa-play"></i> Avvia Test';
    }
}

// Aggiorna visualizzazione relay e dispositivi collegati
function updateRelayVisuals(relayStates) {
    for (let i = 1; i <= 8; i++) {
        const relayBox = document.getElementById(`relay-${i}`);
        if (relayStates[i]) {
            relayBox.classList.add('active');
        } else {
            relayBox.classList.remove('active');
        }
    }
    
    // Aggiorna dispositivi in base ai relay attivi
    if (relayStates[1]) {
        document.getElementById('gate-visual').classList.add('open');
    } else {
        document.getElementById('gate-visual').classList.remove('open');
    }
    
    if (relayStates[2]) {
        document.getElementById('led-red').classList.add('active');
    } else {
        document.getElementById('led-red').classList.remove('active');
    }
    
    if (relayStates[3]) {
        document.getElementById('led-green').classList.add('active');
    } else {
        document.getElementById('led-green').classList.remove('active');
    }
    
    if (relayStates[4]) {
        document.getElementById('led-yellow').classList.add('active');
    } else {
        document.getElementById('led-yellow').classList.remove('active');
    }
    
    if (relayStates[5]) {
        document.getElementById('buzzer').classList.add('active');
    } else {
        document.getElementById('buzzer').classList.remove('active');
    }
}

// Reset tutti i dispositivi
function resetDevices() {
    document.getElementById('gate-visual').classList.remove('open');
    document.getElementById('led-red').classList.remove('active');
    document.getElementById('led-green').classList.remove('active');
    document.getElementById('led-yellow').classList.remove('active');
    document.getElementById('buzzer').classList.remove('active');
}

// Aggiorna animazioni test integrato
function updateIntegratedAnimations(data) {
    const cardVisual = document.getElementById('card-visual');
    const readerVisual = document.getElementById('reader-visual');
    const gateVisual = document.getElementById('integrated-gate');
    const statusText = document.getElementById('integrated-status');
    
    switch(data.phase) {
        case 'connecting':
            statusText.innerHTML = '<i class="fas fa-sync fa-spin"></i> Connessione hardware...';
            statusText.className = 'text-info';
            break;
            
        case 'waiting_card':
            cardVisual.className = 'card-animation waiting';
            readerVisual.className = 'reader-visual scanning';
            statusText.innerHTML = '<i class="fas fa-hand-paper"></i> INSERIRE TESSERA NEL LETTORE';
            statusText.className = 'text-warning animated-text';
            document.getElementById('integrated-led-yellow').classList.add('blink');
            break;
            
        case 'reading_card':
            cardVisual.className = 'card-animation inserting';
            readerVisual.className = 'reader-visual active';
            statusText.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Lettura tessera in corso...';
            statusText.className = 'text-info';
            document.getElementById('integrated-led-yellow').classList.remove('blink');
            break;
            
        case 'access_granted':
            cardVisual.className = 'card-animation success';
            readerVisual.className = 'reader-visual success';
            statusText.innerHTML = '<i class="fas fa-check-circle"></i> ACCESSO AUTORIZZATO!';
            statusText.className = 'text-success fw-bold';
            document.getElementById('integrated-led-green').classList.add('active');
            document.getElementById('integrated-led-red').classList.remove('active');
            gateVisual.classList.add('open');
            document.getElementById('integrated-buzzer').classList.add('active');
            setTimeout(() => {
                document.getElementById('integrated-buzzer').classList.remove('active');
            }, 200);
            break;
            
        case 'access_denied':
            cardVisual.className = 'card-animation denied';
            readerVisual.className = 'reader-visual denied';
            statusText.innerHTML = '<i class="fas fa-times-circle"></i> ACCESSO NEGATO!';
            statusText.className = 'text-danger fw-bold';
            document.getElementById('integrated-led-red').classList.add('active');
            document.getElementById('integrated-led-green').classList.remove('active');
            let beepCount = 0;
            const beepInterval = setInterval(() => {
                document.getElementById('integrated-buzzer').classList.toggle('active');
                beepCount++;
                if (beepCount >= 6) clearInterval(beepInterval);
            }, 150);
            break;
        
        case 'timeout':
            cardVisual.className = 'card-animation';
            readerVisual.className = 'reader-visual';
            statusText.innerHTML = '<i class="fas fa-clock"></i> Timeout - Nessuna tessera inserita';
            statusText.className = 'text-warning';
            document.getElementById('integrated-led-yellow').classList.remove('blink');
            break;
            
        case 'error':
            statusText.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Errore durante il test';
            statusText.className = 'text-danger';
            break;
            
        case 'completed':
            setTimeout(() => {
                if (data.authorized) {
                    gateVisual.classList.remove('open');
                    document.getElementById('integrated-led-green').classList.remove('active');
                } else {
                    document.getElementById('integrated-led-red').classList.remove('active');
                }
                document.getElementById('integrated-led-yellow').classList.remove('blink');
                cardVisual.className = 'card-animation';
                statusText.innerHTML = '<i class="fas fa-check"></i> Test completato';
                statusText.className = 'text-info';
            }, 3000);
            break;
    }
}

// Reset test integrato
function resetIntegratedTest() {
    document.getElementById('integrated-log').innerHTML = 
        '<div class="text-muted text-center">Clicca "Avvia Test" per iniziare...</div>';
    document.getElementById('integrated-status').innerHTML = 
        '<i class="fas fa-info-circle"></i> Pronto';
    document.getElementById('integrated-status').className = '';
    document.getElementById('card-visual').className = 'card-animation';
    document.getElementById('reader-visual').className = 'reader-visual';
    document.getElementById('integrated-gate').classList.remove('open');
    document.getElementById('integrated-led-green').classList.remove('active');
    document.getElementById('integrated-led-red').classList.remove('active');
    document.getElementById('integrated-led-yellow').classList.remove('active', 'blink');
    document.getElementById('integrated-buzzer').classList.remove('active');
    document.getElementById('restart-integrated-test').disabled = true;
}

// Funzione globale per pulire backdrop residui
function cleanupModals() {
    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
    document.body.classList.remove('modal-open');
    document.body.style.removeProperty('overflow');
    document.body.style.removeProperty('padding-right');
    const bodyAttributes = ['data-bs-padding-right', 'data-bs-overflow'];
    bodyAttributes.forEach(attr => document.body.removeAttribute(attr));
}

// ===== INIZIALIZZAZIONE =====

// Inizializza event listeners per modals dopo il caricamento
function initializeModalListeners() {
    const integratedModal = document.getElementById('integratedTestModal');
    if (integratedModal) {
        integratedModal.addEventListener('shown.bs.modal', function () {
            document.getElementById('restart-integrated-test').disabled = false;
        });
        
        integratedModal.addEventListener('hidden.bs.modal', function () {
            document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
            document.body.classList.remove('modal-open');
            document.body.style.removeProperty('overflow');
            document.body.style.removeProperty('padding-right');
        });
    }
    
    const relayModal = document.getElementById('relayTestModal');
    if (relayModal) {
        relayModal.addEventListener('hidden.bs.modal', function () {
            document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
            document.body.classList.remove('modal-open');
            document.body.style = '';
        });
    }
    
    const readerModal = document.getElementById('readerTestModal');
    if (readerModal) {
        readerModal.addEventListener('hidden.bs.modal', function () {
            document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
            document.body.classList.remove('modal-open');
            document.body.style = '';
        });
    }
}

// ===== INIZIALIZZAZIONE AL CARICAMENTO PAGINA =====
// UN SOLO EVENT LISTENER DOMContentLoaded!

document.addEventListener('DOMContentLoaded', function() {
    if (dashboardInitialized) return;
    dashboardInitialized = true;
    
    // Inizializza listeners per i modal (solo se è admin)
    if (window.userRole === 'admin') {
        initializeModalListeners();
    }
    
    // Carica i dati della dashboard UNA SOLA VOLTA
    loadDashboardData();
    
    // Clear any existing interval
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    
    // Auto-refresh ogni 5 secondi con un singolo interval
    refreshInterval = setInterval(loadDashboardData, 5000);
    
    // Cleanup quando si lascia la pagina
    window.addEventListener('beforeunload', function() {
        if (refreshInterval) {
            clearInterval(refreshInterval);
            refreshInterval = null;
        }
    });
    
    // Controlla se deve aprire automaticamente il profilo
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('show_profile') === 'true') {
        window.history.replaceState({}, document.title, '/');
        setTimeout(() => {
            if (window.userMenu) {
                window.userMenu.showProfileModal();
            }
        }, 500);
    }
});

// Funzioni helper per la nuova gestione utenti

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Funzioni per User Manager
function showCreateViewerModal() {
    // Implementa modal per creare viewer
    alert('TODO: Implementare modal creazione viewer');
}

function openExportModal() {
    // Implementa modal per export log
    alert('TODO: Implementare modal export Excel');
}