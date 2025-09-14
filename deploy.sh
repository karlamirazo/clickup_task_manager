#!/bin/bash
# Script de despliegue para Railway

echo "Desplegando ClickUp Project Manager..."

# Verificar que main_simple.py existe
if [ ! -f "main_simple.py" ]; then
    echo "ERROR: main_simple.py no encontrado"
    exit 1
fi

# Verificar que requirements.txt existe
if [ ! -f "requirements.txt" ]; then
    echo "ERROR: requirements.txt no encontrado"
    exit 1
fi

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt

# Ejecutar aplicación
echo "Iniciando aplicacion..."
python main_simple.py
