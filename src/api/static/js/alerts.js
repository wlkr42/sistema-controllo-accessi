// File: /opt/access_control/src/api/static/js/alerts.js

function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Rimuovi alert esistenti
    document.querySelectorAll('.alert').forEach(alert => alert.remove());
    
    // Inserisci nuovo alert all'inizio del container
    document.querySelector('.container').insertAdjacentHTML('afterbegin', alertHtml);
    
    // Auto-chiudi dopo 5 secondi
    setTimeout(() => {
        const alert = document.querySelector('.alert');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

// Esporta per uso globale
window.showAlert = showAlert;
