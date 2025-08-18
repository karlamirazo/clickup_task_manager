#!/usr/bin/env python3
"""
Script para verificar el estado del deployment
"""

import asyncio
import aiohttp
import json

async def check_deployment_status():
    """Verificar el estado del deployment"""
    
    print("🔍 VERIFICANDO ESTADO DEL DEPLOYMENT")
    print("=" * 50)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Probar endpoint básico
            print("📡 Probando endpoint básico...")
            async with session.get(f"{base_url}/") as response:
                print(f"📡 Status: {response.status}")
                response_text = await response.text()
                print(f"📄 Respuesta: {response_text[:200]}...")
                
                if response.status == 200:
                    print("✅ Endpoint básico funciona")
                else:
                    print("❌ Endpoint básico no funciona")
            
            # Probar endpoint de health check
            print(f"\n📡 Probando health check...")
            async with session.get(f"{base_url}/health") as response:
                print(f"📡 Status: {response.status}")
                response_text = await response.text()
                print(f"📄 Respuesta: {response_text}")
                
                if response.status == 200:
                    print("✅ Health check funciona")
                else:
                    print("❌ Health check no funciona")
            
            # Probar endpoint de debug
            print(f"\n📡 Probando endpoint de debug...")
            async with session.get(f"{base_url}/debug") as response:
                print(f"📡 Status: {response.status}")
                response_text = await response.text()
                print(f"📄 Respuesta: {response_text[:200]}...")
                
                if response.status == 200:
                    print("✅ Endpoint de debug funciona")
                else:
                    print("❌ Endpoint de debug no funciona")
            
            # Probar endpoint de tareas
            print(f"\n📡 Probando endpoint de tareas...")
            async with session.get(f"{base_url}/api/v1/tasks") as response:
                print(f"📡 Status: {response.status}")
                response_text = await response.text()
                print(f"📄 Respuesta: {response_text[:200]}...")
                
                if response.status == 200:
                    print("✅ Endpoint de tareas funciona")
                else:
                    print("❌ Endpoint de tareas no funciona")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_deployment_status())
