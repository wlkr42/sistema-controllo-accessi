#!/usr/bin/env python3
"""
Script per aggiornare la memoria permanente di Cline
Aggiorna i file in .clinerules/ con le modifiche al progetto
"""

import os
import json
import sqlite3
from datetime import datetime
import shutil
import hashlib

class ClineMemoryUpdater:
    def __init__(self):
        self.clinerules_dir = '.clinerules'
        self.backup_dir = '.clinerules_backups'
        self.changes_log = []
        
    def print_header(self, text):
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}\n")
    
    def backup_current_memory(self):
        """Crea backup della memoria corrente"""
        if not os.path.exists(self.clinerules_dir):
            print("❌ Directory .clinerules non trovata")
            return False
        
        # Crea directory backup
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Nome backup con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        # Copia directory
        shutil.copytree(self.clinerules_dir, backup_path)
        print(f"✅ Backup creato: {backup_path}")
        
        # Mantieni solo ultimi 5 backup
        self._cleanup_old_backups()
        
        return True
    
    def _cleanup_old_backups(self):
        """Mantiene solo gli ultimi 5 backup"""
        backups = sorted([d for d in os.listdir(self.backup_dir) if d.startswith('backup_')])
        if len(backups) > 5:
            for old_backup in backups[:-5]:
                shutil.rmtree(os.path.join(self.backup_dir, old_backup))
                print(f"🗑️  Rimosso vecchio backup: {old_backup}")
    
    def update_memory_interactive(self):
        """Aggiornamento interattivo della memoria"""
        self.print_header("AGGIORNAMENTO MEMORIA CLINE")
        
        print("Cosa vuoi aggiornare?")
        print("1. Nuovi file/moduli aggiunti")
        print("2. Endpoint API modificati")
        print("3. Schema database cambiato")
        print("4. Regole progetto")
        print("5. Tutto (scan completo)")
        print("0. Esci")
        
        choice = input("\nScelta (0-5): ").strip()
        
        if choice == '0':
            return
        
        # Backup prima di modificare
        if not self.backup_current_memory():
            return
        
        if choice == '1':
            self.update_new_files()
        elif choice == '2':
            self.update_api_endpoints()
        elif choice == '3':
            self.update_database_schema()
        elif choice == '4':
            self.update_project_rules()
        elif choice == '5':
            self.full_update()
        
        # Salva log modifiche
        self.save_changes_log()
    
    def update_new_files(self):
        """Aggiorna memoria con nuovi file/moduli"""
        print("\n📁 AGGIORNAMENTO FILE/MODULI")
        
        # Chiedi info sul nuovo modulo
        module_name = input("Nome del nuovo modulo/file (es. gestione_report): ").strip()
        module_path = input("Path del file (es. src/api/modules/gestione_report.py): ").strip()
        module_desc = input("Descrizione breve: ").strip()
        
        # Leggi memoria corrente
        memory_file = os.path.join(self.clinerules_dir, '02-memory.md')
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Trova sezione moduli
        if "### src/api/modules/" in content:
            # Aggiungi nuovo modulo alla lista
            insert_pos = content.find("### src/api/modules/")
            # Trova fine sezione
            next_section = content.find("\n##", insert_pos + 1)
            if next_section == -1:
                next_section = content.find("\n### ", insert_pos + 20)
            
            if next_section != -1:
                # Inserisci prima della prossima sezione
                new_line = f"- `{module_name}.py` - {module_desc}\n"
                content = content[:next_section] + new_line + content[next_section:]
                self.changes_log.append(f"Aggiunto modulo: {module_name}")
        
        # Chiedi se ci sono nuovi endpoint
        if input("\nIl modulo ha nuovi endpoint API? (s/n): ").lower() == 's':
            self._add_endpoints_to_memory(content, module_name)
        
        # Salva memoria aggiornata
        with open(memory_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Memoria aggiornata con modulo: {module_name}")
    
    def _add_endpoints_to_memory(self, content, module_name):
        """Aggiunge endpoint alla memoria"""
        print("\nAggiungi endpoint (uno per riga, vuoto per terminare):")
        print("Formato: METHOD /path - descrizione")
        print("Esempio: GET /api/reports - Lista report")
        
        endpoints = []
        while True:
            endpoint = input("> ").strip()
            if not endpoint:
                break
            endpoints.append(endpoint)
        
        if endpoints:
            # Trova sezione API endpoints
            api_section = content.find("## 🔌 API ENDPOINTS")
            if api_section != -1:
                # Aggiungi nuova sottosezione
                insert_text = f"\n### {module_name.replace('_', ' ').title()}\n"
                for ep in endpoints:
                    insert_text += f"- `{ep}`\n"
                
                # Trova dove inserire (prima della prossima sezione)
                next_main_section = content.find("\n## ", api_section + 1)
                if next_main_section == -1:
                    content += insert_text
                else:
                    content = content[:next_main_section] + insert_text + content[next_main_section:]
                
                self.changes_log.extend([f"Aggiunto endpoint: {ep}" for ep in endpoints])
        
        return content
    
    def update_database_schema(self):
        """Aggiorna schema database"""
        print("\n🗄️  AGGIORNAMENTO SCHEMA DATABASE")
        
        db_path = 'src/access.db'
        if not os.path.exists(db_path):
            print(f"❌ Database non trovato: {db_path}")
            return
        
        # Analizza database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ottieni tutte le tabelle
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        
        # Genera nuovo schema
        schema_content = """# SCHEMA DATABASE ACCESS_CONTROL

## 📍 POSIZIONE DATABASE
`/opt/access_control/src/access.db`

## 📊 TABELLE ATTUALI

"""
        
        for table_name in tables:
            table_name = table_name[0]
            schema_content += f"### {table_name}\n"
            
            # Schema tabella
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Conta record
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            schema_content += f"**Record attuali**: {count}\n\n"
            schema_content += "| Colonna | Tipo | NOT NULL | Default | PK |\n"
            schema_content += "|---------|------|----------|---------|----|\n"
            
            for col in columns:
                schema_content += f"| {col[1]} | {col[2]} | {'✓' if col[3] else ''} | {col[4] or ''} | {'✓' if col[5] else ''} |\n"
            
            schema_content += "\n"
        
        # Aggiungi timestamp aggiornamento
        schema_content += f"\n---\n*Ultimo aggiornamento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        # Salva nuovo schema
        schema_file = os.path.join(self.clinerules_dir, '03-database.md')
        with open(schema_file, 'w', encoding='utf-8') as f:
            f.write(schema_content)
        
        conn.close()
        
        self.changes_log.append(f"Schema database aggiornato: {len(tables)} tabelle")
        print(f"✅ Schema database aggiornato con {len(tables)} tabelle")
    
    def update_project_rules(self):
        """Aggiorna regole progetto"""
        print("\n📐 AGGIORNAMENTO REGOLE PROGETTO")
        
        print("1. Aggiungi nuova regola")
        print("2. Modifica regola esistente")
        print("3. Rimuovi regola")
        
        choice = input("\nScelta (1-3): ").strip()
        
        rules_file = os.path.join(self.clinerules_dir, '01-project-rules.md')
        
        if choice == '1':
            # Aggiungi nuova regola
            print("\nNuova regola:")
            category = input("Categoria (es. METODOLOGIA, DATABASE, STILE): ").strip()
            rule = input("Regola: ").strip()
            
            with open(rules_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Trova categoria o crea nuova
            cat_header = f"### {category.upper()}"
            if cat_header in content:
                # Aggiungi alla categoria esistente
                pos = content.find(cat_header)
                next_section = content.find("\n### ", pos + 1)
                if next_section == -1:
                    next_section = content.find("\n## ", pos + 1)
                
                insert_pos = next_section if next_section != -1 else len(content)
                content = content[:insert_pos] + f"- ✅ {rule}\n" + content[insert_pos:]
            else:
                # Crea nuova categoria
                content += f"\n{cat_header}\n- ✅ {rule}\n"
            
            with open(rules_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.changes_log.append(f"Aggiunta regola: {rule}")
            print("✅ Regola aggiunta")
    
    def full_update(self):
        """Aggiornamento completo della memoria"""
        print("\n🔄 AGGIORNAMENTO COMPLETO")
        
        # 1. Aggiorna database
        self.update_database_schema()
        
        # 2. Scan nuovi file
        print("\n📂 Scanning nuovi file...")
        self._scan_project_changes()
        
        # 3. Aggiorna timestamp
        self._update_timestamps()
        
        print("\n✅ Aggiornamento completo terminato")
    
    def _scan_project_changes(self):
        """Scansiona cambiamenti nel progetto"""
        # Conta file per tipo
        file_counts = {
            'py': 0,
            'js': 0,
            'html': 0,
            'css': 0
        }
        
        for root, dirs, files in os.walk('src'):
            # Salta directory da ignorare
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv']]
            
            for file in files:
                ext = file.split('.')[-1]
                if ext in file_counts:
                    file_counts[ext] += 1
        
        print(f"\n📊 File trovati:")
        for ext, count in file_counts.items():
            print(f"  - .{ext}: {count} file")
        
        self.changes_log.append(f"Scan completo: {sum(file_counts.values())} file di codice")
    
    def _update_timestamps(self):
        """Aggiorna timestamp in tutti i file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for filename in os.listdir(self.clinerules_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(self.clinerules_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Aggiungi o aggiorna timestamp
                if '*Ultimo aggiornamento:' in content:
                    # Sostituisci timestamp esistente
                    import re
                    content = re.sub(
                        r'\*Ultimo aggiornamento: .*\*',
                        f'*Ultimo aggiornamento: {timestamp}*',
                        content
                    )
                else:
                    # Aggiungi timestamp alla fine
                    content += f"\n\n---\n*Ultimo aggiornamento: {timestamp}*\n"
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
    
    def save_changes_log(self):
        """Salva log delle modifiche"""
        if not self.changes_log:
            print("\n📝 Nessuna modifica da registrare")
            return
        
        log_file = 'memory_updates.log'
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Aggiornamento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n")
            for change in self.changes_log:
                f.write(f"- {change}\n")
        
        print(f"\n📝 Log modifiche salvato in: {log_file}")
        print("Modifiche effettuate:")
        for change in self.changes_log:
            print(f"  - {change}")
    
    def restore_backup(self):
        """Ripristina un backup precedente"""
        self.print_header("RIPRISTINO BACKUP")
        
        if not os.path.exists(self.backup_dir):
            print("❌ Nessun backup trovato")
            return
        
        # Lista backup disponibili
        backups = sorted([d for d in os.listdir(self.backup_dir) if d.startswith('backup_')])
        
        if not backups:
            print("❌ Nessun backup trovato")
            return
        
        print("Backup disponibili:")
        for i, backup in enumerate(backups, 1):
            # Estrai timestamp
            timestamp = backup.replace('backup_', '')
            print(f"{i}. {timestamp}")
        
        choice = input("\nQuale backup ripristinare? (numero): ").strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(backups):
                backup_path = os.path.join(self.backup_dir, backups[idx])
                
                # Rimuovi directory corrente
                if os.path.exists(self.clinerules_dir):
                    shutil.rmtree(self.clinerules_dir)
                
                # Ripristina backup
                shutil.copytree(backup_path, self.clinerules_dir)
                
                print(f"✅ Backup ripristinato: {backups[idx]}")
                self.changes_log.append(f"Ripristinato backup: {backups[idx]}")
            else:
                print("❌ Scelta non valida")
        except ValueError:
            print("❌ Inserisci un numero valido")

def main():
    updater = ClineMemoryUpdater()
    
    while True:
        updater.print_header("GESTIONE MEMORIA CLINE")
        print("1. Aggiorna memoria")
        print("2. Ripristina backup")
        print("3. Mostra ultimi cambiamenti")
        print("0. Esci")
        
        choice = input("\nScelta: ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            updater.update_memory_interactive()
        elif choice == '2':
            updater.restore_backup()
        elif choice == '3':
            if os.path.exists('memory_updates.log'):
                print("\n📋 Ultimi aggiornamenti:")
                with open('memory_updates.log', 'r') as f:
                    lines = f.readlines()
                    # Mostra ultime 20 righe
                    for line in lines[-20:]:
                        print(line.rstrip())
            else:
                print("\n❌ Nessun log trovato")
        
        input("\nPremi ENTER per continuare...")

if __name__ == "__main__":
    main()
