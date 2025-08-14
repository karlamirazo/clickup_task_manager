# Script para configurar PostgreSQL con Docker
Write-Host "🐳 Configurando PostgreSQL con Docker..." -ForegroundColor Green

# Verificar si Docker está instalado
try {
    docker --version | Out-Null
    Write-Host "✅ Docker está instalado" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker no está instalado" -ForegroundColor Red
    Write-Host "💡 Instala Docker Desktop desde: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    exit 1
}

# Verificar si Docker está ejecutándose
try {
    docker info | Out-Null
    Write-Host "✅ Docker está ejecutándose" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker no está ejecutándose" -ForegroundColor Red
    Write-Host "💡 Inicia Docker Desktop" -ForegroundColor Yellow
    exit 1
}

# Detener contenedor existente si existe
Write-Host "🔄 Deteniendo contenedor existente..." -ForegroundColor Yellow
docker stop clickup-postgres 2>$null
docker rm clickup-postgres 2>$null

# Crear red si no existe
Write-Host "🌐 Creando red Docker..." -ForegroundColor Yellow
docker network create clickup-network 2>$null

# Ejecutar PostgreSQL en Docker
Write-Host "🚀 Iniciando PostgreSQL en Docker..." -ForegroundColor Green
docker run -d `
    --name clickup-postgres `
    --network clickup-network `
    -e POSTGRES_DB=clickup_manager `
    -e POSTGRES_USER=postgres `
    -e POSTGRES_PASSWORD=postgres `
    -p 5432:5432 `
    -v clickup_postgres_data:/var/lib/postgresql/data `
    postgres:15-alpine

# Esperar a que PostgreSQL esté listo
Write-Host "⏳ Esperando a que PostgreSQL esté listo..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Verificar que el contenedor esté ejecutándose
$containerStatus = docker ps --filter "name=clickup-postgres" --format "table {{.Status}}"
if ($containerStatus -like "*Up*") {
    Write-Host "✅ PostgreSQL está ejecutándose en Docker" -ForegroundColor Green
    Write-Host "📊 Información del contenedor:" -ForegroundColor Cyan
    docker ps --filter "name=clickup-postgres"
    
    Write-Host "`n🔗 Conexión:" -ForegroundColor Cyan
    Write-Host "   Host: localhost" -ForegroundColor White
    Write-Host "   Puerto: 5432" -ForegroundColor White
    Write-Host "   Usuario: postgres" -ForegroundColor White
    Write-Host "   Contraseña: postgres" -ForegroundColor White
    Write-Host "   Base de datos: clickup_manager" -ForegroundColor White
    
    Write-Host "`n📋 Próximos pasos:" -ForegroundColor Cyan
    Write-Host "1. Ejecuta: python migrate_postgres_async.py" -ForegroundColor White
    Write-Host "2. Verifica la migración" -ForegroundColor White
    Write-Host "3. Reinicia el servidor: python main.py" -ForegroundColor White
} else {
    Write-Host "❌ Error iniciando PostgreSQL en Docker" -ForegroundColor Red
    Write-Host "📋 Logs del contenedor:" -ForegroundColor Yellow
    docker logs clickup-postgres
}


