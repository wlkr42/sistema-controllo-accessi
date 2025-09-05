# 📊 Sistema Esportazione Dati

## Panoramica

Il sistema di esportazione permette di estrarre i log accessi in tre formati diversi, ognuno ottimizzato per specifici casi d'uso. Tutti i formati rispettano i filtri applicati e utilizzano il timezone configurato.

## 🎯 Formati Supportati

### 📄 CSV (Comma Separated Values)
- **Uso**: Import in database, analisi con Excel/LibreOffice
- **Dimensione**: Più leggero
- **Compatibilità**: Universale

### 📗 Excel (.xlsx)
- **Uso**: Report professionali, presentazioni
- **Formattazione**: Header colorati, stili applicati
- **Compatibilità**: Microsoft Excel, LibreOffice Calc

### 📕 PDF (Portable Document Format)
- **Uso**: Archiviazione, documenti ufficiali
- **Layout**: Landscape per migliore leggibilità
- **Stampa**: Ottimizzato per stampa A4

## 🔧 Utilizzo da Interfaccia Web

### Accesso Funzionalità
1. Navigare a `/log-accessi`
2. Applicare filtri desiderati (opzionale)
3. Cliccare sul bottone del formato desiderato:
   - 🟢 **Excel** - Bottone verde
   - 🔵 **CSV** - Bottone blu
   - 🔴 **PDF** - Bottone rosso

### Filtri Applicabili
- **Periodo**: Oggi, Settimana, Mese, Custom
- **Tipo Accesso**: Autorizzato, Negato, etc.
- **Codice Fiscale**: Ricerca specifica
- **Date Custom**: Intervallo personalizzato

## 💻 Implementazione Tecnica

### Endpoint API
```
GET /api/log-accessi/export?format={format}
```

### Parametri Query String
- `format`: **csv** | **excel** | **pdf** (obbligatorio)
- `periodo`: oggi | settimana | mese | custom
- `data_inizio`: YYYY-MM-DD (per periodo custom)
- `data_fine`: YYYY-MM-DD (per periodo custom)
- `tipo`: tipo_accesso da filtrare
- `codice_fiscale`: CF parziale o completo

### Headers Response

#### CSV
```http
Content-Type: text/csv
Content-Disposition: attachment; filename=log_accessi_20250905_123000.csv
```

#### Excel
```http
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename=log_accessi_20250905_123000.xlsx
```

#### PDF
```http
Content-Type: application/pdf
Content-Disposition: attachment; filename=log_accessi_20250905_123000.pdf
```

## 📝 Struttura Dati Esportati

### Colonne Standard
1. **Data/Ora**: Timestamp con timezone locale
2. **Codice Fiscale**: CF completo
3. **Nome Utente**: Nome da database o '-'
4. **Autorizzato**: Si/No
5. **Tipo Accesso**: AUTORIZZATO, NEGATO, etc.
6. **Motivo Rifiuto**: Dettaglio se negato
7. **Terminale**: Nome installazione
8. **Durata (ms)**: Tempo elaborazione

### Formato CSV
```csv
Data/Ora,Codice Fiscale,Nome Utente,Autorizzato,Tipo Accesso,Motivo Rifiuto,Terminale,Durata (ms)
2025-09-05 12:30:00,RSSMRA85M01H501Z,Mario Rossi,Si,AUTORIZZATO,,Isola Ecologica,125.50
2025-09-05 12:31:00,VRDGPP90A01H501Z,Giuseppe Verdi,No,FUORI_ORARIO,Accesso fuori orario,Isola Ecologica,89.25
```

