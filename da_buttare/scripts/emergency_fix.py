# File: /opt/access_control/scripts/emergency_fix.py
# Fix di emergenza - ripristina DASHBOARD_TEMPLATE

content = '''# File: /opt/access_control/src/api/dashboard_templates.py
# Template HTML per dashboard web

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sistema Controllo Accessi - Login</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .login-container { max-width: 400px; margin: 0 auto; padding-top: 100px; }
        .card { border: none; border-radius: 15px; box-shadow: 0 8px 30px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="card">
            <div class="card-body p-5">
                <div class="text-center mb-4">
                    <i class="fas fa-shield-alt fa-3x text-primary mb-3"></i>
                    <h4>Sistema Controllo Accessi</h4>
                    <p class="text-muted">Isola Ecologica RAEE - Rende</p>
                </div>
                
                {% if error %}
                <div class="alert alert-danger">{{ error }}</div>
                {% endif %}
                
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label">Username</label>
                        <input type="text" class="form-control" name="username" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Password</label>
                        <input type="password" class="form-control" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">
                        <i class="fas fa-sign-in-alt me-2"></i>Accedi
                    </button>
                </form>
                
                <div class="mt-4 text-center">
                    <small class="text-muted">
                        Credenziali: admin/admin123, gestore/gestore123, readonly/readonly123
                    </small>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sistema Controllo Accessi - Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .navbar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .stat-card { border: none; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); transition: transform 0.2s; }
        .stat-card:hover { transform: translateY(-5px); }
        .stat-number { font-size: 2.5rem; font-weight: bold; }
        .hardware-card { border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-shield-alt me-2"></i>Sistema Controllo Accessi
            </span>
            <div class="navbar-nav">
                <span class="navbar-text me-3">Isola Ecologica RAEE - Rende</span>
                <a href="/logout" class="btn btn-outline-light btn-sm">
                    <i class="fas fa-sign-out-alt me-1"></i>Logout
                </a>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <h1>Dashboard funzionante - da completare</h1>
    </div>
</body>
</html>
"""

def get_dashboard_template():
    """Ritorna il template dashboard"""
    return DASHBOARD_TEMPLATE
'''

# Scrivi il file
with open('/opt/access_control/src/api/dashboard_templates.py', 'w') as f:
    f.write(content)

print("✅ File ripristinato con versione minima funzionante")
