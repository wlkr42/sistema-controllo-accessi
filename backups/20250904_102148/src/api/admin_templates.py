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
                        <form id="backup-config-form">
                            <div class="mb-3">
                                <label class="form-label">
                                    <input type="checkbox" id="auto-backup-enabled"> Backup Automatici
                                </label>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Frequenza</label>
                                <select class="form-select" id="backup-frequency">
                                    <option value="daily">Giornaliero</option>
                                    <option value="weekly" selected>Settimanale</option>
                                    <option value="monthly">Mensile</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Mantieni per</label>
                                <select class="form-select" id="backup-retention">
                                    <option value="7">7 giorni</option>
                                    <option value="30" selected>30 giorni</option>
                                    <option value="90">90 giorni</option>
                                </select>
                            </div>
                            <button type="submit" class="btn btn-success w-100">
                                <i class="fas fa-save"></i> Salva Configurazione
                            </button>
                        </form>
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
                fetch(`/api/backup/delete/${encodeURIComponent(filename)}`, {method: 'DELETE'})
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showAlert('Backup eliminato', 'success');
                            loadBackupStatus();
                        }
                    });
            }
        }
        
        function restoreBackup(filename) {
            if (confirm(`ATTENZIONE: Il ripristino sovrascriverà la configurazione attuale.\\n\\nVuoi ripristinare il backup ${filename}?`)) {
                fetch(`/api/backup/restore/${encodeURIComponent(filename)}`, {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('Ripristino completato. Il sistema verrà riavviato...');
                            setTimeout(() => window.location.reload(), 3000);
                        }
                    });
            }
        }
        
        function checkBackupOperations() {
            // Implementazione controllo operazioni in corso
        }
        
        function showAlert(message, type) {
            // Implementazione notifiche
            console.log(`${type}: ${message}`);
        }
    </script>
</body>
</html>
"""
