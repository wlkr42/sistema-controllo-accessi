#!/usr/bin/env python3
# File: /opt/access_control/scripts/integrate_profilo.py
# Script per integrare il modulo profilo nel sistema esistente

import os
import sys
import shutil
from datetime import datetime

# Aggiungi path per import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def create_backup():
    """Crea backup del file web_api.py"""
    src_file = "/opt/access_control/src/api/web_api.py"
    backup_file = f"/opt/access_control/src/api/web_api_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    if os.path.exists(src_file):
        shutil.copy2(src_file, backup_file)
        print(f"✅ Backup creato: {backup_file}")
        return True
    else:
        print("❌ File web_api.py non trovato!")
        return False

def add_import_statements():
    """Aggiunge gli import necessari in web_api.py"""
    web_api_file = "/opt/access_control/src/api/web_api.py"
    
    # Leggi il file
    with open(web_api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Trova la posizione dopo gli import esistenti
    import_section_end = content.find("# Setup logging")
    
    if import_section_end == -1:
        print("❌ Non trovata sezione import nel file")
        return False
    
    # Aggiungi import del modulo profilo se non presente
    if "from modules.profilo import init_profilo_module" not in content:
        new_import = "\n# Import modulo profilo\nfrom modules.profilo import init_profilo_module\n"
        content = content[:import_section_end] + new_import + content[import_section_end:]
        
        with open(web_api_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Import statements aggiunti")
    else:
        print("ℹ️ Import già presente")
    
    return True

def add_profilo_initialization():
    """Aggiunge l'inizializzazione del modulo profilo"""
    web_api_file = "/opt/access_control/src/api/web_api.py"
    
    with open(web_api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Trova dove aggiungere l'inizializzazione (dopo config_manager init)
    init_point = content.find("config_manager = ConfigManager()")
    
    if init_point == -1:
        print("❌ Non trovato punto di inizializzazione")
        return False
    
    # Trova la fine della riga
    line_end = content.find('\n', init_point)
    
    # Aggiungi inizializzazione del modulo profilo
    if "init_profilo_module" not in content:
        init_code = """
# Inizializza modulo profilo
profilo_bp = init_profilo_module(config_manager)
app.register_blueprint(profilo_bp)
"""
        content = content[:line_end+1] + init_code + content[line_end+1:]
        
        with open(web_api_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Inizializzazione modulo profilo aggiunta")
    else:
        print("ℹ️ Inizializzazione già presente")
    
    return True

def add_menu_link():
    """Aggiunge il link al profilo nel menu di navigazione"""
    web_api_file = "/opt/access_control/src/api/web_api.py"
    
    with open(web_api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Trova il menu di navigazione nel BASE_TEMPLATE
    menu_marker = '<div class="user-info">'
    menu_pos = content.find(menu_marker)
    
    if menu_pos == -1:
        print("❌ Non trovato menu di navigazione")
        return False
    
    # Trova dove inserire il link (prima del logout)
    logout_pos = content.find('<a href="/logout"', menu_pos)
    
    if logout_pos == -1:
        print("❌ Non trovato link logout")
        return False
    
    # Aggiungi link profilo se non presente
    if 'href="/profilo"' not in content[menu_pos:logout_pos]:
        profile_link = '            <a href="/profilo"><i class="fas fa-user-cog"></i> Profilo</a>\n            '
        content = content[:logout_pos] + profile_link + content[logout_pos:]
        
        with open(web_api_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Link profilo aggiunto al menu")
    else:
        print("ℹ️ Link profilo già presente")
    
    return True

def update_dashboard_cards():
    """Aggiunge un quick link al profilo nella dashboard"""
    web_api_file = "/opt/access_control/src/api/web_api.py"
    
    with open(web_api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Trova la sezione quick links nella dashboard
    quick_links_marker = "<!-- Quick Links -->"
    quick_links_pos = content.find(quick_links_marker)
    
    if quick_links_pos == -1:
        print("⚠️ Sezione Quick Links non trovata, skip...")
        return True
    
    # Trova dove inserire il nuovo link (dopo l'ultimo link esistente)
    grid_end = content.find('</div>', content.find('<div class="grid grid-3">', quick_links_pos))
    
    if 'href="/profilo"' not in content[quick_links_pos:grid_end]:
        profile_card = """
            <a href="/profilo" class="quick-link">
                <i class="fas fa-user-cog"></i>
                <span>Il Mio Profilo</span>
            </a>"""
        
        # Inserisci prima della chiusura del grid
        content = content[:grid_end] + profile_card + '\n            ' + content[grid_end:]
        
        with open(web_api_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Quick link profilo aggiunto alla dashboard")
    else:
        print("ℹ️ Quick link già presente")
    
    return True

def main():
    """Esegue l'integrazione completa"""
    print("�� Integrazione Modulo Profilo Utente")
    print("=" * 50)
    
    # Verifica che esista la directory modules
    modules_dir = "/opt/access_control/src/api/modules"
    if not os.path.exists(modules_dir):
        os.makedirs(modules_dir)
        print(f"✅ Creata directory: {modules_dir}")
        
        # Crea __init__.py
        init_file = os.path.join(modules_dir, "__init__.py")
        with open(init_file, 'w') as f:
            f.write("# Moduli API\n")
        print("✅ Creato __init__.py")
    
    # Copia il modulo profilo
    profilo_src = "/tmp/profilo.py"  # Assumendo che sia stato creato qui
    profilo_dst = os.path.join(modules_dir, "profilo.py")
    
    if os.path.exists(profilo_src):
        shutil.copy2(profilo_src, profilo_dst)
        print(f"✅ Modulo profilo copiato in: {profilo_dst}")
    else:
        print("⚠️ File profilo.py non trovato in /tmp, assicurati di averlo creato")
    
    # Crea backup
    if not create_backup():
        print("❌ Impossibile creare backup, operazione annullata")
        return
    
    # Esegui le modifiche
    steps = [
        ("Aggiunta import statements", add_import_statements),
        ("Aggiunta inizializzazione modulo", add_profilo_initialization),
        ("Aggiunta link menu", add_menu_link),
        ("Aggiunta quick link dashboard", update_dashboard_cards)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📝 {step_name}...")
        if not step_func():
            print(f"❌ Errore durante: {step_name}")
            print("⚠️ Controlla il backup e correggi manualmente")
            return
    
    print("\n" + "=" * 50)
    print("✅ Integrazione completata con successo!")
    print("\n📋 Prossimi passi:")
    print("1. Salva il modulo profilo.py in: /opt/access_control/src/api/modules/profilo.py")
    print("2. Riavvia il servizio web: supervisorctl restart dashboard")
    print("3. Accedi a: http://192.168.178.200:5000/profilo")
    print("\n💡 Funzionalità disponibili:")
    print("- Visualizzazione informazioni profilo utente")
    print("- Cambio password personale con validazione")
    print("- Indicatore forza password in tempo reale")
    print("- Controlli di sicurezza lato server")

if __name__ == "__main__":
    main()
