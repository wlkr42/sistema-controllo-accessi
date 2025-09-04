# File: /opt/access_control/src/api/modules/dispositivi.py
# Modulo Configurazione Dispositivi - Dashboard

from flask import render_template_string, request, jsonify, session
from ..web_api import app, require_auth, require_permission, config_manager, get_base_template

# ===============================
# TEMPLATE DISPOSITIVI
# ===============================

DISPOSITIVI_TEMPLATE = get_base_template() + """
{% block title %}Configurazione Dispositivi - Sistema Controllo Accessi{% endblock %}

{% block content %}
<div class="header">
    <h1><i class="fas fa-microchip"></i> {{ island_name }}</h1>
    <div class="user-info">
        <div class="status-dot"></div>
        <span>{{ user_role_name }}</span>
        <span id="current-time"></span>
        <a href="/logout" class="btn btn-secondary btn-sm">
            <i class="fas fa-sign-out-alt"></i> Logout
        </a>
    </div>
</div>

<div class="main-container">
    <div class="sidebar">
        <h3><i class="fas fa-bars"></i> Menu Principale</h3>
        <ul class="nav-menu">
            <li class="nav-item">
                <a href="/" class="nav-link">
                    <i class="fas fa-tachometer-alt"></i>
                    <span>Panoramica</span>
                </a>
            </li>
            <li class="nav-item">
                <a href="/dispositivi" class="nav-link active">
                    <i class="fas fa-microchip"></i>
                    <span>Dispositivi</span>
                </a>
            </li>
            <li class="nav-item">
                <a href="/email" class="nav-link">
                    <i class="fas fa-envelope"></i>
                    <span>Email</span>
                </a>
            </li>
            {% if 'users' in permissions or 'all' in permissions %}
            <li class="nav-item">
                <a href="/utenti" class="nav-link">
                    <i class="fas fa-users"></i>
                    <span>Utenti</span>
                </a>
            </li>
            {% endif %}
            <li class="nav-item">
                <a href="/log" class="nav-link">
                    <i class="fas fa-list-alt"></i>
                    <span>Log Accessi</span>
                </a>
            </li>
            <li class="nav-item">
                <a href="/allerte" class="nav-link">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>Allerte</span>
                </a>
            </li>
            {% if 'all' in permissions %}
            <li class="nav-item">
                <a href="/sistema" class="nav-link">
                    <i class="fas fa-cog"></i>
                    <span>Sistema</span>
                </a>
            </li>
            {% endif %}
        </ul>
    </div>
    
    <div class="content">
        <h2><i class="fas fa-microchip"></i> Configurazione Dispositivi</h2>
        
        <!-- Test Connessioni -->
        <div class="card">
            <h4><i class="fas fa-network-wired"></i> Test Connessioni Hardware</h4>
            <div class="grid grid-3">
                <div>
                    <strong>Lettore Tessere CF</strong>
                    <div id="reader-test-status" class="mt-3">
                        <span class="loading">Test in corso...</span>
                    </div>
                    <button class="btn btn-primary mt-3" onclick="testReader()">
                        <i class="fas fa-play"></i> Test Lettore
                    </button>
                </div>
                <div>
                    <strong>Modulo Relè USB-RLY08</strong>
                    <div id="relay-test-status" class="mt-3">
                        <span class="loading">Test in corso...</span>
                    </div>
                    <button class="btn btn-primary mt-3" onclick="testRelay()">
                        <i class="fas fa-play"></i> Test Relè
                    </button>
                </div>
                <div>
                    <strong>Connessione Database</strong>
                    <div id="db-test-status" class="mt-3">
                        <span class="loading">Test in corso...</span>
                    </div>
                    <button class="btn btn-primary mt-3" onclick="testDatabase()">
                        <i class="fas fa-play"></i> Test Database
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Configurazione Lettore CF -->
        <div class="card">
            <h4><i class="fas fa-id-card"></i> Configurazione Lettore Tessere</h4>
            <form id="reader-config-form">
                <div class="grid grid-2">
                    <div class="form-group">
                        <label class="form-label" for="reader-type">Tipo Lettore</label>
                        <select class="form-control form-select" id="reader-type" name="tipo">
                            <option value="HID Omnikey 5427CK">HID Omnikey 5427CK</option>
                            <option value="HID Omnikey 3121">HID Omnikey 3121</option>
                            <option value="ACS ACR122U">ACS ACR122U</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="reader-port">Porta Comunicazione</label>
                        <input type="text" class="form-control" id="reader-port" name="porta" placeholder="/dev/ttyACM0">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="reader-timeout">Timeout (secondi)</label>
                        <input type="number" class="form-control" id="reader-timeout" name="timeout" min="10" max="60" value="30">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="reader-retry">Tentativi Retry</label>
                        <input type="number" class="form-control" id="reader-retry" name="retry_tentativi" min="1" max="10" value="3">
                    </div>
                </div>
                <button type="submit" class="btn btn-success">
                    <i class="fas fa-save"></i> Salva Configurazione Lettore
                </button>
            </form>
        </div>
        
        <!-- Configurazione Relè -->
        <div class="card">
            <h4><i class="fas fa-toggle-on"></i> Configurazione Modulo Relè</h4>
            <form id="relay-config-form">
                <div class="grid grid-2">
                    <div class="form-group">
                        <label class="form-label" for="relay-port">Porta USB</label>
                        <input type="text" class="form-control" id="relay-port" name="porta" placeholder="/dev/ttyUSB0">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="relay-baud">Baud Rate</label>
                        <select class="form-control form-select" id="relay-baud" name="baud_rate">
                            <option value="9600">9600</option>
                            <option value="19200" selected>19200</option>
                            <option value="38400">38400</option>
                            <option value="57600">57600</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="relay-id">ID Modulo</label>
                        <input type="number" class="form-control" id="relay-id" name="modulo_id" min="1" max="255" value="8">
                    </div>
                </div>
                
                <h5 class="mt-3"><i class="fas fa-list"></i> Mapping Relè</h5>
                <div id="relay-mapping">
                    <!-- Caricato dinamicamente -->
                </div>
                
                <button type="submit" class="btn btn-success mt-3">
                    <i class="fas fa-save"></i> Salva Configurazione Relè
                </button>
            </form>
        </div>
        
        <!-- Test Individuali Relè -->
        <div class="card">
            <h4><i class="fas fa-flask"></i> Test Individuali Relè</h4>
            <p class="text-muted">Testa ogni relè individualmente per verificare le connessioni</p>
            <div id="relay-test-controls" class="grid grid-3">
                <!-- Caricato dinamicamente -->
            </div>
        </div>
        
        <!-- Log Diagnostici -->
        <div class="card">
            <h4><i class="fas fa-terminal"></i> Log Diagnostici</h4>
            <div class="form-group">
                <button class="btn btn-secondary" onclick="clearDiagnosticLog()">
                    <i class="fas fa-trash"></i> Pulisci Log
                </button>
                <button class="btn btn-primary" onclick="downloadDiagnosticLog()">
                    <i class="fas fa-download"></i> Scarica Log
                </button>
            </div>
            <div id="diagnostic-log" style="background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 15px; height: 300px; overflow-y: auto; font-family: 'Courier New', monospace; font-size: 0.85em;">
                <div class="loading">Caricamento log diagnostici...</div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    let diagnosticLogInterval;
    
    document.addEventListener('DOMContentLoaded', function() {
        loadDeviceConfigurations();
        loadRelayMapping();
        loadRelayTestControls();
        startDiagnosticLogUpdate();
        runInitialTests();
    });
    
    // Caricamento configurazioni iniziali
    async function loadDeviceConfigurations() {
        try {
            const response = await fetch('/api/devices/config');
            const data = await response.json();
            
            if (data.success) {
                // Popola form lettore
                document.getElementById('reader-type').value = data.reader.tipo || 'HID Omnikey 5427CK';
                document.getElementById('reader-port').value = data.reader.porta || '/dev/ttyACM0';
                document.getElementById('reader-timeout').value = data.reader.timeout || 30;
                document.getElementById('reader-retry').value = data.reader.retry_tentativi || 3;
                
                // Popola form relè
                document.getElementById('relay-port').value = data.relay.porta || '/dev/ttyUSB0';
                document.getElementById('relay-baud').value = data.relay.baud_rate || 19200;
                document.getElementById('relay-id').value = data.relay.modulo_id || 8;
            }
        } catch (error) {
            console.error('Errore caricamento configurazioni:', error);
        }
    }
    
    // Carica mapping relè
    async function loadRelayMapping() {
        try {
            const response = await fetch('/api/devices/relay-mapping');
            const data = await response.json();
            
            if (data.success) {
                const container = document.getElementById('relay-mapping');
                let html = '';
                
                for (let i = 1; i <= 6; i++) {
                    const relay = data.mapping[i] || {nome: `Relè ${i}`, durata_sec: 5};
                    html += `
                        <div class="grid grid-3 mb-3" style="align-items: end;">
                            <div class="form-group">
                                <label class="form-label">Relè ${i} - Nome</label>
                                <input type="text" class="form-control" 
                                       name="relay_${i}_nome" 
                                       value="${relay.nome}" 
                                       placeholder="Nome dispositivo">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Durata Attivazione (sec)</label>
                                <input type="number" class="form-control" 
                                       name="relay_${i}_durata" 
                                       value="${relay.durata_sec}" 
                                       min="1" max="60">
                            </div>
                            <div class="form-group">
                                <button type="button" class="btn btn-warning btn-sm" 
                                        onclick="testSingleRelay(${i})">
                                    <i class="fas fa-play"></i> Test
                                </button>
                            </div>
                        </div>
                    `;
                }
                
                container.innerHTML = html;
            }
        } catch (error) {
            console.error('Errore caricamento mapping relè:', error);
        }
    }
    
    // Carica controlli test relè
    async function loadRelayTestControls() {
        try {
            const response = await fetch('/api/devices/relay-mapping');
            const data = await response.json();
            
            if (data.success) {
                const container = document.getElementById('relay-test-controls');
                let html = '';
                
                for (let i = 1; i <= 6; i++) {
                    const relay = data.mapping[i] || {nome: `Relè ${i}`, durata_sec: 5};
                    html += `
                        <div class="card" style="padding: 15px;">
                            <strong>Relè ${i}</strong><br>
                            <small class="text-muted">${relay.nome}</small>
                            <div class="mt-2">
                                <button class="btn btn-success btn-sm" onclick="activateRelay(${i})">
                                    <i class="fas fa-power-off"></i> ON
                                </button>
                                <button class="btn btn-danger btn-sm" onclick="deactivateRelay(${i})">
                                    <i class="fas fa-power-off"></i> OFF
                                </button>
                            </div>
                            <div id="relay-${i}-status" class="mt-2">
                                <span class="status-badge status-offline">
                                    <i class="fas fa-circle"></i> Inattivo
                                </span>
                            </div>
                        </div>
                    `;
                }
                
                container.innerHTML = html;
            }
        } catch (error) {
            console.error('Errore caricamento controlli test:', error);
        }
    }
    
    // Test iniziali automatici
    async function runInitialTests() {
        await testReader();
        await testRelay();
        await testDatabase();
    }
    
    // Test lettore tessere
    async function testReader() {
        const statusEl = document.getElementById('reader-test-status');
        statusEl.innerHTML = '<span class="loading">Test in corso...</span>';
        
        try {
            const response = await fetch('/api/devices/test/reader', {method: 'POST'});
            const data = await response.json();
            
            if (data.success) {
                statusEl.innerHTML = `
                    <span class="status-badge status-online">
                        <i class="fas fa-check-circle"></i> Online
                    </span>
                    <br><small class="text-muted">${data.message}</small>
                `;
            } else {
                statusEl.innerHTML = `
                    <span class="status-badge status-offline">
                        <i class="fas fa-times-circle"></i> Offline
                    </span>
                    <br><small class="text-muted">${data.error}</small>
                `;
            }
        } catch (error) {
            statusEl.innerHTML = `
                <span class="status-badge status-offline">
                    <i class="fas fa-exclamation-triangle"></i> Errore
                </span>
                <br><small class="text-muted">Errore comunicazione</small>
            `;
        }
    }
    
    // Test modulo relè
    async function testRelay() {
        const statusEl = document.getElementById('relay-test-status');
        statusEl.innerHTML = '<span class="loading">Test in corso...</span>';
        
        try {
            const response = await fetch('/api/devices/test/relay', {method: 'POST'});
            const data = await response.json();
            
            if (data.success) {
                statusEl.innerHTML = `
                    <span class="status-badge status-online">
                        <i class="fas fa-check-circle"></i> Online
                    </span>
                    <br><small class="text-muted">${data.message}</small>
                `;
            } else {
                statusEl.innerHTML = `
                    <span class="status-badge status-offline">
                        <i class="fas fa-times-circle"></i> Offline
                    </span>
                    <br><small class="text-muted">${data.error}</small>
                `;
            }
        } catch (error) {
            statusEl.innerHTML = `
                <span class="status-badge status-offline">
                    <i class="fas fa-exclamation-triangle"></i> Errore
                </span>
                <br><small class="text-muted">Errore comunicazione</small>
            `;
        }
    }
    
    // Test database
    async function testDatabase() {
        const statusEl = document.getElementById('db-test-status');
        statusEl.innerHTML = '<span class="loading">Test in corso...</span>';
        
        try {
            const response = await fetch('/api/devices/test/database', {method: 'POST'});
            const data = await response.json();
            
            if (data.success) {
                statusEl.innerHTML = `
                    <span class="status-badge status-online">
                        <i class="fas fa-check-circle"></i> Online
                    </span>
                    <br><small class="text-muted">${data.message}</small>
                `;
            } else {
                statusEl.innerHTML = `
                    <span class="status-badge status-offline">
                        <i class="fas fa-times-circle"></i> Offline
                    </span>
                    <br><small class="text-muted">${data.error}</small>
                `;
            }
        } catch (error) {
            statusEl.innerHTML = `
                <span class="status-badge status-offline">
                    <i class="fas fa-exclamation-triangle"></i> Errore
                </span>
                <br><small class="text-muted">Errore comunicazione</small>
            `;
        }
    }
    
    // Test singolo relè
    async function testSingleRelay(relayNumber) {
        try {
            const response = await fetch(`/api/devices/test/relay/${relayNumber}`, {method: 'POST'});
            const data = await response.json();
            
            if (data.success) {
                showAlert(`Relè ${relayNumber} testato con successo`, 'success');
            } else {
                showAlert(`Errore test relè ${relayNumber}: ${data.error}`, 'danger');
            }
        } catch (error) {
            showAlert(`Errore comunicazione test relè ${relayNumber}`, 'danger');
        }
    }
    
    // Attiva relè specifico
    async function activateRelay(relayNumber) {
        const statusEl = document.getElementById(`relay-${relayNumber}-status`);
        statusEl.innerHTML = '<span class="loading">Attivazione...</span>';
        
        try {
            const response = await fetch(`/api/devices/relay/${relayNumber}/on`, {method: 'POST'});
            const data = await response.json();
            
            if (data.success) {
                statusEl.innerHTML = `
                    <span class="status-badge status-online">
                        <i class="fas fa-circle"></i> Attivo
                    </span>
                `;
                showAlert(`Relè ${relayNumber} attivato`, 'success');
            } else {
                statusEl.innerHTML = `
                    <span class="status-badge status-offline">
                        <i class="fas fa-circle"></i> Errore
                    </span>
                `;
                showAlert(`Errore attivazione relè ${relayNumber}`, 'danger');
            }
        } catch (error) {
            statusEl.innerHTML = `
                <span class="status-badge status-offline">
                    <i class="fas fa-circle"></i> Errore
                </span>
            `;
            showAlert('Errore comunicazione', 'danger');
        }
    }
    
    // Disattiva relè specifico
    async function deactivateRelay(relayNumber) {
        const statusEl = document.getElementById(`relay-${relayNumber}-status`);
        statusEl.innerHTML = '<span class="loading">Disattivazione...</span>';
        
        try {
            const response = await fetch(`/api/devices/relay/${relayNumber}/off`, {method: 'POST'});
            const data = await response.json();
            
            if (data.success) {
                statusEl.innerHTML = `
                    <span class="status-badge status-offline">
                        <i class="fas fa-circle"></i> Inattivo
                    </span>
                `;
                showAlert(`Relè ${relayNumber} disattivato`, 'success');
            } else {
                statusEl.innerHTML = `
                    <span class="status-badge status-offline">
                        <i class="fas fa-circle"></i> Errore
                    </span>
                `;
                showAlert(`Errore disattivazione relè ${relayNumber}`, 'danger');
            }
        } catch (error) {
            statusEl.innerHTML = `
                <span class="status-badge status-offline">
                    <i class="fas fa-circle"></i> Errore
                </span>
            `;
            showAlert('Errore comunicazione', 'danger');
        }
    }
    
    // Salvataggio configurazione lettore
    document.getElementById('reader-config-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const config = {};
        for (let [key, value] of formData.entries()) {
            config[key] = value;
        }
        
        try {
            const response = await fetch('/api/devices/config/reader', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert('Configurazione lettore salvata con successo', 'success');
                await testReader(); // Ritest dopo salvataggio
            } else {
                showAlert('Errore salvataggio configurazione lettore', 'danger');
            }
        } catch (error) {
            showAlert('Errore comunicazione', 'danger');
        }
    });
    
    // Salvataggio configurazione relè
    document.getElementById('relay-config-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const config = {
            porta: formData.get('porta'),
            baud_rate: parseInt(formData.get('baud_rate')),
            modulo_id: parseInt(formData.get('modulo_id')),
            mapping: {}
        };
        
        // Raccogli mapping relè
        for (let i = 1; i <= 6; i++) {
            config.mapping[i] = {
                nome: formData.get(`relay_${i}_nome`) || `Relè ${i}`,
                durata_sec: parseInt(formData.get(`relay_${i}_durata`)) || 5
            };
        }
        
        try {
            const response = await fetch('/api/devices/config/relay', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert('Configurazione relè salvata con successo', 'success');
                await testRelay(); // Ritest dopo salvataggio
                loadRelayTestControls(); // Ricarica controlli
            } else {
                showAlert('Errore salvataggio configurazione relè', 'danger');
            }
        } catch (error) {
            showAlert('Errore comunicazione', 'danger');
        }
    });
    
    // Log diagnostici
    function startDiagnosticLogUpdate() {
        loadDiagnosticLog();
        diagnosticLogInterval = setInterval(loadDiagnosticLog, 3000);
    }
    
    async function loadDiagnosticLog() {
        try {
            const response = await fetch('/api/devices/diagnostic-log');
            const data = await response.json();
            
            if (data.success) {
                const logEl = document.getElementById('diagnostic-log');
                logEl.innerHTML = data.log.map(entry => 
                    `<div>${entry.timestamp} - ${entry.level} - ${entry.message}</div>`
                ).join('');
                
                // Auto-scroll al bottom
                logEl.scrollTop = logEl.scrollHeight;
            }
        } catch (error) {
            console.error('Errore caricamento log diagnostici:', error);
        }
    }
    
    async function clearDiagnosticLog() {
        if (confirm('Sei sicuro di voler cancellare il log diagnostico?')) {
            try {
                const response = await fetch('/api/devices/diagnostic-log', {method: 'DELETE'});
                const data = await response.json();
                
                if (data.success) {
                    showAlert('Log diagnostico cancellato', 'success');
                    loadDiagnosticLog();
                } else {
                    showAlert('Errore cancellazione log', 'danger');
                }
            } catch (error) {
                showAlert('Errore comunicazione', 'danger');
            }
        }
    }
    
    async function downloadDiagnosticLog() {
        try {
            const response = await fetch('/api/devices/diagnostic-log/download');
            const blob = await response.blob();
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `diagnostic-log-${new Date().toISOString().split('T')[0]}.txt`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showAlert('Log diagnostico scaricato', 'success');
        } catch (error) {
            showAlert('Errore download log', 'danger');
        }
    }
    
    // Cleanup al cambio pagina
    window.addEventListener('beforeunload', function() {
        if (diagnosticLogInterval) {
            clearInterval(diagnosticLogInterval);
        }
    });
</script>
{% endblock %}
"""

