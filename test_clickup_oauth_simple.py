#!/usr/bin/env python3
"""
Script simplificado para probar OAuth de ClickUp
"""

import asyncio
import aiohttp
import webbrowser
from urllib.parse import urlencode

async def test_clickup_oauth():
    """Test OAuth de ClickUp con URLs corregidas"""
    
    print("ğŸ”� Probando OAuth de ClickUp")
    print("=" * 50)
    
    # Credenciales
    client_id = "CXH47UNPORL0IJRX5Q24A6947IHHCN0U"
    client_secret = "FHJEHY9JJI68TY4X50XDLTBZEXFY4N1PSQY7VEPZPIFLBUIMKXZ3545M1BI4ME12"
    redirect_uri = "http://localhost:8000/callback"
    
    # URL de autorizacion corregida
    auth_url = "https://app.clickup.com/oauth/authorize"
    
    # Parametros de autorizacion
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "read:workspace read:space read:task read:user"
    }
    
    # Construir URL completa
    full_auth_url = f"{auth_url}?{urlencode(params)}"
    
    print(f"ğŸ”— URL de autorizacion: {full_auth_url}")
    print("\nğŸŒ� Abriendo navegador...")
    
    # Abrir navegador
    webbrowser.open(full_auth_url)
    
    print("\nğŸ“‹ Instrucciones:")
    print("1. Si la pagina se abre correctamente, autoriza la app")
    print("2. Copia el codigo de la URL de callback")
    print("3. Si hay error, dime exactamente que mensaje aparece")
    
    # Esperar input del usuario
    auth_code = input("\nğŸ“� Pega el codigo de autorizacion o describe el error: ").strip()
    
    if not auth_code:
        print("â�Œ No se proporciono informacion")
        return
    
    # Si es un codigo, intentar intercambiarlo
    if auth_code.startswith("http") or len(auth_code) > 20:
        print("ğŸ“� Parece que pegaste una URL. Necesito solo el codigo de autorizacion.")
        return
    
    try:
        print(f"\nğŸ”„ Intercambiando codigo: {auth_code[:10]}...")
        
        # URL para intercambiar codigo por token
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
                print(f"ğŸ“¡ Respuesta del servidor: {response.status}")
                
                if response.status == 200:
                    token_data = await response.json()
                    access_token = token_data.get("access_token")
                    
                    if access_token:
                        print(f"âœ… Token obtenido: {access_token[:20]}...{access_token[-10:]}")
                        print("ğŸ�‰ Â¡OAuth funciono correctamente!")
                    else:
                        print("â�Œ No se encontro access_token en la respuesta")
                        print(f"Respuesta: {token_data}")
                else:
                    error_text = await response.text()
                    print(f"â�Œ Error {response.status}: {error_text}")
                    
    except Exception as e:
        print(f"â�Œ Error: {e}")

if __name__ == "__main__":
    print("ğŸš€ Iniciando prueba de OAuth simplificada")
    asyncio.run(test_clickup_oauth())
    print("\nğŸ�� Prueba completada")
