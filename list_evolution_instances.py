#!/usr/bin/env python3
"""
Listar todas las instancias disponibles en Evolution API
"""

import asyncio
import aiohttp
import json

async def list_evolution_instances():
    """Listar todas las instancias disponibles"""
    print("🔍 LISTANDO INSTANCIAS DE EVOLUTION API")
    print("=" * 50)
    
    # Configuración de Evolution API
    EVOLUTION_URL = "https://evolution-api-production-9d5d.up.railway.app"
    API_KEY = "clickup-evolution-v223"
    
    print(f"📱 Evolution API: {EVOLUTION_URL}")
    print(f"🔑 API Key: {API_KEY}")
    
    try:
        # 1. Listar todas las instancias
        print(f"\n1️⃣ Listando todas las instancias...")
        async with aiohttp.ClientSession() as session:
            headers = {"apikey": API_KEY}
            
            instances_url = f"{EVOLUTION_URL}/instance/fetchInstances"
            async with session.get(instances_url, headers=headers) as response:
                print(f"   📊 Status: {response.status}")
                
                if response.status == 200:
                    instances_data = await response.json()
                    print(f"   ✅ Instancias encontradas: {len(instances_data) if isinstance(instances_data, list) else 'N/A'}")
                    print(f"   📋 Datos completos: {json.dumps(instances_data, indent=2)}")
                    
                    # Procesar instancias
                    if isinstance(instances_data, list):
                        print(f"\n📱 INSTANCIAS DISPONIBLES:")
                        for i, instance in enumerate(instances_data, 1):
                            if isinstance(instance, dict):
                                instance_name = instance.get("instance", "N/A")
                                instance_status = instance.get("status", "N/A")
                                print(f"   {i}. {instance_name} - Estado: {instance_status}")
                            else:
                                print(f"   {i}. {instance}")
                    else:
                        print(f"   ℹ️ Formato de respuesta: {type(instances_data)}")
                        
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error listando instancias: {error_text}")
                    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    try:
        # 2. Intentar obtener información de la instancia específica
        print(f"\n2️⃣ Verificando instancia 'clickup-v23'...")
        async with aiohttp.ClientSession() as session:
            headers = {"apikey": API_KEY}
            
            # Probar diferentes endpoints
            endpoints = [
                "/instance/find/clickup-v23",
                "/instance/info/clickup-v23", 
                "/instance/connectionState/clickup-v23"
            ]
            
            for endpoint in endpoints:
                try:
                    url = f"{EVOLUTION_URL}{endpoint}"
                    async with session.get(url, headers=headers) as response:
                        print(f"   📊 {endpoint}: {response.status}")
                        if response.status != 200:
                            error_text = await response.text()
                            print(f"      ❌ Error: {error_text}")
                        else:
                            data = await response.json()
                            print(f"      ✅ Datos: {data}")
                except Exception as e:
                    print(f"      ❌ Error en {endpoint}: {e}")
                    
    except Exception as e:
        print(f"   ❌ Error verificando instancia específica: {e}")
    
    try:
        # 3. Verificar endpoints disponibles
        print(f"\n3️⃣ Verificando endpoints disponibles...")
        async with aiohttp.ClientSession() as session:
            headers = {"apikey": API_KEY}
            
            # Probar endpoint raíz
            root_url = EVOLUTION_URL
            async with session.get(root_url, headers=headers) as response:
                print(f"   📊 Root endpoint: {response.status}")
                if response.status == 200:
                    root_data = await response.text()
                    print(f"      ✅ Respuesta: {root_data[:200]}...")
                else:
                    print(f"      ❌ Error: {response.status}")
                    
    except Exception as e:
        print(f"   ❌ Error verificando endpoints: {e}")
    
    print(f"\n" + "=" * 50)
    print("✅ VERIFICACIÓN COMPLETADA")

if __name__ == "__main__":
    print("🚀 Verificando instancias de Evolution API...")
    asyncio.run(list_evolution_instances())
