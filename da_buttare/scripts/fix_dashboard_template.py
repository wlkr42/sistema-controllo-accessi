# File: /opt/access_control/scripts/fix_dashboard_template.py
# Fix immediato per l'errore DASHBOARD_TEMPLATE

import os

def fix_dashboard_template():
    """Fix errore DASHBOARD_TEMPLATE not defined"""
    
    file_path = "/opt/access_control/src/api/dashboard_templates.py"
    
    # Leggi il file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Trova la funzione get_dashboard_template e sistemala
    # Sostituisci la funzione rotta con una versione corretta
    fix = '''def get_dashboard_template():
    """Template dashboard"""
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
    user_initial = username[0].upper()
    
    # Ritorna direttamente il template con le sostituzioni
    return DASHBOARD_TEMPLATE.replace('{{ username }}', username).replace('{{ role_icon }}', current_role['icon']).replace('{{ role_label }}', current_role['label']).replace('{{ user_initial }}', user_initial)'''
    
    # Trova dove inizia la funzione
    start = content.find('def get_dashboard_template():')
    if start == -1:
        print("❌ Funzione get_dashboard_template() non trovata!")
        return False
    
    # Trova dove finisce (cerca la prossima 'def ' o la fine del file)
    end = content.find('\ndef ', start + 1)
    if end == -1:
        end = len(content)
    
    # Sostituisci
    content = content[:start] + fix + content[end:]
    
    # Scrivi
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fix applicato!")
    return True

if __name__ == "__main__":
    if fix_dashboard_template():
        print("🔄 Riavvia la dashboard ora")
