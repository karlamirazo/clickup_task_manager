#!/usr/bin/env python3
"""
Script mejorado para probar OAuth de ClickUp con múltiples opciones
"""

import asyncio
import aiohttp
import webbrowser
import time
from urllib.parse import urlencode, parse_qs, urlparse

class ClickUpOAuthTester:
    """Clase para probar OAuth de ClickUp con múltiples métodos"""
    
    def __init__(self):
        self.client_id = "CXH47UNPORL0IJRX5Q24A6947IHHCN0U"
        self.client_secret = "FHJEHY9JJI68TY4X50XDLTBZEXFY4N1PSQY7VEPZPIFLBUIMKXZ3545M1BI4ME12"
        self.redirect_uri = "http://localhost:8000/callback"
        
    async def test_method_1_standard_oauth(self):
        """Método 1: OAuth estándar de ClickUp"""
        print("\n🔐 MÉTODO 1: OAuth Estándar de ClickUp")
        print("=" * 50)
        
        # URL de autorización estándar
        auth_url = "https://app.clickup.com/oauth/authorize"
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "read:workspace read:space read:task read:user"
        }
        
        full_auth_url = f"{auth_url}?{urlencode(params)}"
        print(f"🔗 URL: {full_auth_url}")
        
        print("\n🌐 Abriendo navegador...")
        webbrowser.open(full_auth_url)
        
        return await self._get_auth_code_and_exchange("Método 1")
    
    async def test_method_2_api_oauth(self):
        """Método 2: OAuth usando API endpoint"""
        print("\n🔐 MÉTODO 2: OAuth via API Endpoint")
        print("=" * 50)
        
        # URL de autorización via API
        auth_url = "https://api.clickup.com/api/v2/oauth/authorize"
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "read:workspace read:space read:task read:user"
        }
        
        full_auth_url = f"{auth_url}?{urlencode(params)}"
        print(f"🔗 URL: {full_auth_url}")
        
        print("\n🌐 Abriendo navegador...")
        webbrowser.open(full_auth_url)
        
        return await self._get_auth_code_and_exchange("Método 2")
    
    async def test_method_3_direct_token(self):
        """Método 3: Intentar usar token directo"""
        print("\n🔐 MÉTODO 3: Token Directo (Bypass OAuth)")
        print("=" * 50)
        
        # Intentar usar el token que ya tienes
        test_tokens = [
            "pk_156221125_F8RNYI1M5XOASGLBUF9SFJW16QVNV2P3",
            "pk_156221125_CL5ODAXPK51HAWWENZWSNANAGWQLRQ8L",
            "pk_156221125_EAW6ZP8QWASDNZKT5K0HS8RNL737HIXZ"
        ]
        
        for i, token in enumerate(test_tokens, 1):
            print(f"\n🔄 Probando token {i}: {token[:20]}...{token[-10:]}")
            
            try:
                # Probar con endpoint simple
                test_url = "https://api.clickup.com/api/v2/user"
                headers = {"Authorization": f"Bearer {token}"}
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(test_url, headers=headers) as response:
                        print(f"📡 Status: {response.status}")
                        
                        if response.status == 200:
                            user_data = await response.json()
                            print(f"✅ ¡Funcionó! Usuario: {user_data.get('user', {}).get('username', 'N/A')}")
                            return {"success": True, "token": token, "method": "Direct Token"}
                        else:
                            error_text = await response.text()
                            print(f"❌ Error: {error_text}")
                            
            except Exception as e:
                print(f"❌ Excepción: {e}")
        
        print("❌ Ningún token directo funcionó")
        return {"success": False, "method": "Direct Token"}
    
    async def _get_auth_code_and_exchange(self, method_name):
        """Obtener código de autorización e intercambiarlo por token"""
        print(f"\n📋 Instrucciones para {method_name}:")
        print("1. Si la página se abre correctamente, autoriza la app")
        print("2. Copia el código de la URL de callback")
        print("3. Si hay error, describe exactamente qué aparece")
        
        auth_code = input(f"\n📝 Pega el código de autorización para {method_name}: ").strip()
        
        if not auth_code:
            print("❌ No se proporcionó código")
            return {"success": False, "method": method_name}
        
        # Si es una URL, extraer el código
        if auth_code.startswith("http"):
            parsed = urlparse(auth_code)
            query_params = parse_qs(parsed.query)
            auth_code = query_params.get("code", [None])[0]
            
            if not auth_code:
                print("❌ No se pudo extraer código de la URL")
                return {"success": False, "method": method_name}
        
        try:
            print(f"\n🔄 Intercambiando código: {auth_code[:10]}...")
            
            # Intentar múltiples URLs de token
            token_urls = [
                "https://api.clickup.com/api/v2/oauth/token",
                "https://app.clickup.com/oauth/token",
                "https://api.clickup.com/oauth/token"
            ]
            
            for token_url in token_urls:
                print(f"🔄 Probando: {token_url}")
                
                data = {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": auth_code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri
                }
                
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(token_url, data=data) as response:
                            print(f"📡 Status: {response.status}")
                            
                            if response.status == 200:
                                token_data = await response.json()
                                access_token = token_data.get("access_token")
                                
                                if access_token:
                                    print(f"✅ Token obtenido: {access_token[:20]}...{access_token[-10:]}")
                                    print("🎉 ¡OAuth funcionó correctamente!")
                                    return {
                                        "success": True, 
                                        "token": access_token, 
                                        "method": method_name,
                                        "token_url": token_url
                                    }
                                else:
                                    print("❌ No se encontró access_token")
                                    print(f"Respuesta: {token_data}")
                            else:
                                error_text = await response.text()
                                print(f"❌ Error {response.status}: {error_text}")
                                
                except Exception as e:
                    print(f"❌ Error con {token_url}: {e}")
                    continue
            
            print("❌ Ninguna URL de token funcionó")
            return {"success": False, "method": method_name}
            
        except Exception as e:
            print(f"❌ Error general: {e}")
            return {"success": False, "method": method_name}
    
    async def run_all_tests(self):
        """Ejecutar todos los métodos de prueba"""
        print("🚀 INICIANDO PRUEBAS COMPLETAS DE OAUTH")
        print("=" * 60)
        
        results = []
        
        # Método 3 primero (más rápido)
        print("\n🔄 Probando método más rápido primero...")
        result = await self.test_method_3_direct_token()
        results.append(result)
        
        if result["success"]:
            print("\n🎉 ¡Token directo funcionó! No necesitamos OAuth")
            return results
        
        # Si el método directo falla, probar OAuth
        print("\n🔄 Probando métodos OAuth...")
        
        # Método 1
        result = await self.test_method_1_standard_oauth()
        results.append(result)
        
        if result["success"]:
            return results
        
        # Método 2
        result = await self.test_method_2_api_oauth()
        results.append(result)
        
        return results

async def main():
    """Función principal"""
    tester = ClickUpOAuthTester()
    results = await tester.run_all_tests()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    for i, result in enumerate(results, 1):
        status = "✅ ÉXITO" if result["success"] else "❌ FALLO"
        print(f"{i}. {result['method']}: {status}")
        
        if result["success"]:
            print(f"   🔑 Token: {result['token'][:20]}...{result['token'][-10:]}")
            if "token_url" in result:
                print(f"   🔗 URL: {result['token_url']}")
    
    print("\n🏁 Pruebas completadas")

if __name__ == "__main__":
    asyncio.run(main())
