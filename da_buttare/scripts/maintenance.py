#!/usr/bin/env python3
# File: /opt/access_control/scripts/maintenance.py
# Script manutenzione sistema

import os
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime, timedelta

def run_maintenance():
    """Manutenzione automatica sistema"""
    
    print("🔧 MANUTENZIONE SISTEMA CONTROLLO ACCESSI")
    print("=" * 50)
    
    project_root = Path("/opt/access_control")
    
    # 1. Pulizia log vecchi (>30 giorni)
    cleanup_old_logs(project_root)
    
    # 2. Backup database
    backup_database(project_root)
    
    # 3. Vacuum database
    vacuum_database(project_root)
    
    # 4. Pulizia file temporanei
    cleanup_temp_files(project_root)
    
    # 5. Report spazio disco
    check_disk_space()
    
    print("✅ Manutenzione completata")

def cleanup_old_logs(project_root):
    """Pulisce log vecchi"""
    logs_dir = project_root / "logs"
    if not logs_dir.exists():
        return
    
    cutoff_date = datetime.now() - timedelta(days=30)
    removed = 0
    
    for log_file in logs_dir.glob("*.log*"):
        if log_file.stat().st_mtime < cutoff_date.timestamp():
            log_file.unlink()
            removed += 1
    
    print(f"🗑️ Rimossi {removed} file log vecchi")

def backup_database(project_root):
    """Backup database"""
    db_path = project_root / "src" / "access.db"
    if not db_path.exists():
        return
    
    backup_dir = project_root / "backup" / "daily"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    backup_name = f"access_db_{datetime.now().strftime('%Y%m%d')}.db"
    backup_path = backup_dir / backup_name
    
    shutil.copy2(db_path, backup_path)
    print(f"💾 Database backup: {backup_path}")

def vacuum_database(project_root):
    """Ottimizza database"""
    db_path = project_root / "src" / "access.db"
    if not db_path.exists():
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute("VACUUM")
        conn.close()
        print("🗜️ Database ottimizzato")
    except Exception as e:
        print(f"⚠️ Errore vacuum: {e}")

def cleanup_temp_files(project_root):
    """Pulisce file temporanei"""
    temp_dir = project_root / "temp"
    if not temp_dir.exists():
        return
    
    removed = 0
    for temp_file in temp_dir.glob("*"):
        if temp_file.is_file():
            temp_file.unlink()
            removed += 1
    
    print(f"🧹 Rimossi {removed} file temporanei")

def check_disk_space():
    """Controlla spazio disco"""
    import shutil
    usage = shutil.disk_usage('/')
    free_gb = usage.free / (1024**3)
    total_gb = usage.total / (1024**3)
    used_percent = (usage.used / usage.total) * 100
    
    print(f"💿 Spazio disco: {used_percent:.1f}% usato, {free_gb:.1f}GB liberi")
    
    if used_percent > 90:
        print("⚠️ WARNING: Spazio disco quasi esaurito!")
    elif used_percent > 80:
        print("📢 INFO: Spazio disco in diminuzione")

if __name__ == "__main__":
    run_maintenance()
