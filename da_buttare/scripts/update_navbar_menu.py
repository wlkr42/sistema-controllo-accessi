# File: /opt/access_control/scripts/update_navbar_menu.py
# Aggiorna solo la navbar della dashboard con menu utente moderno

import os
import re
import shutil
from datetime import datetime

def update_dashboard_navbar():
    """Aggiorna solo la navbar nel template dashboard"""
    
    dashboard_templates = "/opt/access_control/src/api/dashboard_templates.py"
    
    # Backup
    backup_name = f"{dashboard_templates}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(dashboard_templates, backup_name)
    print(f"✅ Backup creato: {backup_name}")
    
    # Leggi il file
    with open(dashboard_templates, 'r') as f:
        content = f.read()
    
    # Trova la sezione navbar esistente
    navbar_pattern = r'<nav class="navbar navbar-dark">.*?</nav>'
    
    # Nuova navbar con menu utente
    new_navbar = '''<nav class="navbar navbar-dark">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-shield-alt me-2"></i>Sistema Controllo Accessi
            </span>
            <div class="navbar-nav d-flex flex-row align-items-center">
                <span class="navbar-text me-4 text-white d-none d-md-block">Isola Ecologica RAEE - Rende</span>
                
                <!-- Menu Utente -->
                <div class="user-menu position-relative">
                    <div class="d-flex align-items-center gap-2">
                        <div class="user-info text-end text-white d-none d-sm-block">
                            <div class="user-name fw-semibold small">{{ username }}</div>
                            <div class="user-role opacity-75" style="font-size: 0.75rem;">
                                <i class="fas {{ role_icon }}"></i> {{ role_label }}
                            </div>
                        </div>
                        <div class="user-avatar">
                            {{ user_initial }}
                        </div>
                    </div>
                    
                    <!-- Dropdown Menu -->
                    <div class="user-dropdown position-absolute">
                        <a href="#" class="dropdown-item" onclick="showProfileModal(); return false;">
                            <i class="fas fa-user-circle"></i>
                            <span>Il Mio Profilo</span>
                        </a>
                        <a href="#" class="dropdown-item" onclick="showChangePasswordModal(); return false;">
                            <i class="fas fa-key"></i>
                            <span>Cambio Password</span>
                        </a>
                        <a href="#" class="dropdown-item" onclick="showSettingsModal(); return false;">
                            <i class="fas fa-cog"></i>
                            <span>Impostazioni</span>
                        </a>
                        <div class="dropdown-divider"></div>
                        <a href="#" class="dropdown-item" onclick="showHelpModal(); return false;">
                            <i class="fas fa-question-circle"></i>
                            <span>Aiuto</span>
                        </a>
                        <a href="/logout" class="dropdown-item">
                            <i class="fas fa-sign-out-alt"></i>
                            <span>Logout</span>
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </nav>'''
    
    # Sostituisci navbar
    content = re.sub(navbar_pattern, new_navbar, content, flags=re.DOTALL)
    
    # Aggiungi stili CSS necessari dopo gli stili esistenti
    styles_to_add = '''
        /* Menu utente */
        .user-menu { position: relative; cursor: pointer; padding: 0.5rem; border-radius: 0.5rem; transition: all 0.3s; }
        .user-menu:hover { background: rgba(255,255,255,0.1); }
        .user-avatar { width: 38px; height: 38px; border-radius: 50%; background: white; color: #667eea; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.1rem; }
        .user-dropdown { top: 100%; right: 0; margin-top: 0.5rem; min-width: 200px; background: white; border-radius: 0.5rem; box-shadow: 0 10px 25px rgba(0,0,0,0.2); opacity: 0; visibility: hidden; transform: translateY(-10px); transition: all 0.3s; z-index: 1000; }
        .user-dropdown.show { opacity: 1; visibility: visible; transform: translateY(0); }
        .dropdown-item { padding: 0.75rem 1rem; color: #333; text-decoration: none; display: flex; align-items: center; gap: 0.75rem; transition: all 0.2s; }
        .dropdown-item:hover { background: #f8f9fa; color: #667eea; }
        .dropdown-divider { height: 1px; background: #e9ecef; margin: 0.5rem 0; }'''
    
    # Trova dove inserire gli stili
    style_end = content.find('</style>')
    if style_end != -1:
        content = content[:style_end] + styles_to_add + '\n    ' + content[style_end:]
    
    # Aggiungi JS per gestione dropdown dopo il body
    js_code = '''
    <script>
        // Gestione menu utente
        document.addEventListener('DOMContentLoaded', function() {
            const userMenu = document.querySelector('.user-menu');
            const userDropdown = document.querySelector('.user-dropdown');
            
            if (userMenu && userDropdown) {
                userMenu.addEventListener('click', function(e) {
                    e.stopPropagation();
                    userDropdown.classList.toggle('show');
                });
                
                document.addEventListener('click', function() {
                    userDropdown.classList.remove('show');
                });
                
                userDropdown.addEventListener('click', function(e) {
                    e.stopPropagation();
                });
            }
        });
        
        // Placeholder per le modal (verranno implementate dopo)
        function showProfileModal() { alert('Profilo utente - In sviluppo'); }
        function showChangePasswordModal() { alert('Cambio password - In sviluppo'); }
        function showSettingsModal() { alert('Impostazioni - In sviluppo'); }
        function showHelpModal() { alert('Aiuto - In sviluppo'); }
    </script>'''
    
    # Trova dove inserire il JS (prima di </body>)
    body_end = content.find('</body>')
    if body_end != -1:
        content = content[:body_end] + js_code + '\n' + content[body_end:]
    
    # Aggiorna la funzione get_dashboard_template per passare i dati utente
    def_pattern = r'def get_dashboard_template\(\):'
    def_replacement = '''def get_dashboard_template():
    """Template dashboard con menu utente moderno"""
    from flask import session
    
    username = session.get('username', 'utente')
    role = session.get('role', 'readonly')
    
    # Mappa ruoli
    role_info = {
        'admin': {'icon': 'fa-crown', 'color': '#FFD700', 'label': 'Amministratore'},
        'gestore': {'icon': 'fa-user-tie', 'color': '#20c997', 'label': 'Gestore'},
        'readonly': {'icon': 'fa-user', 'color': '#6c757d', 'label': 'Osservatore'}
    }
    
    current_role = role_info.get(role, role_info['readonly'])
    
    # Sostituisci placeholder nel template
    template = DASHBOARD_TEMPLATE
    template = template.replace('{{ username }}', username)
    template = template.replace('{{ role_icon }}', current_role['icon'])
    template = template.replace('{{ role_label }}', current_role['label'])
    template = template.replace('{{ user_initial }}', username[0].upper())
    
    return template'''
    
    content = re.sub(def_pattern, def_replacement, content)
    
    # Scrivi il file aggiornato
    with open(dashboard_templates, 'w') as f:
        f.write(content)
    
    print("✅ Navbar aggiornata con menu utente moderno")
    print("✅ Mantenuta struttura modulare esistente")
    print("✅ Aggiunti stili e JavaScript necessari")

if __name__ == "__main__":
    update_dashboard_navbar()
    print("\n✅ Aggiornamento completato!")
    print("🔄 Riavvia la dashboard per vedere le modifiche")
