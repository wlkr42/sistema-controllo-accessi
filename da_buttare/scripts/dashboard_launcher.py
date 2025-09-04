# File: /opt/access_control/scripts/dashboard_launcher.py
# Script per avviare e testare la dashboard web

import os
import sys
import json
import time
import socket
import subprocess
import signal
from pathlib import Path
from datetime import datetime

class DashboardLauncher:
    """Launcher per dashboard web con diagnostica integrata"""
    
    def __init__(self):
        self.project_root = Path("/opt/access_control")
        self.web_api_path = self.project_root / "src" / "api" / "web_api.py"
        self.config_path = self.project_root / "config" / "dashboard_config.json"
        self.process = None
        
    def check_prerequisites(self) -> bool:
        """Verifica prerequisiti per dashboard"""
        print("🔍 VERIFICA PREREQUISITI DASHBOARD")
        print("-" * 40)
        
        checks = []
        
        # 1. File web_api.py presente
        if self.web_api_path.exists():
            checks.append(("File web_api.py", True, "✅ Presente"))
        else:
            checks.append(("File web_api.py", False, f"❌ Non trovato: {self.web_api_path}"))
        
        # 2. Configurazione dashboard
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                checks.append(("Config dashboard", True, f"✅ Valida ({len(config)} chiavi)"))
            except json.JSONDecodeError as e:
                checks.append(("Config dashboard", False, f"❌ JSON non valido: {e}"))
        else:
            checks.append(("Config dashboard", False, f"❌ Non trovato: {self.config_path}"))
        
        # 3. Dipendenze Python
        required_modules = ['flask', 'flask_cors', 'pandas', 'sqlite3']
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            checks.append(("Dipendenze Python", False, f"❌ Mancanti: {', '.join(missing_modules)}"))
        else:
            checks.append(("Dipendenze Python", True, f"✅ Tutte presenti ({len(required_modules)})"))
        
        # 4. Database SQLite
        db_path = self.project_root / "src" / "access.db"
        if db_path.exists():
            checks.append(("Database SQLite", True, "✅ Presente"))
        else:
            checks.append(("Database SQLite", False, f"❌ Non trovato: {db_path}"))
        
        # 5. Porta 5000 libera
        if self.is_port_free(5000):
            checks.append(("Porta 5000", True, "✅ Libera"))
        else:
            checks.append(("Porta 5000", False, "❌ Occupata o dashboard già attiva"))
        
        # Stampa risultati
        all_ok = True
        for check_name, status, message in checks:
            print(f"{message}")
            if not status:
                all_ok = False
        
        print("-" * 40)
        if all_ok:
            print("✅ Tutti i prerequisiti soddisfatti")
        else:
            print("❌ Alcuni prerequisiti non soddisfatti")
        
        return all_ok
    
    def is_port_free(self, port: int) -> bool:
        """Verifica se una porta è libera"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result != 0  # 0 = connesso (porta occupata)
        except:
            return True
    
    def create_default_config(self):
        """Crea configurazione di default se mancante"""
        if not self.config_path.exists():
            print("🔧 Creazione configurazione di default...")
            
            # Crea directory config se non esiste
            self.config_path.parent.mkdir(exist_ok=True)
            
            default_config = {
                "comune": "Rende",
                "nome_isola": "Isola Ecologica RAEE",
                "email_destinatari": ["ambiente@comune.rende.cs.it"],
                "email_mittente": "isola@comune.rende.cs.it",
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_password": "",
                "report_automatico": True,
                "durata_apertura": 8,
                "orario_inizio": "08:00",
                "orario_fine": "18:00",
                "illuminazione_auto": True,
                "blocco_magnetico": True,
                "admin_users": {
                    "admin": "scrypt:32768:8:1$default$hash"
                }
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            print(f"✅ Configurazione creata: {self.config_path}")
    
    def test_dashboard_startup(self) -> bool:
        """Test avvio dashboard senza mantenerla attiva"""
        print("\n🧪 TEST AVVIO DASHBOARD")
        print("-" * 40)
        
        try:
            # Cambia directory e attiva venv
            os.chdir(self.project_root)
            
            # Comando per avviare dashboard
            cmd = [sys.executable, str(self.web_api_path)]
            
            print(f"🚀 Comando: {' '.join(cmd)}")
            print("⏳ Avvio test (timeout 10 secondi)...")
            
            # Avvia processo
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.project_root
            )
            
            # Attendi avvio (max 10 secondi)
            for attempt in range(10):
                time.sleep(1)
                if not self.is_port_free(5000):
                    print("✅ Dashboard avviata correttamente!")
                    
                    # Test connessione HTTP
                    try:
                        import urllib.request
                        with urllib.request.urlopen('http://localhost:5000', timeout=3) as response:
                            if response.status == 200:
                                print("✅ Risposta HTTP 200 OK")
                            else:
                                print(f"⚠️ Risposta HTTP: {response.status}")
                    except Exception as e:
                        print(f"⚠️ Test HTTP fallito: {e}")
                    
                    # Termina processo di test
                    process.terminate()
                    process.wait(timeout=5)
                    print("✅ Test completato con successo")
                    return True
                
                # Controlla se processo è morto
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    print("❌ Processo terminato prematuramente")
                    if stderr:
                        print(f"Errore: {stderr}")
                    return False
            
            # Timeout
            print("❌ Timeout: dashboard non risponde")
            process.terminate()
            process.wait(timeout=5)
            return False
            
        except Exception as e:
            print(f"❌ Errore durante test: {e}")
            return False
    
    def launch_dashboard(self, background=False):
        """Avvia dashboard web"""
        print("\n🚀 AVVIO DASHBOARD WEB")
        print("-" * 40)
        
        try:
            # Cambia directory
            os.chdir(self.project_root)
            
            if background:
                # Avvio in background
                cmd = [sys.executable, str(self.web_api_path)]
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=self.project_root
                )
                
                print(f"🔄 Processo avviato in background (PID: {self.process.pid})")
                
                # Attendi avvio
                for attempt in range(15):
                    time.sleep(1)
                    if not self.is_port_free(5000):
                        print("✅ Dashboard disponibile su http://localhost:5000")
                        print("✅ Dashboard disponibile su http://192.168.178.200:5000")
                        print("\n📝 Credenziali di default:")
                        print("   Username: admin")
                        print("   Password: admin")
                        print("\n⏹️ Per fermare: Ctrl+C o kill processo")
                        return True
                    
                    if self.process.poll() is not None:
                        stdout, stderr = self.process.communicate()
                        print("❌ Processo terminato con errore")
                        if stderr:
                            print(f"Errore: {stderr}")
                        return False
                
                print("❌ Timeout: dashboard non risponde")
                self.stop_dashboard()
                return False
            
            else:
                # Avvio diretto (foreground)
                print("🌐 Avvio dashboard in modalità interattiva...")
                print("📍 URL: http://localhost:5000")
                print("📍 URL: http://192.168.178.200:5000")
                print("⏹️ Premi Ctrl+C per fermare")
                print("-" * 40)
                
                # Gestione signal per cleanup
                signal.signal(signal.SIGINT, self._signal_handler)
                signal.signal(signal.SIGTERM, self._signal_handler)
                
                # Avvia direttamente
                sys.path.insert(0, str(self.project_root / "src"))
                
                # Import e avvio
                import api.web_api as web_api
                # Il main di web_api.py gestirà l'avvio Flask
                
        except KeyboardInterrupt:
            print("\n👋 Dashboard fermata dall'utente")
        except Exception as e:
            print(f"❌ Errore durante avvio: {e}")
    
    def _signal_handler(self, signum, frame):
        """Gestione segnali per cleanup"""
        print(f"\n📶 Ricevuto segnale {signum}")
        self.stop_dashboard()
        sys.exit(0)
    
    def stop_dashboard(self):
        """Ferma dashboard se in esecuzione"""
        if self.process and self.process.poll() is None:
            print("⏹️ Fermata dashboard...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            print("✅ Dashboard fermata")
    
    def get_dashboard_status(self):
        """Verifica stato dashboard"""
        print("📊 STATO DASHBOARD")
        print("-" * 40)
        
        if not self.is_port_free(5000):
            print("✅ Dashboard ATTIVA su porta 5000")
            print("🌐 URL: http://localhost:5000")
            print("🌐 URL: http://192.168.178.200:5000")
            
            # Test connessione
            try:
                import urllib.request
                with urllib.request.urlopen('http://localhost:5000', timeout=5) as response:
                    print(f"📡 Risposta HTTP: {response.status}")
            except Exception as e:
                print(f"⚠️ Errore connessione: {e}")
        else:
            print("❌ Dashboard NON ATTIVA")
            print("💡 Per avviare: python scripts/dashboard_launcher.py --start")
    
    def fix_common_issues(self):
        """Risolve problemi comuni"""
        print("🔧 RISOLUZIONE PROBLEMI COMUNI")
        print("-" * 40)
        
        fixes_applied = []
        
        # 1. Crea configurazione se mancante
        if not self.config_path.exists():
            self.create_default_config()
            fixes_applied.append("Creata configurazione di default")
        
        # 2. Crea directory necessarie
        dirs_to_create = ['logs', 'temp', 'config']
        for dir_name in dirs_to_create:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                dir_path.mkdir(exist_ok=True)
                fixes_applied.append(f"Creata directory: {dir_name}")
        
        # 3. Verifica permessi
        try:
            test_file = self.project_root / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()
        except Exception:
            fixes_applied.append("⚠️ Problemi permessi scrittura (da risolvere manualmente)")
        
        if fixes_applied:
            print("✅ Fix applicati:")
            for fix in fixes_applied:
                print(f"  • {fix}")
        else:
            print("✅ Nessun fix necessario")

def main():
    """Funzione principale"""
    launcher = DashboardLauncher()
    
    # Gestione argomenti
    if len(sys.argv) < 2:
        print("🌐 DASHBOARD LAUNCHER - Sistema Controllo Accessi")
        print("=" * 50)
        print("Uso:")
        print("  python dashboard_launcher.py --check     # Verifica prerequisiti")
        print("  python dashboard_launcher.py --test      # Test avvio rapido")
        print("  python dashboard_launcher.py --start     # Avvia dashboard")
        print("  python dashboard_launcher.py --background # Avvia in background")
        print("  python dashboard_launcher.py --status    # Verifica stato")
        print("  python dashboard_launcher.py --fix       # Risolvi problemi")
        print("=" * 50)
        return
    
    command = sys.argv[1].lower()
    
    if command == '--check':
        launcher.check_prerequisites()
    
    elif command == '--test':
        if launcher.check_prerequisites():
            launcher.test_dashboard_startup()
        else:
            print("❌ Prerequisiti non soddisfatti")
    
    elif command == '--start':
        if launcher.check_prerequisites():
            launcher.launch_dashboard(background=False)
        else:
            print("❌ Prerequisiti non soddisfatti - eseguire --fix")
    
    elif command == '--background':
        if launcher.check_prerequisites():
            success = launcher.launch_dashboard(background=True)
            if success:
                print("✅ Dashboard avviata in background")
            else:
                print("❌ Errore durante avvio")
        else:
            print("❌ Prerequisiti non soddisfatti")
    
    elif command == '--status':
        launcher.get_dashboard_status()
    
    elif command == '--fix':
        launcher.fix_common_issues()
        print("\n🔄 Ricontrollo prerequisiti...")
        launcher.check_prerequisites()
    
    else:
        print(f"❌ Comando non riconosciuto: {command}")
        print("💡 Usa --help per vedere i comandi disponibili")

if __name__ == "__main__":
    main()
