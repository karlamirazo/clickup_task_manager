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
        """Generar URL de autorización"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "read:workspace read:space read:task read:user"
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, authorization_code: str) -> dict:
        """Intercambiar código de autorización por token de acceso"""
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
                    raise Exception(f"Error obteniendo token: {response.status} - {error_text}")

async def test_oauth_flow():
    """Probar el flujo OAuth completo"""
    
    print("🔐 Iniciando flujo OAuth de ClickUp")
    print("=" * 50)
    
    # Configurar con los valores reales
    client_id = "CXH47UNPORL0IJRX5Q24A6947IHHCN0U"
    client_secret = "FHJEHY9JJI68TY4X50XDLTBZEXFY4N1PSQY7VEPZPIFLBUIMKXZ3545M1BI4ME12"
    
    # Validación básica
    if not client_id or not client_secret:
        print("❌ Client ID o Client Secret no configurados")
        return
    
    oauth_client = ClickUpOAuth(client_id, client_secret)
    
    # Paso 1: Generar URL de autorización
    auth_url = oauth_client.get_authorization_url()
    print(f"🔗 URL de autorización: {auth_url}")
    
    # Paso 2: Abrir navegador para autorización
    print("\n🌐 Abriendo navegador para autorización...")
    webbrowser.open(auth_url)
    
    print("\n📋 Instrucciones:")
    print("1. Autoriza la app en ClickUp")
    print("2. Copia el código de autorización de la URL de callback")
    print("3. Pégalo aquí cuando te lo pida")
    
    # Paso 3: Obtener código de autorización del usuario
    auth_code = input("\n📝 Pega el código de autorización aquí: ").strip()
    
    if not auth_code:
        print("❌ No se proporcionó código de autorización")
        return
    
    try:
        # Paso 4: Intercambiar código por token
        print("\n🔄 Intercambiando código por token de acceso...")
        token_data = await oauth_client.exchange_code_for_token(auth_code)
        
        access_token = token_data.get("access_token")
        if access_token:
            print(f"✅ Token de acceso obtenido: {access_token[:20]}...{access_token[-10:]}")
            
            # Paso 5: Probar la API con el token OAuth
            print("\n🧪 Probando API con token OAuth...")
            client = ClickUpClient(api_token=access_token)
            
            workspaces = await client.get_workspaces()
            if workspaces:
                print(f"✅ Conexión exitosa! Se encontraron {len(workspaces)} workspace(s):")
                for workspace in workspaces[:3]:
                    print(f"   - {workspace.get('name', 'Sin nombre')} (ID: {workspace.get('id', 'N/A')}")
            else:
                print("⚠️  No se encontraron workspaces")
                
        else:
            print("❌ No se pudo obtener el token de acceso")
            print(f"Respuesta completa: {token_data}")
            
    except Exception as e:
        print(f"❌ Error en el flujo OAuth: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando prueba de OAuth con ClickUp")
    print("=" * 50)
    
    # Ejecutar la prueba
    asyncio.run(test_oauth_flow())
    
    print("\n" + "=" * 50)
    print("🏁 Prueba completada")
