#!/usr/bin/env python3
"""
Script simple para probar la API de ClickUp con tokens directos
"""

import asyncio
import aiohttp
import json

async def test_clickup_api():
    """Probar la API de ClickUp con diferentes enfoques"""
    
    print("🔗 PROBANDO API DE CLICKUP")
    print("=" * 50)
    
    # Tokens a probar
    tokens = [
        "pk_156221125_F8RNYI1M5XOASGLBUF9SFJW16QVNV2P3",
        "pk_156221125_CL5ODAXPK51HAWWENZWSNANAGWQLRQ8L",
        "pk_156221125_EAW6ZP8QWASDNZKT5K0HS8RNL737HIXZ"
    ]
    
    # Endpoints a probar
    endpoints = [
        "https://api.clickup.com/api/v2/user",
        "https://api.clickup.com/api/v2/team",
        "https://api.clickup.com/api/v2/workspace",
        "https://api.clickup.com/api/v2/space"
    ]
    
    # Diferentes formatos de headers
    header_formats = [
        {"Authorization": "Bearer {token}"},
        {"Authorization": "token {token}"},
        {"X-API-Key": "{token}"},
        {"X-ClickUp-Token": "{token}"},
        {"api_key": "{token}"}
    ]
    
    for i, token in enumerate(tokens, 1):
        print(f"\n🔄 PROBANDO TOKEN {i}: {token[:20]}...{token[-10:]}")
        print("-" * 50)
        
        for endpoint in endpoints:
            print(f"\n📡 Probando endpoint: {endpoint}")
            
            for j, header_format in enumerate(header_formats, 1):
                # Crear headers con el token
                headers = {}
                for key, value in header_format.items():
                    headers[key] = value.format(token=token)
                
                print(f"  🔑 Formato {j}: {list(headers.keys())[0]}")
                
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(endpoint, headers=headers, timeout=10) as response:
                            print(f"    📊 Status: {response.status}")
                            
                            if response.status == 200:
                                try:
                                    data = await response.json()
                                    print(f"    ✅ ¡ÉXITO! Respuesta: {json.dumps(data, indent=2)[:200]}...")
                                    
                                    # Si funciona, probar más endpoints
                                    print(f"\n🎉 ¡TOKEN FUNCIONA! Probando más endpoints...")
                                    await test_working_token(token)
                                    return
                                    
                                except Exception as e:
                                    print(f"    ⚠️  Status 200 pero error parseando JSON: {e}")
                                    text = await response.text()
                                    print(f"    📝 Respuesta: {text[:200]}...")
                                    
                            elif response.status == 401:
                                error_text = await response.text()
                                print(f"    ❌ 401 Unauthorized: {error_text}")
                                
                            elif response.status == 403:
                                error_text = await response.text()
                                print(f"    ❌ 403 Forbidden: {error_text}")
                                
                            else:
                                error_text = await response.text()
                                print(f"    ❌ Error {response.status}: {error_text[:100]}...")
                                
                except asyncio.TimeoutError:
                    print(f"    ⏰ Timeout")
                except Exception as e:
                    print(f"    ❌ Excepción: {e}")
    
    print("\n❌ NINGÚN TOKEN FUNCIONÓ")
    print("\n🔍 DIAGNÓSTICO:")
    print("1. Los tokens pueden estar expirados")
    print("2. Los tokens pueden ser de tipo incorrecto")
    print("3. ClickUp puede haber cambiado su API")
    print("4. Puede necesitar permisos específicos")

async def test_working_token(token):
    """Probar más funcionalidades con un token que funciona"""
    
    print(f"\n🚀 PROBANDO FUNCIONALIDADES CON TOKEN VÁLIDO")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Endpoints adicionales para probar
    test_endpoints = [
        ("User Info", "https://api.clickup.com/api/v2/user"),
        ("Teams", "https://api.clickup.com/api/v2/team"),
        ("Workspaces", "https://api.clickup.com/api/v2/workspace"),
        ("Spaces", "https://api.clickup.com/api/v2/space"),
        ("Folders", "https://api.clickup.com/api/v2/folder"),
        ("Lists", "https://api.clickup.com/api/v2/list"),
        ("Tasks", "https://api.clickup.com/api/v2/task")
    ]
    
    for name, endpoint in test_endpoints:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        print(f"✅ {name}: Funciona")
                    else:
                        print(f"❌ {name}: Error {response.status}")
                        
        except Exception as e:
            print(f"❌ {name}: Excepción - {e}")
    
    print(f"\n🎉 ¡CONEXIÓN EXITOSA CON CLICKUP!")
    print(f"🔑 Token válido: {token[:20]}...{token[-10:]}")

async def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DE API DE CLICKUP")
    print("=" * 60)
    
    await test_clickup_api()
    
    print("\n🏁 Pruebas completadas")

if __name__ == "__main__":
    asyncio.run(main())
