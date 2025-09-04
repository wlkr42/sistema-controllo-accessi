# File: /opt/access_control/scripts/system_diagnostics.py
# Script diagnostica completa sistema controllo accessi

import os
import sys
import json
import subprocess
import importlib
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
import socket
import serial
from typing import Dict, List, Tuple, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemDiagnostics:
    """Sistema diagnostica completo"""
    
    def __init__(self):
        self.project_root = Path("/opt/access_control")
        self.results = {}
        self.errors = []
        self.warnings = []
        
    def run_full_diagnostic(self) -> Dict:
        """Esegue diagnostica completa"""
        print("🔍 SISTEMA CONTROLLO ACCESSI - DIAGNOSTICA COMPLETA")
        print("=" * 60)
        print(f"📅 Data/Ora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Directory: {self.project_root}")
        print("=" * 60)
        
        # Test principali
        tests = [
            ("📁 Struttura File", self.check_file_structure),
            ("🐍 Ambiente Python", self.check_python_environment),
            ("📦 Dipendenze", self.check_dependencies),
            ("🗄️ Database", self.check_database),
            ("🔌 Hardware USB", self.check_usb_devices),
            ("🔧 Servizi Sistema", self.check_system_services),
            ("🌐 Connettività", self.check_network),
            ("🚀 Applicazione Principale", self.check_main_app),
            ("🌐 Dashboard Web", self.check_web_dashboard),
            ("📊 Log e Permessi", self.check_logs_permissions),
        ]
        
        for test_name, test_func in tests:
            print(f"\n{test_name}")
            print("-" * 40)
            try:
                result = test_func()
                self.results[test_name] = result
                if result.get('status') == 'OK':
                    print(f"✅ {result.get('message', 'Test superato')}")
                elif result.get('status') == 'WARNING':
                    print(f"⚠️ {result.get('message', 'Warning rilevato')}")
                    self.warnings.append(f"{test_name}: {result.get('message')}")
                else:
                    print(f"❌ {result.get('message', 'Test fallito')}")
                    self.errors.append(f"{test_name}: {result.get('message')}")
                    
                # Mostra dettagli se presenti
                if 'details' in result:
                    for detail in result['details']:
                        print(f"   • {detail}")
                        
            except Exception as e:
                error_msg = f"Errore durante {test_name}: {e}"
                print(f"❌ {error_msg}")
                self.errors.append(error_msg)
                self.results[test_name] = {'status': 'ERROR', 'message': str(e)}
        
        # Riepilogo finale
        self.print_summary()
        return self.results
    
    def check_file_structure(self) -> Dict:
        """Verifica struttura file progetto"""
        required_files = [
            "src/main.py",
            "src/api/web_api.py",
            "src/hardware/card_reader.py",
            "src/database/database_manager.py",
            "src/external/odoo_partner_connector.py",
            "src/hardware/usb_rly08_controller.py",
            "requirements.txt",
            "config/dashboard_config.json"
        ]
        
        missing_files = []
        existing_files = []
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                existing_files.append(file_path)
            else:
                missing_files.append(file_path)
        
        if missing_files:
            return {
                'status': 'ERROR',
                'message': f"File mancanti: {len(missing_files)}",
                'details': [f"Mancante: {f}" for f in missing_files]
            }
        
        return {
            'status': 'OK',
            'message': f"Struttura completa: {len(existing_files)} file",
            'details': [f"Presente: {f}" for f in existing_files[:5]]  # Primi 5
        }
    
    def check_python_environment(self) -> Dict:
        """Verifica ambiente Python"""
        details = []
        
        # Versione Python
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        details.append(f"Python: {python_version}")
        
        # Virtual environment
        venv_path = self.project_root / "venv"
        if venv_path.exists():
            details.append("Virtual environment: ✅ Presente")
            venv_status = True
        else:
            details.append("Virtual environment: ❌ Mancante")
            venv_status = False
        
        # Path moduli
        project_in_path = str(self.project_root) in sys.path
        details.append(f"Progetto in sys.path: {'✅' if project_in_path else '❌'}")
        
        status = 'OK' if venv_status else 'WARNING'
        return {
            'status': status,
            'message': "Ambiente Python configurato",
            'details': details
        }
    
    def check_dependencies(self) -> Dict:
        """Verifica dipendenze Python"""
        required_modules = [
            'flask', 'flask_cors', 'smartcard', 'serial', 'sqlite3',
            'requests', 'yaml', 'pandas', 'cryptography'
        ]
        
        installed = []
        missing = []
        
        for module in required_modules:
            try:
                if module == 'smartcard':
                    # Test speciale per pyscard
                    importlib.import_module('smartcard.System')
                elif module == 'serial':
                    importlib.import_module('serial')
                else:
                    importlib.import_module(module)
                installed.append(module)
            except ImportError:
                missing.append(module)
        
        if missing:
            return {
                'status': 'ERROR',
                'message': f"Dipendenze mancanti: {len(missing)}",
                'details': [f"Installare: pip install {m}" for m in missing]
            }
        
        return {
            'status': 'OK',
            'message': f"Dipendenze OK: {len(installed)}/{len(required_modules)}",
            'details': [f"✅ {m}" for m in installed[:5]]
        }
    
    def check_database(self) -> Dict:
        """Verifica database SQLite"""
        db_path = self.project_root / "src" / "access.db"
        
        if not db_path.exists():
            return {
                'status': 'ERROR',
                'message': "Database non trovato",
                'details': [f"Percorso: {db_path}"]
            }
        
        details = []
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verifica tabelle
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            details.append(f"Tabelle: {len(tables)}")
            
            # Verifica utenti se presente
            try:
                cursor.execute("SELECT COUNT(*) FROM utenti_autorizzati;")
                user_count = cursor.fetchone()[0]
                details.append(f"Utenti autorizzati: {user_count}")
            except sqlite3.OperationalError:
                details.append("Tabella utenti_autorizzati non trovata")
            
            conn.close()
            
            return {
                'status': 'OK',
                'message': "Database funzionante",
                'details': details
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': f"Errore database: {e}",
                'details': []
            }
    
    def check_usb_devices(self) -> Dict:
        """Verifica dispositivi USB"""
        details = []
        
        # Lettore smart card
        try:
            from smartcard.System import readers
            available_readers = readers()
            if available_readers:
                details.append(f"Lettore smart card: ✅ {len(available_readers)} trovati")
                for reader in available_readers:
                    details.append(f"  • {reader}")
            else:
                details.append("Lettore smart card: ❌ Nessuno trovato")
        except Exception as e:
            details.append(f"Lettore smart card: ❌ Errore: {e}")
        
        # Arduino/dispositivi seriali
        serial_devices = []
        for device in ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyUSB0', '/dev/ttyUSB1']:
            if os.path.exists(device):
                serial_devices.append(device)
        
        if serial_devices:
            details.append(f"Dispositivi seriali: ✅ {len(serial_devices)} trovati")
            for device in serial_devices:
                details.append(f"  • {device}")
        else:
            details.append("Dispositivi seriali: ❌ Nessuno trovato")
        
        # Verifica PCSCD
        try:
            result = subprocess.run(['systemctl', 'is-active', 'pcscd'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip() == 'active':
                details.append("Servizio PCSCD: ✅ Attivo")
            else:
                details.append("Servizio PCSCD: ❌ Non attivo")
        except Exception:
            details.append("Servizio PCSCD: ❓ Non verificabile")
        
        status = 'OK' if (available_readers if 'available_readers' in locals() else False) else 'WARNING'
        return {
            'status': status,
            'message': "Hardware verificato",
            'details': details
        }
    
    def check_system_services(self) -> Dict:
        """Verifica servizi sistema"""
        services_to_check = ['pcscd']
        details = []
        
        for service in services_to_check:
            try:
                result = subprocess.run(['systemctl', 'is-active', service], 
                                      capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip() == 'active':
                    details.append(f"{service}: ✅ Attivo")
                else:
                    details.append(f"{service}: ❌ Non attivo")
            except Exception as e:
                details.append(f"{service}: ❓ Errore verifica: {e}")
        
        return {
            'status': 'OK',
            'message': "Servizi verificati",
            'details': details
        }
    
    def check_network(self) -> Dict:
        """Verifica connettività di rete"""
        details = []
        
        # Test connettività base
        hosts_to_test = [
            ('8.8.8.8', 'Google DNS'),
            ('app.calabramaceri.it', 'Server Odoo')
        ]
        
        for host, description in hosts_to_test:
            try:
                result = subprocess.run(['ping', '-c', '1', '-W', '3', host], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    details.append(f"{description}: ✅ Raggiungibile")
                else:
                    details.append(f"{description}: ❌ Non raggiungibile")
            except Exception as e:
                details.append(f"{description}: ❓ Errore test: {e}")
        
        # Test porta specifica per dashboard
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('localhost', 5000))
            sock.close()
            
            if result == 0:
                details.append("Porta 5000: ✅ Aperta (Dashboard web attiva)")
            else:
                details.append("Porta 5000: ❌ Chiusa (Dashboard web non attiva)")
        except Exception as e:
            details.append(f"Porta 5000: ❓ Errore test: {e}")
        
        return {
            'status': 'OK',
            'message': "Connettività verificata",
            'details': details
        }
    
    def check_main_app(self) -> Dict:
        """Verifica applicazione principale"""
        main_path = self.project_root / "src" / "main.py"
        
        if not main_path.exists():
            return {
                'status': 'ERROR',
                'message': "main.py non trovato",
                'details': []
            }
        
        details = []
        
        # Verifica sintassi
        try:
            with open(main_path, 'r') as f:
                content = f.read()
            
            compile(content, str(main_path), 'exec')
            details.append("Sintassi Python: ✅ Valida")
        except SyntaxError as e:
            details.append(f"Sintassi Python: ❌ Errore: {e}")
            return {
                'status': 'ERROR',
                'message': "Errore sintassi main.py",
                'details': details
            }
        
        # Verifica import principali
        required_imports = ['CardReader', 'DatabaseManager', 'OdooPartnerConnector']
        for imp in required_imports:
            if imp in content:
                details.append(f"Import {imp}: ✅ Presente")
            else:
                details.append(f"Import {imp}: ❌ Mancante")
        
        return {
            'status': 'OK',
            'message': "Applicazione principale OK",
            'details': details
        }
    
    def check_web_dashboard(self) -> Dict:
        """Verifica dashboard web"""
        web_api_path = self.project_root / "src" / "api" / "web_api.py"
        
        if not web_api_path.exists():
            return {
                'status': 'ERROR',
                'message': "web_api.py non trovato",
                'details': [f"Percorso: {web_api_path}"]
            }
        
        details = []
        
        # Verifica sintassi
        try:
            with open(web_api_path, 'r') as f:
                content = f.read()
            
            compile(content, str(web_api_path), 'exec')
            details.append("Sintassi Python: ✅ Valida")
        except SyntaxError as e:
            details.append(f"Sintassi Python: ❌ Errore: {e}")
            return {
                'status': 'ERROR',
                'message': "Errore sintassi web_api.py",
                'details': details
            }
        
        # Verifica configurazione
        config_path = self.project_root / "config" / "dashboard_config.json"
        if config_path.exists():
            details.append("Config dashboard: ✅ Presente")
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                details.append(f"Config valida: {len(config)} chiavi")
            except json.JSONDecodeError as e:
                details.append(f"Config dashboard: ❌ JSON non valido: {e}")
        else:
            details.append("Config dashboard: ❌ Mancante")
        
        # Test porta 5000
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', 5000))
            sock.close()
            
            if result == 0:
                details.append("Servizio web: ✅ In esecuzione su porta 5000")
                status = 'OK'
            else:
                details.append("Servizio web: ❌ Non in esecuzione su porta 5000")
                status = 'ERROR'
        except Exception as e:
            details.append(f"Test porta 5000: ❓ Errore: {e}")
            status = 'WARNING'
        
        return {
            'status': status,
            'message': "Dashboard web verificata",
            'details': details
        }
    
    def check_logs_permissions(self) -> Dict:
        """Verifica log e permessi"""
        details = []
        
        # Verifica directory logs
        logs_dir = self.project_root / "logs"
        if logs_dir.exists():
            details.append("Directory logs: ✅ Presente")
            log_files = list(logs_dir.glob("*.log"))
            details.append(f"File log: {len(log_files)} trovati")
        else:
            details.append("Directory logs: ❌ Mancante")
        
        # Verifica permessi scrittura
        try:
            test_file = self.project_root / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()
            details.append("Permessi scrittura: ✅ OK")
        except Exception as e:
            details.append(f"Permessi scrittura: ❌ Errore: {e}")
        
        # Verifica owner files
        main_file = self.project_root / "src" / "main.py"
        if main_file.exists():
            stat_info = main_file.stat()
            details.append(f"Owner main.py: UID {stat_info.st_uid}")
        
        return {
            'status': 'OK',
            'message': "Log e permessi verificati",
            'details': details
        }
    
    def print_summary(self):
        """Stampa riepilogo diagnostica"""
        print("\n" + "=" * 60)
        print("📊 RIEPILOGO DIAGNOSTICA")
        print("=" * 60)
        
        total_tests = len(self.results)
        ok_tests = len([r for r in self.results.values() if r.get('status') == 'OK'])
        warning_tests = len([r for r in self.results.values() if r.get('status') == 'WARNING'])
        error_tests = len([r for r in self.results.values() if r.get('status') == 'ERROR'])
        
        print(f"✅ Test superati: {ok_tests}/{total_tests}")
        print(f"⚠️ Warning: {warning_tests}")
        print(f"❌ Errori: {error_tests}")
        
        if self.errors:
            print(f"\n🚨 ERRORI CRITICI ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        if self.warnings:
            print(f"\n⚠️ WARNING ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        print("\n💡 AZIONI CONSIGLIATE:")
        if error_tests > 0:
            print("  • Risolvere errori critici prima del deploy")
        if warning_tests > 0:
            print("  • Verificare warning per ottimizzazione")
        if ok_tests == total_tests:
            print("  • Sistema pronto per l'uso! 🚀")
        
        print("\n📞 COMANDI UTILI:")
        print("  • Logs applicazione: tail -f /opt/access_control/logs/*.log")
        print("  • Riavvio PCSCD: sudo systemctl restart pcscd")
        print("  • Test lettore: python scripts/test_card_reader.py")
        print("  • Avvio dashboard: python src/api/web_api.py")
        
        print("=" * 60)
    
    def generate_report(self) -> str:
        """Genera report JSON per analisi automatica"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'results': self.results,
            'summary': {
                'total_tests': len(self.results),
                'ok_tests': len([r for r in self.results.values() if r.get('status') == 'OK']),
                'warning_tests': len([r for r in self.results.values() if r.get('status') == 'WARNING']),
                'error_tests': len([r for r in self.results.values() if r.get('status') == 'ERROR']),
                'errors': self.errors,
                'warnings': self.warnings
            }
        }
        
        return json.dumps(report, indent=2, ensure_ascii=False)

def main():
    """Funzione principale"""
    try:
        diagnostics = SystemDiagnostics()
        
        # Esegui diagnostica completa
        results = diagnostics.run_full_diagnostic()
        
        # Salva report se richiesto
        if len(sys.argv) > 1 and sys.argv[1] == '--save-report':
            report_path = Path("/opt/access_control/logs/diagnostic_report.json")
            report_path.parent.mkdir(exist_ok=True)
            with open(report_path, 'w') as f:
                f.write(diagnostics.generate_report())
            print(f"\n📄 Report salvato: {report_path}")
        
        # Exit code basato sui risultati
        if any(r.get('status') == 'ERROR' for r in results.values()):
            sys.exit(1)  # Errori critici
        elif any(r.get('status') == 'WARNING' for r in results.values()):
            sys.exit(2)  # Warning
        else:
            sys.exit(0)  # Tutto OK
            
    except KeyboardInterrupt:
        print("\n👋 Diagnostica interrotta dall'utente")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Errore critico durante diagnostica: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
