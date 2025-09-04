#!/bin/bash

# generate_project_documentation.sh
# Script per generare documentazione completa del progetto access_control

set -e

# Configurazione
PROJECT_ROOT="$(pwd)"
OUTPUT_FILE="DOCUMENTAZIONE_PROGETTO_COMPLETA_$(date +%Y%m%d_%H%M%S).md"
TEMP_DIR="/tmp/project_doc_$$"

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Cartelle e file da escludere
EXCLUDE_PATTERNS=(
    "__pycache__"
    ".cache"
    ".pytest_cache"
    "venv"
    ".vscode"
    "backups"
    ".continue"
    "backup_*"
    "*_backup_*"
    "*.pyc"
    "*.pyo" 
    "*.pyd"
    ".git"
    ".gitignore"
    "node_modules"
    "*.log"
    "*.tmp"
    "*.temp"
    "cookies.txt"
    "da_buttare"
    "cline_test_report_*.json"
    "*.md5"
    "*.tar.gz"
    "access.db"
    "partner_cache.json"
)

# Tipi di file da processare (aggiungi estensioni se necessario)
INCLUDE_EXTENSIONS=(
    "py"
    "sh" 
    "md"
    "txt"
    "json"
    "yml"
    "yaml"
    "html"
    "css"
    "js"
    "c"
    "h"
    "sql"
    "ini"
    "conf"
    "cfg"
    "Makefile"
    "dockerfile"
    "Dockerfile"
)

# Funzione per verificare se un file/cartella deve essere escluso
should_exclude() {
    local path="$1"
    local basename_path=$(basename "$path")
    
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        if [[ "$basename_path" == $pattern ]] || [[ "$path" == *"$pattern"* ]]; then
            return 0  # Escludi
        fi
    done
    return 1  # Non escludere
}

# Funzione per verificare se un file deve essere incluso
should_include_file() {
    local file="$1"
    local ext="${file##*.}"
    local basename_file=$(basename "$file")
    
    # File senza estensione ma con nomi specifici
    case "$basename_file" in
        "Makefile"|"README"|"LICENSE"|"CHANGELOG"|"INSTALL")
            return 0
            ;;
    esac
    
    # Controllo per estensione
    for allowed_ext in "${INCLUDE_EXTENSIONS[@]}"; do
        if [[ "$ext" == "$allowed_ext" ]]; then
            return 0
        fi
    done
    
    return 1
}

# Funzione per determinare il tipo di file
get_file_type() {
    local file="$1"
    local ext="${file##*.}"
    local basename_file=$(basename "$file")
    
    case "$ext" in
        "py") echo "Python" ;;
        "sh") echo "Shell Script" ;;
        "md") echo "Markdown" ;;
        "html") echo "HTML" ;;
        "css") echo "CSS" ;;
        "js") echo "JavaScript" ;;
        "c") echo "C Source" ;;
        "h") echo "C Header" ;;
        "sql") echo "SQL" ;;
        "json") echo "JSON Configuration" ;;
        "yml"|"yaml") echo "YAML Configuration" ;;
        "txt") echo "Text File" ;;
        "ini"|"conf"|"cfg") echo "Configuration File" ;;
        *) 
            case "$basename_file" in
                "Makefile") echo "Makefile" ;;
                *) echo "File" ;;
            esac
            ;;
    esac
}

# Funzione per ottenere statistiche del file
get_file_stats() {
    local file="$1"
    local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
    local lines=0
    
    if [[ -f "$file" && -r "$file" ]]; then
        lines=$(wc -l < "$file" 2>/dev/null || echo "0")
    fi
    
    echo "Size: ${size} bytes | Lines: ${lines}"
}

