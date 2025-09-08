// Backup & Restore Management - Sistema Completo e Funzionante
// Versione 2.0 - Allineato con template HTML attuale

// Variabili globali
let backup_operations = {};
let currentCloudProvider = 'none';

// ========================================
// FUNZIONI PRINCIPALI
// ========================================

// Carica stato backup all'avvio
function loadBackupStatus() {
    fetch('/api/backup/status')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Aggiorna statistiche con gli ID CORRETTI del template HTML
                document.getElementById('total-backups').textContent = data.total_backups || '0';
                document.getElementById('total-size').textContent = data.total_size || '-';
                document.getElementById('last-backup').textContent = data.last_backup || 'Mai';
                document.getElementById('disk-usage').textContent = data.disk_used_percent || '-';
                
                // Aggiorna operazioni in corso se presenti
                if (data.operations) {
                    backup_operations = data.operations;
                    updateOperationsDisplay();
                }
                
                // Renderizza tabella backup
                renderBackupsTable(data.backups || []);
                
                // Carica configurazione schedulazione se presente
                if (data.config && data.config.auto_backup) {
                    loadScheduleConfig(data.config.auto_backup);
                }
            }
        })
        .catch(error => {
            console.error('Errore caricamento stato backup:', error);
            showAlert('Errore nel caricamento dello stato backup', 'danger');
        });
}

// Renderizza tabella backup con ID CORRETTO
function renderBackupsTable(backups) {
    const tbody = document.getElementById('backups-table'); // ID CORRETTO dal template
    if (!tbody) return;
    
    if (!backups || backups.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Nessun backup trovato</td></tr>';
        return;
    }
    
    let html = '';
    backups.forEach(backup => {
        // Formatta data correttamente
        const backupDate = new Date(backup.date);
        const dateStr = backupDate.toLocaleDateString('it-IT');
        const timeStr = backupDate.toLocaleTimeString('it-IT');
        
        html += `
            <tr>
                <td>
                    <i class="fas fa-${backup.type === 'complete' ? 'archive' : 'database'} me-2"></i>
                    ${backup.name}
                </td>
                <td>
                    <span class="badge bg-${backup.type === 'complete' ? 'primary' : 'success'}">
                        ${backup.type === 'complete' ? 'Completo' : 'Database'}
                    </span>
                </td>
                <td>${backup.size}</td>
                <td>${dateStr} ${timeStr}</td>
                <td>${backup.age_days} giorni</td>
                <td>
                    ${backup.has_checksum ? 
                        '<i class="fas fa-check-circle text-success" title="Checksum verificato"></i>' : 
                        '<i class="fas fa-minus-circle text-muted" title="Nessun checksum"></i>'}
                </td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="downloadBackup('${backup.name}')" 
                            title="Scarica backup">
                        <i class="fas fa-download"></i>
                    </button>
                    ${backup.can_restore ? `
                        <button class="btn btn-sm btn-success" onclick="restoreBackup('${backup.name}')"
                                title="Ripristina backup">
                            <i class="fas fa-undo"></i>
                        </button>
                    ` : ''}
                    <button class="btn btn-sm btn-danger" onclick="deleteBackup('${backup.name}')"
                            title="Elimina backup">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

// ========================================
// FUNZIONI BACKUP
// ========================================

function createBackup(type) {
    const confirmMsg = type === 'complete' 
        ? 'Creare un backup COMPLETO del sistema?\n\nInclude: codice, database, configurazioni, log\nDimensione stimata: 50-200 MB\nTempo stimato: 2-5 minuti'
        : 'Creare un backup del SOLO DATABASE?\n\nBackup rapido del database\nDimensione stimata: 5-20 MB\nTempo stimato: < 1 minuto';
    
    if (!confirm(confirmMsg)) return;
    
    // Mostra sezione operazioni
    document.getElementById('backup-operations').style.display = 'block';
    
    fetch('/api/backup/create', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({type: type})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(`Backup ${type} avviato con successo`, 'success');
            // Polling per aggiornamento stato
            setTimeout(() => {
                loadBackupStatus();
                checkBackupOperations();
            }, 2000);
        } else {
            showAlert('Errore: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        console.error('Errore creazione backup:', error);
        showAlert('Errore nella creazione del backup', 'danger');
    });
}

function cleanupBackups() {
    if (!confirm('Eliminare i backup vecchi secondo la policy di retention?\n\nVerranno eliminati:\n- Backup giornalieri più vecchi di 7 giorni\n- Backup settimanali più vecchi di 4 settimane\n- Backup mensili più vecchi di 6 mesi')) {
        return;
    }
    
    fetch('/api/backup/cleanup', {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert(`Pulizia completata: ${data.cleaned_files} file eliminati, ${data.freed_space} liberati`, 'success');
                loadBackupStatus();
            } else {
                showAlert('Errore: ' + data.error, 'danger');
            }
        })
        .catch(error => {
            console.error('Errore pulizia:', error);
            showAlert('Errore durante la pulizia', 'danger');
        });
}

// ========================================
// FUNZIONI OPERAZIONI FILE
// ========================================

function downloadBackup(filename) {
    // Crea link temporaneo per download
    const link = document.createElement('a');
    link.href = `/api/backup/download/${encodeURIComponent(filename)}`;
    link.download = filename;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showAlert(`Download di ${filename} avviato`, 'info');
}

function deleteBackup(filename) {
    if (!confirm(`ATTENZIONE: Eliminare definitivamente il backup?\n\n${filename}\n\nQuesta operazione NON può essere annullata!`)) {
        return;
    }
    
    // Usa POST come fallback per compatibilità
    fetch(`/api/backup/delete/${encodeURIComponent(filename)}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok && response.status === 405) {
            // Fallback a POST se DELETE non supportato
            return fetch(`/api/backup/delete/${encodeURIComponent(filename)}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            });
        }
        return response;
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Gestisci messaggi di warning (file già mancante)
            if (data.warning) {
                showAlert(data.message || 'File già assente - rimosso dalla lista', 'warning');
            } else {
                showAlert(data.message || 'Backup eliminato con successo', 'success');
            }
            // Ricarica la lista in ogni caso
            loadBackupStatus();
        } else {
            showAlert(`Errore eliminazione: ${data.error}`, 'danger');
        }
    })
    .catch(error => {
        console.error('Errore:', error);
        showAlert('Errore di rete durante l\'eliminazione', 'danger');
    });
}

function restoreBackup(filename) {
    // AVVISO IMPORTANTE per ripristino
    const warningMsg = `⚠️ ATTENZIONE - OPERAZIONE CRITICA ⚠️

Stai per RIPRISTINARE il backup:
${filename}

QUESTO COMPORTERÀ:
✗ Sovrascrittura completa del sistema attuale
✗ Perdita di tutte le modifiche recenti
✗ Possibile riavvio del servizio
✗ Downtime di alcuni minuti

Un backup dell'attuale configurazione verrà creato automaticamente prima del ripristino.

Sei ASSOLUTAMENTE SICURO di voler procedere?`;

    if (!confirm(warningMsg)) return;
    
    if (!confirm('SECONDA CONFERMA: Procedere con il ripristino?')) return;
    
    fetch(`/api/backup/restore/${encodeURIComponent(filename)}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ Ripristino completato con successo!\n\n' + data.message + '\n\nIl sistema verrà riavviato...');
            setTimeout(() => window.location.reload(), 3000);
        } else {
            showAlert(`Errore ripristino: ${data.error}`, 'danger');
        }
    })
    .catch(error => {
        console.error('Errore:', error);
        showAlert('Errore critico durante il ripristino', 'danger');
    });
}

