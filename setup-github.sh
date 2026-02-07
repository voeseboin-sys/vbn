#!/bin/bash
# =============================================================================
# SETUP-GITHUB.SH v2.0 - Script de configuración para GitHub
# Repositorio: voeseboin-sys/vbn
#
# USO:
#   ./setup-github.sh <NOMBRE_REPO> <TOKEN_GITHUB>
#
# EJEMPLO:
#   ./setup-github.sh vbn TOKEN_BORRADO
# =============================================================================

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# =============================================================================
# CONFIGURACIÓN - MODIFICAR ESTOS VALORES
# =============================================================================

# Tu usuario de GitHub
GITHUB_USER="voeseboin-sys"

# Tu email de GitHub
GITHUB_EMAIL="voeseboin@gmail.com"

# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

print_header() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║     GESTIÓN FÁBRICA v2.0 - Configuración GitHub              ║"
    echo "║     Script de configuración automática                       ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_step() {
    echo ""
    echo -e "${CYAN}▶ $1${NC}"
}

# =============================================================================
# VALIDACIÓN DE ARGUMENTOS
# =============================================================================

if [ $# -lt 2 ]; then
    echo ""
    print_error "Uso incorrecto"
    echo ""
    echo "Uso: ./setup-github.sh <NOMBRE_REPO> <TOKEN_GITHUB>"
    echo ""
    echo "Ejemplo:"
    echo "  ./setup-github.sh vbn TOKEN_BORRADO"
    echo ""
    exit 1
fi

REPO_NAME="$1"
GITHUB_TOKEN="$2"

# =============================================================================
# INICIO DEL SCRIPT
# =============================================================================

print_header

print_info "Usuario GitHub: $GITHUB_USER"
print_info "Repositorio: $REPO_NAME"
print_info "Email: $GITHUB_EMAIL"

# =============================================================================
# PASO 1: Verificar que estamos en el directorio correcto
# =============================================================================

print_step "Paso 1: Verificando estructura del proyecto"

if [ ! -f "main.py" ]; then
    print_error "No se encontró main.py"
    print_info "Asegúrate de ejecutar este script desde el directorio raíz del proyecto"
    exit 1
fi

if [ ! -f "buildozer.spec" ]; then
    print_error "No se encontró buildozer.spec"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    print_error "No se encontró requirements.txt"
    exit 1
fi

print_status "Estructura del proyecto verificada"

# =============================================================================
# PASO 2: Configurar Git
# =============================================================================

print_step "Paso 2: Configurando Git"

git config --global user.email "$GITHUB_EMAIL"
git config --global user.name "$GITHUB_USER"

print_status "Git configurado"
print_info "Email: $GITHUB_EMAIL"
print_info "Usuario: $GITHUB_USER"

# =============================================================================
# PASO 3: Inicializar repositorio
# =============================================================================

print_step "Paso 3: Inicializando repositorio"

if [ -d ".git" ]; then
    print_warning "El directorio ya es un repositorio git"
    
    # Verificar si hay cambios sin commitear
    if ! git diff --quiet HEAD 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
        print_info "Hay cambios pendientes, se procederá a commitear"
    fi
else
    git init
    print_status "Repositorio git inicializado"
fi

# =============================================================================
# PASO 4: Configurar remote
# =============================================================================

print_step "Paso 4: Configurando remote de GitHub"

# Eliminar remote existente si hay
if git remote get-url origin 2>/dev/null; then
    print_info "Eliminando remote existente"
    git remote remove origin
fi

# Configurar nuevo remote con token
REMOTE_URL="https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${REPO_NAME}.git"
git remote add origin "$REMOTE_URL"

print_status "Remote configurado"
print_info "URL: https://github.com/${GITHUB_USER}/${REPO_NAME}.git"

# =============================================================================
# PASO 5: Verificar estructura de carpetas
# =============================================================================

print_step "Paso 5: Verificando estructura de carpetas"

# Crear carpetas necesarias si no existen
for dir in ".github/workflows" "modules" "assets" "scripts"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        print_status "Carpeta $dir creada"
    fi
done

# =============================================================================
# PASO 6: Agregar archivos a Git
# =============================================================================

print_step "Paso 6: Agregando archivos a Git"

# Crear .gitignore si no existe
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/
.venv

# Buildozer
.buildozer/
buildozer/
bin/
*.apk
*.aab
*.keystore

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log

# Temporary files
tmp/
temp/
*.tmp
EOF
    print_status "Archivo .gitignore creado"
fi

# Agregar todos los archivos
git add .
print_status "Archivos agregados al staging area"

# =============================================================================
# PASO 7: Crear commit
# =============================================================================

print_step "Paso 7: Creando commit"

# Verificar si hay cambios para commitear
if git diff --cached --quiet; then
    print_warning "No hay cambios nuevos para commitear"
    print_info "El repositorio ya está actualizado"
else
    git commit -m "Gestión Fábrica v2.0 - Configuración inicial

Características:
- ✅ Modo Landscape (Horizontal)
- ✅ Tema Oscuro Material Design 3
- ✅ Moneda en Guaraníes (PYG)
- ✅ Base de datos SQLite integrada
- ✅ Generación de PDF con Share Intent
- ✅ Compilación automática con GitHub Actions v2.0

Correcciones v2.0:
- Compatibilidad con Ubuntu 24.04
- KivyMD versión corregida (1.2.0)
- Android SDK Build-Tools instalado correctamente
- GitHub Actions actualizados a v4

Workflow: Push → GitHub Actions → APK automática"

    print_status "Commit creado exitosamente"
fi

# =============================================================================
# PASO 8: Push a GitHub
# =============================================================================

print_step "Paso 8: Subiendo código a GitHub"

# Verificar si existe la rama main
if git show-ref --verify --quiet refs/heads/main; then
    BRANCH="main"
elif git show-ref --verify --quiet refs/heads/master; then
    BRANCH="master"
else
    BRANCH="main"
    git checkout -b main 2>/dev/null || true
fi

print_info "Usando rama: $BRANCH"

# Intentar push
if git push -u origin "$BRANCH" 2>&1; then
    print_status "Código subido exitosamente a GitHub"
else
    print_error "Error al hacer push"
    print_info "Intentando solución alternativa..."
    
    # Intentar pull primero
    git pull origin "$BRANCH" --rebase --allow-unrelated-histories 2>/dev/null || true
    
    # Reintentar push
    if git push -u origin "$BRANCH" 2>&1; then
        print_status "Código subido exitosamente"
    else
        print_error "No se pudo subir el código"
        print_info "Verifica que el repositorio exista en GitHub"
        print_info "URL esperada: https://github.com/${GITHUB_USER}/${REPO_NAME}"
        exit 1
    fi
fi

# =============================================================================
# PASO 9: Información final
# =============================================================================

print_step "Resumen de la configuración"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ¡CONFIGURACIÓN COMPLETADA!                      ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

print_info "Información del repositorio:"
echo "  👤 Usuario: $GITHUB_USER"
echo "  📁 Repositorio: $REPO_NAME"
echo "  🌐 URL: https://github.com/$GITHUB_USER/$REPO_NAME"
echo "  📧 Email: $GITHUB_EMAIL"

echo ""
print_info "Enlaces importantes:"
echo "  🔗 Repositorio: https://github.com/$GITHUB_USER/$REPO_NAME"
echo "  🔗 GitHub Actions: https://github.com/$GITHUB_USER/$REPO_NAME/actions"
echo "  🔗 Releases: https://github.com/$GITHUB_USER/$REPO_NAME/releases"

echo ""
print_info "Próximos pasos:"
echo "  1. Ve a: https://github.com/$GITHUB_USER/$REPO_NAME/actions"
echo "  2. Espera 10-20 minutos (primera compilación)"
echo "  3. Descarga la APK desde 'Artifacts' → 'apk-debug-v2.0'"
echo "  4. Instala en tu dispositivo Android"

echo ""
print_info "Para actualizar la app en el futuro:"
echo "  git add ."
echo "  git commit -m 'Descripción de cambios'"
echo "  git push origin $BRANCH"

echo ""
echo -e "${GREEN}✅ ¡Listo! Tu proyecto está configurado para GitHub Actions v2.0${NC}"
echo ""
