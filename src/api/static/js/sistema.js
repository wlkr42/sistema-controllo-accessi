// File: /opt/access_control/src/api/static/js/sistema.js
// JavaScript per Dashboard Salvataggio parametri di Sistema

// ===== GESTIONE CONFIGURAZIONI SISTEMA =====

// Variabili globali
let configData = {};

// Inizializza al caricamento della pagina
document.addEventListener('DOMContentLoaded', function() {
    loadSystemConfig();
    
    // Event listeners per i form
    document.getElementById('sistema-form').addEventListener('submit', saveSistemaConfig);
    document.getElementById('hardware-form').addEventListener('submit', saveHardwareConfig);
    document.getElementById('sicurezza-form').addEventListener('submit', saveSicurezzaConfig);
    document.getElementById('email-form').addEventListener('submit', saveEmailConfig);
});

// Carica configurazioni dal server
function loadSystemConfig() {
    fetch('/api/system/config')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                configData = data.config;
                populateSystemForms(data.config);
            } else {
                showToast('Errore caricamento configurazioni', 'error');
            }
        })
        .catch(error => {
            console.error('Errore:', error);
            showToast('Errore comunicazione con il server', 'error');
        });
}

// Popola i form con i dati caricati
function populateSystemForms(config) {
    // Sistema
    if (config.sistema) {
        document.getElementById('nome-installazione').value = config.sistema.nome_installazione || '';
        document.getElementById('porta-web').value = config.sistema.porta_web || 5000;
        document.getElementById('debug-mode').checked = config.sistema.debug_mode || false;
        document.getElementById('timeout-sessione').value = config.sistema.timeout_sessione || 1800;
        document.getElementById('ambiente').value = config.sistema.ambiente || 'production';
    }
    
    // Hardware
    if (config.hardware) {
        document.getElementById('lettore-porta').value = config.hardware.lettore_porta || '/dev/ttyACM0';
        document.getElementById('relay-porta').value = config.hardware.relay_porta || '/dev/ttyUSB0';
        document.getElementById('relay-baudrate').value = config.hardware.relay_baudrate || 19200;
        document.getElementById('gate-duration').value = config.hardware.gate_duration || 8;
    }
    
    // Sicurezza
    if (config.sicurezza) {
        document.getElementById('max-tentativi').value = config.sicurezza.max_tentativi_login || 5;
        document.getElementById('durata-blocco').value = config.sicurezza.durata_blocco_minuti || 15;
        document.getElementById('rotazione-password').value = config.sicurezza.rotazione_password_giorni || 90;
        document.getElementById('log-audit').checked = config.sicurezza.log_audit_abilitato !== false;
    }
    
    // Email
    if (config.email) {
        document.getElementById('smtp-server').value = config.email.smtp_server || '';
        document.getElementById('smtp-porta').value = config.email.smtp_porta || 587;
        document.getElementById('email-mittente').value = config.email.mittente || '';
        document.getElementById('report-automatici').checked = config.email.report_automatici || false;
        document.getElementById('frequenza-report').value = config.email.frequenza_report || 'weekly';
    }
}

// Salva configurazioni Sistema
function saveSistemaConfig(e) {
    e.preventDefault();
    
    const config = {
        sistema: {
            nome_installazione: document.getElementById('nome-installazione').value,
            porta_web: parseInt(document.getElementById('porta-web').value),
            debug_mode: document.getElementById('debug-mode').checked,
            timeout_sessione: parseInt(document.getElementById('timeout-sessione').value),
            ambiente: document.getElementById('ambiente').value
        }
    };
    
    saveConfiguration(config, 'sistema');
}

// Salva configurazioni Hardware
function saveHardwareConfig(e) {
    e.preventDefault();
    
    const readerType = document.getElementById('reader-type').value;
    const readerPort = document.getElementById('reader-port').value;
    const relayPort = document.getElementById('relay-port').value;
    const relayBaudrate = parseInt(document.getElementById('relay-baudrate').value);
    const gateDuration = parseFloat(document.getElementById('gate-duration').value);
    
    // Crea configurazione per il nuovo sistema
    const config = {
        assignments: {
            card_reader: {
                reader_type: readerType,
                device_path: readerPort,
                device_id: readerType,
                assigned_function: 'card_reader'
            },
            relay_controller: {
                device_path: relayPort,
                device_id: 'USB-RLY08',
                assigned_function: 'relay_controller',
                baudrate: relayBaudrate,
                gate_duration: gateDuration
            }
        }
    };
    
    // Salva configurazione hardware
    fetch('/api/hardware/config/save', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Configurazione hardware salvata con successo', 'success');
        } else {
            showNotification('Errore salvataggio configurazione: ' + (data.error || 'Sconosciuto'), 'danger');
        }
    })
    .catch(error => {
        console.error('Errore:', error);
        showNotification('Errore di connessione', 'danger');
    });
}

// Salva configurazioni Sicurezza
function saveSicurezzaConfig(e) {
    e.preventDefault();
    
    const config = {
        sicurezza: {
            max_tentativi_login: parseInt(document.getElementById('max-tentativi').value),
            durata_blocco_minuti: parseInt(document.getElementById('durata-blocco').value),
            rotazione_password_giorni: parseInt(document.getElementById('rotazione-password').value),
            log_audit_abilitato: document.getElementById('log-audit').checked
        }
    };
    
    saveConfiguration(config, 'sicurezza');
}

