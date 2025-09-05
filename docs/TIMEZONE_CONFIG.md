# ⏰ Configurazione Timezone e Orologio

## Panoramica

Il sistema supporta la gestione completa dei timezone per garantire che tutti i timestamp (log, export, visualizzazioni) mostrino l'ora locale corretta invece dell'UTC del database.

## 🎯 Problema Risolto

### Situazione Precedente (v2.0.x)
- Database SQLite salva timestamp in UTC
- Log mostravano ora UTC (2 ore indietro per Italia)
- Export con timestamp errati
- Confusione per gli operatori

### Soluzione Implementata (v2.1.0)
- Configurazione timezone da interfaccia web
- Conversione automatica UTC → timezone locale
- Tutti i display mostrano ora locale corretta
- Export con timestamp corretti

## 🔧 Configurazione da UI

### Accesso
1. Login come amministratore
2. Navigare a `/admin/config`
3. Selezionare tab "**Orologio**" 🕐

### Opzioni Disponibili

#### Fuso Orario
- **Default**: Europe/Rome
- **Opzioni comuni**:
  - Europe/Rome (Italia)
  - Europe/London (UK)
  - Europe/Paris (Francia)
  - Europe/Berlin (Germania)
  - America/New_York (US East)
  - America/Chicago (US Central)
  - America/Los_Angeles (US Pacific)
  - UTC (Coordinated Universal Time)

#### Formato Data
- **DD/MM/YYYY** (Europeo) - Default
- **MM/DD/YYYY** (Americano)
- **YYYY-MM-DD** (ISO 8601)

#### Formato Ora
- **24 ore** (00:00 - 23:59) - Default
- **12 ore** (AM/PM)

#### Sincronizzazione NTP
- **Server NTP**: pool.ntp.org (modificabile)
- **Abilitazione**: checkbox per attivare/disattivare
- Mantiene l'ora di sistema sincronizzata

## 💾 Storage Database

### Configurazioni Salvate
Le impostazioni sono salvate nella tabella `system_settings`:

```sql
-- Chiavi utilizzate
sistema.timezone        -- es: 'Europe/Rome'
sistema.formato_data    -- es: 'DD/MM/YYYY'
sistema.formato_ora     -- es: '24'
sistema.ntp_enabled     -- es: 'true'
sistema.ntp_server      -- es: 'pool.ntp.org'
```

### Timestamp nel Database
```sql
-- I timestamp sono sempre salvati in UTC
CREATE TABLE log_accessi (
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ...
);
```

## 🔄 Conversione Timezone

### Pattern Implementazione Python
```python
import pytz
from datetime import datetime

def get_configured_timezone():
    """Recupera timezone configurato dal database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM system_settings WHERE key = 'sistema.timezone'")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'Europe/Rome'

def convert_utc_to_local(timestamp_str):
    """Converte timestamp UTC in timezone configurato"""
    timezone_name = get_configured_timezone()
    
    # Setup timezone
    tz = pytz.timezone(timezone_name)
    utc = pytz.utc
    
    # Parse UTC timestamp from database
    dt_utc = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
    dt_utc = utc.localize(dt_utc)
    
    # Convert to configured timezone
    dt_local = dt_utc.astimezone(tz)
    
    return dt_local.strftime('%Y-%m-%d %H:%M:%S')
```

## 📊 Impatto sui Componenti

### Log Accessi (`/log-accessi`)
- ✅ Visualizzazione con ora locale
- ✅ Filtri data rispettano timezone
- ✅ Statistiche corrette

### Export Dati
- ✅ **CSV**: timestamp convertiti
- ✅ **Excel**: formattazione locale
- ✅ **PDF**: ora locale nel report

### Dashboard
- ✅ Grafici con ora locale
- ✅ Ultimi accessi corretti
- ✅ Clock navbar sincronizzato

### API Responses
- ✅ `/api/log-accessi` ritorna timestamp locali
- ✅ `/api/server-time` include timezone info
- ✅ Export API usa timezone configurato

