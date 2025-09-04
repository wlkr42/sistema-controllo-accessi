// File: /opt/access_control/src/api/static/js/hardware-manager.js
// Interfaccia hardware semplice: RILEVA + CONFIGURA

class SimpleHardwareManager {
    constructor() {
        this.hardwareList = document.getElementById('hardware-list');
        this.detectButton = document.getElementById('detect-hardware');
        this.saveButton = document.getElementById('save-hardware-config');
        
        this.detectedHardware = {
            usb_devices: [],
            serial_ports: [],
            hid_devices: []
        };
        this.deviceAssignments = {};
        
        this.init();
    }
    
    init() {
        if (this.detectButton) {
            this.detectButton.addEventListener('click', () => this.detectHardware());
        }
        
        if (this.saveButton) {
            this.saveButton.addEventListener('click', () => this.saveConfiguration());
        }
        
        // Auto-rilevamento iniziale
        this.detectHardware().then(() => {
            // Carica configurazione esistente DOPO il rilevamento hardware
            this.loadConfiguration();
        });
    }
    
    async detectHardware() {
        if (!this.detectButton) return;
        
        this.detectButton.disabled = true;
        this.detectButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Rilevamento...';
        this.showLoadingMessage();
        
        try {
            const response = await fetch('/api/hardware/detect');
            const data = await response.json();
            
            console.log('Hardware rilevato:', data);
            
            if (data.success) {
                this.detectedHardware = data;
                this.displayHardware(data);
                this.showAlert('success', data.message);
            } else {
                this.showAlert('danger', `Errore: ${data.error}`);
                this.showErrorMessage(data.error);
            }
        } catch (error) {
            console.error('Errore rilevamento:', error);
            this.showAlert('danger', `Errore comunicazione: ${error.message}`);
            this.showErrorMessage(error.message);
        } finally {
            this.detectButton.disabled = false;
            this.detectButton.innerHTML = '<i class="fas fa-search me-2"></i>Rileva Hardware';
        }
    }
    
