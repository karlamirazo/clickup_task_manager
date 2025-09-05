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
    
    print("ğŸ”� DEBUGGING CAMPOS PERSONALIZADOS EN CLICKUP")
    print("=" * 60)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Datos de prueba con campos personalizados especificos
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
    
    print(f"ğŸ“‹ Datos de la tarea:")
    print(f"   ğŸ“� Nombre: {task_data['name']}")
    print(f"   ğŸ“§ Email: {task_data['custom_fields']['Email']}")
    print(f"   ğŸ“± Celular: {task_data['custom_fields']['Celular']}")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            # Create la tarea
            print("ğŸš€ Creando tarea con campos personalizados...")
            async with session.post(
                f"{base_url}/api/v1/tasks/",
                json=task_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                print(f"ğŸ“¡ Status: {response.status}")
                response_text = await response.text()
                print(f"ğŸ“„ Respuesta: {response_text}")
                
                if response.status == 201:
                    response_data = json.loads(response_text)
                    task_id = response_data.get("id")
                    clickup_id = response_data.get("clickup_id")
                    
                    print(f"âœ… Tarea creada:")
                    print(f"   ğŸ†” ID Local: {task_id}")
                    print(f"   ğŸ†” ID ClickUp: {clickup_id}")
                    print(f"   ğŸ“§ Campos personalizados guardados: {response_data.get('custom_fields')}")
                    
                    # Verificar la tarea en ClickUp
                    print(f"\nğŸ”� Verificando tarea en ClickUp...")
                    async with session.get(f"{base_url}/api/v1/tasks/{task_id}") as get_response:
                        if get_response.status == 200:
                            task_info = json.loads(await get_response.text())
                            print(f"âœ… Tarea recuperada:")
                            print(f"   ğŸ“� Nombre: {task_info.get('name')}")
                            print(f"   ğŸ“§ Campos personalizados: {task_info.get('custom_fields')}")
                        else:
                            print(f"â�Œ Error getting tarea: {get_response.status}")
                    
                    # Intentar obtener informacion directa de ClickUp
                    print(f"\nğŸ”� Verificando campos personalizados en ClickUp...")
                    print(f"âš ï¸� Nota: Esto requiere acceso directo a la API de ClickUp")
                    print(f"ğŸ’¡ Los campos personalizados podrian no aparecer inmediatamente")
                    print(f"ğŸ’¡ Verifica manualmente en la interfaz de ClickUp")
                    
                else:
                    print(f"â�Œ Error creating tarea: {response.status}")
                    print(f"ğŸ“„ Detalles: {response_text}")
    
    except Exception as e:
        print(f"â�Œ Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_custom_fields())
