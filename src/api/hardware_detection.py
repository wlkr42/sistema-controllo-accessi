# File: /opt/access_control/src/api/hardware_detection.py
# Rilevamento hardware SEMPLICE con comandi Linux standard

import subprocess
import re
import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

def get_hardware_info() -> Dict[str, Any]:
    """
    Rilevamento hardware semplice: solo comandi Linux standard
    
    Returns:
        Dict: Hardware rilevato + porte seriali
    """
    try:
        # PARTE 1: Dispositivi USB (lsusb)
        usb_devices = get_usb_devices()
        
        # PARTE 2: Porte seriali (ls /dev/tty*)
        serial_ports = get_serial_ports()
        
        # PARTE 3: Dispositivi HID (/dev/hidraw*)
        hid_devices = get_hid_devices()
        
        return {
            'success': True,
            'usb_devices': usb_devices,
            'serial_ports': serial_ports,
            'hid_devices': hid_devices,
            'total_devices': len(usb_devices),
            'message': f"Rilevati {len(usb_devices)} dispositivi USB, {len(serial_ports)} porte seriali, {len(hid_devices)} dispositivi HID"
        }
    
    except Exception as e:
        logger.error(f"Errore rilevamento: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'usb_devices': [],
            'serial_ports': [],
            'hid_devices': []
        }

