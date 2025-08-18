#!/usr/bin/env python3
"""
Script para probar el estado de la API
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_api_status():
    """Probar el estado de la API"""
    
    print("🧪 PROBANDO ESTADO DE LA API")
    print("=" * 40)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    try:
        async with aiohttp.ClientSession() as session:
            # 1. Probar endpoint de test
            print("📡 Probando endpoint /test...")
            async with session.get(f"{base_url}/api/v1/tasks/test") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    response_text = await response.text()
                    print(f"   Respuesta: {response_text}")
                else:
                    print(f"   ❌ Error: {response.status}")
            
            # 2. Probar endpoint de config
            print("\n📡 Probando endpoint /config...")
            async with session.get(f"{base_url}/api/v1/tasks/config") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    response_text = await response.text()
                    print(f"   Respuesta: {response_text}")
                else:
                    print(f"   ❌ Error: {response.status}")
            
            # 3. Probar endpoint de debug
            print("\n📡 Probando endpoint /debug...")
            async with session.get(f"{base_url}/api/v1/tasks/debug") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    response_text = await response.text()
                    print(f"   Respuesta: {response_text}")
                else:
                    print(f"   ❌ Error: {response.status}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api_status())
