#!/bin/bash
# ============================================================================
# CONFIGURAZIONE INSTALLAZIONE - MODIFICARE PRIMA DI ESEGUIRE
# ============================================================================

# Repository GitHub
export GITHUB_REPO="github.com/wlkr42/sistema-controllo-accessi"
export GITHUB_BRANCH="main"

# Credenziali GitHub (opzionale - se non impostate verranno richieste)
# export GITHUB_USER="your_username"
# export GITHUB_TOKEN="your_personal_access_token"

# Directory installazione
export INSTALL_DIR="/opt/access_control"

# Ambiente (development o production)
export INSTALL_ENV="development"

# Python version
export PYTHON_VERSION="3.10"

# Database name
export DB_NAME="access_control.db"

# ============================================================================
# FINE CONFIGURAZIONE
# ============================================================================