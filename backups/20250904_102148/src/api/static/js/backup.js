// Backup & Restore Management

// Carica stato backup
function loadBackupStatus() {
    fetch('/api/backup/status')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Aggiorna statistiche
                document.querySelector('#backup-total .stat-number').textContent = data.backups.length;
                document.querySelector('#backup-size .stat-number').textContent = data.total_size;
                document.querySelector('#disk-usage .stat-number').textContent = data.disk_used_percent + '%';
                
                // Aggiorna tabella backup
                const tbody = document.querySelector('#backup-list tbody');
                tbody.innerHTML = '';
                
                data.backups.forEach(backup => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>
                            <i class="fas fa-${backup.type === 'complete' ? 'archive' : 'database'} me-2 
                               text-${backup.type === 'complete' ? 'primary' : 'success'}"></i>
                            ${backup.name}
                        </td>
                        <td>
                            <span class="badge bg-${backup.type === 'complete' ? 'primary' : 'success'}">
                                ${backup.type === 'complete' ? 'Completo' : 'Database'}
                            </span>
                        </td>
                        <td>${backup.size}</td>
                        <td>${new Date(backup.date).toLocaleString()}</td>
                        <td class="${backup.age_days < 1 ? 'text-success' : 
                                   backup.age_days < 7 ? 'text-warning' : 'text-danger'}">
                            ${backup.age_days < 1 ? 
                              Math.round((Date.now() - new Date(backup.date)) / 3600000) + ' ore' : 
                              backup.age_days + ' giorni'}
                        </td>
                        <td>
                            ${backup.has_checksum ? 
                              '<i class="fas fa-check-circle text-success" title="Verificato"></i>' : 
                              '-'}
                        </td>
                        <td>
                            <button class="btn btn-sm btn-primary" onclick="downloadBackup('${backup.name}')" 
                                    title="Download" ${backup.can_download ? '' : 'disabled'}>
                                <i class="fas fa-download"></i>
                            </button>
                            ${backup.can_restore ? `
                                <button class="btn btn-sm btn-success" onclick="restoreBackup('${backup.name}')"
                                        title="Ripristina">
                                    <i class="fas fa-undo"></i>
                                </button>
                            ` : ''}
                            <button class="btn btn-sm btn-danger" onclick="deleteBackup('${backup.name}')"
                                    title="Elimina">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
                
                // Aggiorna configurazione backup automatico
                if (data.config) {
                    document.querySelector('#auto-backup').checked = data.config.auto_backup.enabled;
                    document.querySelector('#backup-frequency').value = 
                        Object.entries(data.config.auto_backup)
                              .find(([k, v]) => k !== 'enabled' && v.enabled)[0];
                    document.querySelector('#retention-days').value = data.config.retention.daily_keep;
                }
            }
        })
        .catch(error => console.error('Errore caricamento stato backup:', error));
}

// Crea nuovo backup
function createBackup(type) {
    if (!confirm(`Creare un backup ${type === 'complete' ? 'completo' : 'database'}?\n\nL'operazione potrebbe richiedere alcuni minuti.`)) {
        return;
    }
    
    fetch('/api/backup/create', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({type: type})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Backup ${type} avviato!\n\nOperation ID: ${data.operation_id}`);
            // Ricarica stato dopo 5 secondi
            setTimeout(loadBackupStatus, 5000);
        } else {
            alert('Errore durante la creazione del backup: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Errore creazione backup:', error);
        alert('Errore durante la creazione del backup');
    });
}

// Download backup
function downloadBackup(filename) {
    // Crea un link temporaneo per il download
    const link = document.createElement('a');
    link.href = `/api/backup/download/${filename}`;
    link.download = filename; // Suggerisce il nome del file
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Ripristina backup
function restoreBackup(filename) {
    if (!confirm(`Ripristinare il backup ${filename}?\n\nATTENZIONE: Questa operazione sovrascriverà i dati attuali!`)) {
        return;
    }
    
    fetch('/api/backup/restore/' + filename, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Backup ripristinato con successo!\n\n' + data.message);
            loadBackupStatus();
        } else {
            alert('Errore durante il ripristino: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Errore ripristino backup:', error);
        alert('Errore durante il ripristino del backup');
    });
}

// Elimina backup
function deleteBackup(filename) {
    if (!confirm(`Eliminare il backup ${filename}?\n\nQuesta operazione non può essere annullata.`)) {
        return;
    }
    
    fetch('/api/backup/delete/' + filename, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Backup eliminato con successo!');
            loadBackupStatus();
        } else {
            alert('Errore durante l\'eliminazione: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Errore eliminazione backup:', error);
        alert('Errore durante l\'eliminazione del backup');
    });
}

// Pulizia backup vecchi
function cleanupBackups() {
    if (!confirm('Eliminare i backup vecchi secondo la policy di retention?\n\nQuesta operazione non può essere annullata.')) {
        return;
    }
    
    fetch('/api/backup/cleanup', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Pulizia backup completata!\n\n${data.cleaned_files} file eliminati, ${data.freed_space} liberati`);
            loadBackupStatus();
        } else {
            alert('Errore durante la pulizia: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Errore pulizia backup:', error);
        alert('Errore durante la pulizia dei backup');
    });
}

// Salva configurazione backup automatico
function saveBackupConfig() {
    const config = {
        auto_backup: {
            enabled: document.querySelector('#auto-backup').checked,
            daily: {enabled: false},
            weekly: {enabled: false},
            monthly: {enabled: false}
        },
        retention: {
            daily_keep: parseInt(document.querySelector('#retention-days').value),
            weekly_keep: 4,
            monthly_keep: 6,
            max_size_gb: 10
        }
    };
    
    // Imposta frequenza selezionata
    const frequency = document.querySelector('#backup-frequency').value;
    config.auto_backup[frequency] = {
        enabled: true,
        time: "03:00",
        day: frequency === 'weekly' ? 0 : 1
    };
    
    fetch('/api/backup/config', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Configurazione backup salvata con successo!');
        } else {
            alert('Errore durante il salvataggio: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Errore salvataggio config:', error);
        alert('Errore durante il salvataggio della configurazione');
    });
}

// Carica stato iniziale
document.addEventListener('DOMContentLoaded', loadBackupStatus);
