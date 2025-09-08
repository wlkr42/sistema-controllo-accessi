# File: /opt/access_control/src/api/backup_module.py
# Modulo gestione backup per dashboard web

from flask import jsonify, request, send_file, send_from_directory, abort, Blueprint

# Crea Blueprint per il modulo backup
backup_bp = Blueprint('backup', __name__, url_prefix='/api/backup')
import os
import shutil
import tarfile
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import threading
import logging

# Configurazione
PROJECT_ROOT = Path("/opt/access_control")
BACKUP_DIR = PROJECT_ROOT / "backups"
BACKUP_CONFIG = BACKUP_DIR / "backup_config.json"

# Assicurati che la directory backup esista
BACKUP_DIR.mkdir(exist_ok=True)

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurazione di default migliorata
DEFAULT_CONFIG = {
    'auto_backup': {
        'enabled': True,
        'daily': {
            'enabled': True,
            'time': '02:00',
            'type': 'database',  # database o complete
            'retention_days': 7
        },
        'weekly': {
            'enabled': True,
            'time': '03:00',
            'day': '0',  # Domenica
            'type': 'complete',
            'retention_weeks': 4
        },
        'monthly': {
            'enabled': True,
            'time': '04:00',
            'day': '1',  # Primo del mese
            'type': 'complete',
            'retention_months': 6
        },
        'yearly': {
            'enabled': False,
            'time': '05:00',
            'month': '1',  # Gennaio
            'day': '1',
            'type': 'complete',
            'retention_years': 3
        }
    },
    'retention': {
        'auto_cleanup': True,
        'daily_keep': 7,
        'weekly_keep': 4,
        'monthly_keep': 6,
        'yearly_keep': 3,
        'max_size_gb': 10,
        'cleanup_time': '01:00'
    },
    'cloud_backup': {
        'enabled': False,
        'provider': 'none',  # none, aws, google, azure, ftp
        'auto_sync': False,
        'sync_after_backup': True,
        'credentials': {
            'aws': {
                'access_key': '',
                'secret_key': '',
                'bucket': '',
                'region': 'eu-west-1'
            },
            'google': {
                'credentials_json': '',
                'bucket': ''
            },
            'azure': {
                'connection_string': '',
                'container': ''
            },
            'ftp': {
                'host': '',
                'port': 21,
                'username': '',
                'password': '',
                'path': '/backups'
            }
        }
    },
    'integrity_check': {
        'enabled': True,
        'schedule': 'daily',
        'time': '06:00',
        'verify_checksums': True,
        'test_restore': False,
        'alert_on_failure': True
    }
}

