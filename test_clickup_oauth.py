#!/usr/bin/env python3
"""
Script para probar el flujo OAuth completo de ClickUp
"""

import asyncio
import aiohttp
import webbrowser
from urllib.parse import urlencode, parse_qs
from core.clickup_client import ClickUpClient

class ClickUpOAuth:
    """Cliente OAuth para ClickUp"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = "http://localhost:8000/callback"
        self.auth_url = "https://app.clickup.com/api/v2/oauth/authorize"
        self.token_url = "https://api.clickup.com/api/v2/oauth/token"
    
    def get_authorization_url(self) -> str:
        """Generar URL de autorizacion"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "read:workspace read:space read:task read:user"
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, authorization_code: str) -> dict:
        """Intercambiar codigo de autorizacion por token de acceso"""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": authorization_code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.token_url, data=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Error getting token: {response.status} - {error_text}")

async def test_oauth_flow():
    """Test el flujo OAuth completo"""
    
    print("üîê Iniciando flujo OAuth de ClickUp")
    print("=" * 50)
    
    # Configurar con los valores reales
    client_id = "CXH47UNPORL0IJRX5Q24A6947IHHCN0U"
    client_secret = "FHJEHY9JJI68TY4X50XDLTBZEXFY4N1PSQY7VEPZPIFLBUIMKXZ3545M1BI4ME12"
    
    # Validacion basica
    if not client_id or not client_secret:
        print("‚ùå Client ID o Client Secret no configureds")
        return
    
    oauth_client = ClickUpOAuth(client_id, client_secret)
    
    # Paso 1: Generar URL de autorizacion
    auth_url = oauth_client.get_authorization_url()
    print(f"üîó URL de autorizacion: {auth_url}")
    
    # Paso 2: Abrir navegador para autorizacion
    print("\nüåê Abriendo navegador para autorizacion...")
    webbrowser.open(auth_url)
    
    print("\nüìã Instrucciones:")
    print("1. Autoriza la app en ClickUp")
    print("2. Copia el codigo de autorizacion de la URL de callback")
    print("3. Pegalo aqui cuando te lo pida")
    
    # Paso 3: Get codigo de autorizacion del usuario
    auth_code = input("\nüìù Pega el codigo de autorizacion aqui: ").strip()
    
    if not auth_code:
        print("‚ùå No se proporciono codigo de autorizacion")
        return
    
    try:
        # Paso 4: Intercambiar codigo por token
        print("\nüîÑ Intercambiando codigo por token de acceso...")
        token_data = await oauth_client.exchange_code_for_token(auth_code)
        
        access_token = token_data.get("access_token")
        if access_token:
            print(f"‚úÖ Token de acceso obtenido: {access_token[:20]}...{access_token[-10:]}")
            
            # Paso 5: Test la API con el token OAuth
            print("\nüß™ Probando API con token OAuth...")
            client = ClickUpClient(api_token=access_token)
            
            workspaces = await client.get_workspaces()
            if workspaces:
                print(f"‚úÖ Connection successful! Se encontraron {len(workspaces)} workspace(s):")
                for workspace in workspaces[:3]:
                    print(f"   - {workspace.get('name', 'Sin nombre')} (ID: {workspace.get('id', 'N/A')}")
            else:
                print("‚ö†Ô∏è  No se encontraron workspaces")
                
        else:
            print("‚ùå No se pudo obtener el token de acceso")
            print(f"Respuesta completa: {token_data}")
            
    except Exception as e:
        print(f"‚ùå Error en el flujo OAuth: {e}")

if __name__ == "__main__":
    print("üöÄ Iniciando prueba de OAuth con ClickUp")
    print("=" * 50)
    
    # Execute la prueba
    asyncio.run(test_oauth_flow())
    
    print("\n" + "=" * 50)
    print("üèÅ Prueba completada")
