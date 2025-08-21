#!/usr/bin/env python3
"""
Script alternativo para probar ClickUp con diferentes metodos de autenticacion
"""

import asyncio
import aiohttp
import json
import base64

async def test_clickup_alternatives():
    """Test metodos alternativos de autenticacion con ClickUp"""
    
    print("üîó PROBANDO METODOS ALTERNATIVOS DE CLICKUP")
    print("=" * 60)
    
    # Tokens existentes
    existing_tokens = [
        "pk_156221125_F8RNYI1M5XOASGLBUF9SFJW16QVNV2P3",
        "pk_156221125_CL5ODAXPK51HAWWENZWSNANAGWQLRQ8L",
        "pk_156221125_EAW6ZP8QWASDNZKT5K0HS8RNL737HIXZ"
    ]
    
    # Metodos alternativos de autenticacion
    auth_methods = [
        # Metodo 1: Bearer token estandar
        {"name": "Bearer Token", "headers": lambda t: {"Authorization": f"Bearer {t}"}},
        
        # Metodo 2: Token directo (sin Bearer)
        {"name": "Direct Token", "headers": lambda t: {"Authorization": t}},
        
        # Metodo 3: API Key header
        {"name": "API Key Header", "headers": lambda t: {"X-API-Key": t}},
        
        # Metodo 4: ClickUp especifico
        {"name": "ClickUp Token", "headers": lambda t: {"X-ClickUp-Token": t}},
        
        # Metodo 5: Query parameter
        {"name": "Query Param", "headers": lambda t: {}, "params": lambda t: {"token": t}},
        
        # Metodo 6: Basic Auth (codificando token)
        {"name": "Basic Auth", "headers": lambda t: {"Authorization": f"Basic {base64.b64encode(t.encode()).decode()}"}},
        
        # Metodo 7: Custom header
        {"name": "Custom Header", "headers": lambda t: {"X-Auth-Token": t}},
        
        # Metodo 8: Cookie
        {"name": "Cookie Auth", "headers": lambda t: {"Cookie": f"auth_token={t}"}},
        
        # Metodo 9: User-Agent + Token
        {"name": "User-Agent + Token", "headers": lambda t: {"User-Agent": f"ClickUp-API/{t}"}},
        
        # Metodo 10: Referer + Token
        {"name": "Referer + Token", "headers": lambda t: {"Referer": f"https://app.clickup.com?token={t}"}}
    ]
    
    # Endpoints a probar (ordenados por probabilidad de exito)
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
        print(f"\nüîÑ PROBANDO TOKEN {i}: {token[:20]}...{token[-10:]}")
        print("=" * 60)
        
        for auth_method in auth_methods:
            method_name = auth_method["name"]
            print(f"\nüîë Metodo: {method_name}")
            print("-" * 40)
            
            # Test con el primer endpoint (user) para cada metodo
            endpoint_name, endpoint_url = endpoints[0]
            
            try:
                # Preparar headers y parametros
                headers = auth_method["headers"](token)
                params = auth_method.get("params", lambda t: {})(token)
                
                print(f"  üì° Endpoint: {endpoint_name}")
                print(f"  üîß Headers: {list(headers.keys())}")
                if params:
                    print(f"  üîß Params: {list(params.keys())}")
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(endpoint_url, headers=headers, params=params, timeout=15) as response:
                        print(f"  üìä Status: {response.status}")
                        
                        if response.status == 200:
                            try:
                                data = await response.json()
                                print(f"  ‚úÖ ¬°EXITO! Respuesta: {json.dumps(data, indent=2)[:200]}...")
                                
                                # Si funciona, probar todos los endpoints
                                print(f"\nüéâ ¬°METODO FUNCIONA! Probando todos los endpoints...")
                                await test_all_endpoints_with_method(token, auth_method)
                                return
                                
                            except Exception as e:
                                print(f"  ‚ö†Ô∏è  Status 200 pero error parseando JSON: {e}")
                                text = await response.text()
                                print(f"  üìù Respuesta: {text[:200]}...")
                                
                        elif response.status == 401:
                            error_text = await response.text()
                            print(f"  ‚ùå 401 Unauthorized: {error_text}")
                            
                        elif response.status == 403:
                            error_text = await response.text()
                            print(f"  ‚ùå 403 Forbidden: {error_text}")
                            
                        elif response.status == 400:
                            error_text = await response.text()
                            print(f"  ‚ùå 400 Bad Request: {error_text}")
                            
                        else:
                            error_text = await response.text()
                            print(f"  ‚ùå Error {response.status}: {error_text[:100]}...")
                            
            except asyncio.TimeoutError:
                print(f"  ‚è∞ Timeout")
            except Exception as e:
                print(f"  ‚ùå Excepcion: {e}")
    
    print("\n‚ùå NINGUN METODO FUNCIONO")
    print("\nüîç DIAGNOSTICO FINAL:")
    print("1. Los tokens estan expirados o son invalidos")
    print("2. ClickUp requiere un token de cuenta personal (no de app OAuth)")
    print("3. Los permisos de la cuenta pueden estar restringidos")
    print("4. ClickUp puede haber cambiado su sistema de autenticacion")
    
    print("\nüí° SOLUCION RECOMENDADA:")
    print("1. Ve a ClickUp ‚Üí Settings ‚Üí Account")
    print("2. Busca 'API' o 'Developer' o 'Integrations'")
    print("3. Genera un 'Personal API Token' (no OAuth)")
    print("4. O contacta soporte de ClickUp para obtener acceso API")

async def test_all_endpoints_with_method(token, auth_method):
    """Test todos los endpoints con un metodo que funciona"""
    
    print(f"\nüöÄ PROBANDO TODOS LOS ENDPOINTS CON METODO: {auth_method['name']}")
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
                        print(f"‚úÖ {name}: Funciona")
                        working_endpoints.append(name)
                    else:
                        print(f"‚ùå {name}: Error {response.status}")
                        
        except Exception as e:
            print(f"‚ùå {name}: Excepcion - {e}")
    
    print(f"\nüéâ ¬°CONEXION EXITOSA CON CLICKUP!")
    print(f"üîë Token valido: {token[:20]}...{token[-10:]}")
    print(f"üîß Metodo que funciona: {auth_method['name']}")
    print(f"üìä Endpoints funcionando: {len(working_endpoints)}/{len(endpoints)}")
    
    if working_endpoints:
        print(f"‚úÖ Endpoints activos: {', '.join(working_endpoints)}")

async def main():
    """Funcion principal"""
    print("üöÄ INICIANDO PRUEBAS ALTERNATIVAS DE CLICKUP")
    print("=" * 70)
    
    await test_clickup_alternatives()
    
    print("\nüèÅ Pruebas alternativas completadas")

if __name__ == "__main__":
    asyncio.run(main())
