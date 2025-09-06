// File: /opt/access_control/src/api/static/js/utenti_autorizzati.js

// Elementi DOM
const searchInput = document.getElementById('search-input');
const searchClear = document.getElementById('search-clear');
const tableBody = document.getElementById('users-table-body');
const loadingSpinner = document.getElementById('loading-spinner');
const noResults = document.getElementById('no-results');
const perPageSelect = document.getElementById('per-page-select');
const paginationContainer = document.getElementById('pagination-container');

// Statistiche
const statTotale = document.getElementById('stat-totale');
const statAttivi = document.getElementById('stat-attivi');
const statNuovi = document.getElementById('stat-nuovi');

// Stato paginazione
let currentPage = 1;
let currentPerPage = 30;
let currentSearch = '';
let totalPages = 1;

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
        currentSearch = e.target.value;
        currentPage = 1; // Reset alla prima pagina quando si cerca
        loadUsers();
    }, 300);
});

// Event listener per pulire la ricerca
searchClear.addEventListener('click', () => {
    searchInput.value = '';
    currentSearch = '';
    currentPage = 1;
    loadUsers();
});

// Event listener per cambio elementi per pagina
perPageSelect.addEventListener('change', (e) => {
    currentPerPage = e.target.value;
    currentPage = 1; // Reset alla prima pagina
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

// Carica utenti con paginazione
async function loadUsers() {
    showLoading(true);
    
    try {
        const params = new URLSearchParams();
        if (currentSearch) params.append('search', currentSearch);
        params.append('page', currentPage);
        params.append('per_page', currentPerPage);
        
        const url = `/api/utenti-autorizzati/list?${params.toString()}`;
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            renderUsers(data.utenti);
            totalPages = data.total_pages;
            updatePagination(data.page, data.total_pages, data.total);
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

// Formatta data italiana con ora
function formatDateTimeIT(dateString) {
    if (!dateString) return '-';
    
    try {
        // Crea oggetto Date dal timestamp
        const date = new Date(dateString);
        
        // Formatta data e ora in formato italiano
        const options = {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        };
        
        return date.toLocaleString('it-IT', options);
    } catch (error) {
        return dateString; // Ritorna la stringa originale se c'è un errore
    }
}

// Renderizza tabella utenti
function renderUsers(users) {
    tableBody.innerHTML = '';
    
    users.forEach(user => {
        const row = document.createElement('tr');
        
        // Formatta date con ora
        const dataInserimento = formatDateTimeIT(user.data_inserimento);
        const dataAggiornamento = formatDateTimeIT(user.data_aggiornamento);
        
        // Bottone azione basato sullo stato
        const actionButton = user.attivo ?
            `<button class="btn btn-sm btn-danger" title="Disattiva"
                    onclick="toggleUserStatus('${user.codice_fiscale}', ${user.attivo})">
                <i class="fas fa-ban"></i>
            </button>` :
            `<button class="btn btn-sm btn-success" title="Attiva"
                    onclick="toggleUserStatus('${user.codice_fiscale}', ${user.attivo})">
                <i class="fas fa-check"></i>
            </button>`;
        
        row.innerHTML = `
            <td>${user.codice_fiscale}</td>
            <td>${user.nome || '-'}</td>
            <td>${dataInserimento}</td>
            <td>${dataAggiornamento}</td>
            <td>${user.creato_da || 'Sync Odoo'}</td>
            <td>${user.note || '-'}</td>
            <td>${actionButton}</td>
        `;
        
        // Evidenzia riga se utente non attivo
        if (!user.attivo) {
            row.classList.add('table-danger', 'opacity-75');
        }
        
        tableBody.appendChild(row);
    });
}

// Aggiorna controlli paginazione
function updatePagination(page, totalPages, totalItems) {
    const pagination = paginationContainer.querySelector('.pagination');
    pagination.innerHTML = '';
    
    // Info elementi visualizzati
    const startItem = (page - 1) * (currentPerPage === 'all' ? totalItems : parseInt(currentPerPage)) + 1;
    const endItem = Math.min(page * (currentPerPage === 'all' ? totalItems : parseInt(currentPerPage)), totalItems);
    
    // Aggiungi info totale
    const infoItem = document.createElement('li');
    infoItem.className = 'page-item disabled';
    infoItem.innerHTML = `<span class="page-link">Mostrando ${startItem}-${endItem} di ${totalItems}</span>`;
    pagination.appendChild(infoItem);
    
    // Se ci sono più pagine, mostra i controlli
    if (totalPages > 1) {
        // Pulsante precedente
        const prevItem = document.createElement('li');
        prevItem.className = `page-item ${page === 1 ? 'disabled' : ''}`;
        prevItem.innerHTML = `<a class="page-link" href="#" onclick="changePage(${page - 1}); return false;">
            <i class="fas fa-chevron-left"></i>
        </a>`;
        pagination.appendChild(prevItem);
        
        // Numeri pagina (mostra max 5 pagine)
        let startPage = Math.max(1, page - 2);
        let endPage = Math.min(totalPages, startPage + 4);
        
        if (endPage - startPage < 4) {
            startPage = Math.max(1, endPage - 4);
        }
        
        // Prima pagina se non visibile
        if (startPage > 1) {
            const firstItem = document.createElement('li');
            firstItem.className = 'page-item';
            firstItem.innerHTML = `<a class="page-link" href="#" onclick="changePage(1); return false;">1</a>`;
            pagination.appendChild(firstItem);
            
            if (startPage > 2) {
                const dots = document.createElement('li');
                dots.className = 'page-item disabled';
                dots.innerHTML = '<span class="page-link">...</span>';
                pagination.appendChild(dots);
            }
        }
        
        // Pagine
        for (let i = startPage; i <= endPage; i++) {
            const pageItem = document.createElement('li');
            pageItem.className = `page-item ${i === page ? 'active' : ''}`;
            pageItem.innerHTML = `<a class="page-link" href="#" onclick="changePage(${i}); return false;">${i}</a>`;
            pagination.appendChild(pageItem);
        }
        
        // Ultima pagina se non visibile
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                const dots = document.createElement('li');
                dots.className = 'page-item disabled';
                dots.innerHTML = '<span class="page-link">...</span>';
                pagination.appendChild(dots);
            }
            
            const lastItem = document.createElement('li');
            lastItem.className = 'page-item';
            lastItem.innerHTML = `<a class="page-link" href="#" onclick="changePage(${totalPages}); return false;">${totalPages}</a>`;
            pagination.appendChild(lastItem);
        }
        
        // Pulsante successivo
        const nextItem = document.createElement('li');
        nextItem.className = `page-item ${page === totalPages ? 'disabled' : ''}`;
        nextItem.innerHTML = `<a class="page-link" href="#" onclick="changePage(${page + 1}); return false;">
            <i class="fas fa-chevron-right"></i>
        </a>`;
        pagination.appendChild(nextItem);
    }
}

// Cambia pagina
function changePage(page) {
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    loadUsers();
    // Scroll to top della tabella
    window.scrollTo({ top: 200, behavior: 'smooth' });
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
            loadUsers();
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