#!/usr/bin/env python3
"""
Script para probar específicamente el método update_task
"""

import asyncio
import os
import sys
from datetime import datetime

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.clickup_client import ClickUpClient

async def test_update_task_method():
    """Probar específicamente el método update_task"""
    
    print("🧪 PROBANDO MÉTODO UPDATE_TASK")
    print("=" * 50)
    
    # ID de la tarea que acabamos de crear
    task_id = "86b6afv2e"  # ID de la nueva tarea
    
    try:
        # Inicializar cliente ClickUp
        client = ClickUpClient()
        
        print(f"📋 Tarea a actualizar: {task_id}")
        
        # 1. Probar actualización de estado
        print(f"\n📊 Probando actualización de estado...")
        try:
            result = await client.update_task(task_id, {"status": "in progress"})
            print(f"✅ Estado actualizado exitosamente")
            print(f"📄 Respuesta: {result}")
        except Exception as e:
            print(f"❌ Error actualizando estado: {e}")
        
        # Esperar un momento
        await asyncio.sleep(3)
        
        # 2. Probar actualización de prioridad
        print(f"\n⚡ Probando actualización de prioridad...")
        try:
            result = await client.update_task(task_id, {"priority": 1})
            print(f"✅ Prioridad actualizada exitosamente")
            print(f"📄 Respuesta: {result}")
        except Exception as e:
            print(f"❌ Error actualizando prioridad: {e}")
        
        # Esperar un momento
        await asyncio.sleep(3)
        
        # 3. Verificar el resultado
        print(f"\n🔍 Verificando resultado...")
        task_details = await client.get_task(task_id)
        
        if task_details:
            print(f"✅ Tarea encontrada en ClickUp:")
            print(f"   📝 Nombre: {task_details.get('name')}")
            print(f"   📊 Estado: {task_details.get('status', {}).get('status', 'N/A')}")
            print(f"   ⚡ Prioridad: {task_details.get('priority', 'N/A')}")
            print(f"   👤 Asignado: {task_details.get('assignees', [])}")
            
            # Verificar si los campos se actualizaron
            actual_status = task_details.get('status', {}).get('status', 'N/A')
            actual_priority = task_details.get('priority', 'N/A')
            
            if actual_status == "in progress":
                print(f"   🎯 Estado actualizado correctamente: {actual_status}")
            else:
                print(f"   ❌ Estado NO se actualizó. Actual: {actual_status}")
            
            if actual_priority == 1:
                print(f"   🎯 Prioridad actualizada correctamente: {actual_priority}")
            else:
                print(f"   ❌ Prioridad NO se actualizó. Actual: {actual_priority}")
        
        else:
            print(f"❌ No se pudo obtener la tarea")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_update_task_method())
