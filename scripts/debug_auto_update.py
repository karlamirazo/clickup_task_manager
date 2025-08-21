#!/usr/bin/env python3
"""
Script para debuggear la actualizacion automatica de campos personalizados
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def debug_auto_update():
    """Debuggear la actualizacion automatica"""
    
    print("üîç DEBUGGEANDO ACTUALIZACION AUTOMATICA")
    print("=" * 50)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Datos de prueba con campos personalizados
    task_data = {
        "name": f"DEBUG AUTO UPDATE - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Debug de actualizacion automatica",
        "workspace_id": "9014943317",
        "list_id": "901411770471",  # PROYECTO 1
        "status": "in progress",
        "priority": 1,
        "due_date": "2025-08-25",
        "assignees": "88425547",
        "custom_fields": {
            "Email": "debug@test.com",
            "Celular": "+52 55 1111 1111"
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("üì§ Creando tarea para debug...")
            print(f"üìã Datos: {json.dumps(task_data, indent=2)}")
            
            # Create tarea
            async with session.post(
                f"{base_url}/api/v1/tasks/",
                json=task_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"üì° Status: {response.status}")
                response_text = await response.text()
                print(f"üìÑ Respuesta: {response_text}")
                
                if response.status == 201:
                    task_response = json.loads(response_text)
                    task_id = task_response.get('clickup_id')
                    print(f"‚úÖ Tarea creada con ID: {task_id}")
                    
                    # Esperar un momento
                    print(f"\n‚è≥ Esperando 3 segundos...")
                    await asyncio.sleep(3)
                    
                    # Verificar campos personalizados en ClickUp
                    print(f"\nüîç Verificando campos personalizados en ClickUp...")
                    
                    # Usar el cliente ClickUp directamente
                    import os
                    import sys
                    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    from core.clickup_client import ClickUpClient
                    
                    client = ClickUpClient()
                    task_details = await client.get_task(task_id)
                    
                    if task_details:
                        custom_fields = task_details.get('custom_fields', [])
                        print(f"üìß Campos personalizados encontrados: {len(custom_fields)}")
                        
                        for field in custom_fields:
                            field_name = field.get('name')
                            field_value = field.get('value')
                            print(f"   üìß {field_name}: {field_value}")
                        
                        # Verificar si los campos estan vacios
                        email_field = next((f for f in custom_fields if f.get('name') == 'Email'), None)
                        celular_field = next((f for f in custom_fields if f.get('name') == 'Celular'), None)
                        
                        if email_field and email_field.get('value') is None:
                            print(f"\n‚ùå Campo Email esta vacio - La actualizacion automatica no funciono")
                        else:
                            print(f"\n‚úÖ Campo Email tiene valor: {email_field.get('value') if email_field else 'No encontrado'}")
                        
                        if celular_field and celular_field.get('value') is None:
                            print(f"‚ùå Campo Celular esta vacio - La actualizacion automatica no funciono")
                        else:
                            print(f"‚úÖ Campo Celular tiene valor: {celular_field.get('value') if celular_field else 'No encontrado'}")
                    
                else:
                    print(f"‚ùå Error creating tarea: {response.status}")
    
    except Exception as e:
        print(f"‚ùå Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_auto_update())
