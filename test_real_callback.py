#!/usr/bin/env python3
"""
Probar callback real con ClickUp
"""

import requests
import asyncio
import aiohttp
from urllib.parse import urlencode

def test_clickup_token_exchange():
    """Probar intercambio de token con ClickUp"""
    print("🔐 PROBANDO INTERCAMBIO DE TOKEN CON CLICKUP")
    print("=" * 50)
    
    # Configuración OAuth
    client_id = "7US6KJX26FOROTI3ZSOZYCAXBCG7W386"
    client_secret = "H4M3AVO1L6OG7RDH8XMPUK756PB0X2R28E5KTIJBV8PDQNSORKRSAXI7ZGI5MCXC"
    redirect_uri = "http://localhost:8000/api/auth/callback"
    token_url = "https://app.clickup.com/api/v2/oauth/token"
    
    # Datos para el intercambio de token
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': 'test_authorization_code',  # Código de prueba
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    
    print(f"📤 Enviando petición a: {token_url}")
    print(f"📋 Datos: {data}")
    
    try:
        response = requests.post(
            token_url,
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        print(f"📄 Response Text: {response.text[:500]}...")
        
        if response.status_code == 200:
            print("✅ Token exchange exitoso")
            return True
        else:
            print(f"❌ Error en token exchange: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_clickup_user_info():
    """Probar obtención de información de usuario"""
    print("\n👤 PROBANDO INFORMACIÓN DE USUARIO")
    print("=" * 50)
    
    # Usar token de API existente para probar
    api_token = "pk_156221125_GI1OKEUEW57LFWA8RYWHGIC54TL6XVVZ"
    user_url = "https://api.clickup.com/api/v2/user"
    
    headers = {
        'Authorization': api_token
    }
    
    try:
        response = requests.get(user_url, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            print("✅ Información de usuario obtenida")
            return True
        else:
            print(f"❌ Error obteniendo usuario: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_oauth_flow_instructions():
    """Mostrar instrucciones para el flujo OAuth"""
    print("\n📋 INSTRUCCIONES PARA FLUJO OAUTH REAL")
    print("=" * 50)
    print("1. Ve a: http://localhost:8000/api/auth/login")
    print("2. Haz clic en 'Iniciar con ClickUp'")
    print("3. En ClickUp, haz clic en 'Continue on web anyway'")
    print("4. Completa la autorización")
    print("5. ClickUp te redirigirá a: http://localhost:8000/api/auth/callback?code=REAL_CODE&state=REAL_STATE")
    print("6. Tu aplicación procesará el callback y te llevará al dashboard")
    print()
    print("🔧 CONFIGURACIÓN EN CLICKUP:")
    print("   - Redirect URI: http://localhost:8000/api/auth/callback")
    print("   - Permisos: read:user, read:workspace, read:task, write:task")

def main():
    """Función principal"""
    print("🎯 DIAGNÓSTICO DE CALLBACK OAUTH")
    print("=" * 60)
    
    # Probar intercambio de token
    token_ok = test_clickup_token_exchange()
    
    # Probar información de usuario
    user_ok = test_clickup_user_info()
    
    # Mostrar instrucciones
    show_oauth_flow_instructions()
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO")
    print("=" * 60)
    print(f"Token Exchange: {'✅ OK' if token_ok else '❌ ERROR'}")
    print(f"User Info: {'✅ OK' if user_ok else '❌ ERROR'}")
    
    if not token_ok:
        print("\n💡 SOLUCIÓN:")
        print("   El problema es que necesitas un código de autorización REAL de ClickUp")
        print("   Sigue las instrucciones arriba para obtenerlo")

if __name__ == "__main__":
    main()