// ========================================
// FUNZIONI SCHEDULAZIONE
// ========================================

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
    
    // Valida che almeno una schedulazione sia attiva
    const hasActiveSchedule = config.auto_backup.daily.enabled || 
                            config.auto_backup.weekly.enabled || 
                            config.auto_backup.monthly.enabled ||
                            config.auto_backup.yearly.enabled;
    
    if (!hasActiveSchedule) {
        if (!confirm('Nessuna schedulazione attiva. Disabilitare i backup automatici?')) {
            return;
        }
    }
    
    fetch('/api/backup/config', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Schedulazione backup salvata con successo', 'success');
        } else {
            showAlert(`Errore: ${data.error}`, 'danger');
        }
    })
    .catch(error => {
        console.error('Errore:', error);
        showAlert('Errore nel salvataggio della schedulazione', 'danger');
    });
}

function loadScheduleConfig(config) {
    if (!config) return;
    
    // Carica configurazioni daily
    if (config.daily) {
        document.getElementById('daily-enabled').checked = config.daily.enabled || false;
        if (config.daily.time) document.getElementById('daily-time').value = config.daily.time;
        if (config.daily.type) document.getElementById('daily-type').value = config.daily.type;
        if (config.daily.retention_days) document.getElementById('daily-retention').value = config.daily.retention_days;
    }
    
    // Carica configurazioni weekly
    if (config.weekly) {
        document.getElementById('weekly-enabled').checked = config.weekly.enabled || false;
        if (config.weekly.time) document.getElementById('weekly-time').value = config.weekly.time;
        if (config.weekly.day) document.getElementById('weekly-day').value = config.weekly.day;
        if (config.weekly.type) document.getElementById('weekly-type').value = config.weekly.type;
        if (config.weekly.retention_weeks) document.getElementById('weekly-retention').value = config.weekly.retention_weeks;
    }
    
    // Simile per monthly e yearly...
}

