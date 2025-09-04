# File: /opt/access_control/src/api/modules/log_management.py
# Gestione log con export Excel - FIXED IMPORTS

from flask import Blueprint, request, jsonify, send_file, session
import sqlite3
import pandas as pd
import io
from datetime import datetime, timedelta
import os

log_management_bp = Blueprint('log_management', __name__)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'access.db')

def get_db_connection():
    """Connessione database locale"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Errore connessione DB: {e}")
        return None

def require_permission(*required_permissions):
    """Decorator per verificare permessi - versione locale"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if 'username' not in session:
                return jsonify({'error': 'Login richiesto'}), 401
                
            user_role = session.get('role', 'viewer')
            # Verifica permessi base per log
            if user_role in ['admin', 'user_manager', 'viewer']:
                return f(*args, **kwargs)
            else:
                return jsonify({'error': 'Permessi insufficienti'}), 403
        
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@log_management_bp.route('/api/logs/search')
@require_permission('view_logs')
def search_logs():
    """Ricerca log con filtri"""
    # Parametri filtro
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    status = request.args.get('status')  # 'all', 'authorized', 'denied'
    search_text = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database non disponibile'}), 500
    
    try:
        # Query base
        query = """
            SELECT 
                la.timestamp,
                la.codice_fiscale,
                la.autorizzato,
                COALESCE(ua.nome, 'Sconosciuto') as nome_completo,
                ua.comune,
                la.durata_elaborazione,
                la.terminale_id
            FROM log_accessi la
            LEFT JOIN utenti_autorizzati ua ON la.codice_fiscale = ua.codice_fiscale
            WHERE 1=1
        """
        params = []
        
        # Applica filtri
        if date_from:
            query += " AND DATE(la.timestamp) >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND DATE(la.timestamp) <= ?"
            params.append(date_to)
        
        if status == 'authorized':
            query += " AND la.autorizzato = 1"
        elif status == 'denied':
            query += " AND la.autorizzato = 0"
        
        if search_text:
            query += " AND (la.codice_fiscale LIKE ? OR ua.nome LIKE ?)"
            search_param = f"%{search_text}%"
            params.extend([search_param, search_param])
        
        # Conta totale per paginazione
        count_query = f"SELECT COUNT(*) FROM ({query}) as filtered"
        cursor = conn.cursor()
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Aggiungi paginazione
        query += " ORDER BY la.timestamp DESC LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])
        
        # Esegui query
        cursor.execute(query, params)
        logs = []
        
        for row in cursor.fetchall():
            logs.append({
                'timestamp': row[0],
                'codice_fiscale': row[1],
                'autorizzato': bool(row[2]),
                'nome_completo': row[3],
                'comune': row[4] or 'N/D',
                'durata_elaborazione': row[5],
                'terminale_id': row[6]
            })
        
        return jsonify({
            'success': True,
            'logs': logs,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': (total_count + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@log_management_bp.route('/api/logs/export')
@require_permission('export_logs')
def export_logs():
    """Export log in Excel"""
    # Stessi filtri della ricerca
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    status = request.args.get('status')
    search_text = request.args.get('search', '')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database non disponibile'}), 500
    
    try:
        # Query senza paginazione per export
        query = """
            SELECT 
                la.timestamp as 'Data/Ora',
                la.codice_fiscale as 'Codice Fiscale',
                CASE WHEN la.autorizzato = 1 THEN 'Autorizzato' ELSE 'Negato' END as 'Stato',
                COALESCE(ua.nome, 'Sconosciuto') as 'Nome Completo',
                COALESCE(ua.comune, 'N/D') as 'Comune',
                COALESCE(la.durata_elaborazione, 0) as 'Tempo Elaborazione (ms)',
                COALESCE(la.terminale_id, 'N/D') as 'Terminale'
            FROM log_accessi la
            LEFT JOIN utenti_autorizzati ua ON la.codice_fiscale = ua.codice_fiscale
            WHERE 1=1
        """
        params = []
        
        # Applica stessi filtri
        if date_from:
            query += " AND DATE(la.timestamp) >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND DATE(la.timestamp) <= ?"
            params.append(date_to)
        
        if status == 'authorized':
            query += " AND la.autorizzato = 1"
        elif status == 'denied':
            query += " AND la.autorizzato = 0"
        
        if search_text:
            query += " AND (la.codice_fiscale LIKE ? OR ua.nome LIKE ?)"
            search_param = f"%{search_text}%"
            params.extend([search_param, search_param])
        
        query += " ORDER BY la.timestamp DESC"
        
        # Crea DataFrame
        df = pd.read_sql_query(query, conn, params=params)
        
        # Formatta date
        df['Data/Ora'] = pd.to_datetime(df['Data/Ora']).dt.strftime('%d/%m/%Y %H:%M:%S')
        
        # Crea Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Log Accessi', index=False)
            
            # Formatta colonne
            worksheet = writer.sheets['Log Accessi']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        filename = f"log_accessi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@log_management_bp.route('/api/logs/stats')
@require_permission('view_logs')
def get_log_stats():
    """Statistiche log per periodo"""
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database non disponibile'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Query statistiche
        query = """
            SELECT 
                COUNT(*) as totale,
                SUM(CASE WHEN autorizzato = 1 THEN 1 ELSE 0 END) as autorizzati,
                SUM(CASE WHEN autorizzato = 0 THEN 1 ELSE 0 END) as negati,
                AVG(durata_elaborazione) as tempo_medio
            FROM log_accessi
            WHERE 1=1
        """
        params = []
        
        if date_from:
            query += " AND DATE(timestamp) >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND DATE(timestamp) <= ?"
            params.append(date_to)
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        
        stats = {
            'totale': result[0] or 0,
            'autorizzati': result[1] or 0,
            'negati': result[2] or 0,
            'tempo_medio': round(result[3] or 0, 2),
            'tasso_successo': 0
        }
        
        if stats['totale'] > 0:
            stats['tasso_successo'] = round((stats['autorizzati'] / stats['totale']) * 100, 1)
        
        return jsonify({'success': True, 'stats': stats})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
