# REGOLE PROGETTO ACCESS_CONTROL

## 🚨 PRIMA DI OGNI TASK
SEMPRE leggere questi file in ordine:
1. `.clinerules/01-project-rules.md` (questo file)
2. `.clinerules/02-memory.md` (struttura progetto)
3. `.clinerules/03-database.md` (schema database)

## 📋 REGOLE TASSATIVE (OBBLIGATORIE)

### 1. METODOLOGIA DI LAVORO
- ✅ Procedere SEMPRE passo passo
- ✅ Un task alla volta, completarlo prima del successivo
- ✅ MAI modificare più di quello richiesto
- ✅ FOCUS esclusivo sul task corrente

### 2. INTEGRAZIONE CODICE
- ✅ Modificare ESCLUSIVAMENTE i file richiesti nel task
- ✅ NON toccare altri file senza esplicita richiesta
- ✅ Mantenere la modularità Flask Blueprint
- ✅ Rispettare pattern e convenzioni esistenti

### 3. DATABASE - REGOLA CRITICA ⚠️
- `utenti_sistema` = SOLO per login amministratori dashboard
- `utenti_autorizzati` = SOLO per accesso fisico con tessera
- MAI mescolare i due sistemi di autenticazione
- Database path: `/opt/access_control/src/access.db`

### 4. STILE E CONSISTENZA
- ✅ Coerenza totale con codice esistente
- ✅ Indentazione: 4 spazi (Python)
- ✅ Naming: snake_case per Python, kebab-case per file HTML/CSS
- ✅ Response JSON sempre: `{success: bool, message: str, data: any}`

### 5. GESTIONE FILE
- ✅ File obsoleti → SEMPRE in `da_buttare/` con log
- ✅ Log delle modifiche in: `cleanup_log_[timestamp].txt`
- ✅ MAI eliminare file direttamente
- ✅ Backup prima di modifiche importanti

### 6. COMUNICAZIONE
- ✅ Risposte SEMPRE in italiano
- ✅ Percorsi SEMPRE completi: `/opt/access_control/...`
- ✅ Spiegare ogni modifica fatta
- ✅ Confermare completamento task

## 🛠️ WORKFLOW CORRETTO

1. **Analizza** la richiesta
2. **Identifica** i file da modificare
3. **Proponi** soluzione step-by-step
4. **Attendi** conferma prima di procedere
5. **Implementa** solo le modifiche richieste
6. **Verifica** coerenza con esistente
7. **Documenta** cosa è stato fatto
8. **Cleanup** se necessario (file in da_buttare/)

## ❌ NON FARE MAI
- Modificare file non richiesti
- Rifattorizzare senza permesso esplicito
- Cambiare convenzioni esistenti
- Eliminare file (sempre in da_buttare/)
- Procedere senza conferma
- Mischiare task diversi
- Usare librerie non già presenti in requirements.txt

## ✅ RICORDA SEMPRE
- Progetto in: `/opt/access_control/`
- Entry point: `src/main.py`
- API principale: `src/api/web_api.py`
- Moduli in: `src/api/modules/`
- Log in: `logs/`
- Config in: `config/`
- MAI chiudere un task finché non viene esplicitamente scritto "CHIUDI TASK"

## ⚠️ REGOLA CRITICA PER TASK
NON chiudere MAI un task finché non viene esplicitamente scritto "CHIUDI TASK".
Attendere sempre la conferma esplicita prima di usare attempt_completion.

## 🔄 AGGIORNAMENTO MEMORIA AUTOMATICO

### REGOLA: Dopo OGNI task completato
Quando ricevi il comando "AGGIORNA MEMORIA", devi:

1. **Identificare** tutti i file modificati/creati nel task appena completato
2. **Aggiornare** automaticamente:
   - `.clinerules/02-memory.md` se hai aggiunto moduli/endpoint
   - `.clinerules/03-database.md` se hai modificato il database
   - Timestamp di ultimo aggiornamento

3. **Formato aggiornamento**:
   ```
   ## 📝 ULTIMO AGGIORNAMENTO
   - Data: [timestamp]
   - Task: [breve descrizione]
   - Modifiche:
     - [file]: [tipo modifica]
   ```

4. **Confermare** con un riepilogo delle modifiche

### ESEMPIO OUTPUT ATTESO:
```
✅ Memoria aggiornata!

Modifiche registrate:
- Nuovo modulo: gestione_report.py
- Nuovi endpoint: GET /api/reports, POST /api/reports/generate
- Nuova tabella: report_generati
- File in da_buttare/: old_report_handler.py

Aggiornati:
- .clinerules/02-memory.md (moduli + endpoint)
- .clinerules/03-database.md (schema tabella)
```

