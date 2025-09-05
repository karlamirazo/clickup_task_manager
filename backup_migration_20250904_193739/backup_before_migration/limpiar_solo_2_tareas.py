#!/usr/bin/env python3
"""
Script para limpiar la base de datos y dejar SOLO las 2 tareas ABIERTAS
que realmente existen en ClickUp
"""
import asyncio

async def limpiar_solo_2_tareas():
    """Limpiar base de datos para que solo tenga las 2 tareas abiertas"""
    try:
        from core.clickup_client import ClickUpClient
        from core.database import get_db
        from models.task import Task
        
        print("🧹 LIMPIANDO BASE DE DATOS - SOLO 2 TAREAS ABIERTAS")
        print("=" * 60)
        
        # 1. Obtener SOLO tareas ABIERTAS de ClickUp
        client = ClickUpClient()
        workspace_id = "9014943317"
        
        spaces = await client.get_spaces(workspace_id)
        real_task_ids = set()
        
        for space in spaces:
            space_id = space["id"]
            space_name = space.get("name", "Sin nombre")
            print(f"📁 Verificando espacio: {space_name}")
            
            lists = await client.get_lists(space_id)
            for list_item in lists:
                list_id = list_item["id"]
                list_name = list_item.get("name", "Sin nombre")
                
                # SOLO tareas ABIERTAS
                tasks = await client.get_tasks(
                    list_id=list_id,
                    include_closed=False,  # SOLO ABIERTAS
                    page=0,
                    limit=100
                )
                
                for task in tasks:
                    real_task_ids.add(task.get('id'))
                    print(f"   ✅ Tarea ABIERTA: {task.get('name')} (ID: {task.get('id')})")
        
        print(f"\n📊 Total tareas ABIERTAS en ClickUp: {len(real_task_ids)}")
        print(f"🆔 IDs reales: {real_task_ids}")
        
        # 2. Limpiar base de datos local
        print("\n🗄️ Limpiando base de datos local...")
        db = next(get_db())
        
        # Obtener todas las tareas locales
        local_tasks = db.query(Task).all()
        print(f"📋 Tareas en base de datos local: {len(local_tasks)}")
        
        # Eliminar tareas que NO existen en ClickUp (incluyendo cerradas)
        deleted_count = 0
        for local_task in local_tasks:
            if local_task.clickup_id not in real_task_ids:
                print(f"   🗑️ Eliminando tarea obsoleta: {local_task.name} (ID: {local_task.clickup_id})")
                db.delete(local_task)
                deleted_count += 1
        
        # Confirmar cambios
        db.commit()
        
        print(f"\n✅ LIMPIEZA COMPLETADA:")
        print(f"   🗑️ Tareas eliminadas: {deleted_count}")
        print(f"   📊 Tareas restantes: {len(local_tasks) - deleted_count}")
        
        # 3. Verificar resultado final
        final_count = db.query(Task).count()
        print(f"\n🎯 VERIFICACIÓN FINAL:")
        print(f"   ClickUp: {len(real_task_ids)} tareas ABIERTAS")
        print(f"   Local:   {final_count} tareas")
        
        if final_count == len(real_task_ids):
            print("   ✅ BASE DE DATOS PERFECTAMENTE SINCRONIZADA")
            print("   🎯 AHORA SOLO TENDRÁS LAS 2 TAREAS QUE REALMENTE VES")
        else:
            print(f"   ❌ AÚN HAY {final_count - len(real_task_ids)} TAREAS DE MÁS")
        
        return final_count
        
    except Exception as e:
        print(f"❌ Error durante limpieza: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    print("🧹 INICIANDO LIMPIEZA PARA SOLO 2 TAREAS...")
    print()
    
    final_count = asyncio.run(limpiar_solo_2_tareas())
    
    print(f"\n🎯 RESULTADO FINAL: {final_count} tareas en base de datos")
