#!/usr/bin/env python3
"""
Script per generare documentazione completa del progetto Access Control
Genera un documento con nome file, percorso e contenuto di tutti i file rilevanti
"""

import os
import datetime
from pathlib import Path
import mimetypes

class ProjectDocumenter:
    def __init__(self, project_root="/opt/access_control/src"):
        self.project_root = Path(project_root)
        self.output_file = f"documentazione_access_control_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        # Cartelle e file da escludere
        self.excluded_dirs = {
            '__pycache__',
            '.git',
            '.vscode',
            'node_modules',
            'backup',
            'download',
            'venv',
            '.pytest_cache'
        }
        
        # Estensioni di file da escludere
        self.excluded_extensions = {
            '.pyc',
            '.pyo',
            '.pyd',
            '__pycache__',
            '.git',
            '.gitignore',
            '.DS_Store',
            '.tar.gz',
            '.zip',
            '.rar',
            '.7z',
            '.bz2',
            '.o',  # object files
            '.so'  # shared objects (ma potremmo volerli documentare)
        }
        
        # Estensioni di file di codice/configurazione da includere
        self.code_extensions = {
            '.py', '.js', '.html', '.css', '.sql', '.md', '.txt', '.json', 
            '.xml', '.yml', '.yaml', '.ini', '.cfg', '.conf', '.sh', 
            '.c', '.h', '.cpp', '.hpp', '.java', '.php', '.rb', '.go'
        }

    def should_exclude_dir(self, dir_name):
        """Verifica se una directory deve essere esclusa"""
        return dir_name in self.excluded_dirs

    def should_exclude_file(self, file_path):
        """Verifica se un file deve essere escluso"""
        file_path = Path(file_path)
        
        # Esclude per estensione
        if file_path.suffix.lower() in self.excluded_extensions:
            return True
            
        # Esclude file di backup specifici
        if 'backup_completo_' in file_path.name:
            return True
            
        # Esclude file temporanei
        if file_path.name.startswith('.') and file_path.suffix == '':
            return True
            
        return False

    def is_text_file(self, file_path):
        """Verifica se un file è testuale e può essere letto"""
        try:
            # Controlla per estensione
            if file_path.suffix.lower() in self.code_extensions:
                return True
                
            # Usa mimetypes per altri file
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type and mime_type.startswith('text/'):
                return True
                
            # Prova a leggere i primi bytes per verificare se è testo
            with open(file_path, 'rb') as f:
                sample = f.read(1024)
                try:
                    sample.decode('utf-8')
                    return True
                except UnicodeDecodeError:
                    return False
                    
        except Exception:
            return False

    def read_file_content(self, file_path):
        """Legge il contenuto di un file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                return f"[ERRORE LETTURA FILE: {e}]"
        except Exception as e:
            return f"[ERRORE LETTURA FILE: {e}]"

    def get_file_info(self, file_path):
        """Ottiene informazioni su un file"""
        try:
            stat = file_path.stat()
            return {
                'size': stat.st_size,
                'modified': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'permissions': oct(stat.st_mode)[-3:]
            }
        except Exception:
            return {'size': 0, 'modified': 'N/A', 'permissions': 'N/A'}

    def scan_directory(self, directory):
        """Scansiona ricorsivamente una directory"""
        files_info = []
        
        try:
            for root, dirs, files in os.walk(directory):
                # Rimuove le directory da escludere dalla lista
                dirs[:] = [d for d in dirs if not self.should_exclude_dir(d)]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    if self.should_exclude_file(file_path):
                        continue
                        
                    relative_path = file_path.relative_to(self.project_root)
                    file_info = self.get_file_info(file_path)
                    
                    files_info.append({
                        'name': file,
                        'path': str(relative_path),
                        'full_path': str(file_path),
                        'directory': str(relative_path.parent),
                        'is_text': self.is_text_file(file_path),
                        'info': file_info
                    })
                    
        except Exception as e:
            print(f"Errore durante la scansione di {directory}: {e}")
            
        return files_info

    def generate_documentation(self):
        """Genera la documentazione completa"""
        print(f"Generazione documentazione per: {self.project_root}")
        print(f"File output: {self.output_file}")
        
        # Scansiona tutti i file
        all_files = self.scan_directory(self.project_root)
        
        # Ordina per percorso
        all_files.sort(key=lambda x: x['path'])
        
        # Genera il documento
        with open(self.output_file, 'w', encoding='utf-8') as doc:
            # Header del documento
            doc.write(f"# Documentazione Progetto Access Control\n\n")
            doc.write(f"**Data generazione:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            doc.write(f"**Directory progetto:** {self.project_root}\n")
            doc.write(f"**Totale file documentati:** {len(all_files)}\n\n")
            
            # Indice
            doc.write("## Indice File\n\n")
            for file_info in all_files:
                doc.write(f"- [{file_info['path']}](#{file_info['path'].replace('/', '').replace('.', '').replace('_', '').replace('-', '')})\n")
            doc.write("\n---\n\n")
            
            # Contenuto di ogni file
            for i, file_info in enumerate(all_files, 1):
                print(f"Processando file {i}/{len(all_files)}: {file_info['path']}")
                
                doc.write(f"## File: {file_info['name']}\n\n")
                doc.write(f"**Percorso:** `{file_info['path']}`\n")
                doc.write(f"**Directory:** `{file_info['directory']}`\n")
                doc.write(f"**Dimensione:** {file_info['info']['size']} bytes\n")
                doc.write(f"**Ultima modifica:** {file_info['info']['modified']}\n")
                doc.write(f"**Permessi:** {file_info['info']['permissions']}\n\n")
                
                if file_info['is_text']:
                    content = self.read_file_content(file_info['full_path'])
                    
                    # Determina il linguaggio per syntax highlighting
                    extension = Path(file_info['name']).suffix.lower()
                    language_map = {
                        '.py': 'python',
                        '.js': 'javascript', 
                        '.html': 'html',
                        '.css': 'css',
                        '.sql': 'sql',
                        '.sh': 'bash',
                        '.c': 'c',
                        '.h': 'c',
                        '.cpp': 'cpp',
                        '.json': 'json',
                        '.xml': 'xml',
                        '.yml': 'yaml',
                        '.yaml': 'yaml'
                    }
                    
                    lang = language_map.get(extension, 'text')
                    
                    doc.write(f"### Contenuto:\n\n")
                    doc.write(f"```{lang}\n")
                    doc.write(content)
                    doc.write(f"\n```\n\n")
                else:
                    doc.write("### Contenuto:\n\n")
                    doc.write("*[File binario - contenuto non visualizzabile]*\n\n")
                
                doc.write("---\n\n")
        
        print(f"\nDocumentazione generata con successo: {self.output_file}")
        print(f"Totale file documentati: {len(all_files)}")

def main():
    # Configura il percorso del progetto
    project_path = "/opt/access_control/src"
    
    # Se lo script viene eseguito dalla directory del progetto
    if os.path.exists("./src"):
        project_path = "./src"
    elif os.path.exists("../src"):
        project_path = "../src"
    
    print("=== GENERATORE DOCUMENTAZIONE ACCESS CONTROL ===")
    print(f"Percorso progetto: {project_path}")
    
    if not os.path.exists(project_path):
        print(f"ERRORE: Directory {project_path} non trovata!")
        print("Modifica il percorso nella variabile 'project_path' nello script.")
        return
    
    documenter = ProjectDocumenter(project_path)
    documenter.generate_documentation()

if __name__ == "__main__":
    main()
