# Lettore CRT-285 - Documentazione Completa

## Panoramica
Il modulo `crt285_reader.py` fornisce un'interfaccia robusta per il lettore di tessere sanitarie CRT-285/288K con supporto completo per i codici fiscali italiani.

## Caratteristiche Principali

### ✅ Funzionalità Implementate
- **Lettura tessere sanitarie italiane** con estrazione automatica del codice fiscale
- **Validazione CF italiana** con algoritmo di checksum ufficiale
- **Modalità strict e non-strict** per la validazione
- **Test diagnostici completi** del hardware
- **Gestione errori robusta** con retry automatici
- **Debounce e anti-duplicazione** per evitare letture multiple
- **Statistiche di funzionamento** in tempo reale
- **Logging dettagliato** per debug e audit

### 🔧 Test di Funzionamento
Il lettore esegue automaticamente i seguenti test all'avvio:
1. **Test libreria**: Verifica caricamento libreria C
2. **Test connessione**: Verifica connessione USB con il dispositivo
3. **Test stato**: Verifica capacità di lettura stato carta
4. **Test reset**: Verifica capacità di reset (se supportato)
5. **Test info**: Recupero informazioni dispositivo (se disponibile)
6. **Test lettura**: Verifica disponibilità funzioni di lettura

## Installazione

### Prerequisiti
```bash
# Dipendenze sistema
sudo apt update
sudo apt install -y libusb-1.0-0-dev python3-pip

# Permessi utente
sudo usermod -a -G dialout $USER
newgrp dialout

# Libreria CRT-288K
# Assicurarsi che la libreria sia installata in:
# /usr/local/lib/crt_288x_ur.so
```

### Configurazione
```python
from crt285_reader import CRT285Reader

# Inizializzazione standard (modalità non-strict)
reader = CRT285Reader(
    device_path="/dev/ttyACM0",  # Porta USB
    auto_test=True,              # Esegui diagnostica all'avvio
    strict_validation=False      # Accetta CF con formato valido
)

# Inizializzazione strict (richiede checksum valido)
reader_strict = CRT285Reader(
    strict_validation=True       # Richiede checksum CF valido
)
```

## Utilizzo

### Lettura Continua
```python
def handle_cf(codice_fiscale):
    """Callback chiamato quando viene letto un CF"""
    print(f"CF letto: {codice_fiscale}")
    # Qui puoi verificare accesso nel database

# Avvia lettura continua
reader.start_continuous_reading(callback=handle_cf)

# Ferma lettura
reader.stop()
```

### Test Diagnostici
```python
# Esegui diagnostica completa
results = reader.run_diagnostics()
print(f"Test superati: {results['tests_passed']}/{results['summary']['total_tests']}")

# Test validazione CF
reader.test_cf_validation()

# Ottieni statistiche
stats = reader.get_statistics()
print(f"Letture riuscite: {stats['successful_reads']}")
```

## Validazione Codici Fiscali

### Formato CF Italiano
Il lettore valida i CF italiani secondo il formato standard:
- **6 lettere**: Cognome e nome (3+3)
- **2 cifre**: Anno di nascita
- **1 lettera**: Mese (A-E, H, L, M, P, R, S, T)
- **2 cifre**: Giorno di nascita
- **1 lettera + 3 cifre**: Codice comune
- **1 lettera**: Carattere di controllo

### Modalità di Validazione

#### Non-Strict (default)
Accetta CF con formato corretto anche senza checksum valido:
```python
reader = CRT285Reader(strict_validation=False)
# Accetta: RSSMRA80A01H501Z (anche se checksum non valido)
```

#### Strict
Richiede checksum valido secondo l'algoritmo ufficiale:
```python
reader = CRT285Reader(strict_validation=True)
# Richiede CF con checksum corretto
```

## Test Suite

### Esecuzione Test Completi
```bash
# Test completo con validazione e simulazione
python3 src/hardware/test_crt285_complete.py

# Test solo validazione CF
python3 -c "from src.hardware.crt285_reader import CRT285Reader; r = CRT285Reader(); r.test_cf_validation()"
```

### Test Supportati
1. **Validazione CF**: Test pattern e checksum
2. **Mock Reading**: Simulazione letture
3. **Hardware Test**: Test reale del dispositivo (opzionale)

## Troubleshooting

### Problemi Comuni

#### Libreria non trovata
```
Errore: libcrt_288x_ur.so not found
Soluzione: Verificare installazione in /usr/local/lib/
```

#### Permessi insufficienti
```
Errore: Permission denied /dev/ttyACM0
Soluzione: sudo usermod -a -G dialout $USER && newgrp dialout
```

#### Dispositivo non rilevato
```
Errore: Device not connected
Soluzione: 
1. Verificare connessione USB
2. Controllare con: lsusb | grep "23d8:0285"
3. Verificare alimentazione (solo USB, no alimentazione esterna)
```

## Statistiche e Monitoring

Il lettore mantiene statistiche in tempo reale:
```python
stats = reader.get_statistics()
# {
#     'uptime_seconds': 3600,
#     'total_reads': 150,
#     'successful_reads': 145,
#     'failed_reads': 5,
#     'invalid_cf': 3,
#     'success_rate': '96.7%',
#     'hardware_status': {...}
# }
```

## Integrazione con Sistema Access Control

Il lettore è integrato nel sistema principale tramite:
```python
# In src/main.py
from hardware.reader_factory import ReaderFactory

# Creazione automatica basata su configurazione
reader = ReaderFactory.create_reader_by_key(
    device_key="usb:23d8:0285",
    device_path="/dev/ttyACM0"
)
```

## Note di Sicurezza

- **Debounce**: Ignora letture ripetute entro 1 secondo
- **Blocco temporaneo**: Blocca CF ripetuti per 60 secondi
- **Validazione robusta**: Previene pattern uniformi o errati
- **Logging audit**: Tutti gli accessi sono loggati

## Manutenzione

### Log Files
- `logs/access_control.log`: Log generale sistema
- `logs/security_audit.log`: Log sicurezza
- `logs/raee_access.log`: Log accessi RAEE

### Aggiornamenti
Per aggiornare la libreria o il driver:
1. Backup configurazione attuale
2. Aggiornare libreria in `/usr/local/lib/`
3. Testare con `test_crt285_complete.py`
4. Verificare integrazione nel sistema principale

## Supporto

Per problemi o domande:
- Consultare la documentazione in `src/drivers/288K/doc/`
- Verificare i test in `src/hardware/test_crt285_complete.py`
- Controllare i log per messaggi di errore dettagliati

---
*Ultima modifica: Settembre 2025*
*Versione: 2.0 - Supporto completo CF italiani con test integrati*