#!/usr/bin/env python3
"""
Script mejorado para probar OAuth de ClickUp con multiples opciones
"""

import asyncio
import aiohttp
import webbrowser
import time
from urllib.parse import urlencode, parse_qs, urlparse

class ClickUpOAuthTester:
    """Clase para probar OAuth de ClickUp con multiples metodos"""
    
    def __init__(self):
        self.client_id = "CXH47UNPORL0IJRX5Q24A6947IHHCN0U"
        self.client_secret = "FHJEHY9JJI68TY4X50XDLTBZEXFY4N1PSQY7VEPZPIFLBUIMKXZ3545M1BI4ME12"
        self.redirect_uri = "http://localhost:8000/callback"
        
    async def test_method_1_standard_oauth(self):
        """Metodo 1: OAuth estandar de ClickUp"""
        print("\nğŸ”� METODO 1: OAuth Estandar de ClickUp")
        print("=" * 50)
        
        # URL de autorizacion estandar
        auth_url = "https://app.clickup.com/oauth/authorize"
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "read:workspace read:space read:task read:user"
        }
        
        full_auth_url = f"{auth_url}?{urlencode(params)}"
        print(f"ğŸ”— URL: {full_auth_url}")
        
        print("\nğŸŒ� Abriendo navegador...")
        webbrowser.open(full_auth_url)
        
        return await self._get_auth_code_and_exchange("Metodo 1")
    
    async def test_method_2_api_oauth(self):
        """Metodo 2: OAuth usando API endpoint"""
        print("\nğŸ”� METODO 2: OAuth via API Endpoint")
        print("=" * 50)
        
        # URL de autorizacion via API
        auth_url = "https://api.clickup.com/api/v2/oauth/authorize"
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "read:workspace read:space read:task read:user"
        }
        
        full_auth_url = f"{auth_url}?{urlencode(params)}"
        print(f"ğŸ”— URL: {full_auth_url}")
        
        print("\nğŸŒ� Abriendo navegador...")
        webbrowser.open(full_auth_url)
        
        return await self._get_auth_code_and_exchange("Metodo 2")
    
    async def test_method_3_direct_token(self):
        """Metodo 3: Intentar usar token directo"""
        print("\nğŸ”� METODO 3: Token Directo (Bypass OAuth)")
        print("=" * 50)
        
        # Intentar usar el token que ya tienes
        test_tokens = [
            "pk_156221125_F8RNYI1M5XOASGLBUF9SFJW16QVNV2P3",
            "pk_156221125_CL5ODAXPK51HAWWENZWSNANAGWQLRQ8L",
            "pk_156221125_EAW6ZP8QWASDNZKT5K0HS8RNL737HIXZ"
        ]
        
        for i, token in enumerate(test_tokens, 1):
            print(f"\nğŸ”„ Probando token {i}: {token[:20]}...{token[-10:]}")
            
            try:
                # Test con endpoint simple
                test_url = "https://api.clickup.com/api/v2/user"
                headers = {"Authorization": f"Bearer {token}"}
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(test_url, headers=headers) as response:
                        print(f"ğŸ“¡ Status: {response.status}")
                        
                        if response.status == 200:
                            user_data = await response.json()
                            print(f"âœ… Â¡Funciono! Usuario: {user_data.get('user', {}).get('username', 'N/A')}")
                            return {"success": True, "token": token, "method": "Direct Token"}
                        else:
                            error_text = await response.text()
                            print(f"â�Œ Error: {error_text}")
                            
            except Exception as e:
                print(f"â�Œ Excepcion: {e}")
        
        print("â�Œ Ningun token directo funciono")
        return {"success": False, "method": "Direct Token"}
    
    async def _get_auth_code_and_exchange(self, method_name):
        """Get codigo de autorizacion e intercambiarlo por token"""
        print(f"\nğŸ“‹ Instrucciones para {method_name}:")
        print("1. Si la pagina se abre correctamente, autoriza la app")
        print("2. Copia el codigo de la URL de callback")
        print("3. Si hay error, describe exactamente que aparece")
        
        auth_code = input(f"\nğŸ“� Pega el codigo de autorizacion para {method_name}: ").strip()
        
        if not auth_code:
            print("â�Œ No se proporciono codigo")
            return {"success": False, "method": method_name}
        
        # Si es una URL, extraer el codigo
        if auth_code.startswith("http"):
            parsed = urlparse(auth_code)
            query_params = parse_qs(parsed.query)
            auth_code = query_params.get("code", [None])[0]
            
            if not auth_code:
                print("â�Œ No se pudo extraer codigo de la URL")
                return {"success": False, "method": method_name}
        
        try:
            print(f"\nğŸ”„ Intercambiando codigo: {auth_code[:10]}...")
            
            # Intentar multiples URLs de token
            token_urls = [
                "https://api.clickup.com/api/v2/oauth/token",
                "https://app.clickup.com/oauth/token",
                "https://api.clickup.com/oauth/token"
            ]
            
            for token_url in token_urls:
                print(f"ğŸ”„ Probando: {token_url}")
                
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
                            print(f"ğŸ“¡ Status: {response.status}")
                            
                            if response.status == 200:
                                token_data = await response.json()
                                access_token = token_data.get("access_token")
                                
                                if access_token:
                                    print(f"âœ… Token obtenido: {access_token[:20]}...{access_token[-10:]}")
                                    print("ğŸ�‰ Â¡OAuth funciono correctamente!")
                                    return {
                                        "success": True, 
                                        "token": access_token, 
                                        "method": method_name,
                                        "token_url": token_url
                                    }
                                else:
                                    print("â�Œ No se encontro access_token")
                                    print(f"Respuesta: {token_data}")
                            else:
                                error_text = await response.text()
                                print(f"â�Œ Error {response.status}: {error_text}")
                                
                except Exception as e:
                    print(f"â�Œ Error con {token_url}: {e}")
                    continue
            
            print("â�Œ Ninguna URL de token funciono")
            return {"success": False, "method": method_name}
            
        except Exception as e:
            print(f"â�Œ Error general: {e}")
            return {"success": False, "method": method_name}
    
    async def run_all_tests(self):
        """Execute todos los metodos de prueba"""
        print("ğŸš€ INICIANDO PRUEBAS COMPLETAS DE OAUTH")
        print("=" * 60)
        
        results = []
        
        # Metodo 3 primero (mas rapido)
        print("\nğŸ”„ Probando metodo mas rapido primero...")
        result = await self.test_method_3_direct_token()
        results.append(result)
        
        if result["success"]:
            print("\nğŸ�‰ Â¡Token directo funciono! No necesitamos OAuth")
            return results
        
        # Si el metodo directo falla, probar OAuth
        print("\nğŸ”„ Probando metodos OAuth...")
        
        # Metodo 1
        result = await self.test_method_1_standard_oauth()
        results.append(result)
        
        if result["success"]:
            return results
        
        # Metodo 2
        result = await self.test_method_2_api_oauth()
        results.append(result)
        
        return results

async def main():
    """Funcion principal"""
    tester = ClickUpOAuthTester()
    results = await tester.run_all_tests()
    
    print("\n" + "=" * 60)
    print("ğŸ“Š RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    for i, result in enumerate(results, 1):
        status = "âœ… EXITO" if result["success"] else "â�Œ FALLO"
        print(f"{i}. {result['method']}: {status}")
        
        if result["success"]:
            print(f"   ğŸ”‘ Token: {result['token'][:20]}...{result['token'][-10:]}")
            if "token_url" in result:
                print(f"   ğŸ”— URL: {result['token_url']}")
    
    print("\nğŸ�� Pruebas completadas")

if __name__ == "__main__":
    asyncio.run(main())
