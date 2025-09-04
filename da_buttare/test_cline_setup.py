#!/usr/bin/env python3
"""
Test della configurazione Cline per access_control
Verifica che tutto sia configurato correttamente
"""

import os
import json
import sys
from datetime import datetime

def print_header(text):
    print(f"\n{'='*50}")
    print(f"  {text}")
    print(f"{'='*50}")

def check_file(filepath, description):
    """Verifica esistenza file e mostra info"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}")
    print(f"   Path: {filepath}")
    
    if exists:
        size = os.path.getsize(filepath)
        print(f"   Size: {size} bytes")
        if filepath.endswith('.md'):
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"   Lines: {len(lines)}")
                # Mostra prime 3 righe
                print("   Preview:")
                for i, line in enumerate(lines[:3]):
                    print(f"     {line.strip()}")
                    if i >= 2:
                        print("     ...")
                        break
    else:
        print(f"   ⚠️  File mancante!")
    
    print()
    return exists

def test_cline_setup():
    """Test completo setup Cline"""
    
    print_header("TEST CONFIGURAZIONE CLINE")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working dir: {os.getcwd()}")
    
    # 1. Verifica struttura base
    print_header("1. VERIFICA STRUTTURA BASE")
    
    essential_dirs = {
        '.clinerules': 'Directory regole Cline',
        'src': 'Codice sorgente',
        'config': 'Configurazioni',
        'logs': 'File di log',
        'da_buttare': 'File obsoleti'
    }
    
    all_dirs_ok = True
    for dir_path, description in essential_dirs.items():
        exists = os.path.exists(dir_path)
        status = "✅" if exists else "❌"
        print(f"{status} {description}: {dir_path}")
        if not exists:
            all_dirs_ok = False
    
    # 2. Verifica file Cline
    print_header("2. VERIFICA FILE CLINE")
    
    cline_files = {
        '.clinerules/01-project-rules.md': 'Regole progetto',
        '.clinerules/02-memory.md': 'Memoria struttura',
        '.clinerules/03-database.md': 'Schema database'
    }
    
    all_files_ok = True
    for filepath, description in cline_files.items():
        if not check_file(filepath, description):
            all_files_ok = False
    
    # 3. Verifica database
    print_header("3. VERIFICA DATABASE")
    
    db_path = 'src/access.db'
    db_exists = check_file(db_path, "Database SQLite")
    
    if db_exists:
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verifica tabelle critiche
            critical_tables = ['utenti_sistema', 'utenti_autorizzati', 'log_accessi']
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [t[0] for t in cursor.fetchall()]
            
            print("   Tabelle trovate:")
            for table in critical_tables:
                status = "✅" if table in tables else "❌"
                print(f"   {status} {table}")
            
            conn.close()
        except Exception as e:
            print(f"   ❌ Errore lettura database: {e}")
    
    # 4. Verifica rules bank
    print_header("4. VERIFICA RULES BANK")
    
    rules_bank_files = {
        'clinerules-bank/tasks/nuovo-modulo.md': 'Template nuovo modulo',
        'clinerules-bank/tasks/nuova-pagina.md': 'Template nuova pagina'
    }
    
    for filepath, description in rules_bank_files.items():
        check_file(filepath, description)
    
    # 5. Test prompt Cline
    print_header("5. PROMPT TEST PER CLINE")
    
    test_prompts = [
        "Conferma di aver caricato le regole del progetto access_control.",
        "Quale tabella usi per il login degli amministratori?",
        "Dove vanno spostati i file obsoleti?",
        "In che lingua devi rispondere?",
        "Qual è la struttura delle cartelle src/?",
    ]
    
    print("Copia e incolla questi prompt in Cline per verificare:")
    print()
    for i, prompt in enumerate(test_prompts, 1):
        print(f"{i}. {prompt}")
    
    # 6. Genera report
    print_header("6. GENERA REPORT")
    
    report = {
        "test_date": datetime.now().isoformat(),
        "working_dir": os.getcwd(),
        "setup_status": {
            "directories": all_dirs_ok,
            "cline_files": all_files_ok,
            "database": db_exists,
            "overall": all_dirs_ok and all_files_ok and db_exists
        },
        "files_checked": list(cline_files.keys()),
        "recommendations": []
    }
    
    if not all_files_ok:
        report["recommendations"].append("Esegui: python3 setup_cline_complete.py")
    
    if not db_exists:
        report["recommendations"].append("Database non trovato - verifica path")
    
    # Salva report
    report_path = f"cline_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Report salvato: {report_path}")
    
    # 7. Risultato finale
    print_header("RISULTATO TEST")
    
    if report["setup_status"]["overall"]:
        print("✅ SETUP COMPLETATO CORRETTAMENTE!")
        print("\nCline è pronto per l'uso. Le regole si caricheranno automaticamente.")
    else:
        print("❌ SETUP INCOMPLETO")
        print("\nRaccomandazioni:")
        for rec in report["recommendations"]:
            print(f"  - {rec}")
    
    # 8. Quick start
    print_header("QUICK START")
    print("1. Apri Cline in VS Code")
    print("2. Verifica nel popover che veda: .clinerules/")
    print("3. Inizia con un task semplice:")
    print('   "TASK: Mostrami la lista degli endpoint API"')
    print("\n📖 Per maggiori dettagli: cat CLINE_GUIDA_RAPIDA.md")

def check_dependencies():
    """Verifica dipendenze Python"""
    print_header("VERIFICA DIPENDENZE")
    
    try:
        import sqlite3
        print("✅ sqlite3 disponibile")
    except:
        print("❌ sqlite3 non disponibile")
    
    try:
        import flask
        print("✅ Flask installato")
    except:
        print("❌ Flask non installato - esegui: pip install -r requirements.txt")
    
    print()

if __name__ == "__main__":
    try:
        check_dependencies()
        test_cline_setup()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrotto dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Errore durante il test: {e}")
        sys.exit(1)
