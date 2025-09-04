// File: /opt/access_control/src/api/static/js/user-management.js
// Gestione utenti viewer

document.addEventListener('DOMContentLoaded', function() {
    if (session.role === 'user_manager') {
        loadViewers();
        setupCreateForm();
    }
});

function loadViewers() {
    fetch('/api/viewers/list')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderViewersTable(data.viewers);
            }
        })
        .catch(error => console.error('Errore caricamento viewers:', error));
}

function renderViewersTable(viewers) {
    const tbody = document.getElementById('viewers-table');
    
    if (viewers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">Nessun visualizzatore trovato</td></tr>';
        return;
    }
    
    let html = '';
    viewers.forEach(viewer => {
        const statusBadge = viewer.active ? 
            '<span class="badge bg-success">Attivo</span>' : 
            '<span class="badge bg-danger">Disattivato</span>';
        
        html += `
            <tr>
                <td><strong>${viewer.username}</strong></td>
                <td>${viewer.created_by}</td>
                <td>${formatDate(viewer.created_at)}</td>
                <td>${viewer.last_login}</td>
                <td>${statusBadge}</td>
                <td>
                    <button class="btn btn-warning btn-sm" onclick="resetPassword('${viewer.username}')">
                        <i class="fas fa-key"></i> Reset Password
                    </button>
                    <button class="btn btn-${viewer.active ? 'danger' : 'success'} btn-sm" 
                            onclick="toggleActive('${viewer.username}')">
                        <i class="fas fa-${viewer.active ? 'ban' : 'check'}"></i>
                        ${viewer.active ? 'Disattiva' : 'Attiva'}
                    </button>
                </td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

function setupCreateForm() {
    const form = document.getElementById('create-viewer-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('new-username').value.trim().toLowerCase();
            
            try {
                const response = await fetch('/api/viewers/create', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username: username})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showTempPassword(username, data.temp_password);
                    form.reset();
                    loadViewers();
                } else {
                    showAlert(data.error, 'danger');
                }
            } catch (error) {
                showAlert('Errore creazione utente', 'danger');
            }
        });
    }
}

function resetPassword(username) {
    if (confirm(`Resettare la password per ${username}?`)) {
        fetch('/api/viewers/reset-password', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: username})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showTempPassword(username, data.temp_password);
            } else {
                showAlert(data.error, 'danger');
            }
        });
    }
}

function toggleActive(username) {
    fetch('/api/viewers/toggle-active', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: username})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message, 'success');
            loadViewers();
        } else {
            showAlert(data.error, 'danger');
        }
    });
}

function showTempPassword(username, password) {
    document.getElementById('temp-username').textContent = username;
    document.getElementById('temp-password').textContent = password;
    
    const modal = new bootstrap.Modal(document.getElementById('tempPasswordModal'));
    modal.show();
}

function copyTempPassword() {
    const password = document.getElementById('temp-password').textContent;
    navigator.clipboard.writeText(password).then(() => {
        showAlert('Password copiata negli appunti', 'success');
    });
}

function formatDate(dateString) {
    if (!dateString) return 'N/D';
    const date = new Date(dateString);
    return date.toLocaleDateString('it-IT') + ' ' + date.toLocaleTimeString('it-IT');
}
