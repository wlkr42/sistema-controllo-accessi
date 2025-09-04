# 🚀 GUIDA RAPIDA CLINE - ACCESS_CONTROL

## SETUP COMPLETATO ✅

### File creati in `.clinerules/`:
1. `01-project-rules.md` - Regole obbligatorie progetto
2. `02-memory.md` - Struttura e convenzioni
3. `03-database.md` - Schema database completo

### Rules Bank in `clinerules-bank/`:
- `tasks/nuovo-modulo.md` - Per creare nuovi moduli
- `tasks/nuova-pagina.md` - Per creare nuove pagine

## COME USARE CLINE

### 1. VERIFICA SETUP
Nel popover di Cline (sotto la chat) dovresti vedere:
- ✅ Workspace Rules: .clinerules/
  - 01-project-rules.md
  - 02-memory.md
  - 03-database.md

### 2. INIZIO GIORNATA
Non serve fare nulla! Le regole si caricano automaticamente.
Puoi verificare scrivendo:
```
Conferma di aver caricato le regole del progetto access_control.
Quale tabella usi per il login admin?
```

### 3. NUOVO TASK
Scrivi direttamente:
```
TASK: [descrizione di cosa vuoi fare]

Esempio:
TASK: Aggiungi campo "data_ultimo_accesso" alla tabella utenti_autorizzati
```

### 4. TASK COMUNI
Per task ricorrenti, attiva regole specifiche dal rules bank:
```
cp clinerules-bank/tasks/nuovo-modulo.md .clinerules/
```

### 5. FINE GIORNATA
Disattiva regole temporanee:
```
rm .clinerules/nuovo-modulo.md  # rimuovi regole task specifiche
```

## COMANDI UTILI

```bash
# Vedere regole attive
ls -la .clinerules/

# Backup regole
cp -r .clinerules .clinerules.backup

# Analizza database
python3 analyze_database.py

# Vedi log modifiche
ls -la da_buttare/
```

## WORKFLOW ESEMPIO

1. **Richiesta**: "Crea pagina gestione utenti autorizzati"
2. **Cline legge** automaticamente le regole
3. **Propone** soluzione step-by-step
4. **Tu confermi** prima che proceda
5. **Implementa** seguendo le convenzioni
6. **Sposta** file obsoleti in da_buttare/
7. **Conferma** completamento

## TROUBLESHOOTING

- **Cline non vede le regole?** 
  - Verifica che `.clinerules/` sia nella root del progetto
  - Ricarica VS Code

- **Vuoi regole temporanee?**
  - Copia da `clinerules-bank/` a `.clinerules/`
  - Rimuovi dopo l'uso

- **Database cambiato?**
  - Esegui: `python3 analyze_database.py`
  - Aggiorna `.clinerules/03-database.md`

---
Progetto: `/opt/access_control`
Setup: COMPLETATO ✅
