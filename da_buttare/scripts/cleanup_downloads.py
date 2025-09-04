#!/usr/bin/env python3
import os
import sys
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def cleanup_old_downloads():
    """Pulisce i file di download più vecchi di 24 ore"""
    download_dir = "/opt/access_control/src/api/backup/download"
    
    if not os.path.exists(download_dir):
        logging.info(f"Directory {download_dir} non esiste")
        return
        
    now = datetime.now()
    count = 0
    
    for file in os.listdir(download_dir):
        file_path = os.path.join(download_dir, file)
        if os.path.isfile(file_path):
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if now - mtime > timedelta(hours=24):
                try:
                    os.remove(file_path)
                    count += 1
                    logging.info(f"Rimosso file: {file}")
                except Exception as e:
                    logging.error(f"Errore rimozione {file}: {e}")
    
    logging.info(f"Pulizia completata. Rimossi {count} file")

if __name__ == "__main__":
    cleanup_old_downloads()
    
