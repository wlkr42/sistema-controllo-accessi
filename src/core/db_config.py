"""
Configurazione centralizzata del percorso del database.
Questo file deve essere importato da tutti i moduli che necessitano di accedere al database.
"""

import os
from pathlib import Path

# Percorso base del progetto
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Percorso del database nella cartella data
DB_PATH = str(PROJECT_ROOT / "data" / "access.db")

# Percorso alternativo per compatibilità (se esiste ancora il vecchio)
OLD_DB_PATH = str(PROJECT_ROOT / "src" / "access.db")

def get_db_path():
    """
    Restituisce il percorso corretto del database.
    Prima controlla se esiste nella nuova posizione, altrimenti usa la vecchia.
    """
    if os.path.exists(DB_PATH):
        return DB_PATH
    elif os.path.exists(OLD_DB_PATH):
        return OLD_DB_PATH
    else:
        # Se non esiste, usa il nuovo percorso (verrà creato)
        return DB_PATH

# Export del percorso attuale
CURRENT_DB_PATH = get_db_path()