#!/usr/bin/env python3
"""
Configurar OAuth para Railway de forma automática
"""

import os
import requests
from core.config import settings

def configure_railway_oauth():
    """Configurar OAuth para Railway"""
    print("🚀 CONFIGURANDO OAUTH PARA RAILWAY")
    print("=" * 50)
    
    # URLs comunes de Railway
    railway_urls = [
        "https://clickup-task-manager-production.up.railway.app",
        "https://clickup-project-manager-production.up.railway.app",
        "https://clickup-task-manager.up.railway.app",
        "https://clickup-project-manager.up.railway.app"
    ]
    
    print("🔍 Probando URLs comunes de Railway...")
    
    working_url = None
    for url in railway_urls:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                working_url = url
                print(f"✅ Encontrada: {url}")
                break
            else:
                print(f"⚠️  {url} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {url} - Error: {e}")
    
    if not working_url:
        print("\n❌ No se encontró ninguna URL de Railway funcionando")
        print("📝 Ingresa manualmente tu URL de Railway:")
        working_url = input("URL de Railway: ").strip()
        
        if not working_url:
            print("❌ URL requerida")
            return
        
        if not working_url.startswith('https://'):
            working_url = f"https://{working_url}"
    
    # Configurar Redirect URI
    redirect_uri = f"{working_url}/api/auth/callback"
    
    print(f"\n📊 Configuración:")
    print(f"   Railway URL: {working_url}")
    print(f"   Redirect URI: {redirect_uri}")
    
    # Actualizar .env
    print(f"\n🔄 Actualizando .env...")
    
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
        
        lines = env_content.split('\n')
        updated_lines = []
        
        for line in lines:
            if line.startswith('CLICKUP_OAUTH_REDIRECT_URI='):
                updated_lines.append(f'CLICKUP_OAUTH_REDIRECT_URI={redirect_uri}')
            else:
                updated_lines.append(line)
        
        with open('.env', 'w') as f:
            f.write('\n'.join(updated_lines))
        
        print("✅ .env actualizado")
        
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
ALLOWED_ORIGINS=["{working_url}"]
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
    
    # Probar OAuth
    print(f"🧪 Probando OAuth...")
    oauth_url = f"{working_url}/api/auth/clickup"
    
    try:
        response = requests.get(oauth_url, timeout=10)
        if response.status_code == 307:
            redirect_url = response.headers.get('Location', '')
            print("✅ OAuth funcionando")
            print(f"📊 Redirect URL: {redirect_url}")
        else:
            print(f"⚠️  OAuth responde con status: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Error probando OAuth: {e}")
    
    print(f"\n🎉 ¡Configuración completada!")
    print(f"   URL de producción: {working_url}")
    print(f"   Redirect URI: {redirect_uri}")
    print(f"   Archivo .env.production creado")
    
    return working_url, redirect_uri

def main():
    """Función principal"""
    print("🚀 CONFIGURACIÓN AUTOMÁTICA DE OAUTH PARA RAILWAY")
    print("=" * 60)
    
    try:
        working_url, redirect_uri = configure_railway_oauth()
        
        print(f"\n" + "=" * 60)
        print("📋 PRÓXIMOS PASOS:")
        print("1. Actualiza la Redirect URI en ClickUp")
        print("2. Prueba OAuth en producción")
        print("3. Si funciona, haz commit y push de .env.production")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
