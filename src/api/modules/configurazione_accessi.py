# File: /opt/access_control/src/api/modules/configurazione_accessi.py

import os
import sqlite3
from datetime import datetime, time, date
from calendar import monthrange
import pytz
from flask import Blueprint, jsonify, request, session
from ..utils import require_auth, require_permission, get_db_connection

# Fuso orario di Roma
ROME_TZ = pytz.timezone('Europe/Rome')

configurazione_accessi_bp = Blueprint('configurazione_accessi', __name__)

def get_primo_giorno_mese_successivo():
    """Calcola il primo giorno del mese successivo"""
    oggi = date.today()
    if oggi.month == 12:
        return date(oggi.year + 1, 1, 1)
    return date(oggi.year, oggi.month + 1, 1)

def init_db():
    """Inizializza tabelle per configurazione accessi"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Crea le tabelle se non esistono
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orari_accesso (
                giorno TEXT PRIMARY KEY,
                aperto BOOLEAN DEFAULT true,
                mattina_inizio TIME,
                mattina_fine TIME,
                pomeriggio_inizio TIME,
                pomeriggio_fine TIME,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_by TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS limiti_accesso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                max_ingressi_mensili INTEGER DEFAULT 3,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_by TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS log_forzature (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                utente TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                dettagli TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conteggio_ingressi_mensili (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codice_fiscale TEXT NOT NULL,
                mese INTEGER NOT NULL,
                anno INTEGER NOT NULL,
                numero_ingressi INTEGER DEFAULT 0,
                ultimo_ingresso TIMESTAMP,
                UNIQUE(codice_fiscale, mese, anno)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conteggio_ingressi_mensili_archive (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codice_fiscale TEXT NOT NULL,
                mese INTEGER NOT NULL,
                anno INTEGER NOT NULL,
                numero_ingressi INTEGER,
                ultimo_ingresso TIMESTAMP,
                data_archiviazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Verifica se le tabelle sono vuote
        cursor.execute('SELECT COUNT(*) FROM orari_accesso')
        orari_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM limiti_accesso')
        limiti_count = cursor.fetchone()[0]
        
        # Inserisci valori default SOLO se le tabelle sono vuote
        if orari_count == 0:
            print("Inizializzazione orari default...")
            giorni = ['Lunedi', 'Martedi', 'Mercoledi', 'Giovedi', 'Venerdi', 'Sabato', 'Domenica']
            for giorno in giorni:
                cursor.execute('''
                    INSERT INTO orari_accesso 
                    (giorno, aperto, mattina_inizio, mattina_fine, pomeriggio_inizio, pomeriggio_fine)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (giorno, True, '09:00', '12:00', '15:00', '17:00'))
        
        if limiti_count == 0:
            print("Inizializzazione limite ingressi default...")
            cursor.execute('INSERT INTO limiti_accesso (max_ingressi_mensili) VALUES (?)', (3,))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Errore inizializzazione DB: {e}")
        return False
    finally:
        conn.close()

# Inizializza DB
init_db()

@configurazione_accessi_bp.route('/api/configurazione/orari', methods=['GET'])
@require_auth()
def get_orari():
    """Ottiene configurazione orari"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orari_accesso ORDER BY CASE giorno ' + 
                      "WHEN 'Lunedi' THEN 0 " +
                      "WHEN 'Martedi' THEN 1 " +
                      "WHEN 'Mercoledi' THEN 2 " +
                      "WHEN 'Giovedi' THEN 3 " +
                      "WHEN 'Venerdi' THEN 4 " +
                      "WHEN 'Sabato' THEN 5 " +
                      "WHEN 'Domenica' THEN 6 END")
        
        orari = []
        for row in cursor.fetchall():
            orari.append({
                'giorno': row[0],
                'aperto': bool(row[1]),
                'mattina_inizio': str(row[2]),
                'mattina_fine': str(row[3]),
                'pomeriggio_inizio': str(row[4]),
                'pomeriggio_fine': str(row[5])
            })
        
        return jsonify({'success': True, 'orari': orari})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@configurazione_accessi_bp.route('/api/configurazione/orari', methods=['POST'])
