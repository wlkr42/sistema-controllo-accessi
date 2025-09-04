# File: /opt/access_control/src/core/config.py
# Gestione configurazioni multi-ambiente

import os
import yaml
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class HardwareConfig:
    """Configurazioni hardware"""
    arduino_port: str = "/dev/ttyACM0"
    arduino_baudrate: int = 9600
    relay_port: str = "/dev/ttyUSB0"
    relay_baudrate: int = 19200
    card_reader_timeout: int = 10
    gate_open_duration: int = 5

@dataclass
class DatabaseConfig:
    """Configurazioni database"""
    path: str = "/opt/access_control/src/access.db"
    backup_interval: int = 86400  # 24 ore
    max_backups: int = 30
    vacuum_interval: int = 604800  # 7 giorni

@dataclass
class ServerConfig:
    """Configurazioni server centrale"""
    url: str = "https://server-centrale.example.com/api"
    username: str = "terminal_001"
    password: str = "changeme"
    sync_interval: int = 3600  # 1 ora
    timeout: int = 30
    retry_attempts: int = 3
    ssl_verify: bool = True

@dataclass
class SecurityConfig:
    """Configurazioni sicurezza"""
    encrypt_database: bool = True
    max_failed_attempts: int = 5
    lockout_duration: int = 300  # 5 minuti
    session_timeout: int = 1800  # 30 minuti
    audit_log: bool = True

@dataclass
class LoggingConfig:
    """Configurazioni logging"""
    level: str = "INFO"
    max_size: str = "10MB"
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    console_output: bool = True

@dataclass
class WebConfig:
    """Configurazioni interfaccia web"""
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    secret_key: str = "changeme-in-production"
    admin_user: str = "admin"
    admin_password: str = "changeme"

@dataclass
class SystemConfig:
    """Configurazione sistema completa"""
    environment: str = "production"
    terminal_id: str = "TERM-001"
    installation_date: str = ""
    version: str = "1.0.0"
    debug_mode: bool = False

    hardware: Optional[HardwareConfig] = None
    database: Optional[DatabaseConfig] = None
    server: Optional[ServerConfig] = None
    security: Optional[SecurityConfig] = None
    logging: Optional[LoggingConfig] = None
    web: Optional[WebConfig] = None

    def __post_init__(self):
        if self.hardware is None:
            self.hardware = HardwareConfig()
        if self.database is None:
            self.database = DatabaseConfig()
        if self.server is None:
            self.server = ServerConfig()
        if self.security is None:
            self.security = SecurityConfig()
        if self.logging is None:
            self.logging = LoggingConfig()
        if self.web is None:
            self.web = WebConfig()
        if not self.installation_date:
            self.installation_date = datetime.now().isoformat()

