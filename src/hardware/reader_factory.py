import logging
from typing import Optional, Union, Any
from types import ModuleType

# Import condizionale USB
usb_core: Optional[ModuleType] = None
try:
    import usb.core
    usb_core = usb.core
except ImportError:
    pass

# Gestione import sia per esecuzione diretta che come modulo
try:
    from .card_reader import CardReader
    from .crt285_reader import CRT285Reader
except ImportError:
    from card_reader import CardReader
    from crt285_reader import CRT285Reader

logger = logging.getLogger(__name__)

class ReaderFactory:
    """Factory per creare l'istanza corretta del lettore di tessere"""
    
    # ID USB dei lettori supportati
    OMNIKEY_VID_PID = (0x076B, 0x5427)  # OMNIKEY 5427 G2
    CRT285_VID_PID = (0x23d8, 0x0285)   # CREATOR CRT-285

    @staticmethod
    def create_reader_by_key(device_key: Optional[str] = None, device_path: Optional[str] = None) -> Optional[Union[CardReader, CRT285Reader]]:
        """
        Crea l'istanza appropriata del lettore in base al device_key (es. "usb:23d8:0285") o device_path.
        Se device_key corrisponde a CRT-285, istanzia CRT285Reader.
        Se device_key corrisponde a OMNIKEY, istanzia CardReader.
        Se device_key non specificato, autodetect.
        """
        if device_key:
            if device_key.lower() in ["usb:23d8:0285", "23d8:0285"]:
                logger.info("🔍 Selezionato lettore CRT-285 da configurazione")
                return CRT285Reader()
            if device_key.lower() in ["usb:076b:5427", "076b:5427"]:
                logger.info("🔍 Selezionato lettore OMNIKEY 5427 G2 da configurazione")
                return CardReader(device_path=device_path)
        # Fallback autodetect
        return ReaderFactory.create_reader()

    @staticmethod
    def create_reader() -> Optional[Union[CardReader, CRT285Reader]]:
        """
        Crea l'istanza appropriata del lettore in base all'hardware rilevato
        
        Returns:
            CardReader o CRT285Reader se rilevato un lettore supportato
            None se nessun lettore supportato trovato
        """
        if not usb_core:
            logger.error("❌ Libreria USB non disponibile")
            return None
            
        try:
            # Cerca OMNIKEY
            omnikey: Any = usb_core.find(
                idVendor=ReaderFactory.OMNIKEY_VID_PID[0],
                idProduct=ReaderFactory.OMNIKEY_VID_PID[1]
            )
            if omnikey:
                logger.info("🔍 Rilevato lettore OMNIKEY 5427 G2")
                return CardReader()
            
            # Cerca CRT-285
            crt285: Any = usb_core.find(
                idVendor=ReaderFactory.CRT285_VID_PID[0],
                idProduct=ReaderFactory.CRT285_VID_PID[1]
            )
            if crt285:
                logger.info("🔍 Rilevato lettore CRT-285")
                return CRT285Reader()
            
            logger.error("❌ Nessun lettore supportato trovato")
            return None
            
        except Exception as e:
            logger.error(f"❌ Errore rilevamento lettore: {e}")
            return None

# Test standalone
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    reader = ReaderFactory.create_reader()
    if reader:
        print(f"✅ Lettore inizializzato: {reader.__class__.__name__}")
        reader.test_connection()
    else:
        print("❌ Nessun lettore trovato")