// Salva configurazioni Email
function saveEmailConfig(e) {
    e.preventDefault();
    
    const config = {
        email: {
            smtp_server: document.getElementById('smtp-server').value,
            smtp_porta: parseInt(document.getElementById('smtp-porta').value),
            mittente: document.getElementById('email-mittente').value,
            report_automatici: document.getElementById('report-automatici').checked,
            frequenza_report: document.getElementById('frequenza-report').value
        }
    };
    
    saveConfiguration(config, 'email');
}

// Funzione generica per salvare configurazioni
function saveConfiguration(config, section) {
    // Mostra loading
    showToast(`Salvataggio configurazioni ${section}...`, 'info');
    
    fetch('/api/system/config/save', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Aggiorna i dati locali
            Object.assign(configData, config);
            showToast(`Configurazioni ${section} salvate con successo!`, 'success');
            
            // Se cambiate configurazioni critiche, suggerisci riavvio
            if (section === 'sistema' || section === 'hardware') {
                setTimeout(() => {
                    if (confirm('Le modifiche richiedono un riavvio del sistema. Riavviare ora?')) {
                        restartSystem();
                    }
                }, 1000);
            }
        } else {
            showToast(`Errore salvataggio: ${data.error || 'Errore sconosciuto'}`, 'error');
        }
    })
    .catch(error => {
        console.error('Errore:', error);
        showToast('Errore comunicazione con il server', 'error');
    });
}

// Riavvia sistema
function restartSystem() {
    if (!confirm('Sei sicuro di voler riavviare il sistema?\n\nTutte le sessioni attive verranno terminate.')) {
        return;
    }
    
    showToast('Riavvio sistema in corso...', 'warning');
    
    fetch('/api/system/restart', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Sistema in riavvio. La pagina si ricaricherà tra 30 secondi.', 'info');
            
            // Disabilita tutti i controlli
            document.querySelectorAll('button, input, select').forEach(el => {
                el.disabled = true;
            });
            
            // Ricarica la pagina dopo 30 secondi
            setTimeout(() => {
                window.location.reload();
            }, 30000);
        } else {
            showToast('Errore durante il riavvio del sistema', 'error');
        }
    })
    .catch(error => {
        console.error('Errore:', error);
        showToast('Errore comunicazione con il server', 'error');
    });
}

// Esporta configurazioni
function exportConfig() {
    fetch('/api/system/config')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Crea file JSON da scaricare
                const jsonStr = JSON.stringify(data.config, null, 2);
                const blob = new Blob([jsonStr], {type: 'application/json'});
                const url = URL.createObjectURL(blob);
                
                // Crea link temporaneo per download
                const a = document.createElement('a');
                a.href = url;
                a.download = `config_backup_${new Date().toISOString().split('T')[0]}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                
                showToast('Configurazioni esportate con successo', 'success');
            }
        })
        .catch(error => {
            console.error('Errore:', error);
            showToast('Errore durante l\'export delle configurazioni', 'error');
        });
}

// Ripristina configurazioni default
function resetToDefaults() {
    if (!confirm('Ripristinare tutte le configurazioni ai valori default?\n\nQuesta operazione non può essere annullata.')) {
        return;
    }
    
    // Per sicurezza, chiedi una seconda conferma
    if (!confirm('Sei ASSOLUTAMENTE SICURO di voler ripristinare i valori di default?\n\nTutte le personalizzazioni andranno perse.')) {
        return;
    }
    
    showToast('Ripristino configurazioni in corso...', 'warning');
    
    fetch('/api/system/config/reset', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Configurazioni ripristinate. Ricaricamento pagina...', 'success');
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            showToast('Errore durante il ripristino', 'error');
        }
    })
    .catch(error => {
        console.error('Errore:', error);
        showToast('Errore comunicazione con il server', 'error');
    });
}

// Utility per mostrare notifiche toast
function showToast(message, type = 'info') {
    // Rimuovi toast esistenti
    const existingToasts = document.querySelectorAll('.toast-notification');
    existingToasts.forEach(toast => toast.remove());
    
    // Mappa colori per tipo
    const colors = {
        'success': '#28a745',
        'error': '#dc3545',
        'warning': '#ffc107',
        'info': '#17a2b8'
    };
    
    // Crea elemento toast
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type] || colors.info};
        color: white;
        padding: 15px 20px;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        z-index: 9999;
        min-width: 250px;
        animation: slideIn 0.3s ease-out;
    `;
    
    // Aggiungi icona
    const icons = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-exclamation-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    };
    
    toast.innerHTML = `
        <i class="${icons[type] || icons.info} me-2"></i>
        <span>${message}</span>
    `;
    
    // Aggiungi al body
    document.body.appendChild(toast);
    
    // Rimuovi dopo 5 secondi
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Aggiungi stili per animazioni
if (!document.getElementById('toast-styles')) {
    const style = document.createElement('style');
    style.id = 'toast-styles';
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}
