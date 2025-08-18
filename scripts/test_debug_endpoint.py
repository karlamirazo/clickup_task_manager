#!/usr/bin/env python3
"""
Script para probar específicamente el endpoint de debug
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_debug_endpoint():
    """Probar específicamente el endpoint de debug"""
    
    print("🧪 PROBANDO ENDPOINT DE DEBUG")
    print("=" * 40)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📡 Probando endpoint /debug...")
            async with session.get(f"{base_url}/api/v1/tasks/debug") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    response_text = await response.text()
                    print(f"   ✅ Respuesta exitosa:")
                    print(f"   📄 Respuesta: {response_text}")
                    
                    # Intentar parsear JSON
                    try:
                        data = json.loads(response_text)
                        print(f"\n🔍 Datos parseados:")
                        for key, value in data.items():
                            print(f"   📋 {key}: {value}")
                    except json.JSONDecodeError as e:
                        print(f"   ❌ Error parseando JSON: {e}")
                else:
                    print(f"   ❌ Error: {response.status}")
                    response_text = await response.text()
                    print(f"   📄 Respuesta: {response_text}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_debug_endpoint())
