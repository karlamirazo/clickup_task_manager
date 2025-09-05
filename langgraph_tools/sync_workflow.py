#!/usr/bin/env python3
"""
Workflow de LangGraph para sincronización de tareas con ClickUp
Integra manejo de errores y logging automático
"""

from langgraph.graph import StateGraph, END
from typing import Dict, Any, TypedDict, List
import os
import sys
import asyncio
from datetime import datetime

# Agregar el directorio raiz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.clickup.client import ClickUpClient
from core.database import get_db
from models.task import Task
from utils.deployment_logger import log_error_sync

# Estado del workflow de sincronización
class SyncWorkflowState(TypedDict):
    """Estado del workflow de sincronización"""
    workspace_id: str
    sync_status: str
    total_tasks_synced: int
    total_tasks_created: int
    total_tasks_updated: int
    errors: List[str]
    start_time: str
    end_time: str
    logging_result: Dict[str, Any]

# Nodo de inicio de sincronización
def start_sync(state: SyncWorkflowState) -> SyncWorkflowState:
    """Iniciar el proceso de sincronización"""
    print(f"🔄 Iniciando sincronización para workspace: {state['workspace_id']}")
    state['start_time'] = datetime.now().isoformat()
    state['sync_status'] = 'running'
    state['total_tasks_synced'] = 0
    state['total_tasks_created'] = 0
    state['total_tasks_updated'] = 0
    state['errors'] = []
    
    return state

