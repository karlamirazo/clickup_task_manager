#!/usr/bin/env python3
"""
Script para probar especificamente el metodo update_task
"""

import asyncio
import os
import sys
from datetime import datetime

# Agregar el directorio raiz al path para importar modulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.clickup_client import ClickUpClient

async def test_update_task_method():
    """Test especificamente el metodo update_task"""
    
    print("ğŸ§ª PROBANDO METODO UPDATE_TASK")
    print("=" * 50)
    
    # ID de la tarea que acabamos de crear
    task_id = "86b6afv2e"  # ID de la nueva tarea
    
    try:
        # Inicializar cliente ClickUp
        client = ClickUpClient()
        
        print(f"ğŸ“‹ Tarea a actualizar: {task_id}")
        
        # 1. Test actualizacion de estado
        print(f"\nğŸ“Š Probando actualizacion de estado...")
        try:
            result = await client.update_task(task_id, {"status": "in progress"})
            print(f"âœ… Estado actualizado exitosamente")
            print(f"ğŸ“„ Respuesta: {result}")
        except Exception as e:
            print(f"â�Œ Error updating estado: {e}")
        
        # Esperar un momento
        await asyncio.sleep(3)
        
        # 2. Test actualizacion de prioridad
        print(f"\nâš¡ Probando actualizacion de prioridad...")
        try:
            result = await client.update_task(task_id, {"priority": 1})
            print(f"âœ… Prioridad actualizada exitosamente")
            print(f"ğŸ“„ Respuesta: {result}")
        except Exception as e:
            print(f"â�Œ Error updating prioridad: {e}")
        
        # Esperar un momento
        await asyncio.sleep(3)
        
        # 3. Verificar el resultado
        print(f"\nğŸ”� Verificando resultado...")
        task_details = await client.get_task(task_id)
        
        if task_details:
            print(f"âœ… Tarea encontrada en ClickUp:")
            print(f"   ğŸ“� Nombre: {task_details.get('name')}")
            print(f"   ğŸ“Š Estado: {task_details.get('status', {}).get('status', 'N/A')}")
            print(f"   âš¡ Prioridad: {task_details.get('priority', 'N/A')}")
            print(f"   ğŸ‘¤ Asignado: {task_details.get('assignees', [])}")
            
            # Verificar si los campos se actualizaron
            actual_status = task_details.get('status', {}).get('status', 'N/A')
            actual_priority = task_details.get('priority', 'N/A')
            
            if actual_status == "in progress":
                print(f"   ğŸ�¯ Estado actualizado correctamente: {actual_status}")
            else:
                print(f"   â�Œ Estado NO se actualizo. Actual: {actual_status}")
            
            if actual_priority == 1:
                print(f"   ğŸ�¯ Prioridad actualizada correctamente: {actual_priority}")
            else:
                print(f"   â�Œ Prioridad NO se actualizo. Actual: {actual_priority}")
        
        else:
            print(f"â�Œ No se pudo obtener la tarea")
    
    except Exception as e:
        print(f"â�Œ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_update_task_method())