## 🌍 Timezone Supportati

### Europa
- Europe/Rome (UTC+1/+2 DST)
- Europe/London (UTC+0/+1 DST)
- Europe/Paris (UTC+1/+2 DST)
- Europe/Berlin (UTC+1/+2 DST)
- Europe/Madrid (UTC+1/+2 DST)
- Europe/Amsterdam (UTC+1/+2 DST)
- Europe/Brussels (UTC+1/+2 DST)
- Europe/Vienna (UTC+1/+2 DST)

### America
- America/New_York (UTC-5/-4 DST)
- America/Chicago (UTC-6/-5 DST)
- America/Los_Angeles (UTC-8/-7 DST)
- America/Toronto (UTC-5/-4 DST)
- America/Mexico_City (UTC-6/-5 DST)

### Altri
- UTC (No DST)
- Asia/Tokyo (UTC+9)
- Asia/Shanghai (UTC+8)
- Australia/Sydney (UTC+10/+11 DST)

## 🔍 Verifica Configurazione

### Test da Console
```bash
# Verifica timezone corrente
curl -X GET http://localhost:5000/api/admin/clock-config \
  -H "Cookie: session=YOUR_SESSION_COOKIE"

# Response esempio
{
  "success": true,
  "config": {
    "timezone": "Europe/Rome",
    "formato_data": "DD/MM/YYYY",
    "formato_ora": "24",
    "ntp_enabled": true,
    "ntp_server": "pool.ntp.org"
  }
}
```

### Verifica Ora Server
```bash
curl -X GET http://localhost:5000/api/server-time \
  -H "Cookie: session=YOUR_SESSION_COOKIE"

# Response
{
  "time": "14:30:45",
  "date": "05/09/2025",
  "weekday": "Venerdì",
  "timestamp": "2025-09-05T14:30:45+02:00",
  "timezone": "Europe/Rome"
}
```

## ⚠️ Considerazioni Importanti

### Daylight Saving Time (DST)
- Gestito automaticamente da pytz
- Nessuna configurazione manuale richiesta
- Cambio ora automatico

### Performance
- Conversioni cached per sessione
- Minimo overhead (<1ms per conversione)
- Query ottimizzate con indici

### Migrazione Dati
- Timestamp esistenti rimangono in UTC
- Conversione applicata solo in visualizzazione
- Nessuna modifica ai dati storici

## 🐛 Troubleshooting

### Problema: Ora ancora sbagliata dopo configurazione
**Soluzioni**:
1. Verificare selezione timezone corretta
2. Refresh pagina (F5)
3. Clear cache browser
4. Riavviare servizio se necessario

### Problema: Export mostra UTC invece di ora locale
**Soluzioni**:
1. Verificare versione sistema (>= 2.1.0)
2. Controllare configurazione timezone salvata
3. Verificare logs per errori conversione

### Problema: NTP non sincronizza
**Soluzioni**:
1. Verificare connessione internet
2. Controllare firewall (porta 123 UDP)
3. Provare server NTP alternativo

## 📝 Note per Sviluppatori

### Aggiungere Nuovo Timezone
1. Verificare supporto in pytz:
   ```python
   import pytz
   pytz.timezone('Your/Timezone')
   ```

2. Aggiungere option in template:
   ```html
   <option value="Your/Timezone">Descrizione</option>
   ```

### Testing Timezone
```python
# Script test timezone
from datetime import datetime
import pytz

# Test conversione
utc = pytz.utc
rome = pytz.timezone('Europe/Rome')

now_utc = datetime.now(utc)
now_rome = now_utc.astimezone(rome)

print(f"UTC: {now_utc}")
print(f"Rome: {now_rome}")
print(f"Differenza: {(now_rome.hour - now_utc.hour)} ore")
```

---

**Versione Documento**: 1.0.0  
**Sistema Richiesto**: >= 2.1.0  
**Ultimo Aggiornamento**: 2025-09-05