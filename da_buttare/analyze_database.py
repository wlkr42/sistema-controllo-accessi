#!/usr/bin/env python3
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
    print("
📊 Riepilogo tabelle:")
    for table_name, info in db_info["tables"].items():
        print(f"  - {table_name}: {info['record_count']} record, {len(info['columns'])} colonne")
    
    conn.close()

if __name__ == "__main__":
    analyze_real_database()
