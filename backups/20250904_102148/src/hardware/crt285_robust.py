#!/usr/bin/env python3
"""
CRT-285 Reader con gestione errori robusta e auto-recovery
Sistema che non si ferma MAI - gestisce crash hardware/software automaticamente
"""

import os
import sys
import time
import logging
import subprocess
import threading
from typing import Optional, Callable
from datetime import datetime

sys.path.insert(0, '/opt/access_control')

logger = logging.getLogger(__name__)

class RobustCRT285Manager:
    """
    Manager robusto per CRT-285 con:
    - Auto-recovery da crash
    - Reset USB automatico
    - Retry infiniti con backoff
    - Monitoraggio salute dispositivo
    """
    
    def __init__(self):
        self.reader = None
        self.running = False
        self.health_check_thread = None
        self.last_successful_read = None
        self.consecutive_failures = 0
        self.max_failures_before_reset = 10
        self.callback = None
        
        # Configurazione retry con backoff esponenziale
        self.retry_delays = [0.5, 1, 2, 5, 10, 30, 60]
        self.current_retry_index = 0
        
        # Stats per monitoraggio
        self.stats = {
            'total_reads': 0,
            'successful_reads': 0,
            'failed_reads': 0,
            'usb_resets': 0,
            'auto_recoveries': 0,
            'uptime_start': datetime.now()
        }
        
    def _reset_usb_device(self) -> bool:
        """Reset completo del dispositivo USB"""
        logger.warning("🔄 Reset dispositivo USB CRT-285...")
        
        try:
            # Metodo 1: usbreset utility
            result = subprocess.run(
                ['sudo', 'usbreset', '23d8:0285'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("✅ USB reset completato con usbreset")
                self.stats['usb_resets'] += 1
                time.sleep(2)
                return True
        except:
            pass
        
        try:
            # Metodo 2: unbind/bind via sysfs
            for dev_path in os.listdir('/sys/bus/usb/devices/'):
                vendor_file = f'/sys/bus/usb/devices/{dev_path}/idVendor'
                product_file = f'/sys/bus/usb/devices/{dev_path}/idProduct'
                
                if os.path.exists(vendor_file) and os.path.exists(product_file):
                    with open(vendor_file, 'r') as f:
                        vendor = f.read().strip()
                    with open(product_file, 'r') as f:
                        product = f.read().strip()
                    
                    if vendor == '23d8' and product == '0285':
                        driver_unbind = f'/sys/bus/usb/drivers/usb/unbind'
                        driver_bind = f'/sys/bus/usb/drivers/usb/bind'
                        
                        try:
                            subprocess.run(
                                ['sudo', 'sh', '-c', f'echo {dev_path} > {driver_unbind}'],
                                capture_output=True,
                                timeout=2
                            )
                            time.sleep(1)
                            
                            subprocess.run(
                                ['sudo', 'sh', '-c', f'echo {dev_path} > {driver_bind}'],
                                capture_output=True,
                                timeout=2
                            )
                            
                            logger.info("✅ USB reset completato via sysfs")
                            self.stats['usb_resets'] += 1
                            time.sleep(2)
                            return True
                        except:
                            pass
        except Exception as e:
            logger.error(f"❌ Errore reset USB: {e}")
        
        return False
    
    def _initialize_reader(self) -> bool:
        """Inizializza il lettore con gestione errori"""
        try:
            if self.reader:
                try:
                    self.reader.stop()
                except:
                    pass
                self.reader = None
            
            from src.hardware.crt285_reader import CRT285Reader
            
            self.reader = CRT285Reader(
                device_path="/dev/ttyACM0",
                auto_test=False,
                strict_validation=False
            )
            
            logger.info("✅ Lettore CRT-285 inizializzato")
            self.consecutive_failures = 0
            self.current_retry_index = 0
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione lettore: {e}")
            self.consecutive_failures += 1
            
            if self.consecutive_failures >= self.max_failures_before_reset:
                logger.warning(f"🔥 {self.consecutive_failures} errori consecutivi - tentativo reset USB")
                if self._reset_usb_device():
                    self.consecutive_failures = 0
                    time.sleep(2)
                    return self._initialize_reader()
            
            return False
    
    def _get_retry_delay(self) -> float:
        """Ottieni delay con backoff esponenziale"""
        delay = self.retry_delays[min(self.current_retry_index, len(self.retry_delays) - 1)]
        self.current_retry_index += 1
        return delay
    
    def _health_check_loop(self):
        """Thread di monitoraggio salute dispositivo"""
        while self.running:
            try:
                time.sleep(30)
                
                if self.last_successful_read:
                    time_since_last_read = (datetime.now() - self.last_successful_read).total_seconds()
                    
                    if time_since_last_read > 300:
                        logger.warning("⚠️ Nessuna lettura da 5 minuti - verifico dispositivo")
                        
                        result = subprocess.run(
                            ['lsusb', '-d', '23d8:0285'],
                            capture_output=True,
                            text=True
                        )
                        
                        if not result.stdout:
                            logger.error("❌ Dispositivo CRT-285 non rilevato!")
                            self._reset_usb_device()
                            self._initialize_reader()
                
                uptime = (datetime.now() - self.stats['uptime_start']).total_seconds() / 3600
                success_rate = (self.stats['successful_reads'] / max(1, self.stats['total_reads'])) * 100
                
                logger.info(f"📊 Stats: Uptime {uptime:.1f}h | Success {success_rate:.1f}% | "
                           f"USB Resets {self.stats['usb_resets']} | "
                           f"Auto-recoveries {self.stats['auto_recoveries']}")
                
            except Exception as e:
                logger.error(f"Errore health check: {e}")
    
    def _continuous_reading_loop(self):
        """Loop di lettura continua con auto-recovery"""
        while self.running:
            try:
                if not self.reader:
                    if not self._initialize_reader():
                        delay = self._get_retry_delay()
                        logger.warning(f"⏳ Retry tra {delay} secondi...")
                        time.sleep(delay)
                        continue
                
                try:
                    def handle_cf(cf):
                        self.stats['total_reads'] += 1
                        self.stats['successful_reads'] += 1
                        self.last_successful_read = datetime.now()
                        self.consecutive_failures = 0
                        self.current_retry_index = 0
                        
                        logger.info(f"✅ CF Letto: {cf}")
                        
                        if self.callback:
                            try:
                                self.callback(cf)
                            except Exception as e:
                                logger.error(f"Errore callback utente: {e}")
                    
                    self.reader.start_continuous_reading(callback=handle_cf)
                    
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logger.error(f"❌ Errore lettura: {e}")
                    self.stats['failed_reads'] += 1
                    self.consecutive_failures += 1
                    
                    self.reader = None
                    
                    self.stats['auto_recoveries'] += 1
                    delay = self._get_retry_delay()
                    logger.info(f"🔄 Auto-recovery in {delay} secondi...")
                    time.sleep(delay)
                    
            except KeyboardInterrupt:
                logger.info("⏹️ Interruzione utente")
                break
            except Exception as e:
                logger.error(f"❌ Errore critico nel loop: {e}")
                time.sleep(5)
    
    def start(self, callback: Optional[Callable[[str], None]] = None):
        """Avvia sistema robusto di lettura"""
        self.callback = callback
        self.running = True
        
        logger.info("🚀 Avvio sistema robusto CRT-285")
        logger.info("   - Auto-recovery attivo")
        logger.info("   - Reset USB automatico")
        logger.info("   - Monitoraggio salute attivo")
        
        self.health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True
        )
        self.health_check_thread.start()
        
        self._continuous_reading_loop()
    
    def stop(self):
        """Ferma sistema"""
        logger.info("⏹️ Arresto sistema robusto...")
        self.running = False
        
        if self.reader:
            try:
                self.reader.stop()
            except:
                pass
        
        logger.info("✅ Sistema fermato")


def main():
    """Test del sistema robusto"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("🛡️ SISTEMA ROBUSTO CRT-285")
    print("=" * 60)
    print("✅ Auto-recovery da crash")
    print("✅ Reset USB automatico")
    print("✅ Retry infiniti con backoff")
    print("✅ Il sistema NON si ferma MAI")
    print("=" * 60)
    print()
    
    def process_cf(cf):
        print(f"🎯 CODICE FISCALE: {cf}")
    
    manager = RobustCRT285Manager()
    
    try:
        manager.start(callback=process_cf)
    except KeyboardInterrupt:
        print("\n⏹️ Arresto manuale...")
        manager.stop()
        
        print("\n📊 STATISTICHE FINALI:")
        print(f"   Letture totali: {manager.stats['total_reads']}")
        print(f"   Letture riuscite: {manager.stats['successful_reads']}")
        print(f"   USB resets: {manager.stats['usb_resets']}")
        print(f"   Auto-recoveries: {manager.stats['auto_recoveries']}")


if __name__ == "__main__":
    main()