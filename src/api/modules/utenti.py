# File: /opt/access_control/src/api/modules/utenti.py
# Modulo Gestione Utenti con 3 Livelli - Dashboard

from flask import render_template_string, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from ..web_api import app, require_auth, require_permission, config_manager, get_base_template, USER_ROLES

# ===============================
# TEMPLATE GESTIONE UTENTI
# ===============================

UTENTI_TEMPLATE = get_base_template() + """
{% block title %}Gestione Utenti - Sistema Controllo Accessi{% endblock %}

{% block content %}
<div class="header">
    <h1><i class="fas fa-users"></i> {{ island_name }}</h1>
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
                <a href="/dispositivi" class="nav-link">
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
            <li class="nav-item">
                <a href="/utenti" class="nav-link active">
                    <i class="fas fa-users"></i>
                    <span>Utenti</span>
                </a>
            </li>
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
        <h2><i class="fas fa-users-cog"></i> Gestione Utenti Dashboard</h2>
        
        <!-- Informazioni Ruoli -->
        <div class="card">
            <h4><i class="fas fa-info-circle"></i> Livelli Utenti Sistema</h4>
            <div class="grid grid-3">
                <div class="alert alert-info">
                    <strong><i class="fas fa-crown"></i> Amministratore</strong><br>
                    <small>Accesso completo a tutte le funzioni. Può gestire utenti, configurazioni e sistema.</small>
                </div>
                <div class="alert alert-warning">
                    <strong><i class="fas fa-user-tie"></i> Gestore Utenti</strong><br>
                    <small>Può gestire utenti, visualizzare log e configurare email. No accesso configurazioni hardware.</small>
                </div>
                <div class="alert alert-success">
                    <strong><i class="fas fa-eye"></i> Solo Visualizzazione</strong><br>
                    <small>Può solo visualizzare panoramica e log accessi. Nessuna modifica consentita.</small>
                </div>
            </div>
        </div>
        
        <!-- Nuovo Utente -->
        {% if 'all' in permissions or 'users' in permissions %}
        <div class="card">
            <h4><i class="fas fa-user-plus"></i> Aggiungi Nuovo Utente</h4>
            <form id="new-user-form">
                <div class="grid grid-2">
                    <div class="form-group">
                        <label class="form-label" for="new-username">Username</label>
                        <input type="text" class="form-control" id="new-username" name="username" 
                               required minlength="3" maxlength="20" 
                               pattern="[a-zA-Z0-9_]+" 
                               placeholder="Username (solo lettere, numeri, _)">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="new-password">Password</label>
                        <input type="password" class="form-control" id="new-password" name="password" 
                               required minlength="6" placeholder="Password (min 6 caratteri)">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="new-password-confirm">Conferma Password</label>
                        <input type="password" class="form-control" id="new-password-confirm" name="password_confirm" 
                               required placeholder="Ripeti password">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="new-role">Ruolo Utente</label>
                        <select class="form-control form-select" id="new-role" name="role" required>
                            {% if 'all' in permissions %}
                            <option value="admin">👑 Amministratore</option>
                            {% endif %}
                            <option value="manager">👔 Gestore Utenti</option>
                            <option value="viewer">👁️ Solo Visualizzazione</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label" for="new-note">Note (opzionale)</label>
                    <input type="text" class="form-control" id="new-note" name="note" 
                           placeholder="Note aggiuntive sull'utente">
                </div>
                <button type="submit" class="btn btn-success">
                    <i class="fas fa-user-plus"></i> Crea Utente
                </button>
            </form>
        </div>
        {% endif %}
        
        <!-- Lista Utenti Esistenti -->
        <div class="card">
            <h4><i class="fas fa-list"></i> Utenti Esistenti</h4>
            <div class="table-responsive">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Username</th>
                            <th>Ruolo</th>
                            <th>Ultimo Accesso</th>
                            <th>Stato</th>
                            <th>Note</th>
                            {% if 'all' in permissions or 'users' in permissions %}
                            <th>Azioni</th>
                            {% endif %}
                        </tr>
                    </thead>
                    <tbody id="users-table-body">
                        <tr>
                            <td colspan="6" class="text-center">
                                <span class="loading">Caricamento utenti...</span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Statistiche Accessi Utenti -->
        <div class="card">
            <h4><i class="fas fa-chart-pie"></i> Statistiche Accessi per Ruolo</h4>
            <div id="user-stats" class="grid grid-3">
                <div class="loading">Caricamento statistiche...</div>
            </div>
        </div>
        
        <!-- Log Attività Utenti Dashboard -->
        <div class="card">
            <h4><i class="fas fa-history"></i> Log Attività Dashboard</h4>
            <p class="text-muted">Ultime attività degli utenti sulla dashboard amministrativa</p>
            <div id="dashboard-activity-log">
                <div class="loading">Caricamento log attività...</div>
            </div>
        </div>
    </div>
</div>

<!-- Modal Modifica Utente -->
<div id="edit-user-modal" class="modal" style="display: none;">
    <div class="modal-content" style="max-width: 500px; margin: 5% auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h4><i class="fas fa-user-edit"></i> Modifica Utente</h4>
            <button onclick="closeEditModal()" style="border: none; background: none; font-size: 1.5em; cursor: pointer;">&times;</button>
        </div>
        
        <form id="edit-user-form">
            <input type="hidden" id="edit-username" name="username">
            
            <div class="form-group">
                <label class="form-label" for="edit-new-password">Nuova Password (lascia vuoto per non modificare)</label>
                <input type="password" class="form-control" id="edit-new-password" name="new_password" 
                       minlength="6" placeholder="Nuova password">
            </div>
            
            <div class="form-group">
                <label class="form-label" for="edit-role">Ruolo</label>
                <select class="form-control form-select" id="edit-role" name="role">
                    {% if 'all' in permissions %}
                    <option value="admin">👑 Amministratore</option>
                    {% endif %}
                    <option value="manager">👔 Gestore Utenti</option>
                    <option value="viewer">👁️ Solo Visualizzazione</option>
                </select>
            </div>
            
            <div class="form-group">
                <label class="form-label" for="edit-note">Note</label>
                <input type="text" class="form-control" id="edit-note" name="note" placeholder="Note">
            </div>
            
            <div class="form-group">
                <label class="form-label">
                    <input type="checkbox" id="edit-active" name="active" checked>
                    Utente attivo
                </label>
            </div>
            
            <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px;">
                <button type="button" class="btn btn-secondary" onclick="closeEditModal()">
                    <i class="fas fa-times"></i> Annulla
                </button>
                <button type="submit" class="btn btn-success">
                    <i class="fas fa-save"></i> Salva Modifiche
                </button>
            </div>
        </form>
    </div>
</div>

<!-- Overlay Modal -->
<div id="modal-overlay" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 9999;"></div>

{% endblock %}

{% block extra_js %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        loadUsers();
        loadUserStats();
        loadDashboardActivityLog();
    });
    
    // Carica lista utenti
    async function loadUsers() {
        try {
            const response = await fetch('/api/users/list');
            const data = await response.json();
            
            if (data.success) {
                const tbody = document.getElementById('users-table-body');
                let html = '';
                
                data.users.forEach(user => {
                    const roleInfo = getRoleInfo(user.ruolo);
                    const lastAccess = user.ultimo_accesso ? 
                        new Date(user.ultimo_accesso).toLocaleString('it-IT') : 
                        'Mai';
                    
                    html += `
                        <tr>
                            <td>
                                <strong>${user.username}</strong>
                                ${user.username === '{{ session.username }}' ? '<small class="text-muted">(Tu)</small>' : ''}
                            </td>
                            <td>
                                <span class="status-badge ${roleInfo.class}">
                                    ${roleInfo.icon} ${roleInfo.name}
                                </span>
                            </td>
                            <td><small>${lastAccess}</small></td>
                            <td>
                                <span class="status-badge ${user.attivo ? 'status-online' : 'status-offline'}">
                                    ${user.attivo ? '✅ Attivo' : '❌ Inattivo'}
                                </span>
                            </td>
                            <td><small class="text-muted">${user.note || '-'}</small></td>
                            {% if 'all' in permissions or 'users' in permissions %}
                            <td>
                                <button class="btn btn-warning btn-sm" onclick="editUser('${user.username}')">
                                    <i class="fas fa-edit"></i>
                                </button>
                                ${user.username !== '{{ session.username }}' ? `
                                    <button class="btn btn-danger btn-sm" onclick="deleteUser('${user.username}')">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                ` : ''}
                            </td>
                            {% endif %}
                        </tr>
                    `;
                });
                
                tbody.innerHTML = html || '<tr><td colspan="6" class="text-center text-muted">Nessun utente trovato</td></tr>';
            }
        } catch (error) {
            console.error('Errore caricamento utenti:', error);
            document.getElementById('users-table-body').innerHTML = 
                '<tr><td colspan="6" class="text-center text-muted">Errore caricamento</td></tr>';
        }
    }
    
    function getRoleInfo(role) {
        const roles = {
            'admin': { name: 'Amministratore', icon: '👑', class: 'status-warning' },
            'manager': { name: 'Gestore Utenti', icon: '👔', class: 'status-online' },
            'viewer': { name: 'Solo Visualizzazione', icon: '👁️', class: 'status-offline' }
        };
        return roles[role] || { name: 'Sconosciuto', icon: '❓', class: 'status-offline' };
    }
    
    // Carica statistiche utenti
    async function loadUserStats() {
        try {
            const response = await fetch('/api/users/stats');
            const data = await response.json();
            
            if (data.success) {
                const container = document.getElementById('user-stats');
                let html = '';
                
                Object.entries(data.stats).forEach(([role, count]) => {
                    const roleInfo = getRoleInfo(role);
                    html += `
                        <div class="card" style="padding: 15px; text-align: center;">
                            <strong>${roleInfo.icon} ${roleInfo.name}</strong><br>
                            <span style="font-size: 1.5em; color: #667eea;">${count}</span><br>
                            <small class="text-muted">utenti</small>
                        </div>
                    `;
                });
                
                container.innerHTML = html;
            }
        } catch (error) {
            console.error('Errore caricamento statistiche:', error);
        }
    }
    
    // Carica log attività dashboard
    async function loadDashboardActivityLog() {
        try {
            const response = await fetch('/api/users/dashboard-activity');
            const data = await response.json();
            
            if (data.success && data.activities.length > 0) {
                const container = document.getElementById('dashboard-activity-log');
                let html = '<div class="table-responsive"><table class="table"><thead><tr><th>Orario</th><th>Utente</th><th>Azione</th></tr></thead><tbody>';
                
                data.activities.forEach(activity => {
                    html += `
                        <tr>
                            <td><small>${new Date(activity.timestamp).toLocaleString('it-IT')}</small></td>
                            <td>${activity.username}</td>
                            <td><small>${activity.action}</small></td>
                        </tr>
                    `;
                });
                
                html += '</tbody></table></div>';
                container.innerHTML = html;
            } else {
                document.getElementById('dashboard-activity-log').innerHTML = 
                    '<p class="text-muted">Nessuna attività recente</p>';
            }
        } catch (error) {
            console.error('Errore caricamento log attività:', error);
        }
    }
    
    // Nuovo utente
    document.getElementById('new-user-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const password = formData.get('password');
        const passwordConfirm = formData.get('password_confirm');
        
        if (password !== passwordConfirm) {
            showAlert('Le password non corrispondono', 'danger');
            return;
        }
        
        const userData = {
            username: formData.get('username'),
            password: password,
            role: formData.get('role'),
            note: formData.get('note') || ''
        };
        
        try {
            const response = await fetch('/api/users/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(userData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert('Utente creato con successo', 'success');
                this.reset();
                loadUsers();
                loadUserStats();
            } else {
                showAlert(data.error || 'Errore creazione utente', 'danger');
            }
        } catch (error) {
            showAlert('Errore comunicazione', 'danger');
        }
    });
    
    // Modifica utente
    async function editUser(username) {
        try {
            const response = await fetch(`/api/users/get/${username}`);
            const data = await response.json();
            
            if (data.success) {
                document.getElementById('edit-username').value = username;
                document.getElementById('edit-role').value = data.user.ruolo;
                document.getElementById('edit-note').value = data.user.note || '';
                document.getElementById('edit-active').checked = data.user.attivo;
                document.getElementById('edit-new-password').value = '';
                
                showEditModal();
            } else {
                showAlert('Errore caricamento dati utente', 'danger');
            }
        } catch (error) {
            showAlert('Errore comunicazione', 'danger');
        }
    }
    
    function showEditModal() {
        document.getElementById('modal-overlay').style.display = 'block';
        document.getElementById('edit-user-modal').style.display = 'block';
    }
    
    function closeEditModal() {
        document.getElementById('modal-overlay').style.display = 'none';
        document.getElementById('edit-user-modal').style.display = 'none';
    }
    
    // Salva modifiche utente
    document.getElementById('edit-user-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const userData = {
            username: formData.get('username'),
            role: formData.get('role'),
            note: formData.get('note'),
            active: formData.get('active') === 'on'
        };
        
        if (formData.get('new_password')) {
            userData.new_password = formData.get('new_password');
        }
        
        try {
            const response = await fetch('/api/users/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(userData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert('Utente aggiornato con successo', 'success');
                closeEditModal();
                loadUsers();
                loadUserStats();
            } else {
                showAlert(data.error || 'Errore aggiornamento utente', 'danger');
            }
        } catch (error) {
            showAlert('Errore comunicazione', 'danger');
        }
    });
    
    // Elimina utente
    async function deleteUser(username) {
        if (confirm(`Sei sicuro di voler eliminare l'utente "${username}"?`)) {
            try {
                const response = await fetch('/api/users/delete', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username: username})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showAlert('Utente eliminato con successo', 'success');
                    loadUsers();
                    loadUserStats();
                } else {
                    showAlert(data.error || 'Errore eliminazione utente', 'danger');
                }
            } catch (error) {
                showAlert('Errore comunicazione', 'danger');
            }
        }
    }
    
    // Chiudi modal cliccando sull'overlay
    document.getElementById('modal-overlay').addEventListener('click', closeEditModal);
</script>
{% endblock %}
"""

