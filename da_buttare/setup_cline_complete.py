#!/usr/bin/env python3
"""
Setup completo Cline per progetto access_control
Basato sulla struttura reale del progetto
"""

import os
import json
import shutil
from datetime import datetime
import sqlite3

def setup_cline_complete():
    print("🚀 Setup Cline per access_control\n")
    
    # 1. Pulisci vecchia configurazione se esiste
    if os.path.exists('.clinerules'):
        print("⚠️  Trovata vecchia cartella .clinerules")
        response = input("Vuoi fare backup? (s/n): ")
        if response.lower() == 's':
            backup_name = f".clinerules_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.move('.clinerules', backup_name)
            print(f"✅ Backup creato: {backup_name}")
    
    # 2. Crea struttura .clinerules
    print("\n1️⃣ Creazione struttura .clinerules...")
    os.makedirs('.clinerules', exist_ok=True)
    os.makedirs('clinerules-bank/tasks', exist_ok=True)
    os.makedirs('clinerules-bank/features', exist_ok=True)
    
    # 3. Crea file 01-project-rules.md
    print("2️⃣ Creazione regole progetto...")
    project_rules = """# REGOLE PROGETTO ACCESS_CONTROL

## 🚨 PRIMA DI OGNI TASK
SEMPRE leggere questi file in ordine:
1. `.clinerules/01-project-rules.md` (questo file)
2. `.clinerules/02-memory.md` (struttura progetto)
3. `.clinerules/03-database.md` (schema database)

## 📋 REGOLE TASSATIVE (OBBLIGATORIE)

### 1. METODOLOGIA DI LAVORO
- ✅ Procedere SEMPRE passo passo
- ✅ Un task alla volta, completarlo prima del successivo
- ✅ MAI modificare più di quello richiesto
- ✅ FOCUS esclusivo sul task corrente

### 2. INTEGRAZIONE CODICE
- ✅ Modificare ESCLUSIVAMENTE i file richiesti nel task
- ✅ NON toccare altri file senza esplicita richiesta
- ✅ Mantenere la modularità Flask Blueprint
- ✅ Rispettare pattern e convenzioni esistenti

### 3. DATABASE - REGOLA CRITICA ⚠️
- `utenti_sistema` = SOLO per login amministratori dashboard
- `utenti_autorizzati` = SOLO per accesso fisico con tessera
- MAI mescolare i due sistemi di autenticazione
- Database path: `/opt/access_control/src/access.db`

### 4. STILE E CONSISTENZA
- ✅ Coerenza totale con codice esistente
- ✅ Indentazione: 4 spazi (Python)
- ✅ Naming: snake_case per Python, kebab-case per file HTML/CSS
- ✅ Response JSON sempre: `{success: bool, message: str, data: any}`

### 5. GESTIONE FILE
- ✅ File obsoleti → SEMPRE in `da_buttare/` con log
- ✅ Log delle modifiche in: `cleanup_log_[timestamp].txt`
- ✅ MAI eliminare file direttamente
- ✅ Backup prima di modifiche importanti

### 6. COMUNICAZIONE
- ✅ Risposte SEMPRE in italiano
- ✅ Percorsi SEMPRE completi: `/opt/access_control/...`
- ✅ Spiegare ogni modifica fatta
- ✅ Confermare completamento task

## 🛠️ WORKFLOW CORRETTO

1. **Analizza** la richiesta
2. **Identifica** i file da modificare
3. **Proponi** soluzione step-by-step
4. **Attendi** conferma prima di procedere
5. **Implementa** solo le modifiche richieste
6. **Verifica** coerenza con esistente
7. **Documenta** cosa è stato fatto
8. **Cleanup** se necessario (file in da_buttare/)

## ❌ NON FARE MAI
- Modificare file non richiesti
- Rifattorizzare senza permesso esplicito
- Cambiare convenzioni esistenti
- Eliminare file (sempre in da_buttare/)
- Procedere senza conferma
- Mischiare task diversi
- Usare librerie non già presenti in requirements.txt

## ✅ RICORDA SEMPRE
- Progetto in: `/opt/access_control/`
- Entry point: `src/main.py`
- API principale: `src/api/web_api.py`
- Moduli in: `src/api/modules/`
- Log in: `logs/`
- Config in: `config/`
"""
    
    with open('.clinerules/01-project-rules.md', 'w', encoding='utf-8') as f:
        f.write(project_rules)
    
    # 4. Crea file 02-memory.md con struttura reale
    print("3️⃣ Creazione memoria progetto...")
    project_memory = """# MEMORIA PROGETTO ACCESS_CONTROL

## �� STRUTTURA REALE DEL PROGETTO

```
/opt/access_control/
├── src/                    # Codice sorgente principale
│   ├── api/               # API Flask e interfaccia web
│   │   ├── modules/       # Moduli Blueprint
│   │   ├── static/        # File statici (CSS, JS, immagini)
│   │   ├── templates/     # Template HTML aggiuntivi
│   │   ├── utils/         # Utility API
│   │   └── web_api.py     # API principale Flask
│   ├── core/              # Configurazioni core
│   │   └── config.py      # Config manager
│   ├── database/          # Layer database
│   │   └── database_manager.py
│   ├── external/          # Integrazioni esterne
│   │   └── odoo_partner_connector.py
│   ├── hardware/          # Controller hardware
│   │   ├── card_reader.py
│   │   └── usb_rly08_controller.py
│   ├── utils/             # Utility generali
│   ├── access.db          # Database SQLite
│   └── main.py            # Entry point applicazione
├── config/                # Configurazioni
│   ├── admin_config.json
│   ├── base.yml
│   └── dashboard_config.json
├── scripts/               # Script utilità e manutenzione
├── logs/                  # File di log
├── data/                  # Dati applicazione
├── backups/               # Backup automatici
├── tests/                 # Test suite
├── docs/                  # Documentazione
└── da_buttare/            # File obsoleti (non eliminare!)
```

## 🔌 API ENDPOINTS PRINCIPALI

### Autenticazione
- `POST /api/login` - Login utenti_sistema (admin)
- `POST /api/logout` - Logout
- `GET /api/check-auth` - Verifica autenticazione

### Gestione Utenti
- `GET /api/users` - Lista utenti sistema
- `POST /api/users` - Crea utente sistema
- `PUT /api/users/<id>` - Modifica utente sistema
- `DELETE /api/users/<id>` - Elimina utente sistema

### Utenti Autorizzati (Accesso Fisico)
- `GET /api/utenti-autorizzati` - Lista con filtri
- `POST /api/utenti-autorizzati` - Aggiungi utente
- `PUT /api/utenti-autorizzati/<id>` - Modifica
- `DELETE /api/utenti-autorizzati/<id>` - Elimina
- `POST /api/authorize` - Autorizza accesso con tessera

### Hardware
- `POST /api/relay/open` - Apri relè
- `POST /api/relay/close` - Chiudi relè
- `GET /api/relay/status` - Stato relè
- `GET /api/hardware/test` - Test hardware
- `POST /api/test-card-reader` - Test lettore

### Sistema
- `GET /api/logs` - Visualizza log
- `POST /api/backup/create` - Crea backup
- `POST /api/backup/restore` - Ripristina backup
- `GET /api/system/status` - Stato sistema

## 📦 MODULI PRINCIPALI

### src/api/modules/
- `utenti.py` - Gestione utenti sistema
- `utenti_autorizzati.py` - Gestione accesso fisico
- `dispositivi.py` - Gestione dispositivi hardware
- `profilo.py` - Profilo utente corrente
- `log_management.py` - Gestione e visualizzazione log
- `email_log_allerte_sistema.py` - Email e allerte
- `user_management.py` - Utility gestione utenti
- `configurazione_orari.py` - Configurazione orari accesso

### src/api/static/
- `css/` - Stili (dashboard.css, profilo.css, etc.)
- `js/` - JavaScript (dashboard.js, users.js, etc.)
- `html/` - Componenti HTML riutilizzabili

## 🔧 FILE CONFIGURAZIONE
- `config/base.yml` - Config principale applicazione
- `config/admin_config.json` - Config amministrazione
- `config/dashboard_config.json` - Config dashboard
- `.env` - Variabili ambiente (non in git)

## 📝 CONVENZIONI CODICE

### Python
- Indentazione: 4 spazi
- Naming: snake_case
- Docstring per ogni funzione pubblica
- Type hints dove possibile
- Import ordinati (standard, third-party, local)

### JavaScript
- Indentazione: 2 spazi
- Naming: camelCase
- Const/let invece di var
- Arrow function per callback
- Async/await invece di promise chains

### API Response
```python
{
    "success": bool,
    "message": str,
    "data": any,  # optional
    "error": str  # solo se success=False
}
```

## 🔐 AUTENTICAZIONE
- Basata su sessioni Flask
- Login con username/password da tabella `utenti_sistema`
- Decorator `@login_required` per endpoint protetti
- Sessione scade dopo 24 ore di inattività
"""
    
    with open('.clinerules/02-memory.md', 'w', encoding='utf-8') as f:
        f.write(project_memory)
    
    # 5. Crea file 03-database.md
    print("4️⃣ Creazione schema database...")
    
    # Prova a leggere il vero schema dal database
    db_schema_content = """# SCHEMA DATABASE ACCESS_CONTROL

## 📍 POSIZIONE DATABASE
`/opt/access_control/src/access.db`

## 📊 TABELLE PRINCIPALI

### 1. utenti_sistema (LOGIN AMMINISTRATORI)
**Scopo**: Autenticazione amministratori dashboard
```sql
CREATE TABLE utenti_sistema (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,  -- bcrypt hash
    email TEXT,
    ruolo TEXT DEFAULT 'admin',
    attivo INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

### 2. utenti_autorizzati (ACCESSO FISICO)
**Scopo**: Persone autorizzate ad accedere fisicamente
```sql
CREATE TABLE utenti_autorizzati (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cognome TEXT NOT NULL,
    codice_fiscale TEXT UNIQUE,
    numero_tessera TEXT,
    email TEXT,
    telefono TEXT,
    azienda TEXT,
    reparto TEXT,
    attivo INTEGER DEFAULT 1,
    data_registrazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_scadenza DATE,
    note TEXT
);
```

### 3. log_accessi
**Scopo**: Registro di tutti gli accessi
```sql
CREATE TABLE log_accessi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utente_id INTEGER,
    utente_tipo TEXT,  -- 'sistema' o 'autorizzato'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo_accesso TEXT,  -- 'login', 'logout', 'tessera', etc.
    esito TEXT,  -- 'successo', 'fallito'
    dettagli TEXT,
    ip_address TEXT,
    user_agent TEXT
);
```

### 4. dispositivi
**Scopo**: Hardware registrato nel sistema
```sql
CREATE TABLE dispositivi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL,  -- 'lettore_card', 'rele', etc.
    seriale TEXT,
    configurazione TEXT,  -- JSON
    stato TEXT DEFAULT 'attivo',
    data_installazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_manutenzione DATE
);
```

### 5. configurazione_orari
**Scopo**: Fasce orarie di accesso
```sql
CREATE TABLE configurazione_orari (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descrizione TEXT,
    giorni_settimana TEXT,  -- JSON array [1,2,3,4,5]
    ora_inizio TIME,
    ora_fine TIME,
    attivo INTEGER DEFAULT 1
);
```

### 6. utenti_orari
**Scopo**: Associazione utenti-fasce orarie
```sql
CREATE TABLE utenti_orari (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utente_autorizzato_id INTEGER,
    configurazione_orari_id INTEGER,
    FOREIGN KEY(utente_autorizzato_id) REFERENCES utenti_autorizzati(id),
    FOREIGN KEY(configurazione_orari_id) REFERENCES configurazione_orari(id)
);
```

### 7. email_log
**Scopo**: Log email inviate dal sistema
```sql
CREATE TABLE email_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    destinatario TEXT NOT NULL,
    mittente TEXT,
    oggetto TEXT,
    corpo TEXT,
    tipo TEXT,  -- 'alert', 'report', 'notification'
    stato TEXT DEFAULT 'inviato',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    errore TEXT
);
```

### 8. allerte_sistema
**Scopo**: Allerte e notifiche di sistema
```sql
CREATE TABLE allerte_sistema (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,  -- 'sicurezza', 'hardware', 'sistema'
    livello TEXT NOT NULL,  -- 'info', 'warning', 'error', 'critical'
    messaggio TEXT NOT NULL,
    dettagli TEXT,
    risolto INTEGER DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    risolto_da TEXT,
    risolto_timestamp TIMESTAMP
);
```

## 🔑 RELAZIONI CHIAVE

1. **log_accessi** → **utenti_sistema** O **utenti_autorizzati**
   - Traccia chi ha fatto l'accesso
   - Campo `utente_tipo` distingue il tipo

2. **utenti_orari** → **utenti_autorizzati** + **configurazione_orari**
   - Many-to-many per fasce orarie multiple

3. **Nessuna relazione diretta** tra:
   - `utenti_sistema` e `utenti_autorizzati` (sistemi separati!)

## ⚠️ REGOLE CRITICHE DATABASE

1. **MAI** usare `utenti_autorizzati` per login dashboard
2. **MAI** usare `utenti_sistema` per accesso fisico
3. **SEMPRE** hashare password con bcrypt
4. **SEMPRE** validare `codice_fiscale` formato
5. **SEMPRE** loggare accessi in `log_accessi`
6. **SEMPRE** usare transazioni per operazioni multiple
"""
    
    # Prova a leggere lo schema reale
    try:
        if os.path.exists('src/access.db'):
            conn = sqlite3.connect('src/access.db')
            cursor = conn.cursor()
            
            # Aggiungi schema reale se possibile
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            if tables:
                db_schema_content += "\n\n## 📋 TABELLE REALI NEL DATABASE\n"
                for table in tables:
                    db_schema_content += f"- {table[0]}\n"
            
            conn.close()
    except:
        pass
    
    with open('.clinerules/03-database.md', 'w', encoding='utf-8') as f:
        f.write(db_schema_content)
    
    # 6. Crea rules bank con task comuni
    print("5️⃣ Creazione rules bank...")
    
    # Task: Nuovo modulo
    nuovo_modulo_rules = """# TASK: CREAZIONE NUOVO MODULO

## PASSI DA SEGUIRE

1. **Crea file modulo**
   - Path: `src/api/modules/nome_modulo.py`
   - Usa Blueprint Flask
   - Importa utilities da `src/api/utils.py`

2. **Struttura base modulo**:
```python
from flask import Blueprint, request, jsonify, session
from functools import wraps
import logging
from database.database_manager import DatabaseManager

# Blueprint
nome_bp = Blueprint('nome', __name__)
logger = logging.getLogger(__name__)

# Decorator login_required se necessario
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"success": False, "message": "Login richiesto"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Endpoints
@nome_bp.route('/api/nome', methods=['GET'])
@login_required
def get_items():
    try:
        # Logica
        return jsonify({"success": True, "data": []})
    except Exception as e:
        logger.error(f"Errore: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500
```

3. **Registra in web_api.py**:
```python
from modules.nome_modulo import nome_bp
app.register_blueprint(nome_bp)
```

4. **Crea test**:
   - Path: `tests/unit/test_nome_modulo.py`

5. **Aggiorna documentazione**:
   - Aggiungi in `.clinerules/02-memory.md`
   - Documenta endpoint e funzionalità
"""
    
    with open('clinerules-bank/tasks/nuovo-modulo.md', 'w', encoding='utf-8') as f:
        f.write(nuovo_modulo_rules)
    
    # Task: Nuova pagina
    nuova_pagina_rules = """# TASK: CREAZIONE NUOVA PAGINA

## STRUTTURA FILE PER NUOVA PAGINA

1. **HTML** in `src/api/static/html/nome-pagina.html`:
```html
<div class="container mt-4">
    <h2>Titolo Pagina</h2>
    
    <div class="row">
        <div class="col-md-12">
            <!-- Contenuto -->
        </div>
    </div>
</div>
```

2. **JavaScript** in `src/api/static/js/nome-pagina.js`:
```javascript
// Inizializzazione
document.addEventListener('DOMContentLoaded', function() {
    loadData();
});

// Caricamento dati
async function loadData() {
    try {
        const response = await fetch('/api/endpoint');
        const data = await response.json();
        
        if (data.success) {
            renderData(data.data);
        } else {
            showAlert('danger', data.message);
        }
    } catch (error) {
        console.error('Errore:', error);
        showAlert('danger', 'Errore caricamento dati');
    }
}

// Utility alert (usa quella esistente)
function showAlert(type, message) {
    // Implementazione esistente
}
```

3. **CSS** (se necessario) in `src/api/static/css/nome-pagina.css`

4. **Aggiungi route** in `dashboard_templates.py`:
```python
@app.route('/nome-pagina')
@login_required
def nome_pagina():
    return render_template_string(open('static/html/nome-pagina.html').read())
```

5. **Aggiungi voce menu** in navigazione
"""
    
    with open('clinerules-bank/tasks/nuova-pagina.md', 'w', encoding='utf-8') as f:
        f.write(nuova_pagina_rules)
    
    # 7. Crea file per analisi database reale
    print("6️⃣ Analisi database reale...")
    analyze_db_script = """#!/usr/bin/env python3
import sqlite3
import json
import os
from datetime import datetime

def analyze_real_database():
    db_path = 'src/access.db'
    if not os.path.exists(db_path):
        print(f"❌ Database non trovato: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Estrai info tabelle
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()
    
    db_info = {
        "database": db_path,
        "analyzed_at": datetime.now().isoformat(),
        "tables": {}
    }
    
    for table_name in tables:
        table_name = table_name[0]
        
        # Schema tabella
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # Conta record
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        db_info["tables"][table_name] = {
            "record_count": count,
            "columns": [
                {
                    "cid": col[0],
                    "name": col[1],
                    "type": col[2],
                    "not_null": bool(col[3]),
                    "default": col[4],
                    "primary_key": bool(col[5])
                } for col in columns
            ]
        }
    
    # Salva analisi
    with open('.clinerules/database_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(db_info, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Analisi completata: {len(tables)} tabelle trovate")
    print(f"📄 Risultati salvati in: .clinerules/database_analysis.json")
    
    # Mostra riepilogo
    print("\n📊 Riepilogo tabelle:")
    for table_name, info in db_info["tables"].items():
        print(f"  - {table_name}: {info['record_count']} record, {len(info['columns'])} colonne")
    
    conn.close()

if __name__ == "__main__":
    analyze_real_database()
"""
    
    with open('analyze_database.py', 'w', encoding='utf-8') as f:
        f.write(analyze_db_script)
    os.chmod('analyze_database.py', 0o755)
    
    # 8. Esegui analisi database
    print("\n7️⃣ Tentativo analisi database...")
    os.system('python3 analyze_database.py')
    
    # 9. Crea guida rapida
    print("\n8️⃣ Creazione guida rapida...")
    quick_guide = """# 🚀 GUIDA RAPIDA CLINE - ACCESS_CONTROL

## SETUP COMPLETATO ✅

### File creati in `.clinerules/`:
1. `01-project-rules.md` - Regole obbligatorie progetto
2. `02-memory.md` - Struttura e convenzioni
3. `03-database.md` - Schema database completo

### Rules Bank in `clinerules-bank/`:
- `tasks/nuovo-modulo.md` - Per creare nuovi moduli
- `tasks/nuova-pagina.md` - Per creare nuove pagine

## COME USARE CLINE

### 1. VERIFICA SETUP
Nel popover di Cline (sotto la chat) dovresti vedere:
- ✅ Workspace Rules: .clinerules/
  - 01-project-rules.md
  - 02-memory.md
  - 03-database.md

### 2. INIZIO GIORNATA
Non serve fare nulla! Le regole si caricano automaticamente.
Puoi verificare scrivendo:
```
Conferma di aver caricato le regole del progetto access_control.
Quale tabella usi per il login admin?
```

### 3. NUOVO TASK
Scrivi direttamente:
```
TASK: [descrizione di cosa vuoi fare]

Esempio:
TASK: Aggiungi campo "data_ultimo_accesso" alla tabella utenti_autorizzati
```

### 4. TASK COMUNI
Per task ricorrenti, attiva regole specifiche dal rules bank:
```
cp clinerules-bank/tasks/nuovo-modulo.md .clinerules/
```

### 5. FINE GIORNATA
Disattiva regole temporanee:
```
rm .clinerules/nuovo-modulo.md  # rimuovi regole task specifiche
```

## COMANDI UTILI

```bash
# Vedere regole attive
ls -la .clinerules/

# Backup regole
cp -r .clinerules .clinerules.backup

# Analizza database
python3 analyze_database.py

# Vedi log modifiche
ls -la da_buttare/
```

## WORKFLOW ESEMPIO

1. **Richiesta**: "Crea pagina gestione utenti autorizzati"
2. **Cline legge** automaticamente le regole
3. **Propone** soluzione step-by-step
4. **Tu confermi** prima che proceda
5. **Implementa** seguendo le convenzioni
6. **Sposta** file obsoleti in da_buttare/
7. **Conferma** completamento

## TROUBLESHOOTING

- **Cline non vede le regole?** 
  - Verifica che `.clinerules/` sia nella root del progetto
  - Ricarica VS Code

- **Vuoi regole temporanee?**
  - Copia da `clinerules-bank/` a `.clinerules/`
  - Rimuovi dopo l'uso

- **Database cambiato?**
  - Esegui: `python3 analyze_database.py`
  - Aggiorna `.clinerules/03-database.md`

---
Progetto: `/opt/access_control`
Setup: COMPLETATO ✅
"""
    
    with open('CLINE_GUIDA_RAPIDA.md', 'w', encoding='utf-8') as f:
        f.write(quick_guide)
    
    # 10. Mostra riepilogo finale
    print("\n" + "="*50)
    print("🎉 SETUP COMPLETATO CON SUCCESSO!")
    print("="*50)
    print("\n📁 File creati:")
    print("  ✅ .clinerules/01-project-rules.md")
    print("  ✅ .clinerules/02-memory.md") 
    print("  ✅ .clinerules/03-database.md")
    print("  ✅ clinerules-bank/ (task comuni)")
    print("  ✅ CLINE_GUIDA_RAPIDA.md")
    print("  ✅ analyze_database.py")
    
    print("\n�� PROSSIMI PASSI:")
    print("1. Apri Cline in VS Code")
    print("2. Verifica nel popover che veda le regole")
    print("3. Testa con: 'Quale tabella usi per login admin?'")
    print("\n📖 Leggi CLINE_GUIDA_RAPIDA.md per tutti i dettagli!")

if __name__ == "__main__":
    setup_cline_complete()