// ========================================
// FUNZIONI CLOUD
// ========================================

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
        const ftpHost = document.getElementById('ftp-host').value;
        const ftpUsername = document.getElementById('ftp-username').value;
        const ftpPassword = document.getElementById('ftp-password').value;
        
        if (!ftpHost || !ftpUsername || !ftpPassword) {
            showAlert('Compilare tutti i campi FTP', 'warning');
            return;
        }
        
        config.cloud_backup.credentials.ftp = {
            host: ftpHost,
            port: parseInt(document.getElementById('ftp-port').value),
            username: ftpUsername,
            password: ftpPassword,
            path: document.getElementById('ftp-path').value
        };
    } else if (selectedProvider === 'aws') {
        const accessKey = document.getElementById('aws-access-key').value;
        const secretKey = document.getElementById('aws-secret-key').value;
        const bucket = document.getElementById('aws-bucket').value;
        
        if (!accessKey || !secretKey || !bucket) {
            showAlert('Compilare tutti i campi AWS', 'warning');
            return;
        }
        
        config.cloud_backup.credentials.aws = {
            access_key: accessKey,
            secret_key: secretKey,
            bucket: bucket,
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
    })
    .catch(error => {
        console.error('Errore:', error);
        showAlert('Errore nel salvataggio configurazione cloud', 'danger');
    });
}

function syncToCloud() {
    if (!confirm('Sincronizzare tutti i backup con il cloud?\n\nQuesta operazione potrebbe richiedere diversi minuti.')) {
        return;
    }
    
    fetch('/api/backup/cloud/sync', {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('Sincronizzazione cloud avviata', 'info');
                checkBackupOperations(); // Avvia polling
            } else {
                showAlert(`Errore: ${data.error}`, 'danger');
            }
        })
        .catch(error => {
            console.error('Errore:', error);
            showAlert('Errore nella sincronizzazione cloud', 'danger');
        });
}

// ========================================
// FUNZIONI INTEGRITÀ
// ========================================

function checkIntegrity() {
    if (!confirm('Verificare l\'integrità di tutti i backup?\n\nVerrà controllato il checksum MD5 di ogni file.')) {
        return;
    }
    
    document.getElementById('integrity-results').style.display = 'none';
    
    fetch('/api/backup/integrity/check', {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('Verifica integrità avviata', 'info');
                if (data.operation_id) {
                    setTimeout(() => loadIntegrityResults(data.operation_id), 2000);
                }
            } else {
                showAlert(`Errore: ${data.error}`, 'danger');
            }
        })
        .catch(error => {
            console.error('Errore:', error);
            showAlert('Errore nella verifica integrità', 'danger');
        });
}

function loadIntegrityResults(operationId) {
    if (!operationId) return;
    
    fetch('/api/backup/status')
        .then(response => response.json())
        .then(data => {
            if (data.operations && data.operations[operationId]) {
                const op = data.operations[operationId];
                
                if (op.status === 'completed' && op.result) {
                    const result = op.result;
                    
                    // Aggiorna contatori
                    document.getElementById('valid-count').textContent = result.valid || 0;
                    document.getElementById('corrupted-count').textContent = result.corrupted || 0;
                    document.getElementById('missing-count').textContent = result.missing_checksum || 0;
                    document.getElementById('integrity-results').style.display = 'block';
                    
                    // Aggiorna status box
                    const statusDiv = document.getElementById('integrity-status');
                    const lastCheck = document.getElementById('last-check');
                    
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
                    
                    lastCheck.textContent = new Date().toLocaleString('it-IT');
                    
                    // Mostra errori se presenti
                    if (result.errors && result.errors.length > 0) {
                        showAlert('Problemi rilevati:\n' + result.errors.slice(0, 3).join('\n'), 'warning');
                    }
                } else if (op.status === 'running') {
                    // Continua polling
                    setTimeout(() => loadIntegrityResults(operationId), 2000);
                } else if (op.status === 'error') {
                    showAlert('Errore verifica: ' + op.error, 'danger');
                }
            }
        })
        .catch(error => {
            console.error('Errore caricamento risultati:', error);
        });
}

function applyRetention() {
    if (!confirm('Applicare le politiche di retention?\n\nI backup che superano i limiti temporali verranno eliminati PERMANENTEMENTE.')) {
        return;
    }
    
    fetch('/api/backup/retention/apply', {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            if (data.success && data.result) {
                showAlert(`Retention applicata:\n${data.result.cleaned_files} file eliminati\n${data.result.freed_space} liberati`, 'success');
                loadBackupStatus();
            } else {
                showAlert(`Errore: ${data.error || 'Errore sconosciuto'}`, 'danger');
            }
        })
        .catch(error => {
            console.error('Errore:', error);
            showAlert('Errore nell\'applicazione retention', 'danger');
        });
}

