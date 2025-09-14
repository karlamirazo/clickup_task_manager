#!/usr/bin/env python3
"""
Arreglar despliegue en Railway
"""

import os
import json

def fix_railway_deployment():
    """Arreglar despliegue en Railway"""
    print("🛠️  ARREGLANDO DESPLIEGUE EN RAILWAY")
    print("=" * 50)
    
    # 1. Verificar que main_simple.py esté en la raíz
    print("1. Verificando main_simple.py...")
    if os.path.exists('main_simple.py'):
        print("✅ main_simple.py encontrado")
    else:
        print("❌ main_simple.py no encontrado")
        return
    
    # 2. Crear railway.json para usar main_simple.py
    print("2. Creando railway.json...")
    railway_config = {
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "python main_simple.py",
            "healthcheckPath": "/health",
            "healthcheckTimeout": 100,
            "restartPolicyType": "ON_FAILURE",
            "restartPolicyMaxRetries": 10
        }
    }
    
    with open('railway.json', 'w') as f:
        json.dump(railway_config, f, indent=2)
    
    print("✅ railway.json creado")
    
    # 3. Crear Procfile
    print("3. Creando Procfile...")
    with open('Procfile', 'w') as f:
        f.write("web: python main_simple.py")
    
    print("✅ Procfile creado")
    
    # 4. Verificar requirements.txt
    print("4. Verificando requirements.txt...")
    if os.path.exists('requirements.txt'):
        print("✅ requirements.txt encontrado")
        
        # Leer requirements
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        # Verificar dependencias importantes
        required_deps = [
            'fastapi',
            'uvicorn',
            'psycopg2-binary',
            'python-dotenv',
            'aiohttp',
            'sqlalchemy'
        ]
        
        missing_deps = []
        for dep in required_deps:
            if dep not in requirements:
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"⚠️  Dependencias faltantes: {missing_deps}")
        else:
            print("✅ Todas las dependencias están presentes")
    else:
        print("❌ requirements.txt no encontrado")
    
    # 5. Crear .env.production para Railway
    print("5. Creando .env.production...")
    
    production_env = """# Configuración de producción para Railway
DATABASE_URL=postgresql://postgres:password@localhost:5432/clickup_project_manager
CLICKUP_OAUTH_CLIENT_ID=7US6KJX26FOROTI3ZSOZYCAXBCG7W386
CLICKUP_OAUTH_CLIENT_SECRET=H4M3AVO1L6OG7RDH8XMPUK756PB0X2R28E5KTIJBV8PDQNSORKRSAXI7ZGI5MCXC
CLICKUP_OAUTH_REDIRECT_URI=https://clickuptaskmanager-production.up.railway.app/api/auth/callback
JWT_SECRET_KEY=tu_jwt_secret_key_aqui
ALLOWED_ORIGINS=["https://clickuptaskmanager-production.up.railway.app"]
"""
    
    with open('.env.production', 'w') as f:
        f.write(production_env)
    
    print("✅ .env.production creado")
    
    # 6. Crear script de despliegue
    print("6. Creando script de despliegue...")
    
    deploy_script = """#!/bin/bash
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
"""
    
    with open('deploy.sh', 'w') as f:
        f.write(deploy_script)
    
    # Hacer ejecutable
    os.chmod('deploy.sh', 0o755)
    
    print("✅ deploy.sh creado")
    
    print(f"\n🎉 ¡Configuración completada!")
    print(f"   Archivos creados:")
    print(f"   - railway.json")
    print(f"   - Procfile")
    print(f"   - .env.production")
    print(f"   - deploy.sh")

def show_railway_instructions():
    """Mostrar instrucciones para Railway"""
    print(f"\n📋 INSTRUCCIONES PARA RAILWAY:")
    print("=" * 40)
    print("1. Ve a: https://railway.app/dashboard")
    print("2. Busca tu proyecto 'clickuptaskmanager'")
    print("3. Haz clic en el servicio")
    print("4. Ve a la pestaña 'Settings'")
    print("5. En 'Start Command', cambia a: python main_simple.py")
    print("6. En 'Health Check Path', cambia a: /health")
    print("7. Ve a la pestaña 'Variables'")
    print("8. Agrega estas variables de entorno:")
    print("   - CLICKUP_OAUTH_CLIENT_ID=7US6KJX26FOROTI3ZSOZYCAXBCG7W386")
    print("   - CLICKUP_OAUTH_CLIENT_SECRET=H4M3AVO1L6OG7RDH8XMPUK756PB0X2R28E5KTIJBV8PDQNSORKRSAXI7ZGI5MCXC")
    print("   - CLICKUP_OAUTH_REDIRECT_URI=https://clickuptaskmanager-production.up.railway.app/api/auth/callback")
    print("   - JWT_SECRET_KEY=tu_jwt_secret_key_aqui")
    print("   - ALLOWED_ORIGINS=https://clickuptaskmanager-production.up.railway.app")
    print("9. Guarda los cambios")
    print("10. Ve a la pestaña 'Deployments' y haz clic en 'Redeploy'")

def main():
    """Función principal"""
    print("🛠️  ARREGLAR DESPLIEGUE EN RAILWAY")
    print("=" * 60)
    
    # Arreglar despliegue
    fix_railway_deployment()
    
    # Mostrar instrucciones
    show_railway_instructions()
    
    print(f"\n" + "=" * 60)
    print("📋 PRÓXIMOS PASOS:")
    print("1. Sigue las instrucciones de Railway")
    print("2. Redespliega la aplicación")
    print("3. Prueba OAuth una vez que funcione")
    print("4. Actualiza la Redirect URI en ClickUp")

if __name__ == "__main__":
    main()
