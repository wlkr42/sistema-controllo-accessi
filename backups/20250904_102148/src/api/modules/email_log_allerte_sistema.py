# File: /opt/access_control/src/api/modules/email_log_allerte_sistema.py
# Moduli Completi: Email, Log, Allerte, Sistema - Dashboard

from flask import render_template_string, request, jsonify, session, send_file
from datetime import datetime, timedelta
import sqlite3
import smtplib
import csv
import io
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ..web_api import app, require_auth, require_permission, config_manager, get_base_template, USER_ROLES, project_root

# ===============================
# MODULO EMAIL - TEMPLATE
# ===============================

EMAIL_TEMPLATE = get_base_template() + """
{% block title %}Configurazione Email - Sistema Controllo Accessi{% endblock %}

{% block content %}
<div class="header">
    <h1><i class="fas fa-envelope"></i> {{ island_name }}</h1>
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
            <li class="nav-item"><a href="/" class="nav-link"><i class="fas fa-tachometer-alt"></i><span>Panoramica</span></a></li>
            <li class="nav-item"><a href="/dispositivi" class="nav-link"><i class="fas fa-microchip"></i><span>Dispositivi</span></a></li>
            <li class="nav-item"><a href="/email" class="nav-link active"><i class="fas fa-envelope"></i><span>Email</span></a></li>
            <li class="nav-item"><a href="/utenti" class="nav-link"><i class="fas fa-users"></i><span>Utenti</span></a></li>
            <li class="nav-item"><a href="/log" class="nav-link"><i class="fas fa-list-alt"></i><span>Log Accessi</span></a></li>
            <li class="nav-item"><a href="/allerte" class="nav-link"><i class="fas fa-exclamation-triangle"></i><span>Allerte</span></a></li>
            <li class="nav-item"><a href="/sistema" class="nav-link"><i class="fas fa-cog"></i><span>Sistema</span></a></li>
        </ul>
    </div>
    
    <div class="content">
        <h2><i class="fas fa-envelope-open-text"></i> Configurazione Sistema Email</h2>
        
        <!-- Test Connessione SMTP -->
        <div class="card">
            <h4><i class="fas fa-network-wired"></i> Test Connessione SMTP</h4>
            <div id="smtp-test-result" class="mb-3">
                <span class="loading">Test in corso...</span>
            </div>
            <button class="btn btn-primary" onclick="testSMTPConnection()">
                <i class="fas fa-play"></i> Testa Connessione
            </button>
            <button class="btn btn-success ml-2" onclick="sendTestEmail()">
                <i class="fas fa-paper-plane"></i> Invia Email di Test
            </button>
        </div>
        
        <!-- Configurazione SMTP -->
        <div class="card">
            <h4><i class="fas fa-server"></i> Configurazione Server SMTP</h4>
            <form id="smtp-config-form">
                <div class="grid grid-2">
                    <div class="form-group">
                        <label class="form-label" for="smtp-server">Server SMTP</label>
                        <input type="text" class="form-control" id="smtp-server" name="smtp_server" placeholder="smtp.gmail.com">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="smtp-port">Porta</label>
                        <select class="form-control form-select" id="smtp-port" name="smtp_port">
                            <option value="25">25 (SMTP)</option>
                            <option value="587">587 (SMTP TLS)</option>
                            <option value="465">465 (SMTP SSL)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="email-mittente">Email Mittente</label>
                        <input type="email" class="form-control" id="email-mittente" name="mittente" placeholder="isola@comune.example.it">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="email-password">Password Email</label>
                        <input type="password" class="form-control" id="email-password" name="password" placeholder="Password o App Password">
                    </div>
                </div>
                <button type="submit" class="btn btn-success">
                    <i class="fas fa-save"></i> Salva Configurazione SMTP
                </button>
            </form>
        </div>
        
        <!-- Destinatari Email -->
        <div class="card">
            <h4><i class="fas fa-address-book"></i> Gestione Destinatari</h4>
            <div class="form-group">
                <label class="form-label" for="new-recipient">Aggiungi Destinatario</label>
                <div style="display: flex; gap: 10px;">
                    <input type="email" class="form-control" id="new-recipient" placeholder="email@example.com">
                    <button class="btn btn-primary" onclick="addRecipient()">
                        <i class="fas fa-plus"></i> Aggiungi
                    </button>
                </div>
            </div>
            <div id="recipients-list" class="mt-3">
                <div class="loading">Caricamento destinatari...</div>
            </div>
        </div>
        
        <!-- Configurazione Report -->
        <div class="card">
            <h4><i class="fas fa-calendar-alt"></i> Report Automatici</h4>
            <form id="report-config-form">
                <div class="grid grid-2">
                    <div class="form-group">
                        <label class="form-label" for="report-frequency">Frequenza Report</label>
                        <select class="form-control form-select" id="report-frequency" name="frequenza_report">
                            <option value="disabled">Disabilitato</option>
                            <option value="daily">Giornaliero</option>
                            <option value="weekly">Settimanale</option>
                            <option value="monthly">Mensile</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="report-time">Orario Invio</label>
                        <input type="time" class="form-control" id="report-time" name="orario_invio" value="08:00">
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">
                        <input type="checkbox" id="report-include-stats" name="includi_statistiche" checked>
                        Includi statistiche accessi
                    </label>
                </div>
                <div class="form-group">
                    <label class="form-label">
                        <input type="checkbox" id="report-include-errors" name="includi_errori" checked>
                        Includi log errori
                    </label>
                </div>
                <button type="submit" class="btn btn-success">
                    <i class="fas fa-save"></i> Salva Configurazione Report
                </button>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        loadEmailConfig();
        loadRecipients();
        testSMTPConnection();
    });
    
    async function loadEmailConfig() {
        try {
            const response = await fetch('/api/email/config');
            const data = await response.json();
            
            if (data.success) {
                document.getElementById('smtp-server').value = data.config.smtp_server || '';
                document.getElementById('smtp-port').value = data.config.smtp_port || '587';
                document.getElementById('email-mittente').value = data.config.mittente || '';
                document.getElementById('email-password').value = ''; // Non mostrare password
                document.getElementById('report-frequency').value = data.config.frequenza_report || 'disabled';
                document.getElementById('report-time').value = data.config.orario_invio || '08:00';
                document.getElementById('report-include-stats').checked = data.config.includi_statistiche !== false;
                document.getElementById('report-include-errors').checked = data.config.includi_errori !== false;
            }
        } catch (error) {
            console.error('Errore caricamento configurazione email:', error);
        }
    }
    
    async function loadRecipients() {
        try {
            const response = await fetch('/api/email/recipients');
            const data = await response.json();
            
            if (data.success) {
                const container = document.getElementById('recipients-list');
                let html = '';
                
                data.recipients.forEach(email => {
                    html += `
                        <div class="alert alert-info" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <span><i class="fas fa-envelope"></i> ${email}</span>
                            <button class="btn btn-danger btn-sm" onclick="removeRecipient('${email}')">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    `;
                });
                
                container.innerHTML = html || '<p class="text-muted">Nessun destinatario configurato</p>';
            }
        } catch (error) {
            console.error('Errore caricamento destinatari:', error);
        }
    }
    
    async function testSMTPConnection() {
        const resultEl = document.getElementById('smtp-test-result');
        resultEl.innerHTML = '<span class="loading">Test connessione SMTP...</span>';
        
        try {
            const response = await fetch('/api/email/test-smtp', {method: 'POST'});
            const data = await response.json();
            
            if (data.success) {
                resultEl.innerHTML = `
                    <div class="alert alert-success">
                        <i class="fas fa-check-circle"></i> Connessione SMTP operativa
                        <br><small>${data.message}</small>
                    </div>
                `;
            } else {
                resultEl.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-times-circle"></i> Errore connessione SMTP
                        <br><small>${data.error}</small>
                    </div>
                `;
            }
        } catch (error) {
            resultEl.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i> Errore comunicazione
                </div>
            `;
        }
    }
    
    async function sendTestEmail() {
        try {
            const response = await fetch('/api/email/send-test', {method: 'POST'});
            const data = await response.json();
            
            if (data.success) {
                showAlert('Email di test inviata con successo', 'success');
            } else {
                showAlert(`Errore invio email: ${data.error}`, 'danger');
            }
        } catch (error) {
            showAlert('Errore comunicazione', 'danger');
        }
    }
    
    async function addRecipient() {
        const email = document.getElementById('new-recipient').value.trim();
        
        if (!email) {
            showAlert('Inserisci un indirizzo email valido', 'warning');
            return;
        }
        
        if (!email.includes('@')) {
            showAlert('Formato email non valido', 'warning');
            return;
        }
        
        try {
            const response = await fetch('/api/email/add-recipient', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email: email})
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert('Destinatario aggiunto', 'success');
                document.getElementById('new-recipient').value = '';
                loadRecipients();
            } else {
                showAlert(data.error, 'danger');
            }
        } catch (error) {
            showAlert('Errore comunicazione', 'danger');
        }
    }
    
    async function removeRecipient(email) {
        if (confirm(`Rimuovere ${email} dai destinatari?`)) {
            try {
                const response = await fetch('/api/email/remove-recipient', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email: email})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showAlert('Destinatario rimosso', 'success');
                    loadRecipients();
                } else {
                    showAlert(data.error, 'danger');
                }
            } catch (error) {
                showAlert('Errore comunicazione', 'danger');
            }
        }
    }
    
    // Salvataggio configurazioni
    document.getElementById('smtp-config-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const config = {};
        for (let [key, value] of formData.entries()) {
            config[key] = value;
        }
        
        try {
            const response = await fetch('/api/email/save-smtp', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert('Configurazione SMTP salvata', 'success');
                testSMTPConnection();
            } else {
                showAlert('Errore salvataggio configurazione', 'danger');
            }
        } catch (error) {
            showAlert('Errore comunicazione', 'danger');
        }
    });
    
    document.getElementById('report-config-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const config = {
            frequenza_report: formData.get('frequenza_report'),
            orario_invio: formData.get('orario_invio'),
            includi_statistiche: formData.get('includi_statistiche') === 'on',
            includi_errori: formData.get('includi_errori') === 'on'
        };
        
        try {
            const response = await fetch('/api/email/save-report-config', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert('Configurazione report salvata', 'success');
            } else {
                showAlert('Errore salvataggio configurazione', 'danger');
            }
        } catch (error) {
            showAlert('Errore comunicazione', 'danger');
        }
    });
</script>
{% endblock %}
"""