### Formato Excel
- **Header Row**: Background blu (#3498db), testo bianco, bold
- **Data Rows**: Alternanza bianco/grigio chiaro
- **Auto-fit columns**: Larghezza automatica
- **Freeze panes**: Header fisso durante scroll

### Formato PDF
- **Orientamento**: Landscape (orizzontale)
- **Font**: Helvetica
- **Titolo**: "Log Accessi - Sistema Controllo Accessi"
- **Tabella**: Bordi neri, header colorato
- **Righe alternate**: Bianco/grigio per leggibilità

## 🔄 Gestione Timezone

Tutti i timestamp vengono convertiti automaticamente dal UTC (storage) al timezone configurato nel sistema:

```python
# Conversione automatica applicata
UTC: 2025-09-05 10:30:00
Europe/Rome: 2025-09-05 12:30:00  # +2 ore (DST)
```

## 📦 Dipendenze

### CSV
- Nativo Python (`csv` module)
- Nessuna dipendenza esterna

### Excel
- **openpyxl** (3.1.2)
- Gestione stili e formattazione
- Già incluso in requirements.txt

### PDF
- **reportlab** (4.0.4)
- Generazione PDF complessa
- Installato con: `pip install reportlab`

## 🚀 Performance

### Limiti Consigliati
- **CSV**: Fino a 1M record
- **Excel**: Max 1.048.576 righe (limite Excel)
- **PDF**: Max 10.000 record (per dimensione file)

### Ottimizzazioni
- Query con LIMIT per grandi dataset
- Streaming per CSV (chunked response)
- Compressione automatica per download

## 🔍 Testing Export

### Test Manuale via cURL

#### CSV
```bash
curl -X GET "http://localhost:5000/api/log-accessi/export?format=csv" \
  -H "Cookie: session=YOUR_SESSION" \
  -o test_export.csv
```

#### Excel
```bash
curl -X GET "http://localhost:5000/api/log-accessi/export?format=excel" \
  -H "Cookie: session=YOUR_SESSION" \
  -o test_export.xlsx
```

#### PDF
```bash
curl -X GET "http://localhost:5000/api/log-accessi/export?format=pdf" \
  -H "Cookie: session=YOUR_SESSION" \
  -o test_export.pdf
```

### Script Python Test
```python
import requests
from datetime import datetime

# Setup session
session = requests.Session()
session.post('http://localhost:5000/login', 
             data={'username': 'admin', 'password': 'admin123'})

# Test tutti i formati
formats = ['csv', 'excel', 'pdf']
for fmt in formats:
    response = session.get(f'http://localhost:5000/api/log-accessi/export?format={fmt}')
    if response.status_code == 200:
        filename = f'export_{datetime.now():%Y%m%d_%H%M%S}.{fmt}'
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f'✅ {fmt.upper()} salvato: {filename}')
    else:
        print(f'❌ Errore {fmt}: {response.status_code}')
```

## ⚠️ Troubleshooting

### Problema: Export vuoto
**Cause possibili**:
- Nessun dato nel periodo selezionato
- Filtri troppo restrittivi

**Soluzione**:
- Rimuovere filtri
- Verificare presenza dati

### Problema: Excel non si apre
**Cause possibili**:
- File corrotto
- Versione Excel incompatibile

**Soluzione**:
- Provare con LibreOffice
- Verificare dimensione file > 0

### Problema: PDF layout problematico
**Cause possibili**:
- Testi troppo lunghi
- Caratteri speciali

**Soluzione**:
- Sistema tronca automaticamente a 15-20 caratteri
- Verificare encoding UTF-8

### Problema: Download non parte
**Cause possibili**:
- Popup blocker browser
- Sessione scaduta

**Soluzione**:
- Permettere popup dal sito
- Re-login e riprovare

## 🔒 Sicurezza

### Autorizzazioni
- Richiede autenticazione
- Permessi read minimo
- Admin per export completi

### Data Protection
- No dati sensibili in filename
- Timestamp nel nome per unicità
- No cache browser per download

### Audit
- Log di ogni export richiesto
- Tracciamento utente e timestamp
- Filtri applicati registrati

## 📈 Statistiche Export

### Metriche Tracked
- Numero export per formato
- Utenti che esportano
- Dimensioni medie file
- Tempi generazione

### Performance Tipiche
- **CSV 1000 record**: ~100ms
- **Excel 1000 record**: ~500ms
- **PDF 1000 record**: ~800ms

## 🎯 Best Practices

### Per Analisi Dati
1. Usa CSV per import in database
2. Applica filtri per ridurre dimensione
3. Export incrementali (es. mensili)

### Per Report
1. Excel per report interattivi
2. PDF per documenti finali
3. Includi sempre periodo nel filename

### Per Archiviazione
1. PDF per conformità legale
2. Compressione ZIP per storage
3. Backup periodici automatici

---

**Versione Documento**: 1.0.0  
**Sistema Richiesto**: >= 2.1.0  
**Ultimo Aggiornamento**: 2025-09-05