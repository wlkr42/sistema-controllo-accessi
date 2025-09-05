// Orologio live per tutte le pagine - USA L'ORA DEL SERVER
class Clock {
    constructor() {
        // Trova l'elemento orologio esistente invece di crearne uno nuovo
        this.clockElement = document.querySelector('.system-clock');
        if (!this.clockElement) {
            console.error('Elemento orologio non trovato nella navbar');
            return;
        }
        
        // Variabili per sincronizzazione con server
        this.serverTimeOffset = 0;
        this.lastSync = 0;
        
        // Sincronizza con il server all'avvio
        this.syncWithServer();
        
        // Avvia l'orologio
        this.updateClock();
        setInterval(() => this.updateClock(), 1000);
        
        // Risincronizza ogni 5 minuti
        setInterval(() => this.syncWithServer(), 5 * 60 * 1000);
    }
    
    async syncWithServer() {
        try {
            const response = await fetch('/api/server-time');
            if (response.ok) {
                const data = await response.json();
                
                // Calcola offset tra ora server e ora client
                const serverDate = new Date(data.timestamp);
                const clientDate = new Date();
                this.serverTimeOffset = serverDate.getTime() - clientDate.getTime();
                this.lastSync = Date.now();
                
                // Aggiorna immediatamente l'orologio
                this.updateClock();
                
                // Mostra indicatore di sincronizzazione
                this.showSyncIndicator();
            }
        } catch (error) {
            console.error('Errore sincronizzazione ora server:', error);
        }
    }
    
    showSyncIndicator() {
        const indicator = document.createElement('span');
        indicator.innerHTML = ' <i class="fas fa-sync text-success"></i>';
        indicator.style.fontSize = '0.8em';
        this.clockElement.appendChild(indicator);
        
        setTimeout(() => {
            indicator.remove();
        }, 2000);
    }
    
    updateClock() {
        if (!this.clockElement) return;
        
        // Usa l'ora del client + offset del server
        const now = new Date(Date.now() + this.serverTimeOffset);
        
        const time = now.toLocaleTimeString('it-IT', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            timeZone: 'Europe/Rome'
        });
        
        const date = now.toLocaleDateString('it-IT', {
            weekday: 'long',
            day: 'numeric',
            month: 'long',
            year: 'numeric',
            timeZone: 'Europe/Rome'
        });
        
        const timeEl = this.clockElement.querySelector('.clock-time');
        const dateEl = this.clockElement.querySelector('.clock-date');
        
        if (timeEl) timeEl.textContent = time;
        if (dateEl) dateEl.textContent = date + ' (Roma)';
    }
}

// Inizializza quando il DOM è pronto
document.addEventListener('DOMContentLoaded', () => {
    window.systemClock = new Clock();
});
