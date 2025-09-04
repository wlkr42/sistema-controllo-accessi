#!/usr/bin/env python3

import sys
import time
import logging
import argparse
from typing import Tuple, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_card_reader() -> Tuple[bool, Optional[str]]:
    """
    Testa la connessione e il funzionamento del lettore tessere.
    Returns:
        Tuple[bool, Optional[str]]: (success, error_message)
    """
    try:
        import usb.core
        import usb.util
        
        # ID Vendor e Product del lettore tessere
        VENDOR_ID = 0x0483  # STMicroelectronics
        PRODUCT_ID = 0x2150  # RFID Reader
        
        # Cerca il dispositivo
        device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
        
        if device is None:
            return False, "Lettore tessere non trovato. Verificare connessione USB."
            
        # Test configurazione
        try:
            device.set_configuration()
        except usb.core.USBError as e:
            return False, f"Errore configurazione lettore: {str(e)}"
            
        logger.info("✓ Lettore tessere trovato e configurato correttamente")
        return True, None
        
    except Exception as e:
        return False, f"Errore test lettore tessere: {str(e)}"

def test_usb_relay() -> Tuple[bool, Optional[str]]:
    """
    Testa la connessione e il funzionamento del relè USB.
    Returns:
        Tuple[bool, Optional[str]]: (success, error_message)
    """
    try:
        import usb.core
        import usb.util
        
        # ID Vendor e Product del relè USB
        VENDOR_ID = 0x16c0  # Van Ooijen Technische Informatica
        PRODUCT_ID = 0x05df  # USB-Relay
        
        # Cerca il dispositivo
        device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
        
        if device is None:
            return False, "Relè USB non trovato. Verificare connessione USB."
            
        # Test configurazione
        try:
            device.set_configuration()
        except usb.core.USBError as e:
            return False, f"Errore configurazione relè: {str(e)}"
            
        logger.info("✓ Relè USB trovato e configurato correttamente")
        return True, None
        
    except Exception as e:
        return False, f"Errore test relè USB: {str(e)}"

def test_permissions() -> Tuple[bool, Optional[str]]:
    """
    Verifica i permessi di accesso ai dispositivi USB.
    Returns:
        Tuple[bool, Optional[str]]: (success, error_message)
    """
    try:
        import os
        
        # Verifica regole udev
        if not os.path.exists('/etc/udev/rules.d/99-access-control.rules'):
            return False, "File regole udev non trovato"
            
        # Verifica permessi cartella /dev/bus/usb
        if not os.access('/dev/bus/usb', os.R_OK | os.W_OK):
            return False, "Permessi insufficienti su /dev/bus/usb"
            
        logger.info("✓ Permessi dispositivi USB configurati correttamente")
        return True, None
        
    except Exception as e:
        return False, f"Errore verifica permessi: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='Test hardware sistema controllo accessi')
    parser.add_argument('--verbose', action='store_true', help='Mostra output dettagliato')
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info("Inizio test hardware...")
    
    # Test permessi
    perm_ok, perm_err = test_permissions()
    if not perm_ok:
        logger.error(f"❌ Test permessi fallito: {perm_err}")
        sys.exit(1)
    
    # Test lettore tessere
    reader_ok, reader_err = test_card_reader()
    if not reader_ok:
        logger.error(f"❌ Test lettore tessere fallito: {reader_err}")
        sys.exit(1)
    
    # Test relè USB
    relay_ok, relay_err = test_usb_relay()
    if not relay_ok:
        logger.error(f"❌ Test relè USB fallito: {relay_err}")
        sys.exit(1)
    
    logger.info("✓ Test hardware completati con successo!")
    sys.exit(0)

if __name__ == '__main__':
    main()
