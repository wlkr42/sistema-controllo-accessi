#!/usr/bin/env python3
"""
Sistema di lettura tessere sanitarie integrato
Supporta:
1. Mappatura diretta numero tessera -> CF (temporaneo)
2. Lettura banda magnetica con decodifica ABA 
3. Preparato per lettura chip IC (da implementare)
"""

import sys
import logging
import time
sys.path.insert(0, '/opt/access_control')

from src.hardware.crt285_reader import CRT285Reader

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    print("🏥 SISTEMA LETTURA TESSERE SANITARIE ITALIANE")
    print("="*60)
    print("📋 Modalità supportate:")
    print("   1. ✅ Mappatura numero tessera -> CF (temporanea)")
    print("   2. ✅ Decodifica ABA da Track2 banda magnetica")
    print("   3. 🔄 Lettura chip IC (in sviluppo)")
    print("="*60)
    print()
    
    try:
        # Inizializza lettore
        print("🔧 Inizializzazione lettore CRT-285...")
        reader = CRT285Reader(
            device_path="/dev/ttyACM0",
            auto_test=True,
            strict_validation=False  # Accetta CF senza checksum per test
        )
        
        # Abilita debug per vedere tutti i dettagli
        reader.set_debug(True)
        
        print("\n✅ Lettore inizializzato!")
        print("\n" + "="*60)
        print("💳 INSERIRE TESSERA SANITARIA NEL LETTORE")
        print("="*60)
        print("ℹ️  Il sistema tenterà di leggere il CF con tutti i metodi disponibili")
        print("⏹️  Premere Ctrl+C per fermare")
        print()
        
        # Statistiche in tempo reale
        def handle_cf(cf):
            print("\n" + "🎉"*20)
            print(f"✅ CODICE FISCALE LETTO: {cf}")
            
            # Mostra statistiche
            stats = reader.get_statistics()
            print(f"\n📊 Statistiche:")
            print(f"   Letture totali: {stats['total_reads']}")
            print(f"   Letture riuscite: {stats['successful_reads']}")
            print(f"   Letture fallite: {stats['failed_reads']}")
            
            # Info sul metodo di lettura
            if cf in ["RSSMRA80A01H501Z"]:  # CF dalla mappatura
                print(f"\n📝 Metodo: Mappatura tessera (temporanea)")
                print(f"   ⚠️  Questo è un mapping temporaneo per test")
                print(f"   ℹ️  In produzione il CF sarà letto dal chip IC")
            else:
                print(f"\n📝 Metodo: Decodifica banda magnetica")
            
            print("🎉"*20 + "\n")
            print("\n💳 Rimuovere la tessera e inserirne un'altra...")
        
        # Avvia lettura continua
        reader.start_continuous_reading(callback=handle_cf)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Interruzione utente")
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'reader' in locals():
            reader.stop()
            
            # Mostra statistiche finali
            print("\n📊 STATISTICHE FINALI:")
            stats = reader.get_statistics()
            for key, value in stats.items():
                if key not in ['read_errors', 'hardware_status', 'last_error']:
                    print(f"   {key}: {value}")
        
        print("\n✅ Sistema terminato")

if __name__ == "__main__":
    main()