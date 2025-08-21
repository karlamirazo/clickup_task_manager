#!/usr/bin/env python3
"""
Script para probar especificamente la funcionalidad de actualizacion post-creacion
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_post_creation_update():
    """Test especificamente la funcionalidad de actualizacion post-creacion"""
    
    print("ğŸ§ª PROBANDO ACTUALIZACION POST-CREACION")
    print("=" * 60)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Datos de prueba especificos para probar la actualizacion
    task_data = {
        "name": f"PRUEBA POST-CREACION - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Tarea especifica para probar actualizacion post-creacion",
        "workspace_id": "9014943317",
        "list_id": "901411770471",  # PROYECTO 1
        "status": "in progress",  # Deberia mapearse a "en curso"
        "priority": 1,  # Prioridad alta (diferente de 3)
        "assignees": "88425547",  # Karla Rosas
        "custom_fields": {
            "Email": "post.creacion@test.com",
            "Celular": "+52 55 9999 9999"
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("ğŸ“¤ Creando tarea para probar actualizacion post-creacion...")
            print(f"ğŸ“‹ Datos de prueba:")
            print(f"   ğŸ“� Nombre: {task_data['name']}")
            print(f"   ğŸ“Š Estado: {task_data['status']} (deberia mapearse a 'en curso')")
            print(f"   âš¡ Prioridad: {task_data['priority']} (diferente de 3)")
            print(f"   ğŸ“§ Email: {task_data['custom_fields']['Email']}")
            print(f"   ğŸ“± Celular: {task_data['custom_fields']['Celular']}")
            
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
                    print(f"\nâ�³ Esperando 15 segundos para actualizacion post-creacion...")
                    await asyncio.sleep(15)
                    
                    print(f"\nğŸ”� Verificando resultado de actualizacion post-creacion...")
                    print(f"ğŸ�¯ INSTRUCCIONES PARA VERIFICAR EN CLICKUP:")
                    print(f"1. Ve a ClickUp y busca la tarea: '{task_data['name']}'")
                    print(f"2. Verifica que el ESTADO sea: 'en curso' (NO 'pendiente')")
                    print(f"3. Verifica que la PRIORIDAD sea: {task_data['priority']}")
                    print(f"4. Verifica que el campo 'Email' muestre: {task_data['custom_fields']['Email']}")
                    print(f"5. Verifica que el campo 'Celular' muestre: {task_data['custom_fields']['Celular']}")
                    
                    print(f"\nğŸ“‹ Para verificar programaticamente, usa:")
                    print(f"   python scripts/verify_clickup_task.py")
                    print(f"   (Recuerda actualizar el task_id a: {task_id})")
                    
                    return task_id
                    
                else:
                    print(f"â�Œ Error creating tarea: {response.status}")
                    print(f"ğŸ“„ Respuesta: {response_text}")
                    return None
    
    except Exception as e:
        print(f"â�Œ Error: {e}")
        return None

if __name__ == "__main__":
    task_id = asyncio.run(test_post_creation_update())
    if task_id:
        print(f"\nğŸ”� Para verificar en ClickUp, usa el ID: {task_id}")
        print(f"ğŸ“‹ Puedes usar: python scripts/verify_clickup_task.py")
        print(f"   (Recuerda actualizar el task_id en el script)")