// ========================================
// FUNZIONI OPERAZIONI ASINCRONE
// ========================================

function checkBackupOperations() {
    // Polling per operazioni in corso
    fetch('/api/backup/status')
        .then(response => response.json())
        .then(data => {
            if (data.operations) {
                backup_operations = data.operations;
                updateOperationsDisplay();
                
                // Continua polling se ci sono operazioni in corso
                const hasRunning = Object.values(backup_operations).some(op => op.status === 'running');
                if (hasRunning) {
                    setTimeout(checkBackupOperations, 3000);
                } else {
                    // Nascondi sezione operazioni dopo 5 secondi se tutte completate
                    setTimeout(() => {
                        document.getElementById('backup-operations').style.display = 'none';
                        loadBackupStatus(); // Ricarica stato finale
                    }, 5000);
                }
            }
        })
        .catch(error => console.error('Errore polling operazioni:', error));
}

function updateOperationsDisplay() {
    const container = document.getElementById('operations-list');
    if (!container) return;
    
    const operations = Object.entries(backup_operations);
    if (operations.length === 0) {
        container.innerHTML = '<p class="text-muted">Nessuna operazione in corso</p>';
        return;
    }
    
    let html = '';
    operations.forEach(([id, op]) => {
        const icon = op.status === 'running' ? 'fa-spinner fa-spin' : 
                    op.status === 'completed' ? 'fa-check-circle text-success' : 
                    'fa-exclamation-circle text-danger';
        
        html += `
            <div class="mb-2">
                <i class="fas ${icon}"></i>
                <strong>${op.type || 'Operazione'}</strong>: ${op.message || op.status}
                ${op.progress ? `
                    <div class="progress mt-1" style="height: 20px;">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" 
                             style="width: ${op.progress}%">${op.progress}%</div>
                    </div>
                ` : ''}
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // Mostra sezione se nascosta
    const operationsSection = document.getElementById('backup-operations');
    if (operationsSection && operations.some(([_, op]) => op.status === 'running')) {
        operationsSection.style.display = 'block';
    }
}

// ========================================
// FUNZIONI UTILITY
// ========================================

function showAlert(message, type = 'info') {
    // Crea alert Bootstrap 5
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 
                          type === 'danger' ? 'exclamation-triangle' : 
                          type === 'warning' ? 'exclamation-circle' : 
                          'info-circle'}"></i>
        ${message.replace(/\n/g, '<br>')}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-rimuovi dopo 5 secondi
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 300);
    }, 5000);
}

// ========================================
// INIZIALIZZAZIONE
// ========================================

// Inizializza al caricamento pagina
document.addEventListener('DOMContentLoaded', function() {
    // Carica stato iniziale
    loadBackupStatus();
    
    // Polling periodico per operazioni
    setInterval(function() {
        if (Object.keys(backup_operations).length > 0) {
            checkBackupOperations();
        }
    }, 5000);
    
    // Setup cloud provider cards
    document.querySelectorAll('.cloud-provider-card').forEach(card => {
        card.addEventListener('click', function() {
            // Rimuovi selezione precedente
            document.querySelectorAll('.cloud-provider-card').forEach(c => c.classList.remove('selected'));
            
            // Seleziona questo
            this.classList.add('selected');
            currentCloudProvider = this.dataset.provider;
            
            // Mostra/nascondi configurazione
            const cloudConfig = document.getElementById('cloud-config');
            const selectedProviderSpan = document.getElementById('selected-provider');
            
            if (currentCloudProvider === 'none') {
                cloudConfig.style.display = 'none';
            } else {
                cloudConfig.style.display = 'block';
                selectedProviderSpan.textContent = this.querySelector('h6').textContent;
                
                // Nascondi tutte le config
                document.querySelectorAll('.provider-config').forEach(config => {
                    config.style.display = 'none';
                });
                
                // Mostra config del provider selezionato
                const providerConfig = document.getElementById(`${currentCloudProvider}-config`);
                if (providerConfig) {
                    providerConfig.style.display = 'block';
                }
            }
        });
    });
    
    // Auto-refresh ogni 30 secondi
    setInterval(loadBackupStatus, 30000);
});

// Esporta funzioni per uso globale
window.createBackup = createBackup;
window.cleanupBackups = cleanupBackups;
window.downloadBackup = downloadBackup;
window.deleteBackup = deleteBackup;
window.restoreBackup = restoreBackup;
window.saveBackupSchedule = saveBackupSchedule;
window.saveCloudConfig = saveCloudConfig;
window.syncToCloud = syncToCloud;
window.checkIntegrity = checkIntegrity;
window.applyRetention = applyRetention;
window.loadBackupStatus = loadBackupStatus;