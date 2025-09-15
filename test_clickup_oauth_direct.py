#!/usr/bin/env python3
"""
Probar OAuth de ClickUp directamente
"""

import aiohttp
import asyncio
import json
from core.config import settings

async def test_clickup_oauth_direct():
    """Probar OAuth de ClickUp directamente"""
    print("🧪 PROBANDO OAUTH DE CLICKUP DIRECTAMENTE")
    print("=" * 50)
    
    # Configuración
    client_id = settings.CLICKUP_OAUTH_CLIENT_ID
    client_secret = settings.CLICKUP_OAUTH_CLIENT_SECRET
    redirect_uri = settings.CLICKUP_OAUTH_REDIRECT_URI
    
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {client_secret[:10]}...")
    print(f"Redirect URI: {redirect_uri}")
    
    # Datos para el token exchange
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': 'test_code_12345',  # Código de prueba
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    
    print(f"\n📊 Datos enviados:")
    for key, value in data.items():
        print(f"  {key}: {value}")
    
    # Probar token exchange
    print(f"\n🔄 Probando token exchange...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "https://app.clickup.com/api/v2/oauth/token",
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                print(f"Status: {response.status}")
                print(f"Headers: {dict(response.headers)}")
                
                # Leer respuesta
                response_text = await response.text()
                print(f"\n📄 Respuesta completa:")
                print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
                print(f"Longitud: {len(response_text)} caracteres")
                print(f"Primeros 500 caracteres:")
                print(response_text[:500])
                
                if response.status == 200:
                    try:
                        json_data = await response.json()
                        print(f"\n✅ JSON válido:")
                        print(json.dumps(json_data, indent=2))
                    except Exception as e:
                        print(f"\n❌ Error parseando JSON: {e}")
                else:
                    print(f"\n❌ Error HTTP: {response.status}")
                    
        except Exception as e:
            print(f"❌ Error de conexión: {e}")

async def test_clickup_user_info():
    """Probar obtención de información de usuario"""
    print("\n🧪 PROBANDO OBTENCIÓN DE INFORMACIÓN DE USUARIO")
    print("=" * 50)
    
    # Token de prueba (esto fallará, pero veremos el error)
    test_token = "test_token_12345"
    
    headers = {
        'Authorization': test_token,
        'Content-Type': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                "https://api.clickup.com/api/v2/user",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                print(f"Status: {response.status}")
                print(f"Headers: {dict(response.headers)}")
                
                response_text = await response.text()
                print(f"\n📄 Respuesta:")
                print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
                print(f"Primeros 500 caracteres:")
                print(response_text[:500])
                
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Función principal"""
    print("🔍 DIAGNÓSTICO COMPLETO DE OAUTH CON CLICKUP")
    print("=" * 60)
    
    # Probar token exchange
    await test_clickup_oauth_direct()
    
    # Probar user info
    await test_clickup_user_info()
    
    print("\n" + "=" * 60)
    print("📋 ANÁLISIS:")
    print("1. Si el token exchange falla, el problema está en la configuración de ClickUp")
    print("2. Si devuelve HTML en lugar de JSON, ClickUp está rechazando la solicitud")
    print("3. Verifica que la app en ClickUp tenga los permisos correctos")
    print("4. Verifica que el Redirect URI coincida exactamente")

if __name__ == "__main__":
    asyncio.run(main())

