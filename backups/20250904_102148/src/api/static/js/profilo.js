// File: /opt/access_control/src/api/static/js/profilo.js
// JavaScript per la gestione del profilo utente

// Funzione per mostrare messaggi
function showProfileMessage(message, type = 'info') {
    const container = document.getElementById('profile-message');
    const alertClass = type === 'error' ? 'alert-danger' : 
                     type === 'success' ? 'alert-success' : 'alert-info';
    const icon = type === 'error' ? 'fa-exclamation-circle' : 
                type === 'success' ? 'fa-check-circle' : 'fa-info-circle';
    
    container.innerHTML = `
        <div class="alert ${alertClass}">
            <i class="fas ${icon}"></i> ${message}
        </div>
    `;
    
    // Rimuovi il messaggio dopo 5 secondi
    setTimeout(() => {
        container.innerHTML = '';
    }, 5000);
}

// Valutazione forza password
function checkPasswordStrength(password) {
    let strength = 0;
    const strengthDiv = document.getElementById('password-strength');
    
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]+/)) strength++;
    if (password.match(/[A-Z]+/)) strength++;
    if (password.match(/[0-9]+/)) strength++;
    if (password.match(/[^a-zA-Z0-9]+/)) strength++;
    
    if (password.length < 6) {
        strengthDiv.innerHTML = '';
        return;
    }
    
    let strengthText = '';
    let strengthClass = '';
    
    if (strength <= 2) {
        strengthText = 'Password debole';
        strengthClass = 'strength-weak';
    } else if (strength <= 3) {
        strengthText = 'Password media';
        strengthClass = 'strength-medium';
    } else {
        strengthText = 'Password forte';
        strengthClass = 'strength-strong';
    }
    
    strengthDiv.innerHTML = `<span class="${strengthClass}">
        <i class="fas fa-shield-alt"></i> ${strengthText}
    </span>`;
}

// Inizializzazione quando il DOM è pronto
document.addEventListener('DOMContentLoaded', function() {
    // Event listener per la valutazione password
    const newPasswordField = document.getElementById('new-password');
    if (newPasswordField) {
        newPasswordField.addEventListener('input', function() {
            checkPasswordStrength(this.value);
        });
    }
    
    // Gestione form cambio password
    const changePasswordForm = document.getElementById('change-password-form');
    if (changePasswordForm) {
        changePasswordForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            // Validazione lato client
            if (data.new_password !== data.confirm_password) {
                showProfileMessage('Le password non coincidono', 'error');
                return;
            }
            
            if (data.new_password.length < 6) {
                showProfileMessage('La password deve essere di almeno 6 caratteri', 'error');
                return;
            }
            
            try {
                const response = await fetch('/api/profile/change-password', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showProfileMessage('Password aggiornata con successo', 'success');
                    this.reset();
                    document.getElementById('password-strength').innerHTML = '';
                } else {
                    showProfileMessage(result.error || 'Errore durante il cambio password', 'error');
                }
            } catch (error) {
                showProfileMessage('Errore di connessione al server', 'error');
                console.error('Errore:', error);
            }
        });
    }
});
