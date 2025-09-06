// User Management Enhanced - Sistema completo gestione utenti con password management

class UserManagementEnhanced {
    constructor() {
        this.users = [];
        this.currentUser = null;
        this.init();
    }

    init() {
        this.loadUsers();
        this.setupEventHandlers();
        this.loadPasswordPolicy();
        setInterval(() => this.loadUsers(), 30000); // Refresh ogni 30s
    }

    setupEventHandlers() {
        // Form creazione utente
        const createForm = document.getElementById('create-user-form');
        if (createForm) {
            createForm.addEventListener('submit', (e) => this.handleCreateUser(e));
        }

        // Password strength indicator
        const passwordInput = document.getElementById('new-password');
        if (passwordInput) {
            passwordInput.addEventListener('input', (e) => this.checkPasswordStrength(e.target.value));
        }

        // Filtri e ricerca
        const searchInput = document.getElementById('user-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.filterUsers(e.target.value));
        }
    }

    async loadUsers() {
        try {
            const response = await fetch('/api/users/list');
            const data = await response.json();
            
            if (data.success) {
                this.users = data.users;
                this.renderUsersTable();
                this.updateStatistics();
            }
        } catch (error) {
            console.error('Errore caricamento utenti:', error);
            this.showAlert('Errore nel caricamento degli utenti', 'danger');
        }
    }

