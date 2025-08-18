#!/usr/bin/env python3
"""
Script para debuggear campos personalizados en ClickUp
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def debug_custom_fields():
    """Debuggear campos personalizados en ClickUp"""
    
    print("🔍 DEBUGGING CAMPOS PERSONALIZADOS EN CLICKUP")
    print("=" * 60)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Datos de prueba con campos personalizados específicos
    task_data = {
        "name": f"Debug Campos Personalizados - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Tarea para debuggear campos personalizados Email y Celular",
        "workspace_id": "9014943317",
        "list_id": "901411770471",  # PROYECTO 1
        "status": "in progress",
        "priority": 2,
        "due_date": "2025-08-21",
        "assignees": "88425547",  # Karla Rosas
        "custom_fields": {
            "Email": "debug@test.com",
            "Celular": "+52 55 9999 9999"
        }
    }
    
    print(f"📋 Datos de la tarea:")
    print(f"   📝 Nombre: {task_data['name']}")
    print(f"   📧 Email: {task_data['custom_fields']['Email']}")
    print(f"   📱 Celular: {task_data['custom_fields']['Celular']}")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            # Crear la tarea
            print("🚀 Creando tarea con campos personalizados...")
            async with session.post(
                f"{base_url}/api/v1/tasks/",
                json=task_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                print(f"📡 Status: {response.status}")
                response_text = await response.text()
                print(f"📄 Respuesta: {response_text}")
                
                if response.status == 201:
                    response_data = json.loads(response_text)
                    task_id = response_data.get("id")
                    clickup_id = response_data.get("clickup_id")
                    
                    print(f"✅ Tarea creada:")
                    print(f"   🆔 ID Local: {task_id}")
                    print(f"   🆔 ID ClickUp: {clickup_id}")
                    print(f"   📧 Campos personalizados guardados: {response_data.get('custom_fields')}")
                    
                    # Verificar la tarea en ClickUp
                    print(f"\n🔍 Verificando tarea en ClickUp...")
                    async with session.get(f"{base_url}/api/v1/tasks/{task_id}") as get_response:
                        if get_response.status == 200:
                            task_info = json.loads(await get_response.text())
                            print(f"✅ Tarea recuperada:")
                            print(f"   📝 Nombre: {task_info.get('name')}")
                            print(f"   📧 Campos personalizados: {task_info.get('custom_fields')}")
                        else:
                            print(f"❌ Error obteniendo tarea: {get_response.status}")
                    
                    # Intentar obtener información directa de ClickUp
                    print(f"\n🔍 Verificando campos personalizados en ClickUp...")
                    print(f"⚠️ Nota: Esto requiere acceso directo a la API de ClickUp")
                    print(f"💡 Los campos personalizados podrían no aparecer inmediatamente")
                    print(f"💡 Verifica manualmente en la interfaz de ClickUp")
                    
                else:
                    print(f"❌ Error creando tarea: {response.status}")
                    print(f"📄 Detalles: {response_text}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_custom_fields())