    displayHardware(data) {
        if (!this.hardwareList) return;
        
        let html = `
            <div class="row">
                <!-- PARTE 1: HARDWARE RILEVATO -->
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header bg-info text-white">
                            <h5 class="mb-0">
                                <i class="fas fa-list me-2"></i>
                                Hardware Rilevato (comandi Linux)
                            </h5>
                        </div>
                        <div class="card-body">
                            ${this.generateDetectedHardwareSection(data)}
                        </div>
                    </div>
                </div>
                
                <!-- PARTE 2: CONFIGURAZIONE -->
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header bg-success text-white">
                            <h5 class="mb-0">
                                <i class="fas fa-cog me-2"></i>
                                Configurazione Software
                            </h5>
                        </div>
                        <div class="card-body">
                            ${this.generateConfigurationSection()}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.hardwareList.innerHTML = html;
        this.attachEventHandlers();
    }
    
    generateDetectedHardwareSection(data) {
        let html = '';
        
        // Dispositivi USB
        if (data.usb_devices && data.usb_devices.length > 0) {
            html += '<h6><i class="fas fa-usb me-2 text-primary"></i>Dispositivi USB (lsusb)</h6>';
            html += '<div class="table-responsive mb-4">';
            html += '<table class="table table-sm table-striped">';
            html += '<thead><tr><th>ID</th><th>Descrizione</th><th>Bus/Dev</th><th>Azioni</th></tr></thead><tbody>';
            
            data.usb_devices.forEach((device, index) => {
                html += `
                    <tr>
                        <td><code>${device.device_id}</code></td>
                        <td>${device.description}</td>
                        <td>Bus ${device.bus}, Dev ${device.device}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" onclick="hardwareManager.selectForConfig('usb', ${index})">
                                <i class="fas fa-arrow-right"></i> Usa
                            </button>
                        </td>
                    </tr>
                `;
            });
            
            html += '</tbody></table></div>';
        }
        
        // Porte seriali
        if (data.serial_ports && data.serial_ports.length > 0) {
            html += '<h6><i class="fas fa-plug me-2 text-warning"></i>Porte Seriali (ls /dev/tty*)</h6>';
            html += '<div class="table-responsive mb-4">';
            html += '<table class="table table-sm table-striped">';
            html += '<thead><tr><th>Porta</th><th>Tipo</th><th>Stato</th><th>Azioni</th></tr></thead><tbody>';
            
            data.serial_ports.forEach((port, index) => {
                const statusBadge = port.accessible 
                    ? '<span class="badge bg-success">OK</span>' 
                    : '<span class="badge bg-danger">Inaccessibile</span>';
                
                html += `
                    <tr>
                        <td><code>${port.port}</code></td>
                        <td>${port.type}</td>
                        <td>${statusBadge}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" onclick="hardwareManager.selectForConfig('serial', ${index})">
                                <i class="fas fa-arrow-right"></i> Usa
                            </button>
                        </td>
                    </tr>
                `;
            });
            
            html += '</tbody></table></div>';
        }
        
        // Dispositivi HID
        if (data.hid_devices && data.hid_devices.length > 0) {
            html += '<h6><i class="fas fa-keyboard me-2 text-info"></i>Dispositivi HID (ls /dev/hidraw*)</h6>';
            html += '<div class="table-responsive">';
            html += '<table class="table table-sm table-striped">';
            html += '<thead><tr><th>Dispositivo</th><th>Tipo</th><th>Azioni</th></tr></thead><tbody>';
            
            data.hid_devices.forEach((device, index) => {
                html += `
                    <tr>
                        <td><code>${device.device}</code></td>
                        <td>${device.type}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" onclick="hardwareManager.selectForConfig('hid', ${index})">
                                <i class="fas fa-arrow-right"></i> Usa
                            </button>
                        </td>
                    </tr>
                `;
            });
            
            html += '</tbody></table></div>';
        }
        
        if (!data.usb_devices?.length && !data.serial_ports?.length && !data.hid_devices?.length) {
            html = '<div class="alert alert-warning">Nessun hardware rilevato</div>';
        }
        
        return html;
    }
    
    generateConfigurationSection() {
        return `
            <div class="mb-3">
                <label class="form-label"><strong>Lettore Tessere:</strong></label>
                <select class="form-select mb-2" id="card-reader-select">
                    <option value="">-- Seleziona dispositivo --</option>
                </select>
                <button class="btn btn-sm btn-outline-success" onclick="window.hardwareManager.testDevice('card_reader', event)">
                    <i class="fas fa-vial"></i> Test
                </button>
                <div id="card-reader-test-result" class="mt-2"></div>
            </div>
            
            <div class="mb-3">
                <label class="form-label"><strong>Controller Relè:</strong></label>
                <select class="form-select mb-2" id="relay-controller-select">
                    <option value="">-- Seleziona dispositivo --</option>
                </select>
                <button class="btn btn-sm btn-outline-success" onclick="window.hardwareManager.testDevice('relay_controller', event)">
                    <i class="fas fa-vial"></i> Test
                </button>
                <div id="relay-controller-test-result" class="mt-2"></div>
            </div>
            
            <div class="d-grid">
                <button class="btn btn-primary" onclick="window.hardwareManager.saveConfiguration()">
                    <i class="fas fa-save me-2"></i>Salva Configurazione
                </button>
            </div>
            
            <div class="mt-3">
                <small class="text-muted">
                    <i class="fas fa-info-circle"></i>
                    Seleziona i dispositivi dalla lista a sinistra, poi clicca "Usa" per assegnarli.
                </small>
            </div>
        `;
    }
    
    selectForConfig(sourceType, deviceIndex) {
        let device = null;
        let deviceKey = '';
        let deviceName = '';
        let devicePath = '';

        if (sourceType === 'usb') {
            device = this.detectedHardware.usb_devices[deviceIndex];
            deviceKey = `usb:${device.device_id}`;
            deviceName = `${device.description} (${device.device_id})`;
            // Mappatura device USB → porta seriale reale
            // Se una sola porta, la usiamo; se più, chiediamo all’utente
            if (this.detectedHardware.serial_ports && this.detectedHardware.serial_ports.length === 1) {
                devicePath = this.detectedHardware.serial_ports[0].port;
            } else if (this.detectedHardware.serial_ports && this.detectedHardware.serial_ports.length > 1) {
                // Chiedi all’utente quale porta associare
                const portList = this.detectedHardware.serial_ports.map(p => p.port).join('\n');
                devicePath = prompt(
                    `Sono state rilevate più porte seriali:\n${portList}\n\nInserisci la porta da associare a questo device (es. /dev/ttyACM0):`,
                    this.detectedHardware.serial_ports[0].port
                );
            } else {
                devicePath = '';
            }
        } else if (sourceType === 'serial') {
            device = this.detectedHardware.serial_ports[deviceIndex];
            deviceKey = `serial:${device.port}`;
            deviceName = `${device.port} (${device.type})`;
            devicePath = device.port;
        } else if (sourceType === 'hid') {
            device = this.detectedHardware.hid_devices[deviceIndex];
            deviceKey = `hid:${device.device}`;
            deviceName = `${device.device} (HID)`;
            devicePath = device.device;
        }

        if (!device) return;

        // Mostra modal per selezione funzione
        this.showDeviceAssignmentModal(deviceKey, deviceName, device, devicePath);

        // Salva devicePath temporaneamente per conferma
        window.lastDevicePathSelected = devicePath;
    }
    
    showDeviceAssignmentModal(deviceKey, deviceName, deviceData, devicePath) {
        const modalContent = `
            <div class="modal fade" id="assignmentModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Assegna Funzione Dispositivo</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p><strong>Dispositivo:</strong> ${deviceName}</p>
                            <div class="mb-3">
                                <label class="form-label">Funzione nel software:</label>
                                <select class="form-select" id="device-function-select">
                                    <option value="">-- Seleziona funzione --</option>
                                    <option value="card_reader">Lettore Tessere</option>
                                    <option value="relay_controller">Controller Relè</option>
                                    <option value="other">Altro (non utilizzato)</option>
                                </select>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Annulla</button>
                            <button type="button" class="btn btn-primary" onclick="hardwareManager.confirmAssignment('${deviceKey}', '${deviceName}')">
                                Assegna
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Rimuovi modal esistente
        const existingModal = document.getElementById('assignmentModal');
        if (existingModal) existingModal.remove();
        
        // Aggiungi nuovo modal
        document.body.insertAdjacentHTML('beforeend', modalContent);
        const modal = new bootstrap.Modal(document.getElementById('assignmentModal'));
        modal.show();
    }
    
