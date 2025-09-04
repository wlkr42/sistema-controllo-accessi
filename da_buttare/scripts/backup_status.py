#!/usr/bin/env python3
# File: /opt/access_control/scripts/backup_status.py
# Verifica stato backup Sistema Controllo Accessi

import os
from pathlib import Path
from datetime import datetime, timedelta

# Configurazione
PROJECT_ROOT = Path("/opt/access_control")
BACKUP_DIR = PROJECT_ROOT / "backups"

# Colori
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def format_size(bytes):
    """Formatta dimensione in formato leggibile"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} PB"

def format_timedelta(td):
    """Formatta timedelta in formato leggibile"""
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"{days} giorni fa"
    elif hours > 0:
        return f"{hours} ore fa"
    elif minutes > 0:
        return f"{minutes} minuti fa"
    else:
        return "pochi secondi fa"

def get_file_age(file_path):
    """Calcola età del file"""
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    age = datetime.now() - mtime
    return format_timedelta(age)

def check_backup_status():
    """Verifica stato dei backup"""
    print(f"\n{Colors.BOLD}=== STATO BACKUP SISTEMA CONTROLLO ACCESSI ==={Colors.ENDC}")
    print(f"Data verifica: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    
    if not BACKUP_DIR.exists():
        print(f"{Colors.RED}✗ Directory backup non trovata!{Colors.ENDC}")
        print(f"  Creare con: mkdir -p {BACKUP_DIR}")
        return
    
    # 1. Backup completi
    print(f"{Colors.BLUE}BACKUP COMPLETI:{Colors.ENDC}")
    complete_backups = sorted(BACKUP_DIR.glob("backup_completo_*.tar.gz"))
    
    if complete_backups:
        for backup in complete_backups[-5:]:  # Ultimi 5
            size = format_size(backup.stat().st_size)
            age = get_file_age(backup)
            
            # Verifica checksum se esiste
            checksum_file = backup.with_suffix('.tar.gz.md5')
            checksum_status = "✓" if checksum_file.exists() else "✗"
            
            print(f"  • {backup.name}")
            print(f"    Dimensione: {size} | Età: {age} | MD5: {checksum_status}")
    else:
        print(f"  {Colors.YELLOW}Nessun backup completo trovato{Colors.ENDC}")
    
    # 2. Backup rapidi
    print(f"\n{Colors.BLUE}BACKUP RAPIDI RECENTI:{Colors.ENDC}")
    
    # Database
    db_backups = sorted(BACKUP_DIR.glob("access_*.db"))
    if db_backups:
        latest_db = db_backups[-1]
        print(f"  • Ultimo database: {latest_db.name}")
        print(f"    Dimensione: {format_size(latest_db.stat().st_size)} | Età: {get_file_age(latest_db)}")
    
    # Config
    config_backups = sorted(BACKUP_DIR.glob("config_*.tar.gz"))
    if config_backups:
        latest_config = config_backups[-1]
        print(f"  • Ultima config: {latest_config.name}")
        print(f"    Dimensione: {format_size(latest_config.stat().st_size)} | Età: {get_file_age(latest_config)}")
    
    # 3. Spazio utilizzato
    print(f"\n{Colors.BLUE}UTILIZZO SPAZIO:{Colors.ENDC}")
    total_size = sum(f.stat().st_size for f in BACKUP_DIR.rglob("*") if f.is_file())
    file_count = len(list(BACKUP_DIR.rglob('*')))
    print(f"  Spazio totale backup: {format_size(total_size)}")
    print(f"  Numero file: {file_count}")
    
    # 4. Verifica ultimo backup
    print(f"\n{Colors.BLUE}VERIFICA BACKUP:{Colors.ENDC}")
    
    # Controlla ultimo backup completo
    if complete_backups:
        latest_complete = complete_backups[-1]
        age_days = (datetime.now() - datetime.fromtimestamp(latest_complete.stat().st_mtime)).days
        
        if age_days > 7:
            print(f"  {Colors.YELLOW}⚠ Ultimo backup completo: {age_days} giorni fa{Colors.ENDC}")
            print(f"    Consigliato: eseguire backup completo")
        else:
            print(f"  {Colors.GREEN}✓ Backup completo recente ({age_days} giorni fa){Colors.ENDC}")
    else:
        print(f"  {Colors.RED}✗ Nessun backup completo!{Colors.ENDC}")
        print(f"    Eseguire: python3 {PROJECT_ROOT}/scripts/backup_project.py")
    
    # Controlla backup database oggi
    today = datetime.now().strftime("%Y%m%d")
    today_db_backup = list(BACKUP_DIR.glob(f"access_{today}_*.db"))
    
    if today_db_backup:
        print(f"  {Colors.GREEN}✓ Backup database di oggi presente{Colors.ENDC}")
    else:
        print(f"  {Colors.YELLOW}⚠ Nessun backup database di oggi{Colors.ENDC}")
        print(f"    Eseguire: {PROJECT_ROOT}/scripts/quick_backup.sh")
    
    # 5. Suggerimenti
    print(f"\n{Colors.BLUE}COMANDI UTILI:{Colors.ENDC}")
    print(f"  • Backup completo: python3 {PROJECT_ROOT}/scripts/backup_project.py")
    print(f"  • Backup rapido: {PROJECT_ROOT}/scripts/quick_backup.sh")
    print(f"  • Ripristino: vedere script in {BACKUP_DIR}/restore_*.sh")
    
    # 6. Controllo integrità ultimo backup
    if complete_backups:
        print(f"\n{Colors.BLUE}TEST INTEGRITA':{Colors.ENDC}")
        latest = complete_backups[-1]
        checksum_file = latest.with_suffix('.tar.gz.md5')
        
        if checksum_file.exists():
            print(f"  Verifica {latest.name}...")
            try:
                import subprocess
                result = subprocess.run(
                    ['md5sum', '-c', str(checksum_file)],
                    capture_output=True,
                    text=True,
                    cwd=str(BACKUP_DIR)
                )
                if result.returncode == 0:
                    print(f"  {Colors.GREEN}✓ Checksum verificato{Colors.ENDC}")
                else:
                    print(f"  {Colors.RED}✗ Checksum non corrispondente!{Colors.ENDC}")
            except Exception as e:
                print(f"  {Colors.YELLOW}⚠ Impossibile verificare checksum: {str(e)}{Colors.ENDC}")
        else:
            print(f"  {Colors.YELLOW}⚠ File checksum non trovato{Colors.ENDC}")

if __name__ == "__main__":
    check_backup_status()
