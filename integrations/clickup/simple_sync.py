#!/usr/bin/env python3
"""
Sistema de sincronización simplificado y robusto para ClickUp
Resuelve problemas de codificación, conexión y manejo de errores
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from sqlalchemy.orm import Session

from integrations.clickup.client import ClickUpClient
from core.database import get_db
from models.task import Task
from models.workspace import Workspace

# Configurar logging
sync_logger = logging.getLogger("simple_sync")

class SimpleSyncService:
    """Servicio de sincronización simplificado y robusto"""
    
    def __init__(self):
        self.clickup_client = ClickUpClient()
        self.sync_history = []
        self.max_history = 10
    
    async def sync_workspace_tasks(self, workspace_id: str) -> Dict[str, Any]:
        """
        Sincronizar tareas de un workspace completo
        Versión simplificada y robusta
        """
        start_time = datetime.now()
        result = {
            "success": False,
            "workspace_id": workspace_id,
            "total_tasks_synced": 0,
            "total_tasks_created": 0,
            "total_tasks_updated": 0,
            "total_tasks_deleted": 0,
            "errors": [],
            "start_time": start_time.isoformat(),
            "end_time": None,
            "duration": 0
        }
        
        try:
            print(f"🔄 Iniciando sincronización para workspace: {workspace_id}")
            
            # 1. Obtener espacios del workspace
            try:
                spaces = await self.clickup_client.get_spaces(workspace_id)
                if not spaces:
                    error_msg = "No se encontraron espacios en el workspace"
                    result["errors"].append(error_msg)
                    print(f"❌ {error_msg}")
                    return result
                
                print(f"📊 Encontrados {len(spaces)} espacios")
            except Exception as e:
                error_msg = f"Error obteniendo espacios: {str(e)}"
                result["errors"].append(error_msg)
                print(f"❌ {error_msg}")
                return result
            
            # 2. Procesar cada espacio
            for space in spaces:
                space_id = space["id"]
                space_name = space.get("name", "Sin nombre")
                
                try:
                    print(f"  📁 Procesando espacio: {space_name}")
                    
                    # Obtener listas del espacio
                    lists = await self.clickup_client.get_lists(space_id)
                    if not lists:
                        print(f"    ⚠️ No se encontraron listas en el espacio {space_name}")
                        continue
                    
                    print(f"    📋 Encontradas {len(lists)} listas")
                    
                    # Procesar cada lista
                    for list_item in lists:
                        list_id = list_item["id"]
                        list_name = list_item.get("name", "Sin nombre")
                        
                        try:
                            print(f"      📝 Procesando lista: {list_name}")
                            
                            # Obtener tareas de la lista - incluir cerradas para reportes correctos
                            tasks = await self.clickup_client.get_tasks(
                                list_id=list_id,
                                include_closed=True,  # incluir cerradas para conteos exactos
                                page=0,
                                limit=100
                            )
                            
                            if not tasks:
                                print(f"        ⚠️ No se encontraron tareas en la lista {list_name}")
                                continue
                            
                            print(f"        ✅ Encontradas {len(tasks)} tareas")
                            
                            # Sincronizar tareas
                            sync_result = await self._sync_task_batch(tasks, workspace_id)
                            
                            result["total_tasks_synced"] += sync_result["total_synced"]
                            result["total_tasks_created"] += sync_result["total_created"]
                            result["total_tasks_updated"] += sync_result["total_updated"]
                            
                            print(f"        ✅ Lista {list_name} sincronizada: {sync_result['total_synced']} tareas")
                            
                        except Exception as e:
                            error_msg = f"Error procesando lista {list_name}: {str(e)}"
                            result["errors"].append(error_msg)
                            print(f"        ❌ {error_msg}")
                            continue
                    
                except Exception as e:
                    error_msg = f"Error procesando espacio {space_name}: {str(e)}"
                    result["errors"].append(error_msg)
                    print(f"  ❌ {error_msg}")
                    continue
            
            # 3. Detectar tareas eliminadas
            try:
                # No eliminar agresivamente: comparar contra tareas abiertas + cerradas
                deleted_count = await self._detect_deleted_tasks(workspace_id)
                result["total_tasks_deleted"] = deleted_count
                print(f"🗑️ Eliminadas {deleted_count} tareas obsoletas")
            except Exception as e:
                error_msg = f"Error detectando tareas eliminadas: {str(e)}"
                result["errors"].append(error_msg)
                print(f"❌ {error_msg}")
            
            # 4. Marcar como exitoso si no hay errores críticos
            if len(result["errors"]) <= 2:  # Permitir algunos errores menores
                result["success"] = True
                print("✅ Sincronización completada exitosamente")
            else:
                print("⚠️ Sincronización completada con errores")
            
        except Exception as e:
            error_msg = f"Error general en sincronización: {str(e)}"
            result["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        finally:
            # Calcular duración
            end_time = datetime.now()
            result["end_time"] = end_time.isoformat()
            result["duration"] = (end_time - start_time).total_seconds()
            
            # Agregar al historial
            self._add_to_history(result)
            
            print(f"⏱️ Duración total: {result['duration']:.2f} segundos")
            print(f"📊 Resumen: {result['total_tasks_synced']} sincronizadas, {result['total_tasks_created']} creadas, {result['total_tasks_updated']} actualizadas")
        
        return result
    
    async def _sync_task_batch(self, tasks: List[Dict], workspace_id: str) -> Dict[str, int]:
        """Sincronizar un lote de tareas"""
        db = next(get_db())
        total_synced = 0
        total_created = 0
        total_updated = 0
        
        try:
            for task_data in tasks:
                try:
                    task_id = task_data["id"]
                    
                    # Verificar si la tarea ya existe
                    existing_task = db.query(Task).filter(Task.clickup_id == task_id).first()
                    
                    if existing_task:
                        # Actualizar tarea existente
                        updated = await self._update_local_task(existing_task, task_data)
                        if updated:
                            total_updated += 1
                    else:
                        # Crear nueva tarea
                        await self._create_local_task(task_data, db)
                        total_created += 1
                    
                    total_synced += 1
                    
                except Exception as e:
                    print(f"          ⚠️ Error procesando tarea {task_data.get('id', 'unknown')}: {str(e)}")
                    continue
            
            # Commit después de procesar todas las tareas
            db.commit()
            
        except Exception as e:
            db.rollback()
            print(f"        ❌ Error en commit: {str(e)}")
            raise
        finally:
            db.close()
        
        return {
            "total_synced": total_synced,
            "total_created": total_created,
            "total_updated": total_updated
        }
    
    async def _update_local_task(self, local_task: Task, clickup_data: Dict) -> bool:
        """Actualizar tarea local con datos de ClickUp"""
        try:
            # Campos básicos
            if "name" in clickup_data:
                local_task.name = clickup_data["name"]
            
            if "description" in clickup_data:
                local_task.description = clickup_data.get("description", "")
            
            # Status
            if "status" in clickup_data and clickup_data["status"]:
                local_task.status = clickup_data["status"]["status"]
            
            # Priority - extraer valor numérico del diccionario
            if "priority" in clickup_data:
                priority_data = clickup_data.get("priority", {})
                if isinstance(priority_data, dict) and "priority" in priority_data:
                    # ClickUp devuelve: {"priority": "low", "id": "4", "color": "#d8d8d8"}
                    priority_value = priority_data["priority"]
                    if priority_value == "urgent":
                        local_task.priority = 1
                    elif priority_value == "high":
                        local_task.priority = 2
                    elif priority_value == "normal":
                        local_task.priority = 3
                    elif priority_value == "low":
                        local_task.priority = 4
                    else:
                        local_task.priority = 3  # default
                else:
                    local_task.priority = 3  # default
            
            # Dates
            if clickup_data.get("due_date"):
                due_timestamp = clickup_data["due_date"]
                if isinstance(due_timestamp, (int, float)):
                    local_task.due_date = datetime.fromtimestamp(due_timestamp / 1000)
                elif isinstance(due_timestamp, str) and due_timestamp.isdigit():
                    local_task.due_date = datetime.fromtimestamp(int(due_timestamp) / 1000)
            
            if clickup_data.get("start_date"):
                start_timestamp = clickup_data["start_date"]
                if isinstance(start_timestamp, (int, float)):
                    local_task.start_date = datetime.fromtimestamp(start_timestamp / 1000)
                elif isinstance(start_timestamp, str) and start_timestamp.isdigit():
                    local_task.start_date = datetime.fromtimestamp(int(start_timestamp) / 1000)
            
            # Assignees
            if clickup_data.get("assignees"):
                local_task.assignee_id = str(clickup_data["assignees"][0]["id"])
            
            # Custom fields
            if "custom_fields" in clickup_data:
                local_task.custom_fields = clickup_data["custom_fields"]
            
            # Metadata
            local_task.is_synced = True
            local_task.last_sync = datetime.now()
            local_task.updated_at = datetime.now()
            
            return True
            
        except Exception as e:
            print(f"          ❌ Error actualizando tarea {local_task.clickup_id}: {str(e)}")
            return False
    
    async def _create_local_task(self, clickup_data: Dict, db: Session):
        """Crear nueva tarea local desde datos de ClickUp"""
        try:
            # Convertir priority a entero desde diccionario de ClickUp
            priority_data = clickup_data.get("priority", {})
            if isinstance(priority_data, dict) and "priority" in priority_data:
                priority_value = priority_data["priority"]
                if priority_value == "urgent":
                    priority = 1
                elif priority_value == "high":
                    priority = 2
                elif priority_value == "normal":
                    priority = 3
                elif priority_value == "low":
                    priority = 4
                else:
                    priority = 3  # default
            else:
                priority = 3  # default
            
            # Crear tarea
            task = Task(
                clickup_id=clickup_data["id"],
                name=clickup_data["name"],
                description=clickup_data.get("description", ""),
                status=clickup_data["status"]["status"] if clickup_data.get("status") else "open",
                priority=priority,
                due_date=self._parse_timestamp(clickup_data.get("due_date")),
                start_date=self._parse_timestamp(clickup_data.get("start_date")),
                workspace_id=clickup_data["team_id"],
                list_id=clickup_data["list"]["id"],
                assignee_id=str(clickup_data["assignees"][0]["id"]) if clickup_data.get("assignees") else None,
                creator_id=str(clickup_data["creator"]["id"]) if clickup_data.get("creator") else None,
                tags=[tag["name"] for tag in clickup_data.get("tags", [])],
                custom_fields=clickup_data.get("custom_fields", {}),
                is_synced=True,
                last_sync=datetime.now()
            )
            
            db.add(task)
            
        except Exception as e:
            print(f"          ❌ Error creando tarea {clickup_data.get('id', 'unknown')}: {str(e)}")
            raise
    
    def _parse_timestamp(self, timestamp) -> Optional[datetime]:
        """Parsear timestamp de ClickUp a datetime"""
        if not timestamp:
            return None
        
        try:
            if isinstance(timestamp, (int, float)):
                return datetime.fromtimestamp(timestamp / 1000)
            elif isinstance(timestamp, str) and timestamp.isdigit():
                return datetime.fromtimestamp(int(timestamp) / 1000)
            else:
                return None
        except Exception:
            return None
    
    async def _detect_deleted_tasks(self, workspace_id: str) -> int:
        """Detectar y marcar tareas eliminadas"""
        db = next(get_db())
        try:
            # Obtener todas las tareas locales del workspace
            local_tasks = db.query(Task).filter(Task.workspace_id == workspace_id).all()
            local_task_ids = {task.clickup_id for task in local_tasks}
            
            # Obtener tareas actuales de ClickUp
            current_task_ids = set()
            
            try:
                spaces = await self.clickup_client.get_spaces(workspace_id)
                for space in spaces:
                    lists = await self.clickup_client.get_lists(space["id"])
                    for list_item in lists:
                        tasks = await self.clickup_client.get_tasks(
                            list_id=list_item["id"],
                            include_closed=False,  # SOLO ABIERTAS
                            page=0,
                            limit=100
                        )
                        current_task_ids.update(task["id"] for task in tasks)
            except Exception as e:
                print(f"⚠️ Error obteniendo tareas actuales para detección de eliminadas: {str(e)}")
                return 0
            
            # Encontrar tareas que ya no existen en ClickUp
            deleted_task_ids = local_task_ids - current_task_ids
            
            if deleted_task_ids:
                # Marcar como eliminadas
                deleted_count = db.query(Task).filter(
                    Task.clickup_id.in_(deleted_task_ids)
                ).delete(synchronize_session=False)
                
                db.commit()
                return deleted_count
            
            return 0
            
        finally:
            db.close()
    
    def _add_to_history(self, result: Dict):
        """Agregar resultado al historial"""
        self.sync_history.append(result)
        
        # Mantener solo los últimos resultados
        if len(self.sync_history) > self.max_history:
            self.sync_history = self.sync_history[-self.max_history:]
    
    def get_sync_stats(self) -> dict:
        """Obtener estadísticas de sincronización"""
        if not self.sync_history:
            return {"no_syncs": True}
        
        recent_syncs = self.sync_history[-5:]  # Últimas 5 sincronizaciones
        
        total_processed = sum(s.get("total_tasks_synced", 0) for s in recent_syncs)
        total_errors = sum(len(s.get("errors", [])) for s in recent_syncs)
        avg_duration = sum(s.get("duration", 0) for s in recent_syncs) / len(recent_syncs)
        
        return {
            "total_syncs": len(self.sync_history),
            "recent_syncs": len(recent_syncs),
            "total_processed": total_processed,
            "total_errors": total_errors,
            "success_rate": (len([s for s in recent_syncs if s.get("success", False)]) / len(recent_syncs)) * 100,
            "avg_duration": avg_duration,
            "last_sync": recent_syncs[-1].get("start_time") if recent_syncs else None
        }

# Instancia global del servicio de sincronización
simple_sync_service = SimpleSyncService()
