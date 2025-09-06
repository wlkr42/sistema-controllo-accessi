# File: /opt/access_control/src/api/admin_templates.py
# Template per le 3 pagine admin da aggiungere a dashboard_templates.py

# Template per Gestione Utenti Admin
ADMIN_USERS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Gestione Utenti - Sistema Controllo Accessi</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="/static/css/dashboard.css" rel="stylesheet">
    <link href="/static/css/user-menu.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-users-cog me-2"></i>Gestione Utenti Sistema
            </span>
            <div class="d-flex align-items-center gap-3">
                <a href="/" class="btn btn-outline-light btn-sm">
                    <i class="fas fa-arrow-left"></i> Torna alla Dashboard
                </a>
                <div id="user-menu-placeholder"></div>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <!-- Statistiche Utenti -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body text-center">
                        <i class="fas fa-crown fa-2x text-danger mb-3"></i>
                        <div class="stat-number text-danger" id="admin-count">-</div>
                        <h6 class="text-muted">Amministratori</h6>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body text-center">
                        <i class="fas fa-user-tie fa-2x text-primary mb-3"></i>
                        <div class="stat-number text-primary" id="manager-count">-</div>
                        <h6 class="text-muted">Gestori Utenti</h6>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body text-center">
                        <i class="fas fa-eye fa-2x text-success mb-3"></i>
                        <div class="stat-number text-success" id="viewer-count">-</div>
                        <h6 class="text-muted">Visualizzatori</h6>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body text-center">
                        <i class="fas fa-users fa-2x text-info mb-3"></i>
                        <div class="stat-number text-info" id="total-users">-</div>
                        <h6 class="text-muted">Totale</h6>
                    </div>
                </div>
            </div>
        </div>

        <!-- Gestione Utenti -->
        <div class="row">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-list me-2"></i>Lista Utenti Sistema</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Username</th>
                                        <th>Ruolo</th>
                                        <th>Ultimo Accesso</th>
                                        <th>Stato</th>
                                        <th>Azioni</th>
                                    </tr>
                                </thead>
                                <tbody id="users-table">
                                    <tr>
                                        <td colspan="5" class="text-center">
                                            <div class="spinner-border" role="status"></div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-user-plus me-2"></i>Nuovo Utente</h5>
                    </div>
                    <div class="card-body">
                        <form id="create-user-form">
                            <div class="mb-3">
                                <label class="form-label">Username</label>
                                <input type="text" class="form-control" id="new-username" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Password</label>
                                <input type="password" class="form-control" id="new-password" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Ruolo</label>
                                <select class="form-select" id="new-role">
                                    <option value="admin">👑 Amministratore</option>
                                    <option value="user_manager">👔 Gestore Utenti</option>
                                    <option value="viewer">👁️ Visualizzatore</option>
                                </select>
                            </div>
                            <button type="submit" class="btn btn-success w-100">
                                <i class="fas fa-plus"></i> Crea Utente
                            </button>
                        </form>
                    </div>
                </div>
                
                <div class="card mt-3">
                    <div class="card-header">
                        <h6><i class="fas fa-chart-line me-2"></i>Attività Recente</h6>
                    </div>
                    <div class="card-body">
                        <div id="recent-activity">
                            <small class="text-muted">Caricamento...</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/static/js/user-menu.js"></script>
    <script>
        // Carica menu utente
        fetch('/api/user-menu-html')
            .then(response => response.text())
            .then(html => {
                document.getElementById('user-menu-placeholder').innerHTML = html;
                new UserMenu();
            });
        
        // Carica dati utenti
        loadUsersData();
        
        function loadUsersData() {
            // Implementazione caricamento utenti
            console.log('Caricamento dati utenti...');
        }
    </script>
