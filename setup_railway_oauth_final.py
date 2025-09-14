#!/usr/bin/env python3
"""
Configurar OAuth para Railway - URL específica
"""

import os
import requests
from core.config import settings

def setup_railway_oauth_final():
    """Configurar OAuth para Railway con URL específica"""
    print("🚀 CONFIGURANDO OAUTH PARA RAILWAY")
    print("=" * 50)
    
    # URL de Railway
    railway_url = "https://clickuptaskmanager-production.up.railway.app"
    redirect_uri = f"{railway_url}/api/auth/callback"
    
    print(f"📊 Configuración:")
    print(f"   Railway URL: {railway_url}")
    print(f"   Redirect URI: {redirect_uri}")
    
    # Verificar que Railway esté funcionando
    print(f"\n🔍 Verificando Railway...")
    try:
        response = requests.get(f"{railway_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Railway funcionando")
        else:
            print(f"⚠️  Railway responde con status: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Error conectando a Railway: {e}")
        print("   Asegúrate de que la app esté desplegada")
    
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
ALLOWED_ORIGINS=["{railway_url}"]
"""
    
    with open('.env.production', 'w') as f:
        f.write(production_env)
    
    print("✅ .env.production creado")
    
    # Probar OAuth
    print(f"\n🧪 Probando OAuth...")
    oauth_url = f"{railway_url}/api/auth/clickup"
    
    try:
        response = requests.get(oauth_url, timeout=10)
        if response.status_code == 307:
            redirect_url = response.headers.get('Location', '')
            print("✅ OAuth funcionando")
            print(f"📊 Redirect URL: {redirect_url}")
            
            # Verificar parámetros
            if 'client_id=7US6KJX26FOROTI3ZSOZYCAXBCG7W386' in redirect_url:
                print("✅ Client ID correcto")
            else:
                print("❌ Client ID incorrecto")
                
            if f'redirect_uri={redirect_uri.replace(":", "%3A").replace("/", "%2F")}' in redirect_url:
                print("✅ Redirect URI correcto")
            else:
                print("❌ Redirect URI incorrecto")
                
        else:
            print(f"⚠️  OAuth responde con status: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Error probando OAuth: {e}")
    
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
    
    print(f"🎉 ¡Configuración completada!")
    print(f"   URL de producción: {railway_url}")
    print(f"   Redirect URI: {redirect_uri}")
    print(f"   Archivo .env.production creado")
    
    return railway_url, redirect_uri

def test_production_oauth():
    """Probar OAuth en producción"""
    print(f"\n🧪 PROBANDO OAUTH EN PRODUCCIÓN")
    print("=" * 40)
    
    railway_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Probar página de login
    print("1. Probando página de login...")
    try:
        response = requests.get(f"{railway_url}/api/auth/login", timeout=10)
        if response.status_code == 200:
            print("✅ Página de login accesible")
        else:
            print(f"❌ Error en login: {response.status_code}")
    except Exception as e:
        print(f"❌ Error conectando: {e}")
    
    # Probar OAuth
    print("2. Probando OAuth...")
    try:
        response = requests.get(f"{railway_url}/api/auth/clickup", timeout=10, allow_redirects=False)
        if response.status_code == 307:
            redirect_url = response.headers.get('Location', '')
            print("✅ OAuth funcionando")
            print(f"📊 Redirect URL: {redirect_url}")
        else:
            print(f"❌ Error en OAuth: {response.status_code}")
    except Exception as e:
        print(f"❌ Error probando OAuth: {e}")

def main():
    """Función principal"""
    print("🚀 CONFIGURACIÓN FINAL DE OAUTH PARA RAILWAY")
    print("=" * 60)
    
    try:
        # Configurar OAuth
        railway_url, redirect_uri = setup_railway_oauth_final()
        
        # Probar OAuth
        test_production_oauth()
        
        print(f"\n" + "=" * 60)
        print("📋 PRÓXIMOS PASOS:")
        print("1. Actualiza la Redirect URI en ClickUp")
        print("2. Prueba OAuth en producción")
        print("3. Si funciona, haz commit y push de .env.production")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
