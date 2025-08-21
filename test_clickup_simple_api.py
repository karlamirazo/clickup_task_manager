#!/usr/bin/env python3
"""
Script simple para probar la API de ClickUp con tokens directos
"""

import asyncio
import aiohttp
import json

async def test_clickup_api():
    """Test la API de ClickUp con diferentes enfoques"""
    
    print("üîó PROBANDO API DE CLICKUP")
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
        print(f"\nüîÑ PROBANDO TOKEN {i}: {token[:20]}...{token[-10:]}")
        print("-" * 50)
        
        for endpoint in endpoints:
            print(f"\nüì° Probando endpoint: {endpoint}")
            
            for j, header_format in enumerate(header_formats, 1):
                # Create headers con el token
                headers = {}
                for key, value in header_format.items():
                    headers[key] = value.format(token=token)
                
                print(f"  üîë Formato {j}: {list(headers.keys())[0]}")
                
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(endpoint, headers=headers, timeout=10) as response:
                            print(f"    üìä Status: {response.status}")
                            
                            if response.status == 200:
                                try:
                                    data = await response.json()
                                    print(f"    ‚úÖ ¬°EXITO! Respuesta: {json.dumps(data, indent=2)[:200]}...")
                                    
                                    # Si funciona, probar mas endpoints
                                    print(f"\nüéâ ¬°TOKEN FUNCIONA! Probando mas endpoints...")
                                    await test_working_token(token)
                                    return
                                    
                                except Exception as e:
                                    print(f"    ‚ö†Ô∏è  Status 200 pero error parseando JSON: {e}")
                                    text = await response.text()
                                    print(f"    üìù Respuesta: {text[:200]}...")
                                    
                            elif response.status == 401:
                                error_text = await response.text()
                                print(f"    ‚ùå 401 Unauthorized: {error_text}")
                                
                            elif response.status == 403:
                                error_text = await response.text()
                                print(f"    ‚ùå 403 Forbidden: {error_text}")
                                
                            else:
                                error_text = await response.text()
                                print(f"    ‚ùå Error {response.status}: {error_text[:100]}...")
                                
                except asyncio.TimeoutError:
                    print(f"    ‚è∞ Timeout")
                except Exception as e:
                    print(f"    ‚ùå Excepcion: {e}")
    
    print("\n‚ùå NINGUN TOKEN FUNCIONO")
    print("\nüîç DIAGNOSTICO:")
    print("1. Los tokens pueden estar expirados")
    print("2. Los tokens pueden ser de tipo incorrecto")
    print("3. ClickUp puede haber cambiado su API")
    print("4. Puede necesitar permisos especificos")

async def test_working_token(token):
    """Test mas funcionalidades con un token que funciona"""
    
    print(f"\nüöÄ PROBANDO FUNCIONALIDADES CON TOKEN VALIDO")
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
                        print(f"‚úÖ {name}: Funciona")
                    else:
                        print(f"‚ùå {name}: Error {response.status}")
                        
        except Exception as e:
            print(f"‚ùå {name}: Excepcion - {e}")
    
    print(f"\nüéâ ¬°CONEXION EXITOSA CON CLICKUP!")
    print(f"üîë Token valido: {token[:20]}...{token[-10:]}")

async def main():
    """Funcion principal"""
    print("üöÄ INICIANDO PRUEBAS DE API DE CLICKUP")
    print("=" * 60)
    
    await test_clickup_api()
    
    print("\nüèÅ Pruebas completadas")

if __name__ == "__main__":
    asyncio.run(main())
