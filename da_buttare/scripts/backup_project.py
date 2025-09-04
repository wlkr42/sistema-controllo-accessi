#!/usr/bin/env python3
# File: /opt/access_control/scripts/backup_project.py
# Script per backup completo del progetto Sistema Controllo Accessi

import os
import shutil
import tarfile
import hashlib
from datetime import datetime
from pathlib import Path

# Configurazione
PROJECT_ROOT = Path("/opt/access_control")
BACKUP_BASE_DIR = PROJECT_ROOT / "backups"
BACKUP_NAME = f"backup_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Colori per output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_status(message, status="INFO"):
    """Stampa messaggi colorati"""
    if status == "OK":
        print(f"{Colors.GREEN}✓{Colors.ENDC} {message}")
    elif status == "ERROR":
        print(f"{Colors.RED}✗{Colors.ENDC} {message}")
    elif status == "WARNING":
        print(f"{Colors.YELLOW}⚠{Colors.ENDC} {message}")
    else:
        print(f"{Colors.BLUE}ℹ{Colors.ENDC} {message}")

def calculate_checksum(file_path):
    """Calcola MD5 checksum di un file"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_directory_size(path):
    """Calcola dimensione totale di una directory"""
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total += os.path.getsize(fp)
    return total

def format_size(bytes):
    """Formatta dimensione in formato leggibile"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

def create_backup():
    """Crea backup completo del progetto"""
    print(f"\n{Colors.BOLD}=== BACKUP SISTEMA CONTROLLO ACCESSI ==={Colors.ENDC}")
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    
    # Crea directory backup se non esiste
    BACKUP_BASE_DIR.mkdir(exist_ok=True)
    backup_dir = BACKUP_BASE_DIR / BACKUP_NAME
    backup_dir.mkdir(exist_ok=True)
    
    print_status(f"Directory backup: {backup_dir}")
    
    # Lista componenti da backuppare
    components = {
        "src": "Codice sorgente Python",
        "config": "File di configurazione",
        "scripts": "Script di utilità",
        "docs": "Documentazione",
        "requirements.txt": "Dipendenze Python",
        "requirements_dashboard.txt": "Dipendenze Dashboard",
    }
    
    # Backup componenti
    print_status("\nBackup componenti:", "INFO")
    backed_up_files = []
    
    for component, description in components.items():
        source = PROJECT_ROOT / component
        if source.exists():
            dest = backup_dir / component
            try:
                if source.is_file():
                    shutil.copy2(source, dest)
                    size = os.path.getsize(source)
                else:
                    shutil.copytree(source, dest, ignore=shutil.ignore_patterns(
                        '*.pyc', '__pycache__', '*.log', '.git', 'venv', '*.tmp'
                    ))
                    size = get_directory_size(dest)
                
                print_status(f"{description} ({format_size(size)})", "OK")
                backed_up_files.append(component)
            except Exception as e:
                print_status(f"{description}: {str(e)}", "ERROR")
        else:
            print_status(f"{description}: non trovato", "WARNING")
    
    # Backup database (con attenzione alla dimensione)
    print_status("\nBackup database:", "INFO")
    db_path = PROJECT_ROOT / "src" / "access.db"
    if db_path.exists():
        db_size = os.path.getsize(db_path)
        print_status(f"Dimensione database: {format_size(db_size)}", "INFO")
        
        if db_size < 500 * 1024 * 1024:  # Max 500MB
            try:
                shutil.copy2(db_path, backup_dir / "access.db")
                print_status("Database backuppato", "OK")
                backed_up_files.append("access.db")
            except Exception as e:
                print_status(f"Errore backup database: {str(e)}", "ERROR")
        else:
            print_status("Database troppo grande, creazione link simbolico", "WARNING")
            # Crea solo riferimento al database
            with open(backup_dir / "database_info.txt", 'w') as f:
                f.write(f"Database originale: {db_path}\n")
                f.write(f"Dimensione: {format_size(db_size)}\n")
                f.write(f"Data backup: {datetime.now()}\n")
    
    # Crea snapshot del sistema
    print_status("\nCreazione snapshot sistema:", "INFO")
    snapshot_file = backup_dir / "SYSTEM_SNAPSHOT.txt"
    with open(snapshot_file, 'w') as f:
        f.write("=== SNAPSHOT SISTEMA CONTROLLO ACCESSI ===\n")
        f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Host: {os.uname().nodename}\n")
        f.write(f"Sistema: {os.uname().sysname} {os.uname().release}\n")
        f.write(f"Python: {os.sys.version.split()[0]}\n")
        f.write(f"\n=== COMPONENTI BACKUPPATI ===\n")
        for component in backed_up_files:
            f.write(f"- {component}\n")
        
        # Aggiungi info processi
        f.write(f"\n=== PROCESSI ATTIVI ===\n")
        try:
            import subprocess
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'python' in line and 'access_control' in line:
                    f.write(f"{line}\n")
        except:
            f.write("Impossibile ottenere lista processi\n")
        
        # Aggiungi stato servizi
        f.write(f"\n=== STATO SERVIZI ===\n")
        try:
            result = subprocess.run(['systemctl', 'is-active', 'access-control'], 
                                  capture_output=True, text=True)
            f.write(f"Servizio access-control: {result.stdout.strip()}\n")
        except:
            f.write("Servizio systemd non configurato\n")
    
    print_status("Snapshot sistema creato", "OK")
    
    # Crea archivio compresso
    print_status("\nCreazione archivio compresso:", "INFO")
    archive_name = f"{BACKUP_NAME}.tar.gz"
    archive_path = BACKUP_BASE_DIR / archive_name
    
    try:
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(backup_dir, arcname=BACKUP_NAME)
        
        archive_size = os.path.getsize(archive_path)
        print_status(f"Archivio creato: {archive_name} ({format_size(archive_size)})", "OK")
        
        # Calcola checksum
        checksum = calculate_checksum(archive_path)
        print_status(f"MD5 Checksum: {checksum}", "INFO")
        
        # Salva checksum
        with open(archive_path.with_suffix('.tar.gz.md5'), 'w') as f:
            f.write(f"{checksum}  {archive_name}\n")
        
        # Rimuovi directory temporanea
        shutil.rmtree(backup_dir)
        print_status("Directory temporanea rimossa", "OK")
        
    except Exception as e:
        print_status(f"Errore creazione archivio: {str(e)}", "ERROR")
        return False
    
    # Gestione backup vecchi
    print_status("\nGestione backup precedenti:", "INFO")
    backups = sorted([f for f in BACKUP_BASE_DIR.glob("backup_completo_*.tar.gz")])
    
    if len(backups) > 5:  # Mantieni solo ultimi 5 backup
        for old_backup in backups[:-5]:
            try:
                old_backup.unlink()
                # Rimuovi anche checksum
                old_backup.with_suffix('.tar.gz.md5').unlink(missing_ok=True)
                print_status(f"Rimosso backup vecchio: {old_backup.name}", "WARNING")
            except:
                pass
    
    print_status(f"Backup totali mantenuti: {min(len(backups), 5)}", "INFO")
    
    # Report finale
    print(f"\n{Colors.BOLD}=== BACKUP COMPLETATO ==={Colors.ENDC}")
    print_status(f"File: {archive_path}", "OK")
    print_status(f"Dimensione: {format_size(archive_size)}", "OK")
    print_status(f"Checksum: {checksum}", "OK")
    
    # Crea script di ripristino
    create_restore_script(archive_name, checksum)
    
    return True

