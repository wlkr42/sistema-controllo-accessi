#!/usr/bin/env python3
"""
Script per backup automatici - può essere chiamato da cron
Uso: python3 auto_backup.py [complete|database]
"""

import sys
import os
import json
import requests
from datetime import datetime
import logging

# Setup logging
LOG_FILE = '/opt/access_control/logs/auto_backup.log'
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def perform_backup(backup_type='database'):
    """Esegue backup chiamando l'API locale"""
    try:
        # URL API locale
        url = 'http://localhost:5000/api/backup/create'
        
        # Payload
        data = {'type': backup_type}
        
        # Headers
        headers = {'Content-Type': 'application/json'}
        
        logging.info(f"Avvio backup {backup_type}...")
        
        # Esegui richiesta
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                logging.info(f"Backup {backup_type} avviato con successo: {result.get('operation_id')}")
                return True
            else:
                logging.error(f"Errore backup: {result.get('error')}")
                return False
        else:
            logging.error(f"Errore HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Errore connessione API: {e}")
        return False
    except Exception as e:
        logging.error(f"Errore generico: {e}")
        return False

def cleanup_old_backups():
    """Pulizia backup vecchi"""
    try:
        url = 'http://localhost:5000/api/backup/retention/apply'
        response = requests.post(url, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                logging.info(f"Pulizia completata: {result.get('result', {}).get('cleaned_files', 0)} file eliminati")
                return True
        
        logging.warning("Pulizia backup non riuscita")
        return False
        
    except Exception as e:
        logging.error(f"Errore pulizia: {e}")
        return False

def main():
    """Main function"""
    # Determina tipo backup da argv o default
    backup_type = 'database'  # Default
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ['complete', 'database']:
            backup_type = sys.argv[1]
        else:
            logging.error(f"Tipo backup non valido: {sys.argv[1]}")
            sys.exit(1)
    
    # Log inizio
    logging.info("="*50)
    logging.info(f"BACKUP AUTOMATICO AVVIATO - Tipo: {backup_type}")
    
    # Esegui backup
    success = perform_backup(backup_type)
    
    # Se backup completo, esegui anche pulizia
    if backup_type == 'complete' and success:
        logging.info("Avvio pulizia backup vecchi...")
        cleanup_old_backups()
    
    # Log fine
    if success:
        logging.info("BACKUP COMPLETATO CON SUCCESSO")
    else:
        logging.error("BACKUP FALLITO")
        sys.exit(1)

if __name__ == '__main__':
    main()