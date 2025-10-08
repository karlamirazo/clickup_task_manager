#!/usr/bin/env python3
"""
Script para sincronizar tareas faltantes de ClickUp a la base de datos
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def sync_missing_tasks():
    """Sincronizar tareas faltantes de ClickUp"""
    
    try:
        # Importar servicios necesarios
        from integrations.clickup.client import ClickUpClient
        from core.database import get_db
        from models.task import Task
        
        print("INICIANDO SINCRONIZACION DE TAREAS FALTANTES...")
        print("=" * 60)
        
        # Obtener sesión de base de datos
        db = next(get_db())
        
        # Inicializar cliente de ClickUp
        clickup_client = ClickUpClient()
        
        # Obtener todas las tareas de ClickUp
        print("1. Obteniendo tareas de ClickUp...")
        
        # Obtener workspaces
        workspaces = await clickup_client.get_workspaces()
        if not workspaces:
            print("ERROR: No se encontraron workspaces")
            return
        
        workspace_id = workspaces[0]['id']
        print(f"   Usando workspace: {workspace_id}")
        
        # Obtener spaces
        spaces = await clickup_client.get_spaces(workspace_id)
        if not spaces:
            print("ERROR: No se encontraron spaces")
            return
        
        total_synced = 0
        total_new = 0
        
        for space in spaces:
            space_id = space['id']
            space_name = space['name']
            print(f"\n2. Procesando space: {space_name} ({space_id})")
            
            # Obtener folders
            folders = await clickup_client.get_folders(space_id)
            
            for folder in folders:
                folder_id = folder['id']
                folder_name = folder['name']
                print(f"   Procesando folder: {folder_name}")
                
                # Obtener lists
                lists = await clickup_client.get_lists(folder_id)
                
                for list_item in lists:
                    list_id = list_item['id']
                    list_name = list_item['name']
                    print(f"     Procesando list: {list_name}")
                    
                    # Obtener tareas
                    tasks = await clickup_client.get_tasks(list_id, include_closed=True)
                    
                    for task_data in tasks:
                        task_id = task_data['id']
                        
                        # Verificar si la tarea ya existe en BD
                        existing_task = db.query(Task).filter(Task.clickup_id == task_id).first()
                        
                        if not existing_task:
                            print(f"       NUEVA TAREA: {task_data['name'][:50]}...")
                            
                            # Crear nueva tarea
                            new_task = Task(
                                clickup_id=task_id,
                                name=task_data['name'],
                                description=task_data.get('description', ''),
                                status=task_data['status']['status'].lower(),
                                priority=task_data.get('priority', {}).get('priority', 'normal').lower() if task_data.get('priority') else 'normal',
                                due_date=None,  # Se puede agregar lógica para parsear fecha
                                assignee_id=None,  # Se puede agregar lógica para asignar usuario
                                workspace_id=workspace_id,
                                space_id=space_id,
                                folder_id=folder_id,
                                list_id=list_id
                            )
                            
                            db.add(new_task)
                            total_new += 1
                        else:
                            # Actualizar tarea existente
                            existing_task.name = task_data['name']
                            existing_task.status = task_data['status']['status'].lower()
                            existing_task.description = task_data.get('description', '')
                            if task_data.get('priority'):
                                existing_task.priority = task_data['priority']['priority'].lower()
                        
                        total_synced += 1
        
        # Guardar cambios
        db.commit()
        
        print("\n" + "=" * 60)
        print("SINCRONIZACION COMPLETADA")
        print(f"Total tareas procesadas: {total_synced}")
        print(f"Tareas nuevas agregadas: {total_new}")
        
        # Verificar conteos finales
        print("\nCONTEOS FINALES EN BASE DE DATOS:")
        
        from sqlalchemy import text
        result = db.execute(text("""
            SELECT status, COUNT(*) as count 
            FROM tasks 
            GROUP BY status 
            ORDER BY count DESC
        """))
        
        total_tasks = 0
        for row in result:
            print(f"   {row.status}: {row.count}")
            total_tasks += row.count
        
        print(f"\nTOTAL DE TAREAS: {total_tasks}")
        
        db.close()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(sync_missing_tasks())