    confirmAssignment(deviceKey, deviceName) {
        const functionSelect = document.getElementById('device-function-select');
        const selectedFunction = functionSelect.value;

        // Recupera devicePath dal modal (hack: lo passiamo come attributo temporaneo)
        let devicePath = '';
        if (window.lastDevicePathSelected) {
            devicePath = window.lastDevicePathSelected;
        }

        if (!selectedFunction) {
            alert('Seleziona una funzione per il dispositivo');
            return;
        }

        // Salva assegnazione
        this.deviceAssignments[selectedFunction] = {
            device_key: deviceKey,
            device_name: deviceName,
            device_path: devicePath
        };

        // Aggiorna dropdown configurazione
        this.updateConfigurationDropdowns();

        // Chiudi modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('assignmentModal'));
        modal.hide();

        this.showAlert('success', `${deviceName} assegnato come ${this.getFunctionDisplayName(selectedFunction)}`);
    }
    
    updateConfigurationDropdowns() {
        // Aggiorna dropdown lettore tessere
        const cardReaderSelect = document.getElementById('card-reader-select');
        if (cardReaderSelect) {
            cardReaderSelect.innerHTML = '<option value="">-- Seleziona dispositivo --</option>';
            if (this.deviceAssignments.card_reader) {
                const dev = this.deviceAssignments.card_reader;
                // Per CRT-285 non mostrare il device_path perché usa USB diretto
                let label = dev.device_name;
                if (dev.device_key && dev.device_key.includes("23d8:0285")) {
                    // CRT-285 usa comunicazione USB diretta, non seriale
                    label = dev.device_name; // Solo il nome, senza path
                } else if (dev.device_path) {
                    label = dev.device_name + ` [${dev.device_path}]`;
                }
                cardReaderSelect.innerHTML += `<option value="card_reader" selected>${label}</option>`;
            }
        }

        // Aggiorna dropdown controller relè
        const relaySelect = document.getElementById('relay-controller-select');
        if (relaySelect) {
            relaySelect.innerHTML = '<option value="">-- Seleziona dispositivo --</option>';
            if (this.deviceAssignments.relay_controller) {
                const dev = this.deviceAssignments.relay_controller;
                // Per USB-RLY08 mostra sempre il device_path perché usa comunicazione seriale
                const label = dev.device_name + (dev.device_path ? ` [${dev.device_path}]` : '');
                relaySelect.innerHTML += `<option value="relay_controller" selected>${label}</option>`;
            }
        }
    }
    
    getFunctionDisplayName(functionKey) {
        const names = {
            'card_reader': 'Lettore Tessere',
            'relay_controller': 'Controller Relè',
            'other': 'Altro'
        };
        return names[functionKey] || functionKey;
    }
    
    async testDevice(deviceType, event) {
        const assignment = this.deviceAssignments[deviceType];
        if (!assignment) {
            this.showAlert('warning', 'Nessun dispositivo assegnato per il test');
            return;
        }

        const resultDiv = document.getElementById(`${deviceType.replace('_', '-')}-test-result`);
        const testButton = event ? event.target.closest('button') : null;
        
        // Disabilita il pulsante durante il test
        if (testButton) {
            testButton.disabled = true;
            const originalHtml = testButton.innerHTML;
            testButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Testing...';
            testButton.dataset.originalHtml = originalHtml;
        }
        
        if (resultDiv) {
            resultDiv.innerHTML = `<div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
                                   <small class="text-info">Test in corso...</small>`;
        }

        try {
            let endpoint, body;
            
            if (deviceType === 'relay_controller') {
                // Usa l'endpoint che funziona nel dashboard principale
                endpoint = '/api/test_relay';
                body = {};
            } else {
                // Per il lettore tessere
                endpoint = '/api/hardware/test-connection';
                body = {
                    type: deviceType,
                    device_path: assignment.device_path || assignment.device_key,
                    device_id: assignment.device_key
                };
            }
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(body)
            });