# Nodo de sincronización principal
async def sync_tasks(state: SyncWorkflowState) -> SyncWorkflowState:
    """Ejecutar la sincronización de tareas"""
    try:
        print("🔄 Ejecutando sincronización de tareas...")
        
        # Validar que tenemos un workspace_id válido
        if not state['workspace_id'] or state['workspace_id'].strip() == '':
            # Intentar obtener un workspace por defecto
            try:
                clickup_client = ClickUpClient()
                workspaces = await clickup_client.get_workspaces()
                if workspaces and len(workspaces) > 0:
                    state['workspace_id'] = workspaces[0]["id"]
                    print(f"🔄 Usando workspace por defecto: {state['workspace_id']}")
                else:
                    # Fallback al workspace ID hardcodeado
                    state['workspace_id'] = "9014943317"
                    print(f"🔄 Usando workspace ID hardcodeado: {state['workspace_id']}")
            except Exception as e:
                print(f"⚠️ Error obteniendo workspace automáticamente: {e}")
                # Fallback al workspace ID hardcodeado
                state['workspace_id'] = "9014943317"
                print(f"🔄 Usando workspace ID hardcodeado como fallback: {state['workspace_id']}")
        
        print(f"✅ Workspace ID válido: {state['workspace_id']}")
        
        # Obtener cliente de ClickUp
        clickup_client = ClickUpClient()
        
        # Obtener base de datos
        db = next(get_db())
        
        # Obtener espacios del workspace
        try:
            print(f"🔍 Obteniendo espacios para workspace: {state['workspace_id']}")
            spaces = await clickup_client.get_spaces(state['workspace_id'])
            if not spaces:
                error_msg = "Error obteniendo espacios: respuesta vacía"
                state['errors'].append(error_msg)
                state['sync_status'] = 'error'
                print(f"❌ {error_msg}")
                return state
            
            print(f"📊 Encontrados {len(spaces)} espacios en el workspace")
        except Exception as e:
            error_msg = f"Error obteniendo espacios: {str(e)}"
            state['errors'].append(error_msg)
            state['sync_status'] = 'error'
            print(f"❌ {error_msg}")
            return state
        
        total_synced = 0
        total_created = 0
        total_updated = 0
        
        # Sincronizar cada espacio
        for space in spaces:
            space_id = space['id']
            space_name = space['name']
            print(f"🔄 Sincronizando espacio: {space_name} (ID: {space_id})")
            
            try:
                # Obtener listas del espacio
                lists = await clickup_client.get_lists(space_id)
                if not lists:
                    print(f"   ⚠️ No se encontraron listas en el espacio {space_name}")
                    continue
                
                print(f"   📋 Encontradas {len(lists)} listas en el espacio {space_name}")
                
                # Sincronizar cada lista
                for list_item in lists:
                    list_id = list_item['id']
                    list_name = list_item['name']
                    print(f"   🔄 Sincronizando lista: {list_name} (ID: {list_id})")
                    
                    try:
                        # Obtener tareas de la lista
                        tasks = await clickup_client.get_tasks(list_id)
                        if not tasks:
                            print(f"      ⚠️ No se encontraron tareas en la lista {list_name}")
                            continue
                        
                        print(f"      📊 Encontradas {len(tasks)} tareas en la lista {list_name}")
                        
                        # Sincronizar cada tarea
                        for task_data in tasks:
                            try:
                                # Verificar si la tarea ya existe
                                existing_task = db.query(Task).filter(Task.clickup_id == task_data['id']).first()
                                
                                if existing_task:
                                    # Actualizar tarea existente
                                    existing_task.name = task_data.get('name', 'Sin nombre')
                                    existing_task.description = task_data.get('description', '')
                                    existing_task.status = task_data.get('status', {}).get('status', 'to do')
                                    existing_task.priority = task_data.get('priority', {}).get('id', 3) if isinstance(task_data.get('priority'), dict) else task_data.get('priority', 3)
                                    existing_task.assignee_id = task_data.get('assignees', [{}])[0].get('id') if task_data.get('assignees') else None
                                    existing_task.assignee_name = task_data.get('assignees', [{}])[0].get('username') if task_data.get('assignees') else None
                                    existing_task.list_id = list_id
                                    existing_task.list_name = list_name
                                    existing_task.space_id = space_id
                                    existing_task.space_name = space_name
                                    existing_task.workspace_id = state['workspace_id']
                                    
                                    # Manejar campos personalizados
                                    custom_fields = {}
                                    if task_data.get('custom_fields'):
                                        for field in task_data['custom_fields']:
                                            if isinstance(field, dict) and field.get('name') and field.get('value'):
                                                custom_fields[field['name']] = field['value']
                                    existing_task.custom_fields = custom_fields
                                    
                                    existing_task.updated_at = datetime.now()
                                    total_updated += 1
                                    print(f"      ✅ Tarea actualizada: {existing_task.name}")
                                else:
                                    # Crear nueva tarea
                                    new_task = Task(
                                        clickup_id=task_data['id'],
                                        name=task_data.get('name', 'Sin nombre'),
                                        description=task_data.get('description', ''),
                                        status=task_data.get('status', {}).get('status', 'to do'),
                                        priority=task_data.get('priority', {}).get('id', 3) if isinstance(task_data.get('priority'), dict) else task_data.get('priority', 3),
                                        assignee_id=task_data.get('assignees', [{}])[0].get('id') if task_data.get('assignees') else None,
                                        assignee_name=task_data.get('assignees', [{}])[0].get('username') if task_data.get('assignees') else None,
                                        list_id=list_id,
                                        list_name=list_name,
                                        space_id=space_id,
                                        space_name=space_name,
                                        workspace_id=state['workspace_id'],
                                        created_at=datetime.now(),
                                        updated_at=datetime.now()
                                    )
                                    
                                    # Manejar campos personalizados
                                    custom_fields = {}
                                    if task_data.get('custom_fields'):
                                        for field in task_data['custom_fields']:
                                            if isinstance(field, dict) and field.get('name') and field.get('value'):
                                                custom_fields[field['name']] = field['value']
                                    new_task.custom_fields = custom_fields
                                    
                                    db.add(new_task)
                                    total_created += 1
                                    print(f"      ✅ Tarea creada: {new_task.name}")
                                
                                total_synced += 1
                                
                            except Exception as e:
                                error_msg = f"Error procesando tarea {task_data.get('id', 'unknown')}: {str(e)}"
                                state['errors'].append(error_msg)
                                print(f"      ❌ {error_msg}")
                                continue
                        
                        # Commit después de cada lista
                        try:
                            db.commit()
                            print(f"      ✅ Commit exitoso para lista: {list_name}")
                        except Exception as e:
                            db.rollback()
                            error_msg = f"Error en commit para lista {list_name}: {str(e)}"
                            state['errors'].append(error_msg)
                            print(f"      ❌ {error_msg}")
                    
                    except Exception as e:
                        error_msg = f"Error sincronizando lista {list_name}: {str(e)}"
                        state['errors'].append(error_msg)
                        print(f"   ❌ {error_msg}")
                        continue
                        
            except Exception as e:
                error_msg = f"Error sincronizando espacio {space_name}: {str(e)}"
                state['errors'].append(error_msg)
                print(f"   ❌ {error_msg}")
                continue
        
        # Commit final
        try:
            db.commit()
            print("✅ Commit final exitoso")
        except Exception as e:
            db.rollback()
            error_msg = f"Error en commit final: {str(e)}"
            state['errors'].append(error_msg)
            print(f"❌ {error_msg}")
        
        # Actualizar estado
        state['total_tasks_synced'] = total_synced
        state['total_tasks_created'] = total_created
        state['total_tasks_updated'] = total_updated
        
        if state['errors']:
            state['sync_status'] = 'completed_with_errors'
        else:
            state['sync_status'] = 'completed'
        
        print(f"✅ Sincronización completada: {total_synced} tareas procesadas")
        
    except Exception as e:
        error_msg = f"Error general en sincronización: {str(e)}"
        state['errors'].append(error_msg)
        state['sync_status'] = 'error'
        print(f"❌ {error_msg}")
    
    return state

