#!/usr/bin/env python3
"""
Script para probar el estado de la API
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_api_status():
    """Test el estado de la API"""
    
    print("ğŸ§ª PROBANDO ESTADO DE LA API")
    print("=" * 40)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    try:
        async with aiohttp.ClientSession() as session:
            # 1. Test endpoint de test
            print("ğŸ“¡ Probando endpoint /test...")
            async with session.get(f"{base_url}/api/v1/tasks/test") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    response_text = await response.text()
                    print(f"   Respuesta: {response_text}")
                else:
                    print(f"   â�Œ Error: {response.status}")
            
            # 2. Test endpoint de config
            print("\nğŸ“¡ Probando endpoint /config...")
            async with session.get(f"{base_url}/api/v1/tasks/config") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    response_text = await response.text()
                    print(f"   Respuesta: {response_text}")
                else:
                    print(f"   â�Œ Error: {response.status}")
            
            # 3. Test endpoint de debug
            print("\nğŸ“¡ Probando endpoint /debug...")
            async with session.get(f"{base_url}/api/v1/tasks/debug") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    response_text = await response.text()
                    print(f"   Respuesta: {response_text}")
                else:
                    print(f"   â�Œ Error: {response.status}")
    
    except Exception as e:
        print(f"â�Œ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api_status())
