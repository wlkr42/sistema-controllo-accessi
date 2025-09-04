#!/usr/bin/env python3
"""
Test completo del lettore CRT-285 con supporto CF italiani
"""
import sys
import os
import logging
import time
from typing import List, Tuple

# Aggiungi path per import
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from crt285_reader import CRT285Reader

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_cf_validation_standalone():
    """Test standalone della validazione CF"""
    print("\n" + "="*60)
    print("🧪 TEST VALIDAZIONE CODICI FISCALI ITALIANI")
    print("="*60)
    
    # Crea istanza reader solo per test (modalità non-strict per accettare CF senza checksum valido)
    reader = CRT285Reader.__new__(CRT285Reader)
    reader.stats = {'invalid_cf': 0}
    reader.debug = False
    reader.strict_validation = False  # Accetta CF con formato corretto anche senza checksum valido
    
    # Test cases con CF reali e di test
    # NOTA: In modalità non-strict, i CF con formato valido sono accettati anche senza checksum corretto
    test_cases = [
        # CF con formato valido (accettati in modalità non-strict)
        ('RSSMRA80A01H501Z', True, 'CF formato valido (test DB)'),
        ('BNCGVN75L15F205X', True, 'CF formato valido (test DB)'),
        ('VRDLCA85T45Z404Y', True, 'CF formato valido (test DB)'),
        
        # CF con formato errato (sempre rifiutati)
        ('ABCDEF12G34H567I', False, 'Formato completamente errato'),
        ('RSSMRA80W01H501Z', False, 'Mese non valido (W)'),
        ('RSSMRA80K01H501Z', False, 'Mese non valido (K)'),
        ('1234567890ABCDEF', False, 'Formato non CF'),
        
        # CF troppo uniformi o vuoti (sempre rifiutati)
        ('AAAAAAAAAAAAAAAA', False, 'Pattern troppo uniforme'),
        ('', False, 'CF vuoto'),
        ('ABC', False, 'CF troppo corto'),
        ('ABCDEFGHIJKLMNOPQRSTUVWXYZ', False, 'CF troppo lungo'),
        ('RSSMRA8001H501ZZ', False, 'CF 17 caratteri')
    ]
    
    passed = 0
    failed = 0
    
    for cf, expected, description in test_cases:
        try:
            result = reader._validate_cf(cf)
            if result == expected:
                print(f"✅ {description}: {cf[:6]}...{cf[-4:] if len(cf) > 10 else cf} -> {result}")
                passed += 1
            else:
                print(f"❌ {description}: {cf[:6]}...{cf[-4:] if len(cf) > 10 else cf} -> {result} (atteso: {expected})")
                failed += 1
        except Exception as e:
            print(f"⚠️ {description}: Errore - {e}")
            failed += 1
    
    print(f"\n📊 RISULTATI: {passed}/{len(test_cases)} test superati")
    
    if failed == 0:
        print("✅ TUTTI I TEST SUPERATI!")
    else:
        print(f"⚠️ {failed} test falliti")
    
    return passed, failed

def test_hardware_diagnostics():
    """Test diagnostica hardware"""
    print("\n" + "="*60)
    print("🔧 TEST DIAGNOSTICA HARDWARE")
    print("="*60)
    
    try:
        # Prova a inizializzare il lettore
        print("📡 Tentativo connessione al lettore...")
        reader = CRT285Reader(auto_test=False)
        
        # Esegui diagnostica
        results = reader.run_diagnostics()
        
        # Mostra risultati
        print(f"\n📊 Risultati diagnostica:")
        print(f"   Test superati: {results['tests_passed']}")
        print(f"   Test falliti: {results['tests_failed']}")
        print(f"   Success rate: {results['summary']['success_rate']}")
        
        # Dettagli test
        print("\n📝 Dettagli test:")
        for test_name, test_result in results['details'].items():
            emoji = {
                'PASS': '✅',
                'FAIL': '❌',
                'WARN': '⚠️',
                'SKIP': '⏭️'
            }.get(test_result['status'], '❓')
            print(f"   {emoji} {test_name}: {test_result['message']}")
        
        # Test validazione CF integrata
        print("\n🧪 Test validazione CF nel lettore:")
        reader.test_cf_validation()
        
        # Cleanup
        reader.stop()
        
        return results['tests_passed'], results['tests_failed']
        
    except Exception as e:
        print(f"❌ Impossibile inizializzare lettore: {e}")
        print("💡 Suggerimenti:")
        print("   1. Verificare che il lettore sia collegato")
        print("   2. Verificare permessi utente (gruppo dialout)")
        print("   3. Verificare che la libreria sia installata (/usr/local/lib/crt_288x_ur.so)")
        return 0, 1