# Funzione per processare un file
process_file() {
    local file="$1"
    local relative_path="${file#$PROJECT_ROOT/}"
    local file_type=$(get_file_type "$file")
    local file_stats=$(get_file_stats "$file")
    local dirname_path=$(dirname "$relative_path")
    
    echo "## 📄 $(basename "$file")"
    echo ""
    echo "**Tipo:** $file_type  "
    echo "**Percorso:** \`$dirname_path\`  "
    echo "**Path completo:** \`$relative_path\`  "
    echo "**Statistiche:** $file_stats  "
    echo ""
    
    # Controlla se il file è leggibile
    if [[ ! -r "$file" ]]; then
        echo "⚠️ **File non leggibile**"
        echo ""
        return
    fi
    
    # Controlla se il file è binario
    if file "$file" | grep -q "binary"; then
        echo "🔒 **File binario - contenuto non mostrato**"
        echo ""
        return
    fi
    
    # Controlla dimensione file (max 1MB)
    local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
    if [[ $size -gt 1048576 ]]; then
        echo "📦 **File troppo grande (>1MB) - contenuto non mostrato**"
        echo ""
        return
    fi
    
    echo "### Contenuto:"
    echo ""
    
    # Determina il linguaggio per il syntax highlighting
    local lang=""
    case "${file##*.}" in
        "py") lang="python" ;;
        "sh") lang="bash" ;;
        "js") lang="javascript" ;;
        "html") lang="html" ;;
        "css") lang="css" ;;
        "c") lang="c" ;;
        "h") lang="c" ;;
        "sql") lang="sql" ;;
        "json") lang="json" ;;
        "yml"|"yaml") lang="yaml" ;;
        "md") lang="markdown" ;;
        *) lang="text" ;;
    esac
    
    echo "\`\`\`$lang"
    cat "$file" 2>/dev/null || echo "Errore lettura file"
    echo ""
    echo "\`\`\`"
    echo ""
    echo "---"
    echo ""
}

# Funzione per creare l'indice
create_index() {
    local temp_file="$1"
    
    echo "# 📚 DOCUMENTAZIONE COMPLETA PROGETTO ACCESS CONTROL"
    echo ""
    echo "**Generato il:** $(date '+%Y-%m-%d %H:%M:%S')  "
    echo "**Directory progetto:** \`$PROJECT_ROOT\`  "
    echo "**Versione script:** 1.0  "
    echo ""
    
    echo "## 📋 Indice Generale"
    echo ""
    
    # Genera indice per directory
    find "$PROJECT_ROOT" -type d | while read -r dir; do
        if should_exclude "$dir"; then
            continue
        fi
        
        local relative_dir="${dir#$PROJECT_ROOT/}"
        if [[ "$relative_dir" == "." ]]; then
            continue
        fi
        
        local level=$(echo "$relative_dir" | tr -cd '/' | wc -c)
        local indent=""
        for ((i=0; i<level; i++)); do
            indent="  $indent"
        done
        
        local dir_name=$(basename "$dir")
        echo "$indent- 📁 **$dir_name/** (\`$relative_dir\`)"
        
        # Lista file nella directory
        find "$dir" -maxdepth 1 -type f | while read -r file; do
            if should_exclude "$file" || ! should_include_file "$file"; then
                continue
            fi
            
            local file_name=$(basename "$file")
            local file_type=$(get_file_type "$file")
            echo "$indent  - 📄 $file_name ($file_type)"
        done
    done
    
    echo ""
    echo "## 📊 Statistiche Progetto"
    echo ""
    
    # Conta file per tipo
    local total_files=0
    local total_lines=0
    local total_size=0
    
    declare -A file_counts
    declare -A line_counts
    
    find "$PROJECT_ROOT" -type f | while read -r file; do
        if should_exclude "$file" || ! should_include_file "$file"; then
            continue
        fi
        
        local ext="${file##*.}"
        local lines=$(wc -l < "$file" 2>/dev/null || echo "0")
        local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
        
        echo "$ext:$lines:$size"
    done > "$temp_file"
    
    # Processa statistiche
    local py_files=0 py_lines=0
    local sh_files=0 sh_lines=0
    local js_files=0 js_lines=0
    local html_files=0 html_lines=0
    local css_files=0 css_lines=0
    local md_files=0 md_lines=0
    local other_files=0 other_lines=0
    
    while IFS=':' read -r ext lines size; do
        total_files=$((total_files + 1))
        total_lines=$((total_lines + lines))
        total_size=$((total_size + size))
        
        case "$ext" in
            "py") py_files=$((py_files + 1)); py_lines=$((py_lines + lines)) ;;
            "sh") sh_files=$((sh_files + 1)); sh_lines=$((sh_lines + lines)) ;;
            "js") js_files=$((js_files + 1)); js_lines=$((js_lines + lines)) ;;
            "html") html_files=$((html_files + 1)); html_lines=$((html_lines + lines)) ;;
            "css") css_files=$((css_files + 1)); css_lines=$((css_lines + lines)) ;;
            "md") md_files=$((md_files + 1)); md_lines=$((md_lines + lines)) ;;
            *) other_files=$((other_files + 1)); other_lines=$((other_lines + lines)) ;;
        esac
    done < "$temp_file"
    
    # Converti bytes in MB
    local size_mb=$((total_size / 1024 / 1024))
    
    echo "| Tipo File | Numero File | Linee Codice |"
    echo "|-----------|-------------|--------------|"
    echo "| Python (.py) | $py_files | $py_lines |"
    echo "| Shell (.sh) | $sh_files | $sh_lines |"
    echo "| JavaScript (.js) | $js_files | $js_lines |"
    echo "| HTML (.html) | $html_files | $html_lines |"
    echo "| CSS (.css) | $css_files | $css_lines |"
    echo "| Markdown (.md) | $md_files | $md_lines |"
    echo "| Altri | $other_files | $other_lines |"
    echo "| **TOTALE** | **$total_files** | **$total_lines** |"
    echo ""
    echo "**Dimensione totale:** ${size_mb}MB (${total_size} bytes)"
    echo ""
    
    rm -f "$temp_file"
}

