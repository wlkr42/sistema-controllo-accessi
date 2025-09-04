# File: /opt/access_control/scripts/create_project_snapshot.py
# Crea un file CODICE_PROGETTO_AGGIORNATO.md con tutto il codice della cartella src

import os
import datetime
from pathlib import Path

def create_project_snapshot():
    """Crea snapshot completo del codice in src"""
    
    base_dir = "/opt/access_control"
    src_dir = os.path.join(base_dir, "src")
    output_file = os.path.join(base_dir, "CODICE_PROGETTO_AGGIORNATO.md")
    
    # Estensioni da includere
    extensions = ['.py', '.html', '.js', '.css', '.json', '.yml', '.yaml', '.txt', '.md']
    
    # Directory da escludere
    exclude_dirs = ['__pycache__', '.git', 'venv', 'backup', '.idea']
    
    print(f"📸 Creazione snapshot del progetto...")
    print(f"📁 Directory sorgente: {src_dir}")
    print(f"📄 File output: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Header
        f.write("# 📸 CODICE PROGETTO AGGIORNATO\n")
        f.write("## Sistema Controllo Accessi - Snapshot Completo\n\n")
        f.write(f"**Data snapshot**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Directory progetto**: {base_dir}\n\n")
        
        # Struttura directory
        f.write("## 📁 STRUTTURA DIRECTORY SRC\n")
        f.write("```\n")
        
        # Genera albero directory
        for root, dirs, files in os.walk(src_dir):
            # Escludi directory non volute
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            level = root.replace(src_dir, '').count(os.sep)
            indent = '│   ' * level
            sub_indent = '│   ' * (level + 1)
            
            # Nome directory
            if root != src_dir:
                f.write(f"{indent}├── {os.path.basename(root)}/\n")
            else:
                f.write("src/\n")
            
            # Files nella directory
            for file in sorted(files):
                if any(file.endswith(ext) for ext in extensions):
                    if file == files[-1]:
                        f.write(f"{sub_indent[:-4]}└── {file}\n")
                    else:
                        f.write(f"{sub_indent[:-4]}├── {file}\n")
        
        f.write("```\n\n")
        
        # Contenuto dei file
        f.write("## 📄 CONTENUTO DEI FILE\n\n")
        
        file_count = 0
        total_lines = 0
        
        for root, dirs, files in os.walk(src_dir):
            # Escludi directory non volute
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in sorted(files):
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, base_dir)
                    
                    try:
                        # Leggi il file
                        with open(file_path, 'r', encoding='utf-8') as src_file:
                            content = src_file.read()
                            lines = content.count('\n') + 1
                            
                        file_count += 1
                        total_lines += lines
                        
                        # Scrivi nel markdown
                        f.write(f"### 📁 `{relative_path}`\n\n")
                        f.write(f"**Righe**: {lines} | ")
                        f.write(f"**Dimensione**: {os.path.getsize(file_path)} bytes | ")
                        f.write(f"**Modificato**: {datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                        
                        # Determina il linguaggio per syntax highlighting
                        lang_map = {
                            '.py': 'python',
                            '.js': 'javascript',
                            '.html': 'html',
                            '.css': 'css',
                            '.json': 'json',
                            '.yml': 'yaml',
                            '.yaml': 'yaml',
                            '.md': 'markdown',
                            '.txt': 'text'
                        }
                        
                        ext = os.path.splitext(file)[1]
                        lang = lang_map.get(ext, 'text')
                        
                        f.write(f"```{lang}\n")
                        f.write(content)
                        if not content.endswith('\n'):
                            f.write('\n')
                        f.write("```\n\n")
                        f.write("---\n\n")
                        
                        print(f"✅ Aggiunto: {relative_path}")
                        
                    except Exception as e:
                        print(f"❌ Errore leggendo {file_path}: {e}")
                        f.write(f"**ERRORE**: Impossibile leggere il file - {e}\n\n")
                        f.write("---\n\n")
        
        # Statistiche finali
        f.write("## 📊 STATISTICHE\n\n")
        f.write(f"- **File totali**: {file_count}\n")
        f.write(f"- **Righe totali**: {total_lines:,}\n")
        f.write(f"- **Data creazione**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"\n✅ Snapshot completato!")
    print(f"📄 File creato: {output_file}")
    print(f"📊 Statistiche: {file_count} file, {total_lines:,} righe totali")
    
    # Mostra dimensione file
    size = os.path.getsize(output_file)
    if size > 1024 * 1024:
        print(f"📦 Dimensione: {size / (1024 * 1024):.2f} MB")
    else:
        print(f"📦 Dimensione: {size / 1024:.2f} KB")

if __name__ == "__main__":
    create_project_snapshot()
