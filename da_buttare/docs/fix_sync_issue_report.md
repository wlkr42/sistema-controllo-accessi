# Risoluzione Problema Sincronizzazione Odoo

## 📋 Riepilogo Problema

**Data:** 25 Luglio 2025
**Componente:** Sincronizzazione utenti da Odoo
**Gravità:** Alta
**Stato:** Risolto ✅

## 🔍 Descrizione Problema

Durante la sincronizzazione degli utenti dal sistema Odoo al database locale, è stato riscontrato un errore che impediva l'aggiunta di nuovi utenti. Il problema si verificava specificamente quando il metodo `verify_access` in `database_manager.py` tentava di importare le funzioni `verifica_orario` e `verifica_limite_mensile` dal modulo `api.modules.configurazione_accessi`.

L'errore principale era:
```
❌ Errore verifica accesso: No module named 'api'
```

Questo errore si verificava perché il modulo `api` non era disponibile nel contesto in cui veniva eseguito lo script di sincronizzazione.

## 🛠️ Analisi Tecnica

Il problema era causato da una dipendenza circolare:

1. `odoo_partner_connector.py` chiama `database_manager.verify_access()`
2. `database_manager.verify_access()` tenta di importare `api.modules.configurazione_accessi`
3. Questo import fallisce quando eseguito dal contesto di `odoo_partner_connector.py`

La funzione `verify_access` in `database_manager.py` era progettata per verificare non solo l'esistenza dell'utente nel database, ma anche per controllare se l'utente rispettava i vincoli di orario e limite mensile. Tuttavia, questi controlli non sono necessari durante la fase di sincronizzazione, poiché l'obiettivo è semplicemente aggiungere gli utenti al database locale.

## ✅ Soluzione Implementata

La soluzione è stata modificare il metodo `sync_to_database` in `odoo_partner_connector.py` per verificare direttamente l'esistenza dell'utente nel database locale, senza passare per le verifiche aggiuntive di orario e limite mensile.

### Modifiche Apportate:

1. Creato script `fix_sync_permanent.py` per applicare la correzione
2. Modificato il metodo `sync_to_database` in `odoo_partner_connector.py` aggiungendo:
   ```python
   # Verifica esistenza DIRETTA senza passare per verify_access
   cursor = database_manager.conn.cursor()
   cursor.execute("SELECT id FROM utenti_autorizzati WHERE codice_fiscale = ?", (cf.upper(),))
   exists = cursor.fetchone() is not None
   ```
3. Backup del file originale in `/opt/access_control/da_buttare/odoo_partner_connector.py.backup_[timestamp]`

## 🧪 Verifica Soluzione

La soluzione è stata verificata con i seguenti test:

1. **Test Manuale**: Eseguito script `fix_sync_issue.py` per verificare l'esistenza dell'utente specifico
2. **Test Automatico**: Eseguito script `test_sync_fixed.py` per verificare la sincronizzazione completa

Risultati:
- ✅ L'utente specifico è stato trovato nel database
- ✅ La sincronizzazione è stata completata con successo
- ✅ Non si verificano più errori di importazione durante la sincronizzazione

## 📊 Impatto

- **Prima della correzione**: La sincronizzazione falliva con errori di importazione, impedendo l'aggiunta di nuovi utenti
- **Dopo la correzione**: La sincronizzazione funziona correttamente, permettendo l'aggiunta di nuovi utenti

## 🔄 Raccomandazioni Future

1. **Refactoring**: Considerare un refactoring più ampio per evitare dipendenze circolari tra i moduli
2. **Test di Integrazione**: Aggiungere test di integrazione specifici per la sincronizzazione Odoo
3. **Logging**: Migliorare il logging per identificare più rapidamente problemi simili in futuro

## 📝 Documentazione Correlata

- Script di correzione: `/opt/access_control/src/external/fix_sync_permanent.py`
- Script di test: `/opt/access_control/src/external/test_sync_fixed.py`
- Backup file originale: `/opt/access_control/da_buttare/odoo_partner_connector.py.backup_[timestamp]`

---

*Documento creato il: 25 Luglio 2025*
