#!/usr/bin/env python3
"""
Script para probar diferentes estados y ver cuales acepta ClickUp
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_different_statuses():
    """Test diferentes estados para ver cuales acepta ClickUp"""
    
    print("ğŸ§ª PROBANDO DIFERENTES ESTADOS EN CLICKUP")
    print("=" * 60)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Estados a probar
    statuses_to_test = [
        "to do",
        "in progress", 
        "complete",
        "done",
        "pending",
        "active",
        "working",
        "review",
        "testing"
    ]
    
    successful_statuses = []
    failed_statuses = []
    
    for status in statuses_to_test:
        print(f"\nğŸ”� Probando estado: '{status}'")
        
        # Datos de prueba con estado especifico
        task_data = {
            "name": f"PRUEBA ESTADO - {status} - {datetime.now().strftime('%H:%M:%S')}",
            "description": f"Tarea para probar el estado: {status}",
            "workspace_id": "9014943317",
            "list_id": "901411770471",  # PROYECTO 1
            "status": status,
            "priority": 2,
            "due_date": "2025-08-25",
            "assignees": "88425547",  # Karla Rosas
            "custom_fields": {
                "Email": f"test.{status}@test.com",
                "Celular": "+52 55 9999 9999"
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Create tarea
                async with session.post(
                    f"{base_url}/api/v1/tasks/",
                    json=task_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 201:
                        task_response = json.loads(await response.text())
                        task_id = task_response.get('clickup_id')
                        print(f"   âœ… Tarea creada con estado '{status}' - ID: {task_id}")
                        
                        # Esperar un momento
                        await asyncio.sleep(3)
                        
                        # Verificar el estado en ClickUp
                        try:
                            from core.clickup_client import ClickUpClient
                            client = ClickUpClient()
                            task_details = await client.get_task(task_id)
                            
                            if task_details:
                                actual_status = task_details.get('status', {}).get('status', 'N/A')
                                print(f"   ğŸ“Š Estado en ClickUp: '{actual_status}'")
                                
                                if actual_status.lower() == status.lower():
                                    print(f"   ğŸ�¯ Â¡ESTADO COINCIDE!")
                                    successful_statuses.append(status)
                                else:
                                    print(f"   âš ï¸� Estado NO coincide - Enviado: '{status}', Recibido: '{actual_status}'")
                                    failed_statuses.append((status, actual_status))
                            else:
                                print(f"   â�Œ No se pudo obtener la tarea de ClickUp")
                                failed_statuses.append((status, "Error getting tarea"))
                        
                        except Exception as e:
                            print(f"   â�Œ Error verificando estado: {e}")
                            failed_statuses.append((status, f"Error: {e}"))
                    
                    else:
                        response_text = await response.text()
                        print(f"   â�Œ Error creating tarea: {response.status}")
                        print(f"   ğŸ“„ Respuesta: {response_text}")
                        failed_statuses.append((status, f"HTTP {response.status}"))
        
        except Exception as e:
            print(f"   â�Œ Error general: {e}")
            failed_statuses.append((status, f"Error: {e}"))
    
    # Resumen final
    print(f"\nğŸ“Š RESUMEN DE PRUEBAS DE ESTADOS")
    print("=" * 50)
    print(f"âœ… Estados exitosos ({len(successful_statuses)}):")
    for status in successful_statuses:
        print(f"   ğŸ�¯ {status}")
    
    print(f"\nâ�Œ Estados fallidos ({len(failed_statuses)}):")
    for status, error in failed_statuses:
        print(f"   â�Œ {status}: {error}")
    
    if successful_statuses:
        print(f"\nğŸ�¯ RECOMENDACION: Usar estos estados que funcionan:")
        for status in successful_statuses:
            print(f"   - {status}")
    
    return successful_statuses, failed_statuses

if __name__ == "__main__":
    asyncio.run(test_different_statuses())
