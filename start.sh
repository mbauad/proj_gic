#!/bin/bash
set -e

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "Configurando ambiente..."

# Try ensuring pip is available or use system pip
if ! command_exists pip; then
    if command_exists pip3; then
        PIP_CMD=pip3
    elif python3 -m pip --version > /dev/null 2>&1; then
        PIP_CMD="python3 -m pip"
    else
        echo "Error: pip not found."
        exit 1
    fi
else
    PIP_CMD=pip
fi

echo "Usando pip: $PIP_CMD"

# Install Flask if not present
if python3 -c "import flask" >/dev/null 2>&1; then
    echo "Dependências já instaladas."
else
    echo "Instalando dependências..."
    $PIP_CMD install -r requirements.txt || \
    $PIP_CMD install --user -r requirements.txt || \
    $PIP_CMD install --user --break-system-packages -r requirements.txt
fi

echo "Iniciando servidor..."
python3 flask_app/app.py
