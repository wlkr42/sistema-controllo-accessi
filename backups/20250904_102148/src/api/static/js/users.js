// Gestione utenti sistema
let usersTable = document.getElementById('users-table');

// Carica conteggi utenti
function loadUserCounts() {
    fetch('/api/users/list')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const counts = {
                    admin: 0,
                    user_manager: 0,
                    viewer: 0,
                    total: 0
                };
                
                data.users.forEach(user => {
                    counts[user.role]++;
                    counts.total++;
                });

                document.getElementById('admin-count').textContent = counts.admin;
                document.getElementById('manager-count').textContent = counts.user_manager;
                document.getElementById('viewer-count').textContent = counts.viewer;
                document.getElementById('total-count').textContent = counts.total;
            }
        })
        .catch(error => console.error('Errore caricamento conteggi:', error));
}

// Carica lista utenti
function loadUsers() {
    fetch('/api/users/list')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let html = '';
                data.users.forEach(user => {
                    const roleBadge = getRoleBadge(user.role, user.role_name);
                    const statusBadge = getStatusBadge(user.attivo);
                    
                    html += `
                        <tr>
                            <td>${user.username}</td>
                            <td>${roleBadge}</td>
                            <td>
                                <small class="text-muted">
                                    ${user.created_by}<br>
                                    ${formatDate(user.created_at)}
                                </small>
                            </td>
                            <td>
                                <small class="text-muted">
                                    ${formatDate(user.last_login)}
                                </small>
                            </td>
                            <td>${statusBadge}</td>
                            <td class="text-end">
                                ${getUserActions(user)}
                            </td>
                        </tr>
                    `;
                });
                usersTable.innerHTML = html;

                // Inizializza tooltip e popover
                const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
                tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));
            }
        })
        .catch(error => console.error('Errore caricamento utenti:', error));
}

// Formatta data
function formatDate(dateStr) {
    if (!dateStr || dateStr === 'Mai') return 'Mai';
    const date = new Date(dateStr);
    return date.toLocaleString('it-IT', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Badge ruolo
function getRoleBadge(role, roleName) {
    const badges = {
        admin: 'role-badge role-admin',
        user_manager: 'role-badge role-manager',
        viewer: 'role-badge role-viewer'
    };
    return `<span class="${badges[role]}">${roleName}</span>`;
}

// Badge stato
function getStatusBadge(active) {
    return active 
        ? '<span class="badge bg-success">Attivo</span>'
        : '<span class="badge bg-danger">Disattivato</span>';
}

// Pulsanti azioni
function getUserActions(user) {
    const btnSize = 'btn-sm';
    return `
        <div class="btn-group">
            ${user.attivo 
                ? `<button class="btn ${btnSize} btn-outline-danger" 
                     onclick="toggleUserStatus('${user.username}', false)"
                     data-bs-toggle="tooltip" title="Disattiva">
                     <i class="fas fa-ban"></i>
                   </button>`
                : `<button class="btn ${btnSize} btn-outline-success" 
                     onclick="toggleUserStatus('${user.username}', true)"
                     data-bs-toggle="tooltip" title="Attiva">
                     <i class="fas fa-check"></i>
                   </button>`
            }
            <button class="btn ${btnSize} btn-outline-primary" 
                    onclick="resetPassword('${user.username}')"
                    data-bs-toggle="tooltip" title="Reset Password">
                <i class="fas fa-key"></i>
            </button>
            <button class="btn ${btnSize} btn-outline-danger" 
                    onclick="deleteUser('${user.username}')"
                    data-bs-toggle="tooltip" title="Elimina">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
}

// Crea nuovo utente
document.getElementById('create-user-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const data = {
        username: document.getElementById('new-username').value,
        password: document.getElementById('new-password').value,
        role: document.getElementById('new-role').value
    };
    
    fetch('/api/users/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Reset form
            e.target.reset();
            
            // Ricarica dati
            loadUsers();
            loadUserCounts();
            
            // Mostra password temporanea
            document.getElementById('temp-username').textContent = data.username;
            document.getElementById('temp-password').textContent = data.password;
            new bootstrap.Modal(document.getElementById('tempPasswordModal')).show();
        } else {
            alert(data.error || 'Errore creazione utente');
        }
    })
    .catch(error => {
        console.error('Errore creazione utente:', error);
        alert('Errore durante la creazione utente');
    });
});

// Attiva/disattiva utente
function toggleUserStatus(username, active) {
    if (!confirm(`${active ? 'Attivare' : 'Disattivare'} l'utente ${username}?`)) return;
    
    fetch('/api/users/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            attivo: active
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadUsers();
        } else {
            alert(data.error || 'Errore aggiornamento stato');
        }
    })
    .catch(error => {
        console.error('Errore aggiornamento stato:', error);
        alert('Errore durante l\'aggiornamento');
    });
}

// Reset password
function resetPassword(username) {
    if (!confirm(`Resettare la password per l'utente ${username}?`)) return;
    
    const tempPassword = generateTempPassword();
    
    fetch('/api/users/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            password: tempPassword
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('temp-username').textContent = username;
            document.getElementById('temp-password').textContent = data.password;
            new bootstrap.Modal(document.getElementById('tempPasswordModal')).show();
        } else {
            alert(data.error || 'Errore reset password');
        }
    })
    .catch(error => {
        console.error('Errore reset password:', error);
        alert('Errore durante il reset password');
    });
}

// Elimina utente
function deleteUser(username) {
    if (!confirm(`Eliminare definitivamente l'utente ${username}?`)) return;
    
    fetch('/api/users/delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username: username })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadUsers();
            loadUserCounts();
        } else {
            alert(data.error || 'Errore eliminazione utente');
        }
    })
    .catch(error => {
        console.error('Errore eliminazione utente:', error);
        alert('Errore durante l\'eliminazione');
    });
}


// Copia password temporanea
// Genera password temporanea
function generateTempPassword() {
    const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
    let password = '';
    for (let i = 0; i < 12; i++) {
        password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return password;
}

function copyTempPassword() {
    const password = document.getElementById('temp-password').textContent;
    navigator.clipboard.writeText(password)
        .then(() => {
            const btn = document.querySelector('[onclick="copyTempPassword()"]');
            btn.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(() => {
                btn.innerHTML = '<i class="fas fa-copy"></i>';
            }, 2000);
        })
        .catch(err => console.error('Errore copia password:', err));
}

// Ricarica utenti
function refreshUsers() {
    loadUsers();
    loadUserCounts();
}

// Export utenti
function exportUsers() {
    fetch('/api/users/list')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const csv = [
                    ['Username', 'Ruolo', 'Stato', 'Creato Da', 'Data Creazione', 'Ultimo Accesso']
                ];
                
                data.users.forEach(user => {
                    csv.push([
                        user.username,
                        user.role_name,
                        user.attivo ? 'Attivo' : 'Disattivato',
                        user.created_by,
                        formatDate(user.created_at),
                        formatDate(user.last_login)
                    ]);
                });
                
                const csvContent = csv.map(row => row.join(',')).join('\n');
                const blob = new Blob([csvContent], { type: 'text/csv' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'utenti_sistema.csv';
                a.click();
                window.URL.revokeObjectURL(url);
            }
        })
        .catch(error => console.error('Errore export:', error));
}

// Carica dati iniziali
loadUsers();
loadUserCounts();