# ===============================
# MODULO LOG ACCESSI - TEMPLATE
# ===============================

LOG_TEMPLATE = get_base_template() + """
{% block title %}Log Accessi - Sistema Controllo Accessi{% endblock %}

{% block content %}
<div class="header">
    <h1><i class="fas fa-list-alt"></i> {{ island_name }}</h1>
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
            <li class="nav-item"><a href="/" class="nav-link"><i class="fas fa-tachometer-alt"></i><span>Panoramica</span></a></li>
            <li class="nav-item"><a href="/dispositivi" class="nav-link"><i class="fas fa-microchip"></i><span>Dispositivi</span></a></li>
            <li class="nav-item"><a href="/email" class="nav-link"><i class="fas fa-envelope"></i><span>Email</span></a></li>
            <li class="nav-item"><a href="/utenti" class="nav-link"><i class="fas fa-users"></i><span>Utenti</span></a></li>
            <li class="nav-item"><a href="/log" class="nav-link active"><i class="fas fa-list-alt"></i><span>Log Accessi</span></a></li>
            <li class="nav-item"><a href="/allerte" class="nav-link"><i class="fas fa-exclamation-triangle"></i><span>Allerte</span></a></li>
            <li class="nav-item"><a href="/sistema" class="nav-link"><i class="fas fa-cog"></i><span>Sistema</span></a></li>
        </ul>
    </div>
    
    <div class="content">
        <h2><i class="fas fa-history"></i> Log Accessi Sistema</h2>
        
        <!-- Filtri e Ricerca -->
        <div class="card">
            <h4><i class="fas fa-filter"></i> Filtri e Ricerca</h4>
            <form id="filter-form">
                <div class="grid grid-3">
                    <div class="form-group">
                        <label class="form-label" for="filter-date-from">Data Da</label>
                        <input type="date" class="form-control" id="filter-date-from" name="date_from">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="filter-date-to">Data A</label>
                        <input type="date" class="form-control" id="filter-date-to" name="date_to">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="filter-status">Stato Accesso</label>
                        <select class="form-control form-select" id="filter-status" name="status">
                            <option value="">Tutti</option>
                            <option value="1">Solo Autorizzati</option>
                            <option value="0">Solo Negati</option>
                        </select>
                    </div>
                </div>
                <div class="grid grid-2">
                    <div class="form-group">
                        <label class="form-label" for="filter-search">Ricerca (Nome/CF)</label>
                        <input type="text" class="form-control" id="filter-search" name="search" placeholder="Cerca per nome o codice fiscale">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="filter-limit">Risultati per pagina</label>
                        <select class="form-control form-select" id="filter-limit" name="limit">
                            <option value="50">50</option>
                            <option value="100">100</option>
                            <option value="200">200</option>
                            <option value="500">500</option>
                        </select>
                    </div>
                </div>
                <div class="mt-3">
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-search"></i> Applica Filtri
                    </button>
                    <button type="button" class="btn btn-secondary" onclick="resetFilters()">
                        <i class="fas fa-undo"></i> Reset
                    </button>
                    <button type="button" class="btn btn-success" onclick="exportData()">
                        <i class="fas fa-download"></i> Esporta Excel
                    </button>
                </div>
            </form>
        </div>
        
        <!-- Configurazione Campi Visibili -->
        {% if 'all' in permissions %}
        <div class="card">
            <h4><i class="fas fa-eye"></i> Configurazione Campi Visibili</h4>
            <form id="fields-config-form">
                <div class="grid grid-3">
                    <label><input type="checkbox" name="fields" value="timestamp" checked> Data/Ora</label>
                    <label><input type="checkbox" name="fields" value="codice_fiscale" checked> Codice Fiscale</label>
                    <label><input type="checkbox" name="fields" value="autorizzato" checked> Stato Autorizzazione</label>
                    <label><input type="checkbox" name="fields" value="nome_cognome" checked> Nome Cognome</label>
                    <label><input type="checkbox" name="fields" value="comune" checked> Comune</label>
                    <label><input type="checkbox" name="fields" value="motivo_blocco"> Motivo Blocco</label>
                    <label><input type="checkbox" name="fields" value="tempo_elaborazione"> Tempo Elaborazione</label>
                    <label><input type="checkbox" name="fields" value="hardware_status"> Stato Hardware</label>
                    <label><input type="checkbox" name="fields" value="ip_address"> Indirizzo IP</label>
                </div>
                <button type="submit" class="btn btn-success mt-3">
                    <i class="fas fa-save"></i> Salva Configurazione Campi
                </button>
            </form>
        </div>
        {% endif %}
        
        <!-- Statistiche Rapide -->
        <div class="card">
            <h4><i class="fas fa-chart-bar"></i> Statistiche Periodo Selezionato</h4>
            <div id="log-stats" class="grid grid-4">
                <div class="loading">Caricamento statistiche...</div>
            </div>
        </div>
        
        <!-- Tabella Log Accessi -->
        <div class="card">
            <h4><i class="fas fa-table"></i> Log Accessi</h4>
            <div id="log-table-container">
                <div class="loading">Caricamento log accessi...</div>
            </div>
            
            <!-- Paginazione -->
            <div id="pagination" class="text-center mt-3">
                <!-- Caricata dinamicamente -->
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    let currentPage = 1;
    let totalPages = 1;
    
    document.addEventListener('DOMContentLoaded', function() {
        loadLogFields();
        setDefaultDateRange();
        loadLogData();
        loadLogStats();
    });
    
    function setDefaultDateRange() {
        const today = new Date();
        const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
        
        document.getElementById('filter-date-from').value = weekAgo.toISOString().split('T')[0];
        document.getElementById('filter-date-to').value = today.toISOString().split('T')[0];
    }
    
    async function loadLogFields() {
        try {
            const response = await fetch('/api/log/fields-config');
            const data = await response.json();
            
            if (data.success) {
                const checkboxes = document.querySelectorAll('input[name="fields"]');
                checkboxes.forEach(cb => {
                    cb.checked = data.visible_fields.includes(cb.value);
                });
            }
        } catch (error) {
            console.error('Errore caricamento configurazione campi:', error);
        }
    }
    
    async function loadLogData(page = 1) {
        currentPage = page;
        
        try {
            const formData = new FormData(document.getElementById('filter-form'));
            const params = new URLSearchParams();
            
            for (let [key, value] of formData.entries()) {
                if (value) params.append(key, value);
            }
            params.append('page', page);
            
            const response = await fetch(`/api/log/data?${params.toString()}`);
            const data = await response.json();
            
            if (data.success) {
                renderLogTable(data.logs, data.visible_fields);
                renderPagination(data.pagination);
                totalPages = data.pagination.total_pages;
            } else {
                document.getElementById('log-table-container').innerHTML = 
                    '<div class="alert alert-danger">Errore caricamento log</div>';
            }
        } catch (error) {
            console.error('Errore caricamento log:', error);
            document.getElementById('log-table-container').innerHTML = 
                '<div class="alert alert-danger">Errore comunicazione</div>';
        }
    }
    
    function renderLogTable(logs, visibleFields) {
        const container = document.getElementById('log-table-container');
        
        if (logs.length === 0) {
            container.innerHTML = '<div class="alert alert-info">Nessun log trovato per i filtri selezionati</div>';
            return;
        }
        
        let html = '<div class="table-responsive"><table class="table"><thead><tr>';
        
        // Headers dinamici basati sui campi visibili
        if (visibleFields.includes('timestamp')) html += '<th>Data/Ora</th>';
        if (visibleFields.includes('codice_fiscale')) html += '<th>Codice Fiscale</th>';
        if (visibleFields.includes('nome_cognome')) html += '<th>Nome</th>';
        if (visibleFields.includes('autorizzato')) html += '<th>Stato</th>';
        if (visibleFields.includes('comune')) html += '<th>Comune</th>';
        if (visibleFields.includes('motivo_blocco')) html += '<th>Motivo</th>';
        if (visibleFields.includes('tempo_elaborazione')) html += '<th>Tempo (ms)</th>';
        
        html += '</tr></thead><tbody>';
        
        logs.forEach(log => {
            html += '<tr>';
            if (visibleFields.includes('timestamp')) {
                html += `<td><small>${new Date(log.timestamp).toLocaleString('it-IT')}</small></td>`;
            }
            if (visibleFields.includes('codice_fiscale')) {
                const maskedCF = log.codice_fiscale ? 
                    `${log.codice_fiscale.substr(0, 4)}***${log.codice_fiscale.substr(-4)}` : 
                    'N/A';
                html += `<td><small>${maskedCF}</small></td>`;
            }
            if (visibleFields.includes('nome_cognome')) {
                html += `<td>${log.nome_cognome || 'N/A'}</td>`;
            }
            if (visibleFields.includes('autorizzato')) {
                const status = log.autorizzato ? 
                    '<span class="status-badge status-online">✅ Autorizzato</span>' :
                    '<span class="status-badge status-offline">❌ Negato</span>';
                html += `<td>${status}</td>`;
            }
            if (visibleFields.includes('comune')) {
                html += `<td><small>${log.comune || 'N/A'}</small></td>`;
            }
            if (visibleFields.includes('motivo_blocco')) {
                html += `<td><small class="text-muted">${log.motivo_blocco || '-'}</small></td>`;
            }
            if (visibleFields.includes('tempo_elaborazione')) {
                html += `<td><small>${log.tempo_elaborazione || '-'}</small></td>`;
            }
            html += '</tr>';
        });
        
        html += '</tbody></table></div>';
        container.innerHTML = html;
    }
    
    function renderPagination(pagination) {
        const container = document.getElementById('pagination');
        
        if (pagination.total_pages <= 1) {
            container.innerHTML = '';
            return;
        }
        
        let html = '<div class="btn-group">';
        
        // Precedente
        if (pagination.current_page > 1) {
            html += `<button class="btn btn-secondary" onclick="loadLogData(${pagination.current_page - 1})">
                        <i class="fas fa-chevron-left"></i> Precedente
                     </button>`;
        }
        
        // Numeri pagina
        const start = Math.max(1, pagination.current_page - 2);
        const end = Math.min(pagination.total_pages, pagination.current_page + 2);
        
        for (let i = start; i <= end; i++) {
            const active = i === pagination.current_page ? 'btn-primary' : 'btn-secondary';
            html += `<button class="btn ${active}" onclick="loadLogData(${i})">${i}</button>`;
        }
        
        // Successivo
        if (pagination.current_page < pagination.total_pages) {
            html += `<button class="btn btn-secondary" onclick="loadLogData(${pagination.current_page + 1})">
                        Successivo <i class="fas fa-chevron-right"></i>
                     </button>`;
        }
        
        html += '</div>';
        html += `<div class="mt-2"><small class="text-muted">
                    Pagina ${pagination.current_page} di ${pagination.total_pages} 
                    (${pagination.total_records} record totali)
                 </small></div>`;
        
        container.innerHTML = html;
    }
    
    async function loadLogStats() {
        try {
            const formData = new FormData(document.getElementById('filter-form'));
            const params = new URLSearchParams();
            
            for (let [key, value] of formData.entries()) {
                if (value) params.append(key, value);
            }
            
            const response = await fetch(`/api/log/stats?${params.toString()}`);
            const data = await response.json();
            
            if (data.success) {
                const container = document.getElementById('log-stats');
                container.innerHTML = `
                    <div class="card text-center" style="padding: 15px;">
                        <strong>Totale Accessi</strong><br>
                        <span style="font-size: 1.5em; color: #667eea;">${data.stats.total}</span>
                    </div>
                    <div class="card text-center" style="padding: 15px;">
                        <strong>Autorizzati</strong><br>
                        <span style="font-size: 1.5em; color: #27ae60;">${data.stats.authorized}</span>
                    </div>
                    <div class="card text-center" style="padding: 15px;">
                        <strong>Negati</strong><br>
                        <span style="font-size: 1.5em; color: #e74c3c;">${data.stats.denied}</span>
                    </div>
                    <div class="card text-center" style="padding: 15px;">
                        <strong>Tasso Successo</strong><br>
                        <span style="font-size: 1.5em; color: #f39c12;">${data.stats.success_rate}%</span>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Errore caricamento statistiche:', error);
        }
    }
    
    function resetFilters() {
        document.getElementById('filter-form').reset();
        setDefaultDateRange();
        loadLogData(1);
        loadLogStats();
    }
    
    async function exportData() {
        try {
            const formData = new FormData(document.getElementById('filter-form'));
            const params = new URLSearchParams();
            
            for (let [key, value] of formData.entries()) {
                if (value) params.append(key, value);
            }
            params.append('export', 'excel');
            
            const response = await fetch(`/api/log/export?${params.toString()}`);
            const blob = await response.blob();
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `log-accessi-${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showAlert('Export completato', 'success');
        } catch (error) {
            showAlert('Errore durante export', 'danger');
        }
    }
    
    // Event listeners
    document.getElementById('filter-form').addEventListener('submit', function(e) {
        e.preventDefault();
        loadLogData(1);
        loadLogStats();
    });
    
    document.getElementById('fields-config-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const visibleFields = formData.getAll('fields');
        
        try {
            const response = await fetch('/api/log/save-fields-config', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({visible_fields: visibleFields})
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert('Configurazione campi salvata', 'success');
                loadLogData(currentPage);
            } else {
                showAlert('Errore salvataggio configurazione', 'danger');
            }
        } catch (error) {
            showAlert('Errore comunicazione', 'danger');
        }
    });
</script>
{% endblock %}
"""
