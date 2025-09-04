#!/usr/bin/env python3
import os
import sys
import sqlite3
from datetime import datetime, date
from pathlib import Path

# Aggiungi la directory src al path per importare i moduli
sys.path.append(str(Path(__file__).parent.parent))
from src.database.database_manager import get_db_connection

def archive_conteggi_mensili(conn, anno, mese):
    """Archivia i conteggi del mese precedente"""
    cursor = conn.cursor()
    
    try:
        # Sposta i conteggi in archivio
        cursor.execute('''
            INSERT INTO conteggio_ingressi_mensili_archive 
            (codice_fiscale, anno, mese, ingressi)
            SELECT codice_fiscale, anno, mese, ingressi
            FROM conteggio_ingressi_mensili
            WHERE anno = ? AND mese = ?
        ''', (anno, mese))
        
        # Elimina i conteggi archiviati
        cursor.execute('''
            DELETE FROM conteggio_ingressi_mensili
            WHERE anno = ? AND mese = ?
        ''', (anno, mese))
        
        print(f"✓ Archiviati conteggi di {mese}/{anno}")
        return True
        
    except Exception as e:
        print(f"✗ Errore archiviazione conteggi: {e}")
        return False

def reset_contatori():
    """Reset contatori e riattivazione utenti il primo del mese"""
    oggi = date.today()
    
    # Verifica se è il primo del mese
    if oggi.day != 1:
        print("Non è il primo del mese, skip reset")
        return False
    
    conn = get_db_connection()
    if not conn:
        print("✗ Impossibile connettersi al database")
        return False
    
    try:
        # Calcola mese precedente
        anno_prec = oggi.year
        mese_prec = oggi.month - 1
        if mese_prec == 0:
            mese_prec = 12
            anno_prec -= 1
        
        # Archivia conteggi mese precedente
        if not archive_conteggi_mensili(conn, anno_prec, mese_prec):
            return False
        
        cursor = conn.cursor()
        
        # Riattiva tutti gli utenti disattivati per limite ingressi
        cursor.execute('''
            UPDATE utenti_autorizzati 
            SET attivo = 1 
            WHERE attivo = 0
        ''')
        
        # Log operazione
        cursor.execute('''
            INSERT INTO log_forzature (tipo, utente, dettagli)
            VALUES (?, ?, ?)
        ''', (
            'RESET_MENSILE',
            'system',
            f'Reset automatico contatori {oggi.strftime("%Y-%m-%d")}'
        ))
        
        conn.commit()
        print("✓ Reset contatori completato")
        return True
        
    except Exception as e:
        print(f"✗ Errore reset contatori: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    if reset_contatori():
        sys.exit(0)
    sys.exit(1)
