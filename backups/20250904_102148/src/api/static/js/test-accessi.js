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
        this.ingressiInput = document.getElementById('ingressiMensili');
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

    selezionaUtente(utente) {
        this.selectedUtente = utente;
        this.utenteInput.value = utente.label;
        this.searchResults.style.display = 'none';
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
        const ingressi = parseInt(this.ingressiInput.value);
        
        if (!codice_fiscale) {
            showAlert('Seleziona un utente', 'warning');
            return;
        }
        
        try {
            const response = await fetch('/api/configurazione/test/set-ingressi', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ codice_fiscale, ingressi })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert('Conteggio ingressi aggiornato', 'success');
                this.loadUtentiDisattivati();
            } else {
                showAlert(data.error || 'Errore aggiornamento conteggio', 'danger');
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
                showAlert(data.message, 'success');
                // Simula sequenza accesso autorizzato
                await this.simulateAccessGranted();
                // Ricarica dati
                this.loadUtentiDisattivati();
                this.ingressiInput.value = '';
            } else {
                showAlert(data.error || 'Errore simulazione accesso', 'danger');
                // Simula sequenza accesso negato
                await this.simulateAccessDenied();
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
