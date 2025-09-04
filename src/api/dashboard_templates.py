# File: /opt/access_control/src/api/dashboard_templates.py
# Template HTML per dashboard web


LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sistema Controllo Accessi - Login</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .login-container { max-width: 400px; margin: 0 auto; padding-top: 100px; }
        .card { border: none; border-radius: 15px; box-shadow: 0 8px 30px rgba(0,0,0,0.1); }
        .role-info { 
            background: #f8f9fa; 
            border-radius: 10px; 
            padding: 15px; 
            margin-top: 20px;
        }
        .role-badge { 
            display: inline-block; 
            padding: 4px 8px; 
            border-radius: 4px; 
            font-size: 0.8rem;
            font-weight: bold;
        }
        .role-admin { background: #dc3545; color: white; }
        .role-manager { background: #0d6efd; color: white; }
        .role-viewer { background: #198754; color: white; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="card">
            <div class="card-body p-5">
                <div class="text-center mb-4">
                    <i class="fas fa-shield-alt fa-3x text-primary mb-3"></i>
                    <h4>Sistema Controllo Accessi</h4>
                    <p class="text-muted">Isola Ecologica RAEE - Rende</p>
                </div>
                
                {% if error %}
                <div class="alert alert-danger">{{ error }}</div>
                {% endif %}
                
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label">Username</label>
                        <input type="text" class="form-control" name="username" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Password</label>
                        <input type="password" class="form-control" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">
                        <i class="fas fa-sign-in-alt me-2"></i>Accedi
                    </button>
                </form>
                
                <div class="role-info">
                    <h6 class="text-center mb-3">Livelli di Accesso</h6>
                    <div class="mb-2">
                        <span class="role-badge role-admin">Admin</span>
                        <small>admin/admin123</small>
                        <br><small class="text-muted">Accesso completo</small>
                    </div>
                    <div class="mb-2">
                        <span class="role-badge role-manager">Manager</span>
                        <small>manager/manager123</small>
                        <br><small class="text-muted">Gestione viewer + log</small>
                    </div>
                    <div>
                        <span class="role-badge role-viewer">Viewer</span>
                        <small>viewer/viewer123</small>
                        <br><small class="text-muted">Solo visualizzazione</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# Importa dashboard template da file separato per evitare file troppo grande
def get_dashboard_template():
    """Carica il template dashboard con supporto per 3 livelli"""
    template = """
<!DOCTYPE html>
<html>
<head>
    <title>Sistema Controllo Accessi - Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="/static/css/dashboard.css" rel="stylesheet">
    <link href="/static/css/user-menu.css" rel="stylesheet">
    <link href="/static/css/clock.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark">
        <div class="container-fluid d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center">
                <i class="fas fa-shield-alt me-2"></i>
                <span class="navbar-brand mb-0 h1">Sistema Controllo Accessi</span>
            </div>
            <div class="system-clock mx-auto">
                <i class="fas fa-clock"></i>
                <span class="clock-time"></span>
                <span class="clock-date"></span>
            </div>
            <div class="d-flex align-items-center gap-3">
                <span class="navbar-text me-3">Isola Ecologica RAEE - Rende</span>
                <div id="user-menu-placeholder"></div>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <!-- Statistiche - Visibili a tutti -->
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card stat-card">
                    <div class="card-body text-center">
                        <i class="fas fa-clock fa-2x text-primary mb-3"></i>
                        <div class="stat-number text-primary" id="accessi-oggi">-</div>
                        <h6 class="text-muted">Accessi Oggi</h6>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card stat-card">
                    <div class="card-body text-center">
                        <i class="fas fa-check-circle fa-2x text-success mb-3"></i>
                        <div class="stat-number text-success" id="autorizzati">-</div>
                        <h6 class="text-muted">Autorizzati</h6>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card stat-card">
                    <div class="card-body text-center">
                        <i class="fas fa-users fa-2x text-info mb-3"></i>
                        <div class="stat-number text-info" id="utenti-totali">-</div>
                        <h6 class="text-muted">Utenti Totali</h6>
                    </div>
                </div>
            </div>
        </div>

        <!-- Sezione Admin - Solo per amministratori -->
        {% if session.role == 'admin' %}
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card hardware-card">
                    <div class="card-header bg-danger text-white">
                        <h5><i class="fas fa-crown me-2"></i>Controlli Amministratore</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4 mb-2">
                                <button class="btn btn-primary w-100" onclick="testReader()">
                                    <i class="fas fa-credit-card"></i><br><small>Test Lettore</small>
                                </button>
                            </div>
                            <div class="col-md-4 mb-2">
                                <button class="btn btn-warning w-100" onclick="testRelay()">
                                    <i class="fas fa-microchip"></i><br><small>Test USB-RLY08</small>
                                </button>
                            </div>
                            <div class="col-md-4 mb-2">
                                <button class="btn btn-success w-100" onclick="testGate()">
                                    <i class="fas fa-door-open"></i><br><small>Test Cancello</small>
                                </button>
                            </div>
                        </div>
                        <div class="row mt-2">
                            <div class="col-md-12">
                                <button class="btn btn-info w-100" onclick="testIntegrated()">
                                    <i class="fas fa-id-card me-2"></i>Test Completo Sistema
                                </button>
                            </div>
                        </div>
                        <div id="hardware-status" class="mt-3"></div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-danger text-white">
                        <h5><i class="fas fa-cogs me-2"></i>Gestione Sistema</h5>
                    </div>
                    <div class="card-body">
                        <div class="d-grid gap-2">
                            <!-- Menu items dinamici -->
                            {% for item in menu_items %}
                            <a href="{{ item.url }}" class="btn btn-outline-primary">
                                <i class="{{ item.icon }}"></i> {{ item.text }}
                            </a>
                            {% endfor %}
                            
                            <!-- Menu items fissi -->
                            <a href="/admin/config" class="btn btn-outline-primary">
                                <i class="fas fa-sliders-h"></i> Configurazioni Sistema
                            </a>
                            <a href="/admin/backup" class="btn btn-outline-success">
                                <i class="fas fa-database"></i> Backup & Restore
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- Sezione User Manager -->
        {% if session.role == 'user_manager' %}
        <div class="row mb-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5><i class="fas fa-user-tie me-2"></i>Pannello Gestore Utenti</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <button class="btn btn-primary w-100" onclick="showCreateViewerModal()">
                                    <i class="fas fa-user-plus fa-2x"></i>
                                    <br>Crea Utente Viewer
                                </button>
                            </div>
                            <div class="col-md-4">
                                <a href="/manage-viewers" class="btn btn-info w-100">
                                    <i class="fas fa-users fa-2x"></i>
                                    <br>Gestisci Viewers
                                </a>
                            </div>
                            <div class="col-md-4">
                                <button class="btn btn-success w-100" onclick="openExportModal()">
                                    <i class="fas fa-file-excel fa-2x"></i>
                                    <br>Esporta Log Excel
                                </button>
                            </div>
                        </div>
                        <hr>
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle"></i>
                            Come <strong>Gestore Utenti</strong> puoi:
                            <ul class="mb-0">
                                <li>Creare e gestire utenti Visualizzatori</li>
                                <li>Resettare password per i Visualizzatori</li>
                                <li>Visualizzare, filtrare ed esportare log in Excel</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- Sezione Viewer -->
        {% if session.role == 'viewer' %}
        <div class="row mb-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h5><i class="fas fa-eye me-2"></i>Pannello Visualizzatore</h5>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-success">
                            <i class="fas fa-info-circle"></i>
                            Come <strong>Visualizzatore</strong> puoi consultare i log di accesso e filtrarli per data.
                        </div>
                        <a href="/logs" class="btn btn-success btn-lg w-100">
                            <i class="fas fa-list-alt fa-2x"></i>
                            <br>Visualizza Log Accessi
                        </a>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- Log Recenti - Visibile a tutti -->
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-history me-2"></i>Ultimi Accessi</h5>
                    </div>
                    <div class="card-body" id="recent-accesses">
                        <div class="text-center text-muted">Caricamento...</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Include modals -->
    <div id="modals-container"></div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/static/js/dashboard.js"></script>
    <script src="/static/js/user-menu.js"></script>
    <script src="/static/js/clock.js"></script>
    <script>
        // Passa il ruolo utente a JavaScript
        window.userRole = '{{ session.role }}';
        
        // Carica modals solo per admin
        if (window.userRole === 'admin') {
            fetch('/static/html/modals.html')
                .then(response => response.text())
                .then(html => {
                    document.getElementById('modals-container').innerHTML = html;
                    initializeModalListeners();
                });
        }
        
        // Carica menu utente
        fetch('/api/user-menu-html')
            .then(response => response.text())
            .then(html => {
                document.getElementById('user-menu-placeholder').innerHTML = html;
                new UserMenu();
            });
    </script>
</body>
</html>
"""
    return template


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
    <link href="/static/css/clock.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark">
        <div class="container-fluid d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center">
                <i class="fas fa-users-cog me-2"></i>
                <span class="navbar-brand mb-0 h1">Gestione Utenti Sistema</span>
            </div>
            <div class="system-clock mx-auto">
                <i class="fas fa-clock"></i>
                <span class="clock-time"></span>
                <span class="clock-date"></span>
            </div>
            <div class="d-flex align-items-center gap-3">
                <a href="/" class="btn btn-outline-light btn-sm">
                    <i class="fas fa-arrow-left"></i> Dashboard
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
                        <div class="stat-number text-danger" id="admin-count">1</div>
                        <h6 class="text-muted">Amministratori</h6>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body text-center">
                        <i class="fas fa-user-tie fa-2x text-primary mb-3"></i>
                        <div class="stat-number text-primary" id="manager-count">1</div>
                        <h6 class="text-muted">Gestori Utenti</h6>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body text-center">
                        <i class="fas fa-eye fa-2x text-success mb-3"></i>
                        <div class="stat-number text-success" id="viewer-count">1</div>
                        <h6 class="text-muted">Visualizzatori</h6>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body text-center">
                        <i class="fas fa-users fa-2x text-info mb-3"></i>
                        <div class="stat-number text-info" id="total-users">3</div>
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
                                        <th>Info Creazione</th>
                                        <th>Ultimo Accesso</th>
                                        <th>Stato</th>
                                        <th>Azioni</th>
                                    </tr>
                                </thead>
                                <tbody id="users-table">
                                    <!-- Popolato dinamicamente da users.js -->
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
                                <input type="text" class="form-control" id="new-username" placeholder="Username nuovo utente" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Password</label>
                                <input type="password" class="form-control" id="new-password" placeholder="Password sicura" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Ruolo</label>
                                <select class="form-select" id="new-role">
                                    <option value="admin">👑 Amministratore</option>
                                    <option value="user_manager">👔 Gestore Utenti</option>
                                    <option value="viewer" selected>👁️ Visualizzatore</option>
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
                        <div id="recent-activities">
                            <div class="text-center text-muted">
                                <small>Caricamento attività...</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/static/js/user-menu.js"></script>
    <script src="/static/js/clock.js"></script>
    <script src="/static/js/users.js"></script>
    <script src="/static/js/recent-activities.js"></script>
    <script>
        // Carica menu utente
        fetch('/api/user-menu-html')
            .then(response => response.text())
            .then(html => {
                document.getElementById('user-menu-placeholder').innerHTML = html;
                new UserMenu();
            });
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
    <link href="/static/css/clock.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark">
        <div class="container-fluid d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center">
                <i class="fas fa-sliders-h me-2"></i>
                <span class="navbar-brand mb-0 h1">Configurazioni Sistema</span>
            </div>
            <div class="system-clock mx-auto">
                <i class="fas fa-clock"></i>
                <span class="clock-time"></span>
                <span class="clock-date"></span>
            </div>
            <div class="d-flex align-items-center gap-3">
                <a href="/" class="btn btn-outline-light btn-sm">
                    <i class="fas fa-arrow-left"></i> Torna alla Dashboard
                </a>
                <div id="user-menu-placeholder"></div>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <!-- Stato Sistema -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body text-center">
                        <i class="fas fa-server fa-2x text-success mb-3"></i>
                        <div class="stat-number text-success">Online</div>
                        <h6 class="text-muted">Stato Sistema</h6>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body text-center">
                        <i class="fas fa-code-branch fa-2x text-info mb-3"></i>
                        <div class="stat-number text-info">v1.0.0</div>
                        <h6 class="text-muted">Versione</h6>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body text-center">
                        <i class="fas fa-clock fa-2x text-warning mb-3"></i>
                        <div class="stat-number text-warning">24h</div>
                        <h6 class="text-muted">Uptime</h6>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body text-center">
                        <i class="fas fa-memory fa-2x text-primary mb-3"></i>
                        <div class="stat-number text-primary">45%</div>
                        <h6 class="text-muted">RAM Utilizzata</h6>
                    </div>
                </div>
            </div>
        </div>

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
                <a class="nav-link" data-bs-toggle="tab" href="#debug">
                    <i class="fas fa-bug"></i> Debug
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
                                        <input type="text" class="form-control" id="nome-installazione" value="Isola Ecologica RAEE - Rende">
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
                                            <option value="production" selected>Produzione</option>
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
                <div class="card mb-3">
                    <div class="card-header bg-primary text-white">
                        <h5><i class="fas fa-search me-2"></i>Rilevamento Automatico Hardware</h5>
                    </div>
                    <div class="card-body">
                        <div class="row mb-3">
                            <div class="col-md-12">
                                <button id="detect-hardware" class="btn btn-primary">
                                    <i class="fas fa-search me-2"></i>Rileva Hardware Collegato
                                </button>
                                <button class="btn btn-info ms-2" data-bs-toggle="collapse" data-bs-target="#hardware-info">
                                    <i class="fas fa-info-circle me-2"></i>Informazioni
                                </button>
                            </div>
                        </div>
                        
                        <div class="collapse mb-3" id="hardware-info">
                            <div class="alert alert-info">
                                <h6><i class="fas fa-info-circle me-2"></i>Informazioni sul Rilevamento Hardware</h6>
                                <p>Il sistema può rilevare automaticamente qualsiasi tipo di hardware collegato, inclusi:</p>
                                <ul>
                                    <li><strong>Lettori Tessere:</strong> Qualsiasi lettore RFID/NFC USB o seriale</li>
                                    <li><strong>Controller Relè:</strong> Qualsiasi controller relè USB o seriale</li>
                                    <li><strong>Porte Seriali:</strong> Tutte le porte seriali disponibili nel sistema</li>
                                    <li><strong>Dispositivi USB:</strong> Tutti i dispositivi USB collegati</li>
                                    <li><strong>Altri Dispositivi:</strong> Hardware generico rilevabile dal sistema</li>
                                </ul>
                                <p>Assicurati che i dispositivi siano collegati prima di avviare il rilevamento. Il sistema mostrerà tutte le porte disponibili e ti aiuterà a identificare il tipo di dispositivo collegato.</p>
                            </div>
                        </div>
                        
                        <div id="hardware-status"></div>
                        <div id="hardware-list" class="mt-3"></div>
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

            <!-- Debug -->
            <div class="tab-pane fade" id="debug">
                <div class="card mb-3">
                    <div class="card-header bg-dark text-white">
                        <h5><i class="fas fa-terminal me-2"></i>Console Log in Tempo Reale</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <button id="toggle-log" class="btn btn-primary">
                                <i class="fas fa-play"></i> Avvia Log
                            </button>
                            <button id="clear-log" class="btn btn-secondary">
                                <i class="fas fa-eraser"></i> Pulisci
                            </button>
                            <button id="restart-service" class="btn btn-danger float-end">
                                <i class="fas fa-sync-alt"></i> Riavvia Servizio
                            </button>
                        </div>
                        <div class="log-container" style="background: #1e1e1e; color: #0f0; font-family: monospace; padding: 15px; height: 500px; overflow-y: auto; border-radius: 5px;">
                            <div id="log-output">
                                <div class="text-muted">Log non attivo. Clicca 'Avvia Log' per iniziare...</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header bg-info text-white">
                        <h5><i class="fas fa-heartbeat me-2"></i>Stato Sistema</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Servizio Web API</h6>
                                <div id="service-status" class="mb-3">
                                    <span class="badge bg-secondary">Controllo...</span>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <h6>Lettore Tessere</h6>
                                <div id="reader-status" class="mb-3">
                                    <span class="badge bg-secondary">Controllo...</span>
                                </div>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-md-12">
                                <button id="check-status" class="btn btn-info">
                                    <i class="fas fa-heartbeat"></i> Verifica Stato
                                </button>
                            </div>
                        </div>
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
    <script src="/static/js/clock.js"></script>
    <script src="/static/js/sistema.js"></script>
    <script src="/static/js/hardware-manager.js"></script>
    <script>
        // Carica menu utente
        fetch('/api/user-menu-html')
            .then(response => response.text())
            .then(html => {
                document.getElementById('user-menu-placeholder').innerHTML = html;
                new UserMenu();
            });
        
        // Debug section functionality
        let logInterval = null;
        let isLogging = false;
        
        // Toggle log streaming
        document.getElementById('toggle-log')?.addEventListener('click', function() {
            const btn = this;
            if (!isLogging) {
                startLogStreaming();
                btn.innerHTML = '<i class="fas fa-pause"></i> Ferma Log';
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-warning');
            } else {
                stopLogStreaming();
                btn.innerHTML = '<i class="fas fa-play"></i> Avvia Log';
                btn.classList.remove('btn-warning');
                btn.classList.add('btn-primary');
            }
        });
        
        // Clear log
        document.getElementById('clear-log')?.addEventListener('click', function() {
            document.getElementById('log-output').innerHTML = '<div class="text-muted">Log pulito...</div>';
        });
        
        // Restart service
        document.getElementById('restart-service')?.addEventListener('click', function() {
            if (confirm('Sei sicuro di voler riavviare il servizio? Il sistema sarà non disponibile per alcuni secondi.')) {
                const btn = this;
                btn.disabled = true;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Riavvio in corso...';
                
                fetch('/api/restart-service', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Servizio riavviato con successo!');
                        setTimeout(() => window.location.reload(), 3000);
                    } else {
                        alert('Errore: ' + (data.error || 'Sconosciuto'));
                        btn.disabled = false;
                        btn.innerHTML = '<i class="fas fa-sync-alt"></i> Riavvia Servizio';
                    }
                })
                .catch(error => {
                    setTimeout(() => window.location.reload(), 5000);
                });
            }
        });
        
        // Check system status
        document.getElementById('check-status')?.addEventListener('click', checkSystemStatus);
        
        function startLogStreaming() {
            isLogging = true;
            const logOutput = document.getElementById('log-output');
            logOutput.innerHTML = '<div class="text-info">Connessione al log...</div>';
            
            logInterval = setInterval(() => {
                fetch('/api/system-logs')
                    .then(response => response.json())
                    .then(data => {
                        if (data.logs && data.logs.length > 0) {
                            logOutput.innerHTML = '';
                            data.logs.forEach(log => {
                                const logLine = document.createElement('div');
                                logLine.style.marginBottom = '2px';
                                
                                if (log.includes('ERROR') || log.includes('❌')) {
                                    logLine.style.color = '#ff6b6b';
                                } else if (log.includes('WARNING') || log.includes('⚠️')) {
                                    logLine.style.color = '#ffd93d';
                                } else if (log.includes('INFO') || log.includes('✅')) {
                                    logLine.style.color = '#6bcf7f';
                                } else if (log.includes('DEBUG')) {
                                    logLine.style.color = '#95a5a6';
                                } else {
                                    logLine.style.color = '#0f0';
                                }
                                
                                logLine.textContent = log;
                                logOutput.appendChild(logLine);
                            });
                            
                            const container = document.querySelector('.log-container');
                            if (container) container.scrollTop = container.scrollHeight;
                        }
                    })
                    .catch(error => console.error('Errore log:', error));
            }, 1000);
        }
        
        function stopLogStreaming() {
            isLogging = false;
            if (logInterval) {
                clearInterval(logInterval);
                logInterval = null;
            }
            const output = document.getElementById('log-output');
            if (output) output.innerHTML += '<div class="text-warning mt-2">--- Log fermato ---</div>';
        }
        
        function checkSystemStatus() {
            fetch('/api/system-status')
                .then(response => response.json())
                .then(data => {
                    const serviceStatus = document.getElementById('service-status');
                    if (serviceStatus) {
                        serviceStatus.innerHTML = data.service_running ? 
                            '<span class="badge bg-success">✅ Attivo</span>' : 
                            '<span class="badge bg-danger">❌ Non attivo</span>';
                    }
                    
                    const readerStatus = document.getElementById('reader-status');
                    if (readerStatus) {
                        readerStatus.innerHTML = data.reader_connected ? 
                            `<span class="badge bg-success">✅ ${data.reader_type || 'Connesso'}</span>` : 
                            '<span class="badge bg-warning">⚠️ Non connesso</span>';
                    }
                })
                .catch(error => {
                    console.error('Errore stato:', error);
                });
        }
        
        // Check status on load if debug tab exists
        if (document.getElementById('debug')) {
            checkSystemStatus();
        }
        
        // Form handlers
        document.getElementById('sistema-form').addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Configurazioni sistema salvate!\\n\\nFunzionalità completa in sviluppo.');
        });
        
        function restartSystem() {
            if (confirm('Sei sicuro di voler riavviare il sistema?\\n\\nTutte le sessioni attive verranno terminate.')) {
                alert('Sistema in riavvio...\\n\\nRicarica la pagina tra 30 secondi.');
            }
        }
        
        function exportConfig() {
            alert('Export configurazioni in formato JSON...\\n\\nFunzionalità in sviluppo.');
        }
        
        function resetToDefaults() {
            if (confirm('Ripristinare tutte le configurazioni ai valori default?\\n\\nQuesta operazione non può essere annullata.')) {
                alert('Configurazioni ripristinate ai valori default.');
            }
        }
        
        // Funzioni test hardware
        function testReader() {
            const readerType = document.getElementById('reader-type').value;
            const readerPort = document.getElementById('reader-port').value;
            const resultDiv = document.getElementById('test-reader-result');
            
            resultDiv.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Testing...</span></div> Test in corso...';
            
            fetch('/api/hardware/test-connection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    hardware_type: 'card_reader',
                    device_path: readerPort,
                    reader_type: readerType
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    resultDiv.innerHTML = '<div class="alert alert-success">✅ Lettore ' + readerType + ' funzionante!</div>';
                } else {
                    resultDiv.innerHTML = '<div class="alert alert-danger">❌ Test fallito: ' + (data.message || 'Errore sconosciuto') + '</div>';
                }
            })
            .catch(error => {
                console.error('Errore test:', error);
                resultDiv.innerHTML = '<div class="alert alert-danger">❌ Errore di connessione</div>';
            });
        }
        
        function testRelay() {
            const relayPort = document.getElementById('relay-port').value;
            const resultDiv = document.getElementById('test-relay-result');
            
            resultDiv.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Testing...</span></div> Test in corso...';
            
            fetch('/api/hardware/test-connection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    hardware_type: 'relay_controller',
                    device_path: relayPort
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    resultDiv.innerHTML = '<div class="alert alert-success">✅ Relè USB-RLY08 funzionante!</div>';
                } else {
                    resultDiv.innerHTML = '<div class="alert alert-danger">❌ Test fallito: ' + (data.message || 'Errore sconosciuto') + '</div>';
                }
            })
            .catch(error => {
                console.error('Errore test:', error);
                resultDiv.innerHTML = '<div class="alert alert-danger">❌ Errore di connessione</div>';
            });
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
    <link href="/static/css/clock.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark">
        <div class="container-fluid d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center">
                <i class="fas fa-database me-2"></i>
                <span class="navbar-brand mb-0 h1">Backup & Restore Sistema</span>
            </div>
            <div class="system-clock mx-auto">
                <i class="fas fa-clock"></i>
                <span class="clock-time"></span>
                <span class="clock-date"></span>
            </div>
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
                <div class="card stat-card" id="backup-total">
                    <div class="card-body text-center">
                        <i class="fas fa-archive fa-2x text-primary mb-3"></i>
                        <div class="stat-number text-primary">-</div>
                        <h6 class="text-muted">Backup Totali</h6>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card" id="backup-size">
                    <div class="card-body text-center">
                        <i class="fas fa-hdd fa-2x text-success mb-3"></i>
                        <div class="stat-number text-success">-</div>
                        <h6 class="text-muted">Spazio Utilizzato</h6>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body text-center">
                        <i class="fas fa-clock fa-2x text-warning mb-3"></i>
                        <div class="stat-number text-warning">2h fa</div>
                        <h6 class="text-muted">Ultimo Backup</h6>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card" id="disk-usage">
                    <div class="card-body text-center">
                        <i class="fas fa-chart-pie fa-2x text-info mb-3"></i>
                        <div class="stat-number text-info">-</div>
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
                                    <i class="fas fa-archive fa-2x"></i><br>Backup Completo
                                    <small class="d-block">Sistema + Database + Config</small>
                                </button>
                            </div>
                            <div class="col-md-6">
                                <button class="btn btn-success w-100 mb-2" onclick="createBackup('database')">
                                    <i class="fas fa-database fa-2x"></i><br>Solo Database
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
                        <form onsubmit="event.preventDefault(); saveBackupConfig();">
                            <div class="mb-3">
                                <label class="form-label">
                                    <input type="checkbox" id="auto-backup"> Backup Automatici
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
                                <label class="form-label">Mantieni per (giorni)</label>
                                <select class="form-select" id="retention-days">
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
                            <table class="table table-hover" id="backup-list">
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
                                <tbody>
                                    <tr>
                                        <td colspan="7" class="text-center">
                                            <div class="spinner-border text-primary" role="status">
                                                <span class="visually-hidden">Caricamento...</span>
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/static/js/user-menu.js"></script>
    <script src="/static/js/clock.js"></script>
    <script src="/static/js/backup.js"></script>
    <script>
        // Carica menu utente
        fetch('/api/user-menu-html')
            .then(response => response.text())
            .then(html => {
                document.getElementById('user-menu-placeholder').innerHTML = html;
                new UserMenu();
            });
    </script>
</body>
</html>
"""
