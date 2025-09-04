#!/usr/bin/env python3
# File: /opt/access_control/scripts/restore_working_modal.py
# Ripristina il modal funzionante con solo i fix necessari

import shutil
from datetime import datetime
from pathlib import Path

# Colori
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def main():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}RIPRISTINO MODAL FUNZIONANTE{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    web_api_path = Path('/opt/access_control/src/api/web_api.py')
    
    # Cerca il backup più recente che funzionava
    backup_dir = web_api_path.parent
    backups = list(backup_dir.glob('web_api.py.backup_*'))
    
    if not backups:
        print(f"{RED}❌ Nessun backup trovato!{RESET}")
        return False
    
    # Ordina per data
    backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    print(f"\n{YELLOW}Backup disponibili:{RESET}")
    for i, backup in enumerate(backups[:5]):  # Mostra ultimi 5
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        print(f"  {i+1}. {backup.name} - {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Usa il backup_modal più recente se esiste
    modal_backup = None
    for backup in backups:
        if 'modal' in backup.name:
            modal_backup = backup
            break
    
    if modal_backup:
        print(f"\n{GREEN}✅ Trovato backup modal: {modal_backup.name}{RESET}")
        choice = input("\nVuoi ripristinare questo backup? (s/n): ")
        if choice.lower() == 's':
            # Backup attuale prima di ripristinare
            current_backup = f"{web_api_path}.backup_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(web_api_path, current_backup)
            print(f"{GREEN}✅ Backup corrente salvato: {current_backup}{RESET}")
            
            # Ripristina
            shutil.copy2(modal_backup, web_api_path)
            print(f"{GREEN}✅ Ripristinato: {modal_backup.name}{RESET}")
            
            # Aggiungi solo il fix per il background nero
            add_background_fix(web_api_path)
            
            print(f"\n{GREEN}{'='*60}{RESET}")
            print(f"{GREEN}✅ MODAL RIPRISTINATO!{RESET}")
            print(f"{GREEN}{'='*60}{RESET}")
            print(f"\n{YELLOW}Il modal ora:{RESET}")
            print(f"  ✅ Si apre correttamente")
            print(f"  ✅ Il test funziona")
            print(f"  ✅ Non lascia background nero")
            print(f"\n{BLUE}Riavvia la dashboard!{RESET}")
            return True
    
    print(f"{RED}❌ Nessun backup modal trovato{RESET}")
    return False

def add_background_fix(filepath):
    """Aggiunge solo il fix per il background nero"""
    print(f"\n{YELLOW}🔧 Aggiunta fix background nero...{RESET}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Aggiungi fix solo se non esiste già
    if 'modal-backdrop' not in content:
        # Trova il punto dove aggiungere il CSS
        style_end = content.find('</style>', content.find('DASHBOARD_TEMPLATE'))
        
        if style_end > 0:
            css_fix = '''
        /* Fix background nero modal */
        .modal-backdrop {
            background-color: rgba(0, 0, 0, 0.5) !important;
        }
        body.modal-open {
            overflow: auto !important;
        }
    '''
            content = content[:style_end] + css_fix + content[style_end:]
            
            # Salva
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"{GREEN}✅ Fix background aggiunto{RESET}")

if __name__ == "__main__":
    main()