# ===============================
# ROUTES GESTIONE UTENTI
# ===============================

@app.route('/utenti')
@require_auth
@require_permission('users')
def utenti():
    """Pagina gestione utenti"""
    nome_isola = config_manager.get('sistema.nome_isola', '')
    if not nome_isola:
        nome_isola = "Isola Ecologica"
    else:
        nome_isola = f"Isola Ecologica {nome_isola}"
    
    user_role = session.get('role', 'viewer')
    user_role_name = USER_ROLES.get(user_role, {}).get('name', 'Utente')
    permissions = session.get('permissions', [])
    
    return render_template_string(UTENTI_TEMPLATE, 
                                island_name=nome_isola,
                                user_role_name=user_role_name,
                                permissions=permissions,
                                session=session)

# ===============================
# API ENDPOINTS UTENTI
# ===============================

@app.route('/api/users/list')
@require_auth
@require_permission('users')
def api_users_list():
    """Lista utenti dashboard"""
    try:
        utenti = config_manager.get('utenti', {})
        users_list = []
        
        for username, user_data in utenti.items():
            users_list.append({
                'username': username,
                'ruolo': user_data.get('ruolo', 'viewer'),
                'ultimo_accesso': user_data.get('ultimo_accesso'),
                'attivo': user_data.get('attivo', True),
                'note': user_data.get('note', '')
            })
        
        return jsonify({
            'success': True,
            'users': users_list
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/stats')
@require_auth
@require_permission('users')
def api_users_stats():
    """Statistiche utenti per ruolo"""
    try:
        utenti = config_manager.get('utenti', {})
        stats = {'admin': 0, 'manager': 0, 'viewer': 0}
        
        for user_data in utenti.values():
            role = user_data.get('ruolo', 'viewer')
            if role in stats:
                stats[role] += 1
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/dashboard-activity')
@require_auth
@require_permission('users')
def api_dashboard_activity():
    """Log attività dashboard (mock data per ora)"""
    try:
        # Per ora restituiamo dati mock
        # In futuro qui andrà implementato un vero sistema di logging
        activities = []
        
        return jsonify({
            'success': True,
            'activities': activities
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/create', methods=['POST'])
@require_auth
@require_permission('users')
def api_create_user():
    """Crea nuovo utente"""
    try:
        data = request.get_json()
        
        # Validazione
        username = data.get('username', '').strip()
        password = data.get('password', '')
        role = data.get('role', 'viewer')
        note = data.get('note', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username e password sono obbligatori'}), 400
        
        if len(username) < 3 or len(password) < 6:
            return jsonify({'success': False, 'error': 'Username min 3 caratteri, password min 6'}), 400
        
        if role not in USER_ROLES:
            return jsonify({'success': False, 'error': 'Ruolo non valido'}), 400
        
        # Verifica che l'utente non esista già
        utenti = config_manager.get('utenti', {})
        if username in utenti:
            return jsonify({'success': False, 'error': 'Username già esistente'}), 400
        
        # Solo admin può creare altri admin
        if role == 'admin' and session.get('role') != 'admin':
            return jsonify({'success': False, 'error': 'Solo admin può creare amministratori'}), 403
        
        # Crea utente
        user_data = {
            'password_hash': generate_password_hash(password),
            'ruolo': role,
            'ultimo_accesso': None,
            'attivo': True,
            'note': note,
            'creato_da': session.get('username'),
            'creato_il': datetime.now().isoformat()
        }
        
        config_manager.set(f'utenti.{username}', user_data)
        
        return jsonify({
            'success': True,
            'message': f'Utente {username} creato con successo'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/get/<username>')
@require_auth
@require_permission('users')
def api_get_user(username):
    """Ottieni dati utente"""
    try:
        utenti = config_manager.get('utenti', {})
        
        if username not in utenti:
            return jsonify({'success': False, 'error': 'Utente non trovato'}), 404
        
        user_data = utenti[username].copy()
        # Rimuovi password hash per sicurezza
        user_data.pop('password_hash', None)
        
        return jsonify({
            'success': True,
            'user': user_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/update', methods=['POST'])
@require_auth
@require_permission('users')
def api_update_user():
    """Aggiorna utente esistente"""
    try:
        data = request.get_json()
        
        username = data.get('username', '').strip()
        role = data.get('role', 'viewer')
        note = data.get('note', '').strip()
        active = data.get('active', True)
        new_password = data.get('new_password', '').strip()
        
        if not username:
            return jsonify({'success': False, 'error': 'Username richiesto'}), 400
        
        # Verifica che l'utente esista
        utenti = config_manager.get('utenti', {})
        if username not in utenti:
            return jsonify({'success': False, 'error': 'Utente non trovato'}), 404
        
        # Solo admin può modificare altri admin o creare admin
        if (role == 'admin' or utenti[username].get('ruolo') == 'admin') and session.get('role') != 'admin':
            return jsonify({'success': False, 'error': 'Solo admin può gestire amministratori'}), 403
        
        # Non si può disattivare se stesso
        if username == session.get('username') and not active:
            return jsonify({'success': False, 'error': 'Non puoi disattivare il tuo account'}), 400
        
        # Aggiorna dati
        user_data = utenti[username]
        user_data['ruolo'] = role
        user_data['note'] = note
        user_data['attivo'] = active
        user_data['modificato_da'] = session.get('username')
        user_data['modificato_il'] = datetime.now().isoformat()
        
        # Aggiorna password se fornita
        if new_password:
            if len(new_password) < 6:
                return jsonify({'success': False, 'error': 'Password deve essere almeno 6 caratteri'}), 400
            user_data['password_hash'] = generate_password_hash(new_password)
        
        config_manager.set(f'utenti.{username}', user_data)
        
        return jsonify({
            'success': True,
            'message': f'Utente {username} aggiornato con successo'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/delete', methods=['POST'])
@require_auth
@require_permission('users')
def api_delete_user():
    """Elimina utente"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({'success': False, 'error': 'Username richiesto'}), 400
        
        # Non si può eliminare se stesso
        if username == session.get('username'):
            return jsonify({'success': False, 'error': 'Non puoi eliminare il tuo account'}), 400
        
        # Verifica che l'utente esista
        utenti = config_manager.get('utenti', {})
        if username not in utenti:
            return jsonify({'success': False, 'error': 'Utente non trovato'}), 404
        
        # Solo admin può eliminare altri admin
        if utenti[username].get('ruolo') == 'admin' and session.get('role') != 'admin':
            return jsonify({'success': False, 'error': 'Solo admin può eliminare amministratori'}), 403
        
        # Elimina utente
        del utenti[username]
        config_manager.set('utenti', utenti)
        
        return jsonify({
            'success': True,
            'message': f'Utente {username} eliminato con successo'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
