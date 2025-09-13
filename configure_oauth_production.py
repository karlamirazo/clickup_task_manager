#!/usr/bin/env python3
"""
Script para configurar OAuth de ClickUp para producción en Railway
"""

import os
import webbrowser
from urllib.parse import urlencode

def print_banner():
    """Mostrar banner del script"""
    print("🚀 CONFIGURADOR DE OAUTH PARA PRODUCCIÓN (RAILWAY)")
    print("=" * 60)
    print()

def get_oauth_credentials():
    """Obtener credenciales de OAuth del usuario"""
    print("📋 INSTRUCCIONES PARA CONFIGURAR OAUTH EN CLICKUP:")
    print("-" * 50)
    print("1. Ve a https://app.clickup.com/settings/apps")
    print("2. Crea una nueva aplicación OAuth")
    print("3. Configura la URL de redirección:")
    print("   https://clickuptaskmanager-production.up.railway.app/api/auth/callback")
    print("4. Selecciona los permisos:")
    print("   ✅ read:user - Leer información del usuario")
    print("   ✅ read:workspace - Leer información del workspace")
    print("   ✅ read:task - Leer tareas")
    print("   ✅ write:task - Crear y modificar tareas")
    print("5. Copia el Client ID y Client Secret")
    print()
    
    # Preguntar si abrir ClickUp
    response = input("¿Abrir ClickUp Apps en el navegador? (s/n): ").lower()
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        try:
            webbrowser.open("https://app.clickup.com/settings/apps")
            print("✅ ClickUp Apps abierto en el navegador")
        except Exception as e:
            print(f"❌ Error abriendo navegador: {e}")
    
    print()
    print("📝 Ingresa las credenciales de ClickUp:")
    
    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()
    
    return client_id, client_secret

def create_railway_env_file(client_id, client_secret):
    """Crear archivo de variables de entorno para Railway"""
    env_content = f"""# Variables de entorno para Railway - OAuth ClickUp
CLICKUP_OAUTH_CLIENT_ID={client_id}
CLICKUP_OAUTH_CLIENT_SECRET={client_secret}
CLICKUP_OAUTH_REDIRECT_URI=https://clickuptaskmanager-production.up.railway.app/api/auth/callback

# Configuración de seguridad
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Configuración de la aplicación
ENVIRONMENT=production
PORT=8000
HOST=0.0.0.0

# Base de datos (Railway proporciona DATABASE_URL automáticamente)
# DATABASE_URL se configura automáticamente en Railway

# ClickUp API (opcional)
CLICKUP_API_TOKEN=pk_156221125_GI1OKEUEW57LFWA8RYWHGIC54TL6XVVZ
CLICKUP_WORKSPACE_ID=9014943317
CLICKUP_SPACE_ID=90143983983
"""
    
    try:
        with open("railway.env", "w", encoding="utf-8") as f:
            f.write(env_content)
        print("✅ Archivo railway.env creado correctamente")
        return True
    except Exception as e:
        print(f"❌ Error creando archivo railway.env: {e}")
        return False

def show_railway_setup_instructions():
    """Mostrar instrucciones para configurar Railway"""
    print("\n🔧 CONFIGURACIÓN EN RAILWAY:")
    print("-" * 40)
    print("1. Ve a tu proyecto en Railway: https://railway.app/dashboard")
    print("2. Selecciona tu proyecto 'clickuptaskmanager'")
    print("3. Ve a la pestaña 'Variables'")
    print("4. Agrega las siguientes variables:")
    print()
    print("   CLICKUP_OAUTH_CLIENT_ID = [tu_client_id]")
    print("   CLICKUP_OAUTH_CLIENT_SECRET = [tu_client_secret]")
    print("   CLICKUP_OAUTH_REDIRECT_URI = https://clickuptaskmanager-production.up.railway.app/api/auth/callback")
    print("   JWT_SECRET_KEY = [una_clave_secreta_super_segura]")
    print()
    print("5. Haz clic en 'Deploy' para aplicar los cambios")
    print()

def test_oauth_url(client_id):
    """Probar URL de OAuth"""
    if not client_id:
        return
    
    redirect_uri = "https://clickuptaskmanager-production.up.railway.app/api/auth/callback"
    
    auth_url = f"https://app.clickup.com/api/v2/oauth/authorize?" + urlencode({
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'read:user read:workspace read:task write:task'
    })
    
    print(f"\n🔗 URL de autorización para producción:")
    print(f"   {auth_url}")
    
    # Preguntar si probar OAuth
    response = input("\n¿Probar OAuth en producción? (s/n): ").lower()
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        try:
            webbrowser.open(auth_url)
            print("✅ URL de autorización abierta en el navegador")
        except Exception as e:
            print(f"❌ Error abriendo navegador: {e}")

def show_deploy_instructions():
    """Mostrar instrucciones de deploy"""
    print("\n🚀 INSTRUCCIONES DE DEPLOY:")
    print("-" * 40)
    print("1. Haz commit de los cambios:")
    print("   git add .")
    print("   git commit -m 'Add OAuth authentication system'")
    print()
    print("2. Haz push a GitHub:")
    print("   git push origin main")
    print()
    print("3. Railway detectará automáticamente los cambios y hará deploy")
    print("4. Ve a https://clickuptaskmanager-production.up.railway.app")
    print("5. Prueba la autenticación OAuth")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Obtener credenciales
    client_id, client_secret = get_oauth_credentials()
    
    if not client_id or not client_secret:
        print("❌ Credenciales no proporcionadas")
        return False
    
    # Crear archivo de configuración para Railway
    if not create_railway_env_file(client_id, client_secret):
        return False
    
    # Mostrar instrucciones de Railway
    show_railway_setup_instructions()
    
    # Probar URL de OAuth
    test_oauth_url(client_id)
    
    # Mostrar instrucciones de deploy
    show_deploy_instructions()
    
    print("✅ ¡Configuración de OAuth para producción completada!")
    print("🎯 Siguiente paso: Configurar variables en Railway y hacer deploy")
    
    return True

if __name__ == "__main__":
    main()