</body>
</html>
"""

# Template per Configurazioni Sistema
ADMIN_CONFIG_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Configurazioni Sistema - Sistema Controllo Accessi</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="/static/css/dashboard.css" rel="stylesheet">
    <link href="/static/css/user-menu.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-sliders-h me-2"></i>Configurazioni Sistema
            </span>
            <div class="d-flex align-items-center gap-3">
                <a href="/" class="btn btn-outline-light btn-sm">
                    <i class="fas fa-arrow-left"></i> Torna alla Dashboard
                </a>
                <div id="user-menu-placeholder"></div>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <!-- Tab Navigation -->
        <ul class="nav nav-tabs" role="tablist">
            <li class="nav-item">
                <a class="nav-link active" data-bs-toggle="tab" href="#sistema">
                    <i class="fas fa-cog"></i> Sistema
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" data-bs-toggle="tab" href="#hardware">
                    <i class="fas fa-microchip"></i> Hardware
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" data-bs-toggle="tab" href="#sicurezza">
                    <i class="fas fa-shield-alt"></i> Sicurezza
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" data-bs-toggle="tab" href="#email">
                    <i class="fas fa-envelope"></i> Email
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" data-bs-toggle="tab" href="#orologio">
                    <i class="fas fa-clock"></i> Orologio
                </a>
            </li>
        </ul>

        <!-- Tab Content -->
        <div class="tab-content mt-3">
            <!-- Sistema -->
            <div class="tab-pane fade show active" id="sistema">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-server me-2"></i>Configurazioni Sistema</h5>
                    </div>
                    <div class="card-body">
                        <form id="sistema-form">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Nome Installazione</label>
                                        <input type="text" class="form-control" id="nome-installazione" 
                                               value="Isola Ecologica RAEE - Rende">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Porta Web</label>
                                        <input type="number" class="form-control" id="porta-web" value="5000">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">
                                            <input type="checkbox" id="debug-mode"> Modalità Debug
                                        </label>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Timeout Sessione (secondi)</label>
                                        <input type="number" class="form-control" id="timeout-sessione" value="1800">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Ambiente</label>
                                        <select class="form-select" id="ambiente">
                                            <option value="production">Produzione</option>
                                            <option value="development">Sviluppo</option>
                                            <option value="testing">Test</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-success">
                                <i class="fas fa-save"></i> Salva Configurazioni Sistema
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- Hardware -->
            <div class="tab-pane fade" id="hardware">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-microchip me-2"></i>Configurazioni Hardware</h5>
                    </div>
                    <div class="card-body">
                        <form id="hardware-form">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Lettore Tessere</h6>
                                    <div class="mb-3">
                                        <label class="form-label">Porta Lettore</label>
                                        <input type="text" class="form-control" id="lettore-porta" value="/dev/ttyACM0">
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <h6>Controller USB-RLY08</h6>
                                    <div class="mb-3">
                                        <label class="form-label">Porta Relè</label>
                                        <input type="text" class="form-control" id="relay-porta" value="/dev/ttyUSB0">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Baud Rate</label>
                                        <select class="form-select" id="relay-baudrate">
                                            <option value="9600">9600</option>
                                            <option value="19200" selected>19200</option>
                                            <option value="38400">38400</option>
                                        </select>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Durata Apertura Cancello (sec)</label>
                                        <input type="number" class="form-control" id="gate-duration" value="8" min="1" max="30">
                                    </div>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-success">
                                <i class="fas fa-save"></i> Salva Configurazioni Hardware
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- Sicurezza -->
            <div class="tab-pane fade" id="sicurezza">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-shield-alt me-2"></i>Configurazioni Sicurezza</h5>
                    </div>
                    <div class="card-body">
                        <form id="sicurezza-form">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Max Tentativi Login</label>
                                        <input type="number" class="form-control" id="max-tentativi" value="5" min="3" max="10">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Durata Blocco (minuti)</label>
                                        <input type="number" class="form-control" id="durata-blocco" value="15" min="5" max="60">
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Rotazione Password (giorni)</label>
                                        <input type="number" class="form-control" id="rotazione-password" value="90" min="30" max="365">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">
                                            <input type="checkbox" id="log-audit" checked> Log Audit Abilitato
                                        </label>
                                    </div>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-success">
                                <i class="fas fa-save"></i> Salva Configurazioni Sicurezza
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- Email -->
            <div class="tab-pane fade" id="email">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-envelope me-2"></i>Configurazioni Email</h5>
                    </div>
                    <div class="card-body">
                        <form id="email-form">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Server SMTP</label>
                                        <input type="text" class="form-control" id="smtp-server" placeholder="smtp.gmail.com">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Porta SMTP</label>
                                        <select class="form-select" id="smtp-porta">
                                            <option value="25">25 (SMTP)</option>
                                            <option value="587" selected>587 (SMTP TLS)</option>
                                            <option value="465">465 (SMTP SSL)</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Email Mittente</label>
                                        <input type="email" class="form-control" id="email-mittente" placeholder="isola@comune.rende.cs.it">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">
                                            <input type="checkbox" id="report-automatici"> Report Automatici
                                        </label>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Frequenza Report</label>
                                        <select class="form-select" id="frequenza-report">
                                            <option value="daily">Giornaliero</option>
                                            <option value="weekly" selected>Settimanale</option>
                                            <option value="monthly">Mensile</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-success">
                                <i class="fas fa-save"></i> Salva Configurazioni Email
                            </button>
                        </form>
                    </div>
                </div>
            </div>
            
            <!-- Orologio -->
            <div class="tab-pane fade" id="orologio">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-clock me-2"></i>Configurazioni Orologio</h5>
                    </div>
                    <div class="card-body">
                        <form id="orologio-form">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Fuso Orario</label>
                                        <select class="form-select" id="timezone">
                                            <option value="UTC">UTC (Coordinated Universal Time)</option>
                                            <option value="Europe/Rome" selected>Europe/Rome (Italia)</option>
                                            <option value="Europe/London">Europe/London (UK)</option>
                                            <option value="Europe/Paris">Europe/Paris (Francia)</option>
                                            <option value="Europe/Berlin">Europe/Berlin (Germania)</option>
                                            <option value="America/New_York">America/New_York (US Eastern)</option>
                                            <option value="America/Chicago">America/Chicago (US Central)</option>
                                            <option value="America/Los_Angeles">America/Los_Angeles (US Pacific)</option>
                                        </select>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Formato Data</label>
                                        <select class="form-select" id="formato-data">
                                            <option value="DD/MM/YYYY" selected>DD/MM/YYYY</option>
                                            <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                                            <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                                        </select>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Formato Ora</label>
                                        <select class="form-select" id="formato-ora">
                                            <option value="24" selected>24 ore (00:00 - 23:59)</option>
                                            <option value="12">12 ore (AM/PM)</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Sincronizzazione NTP</label>
                                        <div class="form-check">
                                            <input type="checkbox" class="form-check-input" id="ntp-enabled" checked>
                                            <label class="form-check-label" for="ntp-enabled">
                                                Abilita sincronizzazione automatica
                                            </label>
                                        </div>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Server NTP</label>
                                        <input type="text" class="form-control" id="ntp-server" 
                                               value="pool.ntp.org" placeholder="pool.ntp.org">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Ora Corrente del Sistema</label>
                                        <div class="alert alert-info">
                                            <i class="fas fa-clock me-2"></i>
                                            <span id="system-time">--:--:--</span>
                                            <small class="d-block text-muted mt-1">Timezone: <span id="current-timezone">Europe/Rome</span></small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-success">
                                <i class="fas fa-save"></i> Salva Configurazioni Orologio
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <!-- Azioni Sistema -->
        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card border-warning">
                    <div class="card-header bg-warning text-dark">
                        <h5><i class="fas fa-exclamation-triangle me-2"></i>Azioni Sistema</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <button class="btn btn-warning w-100" onclick="restartSystem()">
                                    <i class="fas fa-redo"></i> Riavvia Sistema
                                </button>
                            </div>
                            <div class="col-md-4">
                                <button class="btn btn-info w-100" onclick="exportConfig()">
                                    <i class="fas fa-download"></i> Esporta Configurazioni
                                </button>
                            </div>
                            <div class="col-md-4">
                                <button class="btn btn-secondary w-100" onclick="resetToDefaults()">
                                    <i class="fas fa-undo"></i> Ripristina Default
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/static/js/user-menu.js"></script>
    <script>
        // Carica menu utente
        fetch('/api/user-menu-html')
            .then(response => response.text())
            .then(html => {
                document.getElementById('user-menu-placeholder').innerHTML = html;
                new UserMenu();
            });
        
        // Carica configurazioni
        loadSystemConfig();
        
        function loadSystemConfig() {
            fetch('/api/system/config')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Popola i form con i dati
                        console.log('Configurazioni caricate:', data.config);
                    }
                });
        }
        
        function restartSystem() {
            if (confirm('Sei sicuro di voler riavviare il sistema?')) {
                fetch('/api/system/restart', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('Sistema in riavvio...');
                        }
                    });
            }
        }
        
        function exportConfig() {
            alert('Funzionalità export configurazioni da implementare');
        }
        
        function resetToDefaults() {
            if (confirm('Ripristinare tutte le configurazioni ai valori default?')) {
                alert('Funzionalità reset da implementare');
            }
        }
        
        // Gestione Orologio
        function updateSystemTime() {
            fetch('/api/server-time')
                .then(response => response.json())
                .then(data => {
                    const date = new Date(data.timestamp);
                    const timeStr = date.toLocaleTimeString('it-IT');
                    const dateStr = date.toLocaleDateString('it-IT');
                    document.getElementById('system-time').textContent = `${dateStr} ${timeStr}`;
                    document.getElementById('current-timezone').textContent = data.timezone || 'Europe/Rome';
                })
                .catch(err => console.error('Errore aggiornamento ora:', err));
        }
        
        // Aggiorna ora ogni secondo
        updateSystemTime();
        setInterval(updateSystemTime, 1000);
        
        // Gestione form orologio
        document.getElementById('orologio-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                timezone: document.getElementById('timezone').value,
                formato_data: document.getElementById('formato-data').value,
                formato_ora: document.getElementById('formato-ora').value,
                ntp_enabled: document.getElementById('ntp-enabled').checked,
                ntp_server: document.getElementById('ntp-server').value
            };
            
            fetch('/api/admin/clock-config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Configurazioni orologio salvate con successo!');
                    // Ricarica la pagina per applicare le nuove impostazioni
                    setTimeout(() => location.reload(), 1000);
                } else {
                    alert('Errore nel salvataggio: ' + (data.error || 'Errore sconosciuto'));
                }
            })
            .catch(err => {
                console.error('Errore:', err);
                alert('Errore nel salvataggio delle configurazioni');
            });
        });
        
        // Carica configurazioni orologio correnti
        function loadClockConfig() {
            fetch('/api/admin/clock-config')
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.config) {
                        document.getElementById('timezone').value = data.config.timezone || 'Europe/Rome';
                        document.getElementById('formato-data').value = data.config.formato_data || 'DD/MM/YYYY';
                        document.getElementById('formato-ora').value = data.config.formato_ora || '24';
                        document.getElementById('ntp-enabled').checked = data.config.ntp_enabled !== false;
                        document.getElementById('ntp-server').value = data.config.ntp_server || 'pool.ntp.org';
                    }
                })
                .catch(err => console.error('Errore caricamento config orologio:', err));
        }
        
        // Carica configurazioni all'avvio
        loadClockConfig();
    </script>
</body>
</html>
"""

