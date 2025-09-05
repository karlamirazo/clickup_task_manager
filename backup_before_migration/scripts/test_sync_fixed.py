#!/usr/bin/env python3
"""
Script de prueba para verificar la sincronización corregida
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_sync_endpoints():
    """Probar los endpoints de sincronización"""
    base_url = "http://localhost:8000"
    
    print("🧪 Probando endpoints de sincronización...")
    print(f"📍 URL base: {base_url}")
    print("=" * 60)
    
    # 1. Probar endpoint de sincronización normal
    print("1️⃣ Probando endpoint /sync...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{base_url}/api/v1/tasks/sync") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"   ✅ Sincronización exitosa: {result.get('total_tasks_synced', 0)} tareas")
                    print(f"   📊 Creadas: {result.get('total_tasks_created', 0)}")
                    print(f"   📝 Actualizadas: {result.get('total_tasks_updated', 0)}")
                    print(f"   🗑️ Eliminadas: {result.get('total_tasks_deleted', 0)}")
                    if result.get('errors'):
                        print(f"   ⚠️ Errores: {len(result['errors'])}")
                        for error in result['errors'][:3]:  # Mostrar solo los primeros 3
                            print(f"      - {error}")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error en sincronización: {response.status}")
                    print(f"      {error_text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
    
    print()
    
    # 2. Probar endpoint de sincronización de emergencia
    print("2️⃣ Probando endpoint /sync-emergency...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{base_url}/api/v1/tasks/sync-emergency") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"   ✅ Sincronización de emergencia exitosa")
                    print(f"   📊 Estado: {result.get('status', 'unknown')}")
                    if 'result' in result:
                        sync_result = result['result']
                        print(f"   📈 Tareas sincronizadas: {sync_result.get('total_tasks_synced', 0)}")
                        print(f"   ⏱️ Duración: {sync_result.get('duration', 0):.2f}s")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error en sincronización de emergencia: {response.status}")
                    print(f"      {error_text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
    
    print()
    
    # 3. Verificar estado de las tareas
    print("3️⃣ Verificando estado de las tareas...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/api/v1/tasks/?include_closed=true&page=0&limit=10") as response:
                if response.status == 200:
                    tasks = await response.json()
                    print(f"   ✅ Tareas disponibles: {len(tasks)}")
                    if tasks:
                        # Mostrar información de la primera tarea
                        first_task = tasks[0]
                        print(f"   📋 Primera tarea: {first_task.get('name', 'Sin nombre')[:50]}...")
                        print(f"   🏷️ Status: {first_task.get('status', 'unknown')}")
                        print(f"   📅 Última sincronización: {first_task.get('updated_at', 'unknown')}")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error obteniendo tareas: {response.status}")
                    print(f"      {error_text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
    
    print()
    
    # 4. Probar endpoint de debug
    print("4️⃣ Probando endpoint de debug...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/debug") as response:
                if response.status == 200:
                    debug_info = await response.json()
                    print(f"   ✅ Debug disponible")
                    print(f"   🗄️ Base de datos: {debug_info.get('database', {}).get('database_status', 'unknown')}")
                    print(f"   🔗 ClickUp: {debug_info.get('clickup_client', {}).get('client_status', 'unknown')}")
                    print(f"   📝 Logging: {debug_info.get('logging_system', 'unknown')}")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error en debug: {response.status}")
                    print(f"      {error_text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
    
    print()
    print("=" * 60)
    print("🏁 Pruebas completadas")

async def test_sync_with_workspace_id():
    """Probar sincronización con workspace ID específico"""
    base_url = "http://localhost:8000"
    workspace_id = "9014943317"  # Workspace por defecto
    
    print(f"🎯 Probando sincronización con workspace ID: {workspace_id}")
    print("=" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Probar sincronización normal
            print("🔄 Sincronización normal...")
            async with session.post(f"{base_url}/api/v1/tasks/sync?workspace_id={workspace_id}") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"   ✅ Exitoso: {result.get('total_tasks_synced', 0)} tareas")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error: {response.status} - {error_text}")
            
            print()
            
            # Probar sincronización de emergencia
            print("🆘 Sincronización de emergencia...")
            async with session.post(f"{base_url}/api/v1/tasks/sync-emergency?workspace_id={workspace_id}") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"   ✅ Exitoso: {result.get('status', 'unknown')}")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error: {response.status} - {error_text}")
                    
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
    
    print("=" * 60)

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de sincronización corregida...")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Ejecutar pruebas
    asyncio.run(test_sync_endpoints())
    print()
    asyncio.run(test_sync_with_workspace_id())
    
    print()
    print("🎉 Todas las pruebas completadas")
