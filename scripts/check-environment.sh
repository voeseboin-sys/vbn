#!/bin/bash
# =============================================================================
# CHECK-ENVIRONMENT.SH - Script de verificación del entorno
# Repositorio: voeseboin-sys/vbn
#
# Este script verifica que todas las dependencias estén instaladas correctamente
# antes de intentar compilar la aplicación.
#
# USO:
#   ./scripts/check-environment.sh
# =============================================================================

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Contadores
CHECKS_PASSED=0
CHECKS_FAILED=0
WARNINGS=0

# Funciones
print_header() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║     VERIFICACIÓN DEL ENTORNO - Gestión Fábrica v2.0          ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_check() {
    local name="$1"
    local status="$2"
    local message="$3"
    
    if [ "$status" = "OK" ]; then
        echo -e "  ${GREEN}✓${NC} $name"
        [ -n "$message" ] && echo -e "    ${GREEN}$message${NC}"
        ((CHECKS_PASSED++))
    elif [ "$status" = "WARN" ]; then
        echo -e "  ${YELLOW}⚠${NC} $name"
        [ -n "$message" ] && echo -e "    ${YELLOW}$message${NC}"
        ((WARNINGS++))
    else
        echo -e "  ${RED}✗${NC} $name"
        [ -n "$message" ] && echo -e "    ${RED}$message${NC}"
        ((CHECKS_FAILED++))
    fi
}

print_section() {
    echo ""
    echo -e "${BLUE}▶ $1${NC}"
    echo "──────────────────────────────────────────────────────────────"
}

# =============================================================================
# INICIO DE VERIFICACIONES
# =============================================================================

print_header

# =============================================================================
# SECCIÓN 1: Sistema Operativo
# =============================================================================

print_section "Sistema Operativo"

if [ -f /etc/os-release ]; then
    OS_NAME=$(grep ^NAME /etc/os-release | cut -d= -f2 | tr -d '"')
    OS_VERSION=$(grep ^VERSION_ID /etc/os-release | cut -d= -f2 | tr -d '"')
    print_check "Sistema Operativo" "OK" "$OS_NAME $OS_VERSION"
else
    print_check "Sistema Operativo" "WARN" "No se pudo detectar"
fi

# =============================================================================
# SECCIÓN 2: Python
# =============================================================================

print_section "Python"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    print_check "Python instalado" "OK" "$PYTHON_VERSION"
    
    # Verificar versión mínima (3.8)
    PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
    PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        print_check "Versión Python (>=3.8)" "OK" ""
    else
        print_check "Versión Python (>=3.8)" "FAIL" "Se requiere Python 3.8 o superior"
    fi
else
    print_check "Python instalado" "FAIL" "Python3 no encontrado"
fi

if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version | awk '{print $1" "$2}')
    print_check "pip instalado" "OK" "$PIP_VERSION"
else
    print_check "pip instalado" "FAIL" "pip3 no encontrado"
fi

# =============================================================================
# SECCIÓN 3: Java
# =============================================================================

print_section "Java (JDK)"

if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -1)
    print_check "Java instalado" "OK" "$JAVA_VERSION"
    
    # Verificar JAVA_HOME
    if [ -n "$JAVA_HOME" ]; then
        print_check "JAVA_HOME configurado" "OK" "$JAVA_HOME"
    else
        print_check "JAVA_HOME configurado" "WARN" "Variable JAVA_HOME no está configurada"
    fi
else
    print_check "Java instalado" "FAIL" "Java no encontrado. Instala: sudo apt install openjdk-17-jdk"
fi

# =============================================================================
# SECCIÓN 4: Dependencias del Sistema
# =============================================================================

print_section "Dependencias del Sistema"

# Lista de dependencias a verificar
DEPS=(
    "git"
    "zip"
    "unzip"
    "wget"
    "curl"
    "autoconf"
    "libtool"
    "pkg-config"
    "cmake"
)

for dep in "${DEPS[@]}"; do
    if command -v "$dep" &> /dev/null; then
        print_check "$dep" "OK" ""
    else
        print_check "$dep" "FAIL" "Instala: sudo apt install $dep"
    fi
done

# Verificar librerías específicas
print_section "Librerías del Sistema"

if dpkg -l | grep -q "libtinfo6"; then
    print_check "libtinfo6" "OK" ""
elif dpkg -l | grep -q "libtinfo5"; then
    print_check "libtinfo" "WARN" "libtinfo5 instalado, se recomienda libtinfo6 para Ubuntu 24.04"
else
    print_check "libtinfo" "FAIL" "Instala: sudo apt install libtinfo6"
fi

if dpkg -l | grep -q "libncurses"; then
    print_check "libncurses" "OK" ""
else
    print_check "libncurses" "FAIL" "Instala: sudo apt install libncurses5-dev libncursesw5-dev"
fi

if dpkg -l | grep -q "zlib1g"; then
    print_check "zlib1g" "OK" ""
else
    print_check "zlib1g" "FAIL" "Instala: sudo apt install zlib1g-dev"
fi