            const data = await response.json();
            
            if (deviceType === 'relay_controller' && data.success) {
                // Per il relè, aspetta un po' per mostrare che sta funzionando
                setTimeout(() => {
                    this.showTestResult(deviceType, data.success, data);
                }, 2000);
                
                if (resultDiv) {
                    resultDiv.innerHTML = `<div class="alert alert-warning alert-sm mb-0">
                        <small><i class="fas fa-bolt me-1"></i> Relè attivato! Ascolta i click dei relè...</small>
                    </div>`;
                }
            } else {
                this.showTestResult(deviceType, data.success, data);
            }

        } catch (error) {
            this.showTestResult(deviceType, false, {error: error.message});
        } finally {
            // Ripristina il pulsante dopo 2 secondi
            if (testButton) {
                setTimeout(() => {
                    testButton.disabled = false;
                    testButton.innerHTML = testButton.dataset.originalHtml || '<i class="fas fa-vial"></i> Test';
                }, 2000);
            }
        }
    }
    
    showTestResult(deviceType, success, data) {
        const resultDiv = document.getElementById(`${deviceType.replace('_', '-')}-test-result`);
        if (!resultDiv) return;
        
        const alertClass = success ? 'alert-success' : 'alert-danger';
        const icon = success ? 'fa-check-circle' : 'fa-times-circle';
        let message = data.message || (success ? 'Test OK' : data.error || 'Test fallito');
        
        // Messaggi personalizzati per ogni tipo di dispositivo
        if (success) {
            if (deviceType === 'card_reader') {
                message = '✅ Lettore tessere connesso e funzionante!';
            } else if (deviceType === 'relay_controller') {
                message = '✅ Test relè completato - Tutti i relè sono stati attivati in sequenza!';
            }
        }
        
        resultDiv.innerHTML = `
            <div class="alert ${alertClass} alert-sm mb-0">
                <small><i class="fas ${icon} me-1"></i> ${message}</small>
            </div>
        `;
        
        // Rimuovi il messaggio dopo 5 secondi
        setTimeout(() => {
            resultDiv.innerHTML = '';
        }, 5000);
    }
    
    async loadConfiguration() {
        try {
            const response = await fetch('/api/hardware/config');
            const data = await response.json();
            
            if (data.success && data.config) {
                this.deviceAssignments = data.config.assignments || {};
                this.updateConfigurationDropdowns();
            }
        } catch (error) {
            console.error('Errore caricamento configurazione:', error);
        }
    }
    
    async saveConfiguration() {
        try {
            const response = await fetch('/api/hardware/config/save', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    assignments: this.deviceAssignments
                })
            });

            const data = await response.json();
            if (data.success) {
                this.showAlert('success', 'Configurazione salvata con successo');
                // Ricarica la configurazione per aggiornare i dropdown
                await this.loadConfiguration();
            } else {
                this.showAlert('danger', `Errore salvataggio: ${data.error}`);
            }
        } catch (error) {
            this.showAlert('danger', `Errore: ${error.message}`);
        }
    }
    
    showLoadingMessage() {
        if (this.hardwareList) {
            this.hardwareList.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary mb-3"></div>
                    <p>Esecuzione comandi Linux di rilevamento...</p>
                    <small class="text-muted">lsusb, ls /dev/tty*, ls /dev/hidraw*</small>
                </div>
            `;
        }
    }
    
    showErrorMessage(error) {
        if (this.hardwareList) {
            this.hardwareList.innerHTML = `
                <div class="alert alert-danger">
                    <h6><i class="fas fa-exclamation-triangle me-2"></i>Errore Rilevamento</h6>
                    <p><code>${error}</code></p>
                    <button class="btn btn-primary" onclick="hardwareManager.detectHardware()">
                        <i class="fas fa-redo me-2"></i>Riprova
                    </button>
                </div>
            `;
        }
    }
    
    showAlert(type, message) {
        // Implementazione alert (uguale a prima)
        const existingAlerts = document.querySelectorAll('.hardware-alert');
        existingAlerts.forEach(alert => alert.remove());
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show hardware-alert`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        if (this.hardwareList && this.hardwareList.parentNode) {
            this.hardwareList.parentNode.insertBefore(alertDiv, this.hardwareList);
        }
        
        setTimeout(() => alertDiv?.remove(), 5000);
    }
    
    attachEventHandlers() {
        // Event handlers già gestiti negli onclick inline
    }
}

// Inizializza
document.addEventListener('DOMContentLoaded', function() {
    window.hardwareManager = new SimpleHardwareManager();
});
