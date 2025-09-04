# TASK: CREAZIONE NUOVA PAGINA

## STRUTTURA FILE PER NUOVA PAGINA

1. **HTML** in `src/api/static/html/nome-pagina.html`:
```html
<div class="container mt-4">
    <h2>Titolo Pagina</h2>
    
    <div class="row">
        <div class="col-md-12">
            <!-- Contenuto -->
        </div>
    </div>
</div>
```

2. **JavaScript** in `src/api/static/js/nome-pagina.js`:
```javascript
// Inizializzazione
document.addEventListener('DOMContentLoaded', function() {
    loadData();
});

// Caricamento dati
async function loadData() {
    try {
        const response = await fetch('/api/endpoint');
        const data = await response.json();
        
        if (data.success) {
            renderData(data.data);
        } else {
            showAlert('danger', data.message);
        }
    } catch (error) {
        console.error('Errore:', error);
        showAlert('danger', 'Errore caricamento dati');
    }
}

// Utility alert (usa quella esistente)
function showAlert(type, message) {
    // Implementazione esistente
}
```

3. **CSS** (se necessario) in `src/api/static/css/nome-pagina.css`

4. **Aggiungi route** in `dashboard_templates.py`:
```python
@app.route('/nome-pagina')
@login_required
def nome_pagina():
    return render_template_string(open('static/html/nome-pagina.html').read())
```

5. **Aggiungi voce menu** in navigazione