class ConfigManager:
    """Gestore configurazioni multi-ambiente e hardware dinamico"""
    
    def __init__(self, config_dir: str = "/opt/access_control/config"):
        self.config_dir = Path(config_dir)
        self.config: SystemConfig = SystemConfig()
        self.environment = os.getenv('ACCESS_CONTROL_ENV', 'production')
        
        # Percorsi file configurazione
        self.base_config_file = self.config_dir / "base.yml"
        self.env_config_file = self.config_dir / "environments" / f"{self.environment}.yml"
        self.local_config_file = self.config_dir / "local.yml"
        self.secrets_file = self.config_dir / ".secrets.yml"
        self.device_assignments_file = self.config_dir / "device_assignments.json"
        self.device_assignments = {}
        
        self.load_configuration()
        self.load_device_assignments()
    
    def load_configuration(self):
        """Carica configurazione da file multipli con precedenza"""
        try:
            # 1. Configurazione base
            if self.base_config_file.exists():
                self._merge_config(self._load_yaml(self.base_config_file))
            
            # 2. Configurazione ambiente specifico
            if self.env_config_file.exists():
                self._merge_config(self._load_yaml(self.env_config_file))
            
            # 3. Configurazione locale (override)
            if self.local_config_file.exists():
                self._merge_config(self._load_yaml(self.local_config_file))
            
            # 4. Secrets (non in version control)
            if self.secrets_file.exists():
                self._merge_config(self._load_yaml(self.secrets_file))
            
            # 5. Variabili ambiente (precedenza massima)
            self._load_from_environment()
            
            logger.info(f"Configurazione caricata per ambiente: {self.environment}")
            
        except Exception as e:
            logger.error(f"Errore caricamento configurazione: {e}")
            # Usa configurazione di default se caricamento fallisce
            self.config = SystemConfig()

    def load_device_assignments(self):
        """Carica assegnazioni hardware dinamiche (lettore, relay, ecc.)"""
        try:
            if self.device_assignments_file.exists():
                import json
                with open(self.device_assignments_file, "r", encoding="utf-8") as f:
                    self.device_assignments = json.load(f)
            else:
                self.device_assignments = {}
        except Exception as e:
            logger.error(f"Errore caricamento device_assignments.json: {e}")
            self.device_assignments = {}

    def save_device_assignments(self, assignments: dict):
        """Salva assegnazioni hardware dinamiche"""
        try:
            import json
            self.device_assignments = assignments
            with open(self.device_assignments_file, "w", encoding="utf-8") as f:
                json.dump(assignments, f, indent=2)
            logger.info("Assegnazioni hardware salvate in device_assignments.json")
            return True
        except Exception as e:
            logger.error(f"Errore salvataggio device_assignments.json: {e}")
            return False

    def get_hardware_assignment(self, device_type: str) -> dict:
        """Restituisce la configurazione hardware dinamica per il tipo richiesto (card_reader, relay_controller)"""
        try:
            return self.device_assignments.get("assignments", {}).get(device_type, {})
        except Exception as e:
            logger.error(f"Errore lettura hardware assignment {device_type}: {e}")
            return {}

    def save_hardware_assignment(self, device_type: str, assignment: dict):
        """Aggiorna la configurazione hardware per un tipo specifico"""
        try:
            if "assignments" not in self.device_assignments:
                self.device_assignments["assignments"] = {}
            self.device_assignments["assignments"][device_type] = assignment
            return self.save_device_assignments(self.device_assignments)
        except Exception as e:
            logger.error(f"Errore aggiornamento hardware assignment {device_type}: {e}")
            return False
    
    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Carica file YAML"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Impossibile caricare {file_path}: {e}")
            return {}
    
    def _merge_config(self, config_dict: Dict[str, Any]):
        """Merge configurazione nel sistema config"""
        if not config_dict:
            return
        
        # Update configurazioni specifiche
        if 'hardware' in config_dict:
            self._update_dataclass(self.config.hardware, config_dict['hardware'])
        
        if 'database' in config_dict:
            self._update_dataclass(self.config.database, config_dict['database'])
        
        if 'server' in config_dict:
            self._update_dataclass(self.config.server, config_dict['server'])
        
        if 'security' in config_dict:
            self._update_dataclass(self.config.security, config_dict['security'])
        
        if 'logging' in config_dict:
            self._update_dataclass(self.config.logging, config_dict['logging'])
        
        if 'web' in config_dict:
            self._update_dataclass(self.config.web, config_dict['web'])
        
        # Update configurazione sistema
        for key, value in config_dict.items():
            if hasattr(self.config, key) and key not in ['hardware', 'database', 'server', 'security', 'logging', 'web']:
                setattr(self.config, key, value)
    
    def _update_dataclass(self, target_obj, source_dict: Dict[str, Any]):
        """Aggiorna dataclass con valori da dizionario"""
        for key, value in source_dict.items():
            if hasattr(target_obj, key):
                setattr(target_obj, key, value)
    
    def _load_from_environment(self):
        """Carica configurazioni da variabili ambiente"""
        env_mappings = {
            'ACCESS_CONTROL_ENV': 'environment',
            'ACCESS_CONTROL_TERMINAL_ID': 'terminal_id',
            'ACCESS_CONTROL_DEBUG': 'debug_mode',
            'ACCESS_CONTROL_ARDUINO_PORT': 'hardware.arduino_port',
            'ACCESS_CONTROL_RELAY_PORT': 'hardware.relay_port',
            'ACCESS_CONTROL_DB_PATH': 'database.path',
            'ACCESS_CONTROL_SERVER_URL': 'server.url',
            'ACCESS_CONTROL_SERVER_USER': 'server.username',
            'ACCESS_CONTROL_SERVER_PASS': 'server.password',
            'ACCESS_CONTROL_WEB_PORT': 'web.port',
            'ACCESS_CONTROL_WEB_HOST': 'web.host',
            'ACCESS_CONTROL_SECRET_KEY': 'web.secret_key',
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested_attr(config_path, value)
    
    def _set_nested_attr(self, path: str, value: str):
        """Imposta attributo nested usando dot notation"""
        parts = path.split('.')
        obj = self.config
        
        for part in parts[:-1]:
            obj = getattr(obj, part)
        
        # Conversione tipo automatica
        final_attr = parts[-1]
        if hasattr(obj, final_attr):
            current_value = getattr(obj, final_attr)
            if isinstance(current_value, bool):
                value = value.lower() in ('true', '1', 'yes', 'on')
            elif isinstance(current_value, int):
                value = int(value)
            elif isinstance(current_value, float):
                value = float(value)
            
            setattr(obj, final_attr, value)
    
    def save_configuration(self, file_path: Optional[Path] = None):
        """Salva configurazione su file"""
        if file_path is None:
            file_path = self.local_config_file
        
        try:
            # Crea directory se non esiste
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Converte in dizionario
            config_dict = asdict(self.config)
            
            # Salva in YAML
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            
            logger.info(f"Configurazione salvata in {file_path}")
            return True
        except Exception as e:
            logger.error(f"Errore salvataggio configurazione: {e}")
            return False
    
    def get_config(self) -> SystemConfig:
        """Restituisce configurazione corrente"""
        return self.config
    
    def set_config_value(self, path: str, value: Any):
        """Imposta valore configurazione usando dot notation"""
        try:
            self._set_nested_attr(path, value)
            return True
        except Exception as e:
            logger.error(f"Errore impostazione {path}: {e}")
            return False
    
    def validate_configuration(self) -> list:
        """Valida configurazione corrente"""
        errors = []
        
        # Validazione porte hardware
        if not self.config.hardware.arduino_port.startswith('/dev/'):
            errors.append(f"Porta Arduino non valida: {self.config.hardware.arduino_port}")
        
        if not self.config.hardware.relay_port.startswith('/dev/'):
            errors.append(f"Porta relay non valida: {self.config.hardware.relay_port}")
        
        # Validazione database path
        db_dir = Path(self.config.database.path).parent
        if not db_dir.exists():
            errors.append(f"Directory database non esiste: {db_dir}")
        
        # Validazione server URL
        if not self.config.server.url.startswith(('http://', 'https://')):
            errors.append("URL server deve iniziare con http:// o https://")
        
        # Validazione credenziali default
        if self.config.server.password == "changeme":
            errors.append("Password server deve essere cambiata")
        
        if self.config.web.secret_key == "changeme-in-production":
            errors.append("Secret key web deve essere cambiata")
        
        return errors
    
    def get_hardware_config(self) -> HardwareConfig:
        """Configurazione hardware"""
        if self.config.hardware is None:
            self.config.hardware = HardwareConfig()
        return self.config.hardware

    def get_database_config(self) -> DatabaseConfig:
        """Configurazione database"""
        if self.config.database is None:
            self.config.database = DatabaseConfig()
        return self.config.database

    def get_server_config(self) -> ServerConfig:
        """Configurazione server"""
        if self.config.server is None:
            self.config.server = ServerConfig()
        return self.config.server

    def get_security_config(self) -> SecurityConfig:
        """Configurazione sicurezza"""
        if self.config.security is None:
            self.config.security = SecurityConfig()
        return self.config.security

    def get_logging_config(self) -> LoggingConfig:
        """Configurazione logging"""
        if self.config.logging is None:
            self.config.logging = LoggingConfig()
        return self.config.logging

    def get_web_config(self) -> WebConfig:
        """Configurazione web"""
        if self.config.web is None:
            self.config.web = WebConfig()
        return self.config.web

# Singleton pattern
_config_manager = None

def get_config_manager() -> ConfigManager:
    """Restituisce istanza singleton ConfigManager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_config() -> SystemConfig:
    """Shortcut per ottenere configurazione sistema"""
    return get_config_manager().get_config()
