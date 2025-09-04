// Gestione attività recenti
const activitiesContainer = document.getElementById('recent-activities');

// Carica attività recenti
function loadRecentActivities() {
    fetch('/api/recent-activities')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let html = '';
                data.activities.forEach(activity => {
                    html += getActivityItem(activity);
                });
                activitiesContainer.innerHTML = html || `
                    <div class="list-group-item text-center text-muted">
                        <small>Nessuna attività recente</small>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Errore caricamento attività:', error);
            activitiesContainer.innerHTML = `
                <div class="list-group-item text-center text-danger">
                    <small>Errore caricamento attività</small>
                </div>
            `;
        });
}

// Formatta elemento attività
function getActivityItem(activity) {
    const icons = {
        'CONFIG_UPDATE': 'fas fa-cog',
        'USER_CREATE': 'fas fa-user-plus',
        'USER_UPDATE': 'fas fa-user-edit',
        'USER_DELETE': 'fas fa-user-times',
        'LOGIN': 'fas fa-sign-in-alt',
        'LOGOUT': 'fas fa-sign-out-alt',
        'PASSWORD_RESET': 'fas fa-key',
        'SYSTEM': 'fas fa-server'
    };

    const icon = icons[activity.type] || 'fas fa-info-circle';
    const time = formatActivityTime(activity.timestamp);

    return `
        <div class="list-group-item">
            <div class="d-flex align-items-center">
                <div class="me-3">
                    <i class="${icon} fa-lg text-primary"></i>
                </div>
                <div class="flex-grow-1">
                    <div class="mb-1">${activity.message}</div>
                    <small class="text-muted">${time}</small>
                </div>
            </div>
        </div>
    `;
}

// Formatta timestamp
function formatActivityTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    // Meno di un minuto
    if (diff < 60000) {
        return 'Adesso';
    }
    
    // Meno di un'ora
    if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000);
        return `${minutes} minut${minutes === 1 ? 'o' : 'i'} fa`;
    }
    
    // Meno di un giorno
    if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000);
        return `${hours} or${hours === 1 ? 'a' : 'e'} fa`;
    }
    
    // Meno di una settimana
    if (diff < 604800000) {
        const days = Math.floor(diff / 86400000);
        return `${days} giorn${days === 1 ? 'o' : 'i'} fa`;
    }
    
    // Data completa
    return date.toLocaleString('it-IT', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Aggiorna ogni minuto
setInterval(loadRecentActivities, 60000);

// Carica attività iniziali
loadRecentActivities();