# =============================================================================
# SECCIÓN 5: Dependencias Python
# =============================================================================

print_section "Dependencias Python (del proyecto)"

if [ -f "requirements.txt" ]; then
    print_check "Archivo requirements.txt" "OK" ""
    
    # Verificar cada dependencia
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Ignorar líneas vacías y comentarios
        [[ -z "$line" || "$line" =~ ^# ]] && continue
        
        # Extraer nombre del paquete (antes del ==)
        pkg=$(echo "$line" | cut -d= -f1)
        version=$(echo "$line" | grep -o '==.*' | tr -d '=')
        
        if python3 -c "import $pkg" 2>/dev/null; then
            installed_version=$(pip3 show "$pkg" 2>/dev/null | grep Version | cut -d: -f2 | tr -d ' ')
            if [ -n "$version" ]; then
                print_check "$pkg" "OK" "Versión instalada: $installed_version (requerida: $version)"
            else
                print_check "$pkg" "OK" "Versión: $installed_version"
            fi
        else
            if [ -n "$version" ]; then
                print_check "$pkg" "FAIL" "No instalado. Ejecuta: pip install $pkg==$version"
            else
                print_check "$pkg" "FAIL" "No instalado. Ejecuta: pip install $pkg"
            fi
        fi
    done < requirements.txt
else
    print_check "Archivo requirements.txt" "FAIL" "No encontrado"
fi

# =============================================================================
# SECCIÓN 6: Buildozer
# =============================================================================

print_section "Buildozer"

if command -v buildozer &> /dev/null; then
    BUILDOZER_VERSION=$(buildozer version 2>&1 | head -1)
    print_check "Buildozer instalado" "OK" "$BUILDOZER_VERSION"
else
    print_check "Buildozer instalado" "FAIL" "No instalado. Ejecuta: pip install buildozer"
fi

# =============================================================================
# SECCIÓN 7: Archivos del Proyecto
# =============================================================================

print_section "Archivos del Proyecto"

REQUIRED_FILES=(
    "main.py"
    "factory.kv"
    "buildozer.spec"
    "requirements.txt"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_check "$file" "OK" ""
    else
        print_check "$file" "FAIL" "Archivo requerido no encontrado"
    fi
done

# Verificar módulos
if [ -d "modules" ]; then
    print_check "Carpeta modules/" "OK" ""
    
    if [ -f "modules/__init__.py" ]; then
        print_check "  modules/__init__.py" "OK" ""
    else
        print_check "  modules/__init__.py" "FAIL" "No encontrado"
    fi
    
    if [ -f "modules/pdf_generator.py" ]; then
        print_check "  modules/pdf_generator.py" "OK" ""
    else
        print_check "  modules/pdf_generator.py" "FAIL" "No encontrado"
    fi
else
    print_check "Carpeta modules/" "FAIL" "No encontrada"
fi

# =============================================================================
# SECCIÓN 8: Git
# =============================================================================

print_section "Git"

if [ -d ".git" ]; then
    print_check "Repositorio Git inicializado" "OK" ""
    
    if git remote get-url origin &> /dev/null; then
        REMOTE_URL=$(git remote get-url origin)
        print_check "Remote configurado" "OK" "$REMOTE_URL"
    else
        print_check "Remote configurado" "WARN" "No hay remote configurado. Ejecuta: ./setup-github.sh"
    fi
    
    # Verificar si hay cambios sin commitear
    if ! git diff --quiet HEAD 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
        print_check "Cambios pendientes" "WARN" "Hay cambios sin commitear"
    else
        print_check "Estado del repositorio" "OK" "Sin cambios pendientes"
    fi
else
    print_check "Repositorio Git" "WARN" "No inicializado. Ejecuta: git init"
fi

# =============================================================================
# RESUMEN
# =============================================================================

echo ""
echo "══════════════════════════════════════════════════════════════"
echo ""

if [ $CHECKS_FAILED -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║     ✅ TODO CORRECTO - Entorno listo para compilar           ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Puedes proceder a:"
    echo "  1. Subir cambios: git push origin main"
    echo "  2. O compilar localmente: buildozer android debug"
    
elif [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║     ⚠️  ADVERTENCIAS - Entorno funcional con observaciones   ║${NC}"
    echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Advertencias: $WARNINGS"
    echo "Revisa las advertencias arriba, pero puedes intentar compilar."
    
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║     ❌ ERRORES - Debes corregir antes de compilar            ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Errores encontrados: $CHECKS_FAILED"
    echo "Advertencias: $WARNINGS"
    echo ""
    echo "Para instalar dependencias faltantes:"
    echo "  sudo apt update"
    echo "  sudo apt install -y build-essential git zip unzip openjdk-17-jdk"
    echo "  pip install -r requirements.txt"
fi

echo ""
echo "Resumen:"
echo "  ✅ Pasaron: $CHECKS_PASSED"
echo "  ⚠️  Advertencias: $WARNINGS"
echo "  ❌ Errores: $CHECKS_FAILED"
echo ""

# Salir con código de error si hay fallos
[ $CHECKS_FAILED -eq 0 ]