@backup_bp.route('/download/<filename>')
def download_backup(filename):
    """Download di un backup"""
    try:
        # Costruisci percorso file
        file_path = BACKUP_DIR / filename
        
        # Verifica sicurezza percorso (previene path traversal)
        try:
            file_path.resolve().relative_to(BACKUP_DIR.resolve())
        except ValueError:
            abort(403)
        
        # Verifica che il file esista
        if not file_path.exists() or not file_path.is_file():
            abort(404)
        
        # Invia il file per download
        return send_file(
            str(file_path),
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logging.error(f"Errore download backup {filename}: {str(e)}")
        abort(500)

@backup_bp.route('/status')
def get_backup_status():
    """Stato generale backup"""
    try:
        backups = []
        total_size = 0
        
        # Backup completi
        for backup in sorted(BACKUP_DIR.glob("backup_completo_*.tar.gz"), reverse=True):
            stat = backup.stat()
            total_size += stat.st_size
            
            # Verifica checksum - FIX: usa il nome corretto
            checksum_path = BACKUP_DIR / f"{backup.name}.md5"
            has_checksum = checksum_path.exists()
            
            backups.append({
                'name': backup.name,
                'type': 'complete',
                'size': format_size(stat.st_size),
                'size_bytes': stat.st_size,
                'date': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'age_days': (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days,
                'has_checksum': has_checksum,
                'can_download': True,
                'can_restore': has_checksum  # Solo con checksum valido
            })
        
        # Backup database
        for db_backup in sorted(BACKUP_DIR.glob("access_*.db"), reverse=True)[:10]:
            stat = db_backup.stat()
            total_size += stat.st_size
            
            # Verifica checksum anche per database
            checksum_path = BACKUP_DIR / f"{db_backup.name}.md5"
            has_checksum = checksum_path.exists()
            
            backups.append({
                'name': db_backup.name,
                'type': 'database',
                'size': format_size(stat.st_size),
                'size_bytes': stat.st_size,
                'date': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'age_days': (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days,
                'has_checksum': has_checksum,
                'can_download': True,
                'can_restore': has_checksum  # ORA POSSONO ESSERE RIPRISTINATI!
            })
        
        # Trova ultimo backup
        last_backup = 'Mai'
        if backups:
            last_backup = backups[0]['date']
        
        # Statistiche disco
        disk_stat = os.statvfs(BACKUP_DIR)
        disk_free = disk_stat.f_bavail * disk_stat.f_frsize
        disk_total = disk_stat.f_blocks * disk_stat.f_frsize
        
        return jsonify({
            'success': True,
            'backups': backups[:20],  # Ultimi 20
            'total_backups': len(backups),
            'total_size': format_size(total_size),
            'last_backup': last_backup,
            'disk_free': format_size(disk_free),
            'disk_used_percent': round((1 - disk_free/disk_total) * 100, 1),
            'config': load_config(),
            'operations': backup_operations
        })
        
    except Exception as e:
        logger.error(f"Errore get_backup_status: {e}")
        return jsonify({'success': False, 'error': str(e)})

@backup_bp.route('/create', methods=['POST'])
def create_backup():
    """Crea nuovo backup"""
    try:
        # LEGGI IL TIPO DAL JSON POST
        data = request.get_json() or {}
        backup_type = data.get('type', 'complete')  # Default 'complete' se non specificato
        
        operation_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Avvia backup in thread
        def run_backup():
            global backup_operations
            backup_operations[operation_id] = {
                'status': 'running',
                'type': backup_type,
                'progress': 0,
                'message': 'Inizializzazione...',
                'start_time': datetime.now().isoformat()
            }
            
            try:
                if backup_type == 'complete':
                    result = create_complete_backup(operation_id)
                elif backup_type == 'database':
                    result = create_db_backup(operation_id)
                else:
                    raise ValueError(f"Tipo backup non valido: {backup_type}")
                
                backup_operations[operation_id]['status'] = 'completed'
                backup_operations[operation_id]['result'] = result
                backup_operations[operation_id]['progress'] = 100
                
            except Exception as e:
                backup_operations[operation_id]['status'] = 'error'
                backup_operations[operation_id]['error'] = str(e)
                backup_operations[operation_id]['progress'] = 0
        
        thread = threading.Thread(target=run_backup)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'operation_id': operation_id,
            'message': f'Backup {backup_type} avviato'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def create_complete_backup(operation_id):
    """Crea backup completo"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"backup_completo_{timestamp}"
    temp_dir = BACKUP_DIR / backup_name
    
    try:
        # Update progress
        backup_operations[operation_id]['message'] = 'Creazione directory temporanea...'
        backup_operations[operation_id]['progress'] = 10
        
        temp_dir.mkdir(exist_ok=True)
        
        # Copia componenti - TUTTE LE CARTELLE IMPORTANTI
        components = [
            ("src", "Codice sorgente", 15),
            ("data", "Database e dati", 15),
            ("config", "Configurazioni", 10),
            ("scripts", "Scripts", 10),
            ("docs", "Documentazione", 10),
            ("logs", "Log di sistema", 5),
            ("tests", "Test suite", 5)
        ]
        
        for comp_name, desc, progress in components:
            backup_operations[operation_id]['message'] = f'Backup {desc}...'
            backup_operations[operation_id]['progress'] += progress
            
            source = PROJECT_ROOT / comp_name
            if source.exists():
                if source.is_file():
                    shutil.copy2(source, temp_dir / comp_name)
                else:
                    # Ignora file temporanei ma mantieni i log importanti
                    ignore_patterns = ['*.pyc', '__pycache__', '*.pid', '*.sock']
                    if comp_name == 'logs':
                        # Per i log, mantieni tutto tranne i file troppo grandi
                        ignore_patterns = ['*.pyc', '__pycache__']
                    shutil.copytree(source, temp_dir / comp_name, 
                                  ignore=shutil.ignore_patterns(*ignore_patterns))
        
        # Copia file importanti nella root
        backup_operations[operation_id]['message'] = 'Backup file di configurazione root...'
        backup_operations[operation_id]['progress'] += 10
        
        # File singoli importanti nella root
        root_files = [
            'requirements.txt',
            'README.md',
            'CHANGELOG.md',
            '.env',
            'setup.py',
            'manage.py'
        ]
        
        for file_name in root_files:
            file_path = PROJECT_ROOT / file_name
            if file_path.exists():
                shutil.copy2(file_path, temp_dir / file_name)
        
        # Copia tutti gli script .sh nella root
        for sh_file in PROJECT_ROOT.glob('*.sh'):
            if sh_file.is_file():
                shutil.copy2(sh_file, temp_dir / sh_file.name)
        
        # Copia tutti i file .py nella root (se esistono)
        for py_file in PROJECT_ROOT.glob('*.py'):
            if py_file.is_file():
                shutil.copy2(py_file, temp_dir / py_file.name)
        
        # Database (se non troppo grande)
        from core.db_config import CURRENT_DB_PATH
        db_path = Path(CURRENT_DB_PATH)
        if db_path.exists() and db_path.stat().st_size < 500 * 1024 * 1024:
            backup_operations[operation_id]['message'] = 'Backup database...'
            shutil.copy2(db_path, temp_dir / "access.db")
        
        # Crea archivio
        backup_operations[operation_id]['message'] = 'Creazione archivio...'
        backup_operations[operation_id]['progress'] = 90
        
        archive_path = BACKUP_DIR / f"{backup_name}.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(temp_dir, arcname=backup_name)
        
        # Calcola checksum
        import hashlib
        hash_md5 = hashlib.md5()
        with open(archive_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        
        checksum = hash_md5.hexdigest()
        # FIX: Usa il nome completo con .md5 alla fine invece di with_suffix
        checksum_path = BACKUP_DIR / f"{archive_path.name}.md5"
        with open(checksum_path, 'w') as f:
            f.write(f"{checksum}  {archive_path.name}\n")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        return {
            'filename': archive_path.name,
            'size': format_size(archive_path.stat().st_size),
            'checksum': checksum
        }
        
    except Exception as e:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        raise

def create_db_backup(operation_id):
    """Crea backup solo database con checksum"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    backup_operations[operation_id]['message'] = 'Backup database...'
    backup_operations[operation_id]['progress'] = 30
    
    from core.db_config import CURRENT_DB_PATH
    db_source = Path(CURRENT_DB_PATH)
    db_backup = BACKUP_DIR / f"access_{timestamp}.db"
    
    if db_source.exists():
        # Copia database
        shutil.copy2(db_source, db_backup)
        
        backup_operations[operation_id]['message'] = 'Calcolo checksum...'
        backup_operations[operation_id]['progress'] = 70
        
        # AGGIUNGI CHECKSUM per database
        import hashlib
        hash_md5 = hashlib.md5()
        with open(db_backup, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        
        checksum = hash_md5.hexdigest()
        checksum_path = BACKUP_DIR / f"{db_backup.name}.md5"
        with open(checksum_path, 'w') as f:
            f.write(f"{checksum}  {db_backup.name}\n")
        
        backup_operations[operation_id]['progress'] = 90
        
        # Traccia ultimo backup
        latest_file = BACKUP_DIR / "latest_database.txt"
        latest_file.write_text(db_backup.name)
        
        backup_operations[operation_id]['progress'] = 100
        
        return {
            'filename': db_backup.name,
            'size': format_size(db_backup.stat().st_size),
            'checksum': checksum
        }
    else:
        raise FileNotFoundError("Database non trovato")

@backup_bp.route('/delete/<filename>', methods=['DELETE', 'POST'])  # Aggiungi POST per compatibilità
def delete_backup(filename):
    """Elimina un backup - gestisce anche file mancanti"""
    try:
        logger.info(f"Richiesta eliminazione backup: {filename}")
        
        # Sicurezza: verifica che sia nella directory backup
        file_path = BACKUP_DIR / filename
        
        # Verifica sicurezza percorso PRIMA di controllare esistenza
        try:
            # Usa il nome del file per validazione, non il percorso completo
            if ".." in filename or "/" in filename or "\\" in filename:
                logger.error(f"Nome file non valido: {filename}")
                return jsonify({'success': False, 'error': 'Nome file non valido'})
        except Exception as e:
            logger.error(f"Errore validazione percorso: {e}")
            return jsonify({'success': False, 'error': 'Percorso non valido'})
        
        # Contatori per feedback
        files_deleted = 0
        files_not_found = []
        
        # Prova a eliminare il file principale
        if file_path.exists():
            try:
                # Verifica permessi
                if os.access(file_path, os.W_OK):
                    file_path.unlink()
                    logger.info(f"File eliminato: {file_path}")
                    files_deleted += 1
                else:
                    logger.error(f"Permessi insufficienti per: {file_path}")
                    return jsonify({'success': False, 'error': 'Permessi insufficienti per eliminare il file'})
            except Exception as e:
                logger.error(f"Errore eliminazione file: {e}")
                return jsonify({'success': False, 'error': f'Errore eliminazione: {str(e)}'})
        else:
            logger.warning(f"File principale non trovato: {file_path}")
            files_not_found.append(filename)
        
        # Prova a eliminare il checksum (sempre, anche se il file principale non c'è)
        checksum_file = BACKUP_DIR / f"{filename}.md5"
        if checksum_file.exists():
            try:
                checksum_file.unlink()
                logger.info(f"Checksum eliminato: {checksum_file}")
                files_deleted += 1
            except Exception as e:
                logger.warning(f"Impossibile eliminare checksum: {e}")
        
        # Determina il messaggio di risposta
        if files_deleted > 0:
            # Almeno qualcosa è stato eliminato
            if files_not_found:
                message = f'Backup {filename} rimosso dalla lista (file già assente dal filesystem)'
            else:
                message = f'Backup {filename} eliminato con successo'
            return jsonify({'success': True, 'message': message})
        elif files_not_found:
            # Niente da eliminare ma rimuovi dalla lista comunque
            message = f'Backup {filename} già assente - rimosso dalla lista'
            logger.info(message)
            # Restituisci success=True così la UI rimuove l'entry
            return jsonify({'success': True, 'message': message, 'warning': True})
        else:
            # Non dovrebbe mai arrivare qui
            return jsonify({'success': False, 'error': 'Nessuna operazione eseguita'})
        
    except PermissionError as e:
        logger.error(f"Errore permessi eliminazione {filename}: {e}")
        return jsonify({'success': False, 'error': f'Errore permessi: {str(e)}'})
    except Exception as e:
        logger.error(f"Errore eliminazione {filename}: {e}")
        return jsonify({'success': False, 'error': f'Errore: {str(e)}'})

@backup_bp.route('/cleanup', methods=['POST'])
def cleanup_old_backups():
    """Pulizia backup vecchi secondo policy"""
    try:
        config = load_config()
        retention = config['retention']
        
        cleaned = []
        freed_space = 0
        
        # Backup giornalieri
        daily_backups = sorted([f for f in BACKUP_DIR.glob("access_*.db") 
                              if (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days <= retention['daily_keep']], 
                              key=lambda x: x.stat().st_mtime, reverse=True)
        
        for backup in daily_backups[retention['daily_keep']:]:
            freed_space += backup.stat().st_size
            backup.unlink()
            cleaned.append(backup.name)
        
        # Backup settimanali (backup completi più vecchi di 7 giorni)
        weekly_backups = sorted([f for f in BACKUP_DIR.glob("backup_completo_*.tar.gz")
                               if (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days > 7],
                               key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Mantieni solo uno per settimana
        weeks_kept = set()
        for backup in weekly_backups:
            backup_date = datetime.fromtimestamp(backup.stat().st_mtime)
            week_key = backup_date.strftime("%Y-%W")
            
            if week_key in weeks_kept or len(weeks_kept) >= retention['weekly_keep']:
                freed_space += backup.stat().st_size
                backup.unlink()
                # Elimina anche checksum - FIX: usa il nome corretto
                checksum = BACKUP_DIR / f"{backup.name}.md5"
                if checksum.exists():
                    checksum.unlink()
                cleaned.append(backup.name)
            else:
                weeks_kept.add(week_key)
        
        # Controllo spazio totale
        total_size = sum(f.stat().st_size for f in BACKUP_DIR.rglob("*") if f.is_file())
        max_size = retention['max_size_gb'] * 1024 * 1024 * 1024
        
        if total_size > max_size:
            # Elimina i più vecchi fino a rientrare nel limite
            all_backups = sorted(BACKUP_DIR.glob("*"), key=lambda x: x.stat().st_mtime)
            
            for backup in all_backups:
                if total_size <= max_size:
                    break
                if backup.is_file():
                    size = backup.stat().st_size
                    freed_space += size
                    total_size -= size
                    backup.unlink()
                    cleaned.append(backup.name)
        
        return jsonify({
            'success': True,
            'cleaned_files': len(cleaned),
            'freed_space': format_size(freed_space),
            'files': cleaned[:10]  # Mostra solo primi 10
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@backup_bp.route('/config', methods=['POST'])
def update_config():
    new_config = request.get_json()
    """Aggiorna configurazione backup"""
    try:
        # Valida configurazione
        if not isinstance(new_config, dict):
            return jsonify({'success': False, 'error': 'Configurazione non valida'})
        
        # Salva
        save_config(new_config)
        
        # Aggiorna crontab se necessario
        update_crontab(new_config)
        
        return jsonify({'success': True, 'message': 'Configurazione aggiornata'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def update_crontab(config):
    """Aggiorna crontab per backup automatici"""
    try:
        # Lo script auto_backup.py ora esiste!
        script_path = "/opt/access_control/scripts/auto_backup.py"
        if not Path(script_path).exists():
            logger.warning(f"Script backup non trovato: {script_path}")
            return False
        
        cron_entries = []
        
        if config['auto_backup']['enabled']:
            # Backup giornaliero
            if config['auto_backup']['daily']['enabled']:
                time = config['auto_backup']['daily']['time']
                hour, minute = time.split(':')
                backup_type = config['auto_backup']['daily'].get('type', 'database')
                # Usa lo script Python auto_backup.py
                cron_entries.append(
                    f"{minute} {hour} * * * cd /opt/access_control && /usr/bin/python3 scripts/auto_backup.py {backup_type} >> logs/auto_backup.log 2>&1"
                )
            
            # Backup settimanale
            if config['auto_backup']['weekly']['enabled']:
                time = config['auto_backup']['weekly']['time']
                hour, minute = time.split(':')
                day = config['auto_backup']['weekly']['day']
                backup_type = config['auto_backup']['weekly'].get('type', 'complete')
                cron_entries.append(
                    f"{minute} {hour} * * {day} cd /opt/access_control && /usr/bin/python3 scripts/auto_backup.py {backup_type} >> logs/auto_backup.log 2>&1"
                )
            
            # Backup mensile
            if config['auto_backup']['monthly']['enabled']:
                time = config['auto_backup']['monthly']['time']
                hour, minute = time.split(':')
                day = config['auto_backup']['monthly']['day']
                backup_type = config['auto_backup']['monthly'].get('type', 'complete')
                cron_entries.append(
                    f"{minute} {hour} {day} * * cd /opt/access_control && /usr/bin/python3 scripts/auto_backup.py {backup_type} >> logs/auto_backup.log 2>&1"
                )
            
            # Backup annuale
            if config['auto_backup']['yearly']['enabled']:
                time = config['auto_backup']['yearly']['time']
                hour, minute = time.split(':')
                month = config['auto_backup']['yearly']['month']
                day = config['auto_backup']['yearly']['day']
                backup_type = config['auto_backup']['yearly'].get('type', 'complete')
                cron_entries.append(
                    f"{minute} {hour} {day} {month} * cd /opt/access_control && /usr/bin/python3 scripts/auto_backup.py {backup_type} >> logs/auto_backup.log 2>&1"
                )
        
        # Leggi crontab esistente
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        existing_cron = result.stdout if result.returncode == 0 else ""
        
        # Rimuovi vecchie entry di backup
        new_cron_lines = []
        for line in existing_cron.split('\n'):
            if 'access_control' not in line or 'backup' not in line:
                new_cron_lines.append(line)
        
        # Aggiungi nuove entry
        new_cron_lines.extend(cron_entries)
        
        # Scrivi nuovo crontab - IMPORTANTE: deve terminare con newline
        new_cron = '\n'.join(new_cron_lines)
        if new_cron and not new_cron.endswith('\n'):
            new_cron += '\n'
        
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
        process.communicate(new_cron)
        
        return True
        
    except Exception as e:
        raise

def restore_database_backup(filename, file_path):
    """Ripristina un backup del database"""
    try:
        # Verifica checksum
        checksum_file = BACKUP_DIR / f"{filename}.md5"
        if not checksum_file.exists():
            return jsonify({'success': False, 'error': 'Checksum mancante - ripristino database non consentito'})
        
        # Verifica integrità
        import hashlib
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        
        actual_checksum = hash_md5.hexdigest()
        expected_checksum = checksum_file.read_text().split()[0]
        
        if actual_checksum != expected_checksum:
            return jsonify({'success': False, 'error': 'Checksum non valido - database corrotto'})
        
        # Backup del database attuale
        from core.db_config import CURRENT_DB_PATH
        current_db = Path(CURRENT_DB_PATH)
        
        if current_db.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"access_before_restore_{timestamp}.db"
            backup_path = BACKUP_DIR / backup_name
            shutil.copy2(current_db, backup_path)
            
            # Crea checksum per il backup pre-restore
            hash_md5 = hashlib.md5()
            with open(backup_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            checksum = hash_md5.hexdigest()
            with open(BACKUP_DIR / f"{backup_name}.md5", 'w') as f:
                f.write(f"{checksum}  {backup_name}\n")
        
        # Ripristina il database
        shutil.copy2(file_path, current_db)
        
        return jsonify({
            'success': True,
            'message': f'Database ripristinato da {filename}. Backup precedente salvato come {backup_name if current_db.exists() else "N/A"}'
        })
        
    except Exception as e:
        logger.error(f"Errore restore database: {e}")
        return jsonify({'success': False, 'error': str(e)})

@backup_bp.route('/restore/<filename>', methods=['POST'])
def restore_backup(filename):
    """Ripristina un backup - CON ESTREMA CAUTELA"""
    try:
        # SICUREZZA: Verifica che il servizio non sia in produzione
        import socket
        hostname = socket.gethostname()
        if 'prod' in hostname.lower():
            return jsonify({'success': False, 'error': 'ERRORE: Ripristino non consentito in ambiente di produzione'})
        
        file_path = BACKUP_DIR / filename
        
        # Verifica sicurezza path
        try:
            file_path.resolve().relative_to(BACKUP_DIR.resolve())
        except ValueError:
            return jsonify({'success': False, 'error': 'Percorso non valido'})
        
        if not file_path.exists():
            return jsonify({'success': False, 'error': 'Backup non trovato'})
        
        # Gestisci sia backup completi che database
        if filename.endswith('.db'):
            # RESTORE DATABASE
            return restore_database_backup(filename, file_path)
        elif not filename.endswith('.tar.gz'):
            return jsonify({'success': False, 'error': 'Formato backup non supportato'})
        
        # OBBLIGATORIO: Verifica checksum - FIX: usa il nome corretto
        checksum_file = BACKUP_DIR / f"{filename}.md5"
        if not checksum_file.exists():
            return jsonify({'success': False, 'error': 'Checksum mancante - ripristino non consentito per sicurezza'})
        
        import hashlib
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        
        actual_checksum = hash_md5.hexdigest()
        expected_checksum = checksum_file.read_text().split()[0]
        
        if actual_checksum != expected_checksum:
            return jsonify({'success': False, 'error': 'Checksum non valido - backup corrotto'})
        
        # Crea backup dell'attuale prima di ripristinare
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_current = PROJECT_ROOT.parent / f"access_control_before_restore_{timestamp}"
        shutil.copytree(PROJECT_ROOT, backup_current, 
                       ignore=shutil.ignore_patterns('*.pyc', '__pycache__', '*.log', 'venv'))
        
        # Estrai backup
        temp_restore = PROJECT_ROOT.parent / "restore_temp"
        if temp_restore.exists():
            shutil.rmtree(temp_restore)
        
        with tarfile.open(file_path, "r:gz") as tar:
            tar.extractall(temp_restore)
        
        # Trova directory estratta
        extracted = list(temp_restore.iterdir())[0]
        
        # Sovrascrivi file
        for item in extracted.iterdir():
            dest = PROJECT_ROOT / item.name
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()
            shutil.move(str(item), str(dest))
        
        # Cleanup
        shutil.rmtree(temp_restore)
        
        return jsonify({
            'success': True,
            'message': f'Backup ripristinato. Backup precedente salvato in: {backup_current.name}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def load_config():
    """Carica configurazione backup"""
    if BACKUP_CONFIG.exists():
        try:
            with open(BACKUP_CONFIG, 'r') as f:
                return json.load(f)
        except:
            pass
    
    # Crea config default
    BACKUP_DIR.mkdir(exist_ok=True)
    with open(BACKUP_CONFIG, 'w') as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
    
    return DEFAULT_CONFIG

def save_config(config):
    """Salva configurazione backup"""
    with open(BACKUP_CONFIG, 'w') as f:
        json.dump(config, f, indent=2)

def format_size(bytes):
    """Formatta dimensione file"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

# Stato globale operazioni
backup_operations = {}

# ===============================
# NUOVE FUNZIONI CLOUD E INTEGRITY
# ===============================

@backup_bp.route('/cloud/sync', methods=['POST'])
def sync_to_cloud():
    """Sincronizza backup su cloud"""
    try:
        config = load_config()
        cloud_config = config.get('cloud_backup', {})
        
        if not cloud_config.get('enabled'):
            return jsonify({'success': False, 'error': 'Cloud backup non abilitato'})
        
        provider = cloud_config.get('provider')
        if provider == 'none':
            return jsonify({'success': False, 'error': 'Nessun provider cloud configurato'})
        
        # Avvia sync in background
        operation_id = f"cloud_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        def run_cloud_sync():
            backup_operations[operation_id] = {
                'status': 'running',
                'type': 'cloud_sync',
                'progress': 0,
                'message': f'Sincronizzazione con {provider}...'
            }
            
            try:
                result = perform_cloud_sync(provider, cloud_config, operation_id)
                backup_operations[operation_id]['status'] = 'completed'
                backup_operations[operation_id]['result'] = result
            except Exception as e:
                backup_operations[operation_id]['status'] = 'error'
                backup_operations[operation_id]['error'] = str(e)
        
        thread = threading.Thread(target=run_cloud_sync)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'operation_id': operation_id,
            'message': f'Sincronizzazione cloud avviata con {provider}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def perform_cloud_sync(provider, config, operation_id):
    """Esegue sync con provider cloud specifico"""
    synced_files = []
    
    try:
        if provider == 'ftp':
            import ftplib
            credentials = config['credentials']['ftp']
            
            backup_operations[operation_id]['message'] = 'Connessione FTP...'
            ftp = ftplib.FTP(credentials['host'], credentials['username'], credentials['password'])
            
            # Cambia directory
            ftp.cwd(credentials['path'])
            
            # Lista file locali da sincronizzare
            local_files = list(BACKUP_DIR.glob("*.tar.gz")) + list(BACKUP_DIR.glob("*.db"))
            total = len(local_files)
            
            for idx, file_path in enumerate(local_files):
                backup_operations[operation_id]['progress'] = int((idx / total) * 100)
                backup_operations[operation_id]['message'] = f'Upload {file_path.name}...'
                
                # Verifica se file esiste già
                remote_files = ftp.nlst()
                if file_path.name not in remote_files:
                    with open(file_path, 'rb') as f:
                        ftp.storbinary(f'STOR {file_path.name}', f)
                    synced_files.append(file_path.name)
            
            ftp.quit()
            
        elif provider == 'aws':
            # Implementazione AWS S3
            try:
                import boto3
                credentials = config['credentials']['aws']
                
                s3 = boto3.client('s3',
                    aws_access_key_id=credentials['access_key'],
                    aws_secret_access_key=credentials['secret_key'],
                    region_name=credentials['region']
                )
                
                bucket = credentials['bucket']
                local_files = list(BACKUP_DIR.glob("*.tar.gz")) + list(BACKUP_DIR.glob("*.db"))
                
                for file_path in local_files:
                    s3.upload_file(str(file_path), bucket, file_path.name)
                    synced_files.append(file_path.name)
                    
            except ImportError:
                raise Exception("boto3 non installato. Esegui: pip install boto3")
                
        # Altri provider possono essere aggiunti qui
        
        return {
            'synced_files': len(synced_files),
            'files': synced_files[:10]
        }
        
    except Exception as e:
        raise Exception(f"Errore sync cloud: {str(e)}")

@backup_bp.route('/integrity/check', methods=['POST'])
def check_integrity():
    """Verifica integrità di tutti i backup"""
    try:
        operation_id = f"integrity_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        def run_integrity_check():
            backup_operations[operation_id] = {
                'status': 'running',
                'type': 'integrity_check',
                'progress': 0,
                'message': 'Verifica integrità backup...'
            }
            
            try:
                result = perform_integrity_check(operation_id)
                backup_operations[operation_id]['status'] = 'completed'
                backup_operations[operation_id]['result'] = result
            except Exception as e:
                backup_operations[operation_id]['status'] = 'error'
                backup_operations[operation_id]['error'] = str(e)
        
        thread = threading.Thread(target=run_integrity_check)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'operation_id': operation_id,
            'message': 'Verifica integrità avviata'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def perform_integrity_check(operation_id):
    """Esegue verifica integrità backup"""
    import hashlib
    
    results = {
        'total_files': 0,
        'valid': 0,
        'corrupted': 0,
        'missing_checksum': 0,
        'errors': []
    }
    
    # Trova tutti i backup
    backup_files = list(BACKUP_DIR.glob("*.tar.gz"))
    results['total_files'] = len(backup_files)
    
    for idx, backup_file in enumerate(backup_files):
        backup_operations[operation_id]['progress'] = int((idx / len(backup_files)) * 100)
        backup_operations[operation_id]['message'] = f'Verifica {backup_file.name}...'
        
        # FIX: usa il nome corretto per il checksum
        checksum_file = BACKUP_DIR / f"{backup_file.name}.md5"
        
        if not checksum_file.exists():
            results['missing_checksum'] += 1
            results['errors'].append(f"{backup_file.name}: checksum mancante")
            continue
        
        # Calcola checksum attuale
        hash_md5 = hashlib.md5()
        try:
            with open(backup_file, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            
            actual_checksum = hash_md5.hexdigest()
            expected_checksum = checksum_file.read_text().split()[0]
            
            if actual_checksum == expected_checksum:
                results['valid'] += 1
            else:
                results['corrupted'] += 1
                results['errors'].append(f"{backup_file.name}: checksum non valido")
                
        except Exception as e:
            results['errors'].append(f"{backup_file.name}: errore lettura - {str(e)}")
    
    return results

@backup_bp.route('/retention/apply', methods=['POST'])
def apply_retention_policy():
    """Applica politiche di retention manualmente"""
    try:
        config = load_config()
        result = perform_retention_cleanup(config)
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def perform_retention_cleanup(config):
    """Esegue pulizia secondo le politiche di retention"""
    retention = config.get('retention', {})
    cleaned = []
    freed_space = 0
    
    now = datetime.now()
    
    # Organizza backup per tipo e data
    backups_by_type = {
        'daily': [],
        'weekly': [],
        'monthly': [],
        'yearly': []
    }
    
    for backup_file in BACKUP_DIR.glob("backup_*.tar.gz"):
        file_date = datetime.fromtimestamp(backup_file.stat().st_mtime)
        age_days = (now - file_date).days
        
        # Classifica il backup
        if age_days <= 7:
            backups_by_type['daily'].append(backup_file)
        elif age_days <= 30:
            backups_by_type['weekly'].append(backup_file)
        elif age_days <= 365:
            backups_by_type['monthly'].append(backup_file)
        else:
            backups_by_type['yearly'].append(backup_file)
    
    # Applica retention per tipo
    for backup_type, files in backups_by_type.items():
        keep_count = retention.get(f'{backup_type}_keep', 0)
        
        if keep_count > 0:
            # Ordina per data, mantieni solo i più recenti
            sorted_files = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
            
            for file_to_delete in sorted_files[keep_count:]:
                size = file_to_delete.stat().st_size
                file_to_delete.unlink()
                
                # Elimina anche checksum - FIX: usa il nome corretto
                checksum = BACKUP_DIR / f"{file_to_delete.name}.md5"
                if checksum.exists():
                    checksum.unlink()
                
                cleaned.append(file_to_delete.name)
                freed_space += size
    
    # Controllo spazio massimo
    total_size = sum(f.stat().st_size for f in BACKUP_DIR.rglob("*") if f.is_file())
    max_size = retention.get('max_size_gb', 10) * 1024 * 1024 * 1024
    
    if total_size > max_size:
        all_backups = sorted(BACKUP_DIR.glob("*"), key=lambda x: x.stat().st_mtime)
        
        for backup in all_backups:
            if total_size <= max_size:
                break
            if backup.is_file() and backup.suffix in ['.gz', '.db']:
                size = backup.stat().st_size
                backup.unlink()
                cleaned.append(backup.name)
                freed_space += size
                total_size -= size
    
    return {
        'cleaned_files': len(cleaned),
        'freed_space': format_size(freed_space),
        'files': cleaned[:20]
    }