def create_restore_script(archive_name, checksum):
    """Crea script per ripristino backup"""
    restore_script = BACKUP_BASE_DIR / f"restore_{archive_name}.sh"
    
    script_content = f"""#!/bin/bash
# Script ripristino backup {archive_name}
# Generato: {datetime.now()}

BACKUP_FILE="{archive_name}"
EXPECTED_MD5="{checksum}"
PROJECT_ROOT="/opt/access_control"

echo "=== RIPRISTINO BACKUP SISTEMA CONTROLLO ACCESSI ==="
echo "Backup: $BACKUP_FILE"
echo ""

# Verifica checksum
echo "Verifica integrità backup..."
ACTUAL_MD5=$(md5sum "$BACKUP_FILE" | cut -d' ' -f1)
if [ "$ACTUAL_MD5" != "$EXPECTED_MD5" ]; then
    echo "ERRORE: Checksum non corrispondente!"
    echo "Atteso: $EXPECTED_MD5"
    echo "Trovato: $ACTUAL_MD5"
    exit 1
fi
echo "✓ Checksum verificato"

# Conferma
read -p "Vuoi procedere con il ripristino? (s/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Ripristino annullato"
    exit 0
fi

# Stop servizi
echo "Arresto servizi..."
sudo systemctl stop access-control 2>/dev/null

# Backup attuale
echo "Backup configurazione attuale..."
sudo mv $PROJECT_ROOT $PROJECT_ROOT.old.$(date +%Y%m%d_%H%M%S)

# Estrazione
echo "Estrazione backup..."
sudo tar -xzf "$BACKUP_FILE" -C /opt/

# Ripristino permessi
echo "Ripristino permessi..."
sudo chown -R root:root $PROJECT_ROOT
sudo chmod +x $PROJECT_ROOT/scripts/*.py

# Restart servizi
echo "Riavvio servizi..."
sudo systemctl start access-control 2>/dev/null

echo ""
echo "✓ RIPRISTINO COMPLETATO"
echo "Backup precedente salvato con suffisso .old"
"""
    
    with open(restore_script, 'w') as f:
        f.write(script_content)
    
    os.chmod(restore_script, 0o755)
    print_status(f"Script ripristino creato: {restore_script.name}", "OK")

if __name__ == "__main__":
    try:
        create_backup()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Backup interrotto dall'utente{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.RED}Errore critico: {str(e)}{Colors.ENDC}")
