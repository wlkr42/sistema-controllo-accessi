# TASK: CREAZIONE NUOVO MODULO

## PASSI DA SEGUIRE

1. **Crea file modulo**
   - Path: `src/api/modules/nome_modulo.py`
   - Usa Blueprint Flask
   - Importa utilities da `src/api/utils.py`

2. **Struttura base modulo**:
```python
from flask import Blueprint, request, jsonify, session
from functools import wraps
import logging
from database.database_manager import DatabaseManager

# Blueprint
nome_bp = Blueprint('nome', __name__)
logger = logging.getLogger(__name__)

# Decorator login_required se necessario
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"success": False, "message": "Login richiesto"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Endpoints
@nome_bp.route('/api/nome', methods=['GET'])
@login_required
def get_items():
    try:
        # Logica
        return jsonify({"success": True, "data": []})
    except Exception as e:
        logger.error(f"Errore: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500
```

3. **Registra in web_api.py**:
```python
from modules.nome_modulo import nome_bp
app.register_blueprint(nome_bp)
```

4. **Crea test**:
   - Path: `tests/unit/test_nome_modulo.py`

5. **Aggiorna documentazione**:
   - Aggiungi in `.clinerules/02-memory.md`
   - Documenta endpoint e funzionalità
