#!/usr/bin/env python3
"""
Script MUY SIMPLE para ver EXACTAMENTE qué tareas hay en ClickUp
"""
import asyncio

async def ver_tareas_reales():
    """Ver EXACTAMENTE qué tareas hay en ClickUp"""
    try:
        from core.clickup_client import ClickUpClient
        
        client = ClickUpClient()
        workspace_id = "9014943317"
        
        print("🔍 VERIFICANDO TAREAS REALES EN CLICKUP")
        print("=" * 50)
        
        # Obtener espacios
        spaces = await client.get_spaces(workspace_id)
        print(f"📁 Espacios encontrados: {len(spaces)}")
        
        total_tareas = 0
        
        for space in spaces:
            space_id = space["id"]
            space_name = space.get("name", "Sin nombre")
            print(f"\n📁 ESPACIO: {space_name}")
            
            # Obtener listas
            lists = await client.get_lists(space_id)
            print(f"   📋 Listas: {len(lists)}")
            
            for list_item in lists:
                list_id = list_item["id"]
                list_name = list_item.get("name", "Sin nombre")
                
                print(f"\n      📝 LISTA: {list_name}")
                
                # Obtener tareas SIN FILTROS
                tasks = await client.get_tasks(
                    list_id=list_id,
                    include_closed=True,  # TODAS las tareas
                    page=0,
                    limit=100
                )
                
                task_count = len(tasks)
                total_tareas += task_count
                
                print(f"         📊 Total tareas: {task_count}")
                
                # Mostrar TODAS las tareas con su estado
                if task_count > 0:
                    for i, task in enumerate(tasks, 1):
                        task_name = task.get('name', 'Sin nombre')
                        status = task.get('status', {})
                        status_name = status.get('status', 'N/A') if isinstance(status, dict) else str(status)
                        
                        print(f"            {i}. {task_name}")
                        print(f"               Status: {status_name}")
                        print(f"               ID: {task.get('id', 'N/A')}")
                        
                        # Verificar si está cerrada
                        if status_name in ['complete', 'done', 'closed']:
                            print(f"               ⚠️ ESTA TAREA ESTÁ CERRADA")
                        else:
                            print(f"               ✅ ESTA TAREA ESTÁ ABIERTA")
                        print()
                else:
                    print("         ⚠️ NO HAY TAREAS EN ESTA LISTA")
        
        print(f"\n🎯 RESUMEN FINAL:")
        print(f"   Total tareas encontradas: {total_tareas}")
        print(f"   Si solo ves 2, entonces hay {total_tareas - 2} tareas CERRADAS que no se ven")
        
        return total_tareas
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    print("🚀 Verificando tareas REALES en ClickUp...")
    print()
    
    total = asyncio.run(ver_tareas_reales())
    
    print(f"\n🎯 RESULTADO: {total} tareas encontradas en total")