def get_usb_devices() -> List[Dict[str, Any]]:
    """Esegue lsusb e restituisce tutti i dispositivi"""
    devices = []
    
    try:
        # lsusb base
        result = subprocess.run(['lsusb'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True, timeout=10)
        
        if result.returncode != 0:
            return devices
        
        for line in result.stdout.splitlines():
            # Parse: Bus 001 Device 003: ID 23d8:0285 CREATOR(CHINA)TECH CO.,LTD CRT-285
            match = re.match(r'Bus (\d+) Device (\d+): ID ([0-9a-f]{4}):([0-9a-f]{4}) (.*)', line)
            if match:
                bus, device, vendor_id, product_id, description = match.groups()
                
                # Filtra dispositivi di sistema
                if is_system_device(description):
                    continue
                
                devices.append({
                    'bus': bus,
                    'device': device,
                    'vendor_id': f"0x{vendor_id}",
                    'product_id': f"0x{product_id}", 
                    'description': description.strip(),
                    'raw_line': line.strip(),
                    'device_id': f"{vendor_id}:{product_id}"
                })
        
        return devices
    
    except Exception as e:
        logger.error(f"Errore lsusb: {str(e)}")
        return devices

def get_serial_ports() -> List[Dict[str, Any]]:
    """Trova tutte le porte seriali con ls /dev/tty*"""
    ports = []
    
    try:
        # Lista porte ttyUSB* e ttyACM*
        for pattern in ['/dev/ttyUSB*', '/dev/ttyACM*']:
            result = subprocess.run(f'ls {pattern} 2>/dev/null || true', 
                                  stdout=subprocess.PIPE, 
                                  text=True, shell=True, timeout=5)
            
            for port_path in result.stdout.strip().split():
                if port_path and port_path.startswith('/dev/tty'):
                    # Test se porta è accessibile
                    accessible = test_port_access(port_path)
                    
                    ports.append({
                        'port': port_path,
                        'accessible': accessible,
                        'type': get_port_type(port_path)
                    })
        
        return ports
    
    except Exception as e:
        logger.error(f"Errore porte seriali: {str(e)}")
        return ports

def get_hid_devices() -> List[Dict[str, Any]]:
    """Trova dispositivi HID con ls /dev/hidraw*"""
    devices = []
    
    try:
        result = subprocess.run('ls /dev/hidraw* 2>/dev/null || true', 
                              stdout=subprocess.PIPE, 
                              text=True, shell=True, timeout=5)
        
        for hidraw_path in result.stdout.strip().split():
            if hidraw_path and hidraw_path.startswith('/dev/hidraw'):
                devices.append({
                    'device': hidraw_path,
                    'accessible': True,  # Assumiamo accessibile
                    'type': 'HID'
                })
        
        return devices
    
    except Exception as e:
        logger.error(f"Errore dispositivi HID: {str(e)}")
        return devices

def is_system_device(description: str) -> bool:
    """Filtra dispositivi di sistema"""
    system_terms = [
        'linux foundation', 'root hub', 'host controller', 
        'hub', 'bluetooth', 'wireless', 'xhci', 'ehci'
    ]
    desc_lower = description.lower()
    return any(term in desc_lower for term in system_terms)

def test_port_access(port_path: str) -> bool:
    """Testa se porta è accessibile"""
    try:
        result = subprocess.run(['stty', '-F', port_path, 'size'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              timeout=2)
        return result.returncode == 0
    except:
        return False

def get_port_type(port_path: str) -> str:
    """Determina tipo porta dal nome"""
    if 'ttyUSB' in port_path:
        return 'USB-Serial'
    elif 'ttyACM' in port_path:
        return 'USB-CDC'
    else:
        return 'Serial'

# PARTE 2: CONFIGURAZIONE DISPOSITIVI
def load_device_assignments() -> Dict[str, Any]:
    """Carica assegnazioni dispositivi salvate"""
    try:
        # Prova a leggere file di configurazione
        config_file = '/opt/access_control/config/device_assignments.json'
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Configurazione di default
            return {
                'card_reader': {
                    'device_id': None,
                    'device_path': None,
                    'device_type': 'auto'
                },
                'relay_controller': {
                    'device_id': None, 
                    'device_path': None,
                    'device_type': 'auto'
                },
                'assignments': {}
            }
    except Exception as e:
        logger.error(f"Errore caricamento configurazione: {str(e)}")
        return {'card_reader': {}, 'relay_controller': {}, 'assignments': {}}

def save_device_assignments(assignments: Dict[str, Any]) -> Dict[str, Any]:
    """Salva assegnazioni dispositivi"""
    try:
        import os
        config_dir = '/opt/access_control/config'
        os.makedirs(config_dir, exist_ok=True)
        
        config_file = f'{config_dir}/device_assignments.json'
        with open(config_file, 'w') as f:
            json.dump(assignments, f, indent=2)
        
        return {'success': True, 'message': 'Configurazione salvata'}
    
    except Exception as e:
        logger.error(f"Errore salvataggio configurazione: {str(e)}")
        return {'success': False, 'error': str(e)}

def test_device_connection(device_info: Dict[str, Any]) -> Dict[str, Any]:
    """Testa connessione a dispositivo specifico"""
    try:
        device_id = device_info.get('device_id')
        device_path = device_info.get('device_path')
        device_type = device_info.get('assigned_function')
        reader_type = device_info.get('reader_type', 'CRT-285')
        
        result = {
            'device_id': device_id,
            'device_path': device_path,
            'device_type': device_type,
            'tests': []
        }
        
        # Test base: verifica se dispositivo esiste
        if device_path and device_path.startswith('/dev/'):
            import os
            exists = os.path.exists(device_path)
            result['tests'].append({
                'test': 'device_exists',
                'success': exists,
                'message': f"Dispositivo {device_path} {'trovato' if exists else 'non trovato'}"
            })
            
            if exists:
                # Test accesso
                accessible = test_port_access(device_path)
                result['tests'].append({
                    'test': 'device_access',
                    'success': accessible,
                    'message': f"Dispositivo {device_path} {'accessibile' if accessible else 'non accessibile'}"
                })
        
        # Test specifici per tipo dispositivo
        if device_type == 'card_reader':
            # Test specifico per CRT-285
            if reader_type == 'CRT-285' or 'CRT' in str(reader_type):
                crt_test = test_crt285_reader(device_path)
                result['tests'].append({
                    'test': 'crt285_connection',
                    'success': crt_test,
                    'message': f"Lettore CRT-285 {'connesso e funzionante' if crt_test else 'non risponde'}"
                })
            else:
                # Test lettore tessere PC/SC
                pcsc_test = test_pcsc_reader()
                result['tests'].append({
                    'test': 'pcsc_service',
                    'success': pcsc_test,
                    'message': f"Servizio PC/SC {'disponibile' if pcsc_test else 'non disponibile'}"
                })
        
        elif device_type == 'relay_controller':
            # Test controller relè
            if device_path:
                relay_test = test_relay_communication(device_path)
                result['tests'].append({
                    'test': 'relay_communication',
                    'success': relay_test,
                    'message': f"Comunicazione relè {'OK' if relay_test else 'fallita'}"
                })
        
        # Determina successo complessivo
        result['success'] = len(result['tests']) > 0 and all(t['success'] for t in result['tests'])
        result['message'] = 'Test completato con successo' if result['success'] else 'Alcuni test sono falliti'
        
        return result
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'Errore durante test: {str(e)}'
        }

def test_crt285_reader(device_path: str = None) -> bool:
    """Test specifico per lettore CRT-285"""
    try:
        # Importa e testa il lettore CRT-285
        import sys
        import os
        sys.path.insert(0, '/opt/access_control/src')
        from hardware.crt285_reader import CRT285Reader
        
        reader = CRT285Reader(
            device_path=device_path,
            auto_test=False,
            strict_validation=False
        )
        
        # Verifica che la libreria sia caricata
        if reader.lib:
            reader.stop()
            return True
        return False
    except Exception as e:
        logger.debug(f"Test CRT-285 fallito: {e}")
        return False

def test_pcsc_reader() -> bool:
    """Test rapido servizio PC/SC"""
    try:
        result = subprocess.run(['pcsc_scan', '-n'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              timeout=5)
        return result.returncode == 0
    except:
        return False

def test_relay_communication(device_path: str) -> bool:
    """Test comunicazione controller relè"""
    try:
        # Configura porta per comunicazione
        result = subprocess.run(['stty', '-F', device_path, '19200', 'cs8', '-parenb'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              timeout=5)
        return result.returncode == 0
    except:
        return False

# Funzioni di compatibilità per API esistente
def detect_hardware() -> Dict[str, Any]:
    """Funzione principale per API"""
    return get_hardware_info()

def load_hardware_config(get_db_connection) -> Dict[str, Any]:
    """Carica configurazione dispositivi"""
    assignments = load_device_assignments()
    return {
        'success': True,
        'config': assignments
    }

def save_hardware_config(config_data: Dict[str, Any], get_db_connection) -> Dict[str, Any]:
    """Salva configurazione dispositivi"""
    return save_device_assignments(config_data)

def test_hardware_connection(hardware_type: str, device_path: str, **kwargs) -> Dict[str, Any]:
    """Test connessione hardware"""
    device_info = {
        'device_path': device_path,
        'assigned_function': hardware_type,
        'device_id': kwargs.get('device_id', 'unknown')
    }
    return test_device_connection(device_info)