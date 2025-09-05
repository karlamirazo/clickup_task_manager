#!/usr/bin/env python3
"""
Test de sincronización con ClickUp y diagnóstico de problemas
"""

import asyncio
import sys
import os

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrations.clickup.client import ClickUpClient
from core.config import settings

async def test_clickup_sync():
    """Probar sincronización con ClickUp"""
    
    print("🔍 TEST DE SINCRONIZACIÓN CON CLICKUP")
    print("=" * 60)
    
    # 1. Verificar configuración
    print("\n📱 CONFIGURACIÓN ACTUAL:")
    print("-" * 40)
    print(f"✅ CLICKUP_API_TOKEN: {'Configurado' if settings.CLICKUP_API_TOKEN else 'NO CONFIGURADO'}")
    print(f"✅ CLICKUP_WORKSPACE_ID: {settings.CLICKUP_WORKSPACE_ID}")
    print(f"✅ CLICKUP_SPACE_ID: {settings.CLICKUP_SPACE_ID}")
    
    if not settings.CLICKUP_API_TOKEN:
        print("❌ ERROR: No hay token de ClickUp configurado")
        return
    
    # 2. Probar conexión con ClickUp
    print("\n🔗 PROBANDO CONEXIÓN CON CLICKUP:")
    print("-" * 40)
    
    try:
        client = ClickUpClient()
        print("✅ Cliente ClickUp creado exitosamente")
        
        # Probar obtener espacios
        print("\n🏢 Probando obtener espacios...")
        spaces = await client.get_spaces(settings.CLICKUP_WORKSPACE_ID)
        print(f"✅ Espacios obtenidos: {len(spaces)} espacios")
        
        # Probar obtener listas del primer espacio
        if spaces:
            first_space = spaces[0]
            print(f"\n📋 Probando obtener listas del espacio: {first_space.get('name', 'Sin nombre')}")
            lists = await client.get_lists(first_space['id'])
            print(f"✅ Listas obtenidas: {len(lists)} listas")
            
            if lists:
                first_list = lists[0]
                print(f"\n📝 Probando obtener tareas de la lista: {first_list.get('name', 'Sin nombre')}")
                tasks = await client.get_tasks(first_list['id'])
                print(f"✅ Tareas obtenidas: {len(tasks)} tareas")
                
                if tasks:
                    first_task = tasks[0]
                    task_id = first_task.get('id')
                    task_name = first_task.get('name', 'Sin nombre')
                    print(f"\n✏️ Probando actualizar tarea: {task_name} (ID: {task_id})")
                    
                    # Probar actualización
                    update_data = {
                        "description": f"Test de sincronización - {datetime.now().strftime('%H:%M:%S')}"
                    }
                    
                    try:
                        result = await client.update_task(task_id, update_data)
                        print(f"✅ Tarea actualizada exitosamente en ClickUp")
                        print(f"📋 Resultado: {result}")
                    except Exception as e:
                        print(f"❌ Error actualizando tarea en ClickUp: {e}")
                        print(f"🔍 Tipo de error: {type(e).__name__}")
                        
                else:
                    print("⚠️ No hay tareas para probar")
            else:
                print("⚠️ No hay listas para probar")
        else:
            print("⚠️ No hay espacios para probar")
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        print(f"🔍 Tipo de error: {type(e).__name__}")

if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(test_clickup_sync())

