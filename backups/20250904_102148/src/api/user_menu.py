# File: /opt/access_control/src/api/user_menu.py
# Endpoint per menu utente

from flask import render_template_string, session
from web_api import app, require_auth

@app.route('/api/user-menu-html')
@require_auth()
def get_user_menu_html():
    """Restituisce HTML del menu utente con dati sessione"""
    
    # Mappa ruoli
    role_names = {
        'admin': 'Amministratore',
        'user_manager': 'Gestore Utenti',
        'viewer': 'Visualizzatore'
    }

    # Aggiungi badge colorati per ruolo nel menu
    role_badges = {
        'admin': 'bg-danger',
        'user_manager': 'bg-primary', 
        'viewer': 'bg-success'
    }
    
    user_role = session.get('role', 'readonly')
    user_role_name = role_names.get(user_role, 'Utente')
    
    # Template del menu
    menu_template = """
    <div class="user-menu-container">
        <!-- Trigger Menu -->
        <div class="user-menu-trigger">
            <div class="user-avatar">
                {{ session.username[0].upper() }}
            </div>
            <div class="user-menu-info">
                <div class="user-menu-name">{{ session.username }}</div>
                <div class="user-menu-role">{{ user_role_name }}</div>
            </div>
            <i class="fas fa-chevron-down" style="color: white; font-size: 0.8rem;"></i>
        </div>
        
        <!-- Dropdown Menu -->
        <div class="user-menu-dropdown">
            <div class="user-menu-header">
                <div class="avatar-large">
                    {{ session.username[0].upper() }}
                </div>
                <div class="user-name">{{ session.username }}</div>
                <div class="user-email">{{ user_role_name }}</div>
            </div>
            
            <div class="user-menu-items">
                <a href="#" class="user-menu-item" data-action="profile">
                    <i class="fas fa-user-circle"></i>
                    <span class="user-menu-item-text">Il Mio Profilo</span>
                </a>
                
                <a href="#" class="user-menu-item" data-action="change-password">
                    <i class="fas fa-key"></i>
                    <span class="user-menu-item-text">Cambio Password</span>
                </a>
                
                <a href="#" class="user-menu-item" data-action="settings">
                    <i class="fas fa-cog"></i>
                    <span class="user-menu-item-text">Impostazioni</span>
                    {% if session.role == 'admin' %}
                    <span class="notification-badge">New</span>
                    {% endif %}
                </a>
                
                <div class="user-menu-divider"></div>
                
                <a href="/logout" class="user-menu-item logout">
                    <i class="fas fa-sign-out-alt"></i>
                    <span class="user-menu-item-text">Logout</span>
                </a>
            </div>
        </div>
    </div>
    
    <!-- Overlay -->
    <div class="user-menu-overlay"></div>
    """
    
    return render_template_string(menu_template, 
                                session=session,
                                user_role_name=user_role_name)
