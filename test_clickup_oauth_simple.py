#!/usr/bin/env python3
"""
Script simplificado para probar OAuth de ClickUp
"""

import asyncio
import aiohttp
import webbrowser
from urllib.parse import urlencode

async def test_clickup_oauth():
    """Probar OAuth de ClickUp con URLs corregidas"""
    
    print("🔐 Probando OAuth de ClickUp")
    print("=" * 50)
    
    # Credenciales
    client_id = "CXH47UNPORL0IJRX5Q24A6947IHHCN0U"
    client_secret = "FHJEHY9JJI68TY4X50XDLTBZEXFY4N1PSQY7VEPZPIFLBUIMKXZ3545M1BI4ME12"
    redirect_uri = "http://localhost:8000/callback"
    
    # URL de autorización corregida
    auth_url = "https://app.clickup.com/oauth/authorize"
    
    # Parámetros de autorización
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "read:workspace read:space read:task read:user"
    }
    
    # Construir URL completa
    full_auth_url = f"{auth_url}?{urlencode(params)}"
    
    print(f"🔗 URL de autorización: {full_auth_url}")
    print("\n🌐 Abriendo navegador...")
    
    # Abrir navegador
    webbrowser.open(full_auth_url)
    
    print("\n📋 Instrucciones:")
    print("1. Si la página se abre correctamente, autoriza la app")
    print("2. Copia el código de la URL de callback")
    print("3. Si hay error, dime exactamente qué mensaje aparece")
    
    # Esperar input del usuario
    auth_code = input("\n📝 Pega el código de autorización o describe el error: ").strip()
    
    if not auth_code:
        print("❌ No se proporcionó información")
        return
    
    # Si es un código, intentar intercambiarlo
    if auth_code.startswith("http") or len(auth_code) > 20:
        print("📝 Parece que pegaste una URL. Necesito solo el código de autorización.")
        return
    
    try:
        print(f"\n🔄 Intercambiando código: {auth_code[:10]}...")
        
        # URL para intercambiar código por token
        token_url = "https://api.clickup.com/api/v2/oauth/token"
        
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": auth_code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=data) as response:
                print(f"📡 Respuesta del servidor: {response.status}")
                
                if response.status == 200:
                    token_data = await response.json()
                    access_token = token_data.get("access_token")
                    
                    if access_token:
                        print(f"✅ Token obtenido: {access_token[:20]}...{access_token[-10:]}")
                        print("🎉 ¡OAuth funcionó correctamente!")
                    else:
                        print("❌ No se encontró access_token en la respuesta")
                        print(f"Respuesta: {token_data}")
                else:
                    error_text = await response.text()
                    print(f"❌ Error {response.status}: {error_text}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando prueba de OAuth simplificada")
    asyncio.run(test_clickup_oauth())
    print("\n🏁 Prueba completada")
