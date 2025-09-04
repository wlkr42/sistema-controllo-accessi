// Orologio live per tutte le pagine
class Clock {
    constructor() {
        // Trova l'elemento orologio esistente invece di crearne uno nuovo
        this.clockElement = document.querySelector('.system-clock');
        if (!this.clockElement) {
            console.error('Elemento orologio non trovato nella navbar');
            return;
        }
        
        // Avvia l'orologio
        this.updateClock();
        setInterval(() => this.updateClock(), 1000);
    }
    
    updateClock() {
        if (!this.clockElement) return;
        
        const now = new Date();
        const time = now.toLocaleTimeString('it-IT', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        
        const date = now.toLocaleDateString('it-IT', {
            weekday: 'long',
            day: 'numeric',
            month: 'long',
            year: 'numeric'
        });
        
        const timeEl = this.clockElement.querySelector('.clock-time');
        const dateEl = this.clockElement.querySelector('.clock-date');
        
        if (timeEl) timeEl.textContent = time;
        if (dateEl) dateEl.textContent = date;
    }
}

// Inizializza quando il DOM è pronto
document.addEventListener('DOMContentLoaded', () => {
    window.systemClock = new Clock();
});
