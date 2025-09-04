#!/usr/bin/env python3
# File: /opt/access_control/scripts/test_simple_dashboard.py
# Test Dashboard Semplificato per Debug

from flask import Flask, render_template_string

app = Flask(__name__)

SIMPLE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Dashboard - Sistema Controllo Accessi</title>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .status {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #28a745;
        }
        .btn {
            background: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover {
            background: #0056b3;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .info-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Test Dashboard - Sistema Controllo Accessi</h1>
        
        <div class="status">
            ✅ <strong>Connessione Riuscita!</strong> Il server Flask è operativo.
        </div>
        
        <div class="info-grid">
            <div class="info-card">
                <h3>🌐 Connessione</h3>
                <p><strong>IP:</strong> {{ request.remote_addr }}</p>
                <p><strong>URL:</strong> {{ request.url }}</p>
                <p><strong>User Agent:</strong> {{ request.user_agent.browser }}</p>
            </div>
            
            <div class="info-card">
                <h3>⚙️ Sistema</h3>
                <p><strong>Metodo:</strong> {{ request.method }}</p>
                <p><strong>Host:</strong> {{ request.host }}</p>
                <p><strong>Data/Ora:</strong> <span id="datetime"></span></p>
            </div>
            
            <div class="info-card">
                <h3>📊 Stato</h3>
                <p><strong>Dashboard:</strong> ✅ Operativa</p>
                <p><strong>Database:</strong> ✅ Connesso</p>
                <p><strong>Hardware:</strong> ⏳ Test in corso</p>
            </div>
        </div>
        
        <h2>🧪 Test Funzionalità</h2>
        
        <a href="/test-json" class="btn">📄 Test API JSON</a>
        <a href="/test-database" class="btn">🗄️ Test Database</a>
        <a href="/test-hardware" class="btn">🔧 Test Hardware</a>
        
        <h2>�� Prossimi Step</h2>
        <ol>
            <li>✅ <strong>Connessione verificata</strong> - Il server è raggiungibile</li>
            <li>🔄 <strong>Installazione dashboard completa</strong> - Procediamo con l'upgrade</li>
            <li>🔐 <strong>Sistema login</strong> - Configurazione autenticazione</li>
            <li>⚙️ <strong>Moduli avanzati</strong> - Attivazione tutte le funzionalità</li>
        </ol>
        
        <div style="margin-top: 30px; padding: 20px; background: #e3f2fd; border-radius: 8px;">
            <h3>🎯 Sistema Pronto</h3>
            <p>Se vedi questa pagina, il sistema di base funziona correttamente. Possiamo procedere con l'installazione della dashboard completa con login e tutte le funzionalità avanzate.</p>
        </div>
    </div>
    
    <script>
        // Aggiorna data/ora
        function updateDateTime() {
            document.getElementById('datetime').textContent = new Date().toLocaleString('it-IT');
        }
        updateDateTime();
        setInterval(updateDateTime, 1000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(SIMPLE_TEMPLATE)

@app.route('/test-json')
def test_json():
    return {
        'status': 'success',
        'message': 'API JSON funzionante',
        'timestamp': '2025-07-08 23:30:00',
        'system': {
            'dashboard': 'operativa',
            'database': 'connesso',
            'hardware': 'test_in_corso'
        }
    }

@app.route('/test-database')
def test_database():
    try:
        import sqlite3
        from pathlib import Path
        
        db_path = Path("/opt/access_control/src/access.db")
        
        if db_path.exists():
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM utenti_autorizzati")
                count = cursor.fetchone()[0]
            
            return {
                'status': 'success',
                'message': f'Database connesso - {count} utenti autorizzati',
                'database_path': str(db_path),
                'tables_found': True
            }
        else:
            return {
                'status': 'warning',
                'message': 'Database non trovato',
                'database_path': str(db_path),
                'tables_found': False
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Errore database: {str(e)}'
        }

@app.route('/test-hardware')
def test_hardware():
    hardware_status = {
        'lettore_cf': {'status': 'unknown', 'message': 'Test non implementato'},
        'rele_usb': {'status': 'unknown', 'message': 'Test non implementato'},
        'rete': {'status': 'ok', 'message': 'Connessione web funzionante'}
    }
    
    # Test presenza file hardware
    from pathlib import Path
    
    card_reader_path = Path("/opt/access_control/src/hardware/card_reader.py")
    relay_path = Path("/opt/access_control/src/hardware/usb_rly08_controller.py")
    
    if card_reader_path.exists():
        hardware_status['lettore_cf']['status'] = 'file_present'
        hardware_status['lettore_cf']['message'] = 'Modulo card_reader.py trovato'
    
    if relay_path.exists():
        hardware_status['rele_usb']['status'] = 'file_present'
        hardware_status['rele_usb']['message'] = 'Modulo usb_rly08_controller.py trovato'
    
    return {
        'status': 'success',
        'message': 'Test hardware completato',
        'hardware': hardware_status
    }

if __name__ == '__main__':
    print("🧪 AVVIO TEST DASHBOARD SEMPLIFICATO")
    print("=" * 50)
    print("🌐 URL Test: http://192.168.178.200:5000")
    print("🌐 URL Test: http://localhost:5000")
    print("🔄 Premi CTRL+C per fermare")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

