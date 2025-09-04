# File: /opt/access_control/src/api/modules/utenti_autorizzati.py
from flask import Blueprint, render_template_string, request, jsonify, session
from functools import wraps
import sqlite3
import os
from datetime import datetime

# Import auth per i decoratori
from ..utils import require_auth, require_permission

utenti_autorizzati_bp = Blueprint('utenti_autorizzati', __name__)

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'access.db')

def get_db_connection():
    """Connessione al database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Errore connessione DB: {e}")
        return None

@utenti_autorizzati_bp.route('/utenti-autorizzati')
@require_auth()
def utenti_autorizzati_page():
    """Pagina gestione utenti autorizzati"""
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 
              'templates', 'utenti_autorizzati.html'), 'r') as f:
        template = f.read()
    return render_template_string(template, session=session)

@utenti_autorizzati_bp.route('/api/utenti-autorizzati/list')
@require_auth()
def api_list_utenti_autorizzati():
    """Lista utenti autorizzati con filtro"""
    search = request.args.get('search', '').strip().upper()
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Query base
        query = """
            SELECT codice_fiscale, nome, data_inserimento,
                   data_aggiornamento, attivo, note,
                   creato_da, modificato_da
            FROM utenti_autorizzati
            WHERE 1=1
        """
        params = []
        
        # Aggiungi filtro di ricerca se presente
        if search:
            query += """
                AND (
                    UPPER(codice_fiscale) LIKE ? OR
                    UPPER(nome) LIKE ?
                )
            """
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
        
        # Ordina per nome
        query += " ORDER BY nome"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        utenti = []
        for row in results:
            utenti.append({
                'codice_fiscale': row['codice_fiscale'],
                'nome': row['nome'],
                'data_inserimento': row['data_inserimento'],
                'data_aggiornamento': row['data_aggiornamento'],
                'attivo': bool(row['attivo']),
                'note': row['note'],
                'creato_da': row['creato_da'],
                'modificato_da': row['modificato_da']
            })
        
        return jsonify({
            'success': True,
            'utenti': utenti,
            'total': len(utenti)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@utenti_autorizzati_bp.route('/api/utenti-autorizzati/toggle-active', methods=['POST'])
@require_auth()
@require_permission('all')
def api_toggle_active():
    """Attiva/disattiva utente autorizzato"""
    data = request.get_json()
    codice_fiscale = data.get('codice_fiscale', '').strip()
    
    if not codice_fiscale:
        return jsonify({'success': False, 'error': 'Codice fiscale mancante'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Ottieni stato attuale
        cursor.execute("""
            SELECT attivo 
            FROM utenti_autorizzati 
            WHERE codice_fiscale = ?
        """, (codice_fiscale,))
        
        result = cursor.fetchone()
        if not result:
            return jsonify({'success': False, 'error': 'Utente non trovato'}), 404
        
        # Inverte lo stato
        new_state = not bool(result['attivo'])
        
        # Aggiorna
        cursor.execute("""
            UPDATE utenti_autorizzati 
            SET attivo = ?,
                data_aggiornamento = CURRENT_TIMESTAMP,
                modificato_da = ?
            WHERE codice_fiscale = ?
        """, (int(new_state), session.get('username'), codice_fiscale))
        
        conn.commit()
        
        status = "attivato" if new_state else "disattivato"
        return jsonify({
            'success': True,
            'message': f'Utente {status}',
            'new_state': new_state
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@utenti_autorizzati_bp.route('/api/utenti-autorizzati')
@require_auth()
def get_utenti():
    """Ottiene lista completa utenti autorizzati"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT codice_fiscale, nome
            FROM utenti_autorizzati
            WHERE attivo = 1
            ORDER BY nome
        ''')
        
        utenti = []
        for row in cursor.fetchall():
            utenti.append({
                'codice_fiscale': row['codice_fiscale'],
                'nome': row['nome'],
                'label': f"{row['nome']} ({row['codice_fiscale']})"
            })
        
        return jsonify({'success': True, 'utenti': utenti})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@utenti_autorizzati_bp.route('/api/utenti-autorizzati/disattivati')
@require_auth()
def get_utenti_disattivati():
    """Ottiene lista utenti disattivati"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Ottieni anno e mese correnti
        oggi = datetime.now()
        anno = oggi.year
        mese = oggi.month
        
        # Query per ottenere utenti disattivati con conteggio ingressi
        cursor.execute('''
            SELECT u.nome, u.codice_fiscale,
                   COALESCE(c.numero_ingressi, 0) as ingressi_mensili
            FROM utenti_autorizzati u
            LEFT JOIN conteggio_ingressi_mensili c 
                ON u.codice_fiscale = c.codice_fiscale
                AND c.anno = ? AND c.mese = ?
            WHERE u.attivo = 0
            ORDER BY u.nome
        ''', (anno, mese))
        
        utenti = []
        for row in cursor.fetchall():
            utenti.append({
                'nome': row['nome'],
                'codice_fiscale': row['codice_fiscale'],
                'ingressi_mensili': row['ingressi_mensili']
            })
        
        return jsonify({'success': True, 'utenti': utenti})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@utenti_autorizzati_bp.route('/api/utenti-autorizzati/stats')
@require_auth()
def api_get_stats():
    """Statistiche utenti autorizzati"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Totale utenti
        cursor.execute("SELECT COUNT(*) as total FROM utenti_autorizzati")
        total = cursor.fetchone()['total']
        
        # Utenti attivi
        cursor.execute("SELECT COUNT(*) as active FROM utenti_autorizzati WHERE attivo = 1")
        active = cursor.fetchone()['active']
        
        
        # Ultimi inseriti
        cursor.execute("""
            SELECT COUNT(*) as recent
            FROM utenti_autorizzati
            WHERE data_inserimento >= date('now', '-30 days')
        """)
        recent = cursor.fetchone()['recent']
        
        return jsonify({
            'success': True,
            'stats': {
                'totale': total,
                'attivi': active,
                'nuovi_30gg': recent
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()
