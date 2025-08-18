#!/usr/bin/env python3
"""
Script para probar las importaciones en Railway
"""

import asyncio
import aiohttp
import json

async def test_imports():
    """Probar las importaciones en Railway"""
    
    print("🧪 PROBANDO IMPORTACIONES EN RAILWAY")
    print("=" * 50)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Probar endpoint de test
            print("📡 Probando endpoint de test...")
            async with session.get(f"{base_url}/test-simple") as response:
                print(f"📡 Status: {response.status}")
                response_text = await response.text()
                print(f"📄 Respuesta: {response_text}")
                
                if response.status == 200:
                    print("✅ Endpoint de test funciona")
                else:
                    print("❌ Endpoint de test no funciona")
            
            # Probar endpoint de logging
            print(f"\n📡 Probando endpoint de logging...")
            async with session.get(f"{base_url}/test-logging") as response:
                print(f"📡 Status: {response.status}")
                response_text = await response.text()
                print(f"📄 Respuesta: {response_text}")
                
                if response.status == 200:
                    print("✅ Endpoint de logging funciona")
                else:
                    print("❌ Endpoint de logging no funciona")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_imports())