# Template per Backup & Restore
ADMIN_BACKUP_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Backup & Restore - Sistema Controllo Accessi</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="/static/css/dashboard.css" rel="stylesheet">
    <link href="/static/css/user-menu.css" rel="stylesheet">
    <style>
        .nav-tabs .nav-link { color: #495057; }
        .nav-tabs .nav-link.active { color: #0d6efd; font-weight: 500; }
        .schedule-card { border-left: 4px solid #0d6efd; }
        .schedule-card.disabled { border-left-color: #6c757d; opacity: 0.6; }
        .cloud-provider-card { cursor: pointer; transition: all 0.3s; }
        .cloud-provider-card:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        .cloud-provider-card.selected { border-color: #0d6efd; background: #f0f8ff; }
        .integrity-status { padding: 10px; border-radius: 5px; }
        .integrity-status.success { background: #d4edda; color: #155724; }
        .integrity-status.warning { background: #fff3cd; color: #856404; }
        .integrity-status.danger { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-database me-2"></i>Backup & Restore Sistema
            </span>
            <div class="d-flex align-items-center gap-3">
                <a href="/" class="btn btn-outline-light btn-sm">
                    <i class="fas fa-arrow-left"></i> Torna alla Dashboard
                </a>
                <div id="user-menu-placeholder"></div>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <!-- Statistiche Backup -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body text-center">
                        <i class="fas fa-archive fa-2x text-primary mb-3"></i>
                        <div class="stat-number text-primary" id="total-backups">-</div>
                        <h6 class="text-muted">Backup Totali</h6>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body text-center">
                        <i class="fas fa-hdd fa-2x text-success mb-3"></i>
                        <div class="stat-number text-success" id="total-size">-</div>
                        <h6 class="text-muted">Spazio Utilizzato</h6>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body text-center">
                        <i class="fas fa-clock fa-2x text-warning mb-3"></i>
                        <div class="stat-number text-warning" id="last-backup">-</div>
                        <h6 class="text-muted">Ultimo Backup</h6>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body text-center">
                        <i class="fas fa-chart-pie fa-2x text-info mb-3"></i>
                        <div class="stat-number text-info" id="disk-usage">-</div>
                        <h6 class="text-muted">Disco Utilizzato</h6>
                    </div>
                </div>
            </div>
        </div>

        <!-- Azioni Backup -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-plus-circle me-2"></i>Crea Nuovo Backup</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <button class="btn btn-primary w-100 mb-2" onclick="createBackup('complete')">
                                    <i class="fas fa-archive"></i><br>Backup Completo
                                    <small class="d-block">Sistema + Database + Config</small>
                                </button>
                            </div>
                            <div class="col-md-6">
                                <button class="btn btn-success w-100 mb-2" onclick="createBackup('database')">
                                    <i class="fas fa-database"></i><br>Solo Database
                                    <small class="d-block">Backup rapido DB</small>
                                </button>
                            </div>
                        </div>
                        <button class="btn btn-warning w-100" onclick="cleanupBackups()">
                            <i class="fas fa-broom"></i> Pulizia Backup Vecchi
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-cog me-2"></i>Configurazione Automatica</h5>
                    </div>
                    <div class="card-body">
                        <!-- Tabs per schedulazione -->
                        <ul class="nav nav-tabs mb-3" role="tablist">
                            <li class="nav-item">
                                <a class="nav-link active" data-bs-toggle="tab" href="#daily-schedule">Giornaliero</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" data-bs-toggle="tab" href="#weekly-schedule">Settimanale</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" data-bs-toggle="tab" href="#monthly-schedule">Mensile</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" data-bs-toggle="tab" href="#yearly-schedule">Annuale</a>
                            </li>
                        </ul>
                        
                        <div class="tab-content">
                            <!-- Giornaliero -->
                            <div class="tab-pane fade show active" id="daily-schedule">
                                <div class="schedule-card card mb-3">
                                    <div class="card-body">
                                        <div class="form-check mb-2">
                                            <input type="checkbox" class="form-check-input" id="daily-enabled" checked>
                                            <label class="form-check-label" for="daily-enabled">
                                                <strong>Abilita Backup Giornaliero</strong>
                                            </label>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-6">
                                                <label class="form-label">Ora</label>
                                                <input type="time" class="form-control" id="daily-time" value="02:00">
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label">Tipo</label>
                                                <select class="form-select" id="daily-type">
                                                    <option value="database" selected>Solo Database</option>
                                                    <option value="complete">Completo</option>
                                                </select>
                                            </div>
                                        </div>
                                        <div class="mt-2">
                                            <label class="form-label">Retention</label>
                                            <input type="number" class="form-control" id="daily-retention" value="7" min="1" max="365">
                                            <small class="text-muted">Mantieni per giorni</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Settimanale -->
                            <div class="tab-pane fade" id="weekly-schedule">
                                <div class="schedule-card card mb-3">
                                    <div class="card-body">
                                        <div class="form-check mb-2">
                                            <input type="checkbox" class="form-check-input" id="weekly-enabled" checked>
                                            <label class="form-check-label" for="weekly-enabled">
                                                <strong>Abilita Backup Settimanale</strong>
                                            </label>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-4">
                                                <label class="form-label">Giorno</label>
                                                <select class="form-select" id="weekly-day">
                                                    <option value="0" selected>Domenica</option>
                                                    <option value="1">Lunedì</option>
                                                    <option value="2">Martedì</option>
                                                    <option value="3">Mercoledì</option>
                                                    <option value="4">Giovedì</option>
                                                    <option value="5">Venerdì</option>
                                                    <option value="6">Sabato</option>
                                                </select>
                                            </div>
                                            <div class="col-md-4">
                                                <label class="form-label">Ora</label>
                                                <input type="time" class="form-control" id="weekly-time" value="03:00">
                                            </div>
                                            <div class="col-md-4">
                                                <label class="form-label">Tipo</label>
                                                <select class="form-select" id="weekly-type">
                                                    <option value="database">Solo Database</option>
                                                    <option value="complete" selected>Completo</option>
                                                </select>
                                            </div>
                                        </div>
                                        <div class="mt-2">
                                            <label class="form-label">Retention</label>
                                            <input type="number" class="form-control" id="weekly-retention" value="4" min="1" max="52">
                                            <small class="text-muted">Mantieni per settimane</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Mensile -->
                            <div class="tab-pane fade" id="monthly-schedule">
                                <div class="schedule-card card mb-3">
                                    <div class="card-body">
                                        <div class="form-check mb-2">
                                            <input type="checkbox" class="form-check-input" id="monthly-enabled" checked>
                                            <label class="form-check-label" for="monthly-enabled">
                                                <strong>Abilita Backup Mensile</strong>
                                            </label>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-4">
                                                <label class="form-label">Giorno del mese</label>
                                                <input type="number" class="form-control" id="monthly-day" value="1" min="1" max="28">
                                            </div>
                                            <div class="col-md-4">
                                                <label class="form-label">Ora</label>
                                                <input type="time" class="form-control" id="monthly-time" value="04:00">
                                            </div>
                                            <div class="col-md-4">
                                                <label class="form-label">Tipo</label>
                                                <select class="form-select" id="monthly-type">
                                                    <option value="database">Solo Database</option>
                                                    <option value="complete" selected>Completo</option>
                                                </select>
                                            </div>
                                        </div>
                                        <div class="mt-2">
                                            <label class="form-label">Retention</label>
                                            <input type="number" class="form-control" id="monthly-retention" value="6" min="1" max="24">
                                            <small class="text-muted">Mantieni per mesi</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Annuale -->
                            <div class="tab-pane fade" id="yearly-schedule">
                                <div class="schedule-card card mb-3">
                                    <div class="card-body">
                                        <div class="form-check mb-2">
                                            <input type="checkbox" class="form-check-input" id="yearly-enabled">
                                            <label class="form-check-label" for="yearly-enabled">
                                                <strong>Abilita Backup Annuale</strong>
                                            </label>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-3">
                                                <label class="form-label">Mese</label>
                                                <select class="form-select" id="yearly-month">
                                                    <option value="1" selected>Gennaio</option>
                                                    <option value="2">Febbraio</option>
                                                    <option value="3">Marzo</option>
                                                    <option value="4">Aprile</option>
                                                    <option value="5">Maggio</option>
                                                    <option value="6">Giugno</option>
                                                    <option value="7">Luglio</option>
                                                    <option value="8">Agosto</option>
                                                    <option value="9">Settembre</option>
                                                    <option value="10">Ottobre</option>
                                                    <option value="11">Novembre</option>
                                                    <option value="12">Dicembre</option>
                                                </select>
                                            </div>
                                            <div class="col-md-3">
                                                <label class="form-label">Giorno</label>
                                                <input type="number" class="form-control" id="yearly-day" value="1" min="1" max="28">
                                            </div>
                                            <div class="col-md-3">
                                                <label class="form-label">Ora</label>
                                                <input type="time" class="form-control" id="yearly-time" value="05:00">
                                            </div>
                                            <div class="col-md-3">
                                                <label class="form-label">Tipo</label>
                                                <select class="form-select" id="yearly-type">
                                                    <option value="complete" selected>Completo</option>
                                                </select>
                                            </div>
                                        </div>
                                        <div class="mt-2">
                                            <label class="form-label">Retention</label>
                                            <input type="number" class="form-control" id="yearly-retention" value="3" min="1" max="10">
                                            <small class="text-muted">Mantieni per anni</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                            <button type="button" class="btn btn-success w-100" onclick="saveBackupSchedule()">
                                <i class="fas fa-save"></i> Salva Configurazione Schedulazione
                            </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Cloud Backup -->
        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-cloud me-2"></i>Backup Cloud</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-3">
                                <div class="cloud-provider-card card text-center p-3" data-provider="none">
                                    <i class="fas fa-times-circle fa-3x text-muted mb-2"></i>
                                    <h6>Nessuno</h6>
                                    <small class="text-muted">Backup solo locale</small>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="cloud-provider-card card text-center p-3" data-provider="aws">
                                    <i class="fab fa-aws fa-3x text-warning mb-2"></i>
                                    <h6>Amazon S3</h6>
                                    <small class="text-muted">Storage AWS</small>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="cloud-provider-card card text-center p-3" data-provider="google">
                                    <i class="fab fa-google fa-3x text-primary mb-2"></i>
                                    <h6>Google Cloud</h6>
                                    <small class="text-muted">GCS Bucket</small>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="cloud-provider-card card text-center p-3" data-provider="ftp">
                                    <i class="fas fa-server fa-3x text-success mb-2"></i>
                                    <h6>FTP/SFTP</h6>
                                    <small class="text-muted">Server remoto</small>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Configurazione Provider -->
                        <div id="cloud-config" class="mt-3" style="display: none;">
                            <hr>
                            <h6>Configurazione <span id="selected-provider"></span></h6>
                            
                            <!-- FTP Config -->
                            <div id="ftp-config" class="provider-config" style="display: none;">
                                <div class="row">
                                    <div class="col-md-6">
                                        <label class="form-label">Host</label>
                                        <input type="text" class="form-control" id="ftp-host" placeholder="ftp.esempio.com">
                                    </div>
                                    <div class="col-md-2">
                                        <label class="form-label">Porta</label>
                                        <input type="number" class="form-control" id="ftp-port" value="21">
                                    </div>
                                    <div class="col-md-4">
                                        <label class="form-label">Percorso</label>
                                        <input type="text" class="form-control" id="ftp-path" value="/backups">
                                    </div>
                                </div>
                                <div class="row mt-2">
                                    <div class="col-md-6">
                                        <label class="form-label">Username</label>
                                        <input type="text" class="form-control" id="ftp-username">
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">Password</label>
                                        <input type="password" class="form-control" id="ftp-password">
                                    </div>
                                </div>
                            </div>
                            
                            <!-- AWS Config -->
                            <div id="aws-config" class="provider-config" style="display: none;">
                                <div class="row">
                                    <div class="col-md-6">
                                        <label class="form-label">Access Key</label>
                                        <input type="text" class="form-control" id="aws-access-key">
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">Secret Key</label>
                                        <input type="password" class="form-control" id="aws-secret-key">
                                    </div>
                                </div>
                                <div class="row mt-2">
                                    <div class="col-md-6">
                                        <label class="form-label">Bucket</label>
                                        <input type="text" class="form-control" id="aws-bucket">
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">Region</label>
                                        <select class="form-select" id="aws-region">
                                            <option value="eu-west-1">EU (Ireland)</option>
                                            <option value="eu-central-1">EU (Frankfurt)</option>
                                            <option value="us-east-1">US East (N. Virginia)</option>
                                            <option value="us-west-2">US West (Oregon)</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="mt-3">
                                <div class="form-check">
                                    <input type="checkbox" class="form-check-input" id="cloud-auto-sync">
                                    <label class="form-check-label" for="cloud-auto-sync">
                                        Sincronizza automaticamente dopo ogni backup
                                    </label>
                                </div>
                                <button class="btn btn-primary mt-2" onclick="saveCloudConfig()">
                                    <i class="fas fa-save"></i> Salva Configurazione Cloud
                                </button>
                                <button class="btn btn-success mt-2" onclick="syncToCloud()">
                                    <i class="fas fa-cloud-upload-alt"></i> Sincronizza Ora
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Verifica Integrità -->
        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-shield-alt me-2"></i>Verifica Integrità</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Configurazione Verifica Automatica</h6>
                                <div class="form-check mb-2">
                                    <input type="checkbox" class="form-check-input" id="integrity-enabled" checked>
                                    <label class="form-check-label" for="integrity-enabled">
                                        Abilita verifica integrità periodica
                                    </label>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <label class="form-label">Frequenza</label>
                                        <select class="form-select" id="integrity-schedule">
                                            <option value="daily" selected>Giornaliera</option>
                                            <option value="weekly">Settimanale</option>
                                            <option value="monthly">Mensile</option>
                                        </select>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">Ora</label>
                                        <input type="time" class="form-control" id="integrity-time" value="06:00">
                                    </div>
                                </div>
                                <div class="form-check mt-2">
                                    <input type="checkbox" class="form-check-input" id="integrity-alert" checked>
                                    <label class="form-check-label" for="integrity-alert">
                                        Invia alert in caso di errori
                                    </label>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <h6>Ultimo Controllo</h6>
                                <div id="integrity-status" class="integrity-status success">
                                    <i class="fas fa-check-circle"></i> Tutti i backup sono integri
                                    <small class="d-block mt-1">Ultimo controllo: <span id="last-check">Mai</span></small>
                                </div>
                                <div class="mt-3">
                                    <button class="btn btn-primary" onclick="checkIntegrity()">
                                        <i class="fas fa-shield-alt"></i> Verifica Ora
                                    </button>
                                    <button class="btn btn-warning" onclick="applyRetention()">
                                        <i class="fas fa-broom"></i> Applica Retention
                                    </button>
                                </div>
                                <div id="integrity-results" class="mt-3" style="display: none;">
                                    <small class="text-muted">
                                        Validi: <span id="valid-count">0</span> |
                                        Corrotti: <span id="corrupted-count">0</span> |
                                        Senza checksum: <span id="missing-count">0</span>
                                    </small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Lista Backup -->
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-list me-2"></i>Lista Backup Disponibili</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Nome File</th>
                                        <th>Tipo</th>
                                        <th>Dimensione</th>
                                        <th>Data Creazione</th>
                                        <th>Età</th>
                                        <th>Checksum</th>
                                        <th>Azioni</th>
                                    </tr>
                                </thead>
                                <tbody id="backups-table">
                                    <tr>
                                        <td colspan="7" class="text-center">
                                            <div class="spinner-border" role="status"></div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Operazioni in Corso -->
        <div id="backup-operations" class="row mt-4" style="display: none;">
            <div class="col-md-12">
                <div class="card border-info">
                    <div class="card-header bg-info text-white">
                        <h6><i class="fas fa-spinner fa-spin me-2"></i>Operazioni in Corso</h6>
                    </div>
                    <div class="card-body" id="operations-list">
                        <!-- Popolato dinamicamente -->
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/static/js/user-menu.js"></script>
    <script src="/static/js/backup.js"></script>
    <script>
        // Carica menu utente
        fetch('/api/user-menu-html')
            .then(response => response.text())
            .then(html => {
                document.getElementById('user-menu-placeholder').innerHTML = html;
                new UserMenu();
            });
        
        // Carica stato backup
        loadBackupStatus();
        
        // Polling per operazioni in corso
        setInterval(checkBackupOperations, 3000);
        
        function loadBackupStatus() {
            fetch('/api/backup/status')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('total-backups').textContent = data.total_backups || '0';
                        document.getElementById('total-size').textContent = data.total_size || '-';
                        document.getElementById('last-backup').textContent = data.last_backup || 'Mai';
                        document.getElementById('disk-usage').textContent = data.disk_used_percent + '%' || '-';
                        
                        renderBackupsTable(data.backups);
                    }
                });
        }
        
        function renderBackupsTable(backups) {
            const tbody = document.getElementById('backups-table');
            if (!backups || backups.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Nessun backup trovato</td></tr>';
                return;
            }
            
            let html = '';
            backups.forEach(backup => {
                html += `
                    <tr>
                        <td><i class="fas fa-${backup.type === 'complete' ? 'archive' : 'database'} me-2"></i>${backup.name}</td>
                        <td><span class="badge bg-${backup.type === 'complete' ? 'primary' : 'success'}">${backup.type === 'complete' ? 'Completo' : 'Database'}</span></td>
                        <td>${backup.size}</td>
                        <td>${new Date(backup.date).toLocaleString('it-IT')}</td>
                        <td>${backup.age_days} giorni</td>
                        <td>${backup.has_checksum ? '<i class="fas fa-check-circle text-success"></i>' : '-'}</td>
                        <td>
                            <button class="btn btn-sm btn-primary" onclick="downloadBackup('${backup.name}')">
                                <i class="fas fa-download"></i>
                            </button>
                            ${backup.can_restore ? `
                                <button class="btn btn-sm btn-success" onclick="restoreBackup('${backup.name}')">
                                    <i class="fas fa-undo"></i>
                                </button>
                            ` : ''}
                            <button class="btn btn-sm btn-danger" onclick="deleteBackup('${backup.name}')">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                `;
            });
            tbody.innerHTML = html;
        }
        
        function createBackup(type) {
            fetch('/api/backup/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({type: type})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('Backup avviato', 'success');
                    // Il polling aggiornerà automaticamente lo stato
                } else {
                    showAlert('Errore: ' + data.error, 'danger');
                }
            });
        }
        
        function cleanupBackups() {
            if (confirm('Eliminare i backup vecchi secondo la policy di retention?')) {
                fetch('/api/backup/cleanup', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showAlert('Pulizia completata', 'success');
                            loadBackupStatus();
                        }
                    });
            }
        }
        
        function downloadBackup(filename) {
            window.location.href = `/api/backup/download/${encodeURIComponent(filename)}`;
        }
        
        function deleteBackup(filename) {
            if (confirm(`Eliminare il backup ${filename}?`)) {
                fetch(`/api/backup/delete/${encodeURIComponent(filename)}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        showAlert('Backup eliminato con successo', 'success');
                        loadBackupStatus();
                    } else {
                        showAlert(`Errore eliminazione: ${data.error || 'Errore sconosciuto'}`, 'danger');
                    }
                })
                .catch(error => {
                    console.error('Errore:', error);
                    showAlert(`Errore di rete: ${error.message}`, 'danger');
                });
            }
        }
        
        function restoreBackup(filename) {
            if (confirm(`ATTENZIONE: Il ripristino sovrascriverà la configurazione attuale.\\n\\nVuoi ripristinare il backup ${filename}?`)) {
                fetch(`/api/backup/restore/${encodeURIComponent(filename)}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        alert('Ripristino completato. Il sistema verrà riavviato...');
                        setTimeout(() => window.location.reload(), 3000);
                    } else {
                        showAlert(`Errore ripristino: ${data.error || 'Errore sconosciuto'}`, 'danger');
                    }
                })
                .catch(error => {
                    console.error('Errore:', error);
                    showAlert(`Errore di rete: ${error.message}`, 'danger');
                });
            }
        }
        
        function checkBackupOperations() {
            // Implementazione controllo operazioni in corso
        }
        
        function showAlert(message, type) {
            // Implementazione notifiche
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
            alertDiv.style.zIndex = '9999';
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.body.appendChild(alertDiv);
            setTimeout(() => alertDiv.remove(), 5000);
        }
        
        // Funzioni Cloud Backup
        document.querySelectorAll('.cloud-provider-card').forEach(card => {
            card.addEventListener('click', function() {
                document.querySelectorAll('.cloud-provider-card').forEach(c => c.classList.remove('selected'));
                this.classList.add('selected');
                
                const provider = this.dataset.provider;
                document.getElementById('selected-provider').textContent = this.querySelector('h6').textContent;
                
                // Nascondi tutte le configurazioni
                document.querySelectorAll('.provider-config').forEach(c => c.style.display = 'none');
                
                if (provider === 'none') {
                    document.getElementById('cloud-config').style.display = 'none';
                } else {
                    document.getElementById('cloud-config').style.display = 'block';
                    if (document.getElementById(`${provider}-config`)) {
                        document.getElementById(`${provider}-config`).style.display = 'block';
                    }
                }
            });
        });
        
        function saveCloudConfig() {
            const selectedProvider = document.querySelector('.cloud-provider-card.selected')?.dataset.provider;
            if (!selectedProvider) {
                showAlert('Seleziona un provider cloud', 'warning');
                return;
            }
            
            const config = {
                cloud_backup: {
                    enabled: selectedProvider !== 'none',
                    provider: selectedProvider,
                    auto_sync: document.getElementById('cloud-auto-sync').checked,
                    credentials: {}
                }
            };
            
            // Raccogli credenziali in base al provider
            if (selectedProvider === 'ftp') {
                config.cloud_backup.credentials.ftp = {
                    host: document.getElementById('ftp-host').value,
                    port: parseInt(document.getElementById('ftp-port').value),
                    username: document.getElementById('ftp-username').value,
                    password: document.getElementById('ftp-password').value,
                    path: document.getElementById('ftp-path').value
                };
            } else if (selectedProvider === 'aws') {
                config.cloud_backup.credentials.aws = {
                    access_key: document.getElementById('aws-access-key').value,
                    secret_key: document.getElementById('aws-secret-key').value,
                    bucket: document.getElementById('aws-bucket').value,
                    region: document.getElementById('aws-region').value
                };
            }
            
            fetch('/api/backup/config', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('Configurazione cloud salvata', 'success');
                } else {
                    showAlert(`Errore: ${data.error}`, 'danger');
                }
            });
        }
        
        function syncToCloud() {
            fetch('/api/backup/cloud/sync', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showAlert('Sincronizzazione cloud avviata', 'info');
                    } else {
                        showAlert(`Errore: ${data.error}`, 'danger');
                    }
                });
        }
        
        // Funzioni Integrità
        function checkIntegrity() {
            fetch('/api/backup/integrity/check', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showAlert('Verifica integrità avviata', 'info');
                        // Polling per risultati
                        setTimeout(() => loadIntegrityResults(data.operation_id), 2000);
                    } else {
                        showAlert(`Errore: ${data.error}`, 'danger');
                    }
                });
        }
        
        function loadIntegrityResults(operationId) {
            fetch('/api/backup/status')
                .then(response => response.json())
                .then(data => {
                    if (data.operations && data.operations[operationId]) {
                        const op = data.operations[operationId];
                        if (op.status === 'completed') {
                            const result = op.result;
                            document.getElementById('valid-count').textContent = result.valid || 0;
                            document.getElementById('corrupted-count').textContent = result.corrupted || 0;
                            document.getElementById('missing-count').textContent = result.missing_checksum || 0;
                            document.getElementById('integrity-results').style.display = 'block';
                            
                            // Aggiorna status
                            const statusDiv = document.getElementById('integrity-status');
                            if (result.corrupted > 0) {
                                statusDiv.className = 'integrity-status danger';
                                statusDiv.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Trovati backup corrotti!';
                            } else if (result.missing_checksum > 0) {
                                statusDiv.className = 'integrity-status warning';
                                statusDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> Alcuni backup senza checksum';
                            } else {
                                statusDiv.className = 'integrity-status success';
                                statusDiv.innerHTML = '<i class="fas fa-check-circle"></i> Tutti i backup sono integri';
                            }
                            
                            document.getElementById('last-check').textContent = new Date().toLocaleString('it-IT');
                        } else if (op.status === 'running') {
                            // Continua polling
                            setTimeout(() => loadIntegrityResults(operationId), 2000);
                        }
                    }
                });
        }
        
        function applyRetention() {
            if (confirm('Applicare le politiche di retention? I backup vecchi verranno eliminati.')) {
                fetch('/api/backup/retention/apply', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showAlert(`Retention applicata: ${data.result.cleaned_files} file eliminati, ${data.result.freed_space} liberati`, 'success');
                            loadBackupStatus();
                        } else {
                            showAlert(`Errore: ${data.error}`, 'danger');
                        }
                    });
            }
        }
        
        // Salvataggio configurazione schedulazione
        function saveBackupSchedule() {
            const config = {
                auto_backup: {
                    enabled: true,
                    daily: {
                        enabled: document.getElementById('daily-enabled').checked,
                        time: document.getElementById('daily-time').value,
                        type: document.getElementById('daily-type').value,
                        retention_days: parseInt(document.getElementById('daily-retention').value)
                    },
                    weekly: {
                        enabled: document.getElementById('weekly-enabled').checked,
                        time: document.getElementById('weekly-time').value,
                        day: document.getElementById('weekly-day').value,
                        type: document.getElementById('weekly-type').value,
                        retention_weeks: parseInt(document.getElementById('weekly-retention').value)
                    },
                    monthly: {
                        enabled: document.getElementById('monthly-enabled').checked,
                        time: document.getElementById('monthly-time').value,
                        day: document.getElementById('monthly-day').value,
                        type: document.getElementById('monthly-type').value,
                        retention_months: parseInt(document.getElementById('monthly-retention').value)
                    },
                    yearly: {
                        enabled: document.getElementById('yearly-enabled').checked,
                        time: document.getElementById('yearly-time').value,
                        month: document.getElementById('yearly-month').value,
                        day: document.getElementById('yearly-day').value,
                        type: document.getElementById('yearly-type').value,
                        retention_years: parseInt(document.getElementById('yearly-retention').value)
                    }
                }
            };
            
            fetch('/api/backup/config', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('Schedulazione backup salvata', 'success');
                } else {
                    showAlert(`Errore: ${data.error}`, 'danger');
                }
            });
        }
    </script>
</body>
</html>
"""
