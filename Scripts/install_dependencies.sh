#!/bin/bash

# Script de Instalación de Dependencias - DocuSeal
# Compatible con Linux (Ubuntu 20.04+, Debian 10+)

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================"
echo -e "  DocuSeal - Instalador de Dependencias"
echo -e "========================================${NC}"
echo ""

# Obtener el directorio raíz del proyecto
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}Directorio del proyecto: $PROJECT_ROOT${NC}"
echo ""

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar Python
echo -e "${GREEN}[1/4] Verificando Python...${NC}"
if ! command_exists python3; then
    echo -e "${RED}ERROR: Python3 no está instalado${NC}"
    echo -e "${YELLOW}Por favor, instala Python 3.8 o superior:${NC}"
    echo -e "${GRAY}  sudo apt update${NC}"
    echo -e "${GRAY}  sudo apt install python3 python3-pip python3-venv${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ Python encontrado: $PYTHON_VERSION${NC}"
echo ""

# Verificar Node.js
echo -e "${GREEN}[2/4] Verificando Node.js...${NC}"
if ! command_exists node; then
    echo -e "${RED}ERROR: Node.js no está instalado${NC}"
    echo -e "${YELLOW}Por favor, instala Node.js 16.x o superior:${NC}"
    echo -e "${GRAY}  curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -${NC}"
    echo -e "${GRAY}  sudo apt install -y nodejs${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js encontrado: $NODE_VERSION${NC}"
echo ""

# Instalar dependencias del Backend (Python)
echo -e "${GREEN}[3/4] Instalando dependencias del Backend (Python)...${NC}"
echo -e "${GRAY}----------------------------------------${NC}"

BACKEND_PATH="$PROJECT_ROOT/backend/app"
cd "$BACKEND_PATH" || exit 1

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creando entorno virtual de Python...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: No se pudo crear el entorno virtual${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Entorno virtual creado${NC}"
else
    echo -e "${GREEN}✓ Entorno virtual ya existe${NC}"
fi

# Activar entorno virtual e instalar dependencias
echo -e "${YELLOW}Instalando paquetes de Python...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Falló la instalación de dependencias de Python${NC}"
    deactivate
    exit 1
fi

echo -e "${GREEN}✓ Dependencias de Python instaladas correctamente${NC}"
deactivate
echo ""

# Instalar dependencias del Frontend (Node.js)
echo -e "${GREEN}[4/4] Instalando dependencias del Frontend (Node.js)...${NC}"
echo -e "${GRAY}----------------------------------------${NC}"

FRONTEND_PATH="$PROJECT_ROOT/Frontend/react-app"
cd "$FRONTEND_PATH" || exit 1

echo -e "${YELLOW}Instalando paquetes de Node.js (esto puede tardar varios minutos)...${NC}"
npm install

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Falló la instalación de dependencias de Node.js${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Dependencias de Node.js instaladas correctamente${NC}"
echo ""

# Regresar al directorio raíz
cd "$PROJECT_ROOT" || exit 1

# Resumen final
echo -e "${CYAN}========================================"
echo -e "  ¡Instalación Completada!"
echo -e "========================================${NC}"
echo ""
echo -e "${GREEN}Todas las dependencias se han instalado correctamente.${NC}"
echo ""
echo -e "${YELLOW}Próximos pasos:${NC}"
echo -e "${NC}1. Configurar la base de datos PostgreSQL"
echo -e "2. Crear el archivo .env en backend/app/DB/"
echo -e "3. Ejecutar backend: cd backend/app && source venv/bin/activate && python -m uvicorn main:app --host 0.0.0.0 --port 8000"
echo ""
echo -e "${GRAY}Para más información, consulta el archivo README.md${NC}"
echo ""
