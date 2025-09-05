#!/usr/bin/env python3
"""
Script para probar creacion simple de tareas y verificar actualizacion post-creacion
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_simple_task_creation():
    """Test creacion simple de tareas"""
    
    print("ğŸ§ª PROBANDO CREACION SIMPLE DE TAREAS")
    print("=" * 50)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Datos de prueba SIMPLES
    task_data = {
        "name": f"TAREA SIMPLE - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Tarea simple para probar actualizacion post-creacion",
        "workspace_id": "9014943317",
        "list_id": "901411770471",  # PROYECTO 1
        "status": "in progress",  # Deberia mapearse a "en curso"
        "priority": 2,  # Prioridad media
        "assignees": "88425547",  # Karla Rosas
        "custom_fields": {
            "Email": "simple@test.com",
            "Celular": "+52 55 1111 1111"
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("ğŸ“¤ Creando tarea simple...")
            print(f"ğŸ“‹ Datos: {task_data['name']}")
            print(f"   ğŸ“Š Estado: {task_data['status']} (deberia mapearse a 'en curso')")
            print(f"   âš¡ Prioridad: {task_data['priority']}")
            print(f"   ğŸ“§ Email: {task_data['custom_fields']['Email']}")
            
            # Create tarea
            async with session.post(
                f"{base_url}/api/v1/tasks/",
                json=task_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"\nğŸ“¡ Status de creacion: {response.status}")
                response_text = await response.text()
                print(f"ğŸ“„ Respuesta: {response_text}")
                
                if response.status == 201:
                    task_response = json.loads(response_text)
                    task_id = task_response.get('clickup_id')
                    print(f"\nâœ… Tarea creada exitosamente!")
                    print(f"   ğŸ†” ClickUp ID: {task_id}")
                    
                    # Esperar para que se procese la actualizacion post-creacion
                    print(f"\nâ�³ Esperando 10 segundos para actualizacion post-creacion...")
                    await asyncio.sleep(10)
                    
                    print(f"\nğŸ�¯ INSTRUCCIONES PARA VERIFICAR:")
                    print(f"1. Ve a ClickUp y busca la tarea: '{task_data['name']}'")
                    print(f"2. Verifica que el ESTADO sea: 'en curso' (NO 'pendiente')")
                    print(f"3. Verifica que la PRIORIDAD sea: {task_data['priority']}")
                    print(f"4. Verifica que el campo 'Email' muestre: {task_data['custom_fields']['Email']}")
                    print(f"5. Verifica que el campo 'Celular' muestre: {task_data['custom_fields']['Celular']}")
                    
                    return task_id
                    
                else:
                    print(f"â�Œ Error creating tarea: {response.status}")
                    print(f"ğŸ“„ Respuesta: {response_text}")
                    return None
    
    except Exception as e:
        print(f"â�Œ Error: {e}")
        return None

if __name__ == "__main__":
    task_id = asyncio.run(test_simple_task_creation())
    if task_id:
        print(f"\nğŸ”� Para verificar en ClickUp, usa el ID: {task_id}")
        print(f"ğŸ“‹ Puedes usar: python scripts/verify_clickup_task.py")
        print(f"   (Recuerda actualizar el task_id en el script)")
