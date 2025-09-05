#!/usr/bin/env python3
"""
Script para verificar los campos personalizados de una tarea existente
"""

import asyncio
import aiohttp
import json

async def test_existing_task_fields():
    """Verificar campos personalizados de tareas existentes"""
    
    print("ğŸ”� VERIFICANDO CAMPOS PERSONALIZADOS DE TAREAS EXISTENTES")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get todas las tareas
            print("ğŸ“‹ Obteniendo todas las tareas...")
            async with session.get(f"{base_url}/api/v1/tasks") as response:
                print(f"ğŸ“¡ Status: {response.status}")
                response_text = await response.text()
                print(f"ğŸ“„ Respuesta: {response_text}")
                
                if response.status == 200:
                    tasks_data = json.loads(response_text)
                    tasks = tasks_data if isinstance(tasks_data, list) else []
                    print(f"âœ… Tareas obtenidas: {len(tasks)}")
                    
                    # Buscar la tarea "Partido =" que sabemos que tiene campos personalizados
                    for task in tasks:
                        task_name = task.get("name", "")
                        custom_fields = task.get("custom_fields", {})
                        
                        print(f"\nğŸ“� Tarea: {task_name}")
                        print(f"   ğŸ†” ID: {task.get('id')}")
                        print(f"   ğŸ†” ClickUp ID: {task.get('clickup_id')}")
                        print(f"   ğŸ“§ Campos personalizados: {custom_fields}")
                        
                        # Si es la tarea "Partido =", mostrar mas detalles
                        if "Partido" in task_name:
                            print(f"   ğŸ�¯ Â¡ENCONTRADA LA TAREA CON CAMPOS PERSONALIZADOS!")
                            print(f"   ğŸ“§ Email: {custom_fields.get('Email', 'No encontrado')}")
                            print(f"   ğŸ“± Celular: {custom_fields.get('Celular', 'No encontrado')}")
                            
                            # Intentar obtener mas detalles de esta tarea especifica
                            task_id = task.get("id")
                            if task_id:
                                print(f"\nğŸ”� Obteniendo detalles completos de la tarea {task_id}...")
                                async with session.get(f"{base_url}/api/v1/tasks/{task_id}") as detail_response:
                                    if detail_response.status == 200:
                                        detail_data = json.loads(await detail_response.text())
                                        print(f"âœ… Detalles completos:")
                                        print(f"   ğŸ“� Nombre: {detail_data.get('name')}")
                                        print(f"   ğŸ“§ Campos personalizados: {detail_data.get('custom_fields')}")
                                        print(f"   ğŸ“Š Estado: {detail_data.get('status')}")
                                        print(f"   ğŸ‘¤ Usuario asignado: {detail_data.get('assignee_id')}")
                                    else:
                                        print(f"â�Œ Error getting detalles: {detail_response.status}")
    
    except Exception as e:
        print(f"â�Œ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_existing_task_fields())
