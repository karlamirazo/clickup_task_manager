#!/usr/bin/env python3
"""
Script de emergencia para sincronizar tareas desde ClickUp
Usa el cliente directamente para evitar problemas de cache en Railway
"""

import asyncio
import sys
import os
from datetime import datetime

# Agregar el directorio raiz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.clickup_client import ClickUpClient
from core.database import get_db
from models.task import Task
from sqlalchemy.orm import Session

async def emergency_sync_tasks():
    """Sincronizacion de emergencia de tareas desde ClickUp"""
    
    print("üö® INICIANDO SINCRONIZACION DE EMERGENCIA")
    print("=" * 60)
    
    try:
        # Create cliente de ClickUp
        client = ClickUpClient()
        
        if not client.api_token:
            print("‚ùå ERROR: No hay token de ClickUp configured")
            return False
        
        print(f"‚úÖ Cliente ClickUp creado con token: {client.api_token[:10]}...")
        
        # Get workspaces
        print("üîç Obteniendo workspaces...")
        workspaces = await client.get_workspaces()
        
        if not workspaces:
            print("‚ùå No se encontraron workspaces")
            return False
        
        workspace = workspaces[0]  # Usar el primero
        workspace_id = workspace["id"]
        print(f"‚úÖ Workspace encontrado: {workspace['name']} (ID: {workspace_id})")
        
        # Get espacios
        print("üîç Obteniendo espacios...")
        spaces = await client.get_spaces(workspace_id)
        
        if not spaces:
            print("‚ùå No se encontraron espacios")
            return False
        
        space = spaces[0]  # Usar el primero
        space_id = space["id"]
        print(f"‚úÖ Espacio encontrado: {space['name']} (ID: {space_id})")
        
        # Get listas
        print("üîç Obteniendo listas...")
        lists = await client.get_lists(space_id)
        
        if not lists:
            print("‚ùå No se encontraron listas")
            return False
        
        print(f"‚úÖ {len(lists)} listas encontradas")
        
        # Sync tareas de cada lista
        total_tasks = 0
        for list_info in lists:
            list_id = list_info["id"]
            list_name = list_info["name"]
            
            print(f"üìã Sincronizando lista: {list_name} (ID: {list_id})")
            
            try:
                # Get tareas de la lista
                tasks = await client.get_tasks(list_id)
                
                if not tasks:
                    print(f"   ‚ö†Ô∏è No hay tareas en esta lista")
                    continue
                
                print(f"   üìù {len(tasks)} tareas encontradas")
                
                # Procesar cada tarea
                for task_data in tasks:
                    try:
                        # Verificar si la tarea ya existe
                        existing_task = await check_task_exists(task_data["id"])
                        
                        if existing_task:
                            print(f"      ‚úÖ Tarea ya existe: {task_data['name']}")
                            continue
                        
                        # Create nueva tarea en BD local
                        success = await create_local_task(task_data, workspace_id, list_id)
                        
                        if success:
                            total_tasks += 1
                            print(f"      ‚ûï Nueva tarea creada: {task_data['name']}")
                        else:
                            print(f"      ‚ùå Error creating tarea: {task_data['name']}")
                            
                    except Exception as e:
                        print(f"      ‚ùå Error procesando tarea: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"   ‚ùå Error getting tareas de lista {list_name}: {str(e)}")
                continue
        
        print("=" * 60)
        print(f"üéâ SINCRONIZACION COMPLETADA")
        print(f"   üìä Total de tareas sincronizadas: {total_tasks}")
        print(f"   ‚è∞ Timestamp: {datetime.now().isoformat()}")
        
        return True
        
    except Exception as e:
        print(f"‚ùå ERROR CRITICO: {str(e)}")
        import traceback
        print(f"‚ùå Traceback: {traceback.format_exc()}")
        return False

async def check_task_exists(clickup_id: str) -> bool:
    """Verificar si una tarea ya existe en la BD local"""
    try:
        from core.database import get_db
        db = next(get_db())
        
        existing = db.query(Task).filter(Task.clickup_id == clickup_id).first()
        return existing is not None
        
    except Exception:
        return False

async def create_local_task(task_data: dict, workspace_id: str, list_id: str) -> bool:
    """Create una tarea en la BD local"""
    try:
        from core.database import get_db
        db = next(get_db())
        
        # Extraer priority como entero
        priority_data = task_data.get("priority", {})
        if isinstance(priority_data, dict):
            priority_value = int(priority_data.get("id", 3))
        else:
            priority_value = int(priority_data) if priority_data else 3
        
        # Create nueva tarea
        new_task = Task(
            clickup_id=task_data["id"],
            name=task_data.get("name", "Sin nombre"),
            description=task_data.get("description", ""),
            status=task_data.get("status", {}).get("status", "to_do"),
            priority=priority_value,
            due_date=parse_timestamp(task_data.get("due_date")),
            workspace_id=workspace_id,
            list_id=list_id,
            assignee_id=task_data.get("assignees", [{}])[0].get("id") if task_data.get("assignees") else None,
            creator_id=task_data.get("creator", {}).get("id", "system"),
            custom_fields=task_data.get("custom_fields", []),
            is_synced=True,
            last_sync=datetime.utcnow()
        )
        
        db.add(new_task)
        db.commit()
        
        return True
        
    except Exception as e:
        print(f"      ‚ùå Error en BD: {str(e)}")
        return False

def parse_timestamp(timestamp_value):
    """Parsear timestamp de forma segura"""
    if timestamp_value is None:
        return None
    
    try:
        if isinstance(timestamp_value, str):
            if timestamp_value.isdigit():
                timestamp_value = int(timestamp_value)
            else:
                return None
        
        if isinstance(timestamp_value, (int, float)):
            return datetime.fromtimestamp(timestamp_value)
        
        return None
    except Exception:
        return None

async def main():
    """Funcion principal"""
    print("üöÄ Script de Sincronizacion de Emergencia")
    print("   ClickUp Task Manager - Railway Deployment")
    print("=" * 60)
    
    success = await emergency_sync_tasks()
    
    if success:
        print("\n‚úÖ Sincronizacion completada exitosamente")
        print("üîç Verifica las tareas en la interfaz web")
    else:
        print("\n‚ùå Sincronizacion fallo")
        print("üîç Revisa los errores arriba")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
