#!/usr/bin/env python3
"""
Diagnóstico detallado del problema de redirección OAuth
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE REDIRECCIÓN OAUTH")
    print("=" * 60)
    print()

def check_environment():
    """Verificar variables de entorno"""
    print("🌍 Verificando variables de entorno...")
    
    # Cargar variables de entorno
    from dotenv import load_dotenv
    load_dotenv()
    
    client_id = os.getenv('CLICKUP_OAUTH_CLIENT_ID')
    client_secret = os.getenv('CLICKUP_OAUTH_CLIENT_SECRET')
    redirect_uri = os.getenv('CLICKUP_OAUTH_REDIRECT_URI')
    
    print(f"   Client ID: {client_id[:20] if client_id else 'None'}...")
    print(f"   Client Secret: {'Configurado' if client_secret else 'None'}")
    print(f"   Redirect URI: {redirect_uri}")
    
    return client_id, client_secret, redirect_uri

def check_config():
    """Verificar configuración de la aplicación"""
    print("\n⚙️ Verificando configuración de la aplicación...")
    
    try:
        from core.config import settings
        print(f"   Redirect URI (config): {settings.CLICKUP_OAUTH_REDIRECT_URI}")
        print(f"   Client ID (config): {settings.CLICKUP_OAUTH_CLIENT_ID[:20]}...")
        return True
    except Exception as e:
        print(f"   ❌ Error cargando configuración: {e}")
        return False

def test_oauth_url():
    """Probar la URL de OAuth"""
    print("\n🔗 Probando URL de OAuth...")
    
    try:
        from auth.oauth import ClickUpOAuth
        oauth = ClickUpOAuth()
        auth_url = oauth.get_authorization_url()
        print(f"   URL generada: {auth_url[:100]}...")
        
        # Extraer redirect_uri de la URL
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(auth_url)
        params = parse_qs(parsed.query)
        redirect_uri = params.get('redirect_uri', [None])[0]
        print(f"   Redirect URI en URL: {redirect_uri}")
        
        return redirect_uri
    except Exception as e:
        print(f"   ❌ Error generando URL OAuth: {e}")
        return None

def check_callback_endpoint():
    """Verificar que el endpoint de callback existe"""
    print("\n🎯 Verificando endpoint de callback...")
    
    try:
        import requests
        response = requests.get("http://localhost:8000/api/auth/callback?code=test&state=test", allow_redirects=False)
        print(f"   Status del callback: {response.status_code}")
        
        if response.status_code == 307:  # Redirect
            redirect_url = response.headers.get('Location', '')
            print(f"   Redirige a: {redirect_url}")
            return redirect_url
        else:
            print(f"   ❌ Callback no redirige correctamente")
            return None
    except Exception as e:
        print(f"   ❌ Error probando callback: {e}")
        return None

def show_solution():
    """Mostrar solución"""
    print("\n" + "=" * 60)
    print("💡 SOLUCIÓN AL PROBLEMA")
    print("=" * 60)
    print()
    print("El problema es que la URL de redirección en ClickUp no coincide")
    print("con la URL de callback de tu aplicación.")
    print()
    print("🔧 PASOS PARA SOLUCIONAR:")
    print()
    print("1. Ve a https://app.clickup.com/settings/apps")
    print("2. Busca tu aplicación 'ClickUp Project Manager'")
    print("3. Edita la configuración")
    print("4. Cambia la 'Redirect URI' a:")
    print("   http://localhost:8000/api/auth/callback")
    print()
    print("5. Guarda los cambios")
    print("6. Prueba nuevamente el OAuth")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Verificar variables de entorno
    client_id, client_secret, redirect_uri = check_environment()
    
    # Verificar configuración
    config_ok = check_config()
    
    # Probar URL OAuth
    oauth_redirect = test_oauth_url()
    
    # Verificar callback
    callback_redirect = check_callback_endpoint()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 60)
    print(f"✅ Variables de entorno: {'OK' if client_id and client_secret else 'ERROR'}")
    print(f"✅ Configuración: {'OK' if config_ok else 'ERROR'}")
    print(f"✅ URL OAuth: {'OK' if oauth_redirect else 'ERROR'}")
    print(f"✅ Callback: {'OK' if callback_redirect else 'ERROR'}")
    
    if oauth_redirect and callback_redirect:
        print(f"\n🔍 Redirect URI en OAuth: {oauth_redirect}")
        print(f"🔍 Redirect URI en Callback: {callback_redirect}")
        
        if oauth_redirect != callback_redirect:
            print("\n❌ ¡PROBLEMA ENCONTRADO!")
            print("Las URLs de redirección no coinciden.")
            show_solution()
        else:
            print("\n✅ Las URLs coinciden. El problema puede ser otro.")
    else:
        print("\n❌ Hay problemas en la configuración básica.")

if __name__ == "__main__":
    main()