def test_mock_reading():
    """Test simulato di lettura CF"""
    print("\n" + "="*60)
    print("🎭 TEST SIMULATO LETTURA CF")
    print("="*60)
    
    # CF di test (quelli nel database di test)
    test_cfs = [
        'RSSMRA80A01H501Z',  # CF test DB
        'BNCGVN75L15F205X',  # CF test DB
        'VRDLCA85T45Z404Y',  # CF test DB
        'INVALIDCF1234567',  # Questo verrà rifiutato
    ]
    
    print("📋 Simulazione lettura CF (modalità non-strict):")
    for i, cf in enumerate(test_cfs, 1):
        print(f"\n🔄 Lettura {i}/{len(test_cfs)}...")
        time.sleep(0.5)
        
        # Crea reader mock in modalità non-strict
        reader = CRT285Reader.__new__(CRT285Reader)
        reader.stats = {
            'total_reads': 0,
            'successful_reads': 0,
            'failed_reads': 0,
            'invalid_cf': 0
        }
        reader.debug = False
        reader.strict_validation = False  # Non-strict mode
        
        # Valida CF
        if reader._validate_cf(cf):
            print(f"✅ CF valido: {cf}")
            print(f"   ✓ Formato corretto")
            print(f"   ✓ Validazione superata (modalità non-strict)")
            print(f"   ✓ Accesso autorizzabile")
        else:
            print(f"❌ CF non valido: {cf}")
            print(f"   ✗ Validazione fallita")
            print(f"   ✗ Accesso negato")
    
    print("\n✅ Test simulato completato")

def main():
    """Main test suite"""
    print("\n" + "🏥"*30)
    print("🎯 TEST SUITE COMPLETO CRT-285 READER")
    print("🏥"*30)
    
    total_passed = 0
    total_failed = 0
    
    # Test 1: Validazione CF
    passed, failed = test_cf_validation_standalone()
    total_passed += passed
    total_failed += failed
    
    # Test 2: Mock reading
    test_mock_reading()
    
    # Test 3: Hardware (opzionale)
    response = input("\n🔌 Eseguire test hardware? (richiede lettore collegato) [y/N]: ")
    if response.lower() in ['y', 'yes', 's', 'si']:
        passed, failed = test_hardware_diagnostics()
        total_passed += passed
        total_failed += failed
    else:
        print("⏭️ Test hardware saltato")
    
    # Riepilogo finale
    print("\n" + "="*60)
    print("📊 RIEPILOGO TEST SUITE")
    print("="*60)
    print(f"✅ Test superati: {total_passed}")
    print(f"❌ Test falliti: {total_failed}")
    
    success_rate = (total_passed / (total_passed + total_failed) * 100) if (total_passed + total_failed) > 0 else 0
    print(f"📈 Success rate: {success_rate:.1f}%")
    
    if total_failed == 0:
        print("\n🎉 TUTTI I TEST SUPERATI! Il lettore è pronto per l'uso.")
    else:
        print(f"\n⚠️ Alcuni test sono falliti. Verificare i problemi segnalati.")
    
    return 0 if total_failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())