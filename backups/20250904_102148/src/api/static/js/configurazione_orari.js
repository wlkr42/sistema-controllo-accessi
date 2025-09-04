class ScheduleManager {
    constructor() {
        this.lastModifiedDayId = null;  // Traccia l'ultimo giorno modificato
        this.daysOfWeek = [
            { id: 0, name: 'Lunedi' },
            { id: 1, name: 'Martedi' },
            { id: 2, name: 'Mercoledi' },
            { id: 3, name: 'Giovedi' },
            { id: 4, name: 'Venerdi' },
            { id: 5, name: 'Sabato' },
            { id: 6, name: 'Domenica' }
        ];
        
        this.timeSlots = {
            morning: {
                open: ['00:00', '00:30', '01:00', '01:30', '02:00', '02:30', '03:00', '03:30', '04:00', '04:30', '05:00', '05:30', '06:00', '06:30', '07:00', '07:30', '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00'],
                close: ['00:30', '01:00', '01:30', '02:00', '02:30', '03:00', '03:30', '04:00', '04:30', '05:00', '05:30', '06:00', '06:30', '07:00', '07:30', '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00']
            },
            afternoon: {
                open: ['12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30', '22:00', '22:30', '23:00', '23:30'],
                close: ['12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30', '22:00', '22:30', '23:00', '23:30', '23:59']
            }
        };
        
        this.init();
    }
    
    init() {
        this.generateDays();
        this.setupEventListeners();
        this.loadCurrentSchedule();
    }
    
    generateDays() {
        const container = document.getElementById('days-container');
        container.innerHTML = ''; // Pulisci il contenitore
        
        this.daysOfWeek.forEach(day => {
            const dayHtml = this.generateDayRow(day);
            container.insertAdjacentHTML('beforeend', dayHtml);
            
            // Setup switch event
            const switchEl = document.getElementById(`${day.id}-switch`);
            if (switchEl) {
                switchEl.addEventListener('change', (e) => {
                    this.toggleDaySchedule(day.id, e.target.checked);
                });
            }
        });
    }
    
    generateDayRow(day) {
        return `
            <div class="day-row d-flex align-items-center">
                <div class="day-name">${day.name}</div>
                <div class="form-check form-switch me-3">
                    <input class="form-check-input" type="checkbox" id="${day.id}-switch" checked>
                    <label class="form-check-label" for="${day.id}-switch">Aperto</label>
                </div>
                <div class="time-slots flex-grow-1" id="${day.id}-slots">
                    <div class="time-slot morning">
                        <span class="time-label">Mattina</span>
                        <select class="form-select time-select" name="${day.id}-morning-open">
                            ${this.generateTimeOptions(this.timeSlots.morning.open, '00:00')}
                        </select>
                        <span class="time-separator">-</span>
                        <select class="form-select time-select" name="${day.id}-morning-close">
                            ${this.generateTimeOptions(this.timeSlots.morning.close, '12:00')}
                        </select>
                    </div>
                    <div class="time-slot afternoon">
                        <span class="time-label">Pomeriggio</span>
                        <select class="form-select time-select" name="${day.id}-afternoon-open">
                            ${this.generateTimeOptions(this.timeSlots.afternoon.open, '15:00')}
                        </select>
                        <span class="time-separator">-</span>
                        <select class="form-select time-select" name="${day.id}-afternoon-close">
                            ${this.generateTimeOptions(this.timeSlots.afternoon.close, '23:59')}
                        </select>
                    </div>
                </div>
            </div>
        `;
    }
    
    generateTimeOptions(times, selected) {
        return times.map(time => 
            `<option value="${time}" ${time === selected ? 'selected' : ''}>${time}</option>`
        ).join('');
    }
    
    toggleDaySchedule(dayId, isOpen) {
        const slots = document.getElementById(`${dayId}-slots`);
        const selects = slots.querySelectorAll('select');
        
        if (isOpen) {
            slots.classList.remove('disabled');
            selects.forEach(select => select.disabled = false);
        } else {
            slots.classList.add('disabled');
            selects.forEach(select => select.disabled = true);
        }
    }
    
    setupEventListeners() {
        // Salva configurazione
        document.getElementById('save-schedule').addEventListener('click', () => {
            this.saveSchedule();
        });
        
        // Copia su tutti i giorni
        document.getElementById('copy-to-all').addEventListener('click', () => {
            this.copyToAllDays();
        });
        
        // Salva limite ingressi
        document.getElementById('save-limits').addEventListener('click', () => {
            this.saveLimits();
        });

        // Aggiungi listener per tracciare l'ultimo giorno modificato
        this.daysOfWeek.forEach(day => {
            const daySlots = document.getElementById(`${day.id}-slots`);
            if (daySlots) {
                const selects = daySlots.querySelectorAll('select');
                selects.forEach(select => {
                    select.addEventListener('change', () => {
                        this.lastModifiedDayId = day.id;
                    });
                });
            }
        });
    }
    
    async loadCurrentSchedule() {
        try {
            const response = await fetch('/api/configurazione/orari');
            const data = await response.json();
            
            if (data.success && data.orari) {
                console.log('Orari caricati:', data.orari);
                
                // Mappa i giorni per nome
                const orariMap = {};
                data.orari.forEach(orario => {
                    orariMap[orario.giorno] = orario;
                    console.log(`Orari per ${orario.giorno}:`, orario);
                });
                
                this.daysOfWeek.forEach(day => {
                    const dayConfig = orariMap[day.name];
                    console.log(`Configurazione per ${day.name}:`, dayConfig);
                    
                    if (dayConfig) {
                        // Imposta switch
                        const switchEl = document.getElementById(`${day.id}-switch`);
                        if (switchEl) {
                            switchEl.checked = dayConfig.aperto;
                            this.toggleDaySchedule(day.id, dayConfig.aperto);
                        }
                        
                        // Imposta orari mattina
                        const morningOpen = document.querySelector(`select[name="${day.id}-morning-open"]`);
                        const morningClose = document.querySelector(`select[name="${day.id}-morning-close"]`);
                        if (morningOpen && morningClose) {
                            morningOpen.value = dayConfig.mattina_inizio || '00:00';
                            morningClose.value = dayConfig.mattina_fine || '12:00';
                            console.log(`Mattina ${day.name}:`, morningOpen.value, '-', morningClose.value);
                        }
                        
                        // Imposta orari pomeriggio
                        const afternoonOpen = document.querySelector(`select[name="${day.id}-afternoon-open"]`);
                        const afternoonClose = document.querySelector(`select[name="${day.id}-afternoon-close"]`);
                        if (afternoonOpen && afternoonClose) {
                            afternoonOpen.value = dayConfig.pomeriggio_inizio || '15:00';
                            afternoonClose.value = dayConfig.pomeriggio_fine || '23:59';
                            console.log(`Pomeriggio ${day.name}:`, afternoonOpen.value, '-', afternoonClose.value);
                        }
                    }
                });
            }
            
            // Carica limite ingressi
            const limitsResponse = await fetch('/api/configurazione/limiti');
            const limitsData = await limitsResponse.json();
            
            if (limitsData.success) {
                document.getElementById('max-entries').value = limitsData.max_ingressi_mensili;
            }
            
        } catch (error) {
            console.error('Errore caricamento configurazione:', error);
            showAlert('Errore caricamento configurazione', 'danger');
        }
    }
    
    async saveSchedule() {
        const orari = this.daysOfWeek.map(day => {
            const isOpen = document.getElementById(`${day.id}-switch`).checked;
            
            return {
                giorno: day.name,
                aperto: isOpen,
                mattina_inizio: isOpen ? document.querySelector(`select[name="${day.id}-morning-open"]`).value : null,
                mattina_fine: isOpen ? document.querySelector(`select[name="${day.id}-morning-close"]`).value : null,
                pomeriggio_inizio: isOpen ? document.querySelector(`select[name="${day.id}-afternoon-open"]`).value : null,
                pomeriggio_fine: isOpen ? document.querySelector(`select[name="${day.id}-afternoon-close"]`).value : null
            };
        });
        
        try {
            console.log('Salvataggio orari:', orari);
            
            const response = await fetch('/api/configurazione/orari', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ orari })
            });
            
            const data = await response.json();
            console.log('Risposta salvataggio orari:', data);
            
            if (data.success) {
                showAlert('Configurazione orari salvata con successo', 'success');
                
                // Attendi un momento prima di ricaricare
                await new Promise(resolve => setTimeout(resolve, 500));
                
                // Ricarica la configurazione
                const configResponse = await fetch('/api/configurazione/orari');
                const configData = await configResponse.json();
                console.log('Risposta ricaricamento orari:', configData);
                
                if (configData.success && configData.orari) {
                    // Aggiorna l'interfaccia con i valori salvati
                    const orariMap = {};
                    configData.orari.forEach(orario => {
                        orariMap[orario.giorno] = orario;
                    });
                    
                    this.daysOfWeek.forEach(day => {
                        const dayConfig = orariMap[day.name];
                        if (dayConfig) {
                            const switchEl = document.getElementById(`${day.id}-switch`);
                            if (switchEl) {
                                switchEl.checked = dayConfig.aperto;
                                this.toggleDaySchedule(day.id, dayConfig.aperto);
                            }
                            
                            if (dayConfig.mattina_inizio) {
                                document.querySelector(`select[name="${day.id}-morning-open"]`).value = dayConfig.mattina_inizio;
                                document.querySelector(`select[name="${day.id}-morning-close"]`).value = dayConfig.mattina_fine;
                            }
                            
                            if (dayConfig.pomeriggio_inizio) {
                                document.querySelector(`select[name="${day.id}-afternoon-open"]`).value = dayConfig.pomeriggio_inizio;
                                document.querySelector(`select[name="${day.id}-afternoon-close"]`).value = dayConfig.pomeriggio_fine;
                            }
                        }
                    });
                }
            } else {
                showAlert(data.error || 'Errore salvataggio configurazione', 'danger');
            }
            
        } catch (error) {
            console.error('Errore salvataggio:', error);
            showAlert('Errore di connessione al server', 'danger');
        }
    }
    

    copyToAllDays() {
        if (this.lastModifiedDayId === null) {
            showAlert('Modifica prima un giorno per copiarlo sugli altri', 'warning');
            return;
        }

        // Prendi i valori dall'ultimo giorno modificato
        const sourceSwitch = document.getElementById(`${this.lastModifiedDayId}-switch`);
        const sourceMorningOpen = document.querySelector(`select[name="${this.lastModifiedDayId}-morning-open"]`);
        const sourceMorningClose = document.querySelector(`select[name="${this.lastModifiedDayId}-morning-close"]`);
        const sourceAfternoonOpen = document.querySelector(`select[name="${this.lastModifiedDayId}-afternoon-open"]`);
        const sourceAfternoonClose = document.querySelector(`select[name="${this.lastModifiedDayId}-afternoon-close"]`);
        
        // Applica a tutti gli altri giorni
        this.daysOfWeek.forEach(day => {
            if (day.id !== this.lastModifiedDayId) {
                const daySwitch = document.getElementById(`${day.id}-switch`);
                daySwitch.checked = sourceSwitch.checked;
                this.toggleDaySchedule(day.id, sourceSwitch.checked);
                
                document.querySelector(`select[name="${day.id}-morning-open"]`).value = sourceMorningOpen.value;
                document.querySelector(`select[name="${day.id}-morning-close"]`).value = sourceMorningClose.value;
                document.querySelector(`select[name="${day.id}-afternoon-open"]`).value = sourceAfternoonOpen.value;
                document.querySelector(`select[name="${day.id}-afternoon-close"]`).value = sourceAfternoonClose.value;
            }
        });
        
        showAlert('Orari copiati su tutti i giorni', 'success');
    }
    
    async saveLimits() {
        const maxEntries = document.getElementById('max-entries').value;
        
        if (!maxEntries || maxEntries < 1) {
            showAlert('Inserire un numero valido di ingressi mensili', 'danger');
            return;
        }
        
        try {
            console.log('Salvataggio limite:', maxEntries);
            
            const response = await fetch('/api/configurazione/limiti', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ max_ingressi_mensili: parseInt(maxEntries) })
            });
            
            const data = await response.json();
            console.log('Risposta salvataggio:', data);
            
            if (data.success) {
                showAlert('Limite ingressi mensili salvato con successo', 'success');
                
                // Attendi un momento prima di ricaricare
                await new Promise(resolve => setTimeout(resolve, 500));
                
                // Ricarica il valore salvato
                const limitsResponse = await fetch('/api/configurazione/limiti');
                const limitsData = await limitsResponse.json();
                console.log('Risposta ricaricamento:', limitsData);
                
                if (limitsData.success) {
                    document.getElementById('max-entries').value = limitsData.max_ingressi_mensili;
                    console.log('Valore aggiornato:', limitsData.max_ingressi_mensili);
                }
            } else {
                showAlert(data.error || 'Errore salvataggio limite', 'danger');
            }
            
        } catch (error) {
            console.error('Errore salvataggio:', error);
            showAlert('Errore di connessione al server', 'danger');
        }
    }
}

// Funzione per mostrare alert
function showAlert(message, type) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Rimuovi alert esistenti
    document.querySelectorAll('.alert').forEach(alert => alert.remove());
    
    // Inserisci nuovo alert all'inizio del container
    document.querySelector('.container').insertAdjacentHTML('afterbegin', alertHtml);
    
    // Auto-chiudi dopo 5 secondi
    setTimeout(() => {
        const alert = document.querySelector('.alert');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

// Inizializza quando il DOM è pronto
document.addEventListener('DOMContentLoaded', () => {
    new ScheduleManager();
});
