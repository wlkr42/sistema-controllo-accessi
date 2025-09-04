# File: /opt/access_control/src/external/odoo_partner_connector.py
# Connettore Odoo per controllo accessi
# Solo 4 campi essenziali: CF, name, city, active

import xmlrpc.client
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading
import re
from pathlib import Path

logger = logging.getLogger(__name__)

class OdooPartnerConnector:
    """Connettore Odoo ROBUSTO per cittadini - Solo campi essenziali"""
    
    def __init__(self, config_manager):
        self.config = config_manager.get_config()
        
        # Connessioni XML-RPC
        self.common_proxy = None
        self.object_proxy = None
        self.uid = None
        
        # Stato connessione
        self.is_connected = False
        self.last_sync = None
        self.sync_errors = 0
        self.max_sync_errors = 3
        
        # Thread sincronizzazione
        self.sync_thread = None
        self.running = False
        
        # Cache file
        self.cache_file = Path("/opt/access_control/data/partner_cache.json")
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info("🔗 OdooPartnerConnector ROBUSTO inizializzato")
    
    def configure_connection(self, url: str, database: str, username: str, password: str,
                           comune: str = "Rende", sync_interval: int = 43200):
        """Configura connessione Odoo ROBUSTA"""
        
        # Assicura protocollo HTTPS
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        self.odoo_url = url.rstrip('/')
        self.odoo_database = database
        self.odoo_username = username
        self.odoo_password = password
        self.comune_filter = comune
        self.sync_interval = sync_interval
        
        # URLs XML-RPC
        self.common_url = f"{self.odoo_url}/xmlrpc/2/common"
        self.object_url = f"{self.odoo_url}/xmlrpc/2/object"
        
        logger.info(f"📝 Odoo configurato per {comune}: {url}/{database}")
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test connessione ROBUSTO con timeout"""
        try:
            logger.info(f"🔍 Test connessione {self.odoo_url}...")
            
            # Test endpoint common con timeout
            common = xmlrpc.client.ServerProxy(self.common_url)
            version_info = common.version()
            
            server_version = version_info.get('server_version', 'Unknown')
            logger.info(f"✅ Server Odoo: {server_version}")
            
            # Test autenticazione
            uid = common.authenticate(self.odoo_database, self.odoo_username, self.odoo_password, {})
            
            if not uid:
                return False, "❌ Autenticazione fallita - controllare credenziali"
            
            logger.info(f"✅ Autenticazione OK - UID: {uid}")
            
            # Test accesso res.partner con SOLO campi necessari
            models = xmlrpc.client.ServerProxy(self.object_url)
            
            # Test count con filtri ESATTI
            domain_test = [
                ('city', '=', self.comune_filter),
                ('is_person', '=', True),
                ('is_company', '=', False),
                ('is_ente', '=', False),
                ('l10n_it_codice_fiscale', '!=', False),
                ('l10n_it_codice_fiscale', '!=', '')
            ]
            
            test_count = models.execute_kw(
                self.odoo_database, uid, self.odoo_password,
                'res.partner', 'search_count', [domain_test]
            )
            
            if test_count == 0:
                return False, f"⚠️ Nessun cittadino per {self.comune_filter} - verificare dati"
            
            logger.info(f"✅ Test OK: {test_count} cittadini {self.comune_filter}")
            return True, f"✅ Connessione OK - {test_count} cittadini disponibili"
                
        except Exception as e:
            return False, f"❌ Errore connessione: {e}"
    
    def connect(self) -> bool:
        """Stabilisce connessione Odoo ROBUSTA"""
        try:
            if not all([self.odoo_url, self.odoo_database, self.odoo_username, self.odoo_password]):
                logger.error("❌ Configurazione Odoo incompleta")
                return False
            
            # Connessioni XML-RPC
            self.common_proxy = xmlrpc.client.ServerProxy(self.common_url)
            self.object_proxy = xmlrpc.client.ServerProxy(self.object_url)
            
            # Autenticazione
            self.uid = self.common_proxy.authenticate(
                self.odoo_database, self.odoo_username, self.odoo_password, {}
            )
            
            if self.uid:
                self.is_connected = True
                self.sync_errors = 0
                logger.info(f"✅ Connesso a Odoo - UID: {self.uid}")
                return True
            else:
                logger.error("❌ Autenticazione Odoo fallita")
                return False
                
        except Exception as e:
            logger.error(f"❌ Errore connessione: {e}")
            return False
    
    def fetch_cittadini_autorizzati(self) -> List[Dict]:
        """Recupera cittadini SOLO con campi essenziali
        
        Returns:
            Lista dizionari con dati cittadini essenziali
        """
        try:
            if not self.is_connected and not self.connect():
                logger.warning("⚠️ Connessione Odoo non disponibile - uso cache")
                return self._load_from_cache()
            
            # Domain ROBUSTO per filtri
            domain = [
                ('city', '=', self.comune_filter),
                ('is_person', '=', True),
                ('is_company', '=', False),
                ('is_ente', '=', False),
                ('l10n_it_codice_fiscale', '!=', False),
                ('l10n_it_codice_fiscale', '!=', ''),
                ('active', '=', True)  # Solo attivi
            ]
            
            # SOLO 4 campi essenziali - PERFORMANCE OTTIMIZZATA
            fields = [
                'l10n_it_codice_fiscale',  # CF per identificazione
                'name',                    # Nome completo per log
                'city',                    # Città per verifica
                'active'                   # Stato attivo
            ]
            
            logger.info(f"📥 Recupero cittadini {self.comune_filter} - SOLO campi essenziali...")
            
            # Ricerca IDs con LIMIT per sicurezza
            partner_ids = self.object_proxy.execute_kw(
                self.odoo_database, self.uid, self.odoo_password,
                'res.partner', 'search', [domain], {'limit': 30000}
            )
            
            if not partner_ids:
                logger.warning(f"⚠️ Nessun cittadino per {self.comune_filter}")
                return []
            
            logger.info(f"📋 Trovati {len(partner_ids)} cittadini, recupero dati essenziali...")
            
            # Lettura dati in batch per performance
            batch_size = 1000
            all_partners = []
            
            for i in range(0, len(partner_ids), batch_size):
                batch_ids = partner_ids[i:i + batch_size]
                
                batch_partners = self.object_proxy.execute_kw(
                    self.odoo_database, self.uid, self.odoo_password,
                    'res.partner', 'read', [batch_ids], {'fields': fields}
                )
                
                all_partners.extend(batch_partners)
                logger.info(f"📦 Batch {i//batch_size + 1}: {len(batch_partners)} record")
            
            # Processamento SEMPLIFICATO e ROBUSTO
            cittadini_validi = []
            errori_cf = 0
            dettagli_cf_invalidi = []

            for partner in all_partners:
                try:
                    # CF validation ROBUSTA
                    cf = partner.get('l10n_it_codice_fiscale', '').strip().upper()
                    
                    if not self._validate_codice_fiscale(cf):
                        errori_cf += 1
                        dettagli_cf_invalidi.append({
                            'id': partner.get('id'),
                            'nome': partner.get('name', '').strip(),
                            'cf': cf
                        })
                        continue
                    
                    # Nome completo da Odoo
                    nome = partner.get('name', '').strip()
                    if not nome:
                        nome = 'Cittadino Sconosciuto'
                    
                    # Dati cittadino ESSENZIALI
                    cittadino = {
                        'codice_fiscale': cf,
                        'nome': nome,
                        'note': f"Sync Odoo {datetime.now().strftime('%Y-%m-%d')}",
                        'attivo': partner.get('active', True),
                        'odoo_id': partner.get('id'),
                        'sync_timestamp': datetime.now().isoformat(),
                        'creato_da': 'ODOO_SYNC',
                        'modificato_da': 'ODOO_SYNC'
                    }
                    
                    cittadini_validi.append(cittadino)
                    
                except Exception as e:
                    errori_cf += 1
                    dettagli_cf_invalidi.append({
                        'id': partner.get('id'),
                        'nome': partner.get('name', '').strip(),
                        'cf': partner.get('l10n_it_codice_fiscale', '')
                    })
                    logger.debug(f"⚠️ Errore partner {partner.get('id')}: {e}")

            # Statistiche finali
            logger.info(f"✅ Processati {len(cittadini_validi)} cittadini validi")
            if errori_cf > 0:
                logger.warning(f"⚠️ {errori_cf} record con CF invalido/mancante: {dettagli_cf_invalidi}")

            # Salva in cache
            self._save_to_cache(cittadini_validi)
            
            return cittadini_validi
            
        except Exception as e:
            logger.error(f"❌ Errore recupero cittadini: {e}")
            self.sync_errors += 1
            
            # Fallback cache
            logger.info("🔄 Fallback su cache locale")
            return self._load_from_cache()
    
    def _validate_codice_fiscale(self, cf: str) -> bool:
        """Validazione CF ROBUSTA"""
        if not cf or len(cf) != 16:
            return False
        
        # Pattern CF italiano
        pattern = r'^[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]$'
        if not re.match(pattern, cf):
            return False
        
        # Evita pattern troppo uniformi (test data)
        if len(set(cf)) < 6:
            return False
        
        return True
    
    def _save_to_cache(self, cittadini: List[Dict]):
        """Salva cittadini in cache locale ROBUSTA"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'comune': self.comune_filter,
                'count': len(cittadini),
                'cittadini': cittadini
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"💾 Cache salvata: {len(cittadini)} cittadini")
            
        except Exception as e:
            logger.error(f"❌ Errore salvataggio cache: {e}")
    
    def _load_from_cache(self) -> List[Dict]:
        """Carica cittadini da cache locale"""
        try:
            if not self.cache_file.exists():
                logger.warning("⚠️ Cache locale non esistente")
                return []
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            cittadini = cache_data.get('cittadini', [])
            timestamp = cache_data.get('timestamp', 'Unknown')
            
            logger.info(f"📂 Cache: {len(cittadini)} cittadini ({timestamp})")
            return cittadini
            
        except Exception as e:
            logger.error(f"❌ Errore caricamento cache: {e}")
            return []
    
    def sync_to_database(self, database_manager) -> Tuple[bool, Dict]:
        """Sincronizza cittadini con database locale ROBUSTO"""
        start_time = time.time()
        stats = {'fetched': 0, 'updated': 0, 'added': 0, 'errors': 0, 'skipped': 0}
        
        try:
            logger.info(f"🔄 Sync ROBUSTA cittadini {self.comune_filter}")
            
            # Recupera cittadini
            logger.info("📥 Recupero cittadini autorizzati...")
            cittadini = self.fetch_cittadini_autorizzati()
            stats['fetched'] = len(cittadini)
            
            if not cittadini:
                logger.warning("⚠️ Nessun cittadino da sincronizzare")
                return False, stats
            
            # Log dettagliato
            logger.info(f"🔍 Inizio sincronizzazione di {stats['fetched']} cittadini")
            
            # Contatori per debug
            check_count = 0
            
            # Sincronizzazione ROBUSTA
            dettagli_errori = []
            cittadini_aggiunti = []  # Lista dettagli cittadini aggiunti
            for cittadino in cittadini:
                try:
                    cf = cittadino['codice_fiscale']
                    
                    # Log solo per i primi 5 cittadini e poi ogni 5000
                    if check_count < 5 or check_count % 5000 == 0:
                        logger.info(f"🔄 Verifica cittadino {check_count+1}/{stats['fetched']}: {cf}")
                    
                    check_count += 1
                    
                    # Verifica esistenza tramite metodo pubblico (NO accesso diretto a .conn)
                    exists = database_manager.user_exists(cf)
                    
                    # Log dettagliato per i primi 5 cittadini
                    if check_count <= 5:
                        if exists:
                            logger.info(f"✓ Cittadino {cf} già presente (user_exists=True)")
                        else:
                            logger.info(f"+ Cittadino {cf} non presente, sarà aggiunto")
                    
                    if exists:
                        # Già presente - skip
                        stats['skipped'] += 1
                    else:
                        # Aggiungi nuovo cittadino
                        logger.info(f"➕ Tentativo inserimento cittadino {cf} nel database...")
                        try:
                            success = database_manager.add_user(
                                codice_fiscale=cf,
                                nome=cittadino['nome'],
                                note=cittadino['note'],
                                created_by=cittadino['creato_da']  # Passiamo creato_da come created_by
                            )
                        except Exception as sync_exc:
                            dettagli_errori.append({
                                'cf': cf,
                                'nome': cittadino.get('nome'),
                                'note': cittadino.get('note'),
                                'creato_da': cittadino.get('creato_da'),
                                'errore': str(sync_exc)
                            })
                            success = False
                        
                        if success:
                            logger.info(f"✅ Cittadino {cf} inserito con successo")
                            cittadini_aggiunti.append({'nome': cittadino['nome'], 'cf': cf})
                        else:
                            logger.error(f"❌ Errore inserimento cittadino {cf} | DATI: {cittadino}")
                            dettagli_errori.append({
                                'cf': cf,
                                'nome': cittadino.get('nome'),
                                'note': cittadino.get('note'),
                                'creato_da': cittadino.get('creato_da'),
                                'errore': 'add_user returned False'
                            })
                        
                        if success:
                            stats['added'] += 1
                            if stats['added'] % 100 == 0:
                                logger.info(f"📈 Aggiunti {stats['added']} cittadini...")
                        else:
                            stats['errors'] += 1
                            if stats['errors'] < 10:  # Limita i log di errore
                                logger.error(f"❌ Errore aggiunta cittadino {cf}")
                
                except Exception as e:
                    stats['errors'] += 1
                    dettagli_errori.append({
                        'cf': cittadino.get('codice_fiscale'),
                        'nome': cittadino.get('nome'),
                        'note': cittadino.get('note'),
                        'creato_da': cittadino.get('creato_da'),
                        'errore': str(e)
                    })
                    logger.debug(f"⚠️ Errore sync cittadino: {e}")

            # Log dettagli errori a fine sync
            if stats['errors'] > 0:
                logger.critical(f"❌ Dettagli errori sync: {dettagli_errori[:10]} ... (totale: {len(dettagli_errori)})")
            
            # Log dettagli cittadini aggiunti a fine sync (max 20)
            if cittadini_aggiunti:
                max_log = 20
                logger.info(f"👤 Dettaglio cittadini aggiunti (max {max_log}):")
                for c in cittadini_aggiunti[:max_log]:
                    logger.info(f"   - {c['nome']} ({c['cf']})")
                if len(cittadini_aggiunti) > max_log:
                    logger.info(f"... altri {len(cittadini_aggiunti) - max_log} non mostrati")
            
            # Risultati
            self.last_sync = datetime.now()
            duration = time.time() - start_time
            
            logger.info(f"✅ Sync completata in {duration:.2f}s")
            logger.info(f"📊 {stats['added']} aggiunti, {stats['skipped']} esistenti, {stats['errors']} errori")
            
            return True, stats
            
        except Exception as e:
            logger.error(f"❌ Errore sincronizzazione: {e}")
            return False, stats
    
    def get_sync_status(self) -> Dict:
        """Status connessione e sincronizzazione"""
        return {
            'connected': self.is_connected,
            'comune': self.comune_filter,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'sync_errors': self.sync_errors,
            'cache_exists': self.cache_file.exists(),
            'cache_size': self.cache_file.stat().st_size if self.cache_file.exists() else 0
        }
    
    def disconnect(self):
        """Disconnetti da Odoo"""
        self.common_proxy = None
        self.object_proxy = None
        self.uid = None
        self.is_connected = False
        logger.info("🔌 Disconnesso da Odoo")

# Factory function
def create_partner_connector(config_manager) -> OdooPartnerConnector:
    """Crea istanza OdooPartnerConnector ROBUSTO"""
    return OdooPartnerConnector(config_manager)
