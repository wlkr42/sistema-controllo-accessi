// File: /opt/access_control/src/api/static/js/utenti_autorizzati.js

// Elementi DOM
const searchInput = document.getElementById('search-input');
const searchClear = document.getElementById('search-clear');
const tableBody = document.getElementById('users-table-body');
const loadingSpinner = document.getElementById('loading-spinner');
const noResults = document.getElementById('no-results');

// Statistiche
const statTotale = document.getElementById('stat-totale');
const statAttivi = document.getElementById('stat-attivi');
const statNuovi = document.getElementById('stat-nuovi');

// Debounce per la ricerca
let searchTimeout = null;

// Carica dati iniziali
document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
    loadStats();
});

// Event listener per la ricerca
searchInput.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        loadUsers(e.target.value);
    }, 300);
});

// Event listener per pulire la ricerca
searchClear.addEventListener('click', () => {
    searchInput.value = '';
    loadUsers();
});

// Carica statistiche
async function loadStats() {
    try {
        const response = await fetch('/api/utenti-autorizzati/stats');
        const data = await response.json();
        
        if (data.success) {
            statTotale.textContent = data.stats.totale;
            statAttivi.textContent = data.stats.attivi;
            statNuovi.textContent = data.stats.nuovi_30gg;
        }
    } catch (error) {
        console.error('Errore caricamento statistiche:', error);
    }
}

// Carica utenti con filtro opzionale
async function loadUsers(search = '') {
    showLoading(true);
    
    try {
        const url = `/api/utenti-autorizzati/list${search ? `?search=${encodeURIComponent(search)}` : ''}`;
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            renderUsers(data.utenti);
            noResults.classList.toggle('d-none', data.utenti.length > 0);
        } else {
            showError('Errore caricamento utenti');
        }
    } catch (error) {
        console.error('Errore caricamento utenti:', error);
        showError('Errore di rete');
    } finally {
        showLoading(false);
    }
}

// Renderizza tabella utenti
function renderUsers(users) {
    tableBody.innerHTML = '';
    
    users.forEach(user => {
        const row = document.createElement('tr');
        
        // Formatta date
        const dataInserimento = new Date(user.data_inserimento).toLocaleDateString('it-IT');
        const dataAggiornamento = new Date(user.data_aggiornamento).toLocaleDateString('it-IT');
        
        // Stato attivo/inattivo
        const statoBadge = user.attivo ?
            '<span class="badge bg-success status-badge">Attivo</span>' :
            '<span class="badge bg-danger status-badge">Inattivo</span>';
        
        row.innerHTML = `
            <td>${user.codice_fiscale}</td>
            <td>${user.nome || '-'}</td>
            <td>${dataInserimento}</td>
            <td>${dataAggiornamento}</td>
            <td>${user.creato_da || '-'}</td>
            <td>${user.modificato_da || '-'}</td>
            <td>${user.note || '-'}</td>
            <td>${statoBadge}</td>
            <td>
                <button class="btn btn-sm btn-${user.attivo ? 'danger' : 'success'}"
                        onclick="toggleUserStatus('${user.codice_fiscale}', ${user.attivo})">
                    <i class="fas fa-${user.attivo ? 'ban' : 'check'}"></i>
                </button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Attiva/disattiva utente
async function toggleUserStatus(codiceFiscale, currentStatus) {
    try {
        const response = await fetch('/api/utenti-autorizzati/toggle-active', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ codice_fiscale: codiceFiscale })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Ricarica dati e statistiche
            loadUsers(searchInput.value);
            loadStats();
            
            // Notifica
            showNotification(data.message, 'success');
        } else {
            showNotification(data.error, 'danger');
        }
    } catch (error) {
        console.error('Errore toggle stato:', error);
        showNotification('Errore di rete', 'danger');
    }
}

// Utility per mostrare/nascondere loading
function showLoading(show) {
    loadingSpinner.classList.toggle('d-none', !show);
    tableBody.classList.toggle('d-none', show);
}

// Utility per mostrare errori
function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger mt-3';
    alert.textContent = message;
    
    tableBody.innerHTML = '';
    tableBody.appendChild(alert);
}

// Utility per mostrare notifiche toast
function showNotification(message, type = 'success') {
    // Crea toast container se non esiste
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Crea toast
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toastEl);
    
    // Inizializza e mostra toast
    const toast = new bootstrap.Toast(toastEl, {
        autohide: true,
        delay: 3000
    });
    toast.show();
    
    // Rimuovi dopo nascosto
    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    });
}