@require_auth()
@require_permission('all')
def save_orari():
    """Salva configurazione orari"""
    # Verifica sessione
    if not session.get('username'):
        return jsonify({'success': False, 'error': 'Sessione non valida'}), 401
        
    data = request.get_json()
    if not data or 'orari' not in data:
        return jsonify({'success': False, 'error': 'Dati mancanti'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Verifica validità orari
        for orario in data['orari']:
            if not all(key in orario for key in ['giorno', 'aperto']):
                return jsonify({'success': False, 'error': 'Formato orari non valido'}), 400
            
            if orario['aperto']:
                if not all(key in orario for key in ['mattina_inizio', 'mattina_fine', 
                                                    'pomeriggio_inizio', 'pomeriggio_fine']):
                    return jsonify({'success': False, 'error': 'Orari incompleti'}), 400
        
        # Elimina tutti i record esistenti
        cursor.execute('DELETE FROM orari_accesso')
        
        # Inserisci nuovi record
        for orario in data['orari']:
            cursor.execute('''
                INSERT INTO orari_accesso 
                (giorno, aperto, mattina_inizio, mattina_fine, pomeriggio_inizio, pomeriggio_fine, updated_at, updated_by)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
            ''', (
                orario['giorno'],
                orario['aperto'],
                orario['mattina_inizio'] if orario['aperto'] else None,
                orario['mattina_fine'] if orario['aperto'] else None,
                orario['pomeriggio_inizio'] if orario['aperto'] else None,
                orario['pomeriggio_fine'] if orario['aperto'] else None,
                session.get('username')
            ))
        
        # Verifica il salvataggio
        cursor.execute('SELECT COUNT(*) FROM orari_accesso')
        count = cursor.fetchone()[0]
        
        if count != len(data['orari']):
            print(f"Errore verifica salvataggio orari: attesi={len(data['orari'])}, salvati={count}")
            conn.rollback()
            return jsonify({'success': False, 'error': 'Errore verifica salvataggio'}), 500
            
        print(f"Orari salvati correttamente: {count} record")
        conn.commit()
        return jsonify({'success': True, 'message': 'Orari salvati'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@configurazione_accessi_bp.route('/api/configurazione/limiti', methods=['GET'])
@require_auth()
def get_limiti():
    """Ottiene limiti accessi"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        # Seleziona il record più recente basato su updated_at
        cursor.execute('''
            SELECT max_ingressi_mensili, updated_at, updated_by 
            FROM limiti_accesso 
            ORDER BY updated_at DESC 
            LIMIT 1
        ''')
        row = cursor.fetchone()
        
        if row:
            print(f"Lettura limite accessi: valore={row[0]}, aggiornato_il={row[1]}, da={row[2]}")
        else:
            print("Nessun limite accessi configurato, uso default=3")
        
        return jsonify({
            'success': True,
            'max_ingressi_mensili': row[0] if row else 3,
            'last_update': row[1] if row else None
        })
        
    except Exception as e:
        print(f"Errore lettura limite accessi: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@configurazione_accessi_bp.route('/api/configurazione/limiti', methods=['POST'])
@require_auth()
@require_permission('all')
def save_limiti():
    """Salva limiti accessi"""
    # Verifica sessione
    if not session.get('username'):
        return jsonify({'success': False, 'error': 'Sessione non valida'}), 401
        
    data = request.get_json()
    if not data or 'max_ingressi_mensili' not in data:
        return jsonify({'success': False, 'error': 'Dati mancanti'}), 400
    
    nuovo_valore = data['max_ingressi_mensili']
    print(f"Richiesta salvataggio limite accessi: nuovo_valore={nuovo_valore}")
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Leggi valore attuale
        cursor.execute('SELECT max_ingressi_mensili FROM limiti_accesso ORDER BY updated_at DESC LIMIT 1')
        row = cursor.fetchone()
        valore_attuale = row[0] if row else None
        print(f"Valore attuale limite accessi: {valore_attuale}")
        
        # Elimina tutti i record esistenti
        cursor.execute('DELETE FROM limiti_accesso')
        
        # Inserisci nuovo record
        cursor.execute('''
            INSERT INTO limiti_accesso (max_ingressi_mensili, updated_by, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (nuovo_valore, session.get('username')))
        
        # Verifica il salvataggio
        cursor.execute('''
            SELECT max_ingressi_mensili, updated_at, updated_by 
            FROM limiti_accesso 
            ORDER BY updated_at DESC 
            LIMIT 1
        ''')
        saved = cursor.fetchone()
        
        if not saved or saved[0] != nuovo_valore:
            print(f"Errore verifica salvataggio: atteso={nuovo_valore}, trovato={saved[0] if saved else None}")
            conn.rollback()
            return jsonify({'success': False, 'error': 'Errore verifica salvataggio'}), 500
        
        print(f"Limite accessi salvato: valore={saved[0]}, aggiornato_il={saved[1]}, da={saved[2]}")
        conn.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Limite salvato correttamente',
            'value': saved[0],
            'updated_at': saved[1]
        })
        
    except Exception as e:
        print(f"Errore salvataggio limite accessi: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

def verifica_orario() -> bool:
    """Verifica se l'orario attuale è valido per l'accesso"""
    ora_sistema = datetime.now()
    ora_roma = datetime.now(ROME_TZ)
    print(f"Ora sistema: {ora_sistema}, Ora Roma: {ora_roma}")
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Usa SEMPRE ora_roma per tutte le verifiche
        # Questo garantisce coerenza indipendentemente dalle impostazioni di sistema
        
        # Ottieni giorno della settimana (weekday: 0=Lunedì -> 6=Domenica)
        giorni = ['Lunedi', 'Martedi', 'Mercoledi', 'Giovedi', 'Venerdi', 'Sabato', 'Domenica']
        giorno_attuale = giorni[ora_roma.weekday()]
        ora_attuale = ora_roma.time()
        
        print(f"\nVerifica accesso:")
        print(f"Giorno: {giorno_attuale}")
        print(f"Ora: {ora_attuale}")
        
        # Ottieni orari per il giorno
        cursor.execute('SELECT * FROM orari_accesso WHERE giorno = ?', (giorno_attuale,))
        orario = cursor.fetchone()
        
        # Verifica se il giorno è configurato e attivo
        if not orario:
            print("Giorno non configurato")
            return False
            
        if not orario[1]:  # not aperto
            print("Giorno non attivo")
            return False
        
        # Converti stringhe in oggetti time
        try:
            mattina_inizio = datetime.strptime(orario[2], '%H:%M').time() if orario[2] else None
            mattina_fine = datetime.strptime(orario[3], '%H:%M').time() if orario[3] else None
            pomeriggio_inizio = datetime.strptime(orario[4], '%H:%M').time() if orario[4] else None
            pomeriggio_fine = datetime.strptime(orario[5], '%H:%M').time() if orario[5] else None
            
            print("\nOrari configurati:")
            if mattina_inizio and mattina_fine:
                print(f"Mattina: {mattina_inizio}-{mattina_fine}")
            if pomeriggio_inizio and pomeriggio_fine:
                print(f"Pomeriggio: {pomeriggio_inizio}-{pomeriggio_fine}")
                
        except ValueError as e:
            print(f"Errore conversione orari: {e}")
            return False
        
        # Verifica se ora attuale è in uno dei range
        in_mattina = False
        in_pomeriggio = False
        
        if mattina_inizio and mattina_fine:
            # Converti ora_attuale in minuti per confronto più semplice
            ora_attuale_minuti = ora_attuale.hour * 60 + ora_attuale.minute
            mattina_inizio_minuti = mattina_inizio.hour * 60 + mattina_inizio.minute
            mattina_fine_minuti = mattina_fine.hour * 60 + mattina_fine.minute
            
            # Se l'intervallo attraversa la mezzanotte (es. 23:00-01:00)
            if mattina_inizio_minuti > mattina_fine_minuti:
                in_mattina = ora_attuale_minuti >= mattina_inizio_minuti or ora_attuale_minuti <= mattina_fine_minuti
            else:
                in_mattina = mattina_inizio_minuti <= ora_attuale_minuti <= mattina_fine_minuti
            print(f"Verifica mattina: {mattina_inizio}-{mattina_fine} -> {in_mattina}")
            
        if pomeriggio_inizio and pomeriggio_fine:
            # Converti ora_attuale in minuti per confronto più semplice
            ora_attuale_minuti = ora_attuale.hour * 60 + ora_attuale.minute
            pomeriggio_inizio_minuti = pomeriggio_inizio.hour * 60 + pomeriggio_inizio.minute
            pomeriggio_fine_minuti = pomeriggio_fine.hour * 60 + pomeriggio_fine.minute
            
            # Se l'intervallo attraversa la mezzanotte (es. 23:00-01:00)
            if pomeriggio_inizio_minuti > pomeriggio_fine_minuti:
                in_pomeriggio = ora_attuale_minuti >= pomeriggio_inizio_minuti or ora_attuale_minuti <= pomeriggio_fine_minuti
            else:
                in_pomeriggio = pomeriggio_inizio_minuti <= ora_attuale_minuti <= pomeriggio_fine_minuti
            print(f"Verifica pomeriggio: {pomeriggio_inizio}-{pomeriggio_fine} -> {in_pomeriggio}")
        
        accesso_consentito = in_mattina or in_pomeriggio
        print(f"\nAccesso consentito: {accesso_consentito}")
        
        return accesso_consentito
        
    except Exception as e:
        print(f"Errore verifica orario: {e}")
        return False
    finally:
        conn.close()

def verifica_limite_mensile(codice_fiscale: str) -> bool:
    """Verifica se l'utente ha superato il limite mensile di accessi"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Ottieni limite configurato
        cursor.execute('SELECT max_ingressi_mensili FROM limiti_accesso ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        limite = row[0] if row else 3
        
        # Ottieni anno e mese correnti
        oggi = datetime.now()
        
        # Conta accessi del mese corrente dalla tabella conteggio_ingressi_mensili
        cursor.execute('''
            SELECT numero_ingressi FROM conteggio_ingressi_mensili 
            WHERE codice_fiscale = ? AND mese = ? AND anno = ?
        ''', (codice_fiscale, oggi.month, oggi.year))
        
        row = cursor.fetchone()
        accessi = row[0] if row else 0
        return accessi < limite
        
    except Exception as e:
        print(f"Errore verifica limite mensile: {e}")
        return False
    finally:
        conn.close()

def log_forzatura(tipo: str, utente: str, dettagli: str = None):
    """Registra una forzatura nel log"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO log_forzature (tipo, utente, dettagli)
            VALUES (?, ?, ?)
        ''', (tipo, utente, dettagli))
        conn.commit()
    except Exception as e:
        print(f"Errore log forzatura: {e}")
    finally:
        conn.close()

@configurazione_accessi_bp.route('/api/utenti-autorizzati/disattivati', methods=['GET'])
@require_auth()
def get_utenti_disattivati():
    """Ottiene lista utenti disattivati per limite ingressi"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Ottieni anno e mese correnti
        oggi = datetime.now()
        anno = oggi.year
        mese = oggi.month
        
        # Query per ottenere utenti disattivati
        cursor.execute('''
            SELECT u.codice_fiscale, u.nome, c.numero_ingressi as ingressi_mensili
            FROM utenti_autorizzati u
            JOIN conteggio_ingressi_mensili c 
                ON u.codice_fiscale = c.codice_fiscale
            WHERE c.anno = ? AND c.mese = ?
            AND u.attivo = 0
        ''', (anno, mese))
        
        utenti = []
        for row in cursor.fetchall():
            utenti.append({
                'codice_fiscale': row[0],
                'nome': row[1],
                'ingressi_mensili': row[2]
            })
        
        return jsonify({'success': True, 'utenti': utenti})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@configurazione_accessi_bp.route('/api/configurazione/test/set-ingressi', methods=['POST'])
@require_auth()
@require_permission('all')
def set_ingressi():
    """Imposta manualmente il numero di ingressi per un utente"""
    data = request.get_json()
    if not data or 'codice_fiscale' not in data or 'ingressi' not in data:
        return jsonify({'success': False, 'error': 'Dati mancanti'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        oggi = datetime.now()
        
        # Verifica esistenza utente
        cursor.execute('SELECT id FROM utenti_autorizzati WHERE codice_fiscale = ?', 
                      (data['codice_fiscale'],))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Utente non trovato'}), 404
        
        # Aggiorna o inserisci conteggio
        cursor.execute('''
            INSERT OR REPLACE INTO conteggio_ingressi_mensili 
            (codice_fiscale, mese, anno, numero_ingressi, ultimo_ingresso)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (data['codice_fiscale'], oggi.month, oggi.year, data['ingressi']))
        
        # Ottieni limite configurato
        cursor.execute('SELECT max_ingressi_mensili FROM limiti_accesso ORDER BY id DESC LIMIT 1')
        limite = cursor.fetchone()[0]
        
        # Aggiorna stato utente
        cursor.execute('''
            UPDATE utenti_autorizzati 
            SET attivo = ?
            WHERE codice_fiscale = ?
        ''', (1 if data['ingressi'] < limite else 0, data['codice_fiscale']))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Conteggio aggiornato'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@configurazione_accessi_bp.route('/api/configurazione/test/simula-accesso', methods=['POST'])
@require_auth()
@require_permission('all')
def simula_accesso():
    """Simula un tentativo di accesso come se fosse una lettura reale da Omnikey"""
    data = request.get_json()
    if not data or 'codice_fiscale' not in data:
        return jsonify({'success': False, 'error': 'Codice fiscale mancante'}), 400
    
    # Simula lettura da Omnikey usando CardReader
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from hardware.card_reader import CardReader
    from hardware.usb_rly08_controller import USBRLY08Controller
    
    # Verifica orario prima di tutto
    if not verifica_orario():
        return jsonify({
            'success': False, 
            'error': 'Accesso non consentito in questo orario'
        }), 403
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        oggi = datetime.now()
        
        # Verifica utente
        cursor.execute('''
            SELECT attivo 
            FROM utenti_autorizzati 
            WHERE codice_fiscale = ?
        ''', (data['codice_fiscale'],))
        row = cursor.fetchone()
        if not row:
            return jsonify({'success': False, 'error': 'Utente non trovato'}), 404
        if not row[0]:
            return jsonify({'success': False, 'error': 'Utente disattivato'}), 403
        
        # Verifica limite mensile
        cursor.execute('SELECT max_ingressi_mensili FROM limiti_accesso ORDER BY id DESC LIMIT 1')
        limite = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT numero_ingressi 
            FROM conteggio_ingressi_mensili
            WHERE codice_fiscale = ? AND mese = ? AND anno = ?
        ''', (data['codice_fiscale'], oggi.month, oggi.year))
        row = cursor.fetchone()
        ingressi_attuali = row[0] if row else 0
        
        if ingressi_attuali >= limite:
            # Disattiva utente
            cursor.execute('''
                UPDATE utenti_autorizzati 
                SET attivo = 0
                WHERE codice_fiscale = ?
            ''', (data['codice_fiscale'],))
            conn.commit()
            
            return jsonify({
                'success': False,
                'error': f'Limite mensile di {limite} ingressi raggiunto'
            }), 403
        
        # Incrementa contatore
        cursor.execute('''
            INSERT OR REPLACE INTO conteggio_ingressi_mensili 
            (codice_fiscale, mese, anno, numero_ingressi, ultimo_ingresso)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (data['codice_fiscale'], oggi.month, oggi.year, ingressi_attuali + 1))
        
        # Registra accesso con dettagli simulazione
        cursor.execute('''
            INSERT INTO log_accessi 
            (timestamp, codice_fiscale, autorizzato, metodo_lettura, qualita_lettura, tipo_accesso)
            VALUES (CURRENT_TIMESTAMP, ?, 1, 'OMNIKEY_5427_G2', 100, 'simulazione')
        ''', (data['codice_fiscale'],))
        
        conn.commit()
        
        # Simula lettura tessera
        reader = CardReader()
        reader.last_cf = data['codice_fiscale']  # Simula lettura
        
        # Sollecita il relè come nella lettura reale
        controller = USBRLY08Controller()
        if controller.connect():
            # Segnala accesso autorizzato (LED Verde + Buzzer)
            controller.access_granted()
            
            # Apri cancello (disattiva blocco magnetico, attiva motore, riattiva blocco)
            controller.open_gate(8.0)  # 8 secondi
            
            controller.disconnect()
        
        return jsonify({
            'success': True,
            'message': f'Accesso autorizzato (ingresso {ingressi_attuali + 1}/{limite})',
            'details': {
                'lettore': 'OMNIKEY 5427 G2',
                'qualita_lettura': '100%',
                'apertura_rele': '8 secondi'
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@configurazione_accessi_bp.route('/api/configurazione/test/reset-contatore', methods=['POST'])
@require_auth()
@require_permission('all')
def reset_contatore():
    """Reset manuale contatore accessi mensili per un utente"""
    data = request.get_json()
    if not data or 'codice_fiscale' not in data:
        return jsonify({'success': False, 'error': 'Codice fiscale mancante'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        oggi = datetime.now()
        
        # Verifica esistenza utente
        cursor.execute('SELECT id FROM utenti_autorizzati WHERE codice_fiscale = ?', 
                      (data['codice_fiscale'],))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Utente non trovato'}), 404
        
        # Archivia conteggio corrente
        cursor.execute('''
            INSERT INTO conteggio_ingressi_mensili_archive
            (codice_fiscale, mese, anno, numero_ingressi, ultimo_ingresso, data_archiviazione)
            SELECT codice_fiscale, mese, anno, numero_ingressi, ultimo_ingresso, CURRENT_TIMESTAMP
            FROM conteggio_ingressi_mensili
            WHERE codice_fiscale = ? AND mese = ? AND anno = ?
        ''', (data['codice_fiscale'], oggi.year, oggi.month))
        
        # Resetta conteggio
        cursor.execute('''
            DELETE FROM conteggio_ingressi_mensili 
            WHERE codice_fiscale = ? AND anno = ? AND mese = ?
        ''', (data['codice_fiscale'], oggi.year, oggi.month))
        
        # Riattiva utente
        cursor.execute('''
            UPDATE utenti_autorizzati 
            SET attivo = 1
            WHERE codice_fiscale = ?
        ''', (data['codice_fiscale'],))
        
        # Log forzatura
        log_forzatura(
            'RESET_CONTATORE',
            session.get('username'),
            f"Reset contatore per CF: {data['codice_fiscale']}"
        )
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Contatore resettato e utente riattivato'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@configurazione_accessi_bp.route('/api/configurazione/test/apri-cancello', methods=['POST'])
@require_auth()
@require_permission('all')
def apri_cancello_forzato():
    """Apertura forzata cancello fuori orario"""
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from hardware.usb_rly08_controller import USBRLY08Controller
    
    if verifica_orario():
        return jsonify({'success': False, 'error': 'Cancello già apribile in orario normale'}), 400
    
    try:
        controller = USBRLY08Controller()
        if not controller.connect():
            return jsonify({'success': False, 'error': 'Impossibile connettersi al controller'}), 500
        
        # Apri cancello
        controller.open_gate(8.0)  # 8 secondi
        
        # Log forzatura
        log_forzatura(
            'APERTURA_FORZATA',
            session.get('username'),
            'Apertura cancello fuori orario'
        )
        
        return jsonify({'success': True, 'message': 'Cancello aperto'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'controller' in locals():
            controller.disconnect()

@configurazione_accessi_bp.route('/api/configurazione/log-forzature', methods=['GET'])
@require_auth()
@require_permission('all')
def get_log_forzature():
    """Ottiene log delle forzature"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT tipo, utente, timestamp, dettagli
            FROM log_forzature
            ORDER BY timestamp DESC
            LIMIT 100
        ''')
        
        log = []
        for row in cursor.fetchall():
            log.append({
                'tipo': row[0],
                'utente': row[1],
                'timestamp': row[2],
                'dettagli': row[3]
            })
        
        return jsonify({'success': True, 'log': log})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()
