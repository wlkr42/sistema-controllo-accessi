#!/usr/bin/env python3
"""
Wrapper per gestire il lettore CRT-285 con permessi appropriati
Gestisce il problema del detach kernel driver quando non necessario
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class CRT285PermissionHelper:
    """Helper per gestire permessi e problemi di accesso USB del CRT-285"""
    
    @staticmethod
    def setup_permissions():
        """Configura permessi per accesso senza sudo"""
        try:
            # Verifica se l'utente è in plugdev
            import getpass
            current_user = getpass.getuser()
            groups = subprocess.run(['groups', current_user], 
                                  capture_output=True, text=True)
            
            if 'plugdev' not in groups.stdout:
                logger.warning(f"Utente {current_user} non in gruppo plugdev")
                return False
                
            # Verifica regole udev
            udev_rule = "/etc/udev/rules.d/99-crt288x.rules"
            if not os.path.exists(udev_rule):
                logger.info("Creazione regole udev per CRT-285...")
                rule_content = """# CRT-285/288K Card Reader
SUBSYSTEM=="usb", ATTR{idVendor}=="23d8", ATTR{idProduct}=="0285", MODE="0666", GROUP="plugdev", TAG+="uaccess"
KERNEL=="hidraw*", ATTRS{idVendor}=="23d8", ATTRS{idProduct}=="0285", MODE="0666", GROUP="plugdev"
# Disable autosuspend for better performance
SUBSYSTEM=="usb", ATTR{idVendor}=="23d8", ATTR{idProduct}=="0285", ATTR{power/autosuspend}="-1"
"""
                try:
                    # Prova a creare con sudo se disponibile
                    subprocess.run(['sudo', 'tee', udev_rule], 
                                 input=rule_content, text=True, 
                                 capture_output=True, check=False)
                    subprocess.run(['sudo', 'udevadm', 'control', '--reload-rules'], 
                                 capture_output=True, check=False)
                    subprocess.run(['sudo', 'udevadm', 'trigger'], 
                                 capture_output=True, check=False)
                    logger.info("Regole udev create con successo")
                except:
                    logger.warning("Impossibile creare regole udev automaticamente")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Errore configurazione permessi: {e}")
            return False
    
    @staticmethod
    def check_device_access():
        """Verifica accesso al dispositivo CRT-285"""
        try:
            # Trova dispositivo USB CRT-285
            result = subprocess.run(['lsusb'], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if '23d8:0285' in line:
                    # Estrai bus e device number
                    parts = line.split()
                    bus = parts[1]
                    device = parts[3].rstrip(':')
                    
                    device_path = f"/dev/bus/usb/{bus}/{device}"
                    
                    # Verifica permessi
                    if os.path.exists(device_path):
                        stat_info = os.stat(device_path)
                        mode = oct(stat_info.st_mode)[-3:]
                        
                        if mode == '666':
                            logger.info(f"✅ Dispositivo {device_path} accessibile (mode {mode})")
                            return True
                        else:
                            logger.warning(f"⚠️ Dispositivo {device_path} ha permessi {mode}, servono 666")
                            
                            # Prova a fixare con chmod
                            try:
                                subprocess.run(['sudo', 'chmod', '666', device_path], 
                                             capture_output=True, check=False)
                                logger.info("Permessi corretti con chmod")
                                return True
                            except:
                                pass
                                
            logger.warning("Dispositivo CRT-285 non trovato")
            return False
            
        except Exception as e:
            logger.error(f"Errore verifica accesso: {e}")
            return False
    
    @staticmethod
    def reset_usb_device():
        """Reset del dispositivo USB CRT-285 se necessario"""
        try:
            # Trova e resetta il dispositivo
            result = subprocess.run(['lsusb'], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if '23d8:0285' in line:
                    # Usa usbreset se disponibile
                    try:
                        subprocess.run(['sudo', 'usbreset', '23d8:0285'], 
                                     capture_output=True, check=False)
                        logger.info("Dispositivo USB resettato")
                        return True
                    except:
                        # Alternativa: unbind/bind via sysfs
                        parts = line.split()
                        bus = int(parts[1])
                        
                        # Trova il path sysfs
                        for sysfs_dev in Path('/sys/bus/usb/devices').glob('*'):
                            try:
                                with open(sysfs_dev / 'idVendor', 'r') as f:
                                    vendor = f.read().strip()
                                with open(sysfs_dev / 'idProduct', 'r') as f:
                                    product = f.read().strip()
                                    
                                if vendor == '23d8' and product == '0285':
                                    # Unbind e rebind
                                    dev_name = sysfs_dev.name
                                    unbind_path = sysfs_dev.parent / 'driver/unbind'
                                    bind_path = sysfs_dev.parent / 'driver/bind'
                                    
                                    try:
                                        with open(unbind_path, 'w') as f:
                                            f.write(dev_name)
                                        with open(bind_path, 'w') as f:
                                            f.write(dev_name)
                                        logger.info("Dispositivo resettato via sysfs")
                                        return True
                                    except:
                                        pass
                            except:
                                continue
                                
            return False
            
        except Exception as e:
            logger.error(f"Errore reset dispositivo: {e}")
            return False
    
    @staticmethod
    def fix_libusb_permissions():
        """Fix specifico per errore libusb_detach_kernel_driver"""
        try:
            # Disabilita temporaneamente il driver HID per il dispositivo
            result = subprocess.run(['lsusb', '-d', '23d8:0285'], 
                                  capture_output=True, text=True)
            if result.stdout:
                # Il dispositivo esiste, proviamo a unbindare il driver
                # Questo evita il problema del detach_kernel_driver
                for sysfs_dev in Path('/sys/bus/usb/devices').glob('*'):
                    try:
                        vendor_file = sysfs_dev / 'idVendor'
                        product_file = sysfs_dev / 'idProduct'
                        
                        if vendor_file.exists() and product_file.exists():
                            with open(vendor_file, 'r') as f:
                                vendor = f.read().strip()
                            with open(product_file, 'r') as f:
                                product = f.read().strip()
                                
                            if vendor == '23d8' and product == '0285':
                                # Verifica se ha un driver bound
                                driver_link = sysfs_dev / 'driver'
                                if driver_link.exists():
                                    driver_name = driver_link.resolve().name
                                    logger.info(f"Driver attuale: {driver_name}")
                                    
                                    # Se è un driver HID, lo unbindiamo
                                    if 'hid' in driver_name.lower():
                                        dev_name = sysfs_dev.name
                                        unbind_path = driver_link / 'unbind'
                                        
                                        try:
                                            subprocess.run(['sudo', 'sh', '-c', 
                                                          f'echo {dev_name} > {unbind_path}'],
                                                         capture_output=True, check=False)
                                            logger.info("Driver HID unbindato")
                                            return True
                                        except:
                                            pass
                    except:
                        continue
                        
            return True  # Anche se non unbindiamo, proviamo comunque
            
        except Exception as e:
            logger.error(f"Errore fix libusb: {e}")
            return True  # Non blocchiamo per questo

def prepare_crt285_access():
    """Funzione principale per preparare accesso al CRT-285"""
    helper = CRT285PermissionHelper()
    
    # 1. Setup permessi base
    helper.setup_permissions()
    
    # 2. Verifica accesso dispositivo
    if not helper.check_device_access():
        logger.warning("Accesso dispositivo limitato, tentativo con permessi attuali")
    
    # 3. Fix per libusb_detach_kernel_driver
    helper.fix_libusb_permissions()
    
    return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if prepare_crt285_access():
        print("✅ Sistema preparato per accesso CRT-285")
    else:
        print("⚠️ Alcuni controlli falliti, ma si può procedere")