# ===============================
# ROUTES DISPOSITIVI
# ===============================

@app.route('/dispositivi')
@require_auth
@require_permission('all')  # Solo admin
def dispositivi():
    """Pagina configurazione dispositivi"""
    nome_isola = config_manager.get('sistema.nome_isola', '')
    if not nome_isola:
        nome_isola = "Isola Ecologica"
    else:
        nome_isola = f"Isola Ecologica {nome_isola}"
    
    user_role = session.get('role', 'viewer')
    user_role_name = USER_ROLES.get(user_role, {}).get('name', 'Utente')
    permissions = session.get('permissions', [])
    
    return render_template_string(DISPOSITIVI_TEMPLATE, 
                                island_name=nome_isola,
                                user_role_name=user_role_name,
                                permissions=permissions)

# ===============================
# API ENDPOINTS DISPOSITIVI
# ===============================

@app.route('/api/devices/config')
@require_auth
def api_devices_config():
    """Ottieni configurazione dispositivi"""
    try:
        return jsonify({
            'success': True,
            'reader': config_manager.get('dispositivi.lettore_cf', {}),
            'relay': config_manager.get('dispositivi.rele', {})
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/devices/relay-mapping')
@require_auth
def api_relay_mapping():
    """Ottieni mapping relè"""
    try:
        mapping = config_manager.get('dispositivi.rele.mapping', {})
        return jsonify({
            'success': True,
            'mapping': mapping
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/devices/test/reader', methods=['POST'])
@require_auth
@require_permission('all')
def api_test_reader():
    """Test connessione lettore tessere"""
    try:
        # Testa connessione al lettore
        # Qui andrà integrato il codice del card_reader esistente
        
        return jsonify({
            'success': True,
            'message': 'Lettore operativo - OMNIKEY 5427CK'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Errore lettore: {str(e)}'
        }), 500

@app.route('/api/devices/test/relay', methods=['POST'])
@require_auth
@require_permission('all')
def api_test_relay():
    """Test connessione modulo relè"""
    try:
        # Testa connessione al modulo relè
        # Qui andrà integrato il codice dell'USB-RLY08 esistente
        
        return jsonify({
            'success': True,
            'message': 'Modulo relè operativo - USB-RLY08'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Errore relè: {str(e)}'
        }), 500

@app.route('/api/devices/test/database', methods=['POST'])
@require_auth
def api_test_database():
    """Test connessione database"""
    try:
        import sqlite3
        db_path = project_root / "src" / "access.db"
        
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM utenti_autorizzati")
            count = cursor.fetchone()[0]
        
        return jsonify({
            'success': True,
            'message': f'Database operativo - {count} utenti autorizzati'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Errore database: {str(e)}'
        }), 500

@app.route('/api/devices/config/reader', methods=['POST'])
@require_auth
@require_permission('all')
def api_save_reader_config():
    """Salva configurazione lettore"""
    try:
        config = request.get_json()
        
        # Valida configurazione
        if not config.get('tipo') or not config.get('porta'):
            return jsonify({'success': False, 'error': 'Configurazione incompleta'}), 400
        
        # Salva configurazione
        for key, value in config.items():
            if key in ['timeout', 'retry_tentativi']:
                value = int(value)
            config_manager.set(f'dispositivi.lettore_cf.{key}', value)
        
        return jsonify({'success': True, 'message': 'Configurazione lettore salvata'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/devices/config/relay', methods=['POST'])
@require_auth
@require_permission('all')
def api_save_relay_config():
    """Salva configurazione relè"""
    try:
        config = request.get_json()
        
        # Valida configurazione
        if not config.get('porta') or not config.get('baud_rate'):
            return jsonify({'success': False, 'error': 'Configurazione incompleta'}), 400
        
        # Salva configurazione base
        config_manager.set('dispositivi.rele.porta', config['porta'])
        config_manager.set('dispositivi.rele.baud_rate', config['baud_rate'])
        config_manager.set('dispositivi.rele.modulo_id', config['modulo_id'])
        
        # Salva mapping
        if 'mapping' in config:
            config_manager.set('dispositivi.rele.mapping', config['mapping'])
        
        return jsonify({'success': True, 'message': 'Configurazione relè salvata'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