## 📁 AGGIORNAMENTO STRUTTURA CARTELLE

### QUANDO AGGIORNI MEMORIA, DEVI SEMPRE:

1. **Aggiornare la struttura cartelle** in `.clinerules/02-memory.md`
   - Se hai creato nuovi file, aggiungili nell'albero
   - Se hai creato nuove cartelle, mostra la gerarchia
   - Mantieni l'ASCII art della struttura

2. **Esempio di aggiornamento struttura**:
   ```
   src/
   ├── api/
   │   ├── modules/
   │   │   ├── utenti.py
   │   │   ├── dispositivi.py
   │   │   └── notifiche.py         # ← NUOVO FILE AGGIUNTO
   │   └── web_api.py
   ```

3. **Per ogni nuovo file indica**:
   - Percorso completo nella struttura
   - Breve commento sul suo scopo
   - Se è un modulo, quali endpoint gestisce

### TEMPLATE AGGIORNAMENTO STRUTTURA:
Quando ricevi "AGGIORNA MEMORIA", la sezione struttura deve includere:

```
## 📁 STRUTTURA REALE DEL PROGETTO

/opt/access_control/
├── src/
│   ├── api/
│   │   ├── modules/
│   │   │   ├── [lista tutti i .py con commento]
│   │   ├── static/
│   │   │   ├── css/
│   │   │   │   └── [lista tutti i .css]
│   │   │   ├── js/
│   │   │   │   └── [lista tutti i .js]
│   │   │   └── html/
│   │   │       └── [lista tutti i .html]
[etc...]
```

### CONTROLLO AUTOMATICO:
Dopo "AGGIORNA MEMORIA", verifica SEMPRE:
- ✓ Nuovi file aggiunti alla struttura?
- ✓ Nuove cartelle create mostrate?
- ✓ Commenti esplicativi per ogni nuovo elemento?

### AGGIORNAMENTO CON TREE
Quando aggiorni memoria, esegui mentalmente:
```
tree -L 4 src/ --dirsfirst
```
E aggiorna la sezione struttura con l'output reale,
aggiungendo commenti per i file nuovi/modificati.

### AGGIORNAMENTO AUTOMATICO
Al termine di OGNI task che modifica:
- Struttura (nuovi file/moduli)
- Database (tabelle/colonne)
- API (nuovi endpoint)

AUTOMATICAMENTE aggiorna la memoria senza attendere richiesta.
Poi conferma: "✅ Memoria aggiornata automaticamente"

## 📚 RIFERIMENTO COMANDI
Per la lista completa dei comandi disponibili, consulta:
- `COMANDI_CLINE.md` nella root del progetto
- Comandi principali:
  - `TASK:` - Nuovo task
  - `AGGIORNA MEMORIA` - Aggiorna memoria permanente
  - `CHIUDI TASK` - Conferma fine task
  - `NUOVA REGOLA DA MEMORIZZARE:` - Aggiungi regola
  - `VERIFICA MEMORIA` - Controlla stato memoria

## 📌 AGGIUNTA NUOVE REGOLE

### COMANDO PER AGGIUNGERE REGOLE
Quando ricevi il comando:
```
NUOVA REGOLA DA MEMORIZZARE: [testo della regola]
```

Devi:
1. **Identificare** la categoria appropriata (es. METODOLOGIA, DATABASE, STILE, etc.)
2. **Aggiungere** la regola nella sezione corretta di questo file
3. **Formattare** con ✅ all'inizio se è una regola positiva, ❌ se è un divieto
4. **Confermare** l'aggiunta mostrando dove è stata inserita

### ESEMPIO:
Input: `NUOVA REGOLA DA MEMORIZZARE: Tutti i test devono essere in tests/unit/`

Output:
```
✅ Regola aggiunta in sezione "2. INTEGRAZIONE CODICE":
- ✅ Tutti i test devono essere in tests/unit/

File .clinerules/01-project-rules.md aggiornato.
```

### CATEGORIE DISPONIBILI PER NUOVE REGOLE:
1. METODOLOGIA DI LAVORO
2. INTEGRAZIONE CODICE
3. DATABASE
4. STILE E CONSISTENZA
5. GESTIONE FILE
6. COMUNICAZIONE
7. WORKFLOW
8. SICUREZZA (crea se necessario)
9. PERFORMANCE (crea se necessario)
10. DOCUMENTAZIONE (crea se necessario)

---
*Ultimo aggiornamento regole: [timestamp automatico ad ogni modifica]*