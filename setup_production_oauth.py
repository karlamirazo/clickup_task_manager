#!/usr/bin/env python3
"""
Configurar OAuth para producción con Railway
"""

import os
import requests
from core.config import settings

def setup_production_oauth():
    """Configurar OAuth para producción"""
    print("🚀 CONFIGURANDO OAUTH PARA PRODUCCIÓN")
    print("=" * 50)
    
    # Obtener URL de Railway
    railway_url = input("Ingresa la URL de tu app en Railway (ej: https://tu-app.railway.app): ").strip()
    
    if not railway_url:
        print("❌ URL de Railway requerida")
        return
    
    # Asegurar que la URL tenga https
    if not railway_url.startswith('https://'):
        railway_url = f"https://{railway_url}"
    
    # Configurar Redirect URI para producción
    redirect_uri = f"{railway_url}/api/auth/callback"
    
    print(f"\n📊 Configuración:")
    print(f"   Railway URL: {railway_url}")
    print(f"   Redirect URI: {redirect_uri}")
    
    # Actualizar .env para producción
    print(f"\n🔄 Actualizando .env para producción...")
    
    try:
        # Leer .env actual
        with open('.env', 'r') as f:
            env_content = f.read()
        
        # Actualizar Redirect URI
        lines = env_content.split('\n')
        updated_lines = []
        
        for line in lines:
            if line.startswith('CLICKUP_OAUTH_REDIRECT_URI='):
                updated_lines.append(f'CLICKUP_OAUTH_REDIRECT_URI={redirect_uri}')
            else:
                updated_lines.append(line)
        
        # Escribir .env actualizado
        with open('.env', 'w') as f:
            f.write('\n'.join(updated_lines))
        
        print("✅ .env actualizado para producción")
        
    except Exception as e:
        print(f"❌ Error actualizando .env: {e}")
        return
    
    # Crear .env.production
    print(f"\n📝 Creando .env.production...")
    
    production_env = f"""# Configuración de producción para Railway
DATABASE_URL=postgresql://postgres:password@localhost:5432/clickup_project_manager
CLICKUP_OAUTH_CLIENT_ID={settings.CLICKUP_OAUTH_CLIENT_ID}
CLICKUP_OAUTH_CLIENT_SECRET={settings.CLICKUP_OAUTH_CLIENT_SECRET}
CLICKUP_OAUTH_REDIRECT_URI={redirect_uri}
JWT_SECRET_KEY=tu_jwt_secret_key_aqui
ALLOWED_ORIGINS=["{railway_url}"]
"""
    
    with open('.env.production', 'w') as f:
        f.write(production_env)
    
    print("✅ .env.production creado")
    
    # Mostrar instrucciones para ClickUp
    print(f"\n📋 INSTRUCCIONES PARA CLICKUP:")
    print("=" * 40)
    print("1. Ve a: https://app.clickup.com/settings/apps")
    print("2. Busca tu app 'clickuptaskmanager'")
    print("3. Haz clic en 'Edit'")
    print("4. Cambia Redirect URI a:")
    print(f"   {redirect_uri}")
    print("5. Guarda los cambios")
    print()
    
    # Probar configuración
    print(f"🧪 Probando configuración...")
    test_oauth_url = f"{railway_url}/api/auth/clickup"
    
    try:
        response = requests.get(test_oauth_url, timeout=10)
        if response.status_code == 200:
            print("✅ App de Railway funcionando")
        else:
            print(f"⚠️  App de Railway responde con status: {response.status_code}")
    except Exception as e:
        print(f"⚠️  No se pudo conectar a Railway: {e}")
        print("   Asegúrate de que la app esté desplegada")
    
    print(f"\n🎉 ¡Configuración completada!")
    print(f"   URL de producción: {railway_url}")
    print(f"   Redirect URI: {redirect_uri}")
    print(f"   Archivo .env.production creado")

def create_railway_config():
    """Crear configuración para Railway"""
    print(f"\n📝 Creando configuración para Railway...")
    
    # Crear railway.json
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
    
    import json
    with open('railway.json', 'w') as f:
        json.dump(railway_config, f, indent=2)
    
    print("✅ railway.json creado")
    
    # Crear Procfile
    procfile_content = "web: python main_simple.py"
    with open('Procfile', 'w') as f:
        f.write(procfile_content)
    
    print("✅ Procfile creado")

def main():
    """Función principal"""
    print("🚀 CONFIGURACIÓN DE OAUTH PARA PRODUCCIÓN")
    print("=" * 60)
    
    # Configurar OAuth
    setup_production_oauth()
    
    # Crear configuración de Railway
    create_railway_config()
    
    print(f"\n" + "=" * 60)
    print("📋 PRÓXIMOS PASOS:")
    print("1. Actualiza la Redirect URI en ClickUp")
    print("2. Haz commit y push de los cambios")
    print("3. Despliega en Railway")
    print("4. Prueba OAuth en producción")

if __name__ == "__main__":
    main()
