# 🚀 GUIDA RAPIDA - LETTORE CRT-285

## ✅ COME USARE IL LETTORE

### 1️⃣ Test Rapido
```bash
# Attiva virtual environment
source /opt/access_control/venv/bin/activate

# Esegui lettore
sudo python /opt/access_control/src/hardware/crt285_reader.py
```

### 2️⃣ Integrazione nel Sistema
```python
from src.hardware.crt285_reader import CRT285Reader

# Inizializza
reader = CRT285Reader(
    auto_test=True,
    strict_validation=False
)

# Callback per gestire CF
def process_cf(codice_fiscale):
    print(f"CF Letto: {codice_fiscale}")
    # Qui: verifica database, apri cancello, etc.

# Avvia lettura continua
reader.start_continuous_reading(callback=process_cf)
```

### 3️⃣ Script di Test

#### Test completo con debug:
```bash
cd /opt/access_control/src/drivers/288K/dev_controllo_accessi
sudo ./scripts/test_lettore_live.sh
```

#### Fix permessi USB (se necessario):
```bash
sudo ./scripts/fix_usb_permissions.sh
```

---

## 📊 STATI DEL LETTORE

| Stato | Significato | LED |
|-------|-------------|-----|
| Status 1 | Nessuna carta | Spento |
| Status 2 | Carta in inserimento | - |
| Status 3 | Carta presente - lettura | Blu fisso |
| CF Letto | Codice fiscale valido trovato | Blu lampeggiante |
| Errore | Lettura fallita | Rosso fisso |

---

## 🔍 COSA VIENE LETTO

### Dal CHIP IC (prioritario):
- **File**: EF.Dati_Personali (1102)
- **Offset**: 0x44
- **Contenuto**: Codice Fiscale in ASCII

### Dalla BANDA MAGNETICA (fallback):
- **Track 1**: CF + Nome (primi 16 caratteri)
- **Track 2**: Numero tessera (20 cifre)

---

## ⚠️ TROUBLESHOOTING VELOCE

| Problema | Soluzione |
|----------|-----------|
| Errore permessi USB | Eseguire con `sudo` |
| Dispositivo non trovato | Verificare: `lsusb \| grep 23d8:0285` |
| CF non letto | Tessera inserita correttamente? Chip verso l'alto |
| Lettura lenta | Normale per chip (300-500ms) |

---

## 📝 FILE IMPORTANTI

```
/opt/access_control/
├── src/hardware/crt285_reader.py      # Modulo principale
├── src/hardware/tessera_cf_mapping.json   # Mappature test
└── venv/                               # Python environment
```

---

## 🎯 ESEMPI D'USO

### Esempio 1: Lettura singola
```python
reader = CRT285Reader()
# Inserire tessera...
cf = reader._read_card_robust()
print(f"CF: {cf}")
reader.stop()
```

### Esempio 2: Con statistiche
```python
reader = CRT285Reader()
reader.start_continuous_reading(callback=process_cf)
# ... dopo alcune letture ...
stats = reader.get_statistics()
print(f"Letture totali: {stats['total_reads']}")
print(f"Success rate: {stats['successful_reads']}/{stats['total_reads']}")
```

### Esempio 3: Debug mode
```python
reader = CRT285Reader()
reader.set_debug(True)  # Log dettagliato
reader.start_continuous_reading(callback=process_cf)
```

### Esempio 4: Controllo LED
```python
reader = CRT285Reader()
# LED durante lettura
reader.set_led(1, 1)  # LED blu acceso
reader.set_led(0, 2)  # LED rosso lampeggiante
reader.set_led(2, 0)  # Spegni tutti i LED

# Configura tempo lampeggio (x0.25 sec)
reader.set_led_flash_time(4, 4)  # 1 sec on, 1 sec off
```

---

## 💡 TIPS

1. **Performance**: Il chip è più sicuro ma più lento (300ms vs 150ms banda)
2. **Affidabilità**: Il sistema prova automaticamente chip → banda → mappatura
3. **Test**: Usa tessere diverse per verificare compatibilità
4. **Log**: Abilita debug solo per troubleshooting (verbose!)

---

**Versione**: 1.0.0 | **Data**: Settembre 2025