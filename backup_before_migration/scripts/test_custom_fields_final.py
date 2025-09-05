#!/usr/bin/env python3
"""
Script final para probar campos personalizados Email y Celular
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_custom_fields_final():
    """Test campos personalizados con datos especificos"""
    
    print("ğŸ§ª PRUEBA FINAL DE CAMPOS PERSONALIZADOS")
    print("=" * 60)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Datos de prueba con campos personalizados especificos
    task_data = {
        "name": f"PRUEBA FINAL - Email y Celular - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Esta tarea debe mostrar los campos Email y Celular en ClickUp",
        "workspace_id": "9014943317",
        "list_id": "901411770471",  # PROYECTO 1
        "status": "in progress",
        "priority": 1,
        "due_date": "2025-08-25",
        "assignees": "88425547",  # Karla Rosas
        "custom_fields": {
            "Email": "karla.rosas@empresa.com",
            "Celular": "+52 55 1234 5678"
        }
    }
    
    print(f"ğŸ“‹ Datos de la tarea:")
    print(f"   ğŸ“� Nombre: {task_data['name']}")
    print(f"   ğŸ“„ Descripcion: {task_data['description']}")
    print(f"   ğŸ“Š Estado: {task_data['status']}")
    print(f"   âš¡ Prioridad: {task_data['priority']}")
    print(f"   ğŸ“… Fecha limite: {task_data['due_date']}")
    print(f"   ğŸ‘¤ Usuario asignado: {task_data['assignees']}")
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
                
                if response.status == 201:
                    response_data = json.loads(response_text)
                    task_id = response_data.get("id")
                    clickup_id = response_data.get("clickup_id")
                    
                    print(f"âœ… Â¡TAREA CREADA EXITOSAMENTE!")
                    print(f"   ğŸ†” ID Local: {task_id}")
                    print(f"   ğŸ†” ID ClickUp: {clickup_id}")
                    print(f"   ğŸ“� Nombre: {response_data.get('name')}")
                    print(f"   ğŸ“§ Campos personalizados guardados: {response_data.get('custom_fields')}")
                    
                    print(f"\nğŸ�¯ INSTRUCCIONES PARA VERIFICAR EN CLICKUP:")
                    print(f"   1. Ve a ClickUp y busca la tarea: '{response_data.get('name')}'")
                    print(f"   2. Verifica que aparezcan los campos personalizados:")
                    print(f"      ğŸ“§ Email: {task_data['custom_fields']['Email']}")
                    print(f"      ğŸ“± Celular: {task_data['custom_fields']['Celular']}")
                    print(f"   3. Verifica que el estado sea: {task_data['status']}")
                    print(f"   4. Verifica que el usuario asignado sea: Karla Rosas")
                    print(f"   5. Verifica que la prioridad sea: {task_data['priority']}")
                    
                    print(f"\nğŸ”— Enlaces utiles:")
                    print(f"   ğŸ“‹ Lista: PROYECTO 1 (ID: {task_data['list_id']})")
                    print(f"   ğŸ‘¤ Usuario: Karla Rosas (ID: {task_data['assignees']})")
                    print(f"   ğŸ“� Workspace: 9014943317")
                    
                else:
                    print(f"â�Œ Error creating tarea: {response.status}")
                    print(f"ğŸ“„ Detalles: {response_text}")
    
    except Exception as e:
        print(f"â�Œ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_custom_fields_final())
