// File: /opt/access_control/src/api/static/js/admin-functions.js
// JavaScript aggiuntivo per le funzioni admin

// Funzioni per Gestione Utenti Admin
function loadUsersData() {
    // Simula caricamento dati utenti
    console.log('Caricamento dati utenti dal sistema...');
    
    // In futuro qui si collegherà alle API reali
    const mockUsers = [
        {username: 'admin', role: 'admin', lastLogin: 'Ora', active: true},
        {username: 'manager', role: 'user_manager', lastLogin: 'Mai', active: true},
        {username: 'viewer', role: 'viewer', lastLogin: 'Mai', active: true}
    ];
    
    // Aggiorna contatori
    document.getElementById('admin-count').textContent = mockUsers.filter(u => u.role === 'admin').length;
    document.getElementById('manager-count').textContent = mockUsers.filter(u => u.role === 'user_manager').length;
    document.getElementById('viewer-count').textContent = mockUsers.filter(u => u.role === 'viewer').length;
    document.getElementById('total-users').textContent = mockUsers.length;
}

// Funzioni per Configurazioni Sistema
function loadSystemConfig() {
    console.log('Caricamento configurazioni sistema...');
    
    // Simula chiamata API
    fetch('/api/system/config')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Configurazioni caricate:', data.config);
                // Popola i form con i dati reali
            }
        })
        .catch(error => {
            console.error('Errore caricamento configurazioni:', error);
        });
}

function saveSystemConfig(formData) {
    console.log('Salvataggio configurazioni...', formData);
    
    // Simula salvataggio
    return fetch('/api/system/config/save', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(formData)
    })
    .then(response => response.json());
}

// Funzioni per Backup & Restore (estende backup.js esistente)
function initializeBackupPage() {
    // Carica stato backup dalla API esistente
    loadBackupStatus();
    
    // Avvia polling per operazioni in corso
    setInterval(checkBackupOperations, 3000);
}

function loadBackupStatus() {
    fetch('/api/backup/status')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateBackupStats(data);
                updateBackupsList(data.backups);
            }
        })
        .catch(error => {
            console.error('Errore caricamento stato backup:', error);
        });
}

function updateBackupStats(data) {
    // Aggiorna le statistiche nella UI
    if (document.getElementById('total-backups')) {
        document.getElementById('total-backups').textContent = data.total_backups || '0';
    }
    if (document.getElementById('total-size')) {
        document.getElementById('total-size').textContent = data.total_size || '-';
    }
    if (document.getElementById('last-backup')) {
        document.getElementById('last-backup').textContent = data.last_backup || 'Mai';
    }
    if (document.getElementById('disk-usage')) {
        document.getElementById('disk-usage').textContent = (data.disk_used_percent || 0) + '%';
    }
}

function updateBackupsList(backups) {
    const tbody = document.querySelector('#backups-table tbody');
    if (!tbody || !backups || backups.length === 0) {
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Nessun backup trovato</td></tr>';
        }
        return;
    }
    
    let html = '';
    backups.forEach(backup => {
        const typeIcon = backup.type === 'complete' ? 'archive' : 'database';
        const typeColor = backup.type === 'complete' ? 'primary' : 'success';
        const typeLabel = backup.type === 'complete' ? 'Completo' : 'Database';
        
        html += `
            <tr>
                <td><i class="fas fa-${typeIcon} me-2 text-${typeColor}"></i>${backup.name}</td>
                <td><span class="badge bg-${typeColor}">${typeLabel}</span></td>
                <td>${backup.size}</td>
                <td>${new Date(backup.date).toLocaleString('it-IT')}</td>
                <td class="${backup.age_days < 7 ? 'text-success' : backup.age_days < 30 ? 'text-warning' : 'text-danger'}">${backup.age_days} giorni</td>
                <td>${backup.has_checksum ? '<i class="fas fa-check-circle text-success" title="Verificato"></i>' : '-'}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="downloadBackup('${backup.name}')" title="Download">
                        <i class="fas fa-download"></i>
                    </button>
                    ${backup.can_restore ? `
                        <button class="btn btn-sm btn-success" onclick="restoreBackup('${backup.name}')" title="Ripristina">
                            <i class="fas fa-undo"></i>
                        </button>
                    ` : ''}
                    <button class="btn btn-sm btn-danger" onclick="deleteBackup('${backup.name}')" title="Elimina">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

// Funzioni di utilità
function showAlert(message, type = 'info') {
    // Crea notifica Bootstrap
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Rimuovi dopo 5 secondi
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function formatFileSize(bytes) {
    const sizes = ['B', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 B';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('it-IT');
}

// Esporta funzioni per uso globale
window.AdminFunctions = {
    loadUsersData,
    loadSystemConfig,
    saveSystemConfig,
    initializeBackupPage,
    loadBackupStatus,
    showAlert,
    formatFileSize,
    formatDate
};

// Auto-inizializzazione per le pagine admin
document.addEventListener('DOMContentLoaded', function() {
    // Rileva quale pagina admin è caricata e inizializza di conseguenza
    const path = window.location.pathname;
    
    if (path.includes('/admin/users')) {
        loadUsersData();
    } else if (path.includes('/admin/config')) {
        loadSystemConfig();
    } else if (path.includes('/admin/backup')) {
        initializeBackupPage();
    }
});
