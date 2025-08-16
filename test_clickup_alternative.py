#!/usr/bin/env python3
"""
Script alternativo para probar ClickUp con diferentes métodos de autenticación
"""

import asyncio
import aiohttp
import json
import base64

async def test_clickup_alternatives():
    """Probar métodos alternativos de autenticación con ClickUp"""
    
    print("🔗 PROBANDO MÉTODOS ALTERNATIVOS DE CLICKUP")
    print("=" * 60)
    
    # Tokens existentes
    existing_tokens = [
        "pk_156221125_F8RNYI1M5XOASGLBUF9SFJW16QVNV2P3",
        "pk_156221125_CL5ODAXPK51HAWWENZWSNANAGWQLRQ8L",
        "pk_156221125_EAW6ZP8QWASDNZKT5K0HS8RNL737HIXZ"
    ]
    
    # Métodos alternativos de autenticación
    auth_methods = [
        # Método 1: Bearer token estándar
        {"name": "Bearer Token", "headers": lambda t: {"Authorization": f"Bearer {t}"}},
        
        # Método 2: Token directo (sin Bearer)
        {"name": "Direct Token", "headers": lambda t: {"Authorization": t}},
        
        # Método 3: API Key header
        {"name": "API Key Header", "headers": lambda t: {"X-API-Key": t}},
        
        # Método 4: ClickUp específico
        {"name": "ClickUp Token", "headers": lambda t: {"X-ClickUp-Token": t}},
        
        # Método 5: Query parameter
        {"name": "Query Param", "headers": lambda t: {}, "params": lambda t: {"token": t}},
        
        # Método 6: Basic Auth (codificando token)
        {"name": "Basic Auth", "headers": lambda t: {"Authorization": f"Basic {base64.b64encode(t.encode()).decode()}"}},
        
        # Método 7: Custom header
        {"name": "Custom Header", "headers": lambda t: {"X-Auth-Token": t}},
        
        # Método 8: Cookie
        {"name": "Cookie Auth", "headers": lambda t: {"Cookie": f"auth_token={t}"}},
        
        # Método 9: User-Agent + Token
        {"name": "User-Agent + Token", "headers": lambda t: {"User-Agent": f"ClickUp-API/{t}"}},
        
        # Método 10: Referer + Token
        {"name": "Referer + Token", "headers": lambda t: {"Referer": f"https://app.clickup.com?token={t}"}}
    ]
    
    # Endpoints a probar (ordenados por probabilidad de éxito)
    endpoints = [
        ("User Info", "https://api.clickup.com/api/v2/user"),
        ("Teams", "https://api.clickup.com/api/v2/team"),
        ("Workspaces", "https://api.clickup.com/api/v2/workspace"),
        ("Spaces", "https://api.clickup.com/api/v2/space"),
        ("Folders", "https://api.clickup.com/api/v2/folder"),
        ("Lists", "https://api.clickup.com/api/v2/list"),
        ("Tasks", "https://api.clickup.com/api/v2/task")
    ]
    
    for i, token in enumerate(existing_tokens, 1):
        print(f"\n🔄 PROBANDO TOKEN {i}: {token[:20]}...{token[-10:]}")
        print("=" * 60)
        
        for auth_method in auth_methods:
            method_name = auth_method["name"]
            print(f"\n🔑 Método: {method_name}")
            print("-" * 40)
            
            # Probar con el primer endpoint (user) para cada método
            endpoint_name, endpoint_url = endpoints[0]
            
            try:
                # Preparar headers y parámetros
                headers = auth_method["headers"](token)
                params = auth_method.get("params", lambda t: {})(token)
                
                print(f"  📡 Endpoint: {endpoint_name}")
                print(f"  🔧 Headers: {list(headers.keys())}")
                if params:
                    print(f"  🔧 Params: {list(params.keys())}")
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(endpoint_url, headers=headers, params=params, timeout=15) as response:
                        print(f"  📊 Status: {response.status}")
                        
                        if response.status == 200:
                            try:
                                data = await response.json()
                                print(f"  ✅ ¡ÉXITO! Respuesta: {json.dumps(data, indent=2)[:200]}...")
                                
                                # Si funciona, probar todos los endpoints
                                print(f"\n🎉 ¡MÉTODO FUNCIONA! Probando todos los endpoints...")
                                await test_all_endpoints_with_method(token, auth_method)
                                return
                                
                            except Exception as e:
                                print(f"  ⚠️  Status 200 pero error parseando JSON: {e}")
                                text = await response.text()
                                print(f"  📝 Respuesta: {text[:200]}...")
                                
                        elif response.status == 401:
                            error_text = await response.text()
                            print(f"  ❌ 401 Unauthorized: {error_text}")
                            
                        elif response.status == 403:
                            error_text = await response.text()
                            print(f"  ❌ 403 Forbidden: {error_text}")
                            
                        elif response.status == 400:
                            error_text = await response.text()
                            print(f"  ❌ 400 Bad Request: {error_text}")
                            
                        else:
                            error_text = await response.text()
                            print(f"  ❌ Error {response.status}: {error_text[:100]}...")
                            
            except asyncio.TimeoutError:
                print(f"  ⏰ Timeout")
            except Exception as e:
                print(f"  ❌ Excepción: {e}")
    
    print("\n❌ NINGÚN MÉTODO FUNCIONÓ")
    print("\n🔍 DIAGNÓSTICO FINAL:")
    print("1. Los tokens están expirados o son inválidos")
    print("2. ClickUp requiere un token de cuenta personal (no de app OAuth)")
    print("3. Los permisos de la cuenta pueden estar restringidos")
    print("4. ClickUp puede haber cambiado su sistema de autenticación")
    
    print("\n💡 SOLUCIÓN RECOMENDADA:")
    print("1. Ve a ClickUp → Settings → Account")
    print("2. Busca 'API' o 'Developer' o 'Integrations'")
    print("3. Genera un 'Personal API Token' (no OAuth)")
    print("4. O contacta soporte de ClickUp para obtener acceso API")

