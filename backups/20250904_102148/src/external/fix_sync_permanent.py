#!/usr/bin/env python3
"""
Fix permanente per il problema di sincronizzazione degli utenti da Odoo
"""
import os
import sys
import re
from pathlib import Path
import logging
import shutil
from datetime import datetime

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Percorso file
ODOO_CONNECTOR_PATH = "/opt/access_control/src/external/odoo_partner_connector.py"
BACKUP_DIR = "/opt/access_control/da_buttare"

def main():
    """Funzione principale"""
    print(f"🔧 Fix permanente problema sincronizzazione utenti da Odoo")
    
    # 1. Backup del file originale
    print("\n1️⃣ BACKUP FILE ORIGINALE")
    backup_path = create_backup(ODOO_CONNECTOR_PATH)
    
    if not backup_path:
        print("❌ Impossibile creare backup, operazione annullata")
        return
    
    print(f"✅ Backup creato: {backup_path}")
    
    # 2. Modifica del file
    print("\n2️⃣ MODIFICA FILE")
    success = modify_sync_to_database()
    
    if not success:
        print("❌ Modifica fallita, ripristino backup...")
        restore_backup(backup_path, ODOO_CONNECTOR_PATH)
        return
    
    print("✅ File modificato con successo")
    
    # 3. Verifica modifiche
    print("\n3️⃣ VERIFICA MODIFICHE")
    verify_success = verify_changes()
    
    if not verify_success:
        print("❌ Verifica fallita, ripristino backup...")
        restore_backup(backup_path, ODOO_CONNECTOR_PATH)
        return
    
    print("✅ Modifiche verificate con successo")
    
    # 4. Conclusione
    print("\n🔍 CONCLUSIONE:")
    print("✅ Fix permanente applicato con successo")
    print("   Il metodo sync_to_database ora verifica direttamente l'esistenza dell'utente")
    print("   senza passare per le verifiche aggiuntive di orario e limite mensile")
    print("\n📝 CHANGELOG:")
    print("   - Modificato metodo sync_to_database in odoo_partner_connector.py")
    print("   - Aggiunto controllo diretto esistenza utente nel database")
    print("   - Backup originale salvato in: " + backup_path)

def create_backup(file_path):
    """Crea backup del file originale"""
    try:
        # Crea directory backup se non esiste
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # Nome file backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        backup_name = f"{filename}.backup_{timestamp}"
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        
        # Copia file
        shutil.copy2(file_path, backup_path)
        
        return backup_path
    except Exception as e:
        print(f"❌ Errore creazione backup: {e}")
        return None

def restore_backup(backup_path, original_path):
    """Ripristina backup in caso di errore"""
    try:
        shutil.copy2(backup_path, original_path)
        print(f"✅ Backup ripristinato: {original_path}")
        return True
    except Exception as e:
        print(f"❌ Errore ripristino backup: {e}")
        return False

def modify_sync_to_database():
    """Modifica il metodo sync_to_database"""
    try:
        # Leggi il file
        with open(ODOO_CONNECTOR_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern per trovare il blocco di codice da modificare
        pattern = r'(def sync_to_database.*?exists, existing_user = database_manager\.verify_access\(cf\))(.*?)(if exists:.*?# Già presente - skip.*?stats\[\'skipped\'\] \+= 1)(.*?)(else:.*?# Aggiungi nuovo cittadino)'
        
        # Sostituzione
        new_content = re.sub(
            pattern,
            r'\1\2# Verifica esistenza DIRETTA senza passare per verify_access\n            cursor = database_manager.conn.cursor()\n            cursor.execute("SELECT id FROM utenti_autorizzati WHERE codice_fiscale = ?", (cf.upper(),))\n            exists = cursor.fetchone() is not None\n            \n            \3\4\5',
            content,
            flags=re.DOTALL
        )
        
        # Verifica se la sostituzione è avvenuta
        if content == new_content:
            print("⚠️ Nessuna modifica effettuata, pattern non trovato")
            return False
        
        # Scrivi il file modificato
        with open(ODOO_CONNECTOR_PATH, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    except Exception as e:
        print(f"❌ Errore modifica file: {e}")
        return False

def verify_changes():
    """Verifica che le modifiche siano state applicate correttamente"""
    try:
        # Leggi il file modificato
        with open(ODOO_CONNECTOR_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica presenza modifiche
        if "# Verifica esistenza DIRETTA senza passare per verify_access" in content and \
           "cursor.execute(\"SELECT id FROM utenti_autorizzati WHERE codice_fiscale = ?\"" in content:
            return True
        else:
            print("⚠️ Modifiche non trovate nel file")
            return False
    except Exception as e:
        print(f"❌ Errore verifica modifiche: {e}")
        return False

if __name__ == "__main__":
    main()
