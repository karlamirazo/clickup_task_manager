#!/usr/bin/env python3
"""
Script para probar las importaciones en Railway
"""

import asyncio
import aiohttp
import json

async def test_imports():
    """Test las importaciones en Railway"""
    
    print("ğŸ§ª PROBANDO IMPORTACIONES EN RAILWAY")
    print("=" * 50)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test endpoint de test
            print("ğŸ“¡ Probando endpoint de test...")
            async with session.get(f"{base_url}/test-simple") as response:
                print(f"ğŸ“¡ Status: {response.status}")
                response_text = await response.text()
                print(f"ğŸ“„ Respuesta: {response_text}")
                
                if response.status == 200:
                    print("âœ… Endpoint de test funciona")
                else:
                    print("â�Œ Endpoint de test no funciona")
            
            # Test endpoint de logging
            print(f"\nğŸ“¡ Probando endpoint de logging...")
            async with session.get(f"{base_url}/test-logging") as response:
                print(f"ğŸ“¡ Status: {response.status}")
                response_text = await response.text()
                print(f"ğŸ“„ Respuesta: {response_text}")
                
                if response.status == 200:
                    print("âœ… Endpoint de logging funciona")
                else:
                    print("â�Œ Endpoint de logging no funciona")
    
    except Exception as e:
        print(f"â�Œ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_imports())
