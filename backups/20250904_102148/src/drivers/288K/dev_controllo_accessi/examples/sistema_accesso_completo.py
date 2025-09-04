#!/usr/bin/env python3
"""
Sistema Completo di Controllo Accesso RAEE
Integrazione lettore CRT-285 con gestione autorizzazioni
"""
import sys
import time
import json
import logging
from datetime import datetime
from typing import Optional, Dict, List

sys.path.insert(0, '/opt/access_control')
from src.hardware.crt285_reader import CRT285Reader

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/accesso_raee.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SistemaAccessoRAEE:
    """Sistema completo di controllo accesso isola ecologica"""
    
    def __init__(self, config_file: str = "config_accesso.json"):
        """
        Inizializza sistema di accesso
        
        Args:
            config_file: File configurazione con CF autorizzati
        """
        self.config = self._load_config(config_file)
        self.reader = None
        self.accessi_log = []
        self.stats = {
            'accessi_totali': 0,
            'accessi_autorizzati': 0,
            'accessi_negati': 0,
            'errori_lettura': 0
        }
    
    def _load_config(self, config_file: str) -> Dict:
        """Carica configurazione e lista CF autorizzati"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config non trovato, uso config default")
            return {
                'cf_autorizzati': [],
                'modalita': 'permissiva',  # permissiva o restrittiva
                'timeout_cancello': 5,
                'log_accessi': True
            }
    
    def inizializza_lettore(self) -> bool:
        """Inizializza il lettore CRT-285"""
        try:
            logger.info("🔧 Inizializzazione lettore CRT-285...")
            
            self.reader = CRT285Reader(
                device_path="/dev/ttyACM0",
                auto_test=True,
                strict_validation=False  # Accetta CF senza checksum per test
            )
            
            # Test iniziale
            status = self.reader.lib.CRT288x_GetCardStatus()
            logger.info(f"✅ Lettore inizializzato (status: {status})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione lettore: {e}")
            return False
    
    def verifica_autorizzazione(self, cf: str) -> bool:
        """
        Verifica se il CF è autorizzato all'accesso
        
        Args:
            cf: Codice fiscale da verificare
            
        Returns:
            True se autorizzato, False altrimenti
        """
        # Modalità permissiva: tutti possono entrare (solo log)
        if self.config.get('modalita') == 'permissiva':
            logger.info(f"✅ Accesso permesso (modalità permissiva): {cf}")
            return True
        
        # Modalità restrittiva: solo CF in lista
        cf_autorizzati = self.config.get('cf_autorizzati', [])
        
        if cf in cf_autorizzati:
            logger.info(f"✅ CF autorizzato: {cf}")
            return True
        else:
            logger.warning(f"⛔ CF non autorizzato: {cf}")
            return False
    
    def apri_cancello(self, durata: int = 5):
        """
        Simula apertura cancello
        
        Args:
            durata: Secondi di apertura
        """
        logger.info(f"🚪 APERTURA CANCELLO per {durata} secondi")
        
        # Qui andrebbero i comandi reali per aprire il cancello
        # Es: GPIO.output(RELAY_PIN, GPIO.HIGH)
        
        time.sleep(durata)
        
        logger.info("🚪 CHIUSURA CANCELLO")
        # GPIO.output(RELAY_PIN, GPIO.LOW)
    
    def registra_accesso(self, cf: str, autorizzato: bool):
        """
        Registra l'accesso nel log
        
        Args:
            cf: Codice fiscale
            autorizzato: Se l'accesso è stato autorizzato
        """
        accesso = {
            'timestamp': datetime.now().isoformat(),
            'codice_fiscale': cf,
            'autorizzato': autorizzato,
            'tipo_lettura': 'chip' if 'CHIP' in str(self.reader.stats.get('last_read_type', '')) else 'banda'
        }
        
        self.accessi_log.append(accesso)
        
        # Salva su file se configurato
        if self.config.get('log_accessi'):
            with open('/var/log/accessi_raee.jsonl', 'a') as f:
                f.write(json.dumps(accesso) + '\n')
        
        # Aggiorna statistiche
        self.stats['accessi_totali'] += 1
        if autorizzato:
            self.stats['accessi_autorizzati'] += 1
        else:
            self.stats['accessi_negati'] += 1
    
    def gestisci_accesso(self, cf: str):
        """
        Gestisce il processo completo di accesso
        
        Args:
            cf: Codice fiscale letto dalla tessera
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"📋 NUOVO ACCESSO: {cf}")
        logger.info(f"{'='*60}")
        
        # Verifica autorizzazione
        autorizzato = self.verifica_autorizzazione(cf)
        
        # Registra accesso
        self.registra_accesso(cf, autorizzato)
        
        # Azioni in base all'autorizzazione
        if autorizzato:
            print("\n✅ ACCESSO AUTORIZZATO")
            print(f"   CF: {cf}")
            print(f"   Ora: {datetime.now().strftime('%H:%M:%S')}")
            
            # Apri cancello
            self.apri_cancello(self.config.get('timeout_cancello', 5))
            
        else:
            print("\n⛔ ACCESSO NEGATO")
            print(f"   CF: {cf}")
            print("   Motivo: Non in lista autorizzati")
            
            # Potrebbe attivare un allarme o notifica
            logger.warning(f"Tentativo accesso non autorizzato: {cf}")
        
        print(f"\n{'='*60}")
        print("💳 In attesa prossima tessera...")
    
    def avvia_sistema(self):
        """Avvia il sistema di controllo accesso"""
        print("🏭 SISTEMA CONTROLLO ACCESSO RAEE")
        print("="*60)
        print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y')}")
        print(f"🕐 Ora avvio: {datetime.now().strftime('%H:%M:%S')}")
        print(f"📋 Modalità: {self.config.get('modalita', 'permissiva').upper()}")
        print(f"👥 CF autorizzati: {len(self.config.get('cf_autorizzati', []))}")
        print("="*60)
        
        # Inizializza lettore
        if not self.inizializza_lettore():
            print("❌ Impossibile inizializzare il lettore!")
            return
        
        print("\n✅ Sistema pronto")
        print("💳 Inserire tessera sanitaria per accedere")
        print("⏹️  Premere Ctrl+C per fermare\n")
        
        try:
            # Avvia lettura continua con callback
            self.reader.start_continuous_reading(callback=self.gestisci_accesso)
            
        except KeyboardInterrupt:
            logger.info("\n⏹️ Arresto sistema richiesto")
            
        finally:
            self.ferma_sistema()
    
    def ferma_sistema(self):
        """Ferma il sistema e mostra statistiche"""
        if self.reader:
            self.reader.stop()
        
        print("\n" + "="*60)
        print("📊 STATISTICHE SESSIONE")
        print("="*60)
        print(f"Accessi totali: {self.stats['accessi_totali']}")
        print(f"Accessi autorizzati: {self.stats['accessi_autorizzati']}")
        print(f"Accessi negati: {self.stats['accessi_negati']}")
        print(f"Errori lettura: {self.stats['errori_lettura']}")
        
        if self.reader:
            reader_stats = self.reader.get_statistics()
            print(f"\nStatistiche lettore:")
            print(f"  Letture riuscite: {reader_stats['successful_reads']}")
            print(f"  Letture fallite: {reader_stats['failed_reads']}")
        
        print("\n✅ Sistema arrestato correttamente")
        logger.info("Sistema controllo accesso arrestato")


# Configurazione di esempio
def crea_config_esempio():
    """Crea file di configurazione di esempio"""
    config = {
        "modalita": "restrittiva",
        "cf_autorizzati": [
            "RSSMRA80A01H501Z",  # Rossi Mario
            "VRDLGI75B15G273K",  # Verdi Luigi
            "BNCLRA85T45L219E",  # Bianchi Laura
        ],
        "timeout_cancello": 5,
        "log_accessi": True,
        "orari_apertura": {
            "lunedi": ["08:00", "18:00"],
            "martedi": ["08:00", "18:00"],
            "mercoledi": ["08:00", "18:00"],
            "giovedi": ["08:00", "18:00"],
            "venerdi": ["08:00", "18:00"],
            "sabato": ["08:00", "13:00"],
            "domenica": []  # Chiuso
        }
    }
    
    with open('config_accesso.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Creato file config_accesso.json di esempio")


if __name__ == "__main__":
    import os
    
    # Se non esiste config, crea esempio
    if not os.path.exists('config_accesso.json'):
        crea_config_esempio()
    
    # Avvia sistema
    sistema = SistemaAccessoRAEE('config_accesso.json')
    sistema.avvia_sistema()