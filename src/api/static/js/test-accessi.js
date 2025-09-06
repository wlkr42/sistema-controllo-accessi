class TestAccessi {
    constructor() {
        this.initElements();
        this.initRelayElements();
        this.loadUtenti();
        this.loadUtentiDisattivati();
        this.setupEventListeners();
    }

    initElements() {
        this.utenteInput = document.getElementById('utente');
        this.searchResults = document.getElementById('searchResults');
        this.progressBarIngressi = document.getElementById('progressBarIngressi');
        this.textIngressi = document.getElementById('textIngressi');
        this.ingressiAggiuntiviInput = document.getElementById('ingressiAggiuntivi');
        this.motivazioneInput = document.getElementById('motivazione');
        this.testForm = document.getElementById('testAccessoForm');
        this.utentiDisattivatiTable = document.getElementById('utentiDisattivati');
        this.cercaCFInput = document.getElementById('cercaCF');
        this.utentiList = []; // Cache degli utenti
        this.selectedUtente = null; // Utente selezionato
    }

    setupEventListeners() {
        // Form test accesso
        this.testForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.salvaIngressi();
        });

        // Simula accesso
        document.getElementById('simulaAccesso').addEventListener('click', () => {
            this.simulaAccesso();
        });

        // Ricerca CF
        this.cercaCFInput.addEventListener('input', () => {
            this.filtraUtentiDisattivati();
        });

        // Ricerca utente inline
        this.utenteInput.addEventListener('input', (e) => {
            this.selectedUtente = null; // Reset selezione quando l'utente digita
            this.resetProgressBar(); // Reset progress bar quando si cambia utente
            this.filtraUtenti(e.target.value);
        });

        // Chiudi risultati quando si clicca fuori
        document.addEventListener('click', (e) => {
            if (!this.utenteInput.contains(e.target) && !this.searchResults.contains(e.target)) {
                this.searchResults.style.display = 'none';
            }
        });

        // Focus sul campo di ricerca mostra i risultati
        this.utenteInput.addEventListener('focus', () => {
            if (this.utentiList.length > 0) {
                this.filtraUtenti(this.utenteInput.value);
            }
        });
    }

    async loadUtenti() {
        try {
            const response = await fetch('/api/utenti-autorizzati');
            const data = await response.json();
            
            if (data.success) {
                this.utentiList = data.utenti;
            }
        } catch (error) {
            console.error('Errore caricamento utenti:', error);
            showAlert('Errore caricamento lista utenti', 'danger');
        }
    }

    filtraUtenti(searchTerm) {
        searchTerm = searchTerm.toLowerCase().trim();
        
        const utentiFiltrati = searchTerm ? 
            this.utentiList.filter(utente => 
                utente.label.toLowerCase().includes(searchTerm) || 
                utente.codice_fiscale.toLowerCase().includes(searchTerm)
            ) : this.utentiList;
        
        this.renderRisultatiRicerca(utentiFiltrati);
    }

    renderRisultatiRicerca(utenti) {
        if (utenti.length === 0) {
            this.searchResults.style.display = 'none';
            return;
        }

        this.searchResults.innerHTML = utenti.map(utente => `
            <div class="result-item" data-cf="${utente.codice_fiscale}">
                ${utente.label}
            </div>
        `).join('');

        // Aggiungi event listener per la selezione
        this.searchResults.querySelectorAll('.result-item').forEach(item => {
            item.addEventListener('click', () => {
                const cf = item.dataset.cf;
                const utente = this.utentiList.find(u => u.codice_fiscale === cf);
                this.selezionaUtente(utente);
            });
        });

        this.searchResults.style.display = 'block';
    }

    async selezionaUtente(utente) {
        this.selectedUtente = utente;
        this.utenteInput.value = utente.label;
        this.searchResults.style.display = 'none';
        
        // Carica informazioni accessi per l'utente selezionato
        await this.caricaInfoAccessi(utente.codice_fiscale);
    }

    async caricaInfoAccessi(codice_fiscale) {
        try {
            const response = await fetch('/api/configurazione/utente-info-accessi', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ codice_fiscale })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.aggiornaProgressBar(data);
            } else {
                console.error('Errore caricamento info accessi:', data.error);
                this.resetProgressBar();
            }
            
        } catch (error) {
            console.error('Errore connessione:', error);
            this.resetProgressBar();
        }
    }

    aggiornaProgressBar(data) {
        const percentuale = data.percentuale_utilizzo || 0;
        const ingressi = data.numero_accessi_mese || 0;
        const limite = data.limite_mensile || 0;
        
        // Aggiorna progress bar
        this.progressBarIngressi.style.width = `${Math.min(percentuale, 100)}%`;
        this.textIngressi.textContent = `${ingressi} / ${limite}`;
        
        // Colore gradiente basato su percentuale
        if (percentuale <= 50) {
            this.progressBarIngressi.className = 'progress-bar bg-success';
        } else if (percentuale <= 80) {
            this.progressBarIngressi.className = 'progress-bar bg-warning';
        } else {
            this.progressBarIngressi.className = 'progress-bar bg-danger';
        }
        
        // Abilita/disabilita campo ingressi aggiuntivi
        const haRaggiuntoLimite = data.ingressi_rimanenti === 0;
        this.ingressiAggiuntiviInput.disabled = !haRaggiuntoLimite;
        
        if (haRaggiuntoLimite) {
            this.ingressiAggiuntiviInput.placeholder = 'Inserisci ingressi extra';
        } else {
            this.ingressiAggiuntiviInput.placeholder = 'Disponibile solo a limite raggiunto';
            this.ingressiAggiuntiviInput.value = '0';
        }
    }

    resetProgressBar() {
        this.progressBarIngressi.style.width = '0%';
        this.progressBarIngressi.className = 'progress-bar';
        this.textIngressi.textContent = '0 / 0';
        this.ingressiAggiuntiviInput.disabled = true;
        this.ingressiAggiuntiviInput.placeholder = 'Seleziona prima un utente';
        this.ingressiAggiuntiviInput.value = '0';
    }

    async loadUtentiDisattivati() {
        try {
            const response = await fetch('/api/utenti-autorizzati/disattivati');
            const data = await response.json();
            
            if (data.success) {
                this.renderUtentiDisattivati(data.utenti);
            }
        } catch (error) {
            console.error('Errore caricamento utenti disattivati:', error);
            showAlert('Errore caricamento utenti disattivati', 'danger');
        }
    }

    renderUtentiDisattivati(utenti) {
        const searchTerm = this.cercaCFInput.value.trim().toUpperCase();
        
        const filteredUtenti = searchTerm ? 
            utenti.filter(u => u.codice_fiscale.toUpperCase().includes(searchTerm)) : 
            utenti;
        
        this.utentiDisattivatiTable.innerHTML = filteredUtenti.map(utente => `
            <tr>
                <td>${utente.nome}</td>
                <td>${utente.cognome}</td>
                <td>${utente.codice_fiscale}</td>
                <td>${utente.ingressi_mensili}</td>
                <td>
                    <button class="btn btn-sm btn-warning" onclick="testAccessi.resetContatore('${utente.codice_fiscale}')">
                        <i class="fas fa-redo me-1"></i>
                        Reset
                    </button>
                </td>
            </tr>
        `).join('') || '<tr><td colspan="5" class="text-center">Nessun utente disattivato trovato</td></tr>';
    }

    filtraUtentiDisattivati() {
        this.loadUtentiDisattivati();
    }

    async salvaIngressi() {
        if (!this.selectedUtente) {
            showAlert('Seleziona un utente', 'warning');
            return;
        }
        
        const codice_fiscale = this.selectedUtente.codice_fiscale;
        const ingressi_aggiuntivi = parseInt(this.ingressiAggiuntiviInput.value) || 0;
        const motivazione = this.motivazioneInput.value.trim();
        
        if (ingressi_aggiuntivi <= 0) {
            showAlert('Inserisci un numero di ingressi aggiuntivi valido', 'warning');
            return;
        }
        
        // Verifica che l'utente abbia raggiunto il limite prima di procedere
        const infoResponse = await fetch('/api/configurazione/utente-info-accessi', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ codice_fiscale })
        });
        
        const infoData = await infoResponse.json();
        if (infoData.success && infoData.ingressi_rimanenti > 0) {
            const ingressiRimanenti = infoData.ingressi_rimanenti;
            const limite = infoData.limite_mensile;
            showAlert(
                `❌ L'utente ha ancora ${ingressiRimanenti} ingressi disponibili su ${limite}. ` +
                `Non puoi aggiungere ingressi extra finché non raggiunge il limite.`,
                'warning'
            );
            return;
        }
        
        try {
            const response = await fetch('/api/configurazione/test/aggiungi-ingressi', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    codice_fiscale, 
                    ingressi_aggiuntivi,
                    motivazione 
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert(`✅ ${data.message}`, 'success');
                this.loadUtentiDisattivati();
                // Ricarica info accessi aggiornate
                await this.caricaInfoAccessi(codice_fiscale);
                // Reset campi
                this.ingressiAggiuntiviInput.value = '0';
                this.motivazioneInput.value = '';
            } else {
                showAlert(`❌ ${data.error}`, 'danger');
            }
            
        } catch (error) {
            console.error('Errore salvataggio:', error);
            showAlert('Errore di connessione al server', 'danger');
        }
    }

    // Gestione animazioni relè
    initRelayElements() {
        this.ledGreen = document.querySelector('.led-green');
        this.ledRed = document.querySelector('.led-red');
        this.buzzer = document.querySelector('.buzzer');
        this.gate = document.querySelector('.gate');
    }

    activateLedGreen(duration = 3000) {
        this.ledGreen.classList.add('active');
        setTimeout(() => this.ledGreen.classList.remove('active'), duration);
    }

    activateLedRed(duration = 3000) {
        this.ledRed.classList.add('active');
        setTimeout(() => this.ledRed.classList.remove('active'), duration);
    }

    activateBuzzer(duration = 500) {
        this.buzzer.classList.add('active');
        setTimeout(() => this.buzzer.classList.remove('active'), duration);
    }

    activateGate(duration = 8000) {
        this.gate.classList.add('opening');
        setTimeout(() => this.gate.classList.remove('opening'), duration);
    }

    async simulateAccessGranted() {
        // LED Verde + Buzzer breve
        this.activateLedGreen();
        this.activateBuzzer(500);
        
        // Apri cancello dopo 500ms
        setTimeout(() => {
            this.activateGate();
        }, 500);
    }

    async simulateAccessDenied() {
        // LED Rosso
        this.activateLedRed();
        
        // Pattern buzzer: 3 beep
        for (let i = 0; i < 3; i++) {
            setTimeout(() => {
                this.activateBuzzer(200);
            }, i * 500);
        }
    }

    async simulaAccesso() {
        if (!this.selectedUtente) {
            showAlert('Seleziona un utente', 'warning');
            return;
        }
        const codice_fiscale = this.selectedUtente.codice_fiscale;
        
        if (!codice_fiscale) {
            showAlert('Seleziona un utente', 'warning');
            return;
        }
        
        try {
            const response = await fetch('/api/configurazione/test/simula-accesso', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ codice_fiscale })
            });
            
            const data = await response.json();
            
            if (data.success) {
                if (data.accesso_consentito) {
                    // Accesso consentito
                    const msg = `✅ ${data.messaggio}\n${data.nome_utente}\nIngressi: ${data.numero_accessi_mese}/${data.limite_mensile}\n${data.nota || ''}`;
                    showAlert(msg, 'success');
                    // Simula sequenza accesso autorizzato
                    await this.simulateAccessGranted();
                } else {
                    // Accesso negato
                    const msg = `❌ ${data.motivo_rifiuto}\n${data.nome_utente || ''}\nIngressi: ${data.numero_accessi_mese}/${data.limite_mensile}`;
                    showAlert(msg, 'warning');
                    // Simula sequenza accesso negato
                    await this.simulateAccessDenied();
                }
                // NON ricarichiamo i dati perché è solo una simulazione
                // Ricarica info accessi se c'è un utente selezionato
                if (this.selectedUtente) {
                    await this.caricaInfoAccessi(this.selectedUtente.codice_fiscale);
                }
            } else {
                showAlert(data.error || 'Errore simulazione accesso', 'danger');
            }
            
        } catch (error) {
            console.error('Errore simulazione:', error);
            showAlert('Errore di connessione al server', 'danger');
        }
    }

    async resetContatore(codice_fiscale) {
        try {
            const response = await fetch('/api/configurazione/test/reset-contatore', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ codice_fiscale })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert('Contatore resettato con successo', 'success');
                this.loadUtentiDisattivati();
            } else {
                showAlert(data.error || 'Errore reset contatore', 'danger');
            }
            
        } catch (error) {
            console.error('Errore reset:', error);
            showAlert('Errore di connessione al server', 'danger');
        }
    }
}

// Inizializza quando il DOM è pronto
document.addEventListener('DOMContentLoaded', () => {
    window.testAccessi = new TestAccessi();
});