async def test_all_endpoints_with_method(token, auth_method):
    """Probar todos los endpoints con un método que funciona"""
    
    print(f"\n🚀 PROBANDO TODOS LOS ENDPOINTS CON MÉTODO: {auth_method['name']}")
    print("=" * 60)
    
    endpoints = [
        ("User Info", "https://api.clickup.com/api/v2/user"),
        ("Teams", "https://api.clickup.com/api/v2/team"),
        ("Workspaces", "https://api.clickup.com/api/v2/workspace"),
        ("Spaces", "https://api.clickup.com/api/v2/space"),
        ("Folders", "https://api.clickup.com/api/v2/folder"),
        ("Lists", "https://api.clickup.com/api/v2/list"),
        ("Tasks", "https://api.clickup.com/api/v2/task")
    ]
    
    working_endpoints = []
    
    for name, endpoint_url in endpoints:
        try:
            headers = auth_method["headers"](token)
            params = auth_method.get("params", lambda t: {})(token)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint_url, headers=headers, params=params, timeout=15) as response:
                    if response.status == 200:
                        print(f"✅ {name}: Funciona")
                        working_endpoints.append(name)
                    else:
                        print(f"❌ {name}: Error {response.status}")
                        
        except Exception as e:
            print(f"❌ {name}: Excepción - {e}")
    
    print(f"\n🎉 ¡CONEXIÓN EXITOSA CON CLICKUP!")
    print(f"🔑 Token válido: {token[:20]}...{token[-10:]}")
    print(f"🔧 Método que funciona: {auth_method['name']}")
    print(f"📊 Endpoints funcionando: {len(working_endpoints)}/{len(endpoints)}")
    
    if working_endpoints:
        print(f"✅ Endpoints activos: {', '.join(working_endpoints)}")

async def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS ALTERNATIVAS DE CLICKUP")
    print("=" * 70)
    
    await test_clickup_alternatives()
    
    print("\n🏁 Pruebas alternativas completadas")

if __name__ == "__main__":
    asyncio.run(main())
