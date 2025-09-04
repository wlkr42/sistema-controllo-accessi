#!/usr/bin/env python3
import os
import sys
import logging
from typing import Optional, Union

# Aggiungi la directory src al path per gli import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hardware.card_reader import CardReader
from hardware.crt285_reader import CRT285Reader
from hardware.reader_factory import ReaderFactory

def test_reader(reader: Optional[Union[CardReader, CRT285Reader]]) -> None:
    """Test funzionalità base del lettore"""
    if not reader:
        print("❌ Nessun lettore trovato")
        return
        
    print(f"\n=== TEST LETTORE {reader.__class__.__name__} ===")
    print("✓ Lettore inizializzato correttamente")
    
    # Test connessione
    try:
        if reader.test_connection():
            print("✓ Test connessione OK")
        else:
            print("❌ Test connessione fallito")
    except Exception as e:
        print(f"❌ Errore test connessione: {e}")
    
    # Info aggiuntive
    print("\nℹ️ Informazioni lettore:")
    print(f"- Tipo: {reader.__class__.__name__}")
    print(f"- Debug: {'Attivo' if getattr(reader, 'debug', False) else 'Non attivo'}")
    print(f"- Ultimo CF letto: {reader.get_last_cf() or 'Nessuno'}")

def main():
    """Test principale"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("\n🔍 RICERCA LETTORI SUPPORTATI...")
    reader = ReaderFactory.create_reader()
    
    if reader:
        test_reader(reader)
        
        # Test lettura continua
        try:
            print("\n💳 AVVIO TEST LETTURA...")
            print("- Inserire una tessera per testare")
            print("- Ctrl+C per terminare")
            
            def handle_cf(cf: str):
                print(f"\n✅ TESSERA LETTA!")
                print(f"📋 Codice Fiscale: {cf}")
            
            reader.start_continuous_reading(callback=handle_cf)
            
        except KeyboardInterrupt:
            print("\n⏹️ Test interrotto dall'utente")
        finally:
            reader.stop()
            print("✅ Test completato")
    else:
        print("\n❌ NESSUN LETTORE SUPPORTATO TROVATO")
        print("Verificare che:")
        print("1. Il lettore sia collegato correttamente")
        print("2. Le librerie necessarie siano installate")
        print("3. L'utente abbia i permessi necessari")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
    finally:
        print("\n=== TEST TERMINATO ===")
