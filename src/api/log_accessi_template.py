# Template per la pagina Log Accessi

LOG_ACCESSI_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Log Accessi - Sistema Controllo Accessi</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="/static/css/dashboard.css" rel="stylesheet">
    <link href="/static/css/user-menu.css" rel="stylesheet">
    <link href="/static/css/clock.css" rel="stylesheet">
    <style>
        .filter-card {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .log-table {
            font-size: 0.9rem;
        }
        .badge-autorizzato {
            background-color: #28a745;
        }
        .badge-negato {
            background-color: #dc3545;
        }
        .badge-fuori-orario {
            background-color: #ffc107;
            color: #212529;
        }
        .export-buttons {
            gap: 10px;
        }
        .stat-card {
            border-left: 4px solid;
        }
        .stat-card.success {
            border-left-color: #28a745;
        }
        .stat-card.danger {
            border-left-color: #dc3545;
        }
        .stat-card.warning {
            border-left-color: #ffc107;
        }
        .stat-card.info {
            border-left-color: #17a2b8;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark">
        <div class="container-fluid d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center">
                <i class="fas fa-history me-2"></i>
                <span class="navbar-brand mb-0 h1">Log Accessi Sistema</span>
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
        <!-- Statistiche Riepilogo -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card stat-card success">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h6 class="text-muted mb-2">Accessi Autorizzati</h6>
                                <h3 class="mb-0" id="stat-autorizzati">0</h3>
                            </div>
                            <i class="fas fa-check-circle text-success fa-2x"></i>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card danger">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h6 class="text-muted mb-2">Accessi Negati</h6>
                                <h3 class="mb-0" id="stat-negati">0</h3>
                            </div>
                            <i class="fas fa-times-circle text-danger fa-2x"></i>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card warning">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h6 class="text-muted mb-2">Fuori Orario</h6>
                                <h3 class="mb-0" id="stat-fuori-orario">0</h3>
                            </div>
                            <i class="fas fa-clock text-warning fa-2x"></i>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card info">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h6 class="text-muted mb-2">Totale Oggi</h6>
                                <h3 class="mb-0" id="stat-oggi">0</h3>
                            </div>
                            <i class="fas fa-calendar-day text-info fa-2x"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Filtri -->
        <div class="filter-card">
            <h5 class="mb-3"><i class="fas fa-filter me-2"></i>Filtri Ricerca</h5>
            <div class="row">
                <div class="col-md-3">
                    <label class="form-label">Periodo</label>
                    <select class="form-select" id="filter-periodo">
                        <option value="oggi">Oggi</option>
                        <option value="settimana">Ultima Settimana</option>
                        <option value="mese" selected>Mese Corrente</option>
                        <option value="custom">Personalizzato</option>
                    </select>
                </div>
                <div class="col-md-2 custom-date" style="display:none;">
                    <label class="form-label">Data Inizio</label>
                    <input type="date" class="form-control" id="filter-data-inizio">
                </div>
                <div class="col-md-2 custom-date" style="display:none;">
                    <label class="form-label">Data Fine</label>
                    <input type="date" class="form-control" id="filter-data-fine">
                </div>
                <div class="col-md-3">
                    <label class="form-label">Tipo Accesso</label>
                    <select class="form-select" id="filter-tipo">
                        <option value="">Tutti</option>
                        <option value="AUTORIZZATO">Autorizzati</option>
                        <option value="UTENTE_NON_TROVATO">Utente Non Trovato</option>
                        <option value="FUORI_ORARIO">Fuori Orario</option>
                        <option value="LIMITE_SUPERATO">Limite Superato</option>
                        <option value="UTENTE_DISATTIVATO">Utente Disattivato</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label">Codice Fiscale</label>
                    <input type="text" class="form-control" id="filter-cf" placeholder="Ricerca CF...">
                </div>
                <div class="col-md-3 d-flex align-items-end">
                    <button class="btn btn-primary w-100" onclick="applyFilters()">
                        <i class="fas fa-search me-2"></i>Applica Filtri
                    </button>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-md-12 d-flex justify-content-between">
                    <button class="btn btn-secondary" onclick="resetFilters()">
                        <i class="fas fa-redo me-2"></i>Reset Filtri
                    </button>
                    <div class="export-buttons d-flex">
                        <button class="btn btn-success" onclick="exportData('excel')">
                            <i class="fas fa-file-excel me-2"></i>Excel
                        </button>
                        <button class="btn btn-info" onclick="exportData('csv')">
                            <i class="fas fa-file-csv me-2"></i>CSV
                        </button>
                        <button class="btn btn-danger" onclick="exportData('pdf')">
                            <i class="fas fa-file-pdf me-2"></i>PDF
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tabella Log -->
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="fas fa-list me-2"></i>Log Accessi
                    <span class="badge bg-secondary ms-2" id="log-count">0 record</span>
                </h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover log-table" id="log-table">
                        <thead>
                            <tr>
                                <th>Data/Ora</th>
                                <th>Codice Fiscale</th>
                                <th>Nome Utente</th>
                                <th>Tipo Accesso</th>
                                <th>Motivo</th>
                                <th>Terminale</th>
                                <th>Durata (ms)</th>
                            </tr>
                        </thead>
                        <tbody id="log-tbody">
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
                
                <!-- Paginazione -->
                <nav aria-label="Paginazione log">
                    <ul class="pagination justify-content-center" id="pagination">
                    </ul>
                </nav>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/static/js/user-menu.js"></script>
    <script src="/static/js/clock.js"></script>
    <script>
        let currentPage = 1;
        let totalPages = 1;
        let currentFilters = {};

        // Carica menu utente
        fetch('/api/user-menu-html')
            .then(response => response.text())
            .then(html => {
                document.getElementById('user-menu-placeholder').innerHTML = html;
                new UserMenu();
            });

        // Gestione cambio periodo
        document.getElementById('filter-periodo').addEventListener('change', function() {
            const customDateElements = document.querySelectorAll('.custom-date');
            if (this.value === 'custom') {
                customDateElements.forEach(el => el.style.display = 'block');
            } else {
                customDateElements.forEach(el => el.style.display = 'none');
            }
        });

        function applyFilters() {
            currentFilters = {
                periodo: document.getElementById('filter-periodo').value,
                data_inizio: document.getElementById('filter-data-inizio').value,
                data_fine: document.getElementById('filter-data-fine').value,
                tipo: document.getElementById('filter-tipo').value,
                codice_fiscale: document.getElementById('filter-cf').value
            };
            currentPage = 1;
            loadLogs();
        }

        function resetFilters() {
            document.getElementById('filter-periodo').value = 'mese';
            document.getElementById('filter-tipo').value = '';
            document.getElementById('filter-cf').value = '';
            document.getElementById('filter-data-inizio').value = '';
            document.getElementById('filter-data-fine').value = '';
            document.querySelectorAll('.custom-date').forEach(el => el.style.display = 'none');
            currentFilters = {};
            currentPage = 1;
            loadLogs();
        }

        function loadLogs() {
            const params = new URLSearchParams({
                page: currentPage,
                ...currentFilters
            });

            fetch(`/api/log-accessi?${params}`)
                .then(response => response.json())
                .then(data => {
                    updateTable(data.logs);
                    updateStatistics(data.statistics);
                    updatePagination(data.total_pages, data.current_page);
                    document.getElementById('log-count').textContent = `${data.total_records} record`;
                })
                .catch(error => {
                    console.error('Errore caricamento log:', error);
                    alert('Errore nel caricamento dei log');
                });
        }

        function updateTable(logs) {
            const tbody = document.getElementById('log-tbody');
            if (logs.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="7" class="text-center text-muted">Nessun log trovato</td>
                    </tr>
                `;
                return;
            }

            tbody.innerHTML = logs.map(log => {
                const badge = getBadgeClass(log.tipo_accesso);
                const cfMasked = log.codice_fiscale ? 
                    `${log.codice_fiscale.substring(0, 4)}***${log.codice_fiscale.substring(12)}` : 
                    'N/D';
                
                return `
                    <tr>
                        <td>${new Date(log.timestamp).toLocaleString('it-IT')}</td>
                        <td><code>${cfMasked}</code></td>
                        <td>${log.nome_utente || '-'}</td>
                        <td><span class="badge ${badge}">${formatTipoAccesso(log.tipo_accesso)}</span></td>
                        <td>${log.motivo_rifiuto || '-'}</td>
                        <td>${log.terminale_id || '-'}</td>
                        <td>${log.durata_elaborazione ? log.durata_elaborazione.toFixed(2) : '-'}</td>
                    </tr>
                `;
            }).join('');
        }

        function getBadgeClass(tipo) {
            switch(tipo) {
                case 'AUTORIZZATO': return 'badge-autorizzato';
                case 'FUORI_ORARIO': return 'badge-fuori-orario';
                default: return 'badge-negato';
            }
        }

        function formatTipoAccesso(tipo) {
            const mapping = {
                'AUTORIZZATO': 'Autorizzato',
                'UTENTE_NON_TROVATO': 'Utente Non Trovato',
                'FUORI_ORARIO': 'Fuori Orario',
                'LIMITE_SUPERATO': 'Limite Superato',
                'UTENTE_DISATTIVATO': 'Utente Disattivato',
                'ERRORE': 'Errore'
            };
            return mapping[tipo] || tipo || 'N/D';
        }

        function updateStatistics(stats) {
            document.getElementById('stat-autorizzati').textContent = stats.autorizzati || 0;
            document.getElementById('stat-negati').textContent = stats.negati || 0;
            document.getElementById('stat-fuori-orario').textContent = stats.fuori_orario || 0;
            document.getElementById('stat-oggi').textContent = stats.oggi || 0;
        }

        function updatePagination(total, current) {
            totalPages = total;
            currentPage = current;
            
            const pagination = document.getElementById('pagination');
            let html = '';
            
            // Previous
            html += `
                <li class="page-item ${current === 1 ? 'disabled' : ''}">
                    <a class="page-link" href="#" onclick="changePage(${current - 1}); return false;">
                        <i class="fas fa-chevron-left"></i>
                    </a>
                </li>
            `;
            
            // Pages
            for (let i = 1; i <= Math.min(total, 10); i++) {
                html += `
                    <li class="page-item ${i === current ? 'active' : ''}">
                        <a class="page-link" href="#" onclick="changePage(${i}); return false;">${i}</a>
                    </li>
                `;
            }
            
            // Next
            html += `
                <li class="page-item ${current === total ? 'disabled' : ''}">
                    <a class="page-link" href="#" onclick="changePage(${current + 1}); return false;">
                        <i class="fas fa-chevron-right"></i>
                    </a>
                </li>
            `;
            
            pagination.innerHTML = html;
        }

        function changePage(page) {
            if (page < 1 || page > totalPages) return;
            currentPage = page;
            loadLogs();
        }

        function exportData(format) {
            const params = new URLSearchParams({
                format: format,
                ...currentFilters
            });
            
            window.location.href = `/api/log-accessi/export?${params}`;
        }

        // Carica dati iniziali
        loadLogs();

        // Auto-refresh ogni 30 secondi
        setInterval(loadLogs, 30000);
    </script>
</body>
</html>
"""