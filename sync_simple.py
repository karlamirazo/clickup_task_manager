#!/usr/bin/env python3
"""
Script simple para sincronizar tareas desde ClickUp
"""

import asyncio
import sys
import os
from datetime import datetime

# Configurar encoding para Windows
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

# Importar módulos del proyecto
sys.path.append('.')

async def sync_tasks():
    """Sincronizar tareas desde ClickUp"""
    
    print("Iniciando sincronizacion de tareas...")
    
    try:
        from core.database import get_db
        from models.task import Task
        from integrations.clickup.client import ClickUpClient
        from sqlalchemy import func
        
        # Obtener sesión de base de datos
        db = next(get_db())
        
        # Contar tareas antes
        tasks_before = db.query(Task).count()
        print(f"Tareas en BD antes: {tasks_before}")
        
        # Cliente ClickUp
        clickup_client = ClickUpClient()
        
        # Obtener workspaces
        print("Obteniendo workspaces...")
        workspaces = await clickup_client.get_workspaces()
        
        if not workspaces:
            print("No se encontraron workspaces")
            return
        
        workspace_id = workspaces[0]["id"]
        workspace_name = workspaces[0]["name"]
        print(f"Workspace: {workspace_name} (ID: {workspace_id})")
        
        # Obtener espacios
        print("Obteniendo espacios...")
        spaces = await clickup_client.get_spaces(workspace_id)
        
        total_created = 0
        total_updated = 0
        
        for space in spaces:
            space_id = space["id"]
            space_name = space["name"]
            print(f"Procesando espacio: {space_name}")
            
            # Obtener listas del espacio
            try:
                lists = await clickup_client.get_lists(space_id)
                
                for list_item in lists:
                    list_id = list_item["id"]
                    list_name = list_item["name"]
                    print(f"  Lista: {list_name}")
                    
                    # Obtener tareas
                    tasks = await clickup_client.get_tasks(list_id)
                    print(f"    Encontradas {len(tasks)} tareas")
                    
                    for task_data in tasks:
                        task_id = task_data["id"]
                        task_name = task_data.get("name", "Sin nombre")
                        task_status = task_data.get("status", {}).get("status", "sin estado")
                        
                        # Verificar si existe
                        existing_task = db.query(Task).filter(Task.clickup_id == task_id).first()
                        
                        if existing_task:
                            # Actualizar
                            existing_task.name = task_name
                            existing_task.status = task_status
                            existing_task.last_sync = datetime.now()
                            
                            # Fecha de vencimiento
                            if task_data.get("due_date"):
                                try:
                                    existing_task.due_date = datetime.fromtimestamp(int(task_data["due_date"]) / 1000)
                                except:
                                    pass
                            
                            total_updated += 1
                            print(f"    Actualizada: {task_name[:40]}...")
                        else:
                            # Crear nueva
                            new_task = Task(
                                clickup_id=task_id,
                                name=task_name,
                                status=task_status,
                                list_id=list_id,
                                workspace_id=workspace_id,
                                last_sync=datetime.now()
                            )
                            
                            # Fecha de vencimiento
                            if task_data.get("due_date"):
                                try:
                                    new_task.due_date = datetime.fromtimestamp(int(task_data["due_date"]) / 1000)
                                except:
                                    pass
                            
                            db.add(new_task)
                            total_created += 1
                            print(f"    Creada: {task_name[:40]}...")
            
            except Exception as e:
                print(f"  Error procesando espacio {space_name}: {e}")
                continue
        
        # Guardar cambios
        print("Guardando cambios...")
        db.commit()
        
        # Contar después
        tasks_after = db.query(Task).count()
        
        # Estados
        by_status = db.query(
            Task.status,
            func.count().label('count')
        ).group_by(Task.status).all()
        
        print(f"\nSINCRONIZACION COMPLETADA")
        print(f"Tareas antes: {tasks_before}")
        print(f"Tareas despues: {tasks_after}")
        print(f"Creadas: {total_created}")
        print(f"Actualizadas: {total_updated}")
        
        print(f"\nDISTRIBUCION POR ESTADO:")
        for item in by_status:
            print(f"  {item.status}: {item.count}")
        
        return {
            "before": tasks_before,
            "after": tasks_after,
            "created": total_created,
            "updated": total_updated
        }
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    result = asyncio.run(sync_tasks())
    if result:
        print(f"\nExito: {result}")
    else:
        print(f"\nFallo en sincronizacion")
