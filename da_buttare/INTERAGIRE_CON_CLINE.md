# 📚 GUIDA COMANDI CLINE - ACCESS_CONTROL

## 🚀 COMANDI BASE

### INIZIO SESSIONE
```
Ciao, lavoriamo su access_control
```
*Le regole si caricano automaticamente da `.clinerules/`*

### NUOVO TASK
```
TASK: [descrizione del task]
```
*Esempio: `TASK: Aggiungi campo telefono alla tabella utenti_autorizzati`*

### FINE TASK
```
CHIUDI TASK
```
*Conferma la chiusura del task corrente*

---

## 📝 GESTIONE MEMORIA

### AGGIORNA MEMORIA
```
AGGIORNA MEMORIA
```
*Aggiorna automaticamente:*
- Struttura cartelle con nuovi file
- Moduli e endpoint aggiunti
- Schema database modificato
- Timestamp aggiornamento

### VERIFICA MEMORIA
```
VERIFICA MEMORIA
```
*Mostra:*
- Ultimo aggiornamento
- Moduli documentati vs reali
- Discrepanze trovate

### AGGIORNA MEMORIA COMPLETA
```
AGGIORNA MEMORIA COMPLETA

Includi:
1. Struttura cartelle aggiornata
2. Lista moduli in src/api/modules/
3. Endpoint aggiunti
4. Modifiche database
5. File in da_buttare/
```
*Per aggiornamento dettagliato*

---

## 📋 GESTIONE REGOLE

### AGGIUNGI NUOVA REGOLA
```
NUOVA REGOLA DA MEMORIZZARE: [testo della regola]
```
*Esempio: `NUOVA REGOLA DA MEMORIZZARE: Tutti i test devono includere docstring`*

### MOSTRA REGOLE ATTIVE
```
MOSTRA REGOLE ATTIVE
```
*Lista tutte le regole caricate da `.clinerules/`*

### VERIFICA RISPETTO REGOLE
```
VERIFICA RISPETTO REGOLE

File: [percorso/file.py]
```
*Controlla se un file rispetta le convenzioni*

---

## 🔍 COMANDI ANALISI

### ANALIZZA STRUTTURA
```
ANALIZZA STRUTTURA src/
```
*Mostra albero directory con commenti*

### ANALIZZA DATABASE
```
ANALIZZA DATABASE

Mostra:
- Tutte le tabelle
- Numero record per tabella
- Relazioni tra tabelle
```

### TROVA FILE
```
TROVA FILE: [pattern]
```
*Esempio: `TROVA FILE: *report*.py`*

### LISTA ENDPOINT
```
LISTA ENDPOINT API
```
*Mostra tutti gli endpoint con metodi e descrizioni*

---

## 🛠️ COMANDI SVILUPPO

### CREA MODULO
```
CREA MODULO: [nome_modulo]

Descrizione: [cosa fa]
Endpoint: [lista endpoint necessari]
```
*Crea nuovo modulo seguendo le convenzioni*

### CREA PAGINA
```
CREA PAGINA: [nome-pagina]

Tipo: [lista|form|dashboard]
Dati: [quali dati mostrare]
```
*Crea HTML + JS + route*

### AGGIUNGI ENDPOINT
```
AGGIUNGI ENDPOINT

Modulo: [nome_modulo.py]
Metodo: [GET|POST|PUT|DELETE]
Path: /api/[percorso]
Funzione: [descrizione]
```

### MODIFICA TABELLA
```
MODIFICA TABELLA: [nome_tabella]

Aggiungi colonne:
- [nome_colonna] [tipo] [constraints]
```
*Genera migration SQL*

---

## 🧹 COMANDI PULIZIA

### CLEANUP FILE OBSOLETI
```
CLEANUP FILE OBSOLETI
```
*Identifica e sposta file non utilizzati in `da_buttare/`*

### MOSTRA FILE IN DA_BUTTARE
```
LISTA DA_BUTTARE
```
*Mostra contenuto cartella con motivi spostamento*

### GENERA LOG PULIZIA
```
GENERA LOG PULIZIA
```
*Crea `cleanup_log_[timestamp].txt`*

---

## 🔧 COMANDI UTILITÀ

### GENERA DOCUMENTAZIONE
```
GENERA DOC: [modulo/funzione]
```
*Crea documentazione formato Markdown*

### CONTROLLA IMPORT
```
CONTROLLA IMPORT MANCANTI
```
*Verifica tutti gli import nei file Python*

### TEST RAPIDO
```
TEST RAPIDO: [funzionalità]
```
*Crea test unitario base*

### BACKUP PRIMA DI MODIFICHE
```
BACKUP FILE: [percorso/file.py]
```
*Crea copia in `backups/` prima di modifiche*

---

## 💡 COMANDI SPECIALI

### SPIEGA CODICE
```
SPIEGA: [percorso/file.py]

Focus su: [funzione specifica]
```
*Spiega funzionamento in italiano*

### SUGGERISCI MIGLIORAMENTI
```
ANALIZZA E SUGGERISCI: [percorso/file.py]
```
*Suggerisce miglioramenti mantenendo convenzioni*

### CONFRONTA FILE
```
CONFRONTA:
- File1: [percorso1]
- File2: [percorso2]
```
*Mostra differenze e suggerisce quale usare*

---

## 🎯 WORKFLOW ESEMPI

### ESEMPIO 1: Aggiungi Campo Database
```
1. TASK: Aggiungi campo 'note' a utenti_autorizzati
2. [Cline lavora]
3. AGGIORNA MEMORIA
4. CHIUDI TASK
```

### ESEMPIO 2: Nuovo Modulo Completo
```
1. TASK: Crea modulo gestione notifiche email
2. CREA MODULO: notifiche
   Descrizione: Invio notifiche email/SMS
   Endpoint: POST /api/notifiche/invia
3. [Cline crea file]
4. AGGIORNA MEMORIA
5. CHIUDI TASK
```

### ESEMPIO 3: Pulizia Progetto
```
1. CLEANUP FILE OBSOLETI
2. LISTA DA_BUTTARE
3. GENERA LOG PULIZIA
4. AGGIORNA MEMORIA
```

---

## ⚡ COMANDI RAPIDI

| Comando | Shortcut | Descrizione |
|---------|----------|-------------|
| `TASK:` | `T:` | Nuovo task |
| `AGGIORNA MEMORIA` | `AM` | Aggiorna memoria |
| `CHIUDI TASK` | `CT` | Chiude task corrente |
| `NUOVA REGOLA DA MEMORIZZARE:` | `NR:` | Aggiungi regola |
| `LISTA ENDPOINT API` | `LEA` | Lista endpoint |

---

## 🔴 COMANDI DI EMERGENZA

### ANNULLA MODIFICHE
```
ANNULLA ULTIME MODIFICHE

File: [percorso]
```
*Ripristina da backup se disponibile*

### STOP IMMEDIATO
```
STOP - NON PROCEDERE
```
*Ferma qualsiasi operazione in corso*

### MOSTRA MODIFICHE PENDING
```
MOSTRA MODIFICHE NON SALVATE
```
*Lista file modificati ma non ancora salvati*

---

## 📌 NOTE IMPORTANTI

1. **MAI** chiudere un task senza `CHIUDI TASK`
2. **SEMPRE** aggiornare memoria dopo modifiche strutturali
3. **File obsoleti** sempre in `da_buttare/`, mai eliminare
4. **Risposte** sempre in italiano
5. **Percorsi** sempre completi: `/opt/access_control/...`

---

*Ultimo aggiornamento: [auto-timestamp]*
*Progetto: `/opt/access_control`*
*Regole in: `.clinerules/`*