// File: /opt/access_control/src/api/static/js/user-menu.js
// JavaScript per gestione menu utente moderno

class UserMenu {
    constructor() {
        this.menuTrigger = null;
        this.menuDropdown = null;
        this.overlay = null;
        this.isOpen = false;
        this.init();
    }
    
    init() {
        // Attendi che il DOM sia carico
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }
    
    setup() {
        this.menuTrigger = document.querySelector('.user-menu-trigger');
        this.menuDropdown = document.querySelector('.user-menu-dropdown');
        this.overlay = document.querySelector('.user-menu-overlay');
        
        if (!this.menuTrigger || !this.menuDropdown) {
            console.error('Menu utente: elementi non trovati');
            return;
        }
        
        // Event listeners
        this.menuTrigger.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggle();
        });
        
        // Click su overlay per chiudere
        if (this.overlay) {
            this.overlay.addEventListener('click', () => this.close());
        }
        
        // Click fuori per chiudere
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.user-menu-container')) {
                this.close();
            }
        });
        
        // Escape per chiudere
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
        
        // Gestione link menu con animazioni
        this.setupMenuItems();
    }
    
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
    
    open() {
        this.isOpen = true;
        this.menuDropdown.classList.add('active');
        if (this.overlay) {
            this.overlay.classList.add('active');
        }
        
        // Animazione apertura
        this.animateOpen();
    }
    
    close() {
        this.isOpen = false;
        this.menuDropdown.classList.remove('active');
        if (this.overlay) {
            this.overlay.classList.remove('active');
        }
    }
    
    animateOpen() {
        const items = this.menuDropdown.querySelectorAll('.user-menu-item');
        items.forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'translateX(-20px)';
            
            setTimeout(() => {
                item.style.transition = 'all 0.3s ease';
                item.style.opacity = '1';
                item.style.transform = 'translateX(0)';
            }, index * 50);
        });
    }
    
    setupMenuItems() {
        // Gestione click su Profilo
        const profileLink = document.querySelector('[data-action="profile"]');
        if (profileLink) {
            profileLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.close();
                this.showProfileModal();
            });
        }
        
        // Gestione click su Cambio Password
        const passwordLink = document.querySelector('[data-action="change-password"]');
        if (passwordLink) {
            passwordLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.close();
                this.showPasswordModal();
            });
        }
        
        // Gestione click su Impostazioni
        const settingsLink = document.querySelector('[data-action="settings"]');
        if (settingsLink) {
            settingsLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.close();
                showAlert('Impostazioni disponibili prossimamente', 'info');
            });
        }
    }
    
    showProfileModal() {
        // Crea modal profilo se non esiste
        let modal = document.getElementById('profileModal');
        if (!modal) {
            modal = this.createProfileModal();
            document.body.appendChild(modal);
        }
        
        // Mostra modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Carica dati profilo
        this.loadProfileData();
    }
    
    showPasswordModal() {
        // Crea modal password se non esiste
        let modal = document.getElementById('passwordModal');
        if (!modal) {
            modal = this.createPasswordModal();
            document.body.appendChild(modal);
        }
        
        // Mostra modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
    
    createProfileModal() {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'profileModal';
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-user-circle me-2"></i>Il Mio Profilo
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="text-center mb-4">
                            <div class="avatar-xlarge mx-auto mb-3">
                                <i class="fas fa-user"></i>
                            </div>
                            <h4 id="profile-username">-</h4>
                            <span id="profile-role-badge" class="badge">-</span>
                        </div>
                        
                        <div class="profile-info">
                            <div class="info-row">
                                <span class="info-label">
                                    <i class="fas fa-at"></i> Username:
                                </span>
                                <span id="profile-username-detail" class="info-value">-</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">
                                    <i class="fas fa-shield-alt"></i> Ruolo:
                                </span>
                                <span id="profile-role-detail" class="info-value">-</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">
                                    <i class="fas fa-key"></i> Permessi:
                                </span>
                                <span id="profile-permissions" class="info-value">-</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">
                                    <i class="fas fa-clock"></i> Ultimo accesso:
                                </span>
                                <span id="profile-last-login" class="info-value">-</span>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-times"></i> Chiudi
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Aggiungi stili inline per il modal
        const style = document.createElement('style');
        style.textContent = `
            .avatar-xlarge {
                width: 100px;
                height: 100px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 3rem;
                box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
            }
            
            .profile-info {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
            }
            
            .info-row {
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #e9ecef;
            }
            
            .info-row:last-child {
                border-bottom: none;
            }
            
            .info-label {
                font-weight: 600;
                color: #6c757d;
            }
            
            .info-value {
                color: #333;
            }
        `;
        document.head.appendChild(style);
        
        return modal;
    }
    
    createPasswordModal() {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'passwordModal';
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-warning text-dark">
                        <h5 class="modal-title">
                            <i class="fas fa-key me-2"></i>Cambio Password
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form id="change-password-form-modal">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">Password Attuale</label>
                                <input type="password" class="form-control" name="current_password" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Nuova Password</label>
                                <input type="password" class="form-control" name="new_password" 
                                       required minlength="6" id="new-password-modal">
                                <div id="password-strength-modal" class="mt-2"></div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Conferma Nuova Password</label>
                                <input type="password" class="form-control" name="confirm_password" required>
                            </div>
                            
                            <div class="alert alert-info">
                                <i class="fas fa-info-circle"></i>
                                La password deve contenere almeno 6 caratteri
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                <i class="fas fa-times"></i> Annulla
                            </button>
                            <button type="submit" class="btn btn-warning">
                                <i class="fas fa-save"></i> Aggiorna Password
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        
        // Aggiungi event listener per il form
        setTimeout(() => {
            const form = document.getElementById('change-password-form-modal');
            const newPasswordField = document.getElementById('new-password-modal');
            
            if (newPasswordField) {
                newPasswordField.addEventListener('input', function() {
                    checkPasswordStrength(this.value, 'password-strength-modal');
                });
            }
            
            if (form) {
                form.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    await this.handlePasswordChange(e);
                });
            }
        }, 100);
        
        return modal;
    }
    
    async loadProfileData() {
        try {
            const response = await fetch('/api/profile/info');
            const data = await response.json();
            
            if (data.success) {
                const user = data.user;
                
                // Aggiorna elementi del modal
                document.getElementById('profile-username').textContent = user.username;
                document.getElementById('profile-username-detail').textContent = user.username;
                
                // Ruolo con badge colorato
                const roleMap = {
                    'admin': { name: 'Amministratore', class: 'bg-danger', icon: '👑' },
                    'gestore': { name: 'Gestore', class: 'bg-warning', icon: '👔' },
                    'readonly': { name: 'Solo Lettura', class: 'bg-success', icon: '👁️' }
                };
                
                const roleInfo = roleMap[user.role] || { name: 'Utente', class: 'bg-secondary', icon: '👤' };
                
                const roleBadge = document.getElementById('profile-role-badge');
                roleBadge.textContent = `${roleInfo.icon} ${roleInfo.name}`;
                roleBadge.className = `badge ${roleInfo.class}`;
                
                document.getElementById('profile-role-detail').textContent = roleInfo.name;
                
                // Permessi
                const permissions = {
                    'admin': 'Accesso completo al sistema',
                    'gestore': 'Gestione accessi e visualizzazione log',
                    'readonly': 'Solo visualizzazione log'
                };
                
                document.getElementById('profile-permissions').textContent = 
                    permissions[user.role] || 'Permessi base';
                
                // Ultimo accesso (simulato)
                const lastLogin = user.login_time || new Date().toLocaleString('it-IT');
                document.getElementById('profile-last-login').textContent = lastLogin;
            }
        } catch (error) {
            console.error('Errore caricamento profilo:', error);
            showAlert('Errore caricamento dati profilo', 'danger');
        }
    }
    
    async handlePasswordChange(e) {
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);
        
        // Validazione
        if (data.new_password !== data.confirm_password) {
            showAlert('Le password non coincidono', 'danger');
            return;
        }
        
        if (data.new_password.length < 6) {
            showAlert('La password deve essere di almeno 6 caratteri', 'danger');
            return;
        }
        
        try {
            const response = await fetch('/api/profile/change-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                showAlert('Password aggiornata con successo', 'success');
                // Chiudi modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('passwordModal'));
                modal.hide();
                // Reset form
                e.target.reset();
            } else {
                showAlert(result.error || 'Errore durante il cambio password', 'danger');
            }
        } catch (error) {
            showAlert('Errore di connessione al server', 'danger');
            console.error('Errore:', error);
        }
    }
}

// Funzione per valutare forza password
function checkPasswordStrength(password, targetId = 'password-strength') {
    let strength = 0;
    const strengthDiv = document.getElementById(targetId);
    
    if (!strengthDiv) return;
    
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
    let strengthColor = '';
    
    if (strength <= 2) {
        strengthText = 'Password debole';
        strengthClass = 'text-danger';
        strengthColor = '#dc3545';
    } else if (strength <= 3) {
        strengthText = 'Password media';
        strengthClass = 'text-warning';
        strengthColor = '#ffc107';
    } else {
        strengthText = 'Password forte';
        strengthClass = 'text-success';
        strengthColor = '#28a745';
    }
    
    strengthDiv.innerHTML = `
        <div class="${strengthClass}" style="font-size: 0.875rem;">
            <i class="fas fa-shield-alt"></i> ${strengthText}
            <div class="progress mt-1" style="height: 5px;">
                <div class="progress-bar" style="width: ${strength * 20}%; background-color: ${strengthColor};"></div>
            </div>
        </div>
    `;
}

// Inizializza menu utente quando il DOM è pronto
const userMenu = new UserMenu();

// Esporta per uso globale se necessario
window.UserMenu = UserMenu;