# Nodo de finalización
def finish_sync(state: SyncWorkflowState) -> SyncWorkflowState:
    """Finalizar el proceso de sincronización"""
    state['end_time'] = datetime.now().isoformat()
    
    if state['sync_status'] == 'completed':
        print("🎉 Sincronización completada exitosamente")
    elif state['sync_status'] == 'completed_with_errors':
        print("⚠️ Sincronización completada con errores menores")
    else:
        print("❌ Sincronización falló")
    
    return state

# Nodo de logging de errores (si los hay)
def log_errors_if_any(state: SyncWorkflowState) -> SyncWorkflowState:
    """Registrar errores en el sistema de logging si los hay"""
    if not state['errors']:
        return state
    
    print("📝 Registrando errores en sistema de logging...")
    
    try:
        # Preparar datos para logging
        logging_inputs = {
            "error_description": f"Errores en sincronización: {'; '.join(state['errors'])}",
            "solution_description": "Revisar logs y configuración de ClickUp",
            "context_info": f"Workspace: {state['workspace_id']}, Tareas sincronizadas: {state['total_tasks_synced']}",
            "deployment_id": "sync_workflow",
            "environment": "production",
            "severity": "medium" if len(state['errors']) <= 3 else "high",
            "status": "resolved"
        }
        
        # Usar nuestro sistema de logging
        result = log_error_sync(logging_inputs)
        state['logging_result'] = result
        
        if result["status"] == "documentado":
            print("   ✅ Errores registrados exitosamente")
        else:
            print(f"   ❌ Error en logging: {result.get('message', 'Error desconocido')}")
            
    except Exception as e:
        error_msg = f"Error en logging: {str(e)}"
        print(f"   ❌ {error_msg}")
        state['logging_result'] = {"status": "error", "message": error_msg}
    
    return state

# Crear el workflow
def create_sync_workflow() -> StateGraph:
    """Crear el workflow de sincronización"""
    workflow = StateGraph(SyncWorkflowState)
    
    # Agregar nodos
    workflow.add_node("start_sync", start_sync)
    workflow.add_node("sync_tasks", sync_tasks)
    workflow.add_node("finish_sync", finish_sync)
    workflow.add_node("log_errors_if_any", log_errors_if_any)
    
    # Definir flujo
    workflow.set_entry_point("start_sync")
    workflow.add_edge("start_sync", "sync_tasks")
    workflow.add_edge("sync_tasks", "finish_sync")
    workflow.add_edge("finish_sync", "log_errors_if_any")
    workflow.add_edge("log_errors_if_any", END)
    
    return workflow

# Función principal para ejecutar la sincronización
async def run_sync_workflow(workspace_id: str) -> Dict[str, Any]:
    """Ejecutar el workflow de sincronización"""
    workflow = create_sync_workflow()
    app = workflow.compile()
    
    # Estado inicial
    initial_state = {
        "workspace_id": workspace_id,
        "sync_status": "",
        "total_tasks_synced": 0,
        "total_tasks_created": 0,
        "total_tasks_updated": 0,
        "errors": [],
        "start_time": "",
        "end_time": "",
        "logging_result": {}
    }
    
    # Ejecutar workflow
    result = await app.ainvoke(initial_state)
    
    return {
        "message": "Sincronización completada",
        "total_tasks_synced": result["total_tasks_synced"],
        "total_tasks_created": result["total_tasks_created"],
        "total_tasks_updated": result["total_tasks_updated"],
        "workspace_id": workspace_id,
        "status": result["sync_status"],
        "errors": result["errors"]
    }