# Funzione principale
main() {
    log_info "Inizializzazione generazione documentazione..."
    
    if [[ ! -d "$PROJECT_ROOT/src" ]]; then
        log_error "Directory 'src' non trovata. Assicurati di essere nella root del progetto."
        exit 1
    fi
    
    # Crea directory temporanea
    mkdir -p "$TEMP_DIR"
    
    log_info "Generazione indice e statistiche..."
    
    # Crea il file di output
    {
        create_index "$TEMP_DIR/stats.tmp"
        
        echo ""
        echo "---"
        echo ""
        echo "# 🗂️ CONTENUTO FILES"
        echo ""
        
        # Processa tutti i file
        find "$PROJECT_ROOT" -type f | sort | while read -r file; do
            if should_exclude "$file" || ! should_include_file "$file"; then
                continue
            fi
            
            local relative_path="${file#$PROJECT_ROOT/}"
            log_info "Processando: $relative_path"
            
            process_file "$file"
        done
        
        echo ""
        echo "---"
        echo ""
        echo "## 📝 Note Finali"
        echo ""
        echo "- Documentazione generata automaticamente"
        echo "- File binari e cache esclusi"
        echo "- File superiori a 1MB non mostrati per limitazioni di dimensione"
        echo "- Per aggiornamenti, ri-eseguire lo script"
        echo ""
        echo "**Script generato il:** $(date)"
        echo "**Versione:** 1.0"
        
    } > "$OUTPUT_FILE"
    
    # Cleanup
    rm -rf "$TEMP_DIR"
    
    # Statistiche finali
    local file_size=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null || echo "0")
    local file_lines=$(wc -l < "$OUTPUT_FILE")
    local size_mb=$((file_size / 1024 / 1024))
    
    log_success "Documentazione generata con successo!"
    echo ""
    echo "📄 **File:** $OUTPUT_FILE"
    echo "📊 **Dimensione:** ${size_mb}MB (${file_size} bytes)"
    echo "📝 **Righe:** $file_lines"
    echo ""
    log_info "Per visualizzare: less $OUTPUT_FILE"
    log_info "Per convertire in PDF: pandoc $OUTPUT_FILE -o documentazione.pdf"
}

# Esegui lo script
main "$@"