    renderUsersTable() {
        const tbody = document.getElementById('users-table');
        if (!tbody) return;

        if (this.users.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center py-4">
                        <i class="fas fa-users text-muted fa-3x mb-3"></i>
                        <p class="text-muted">Nessun utente trovato</p>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = this.users.map(user => `
            <tr data-username="${user.username}">
                <td>
                    <div class="d-flex align-items-center">
                        <div class="avatar-sm me-2">
                            <span class="avatar-title rounded-circle bg-primary">
                                ${user.username[0].toUpperCase()}
                            </span>
                        </div>
                        <div>
                            <strong>${user.username}</strong>
                            ${user.email ? `<br><small class="text-muted">${user.email}</small>` : ''}
                        </div>
                    </div>
                </td>
                <td>
                    <span class="badge ${this.getRoleClass(user.role)}">
                        ${this.getRoleIcon(user.role)} ${user.role_name}
                    </span>
                </td>
                <td>
                    ${user.created_by || 'system'}
                    <br><small class="text-muted">${this.formatDate(user.created_at)}</small>
                </td>
                <td>
                    ${this.formatLastLogin(user.last_login)}
                    ${this.getPasswordStatus(user)}
                </td>
                <td>
                    ${this.getUserStatus(user)}
                </td>
                <td class="text-end">
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="userMgmt.editUser('${user.username}')" 
                                title="Modifica">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-warning" onclick="userMgmt.resetPassword('${user.username}')" 
                                title="Reset Password">
                            <i class="fas fa-key"></i>
                        </button>
                        <button class="btn btn-outline-info" onclick="userMgmt.viewUserDetails('${user.username}')" 
                                title="Dettagli">
                            <i class="fas fa-info-circle"></i>
                        </button>
                        ${user.attivo ? 
                            `<button class="btn btn-outline-danger" onclick="userMgmt.toggleUserStatus('${user.username}', false)" 
                                     title="Disattiva">
                                <i class="fas fa-ban"></i>
                            </button>` :
                            `<button class="btn btn-outline-success" onclick="userMgmt.toggleUserStatus('${user.username}', true)" 
                                     title="Attiva">
                                <i class="fas fa-check"></i>
                            </button>`
                        }
                        <button class="btn btn-outline-danger" onclick="userMgmt.deleteUser('${user.username}')" 
                                title="Elimina">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    getRoleIcon(role) {
        const icons = {
            'admin': '👑',
            'user_manager': '👔',
            'viewer': '👁️'
        };
        return icons[role] || '👤';
    }
    
    getRoleClass(role) {
        const classes = {
            'admin': 'bg-danger text-white',
            'user_manager': 'bg-primary text-white',
            'viewer': 'bg-success text-white'
        };
        return classes[role] || 'bg-secondary text-white';
    }

    getPasswordStatus(user) {
        let html = '';
        
        // Password scaduta
        if (user.password_expires_at) {
            const expires = new Date(user.password_expires_at);
            const now = new Date();
            const daysLeft = Math.ceil((expires - now) / (1000 * 60 * 60 * 24));
            
            if (daysLeft < 0) {
                html += '<br><span class="badge bg-danger">Password scaduta</span>';
            } else if (daysLeft < 7) {
                html += `<br><span class="badge bg-warning">Scade tra ${daysLeft}g</span>`;
            }
        }
        
        // Deve cambiare password
        if (user.must_change_password) {
            html += '<br><span class="badge bg-warning">Cambio richiesto</span>';
        }
        
        // Account bloccato
        if (user.locked_until) {
            const locked = new Date(user.locked_until);
            if (locked > new Date()) {
                html += '<br><span class="badge bg-danger">Bloccato</span>';
            }
        }
        
        // Tentativi falliti
        if (user.failed_attempts > 3) {
            html += `<br><small class="text-danger">${user.failed_attempts} tentativi falliti</small>`;
        }
        
        return html;
    }

    getUserStatus(user) {
        if (!user.attivo) {
            return '<span class="badge bg-danger">Disattivato</span>';
        }
        
        if (user.locked_until && new Date(user.locked_until) > new Date()) {
            return '<span class="badge bg-warning">Bloccato</span>';
        }
        
        return '<span class="badge bg-success">Attivo</span>';
    }

    formatDate(dateStr) {
        if (!dateStr) return 'N/A';
        const date = new Date(dateStr);
        return date.toLocaleDateString('it-IT', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    formatLastLogin(lastLogin) {
        if (!lastLogin || lastLogin === 'Mai') {
            return '<span class="text-muted">Mai effettuato</span>';
        }
        return this.formatDate(lastLogin);
    }

    async handleCreateUser(event) {
        event.preventDefault();
        
        const formData = {
            username: document.getElementById('new-username').value,
            password: document.getElementById('new-password').value,
            email: document.getElementById('new-email').value,
            nome: document.getElementById('new-nome').value,
            cognome: document.getElementById('new-cognome').value,
            role: document.getElementById('new-role').value
        };

        // Valida password
        const passwordValid = await this.validatePassword(formData.password, formData.username);
        if (!passwordValid) {
            return;
        }

        try {
            const response = await fetch('/api/users/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            
            if (data.success) {
                this.showAlert(`Utente ${formData.username} creato con successo`, 'success');
                
                // Mostra password temporanea
                this.showTempPassword(formData.username, formData.password);
                
                // Reset form
                event.target.reset();
                
                // Ricarica lista
                this.loadUsers();
            } else {
                this.showAlert(data.error || 'Errore creazione utente', 'danger');
            }
        } catch (error) {
            this.showAlert('Errore di connessione', 'danger');
        }
    }

    async editUser(username) {
        const user = this.users.find(u => u.username === username);
        if (!user) return;

        // Mostra modal di modifica
        const modal = this.createEditModal(user);
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    createEditModal(user) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Modifica Profilo: ${user.username}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="edit-user-form" enctype="multipart/form-data">
                            <div class="row">
                                <div class="col-md-4 text-center">
                                    <div class="mb-3">
                                        <img id="avatar-preview" 
                                             src="${user.avatar_path || '/api/static/img/default-avatar.png'}" 
                                             class="rounded-circle mb-3" 
                                             style="width: 150px; height: 150px; object-fit: cover; border: 3px solid #dee2e6;">
                                        <div>
                                            <label for="avatar-upload" class="btn btn-sm btn-outline-primary">
                                                📷 Cambia Avatar
                                            </label>
                                            <input type="file" id="avatar-upload" accept="image/*" 
                                                   style="display: none;" onchange="userMgmt.previewAvatar(this)">
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-8">
                                    <div class="row">
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label">Nome</label>
                                            <input type="text" class="form-control" id="edit-nome" 
                                                   value="${user.nome || ''}" placeholder="Nome">
                                        </div>
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label">Cognome</label>
                                            <input type="text" class="form-control" id="edit-cognome" 
                                                   value="${user.cognome || ''}" placeholder="Cognome">
                                        </div>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Email</label>
                                        <input type="email" class="form-control" id="edit-email" 
                                               value="${user.email || ''}" placeholder="email@esempio.it">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Telefono</label>
                                        <input type="tel" class="form-control" id="edit-telefono" 
                                               value="${user.telefono || ''}" placeholder="+39 123 456 7890">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Bio</label>
                                        <textarea class="form-control" id="edit-bio" rows="3" 
                                                  placeholder="Breve descrizione...">${user.bio || ''}</textarea>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Ruolo</label>
                                        <select class="form-select" id="edit-role">
                                            <option value="admin" ${user.role === 'admin' ? 'selected' : ''}>
                                                👑 Amministratore
                                            </option>
                                            <option value="user_manager" ${user.role === 'user_manager' ? 'selected' : ''}>
                                                👔 Gestore Utenti
                                            </option>
                                            <option value="viewer" ${user.role === 'viewer' ? 'selected' : ''}>
                                                👁️ Visualizzatore
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Annulla</button>
                        <button type="button" class="btn btn-primary" onclick="userMgmt.saveUserChanges('${user.username}')">
                            Salva Modifiche
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        return modal;
    }

    previewAvatar(input) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById('avatar-preview').src = e.target.result;
            };
            reader.readAsDataURL(input.files[0]);
        }
    }

    async saveUserChanges(username) {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('nome', document.getElementById('edit-nome').value);
        formData.append('cognome', document.getElementById('edit-cognome').value);
        formData.append('email', document.getElementById('edit-email').value);
        formData.append('telefono', document.getElementById('edit-telefono').value);
        formData.append('bio', document.getElementById('edit-bio').value);
        formData.append('role', document.getElementById('edit-role').value);
        
        // Aggiungi avatar se selezionato
        const avatarInput = document.getElementById('avatar-upload');
        if (avatarInput.files && avatarInput.files[0]) {
            formData.append('avatar', avatarInput.files[0]);
        }

        try {
            const response = await fetch('/api/users/update-profile', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.success) {
                this.showAlert('Utente aggiornato con successo', 'success');
                bootstrap.Modal.getInstance(document.querySelector('.modal')).hide();
                this.loadUsers();
            } else {
                this.showAlert(data.error || 'Errore aggiornamento', 'danger');
            }
        } catch (error) {
            this.showAlert('Errore di connessione', 'danger');
        }
    }

    async resetPassword(username) {
        const user = this.users.find(u => u.username === username);
        if (!user) return;
        
        // Mostra modal con opzioni
        const modal = this.createPasswordResetModal(user);
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }
    
    createPasswordResetModal(user) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-warning">
                        <h5 class="modal-title">
                            <i class="fas fa-key me-2"></i>Gestione Password: ${user.username}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            Scegli come gestire la password per l'utente <strong>${user.username}</strong>
                            ${user.email ? `(${user.email})` : '(nessuna email configurata)'}
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="card h-100">
                                    <div class="card-body">
                                        <h5 class="card-title">
                                            <i class="fas fa-edit text-primary"></i> Cambio Diretto
                                        </h5>
                                                                                
                                        <div class="mb-3">
                                            <label class="form-label">Nuova Password</label>
                                            <div class="input-group">
                                                <input type="text" class="form-control" id="direct-password-${user.username}" 
                                                       placeholder="Inserisci password">
                                                <button class="btn btn-outline-secondary" 
                                                        onclick="userMgmt.generatePassword('direct-password-${user.username}')">
                                                    <i class="fas fa-dice"></i> Genera
                                                </button>
                                            </div>
                                            <div class="password-strength mt-2" id="direct-strength-${user.username}"></div>
                                            <div id="password-requirements-${user.username}" class="mt-2 small">
                                                <div class="requirement-item" data-req="length">
                                                    <i class="fas fa-circle text-muted"></i> Minimo 8 caratteri
                                                </div>
                                                <div class="requirement-item" data-req="uppercase">
                                                    <i class="fas fa-circle text-muted"></i> Una lettera maiuscola
                                                </div>
                                                <div class="requirement-item" data-req="lowercase">
                                                    <i class="fas fa-circle text-muted"></i> Una lettera minuscola
                                                </div>
                                                <div class="requirement-item" data-req="number">
                                                    <i class="fas fa-circle text-muted"></i> Un numero
                                                </div>
                                                <div class="requirement-item" data-req="special">
                                                    <i class="fas fa-circle text-muted"></i> Un carattere speciale
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div class="form-check mb-3">
                                            <input type="checkbox" class="form-check-input" 
                                                   id="force-change-${user.username}" checked>
                                            <label class="form-check-label" for="force-change-${user.username}">
                                                Richiedi cambio al primo accesso
                                            </label>
                                        </div>
                                        
                                        <button class="btn btn-primary w-100" 
                                                onclick="userMgmt.setDirectPassword('${user.username}')">
                                            <i class="fas fa-save me-2"></i>Imposta Password
                                        </button>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-md-6">
                                <div class="card h-100">
                                    <div class="card-body">
                                        <h5 class="card-title">
                                            <i class="fas fa-envelope text-info"></i> Invio Link Reset
                                        </h5>
                                        <p class="card-text">Invia all'utente un link per reimpostare autonomamente la password.</p>
                                        
                                        <div class="mb-3">
                                            <label class="form-label">Email Destinatario</label>
                                            <input type="email" class="form-control" id="reset-email-${user.username}" 
                                                   value="${user.email || ''}" 
                                                   placeholder="email@esempio.it">
                                        </div>
                                        
                                        <div class="mb-3">
                                            <label class="form-label">Messaggio Personalizzato</label>
                                            <textarea class="form-control" id="reset-message-${user.username}" 
                                                      rows="3" placeholder="Opzionale: aggiungi un messaggio personalizzato"></textarea>
                                        </div>
                                        
                                        <button class="btn btn-info w-100" 
                                                onclick="userMgmt.sendResetLink('${user.username}')"
                                                ${!user.email ? 'disabled' : ''}>
                                            <i class="fas fa-paper-plane me-2"></i>Invia Link Reset
                                        </button>
                                        
                                        ${!user.email ? '<small class="text-danger mt-2 d-block">⚠️ Email non configurata per questo utente</small>' : ''}
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-3">
                            <div class="card bg-light">
                                <div class="card-body">
                                    <h6><i class="fas fa-history me-2"></i>Informazioni Password Corrente</h6>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <small>
                                                <strong>Ultima modifica:</strong> 
                                                ${user.password_changed_at ? this.formatDate(user.password_changed_at) : 'Mai'}
                                            </small>
                                        </div>
                                        <div class="col-md-6">
                                            <small>
                                                <strong>Scadenza:</strong> 
                                                ${user.password_expires_at ? this.formatDate(user.password_expires_at) : 'Mai'}
                                            </small>
                                        </div>
                                        <div class="col-md-6">
                                            <small>
                                                <strong>Tentativi falliti:</strong> ${user.failed_attempts || 0}
                                            </small>
                                        </div>
                                        <div class="col-md-6">
                                            <small>
                                                <strong>Account bloccato:</strong> 
                                                ${user.locked_until && new Date(user.locked_until) > new Date() ? 'Sì' : 'No'}
                                            </small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Chiudi</button>
                    </div>
                </div>
            </div>
        `;
        
        // Setup password strength checker con validazione in tempo reale
        const passwordInput = modal.querySelector(`#direct-password-${user.username}`);
        passwordInput.addEventListener('input', (e) => {
            const password = e.target.value;
            this.checkPasswordStrength(password, `direct-strength-${user.username}`);
            this.updatePasswordRequirementsDisplay(password, user.username);
            
            // Rimuovi classe invalid quando l'utente digita
            if (password) {
                passwordInput.classList.remove('is-invalid');
            }
        });
        
        return modal;
    }
    
    updatePasswordRequirementsDisplay(password, username) {
        const container = document.getElementById(`password-requirements-${username}`);
        if (!container) return;
        
        const requirements = {
            'length': password.length >= 8,
            'uppercase': /[A-Z]/.test(password),
            'lowercase': /[a-z]/.test(password),
            'number': /\d/.test(password),
            'special': /[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/]/.test(password)
        };
        
        Object.keys(requirements).forEach(req => {
            const element = container.querySelector(`[data-req="${req}"]`);
            if (element) {
                const icon = element.querySelector('i');
                if (requirements[req]) {
                    icon.className = 'fas fa-check-circle text-success';
                    element.classList.add('text-success');
                    element.classList.remove('text-danger');
                } else {
                    icon.className = 'fas fa-times-circle text-danger';
                    element.classList.add('text-danger');
                    element.classList.remove('text-success');
                }
            }
        });
        
        // Aggiungi/rimuovi bottone in base alla validità
        const submitButton = document.querySelector(`button[onclick*="setDirectPassword('${username}')"]`);
        if (submitButton) {
            const validation = this.validatePasswordRequirements(password);
            if (validation.valid) {
                submitButton.classList.remove('btn-secondary', 'disabled');
                submitButton.classList.add('btn-primary');
                submitButton.disabled = false;
            } else {
                submitButton.classList.remove('btn-primary');
                submitButton.classList.add('btn-secondary', 'disabled');
                submitButton.disabled = true;
            }
        }
    }
    
    validatePasswordRequirements(password) {
        const errors = [];
        let valid = true;
        
        // Requisito 1: Lunghezza minima 8 caratteri
        if (password.length < 8) {
            errors.push('Minimo 8 caratteri (hai ' + password.length + ')');
            valid = false;
        }
        
        // Requisito 2: Almeno una lettera maiuscola
        if (!/[A-Z]/.test(password)) {
            errors.push('Almeno una lettera MAIUSCOLA');
            valid = false;
        }
        
        // Requisito 3: Almeno una lettera minuscola
        if (!/[a-z]/.test(password)) {
            errors.push('Almeno una lettera minuscola');
            valid = false;
        }
        
        // Requisito 4: Almeno un numero
        if (!/\d/.test(password)) {
            errors.push('Almeno un numero');
            valid = false;
        }
        
        // Requisito 5: Almeno un carattere speciale
        if (!/[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/]/.test(password)) {
            errors.push('Almeno un carattere speciale (!@#$%^&*...)');
            valid = false;
        }
        
        // Requisito 6: Non deve contenere spazi
        if (/\s/.test(password)) {
            errors.push('Non deve contenere spazi');
            valid = false;
        }
        
        return {
            valid: valid,
            errors: errors,
            strength: this.calculatePasswordStrengthScore(password)
        };
    }
    
    calculatePasswordStrengthScore(password) {
        let score = 0;
        
        // Lunghezza
        if (password.length >= 8) score += 20;
        if (password.length >= 12) score += 10;
        if (password.length >= 16) score += 10;
        
        // Complessità
        if (/[a-z]/.test(password)) score += 15;
        if (/[A-Z]/.test(password)) score += 15;
        if (/\d/.test(password)) score += 15;
        if (/[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/]/.test(password)) score += 15;
        
        // Varietà di caratteri
        const uniqueChars = new Set(password).size;
        if (uniqueChars >= 10) score += 10;
        
        return Math.min(score, 100);
    }
    
    generatePassword(inputId) {
        const length = 12;
        const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*";
        let password = "";
        
        // Assicura almeno un carattere di ogni tipo
        password += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[Math.floor(Math.random() * 26)];
        password += "abcdefghijklmnopqrstuvwxyz"[Math.floor(Math.random() * 26)];
        password += "0123456789"[Math.floor(Math.random() * 10)];
        password += "!@#$%^&*"[Math.floor(Math.random() * 8)];
        
        // Riempi il resto
        for (let i = password.length; i < length; i++) {
            password += charset[Math.floor(Math.random() * charset.length)];
        }
        
        // Mescola la password
        password = password.split('').sort(() => 0.5 - Math.random()).join('');
        
        document.getElementById(inputId).value = password;
        document.getElementById(inputId).type = 'text'; // Mostra la password generata
        
        // Trigger strength check
        const username = inputId.replace('direct-password-', '');
        this.checkPasswordStrength(password, `direct-strength-${username}`);
    }
    
    async setDirectPassword(username) {
        const passwordInput = document.getElementById(`direct-password-${username}`);
        const forceChange = document.getElementById(`force-change-${username}`).checked;
        const password = passwordInput.value;
        
        if (!password) {
            this.showAlert('Inserisci una password', 'warning');
            return;
        }
        
        // VALIDAZIONE RIGOROSA DELLA PASSWORD
        const validationResult = this.validatePasswordRequirements(password);
        if (!validationResult.valid) {
            // Mostra TUTTI i requisiti mancanti
            let errorMessage = 'Password non valida. Requisiti mancanti:\n';
            validationResult.errors.forEach(error => {
                errorMessage += `❌ ${error}\n`;
            });
            this.showAlert(errorMessage, 'danger', 7000);
            
            // Evidenzia il campo password
            passwordInput.classList.add('is-invalid');
            passwordInput.focus();
            return;
        }
        
        // Verifica anche che non sia una password comune
        const commonPasswords = ['password', '12345678', 'admin123', 'Password123!', 'Qwerty123!'];
        if (commonPasswords.some(common => password.toLowerCase().includes(common.toLowerCase()))) {
            this.showAlert('Password troppo comune o prevedibile. Scegli una password più sicura.', 'danger');
            passwordInput.classList.add('is-invalid');
            return;
        }
        
        try {
            const response = await fetch('/api/users/admin-set-password', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                credentials: 'same-origin',  // Importante per i cookie di sessione
                body: JSON.stringify({
                    username: username,
                    password: password,
                    must_change_password: forceChange
                })
            });
            
            // Verifica se la risposta è OK
            if (!response.ok) {
                console.error('Errore HTTP:', response.status, response.statusText);
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('Risposta API:', data);
            
            if (data.success) {
                this.showAlert(`Password impostata per ${username}`, 'success');
                
                // Mostra modal con la password
                this.showNewPasswordModal(username, password);
                
                // Chiudi modal corrente se esiste
                const currentModal = document.querySelector('.modal.show');
                if (currentModal) {
                    const bsModal = bootstrap.Modal.getInstance(currentModal);
                    if (bsModal) {
                        bsModal.hide();
                    }
                }
                
                // Ricarica utenti
                this.loadUsers();
            } else {
                // Mostra errori dettagliati dal server
                let errorMessage = data.error || 'Errore impostazione password';
                if (data.details && Array.isArray(data.details)) {
                    errorMessage += '\n\nProblemi rilevati:\n';
                    data.details.forEach(detail => {
                        errorMessage += `❌ ${detail}\n`;
                    });
                }
                this.showAlert(errorMessage, 'danger', 8000);
                
                // Evidenzia campo password
                passwordInput.classList.add('is-invalid');
            }
        } catch (error) {
            console.error('Errore setDirectPassword:', error);
            this.showAlert(`Errore: ${error.message || 'Errore di connessione'}`, 'danger');
        }
    }
    
    async sendResetLink(username) {
        const emailInput = document.getElementById(`reset-email-${username}`);
        const messageInput = document.getElementById(`reset-message-${username}`);
        const email = emailInput.value;
        const message = messageInput.value;
        
        if (!email) {
            this.showAlert('Inserisci un indirizzo email', 'warning');
            return;
        }
        
        try {
            const response = await fetch('/api/users/send-reset-link', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    username: username,
                    email: email,
                    message: message
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showAlert(`Link di reset inviato a ${email}`, 'success');
                
                // Se c'è un debug token (email non configurata), mostralo
                if (data.debug_token) {
                    this.showDebugToken(username, data.debug_token);
                }
                
                // Chiudi modal corrente se esiste
                const currentModal = document.querySelector('.modal.show');
                if (currentModal) {
                    const bsModal = bootstrap.Modal.getInstance(currentModal);
                    if (bsModal) {
                        bsModal.hide();
                    }
                }
            } else {
                this.showAlert(data.error || 'Errore invio link', 'danger');
            }
        } catch (error) {
            this.showAlert('Errore di connessione', 'danger');
        }
    }
    
    showNewPasswordModal(username, password) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-success text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-check-circle me-2"></i>Password Impostata
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-warning">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            <strong>Importante:</strong> Comunica questa password all'utente.
                            Non sarà più visibile dopo la chiusura!
                        </div>
                        
                        <div class="text-center">
                            <h5>Utente: <span class="text-primary">${username}</span></h5>
                            <div class="my-3 p-3 bg-light rounded">
                                <label class="form-label">Nuova Password:</label>
                                <div class="input-group">
                                    <input type="text" class="form-control form-control-lg text-center font-monospace" 
                                           id="new-pwd-display" value="${password}" readonly>
                                    <button class="btn btn-primary" type="button" onclick="copyPasswordToClipboard('new-pwd-display')">
                                        <i class="fas fa-copy"></i> Copia
                                    </button>
                                </div>
                            </div>
                            
                            <div class="alert alert-info">
                                <small>
                                    <i class="fas fa-info-circle me-1"></i>
                                    L'utente dovrà cambiare questa password al primo accesso.
                                </small>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            Ho copiato la password
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    async toggleUserStatus(username, activate) {
        const action = activate ? 'attivare' : 'disattivare';
        
        if (!confirm(`Vuoi davvero ${action} l'utente ${username}?`)) {
            return;
        }

        try {
            const response = await fetch('/api/users/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    username: username,
                    attivo: activate
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.showAlert(`Utente ${activate ? 'attivato' : 'disattivato'}`, 'success');
                this.loadUsers();
            } else {
                this.showAlert(data.error || 'Errore aggiornamento stato', 'danger');
            }
        } catch (error) {
            this.showAlert('Errore di connessione', 'danger');
        }
    }

    async deleteUser(username) {
        if (!confirm(`Sei sicuro di voler eliminare definitivamente l'utente ${username}?`)) {
            return;
        }

        try {
            const response = await fetch('/api/users/delete', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: username})
            });

            const data = await response.json();
            
            if (data.success) {
                this.showAlert('Utente eliminato', 'success');
                this.loadUsers();
            } else {
                this.showAlert(data.error || 'Errore eliminazione', 'danger');
            }
        } catch (error) {
            this.showAlert('Errore di connessione', 'danger');
        }
    }

    viewUserDetails(username) {
        const user = this.users.find(u => u.username === username);
        if (!user) return;

        const modal = this.createDetailsModal(user);
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    createDetailsModal(user) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Dettagli Utente: ${user.username}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Informazioni Account</h6>
                                <table class="table table-sm">
                                    <tr><td><strong>Username:</strong></td><td>${user.username}</td></tr>
                                    <tr><td><strong>Email:</strong></td><td>${user.email || 'Non impostata'}</td></tr>
                                    <tr><td><strong>Ruolo:</strong></td><td>${user.role_name}</td></tr>
                                    <tr><td><strong>Stato:</strong></td><td>${user.attivo ? 'Attivo' : 'Disattivato'}</td></tr>
                                </table>
                            </div>
                            <div class="col-md-6">
                                <h6>Informazioni Accesso</h6>
                                <table class="table table-sm">
                                    <tr><td><strong>Ultimo accesso:</strong></td><td>${this.formatLastLogin(user.last_login)}</td></tr>
                                    <tr><td><strong>Tentativi falliti:</strong></td><td>${user.failed_attempts || 0}</td></tr>
                                    <tr><td><strong>Bloccato fino:</strong></td><td>${user.locked_until ? this.formatDate(user.locked_until) : 'No'}</td></tr>
                                </table>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-md-6">
                                <h6>Informazioni Password</h6>
                                <table class="table table-sm">
                                    <tr><td><strong>Cambiata il:</strong></td><td>${user.password_changed_at ? this.formatDate(user.password_changed_at) : 'Mai'}</td></tr>
                                    <tr><td><strong>Scade il:</strong></td><td>${user.password_expires_at ? this.formatDate(user.password_expires_at) : 'Mai'}</td></tr>
                                    <tr><td><strong>Cambio richiesto:</strong></td><td>${user.must_change_password ? 'Sì' : 'No'}</td></tr>
                                </table>
                            </div>
                            <div class="col-md-6">
                                <h6>Informazioni Sistema</h6>
                                <table class="table table-sm">
                                    <tr><td><strong>Creato il:</strong></td><td>${this.formatDate(user.created_at)}</td></tr>
                                    <tr><td><strong>Creato da:</strong></td><td>${user.created_by || 'system'}</td></tr>
                                    <tr><td><strong>Modificato il:</strong></td><td>${user.modified_at ? this.formatDate(user.modified_at) : 'Mai'}</td></tr>
                                    <tr><td><strong>Modificato da:</strong></td><td>${user.modified_by || 'N/A'}</td></tr>
                                </table>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Chiudi</button>
                    </div>
                </div>
            </div>
        `;
        return modal;
    }

    async checkPasswordStrength(password, targetId = 'strength-bar') {
        const strengthBar = document.getElementById(targetId);
        if (!strengthBar) return;

        if (!password) {
            strengthBar.style.width = '0%';
            strengthBar.className = 'password-strength';
            return;
        }

        try {
            const response = await fetch('/api/password/validate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({password: password})
            });

            const data = await response.json();
            
            if (data.success) {
                const strength = data.strength || 0;
                strengthBar.style.width = strength + '%';
                
                if (strength < 40) {
                    strengthBar.className = 'password-strength bg-danger';
                } else if (strength < 70) {
                    strengthBar.className = 'password-strength bg-warning';
                } else {
                    strengthBar.className = 'password-strength bg-success';
                }
            } else {
                strengthBar.className = 'password-strength bg-danger';
                strengthBar.style.width = '100%';
                this.showAlert(data.message, 'warning');
            }
        } catch (error) {
            console.error('Errore validazione password:', error);
        }
    }

    async validatePassword(password, username) {
        try {
            const response = await fetch('/api/password/validate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({password: password, username: username})
            });

            const data = await response.json();
            
            if (!data.success) {
                this.showAlert(data.message, 'danger');
                return false;
            }
            
            return true;
        } catch (error) {
            this.showAlert('Errore validazione password', 'danger');
            return false;
        }
    }

    async loadPasswordPolicy() {
        try {
            const response = await fetch('/api/password/policy');
            const data = await response.json();
            
            if (data.success) {
                this.passwordPolicy = data.policy;
                this.updatePasswordRequirements();
            }
        } catch (error) {
            console.error('Errore caricamento policy:', error);
        }
    }

    updatePasswordRequirements() {
        const reqDiv = document.getElementById('password-requirements');
        if (!reqDiv || !this.passwordPolicy) return;

        reqDiv.innerHTML = `
            <small class="text-muted">
                Requisiti password:
                <ul class="mb-0">
                    <li>Minimo ${this.passwordPolicy.min_length} caratteri</li>
                    ${this.passwordPolicy.require_uppercase ? '<li>Almeno una maiuscola</li>' : ''}
                    ${this.passwordPolicy.require_lowercase ? '<li>Almeno una minuscola</li>' : ''}
                    ${this.passwordPolicy.require_numbers ? '<li>Almeno un numero</li>' : ''}
                    ${this.passwordPolicy.require_special ? '<li>Almeno un carattere speciale</li>' : ''}
                </ul>
            </small>
        `;
    }

    updateStatistics() {
        let adminCount = 0, managerCount = 0, viewerCount = 0;
        
        this.users.forEach(user => {
            if (user.attivo) {
                switch(user.role) {
                    case 'admin': adminCount++; break;
                    case 'user_manager': managerCount++; break;
                    case 'viewer': viewerCount++; break;
                }
            }
        });

        document.getElementById('admin-count').textContent = adminCount;
        document.getElementById('manager-count').textContent = managerCount;
        document.getElementById('viewer-count').textContent = viewerCount;
        document.getElementById('total-count').textContent = this.users.length;
    }

    filterUsers(searchTerm) {
        const term = searchTerm.toLowerCase();
        const rows = document.querySelectorAll('#users-table tr');
        
        rows.forEach(row => {
            const username = row.dataset.username;
            if (!username) return;
            
            const user = this.users.find(u => u.username === username);
            if (!user) return;
            
            const matches = 
                user.username.toLowerCase().includes(term) ||
                (user.email && user.email.toLowerCase().includes(term)) ||
                user.role_name.toLowerCase().includes(term);
            
            row.style.display = matches ? '' : 'none';
        });
    }

    showTempPassword(username, password) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog'>
                <div class="modal-content'>
                    <div class="modal-header bg-success text-white'>
                        <h5 class="modal-title">
                            <i class="fas fa-key me-2"></i>Password Temporanea
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            Copia questa password e comunicala all'utente.
                            <br>L'utente dovrà cambiarla al primo accesso.
                        </div>
                        <h5>Username: <span class="text-primary">${username}</span></h5>
                        <div class="d-flex justify-content-center align-items-center gap-2 my-3">
                            <code class="h4 mb-0" id="temp-pwd">${password}</code>
                            <button class="btn btn-sm btn-outline-primary" onclick="userMgmt.copyToClipboard('temp-pwd')">
                                <i class="fas fa-copy"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    showDebugToken(username, token) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-warning">
                        <h5 class="modal-title">
                            <i class="fas fa-bug me-2"></i>Debug: Token Reset Password
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-warning">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Email non configurata. Usa questo link per il reset:
                        </div>
                        <p><strong>Username:</strong> ${username}</p>
                        <p><strong>Link reset:</strong></p>
                        <div class="input-group">
                            <input type="text" class="form-control" id="debug-link" 
                                   value="http://192.168.1.236:5000/reset-password?token=${token}" readonly>
                            <button class="btn btn-outline-primary" onclick="userMgmt.copyToClipboard('debug-link')">
                                <i class="fas fa-copy"></i> Copia
                            </button>
                        </div>
                        <p class="mt-3 text-muted">Il link scade tra 1 ora.</p>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    copyToClipboard(elementId) {
        const element = document.getElementById(elementId);
        if (!element) {
            console.error('Elemento non trovato:', elementId);
            return;
        }
        
        let text = '';
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            text = element.value;
        } else {
            text = element.textContent || element.innerText;
        }
        
        // Log per debug
        console.log('Copiando testo:', text);
        
        // Metodo 1: Prova con l'API moderna
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(() => {
                console.log('Copia riuscita con clipboard API');
                this.showCopySuccess(element);
            }).catch(err => {
                console.warn('Clipboard API fallita, uso fallback:', err);
                this.fallbackCopyToClipboard(text, element);
            });
        } else {
            // Metodo 2: Usa il fallback direttamente
            this.fallbackCopyToClipboard(text, element);
        }
    }
    
    fallbackCopyToClipboard(text, originalElement) {
        // Metodo alternativo che funziona anche su HTTP
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.top = "0";
        textArea.style.left = "0";
        textArea.style.width = "2em";
        textArea.style.height = "2em";
        textArea.style.padding = "0";
        textArea.style.border = "none";
        textArea.style.outline = "none";
        textArea.style.boxShadow = "none";
        textArea.style.background = "transparent";
        
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                console.log('Copia riuscita con execCommand');
                this.showCopySuccess(originalElement);
            } else {
                console.error('execCommand copy fallito');
                this.showAlert('Copia non riuscita - seleziona e copia manualmente', 'warning');
            }
        } catch (err) {
            console.error('Errore nella copia:', err);
            this.showAlert('Errore nella copia - seleziona e copia manualmente', 'danger');
        }
        
        document.body.removeChild(textArea);
    }
    
    showCopySuccess(element) {
        // Effetto visivo di conferma copia
        this.showAlert('✓ Password copiata negli appunti!', 'success', 2000);
        
        // Aggiungi effetto visivo all'elemento
        if (element) {
            const originalBg = element.style.backgroundColor;
            element.style.backgroundColor = '#d4edda';
            element.style.transition = 'background-color 0.3s';
            setTimeout(() => {
                element.style.backgroundColor = originalBg;
            }, 500);
        }
    }

    showAlert(message, type = 'info', duration = 5000) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
        alertDiv.style.zIndex = '9999';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        setTimeout(() => {
            alertDiv.remove();
        }, duration);
    }
}

// Funzione globale per la copia (utilizzabile da onclick)
window.copyPasswordToClipboard = function(elementId) {
    if (window.userMgmt) {
        window.userMgmt.copyToClipboard(elementId);
    } else {
        // Fallback se userMgmt non è ancora inizializzato
        const element = document.getElementById(elementId);
        if (element) {
            const text = element.value || element.textContent;
            if (navigator.clipboard) {
                navigator.clipboard.writeText(text).then(() => {
                    alert('Password copiata!');
                }).catch(() => {
                    element.select();
                    document.execCommand('copy');
                });
            } else {
                element.select();
                document.execCommand('copy');
                alert('Password copiata!');
            }
        }
    }
};

// Inizializza quando il DOM è pronto
document.addEventListener('DOMContentLoaded', () => {
    window.userMgmt = new UserManagementEnhanced();
});