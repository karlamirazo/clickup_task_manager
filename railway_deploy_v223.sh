#!/bin/bash
# Script para deploy Evolution API v2.2.3

echo "🚀 DEPLOYANDO EVOLUTION API v2.2.3"
echo "=================================="

# Verificar Railway CLI
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI no instalado. Instalar desde: https://railway.app/cli"
    exit 1
fi

# Login a Railway
echo "📝 Conectando a Railway..."
railway login

# Crear directorio temporal
echo "📁 Creando directorio temporal..."
mkdir -p temp-evolution-v223
cd temp-evolution-v223

# Clonar repositorio en versión específica
echo "📥 Clonando Evolution API v2.2.3..."
git clone -b v2.2.3 --depth 1 https://github.com/EvolutionAPI/evolution-api.git .

# Crear proyecto en Railway
echo "🏗️  Creando proyecto en Railway..."
railway project create evolution-v223

# Configurar variables de entorno
echo "⚙️  Configurando variables..."
railway variables set AUTHENTICATION_API_KEY=clickup-evolution-v223
railway variables set DATABASE_PROVIDER=postgresql
railway variables set CONFIG_SESSION_PHONE_CLIENT="Evolution API"
railway variables set CONFIG_SESSION_PHONE_NAME=Chrome
railway variables set QRCODE_LIMIT=30
railway variables set LOG_LEVEL=ERROR
railway variables set WEBHOOK_ENABLED=false

# Agregar PostgreSQL
echo "🗄️  Agregando PostgreSQL..."
railway add postgresql

# Deploy
echo "🚀 Deployando..."
railway up

echo "✅ Deploy completado!"
echo "📱 Manager estará disponible en la URL que Railway te proporcione"
echo "🔑 API Key: clickup-evolution-v223"
