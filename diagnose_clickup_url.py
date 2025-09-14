#!/usr/bin/env python3
"""
Diagnóstico específico de la URL de ClickUp
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE URL DE CLICKUP")
    print("=" * 60)
    print()

def check_oauth_config():
    """Verificar configuración OAuth"""
    print("⚙️ Verificando configuración OAuth...")
    
    try:
        from core.config import settings
        
        print(f"   Client ID: {settings.CLICKUP_OAUTH_CLIENT_ID[:20]}...")
        print(f"   Client Secret: {'Configurado' if settings.CLICKUP_OAUTH_CLIENT_SECRET else 'No configurado'}")
        print(f"   Redirect URI: {settings.CLICKUP_OAUTH_REDIRECT_URI}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def generate_oauth_url():
    """Generar URL de OAuth"""
    print("\n🔗 Generando URL de OAuth...")
    
    try:
        from auth.oauth import clickup_oauth
        
        # Generar URL de autorización
        auth_url = clickup_oauth.get_authorization_url()
        print(f"   URL generada: {auth_url}")
        
        # Verificar componentes de la URL
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(auth_url)
        params = parse_qs(parsed.query)
        
        print(f"   Host: {parsed.hostname}")
        print(f"   Path: {parsed.path}")
        print(f"   Client ID: {params.get('client_id', [None])[0]}")
        print(f"   Redirect URI: {params.get('redirect_uri', [None])[0]}")
        print(f"   Response Type: {params.get('response_type', [None])[0]}")
        print(f"   State: {params.get('state', [None])[0]}")
        print(f"   Scope: {params.get('scope', [None])[0]}")
        
        return auth_url, params
        
    except Exception as e:
        print(f"   ❌ Error generando URL: {e}")
        return None, None

def test_clickup_url(auth_url):
    """Probar la URL de ClickUp"""
    print("\n🌐 Probando URL de ClickUp...")
    
    try:
        import requests
        
        # Hacer request a la URL de ClickUp
        response = requests.get(auth_url, allow_redirects=False)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ URL de ClickUp accesible")
            return True
        elif response.status_code == 302:
            print("   ✅ URL de ClickUp redirige (normal)")
            redirect_url = response.headers.get('Location', '')
            print(f"   Redirige a: {redirect_url[:100]}...")
            return True
        else:
            print(f"   ❌ Error en URL de ClickUp: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Error probando URL: {e}")
        return False

def show_clickup_config_instructions():
    """Mostrar instrucciones para configurar ClickUp"""
    print("\n" + "=" * 60)
    print("🔧 CONFIGURACIÓN REQUERIDA EN CLICKUP")
    print("=" * 60)
    print()
    print("El problema es que la aplicación OAuth en ClickUp no está")
    print("configurada correctamente o no existe.")
    print()
    print("📋 PASOS PARA SOLUCIONAR:")
    print()
    print("1. Ve a: https://app.clickup.com/settings/apps")
    print("2. Busca tu aplicación 'ClickUp Project Manager'")
    print("   - Si no existe, crea una nueva")
    print("   - Si existe, edítala")
    print()
    print("3. Configura los siguientes valores:")
    print("   - App Name: ClickUp Project Manager")
    print("   - Description: Gestión de proyectos con ClickUp")
    print("   - Redirect URI: http://localhost:8000/api/auth/callback")
    print()
    print("4. Selecciona los permisos:")
    print("   ✅ read:user")
    print("   ✅ read:workspace")
    print("   ✅ read:task")
    print("   ✅ write:task")
    print()
    print("5. Guarda los cambios")
    print()
    print("⚠️  IMPORTANTE:")
    print("   - La Redirect URI debe ser EXACTAMENTE:")
    print("     http://localhost:8000/api/auth/callback")
    print("   - No debe tener '/' al final")
    print("   - Debe usar 'http' no 'https'")
    print("   - Debe usar 'localhost' no '127.0.0.1'")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Verificar configuración
    config_ok = check_oauth_config()
    
    if not config_ok:
        print("\n❌ Error en la configuración OAuth")
        return
    
    # Generar URL
    auth_url, params = generate_oauth_url()
    
    if not auth_url:
        print("\n❌ No se pudo generar la URL de OAuth")
        return
    
    # Probar URL
    url_ok = test_clickup_url(auth_url)
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO DEL DIAGNÓSTICO")
    print("=" * 60)
    print(f"✅ Configuración: {'OK' if config_ok else 'ERROR'}")
    print(f"✅ URL generada: {'OK' if auth_url else 'ERROR'}")
    print(f"✅ URL ClickUp: {'OK' if url_ok else 'ERROR'}")
    
    if not url_ok:
        print("\n❌ La URL de ClickUp no es accesible")
        print("💡 Esto indica un problema con la configuración en ClickUp")
        show_clickup_config_instructions()
    else:
        print("\n✅ La URL de ClickUp es accesible")
        print("💡 El problema puede estar en otra parte")

if __name__ == "__main__":
    main()
