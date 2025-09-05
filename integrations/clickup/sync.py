"""
Sistema avanzado de sincronizacion con ClickUp
- Sincronizacion bidireccional
- Deteccion de cambios
- Cache inteligente
- Rate limiting
- Reintentos automaticos
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
import hashlib
import logging
from dataclasses import dataclass, asdict
from sqlalchemy.orm import Session

from integrations.clickup.client import ClickUpClient
from core.database import get_db
from models.task import Task
from models.workspace import Workspace

# Configurar logging
sync_logger = logging.getLogger("sync")


@dataclass
class SyncResult:
    """Resultado de operacion de sincronizacion"""
    success: bool
    items_processed: int
    items_created: int
    items_updated: int
    items_deleted: int
    errors: List[str]
    duration: float
    timestamp: datetime
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TaskChange:
    """Representa un cambio en una tarea"""
    task_id: str
    change_type: str  # created, updated, deleted
    field_changes: Dict[str, Any]
    timestamp: datetime
    source: str  # clickup, local


class TaskCache:
    """Cache inteligente para tareas"""
    
    def __init__(self):
        self._cache: Dict[str, Dict] = {}
        self._hashes: Dict[str, str] = {}
        self._last_update: Dict[str, datetime] = {}
        self.ttl = timedelta(minutes=5)  # TTL de 5 minutos
    
    def get(self, task_id: str) -> Optional[Dict]:
        """Get tarea del cache"""
        if task_id in self._cache:
            if datetime.now() - self._last_update.get(task_id, datetime.min) < self.ttl:
                return self._cache[task_id]
            else:
                # Cache expirado
                self.remove(task_id)
        return None
    
    def set(self, task_id: str, task_data: Dict):
        """Guardar tarea en cache"""
        self._cache[task_id] = task_data
        self._hashes[task_id] = self._compute_hash(task_data)
        self._last_update[task_id] = datetime.now()
    
    def remove(self, task_id: str):
        """Remover tarea del cache"""
        self._cache.pop(task_id, None)
        self._hashes.pop(task_id, None)
        self._last_update.pop(task_id, None)
    
    def has_changed(self, task_id: str, task_data: Dict) -> bool:
        """Verificar si la tarea ha cambiado"""
        current_hash = self._compute_hash(task_data)
        cached_hash = self._hashes.get(task_id)
        return current_hash != cached_hash
    
    def _compute_hash(self, task_data: Dict) -> str:
        """Computar hash de la tarea para detectar cambios"""
        # Seleccionar campos relevantes para el hash
        relevant_fields = {
            'name': task_data.get('name', ''),
            'description': task_data.get('description', ''),
            'status': task_data.get('status', {}),
            'priority': task_data.get('priority', 0),
            'due_date': task_data.get('due_date'),
            'assignees': task_data.get('assignees', []),
            'custom_fields': task_data.get('custom_fields', [])
        }
        
        data_string = json.dumps(relevant_fields, sort_keys=True)
        return hashlib.md5(data_string.encode()).hexdigest()
    
    def clear(self):
        """Limpiar todo el cache"""
        self._cache.clear()
        self._hashes.clear()
        self._last_update.clear()
    
    def get_stats(self) -> dict:
        """Get estadisticas del cache"""
        now = datetime.now()
        expired_count = sum(1 for last_update in self._last_update.values() 
                          if now - last_update >= self.ttl)
        
        return {
            "total_cached": len(self._cache),
            "expired": expired_count,
            "active": len(self._cache) - expired_count,
            "hit_rate": 0  # Seria necesario trackear hits/misses
        }


class RateLimiter:
    """Rate limiter para APIs"""
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: List[datetime] = []
    
    async def acquire(self):
        """Adquirir permiso para hacer request"""
        now = datetime.now()
        
        # Limpiar requests antiguos
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < timedelta(seconds=self.time_window)]
        
        # Verificar si podemos hacer mas requests
        if len(self.requests) >= self.max_requests:
            # Calcular tiempo de espera
            oldest_request = min(self.requests)
            wait_time = self.time_window - (now - oldest_request).total_seconds()
            
            if wait_time > 0:
                sync_logger.info(f"ðŸš¦ Rate limit alcanzado, esperando {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        self.requests.append(now)
    
    def get_stats(self) -> dict:
        """Get estadisticas del rate limiter"""
        now = datetime.now()
        recent_requests = [req for req in self.requests 
                          if now - req < timedelta(seconds=self.time_window)]
        
        return {
            "requests_in_window": len(recent_requests),
            "max_requests": self.max_requests,
            "time_window": self.time_window,
            "requests_remaining": max(0, self.max_requests - len(recent_requests))
        }


class AdvancedSyncService:
    """Servicio avanzado de sincronizacion con ClickUp"""
    
    def __init__(self):
        self.clickup_client = ClickUpClient()
        self.cache = TaskCache()
        self.rate_limiter = RateLimiter(max_requests=50, time_window=60)  # 50 requests por minuto
        self.sync_history: List[SyncResult] = []
        self.max_history = 100
        
        # Configuracion de sincronizacion
        self.batch_size = 50
        self.max_retries = 3
        self.retry_delay = 2
    
    async def full_sync_workspace(self, workspace_id: str) -> SyncResult:
        """Sincronizacion completa de un workspace"""
        start_time = datetime.now()
        result = SyncResult(
            success=False,
            items_processed=0,
            items_created=0,
            items_updated=0,
            items_deleted=0,
            errors=[],
            duration=0,
            timestamp=start_time
        )
        
        try:
            sync_logger.info(f"ðŸ”„ Iniciando sincronizacion completa del workspace {workspace_id}")
            
            # Get todas las listas del workspace
            await self.rate_limiter.acquire()
            spaces = await self.clickup_client.get_spaces(workspace_id)
            
            all_tasks = []
            for space in spaces:
                lists = await self.clickup_client.get_lists(space["id"])
                for list_data in lists:
                    await self.rate_limiter.acquire()
                    tasks = await self.clickup_client.get_tasks(list_data["id"])
                    all_tasks.extend(tasks)
            
            # Procesar tareas en lotes
            for i in range(0, len(all_tasks), self.batch_size):
                batch = all_tasks[i:i + self.batch_size]
                batch_result = await self._process_task_batch(batch, workspace_id)
                
                result.items_processed += batch_result.items_processed
                result.items_created += batch_result.items_created
                result.items_updated += batch_result.items_updated
                result.errors.extend(batch_result.errors)
            
            # Detectar tareas eliminadas
            deleted_count = await self._detect_deleted_tasks(workspace_id, [t["id"] for t in all_tasks])
            result.items_deleted = deleted_count
            
            result.success = len(result.errors) == 0
            
        except Exception as e:
            error_msg = f"Error en sincronizacion completa: {e}"
            sync_logger.error(error_msg)
            result.errors.append(error_msg)
        
        result.duration = (datetime.now() - start_time).total_seconds()
        self._add_to_history(result)
        
        sync_logger.info(f"âœ… Sincronizacion completa terminada: {result.items_processed} procesadas, "
                        f"{result.items_created} creadas, {result.items_updated} actualizadas, "
                        f"{result.items_deleted} eliminadas en {result.duration:.1f}s")
        
        return result
    
    async def incremental_sync(self, workspace_id: str, since: Optional[datetime] = None) -> SyncResult:
        """Sincronizacion incremental basada en cambios recientes"""
        start_time = datetime.now()
        
        if since is None:
            since = start_time - timedelta(hours=1)  # Ultima hora por defecto
        
        result = SyncResult(
            success=False,
            items_processed=0,
            items_created=0,
            items_updated=0,
            items_deleted=0,
            errors=[],
            duration=0,
            timestamp=start_time
        )
        
        try:
            sync_logger.info(f"ðŸ”„ Sincronizacion incremental desde {since}")
            
            # Get tareas modificadas recientemente
            # Nota: ClickUp no tiene API nativa para esto, asi que usamos cache
            db = next(get_db())
            try:
                local_tasks = db.query(Task).filter(
                    Task.workspace_id == workspace_id,
                    Task.last_sync >= since
                ).all()
                
                for task in local_tasks:
                    try:
                        await self.rate_limiter.acquire()
                        clickup_task = await self.clickup_client.get_task(task.clickup_id)
                        
                        if self.cache.has_changed(task.clickup_id, clickup_task):
                            await self._update_local_task(task, clickup_task, db)
                            result.items_updated += 1
                        
                        self.cache.set(task.clickup_id, clickup_task)
                        result.items_processed += 1
                        
                    except Exception as e:
                        error_msg = f"Error syncing tarea {task.clickup_id}: {e}"
                        sync_logger.error(error_msg)
                        result.errors.append(error_msg)
                
                db.commit()
                result.success = len(result.errors) == 0
                
            finally:
                db.close()
        
        except Exception as e:
            error_msg = f"Error en sincronizacion incremental: {e}"
            sync_logger.error(error_msg)
            result.errors.append(error_msg)
        
        result.duration = (datetime.now() - start_time).total_seconds()
        self._add_to_history(result)
        
        return result
    
    async def sync_single_task(self, task_id: str) -> SyncResult:
        """Sync una sola tarea"""
        start_time = datetime.now()
        result = SyncResult(
            success=False,
            items_processed=0,
            items_created=0,
            items_updated=0,
            items_deleted=0,
            errors=[],
            duration=0,
            timestamp=start_time
        )
        
        try:
            await self.rate_limiter.acquire()
            clickup_task = await self.clickup_client.get_task(task_id)
            
            db = next(get_db())
            try:
                local_task = db.query(Task).filter(Task.clickup_id == task_id).first()
                
                if local_task:
                    if self.cache.has_changed(task_id, clickup_task):
                        await self._update_local_task(local_task, clickup_task, db)
                        result.items_updated = 1
                else:
                    await self._create_local_task(clickup_task, db)
                    result.items_created = 1
                
                self.cache.set(task_id, clickup_task)
                result.items_processed = 1
                result.success = True
                db.commit()
                
            finally:
                db.close()
        
        except Exception as e:
            error_msg = f"Error syncing tarea {task_id}: {e}"
            sync_logger.error(error_msg)
            result.errors.append(error_msg)
        
        result.duration = (datetime.now() - start_time).total_seconds()
        return result
    
    async def _process_task_batch(self, tasks: List[Dict], workspace_id: str) -> SyncResult:
        """Procesar un lote de tareas"""
        result = SyncResult(
            success=True,
            items_processed=0,
            items_created=0,
            items_updated=0,
            items_deleted=0,
            errors=[],
            duration=0,
            timestamp=datetime.now()
        )
        
        db = next(get_db())
        try:
            for task_data in tasks:
                try:
                    task_id = task_data["id"]
                    local_task = db.query(Task).filter(Task.clickup_id == task_id).first()
                    
                    if local_task:
                        if self.cache.has_changed(task_id, task_data):
                            await self._update_local_task(local_task, task_data, db)
                            result.items_updated += 1
                    else:
                        await self._create_local_task(task_data, db)
                        result.items_created += 1
                    
                    self.cache.set(task_id, task_data)
                    result.items_processed += 1
                    
                except Exception as e:
                    error_msg = f"Error procesando tarea {task_data.get('id', 'unknown')}: {e}"
                    result.errors.append(error_msg)
            
            db.commit()
            
        finally:
            db.close()
        
        return result
    
    async def _update_local_task(self, local_task: Task, clickup_data: Dict, db: Session):
        """Update tarea local con datos de ClickUp"""
        # Update campos
        local_task.name = clickup_data.get("name", local_task.name)
        local_task.description = clickup_data.get("description", local_task.description)
        
        # Status
        if "status" in clickup_data and clickup_data["status"]:
            local_task.status = clickup_data["status"]["status"]
        
        # Priority
        local_task.priority = clickup_data.get("priority", local_task.priority)
        
        # Dates
        if clickup_data.get("due_date"):
            _dv = clickup_data.get("due_date")
            local_task.due_date = (
                datetime.fromtimestamp(_dv / 1000) if isinstance(_dv, (int, float)) else (datetime.fromtimestamp(int(_dv) / 1000) if isinstance(_dv, str) and _dv.isdigit() else None)
            )
        
        if clickup_data.get("start_date"):
            _sv = clickup_data.get("start_date")
            local_task.start_date = (
                datetime.fromtimestamp(_sv / 1000) if isinstance(_sv, (int, float)) else (datetime.fromtimestamp(int(_sv) / 1000) if isinstance(_sv, str) and _sv.isdigit() else None)
            )
        
        # Assignees
        if clickup_data.get("assignees"):
            local_task.assignee_id = str(clickup_data["assignees"][0]["id"])
        
        # Custom fields
        local_task.custom_fields = clickup_data.get("custom_fields", {})
        
        # Metadata
        local_task.is_synced = True
        local_task.last_sync = datetime.now()
        
        sync_logger.debug(f"Actualizada tarea local {local_task.clickup_id}")
    
    async def _create_local_task(self, clickup_data: Dict, db: Session):
        """Create nueva tarea local desde datos de ClickUp"""
        from api.routes.tasks import _priority_to_int
        
        task = Task(
            clickup_id=clickup_data["id"],
            name=clickup_data["name"],
            description=clickup_data.get("description", ""),
            status=clickup_data["status"]["status"] if clickup_data.get("status") else "open",
            priority=_priority_to_int(clickup_data.get("priority", 3)),
            due_date=(
                (lambda _v: (
                    datetime.fromtimestamp(_v / 1000)
                    if isinstance(_v, (int, float))
                    else (datetime.fromtimestamp(int(_v) / 1000) if isinstance(_v, str) and _v.isdigit() else None)
                ))(clickup_data.get("due_date"))
                if clickup_data.get("due_date") is not None
                else None
            ),
            start_date=(
                (lambda _v: (
                    datetime.fromtimestamp(_v / 1000)
                    if isinstance(_v, (int, float))
                    else (datetime.fromtimestamp(int(_v) / 1000) if isinstance(_v, str) and _v.isdigit() else None)
                ))(clickup_data.get("start_date"))
                if clickup_data.get("start_date") is not None
                else None
            ),
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
        sync_logger.debug(f"Creada nueva tarea local {task.clickup_id}")
    
    async def _detect_deleted_tasks(self, workspace_id: str, current_task_ids: List[str]) -> int:
        """Detectar y marcar tareas eliminadas"""
        db = next(get_db())
        try:
            # Get todas las tareas locales del workspace
            local_tasks = db.query(Task).filter(Task.workspace_id == workspace_id).all()
            local_task_ids = {task.clickup_id for task in local_tasks}
            current_task_ids_set = set(current_task_ids)
            
            # Encontrar tareas que ya no existen en ClickUp
            deleted_task_ids = local_task_ids - current_task_ids_set
            
            if deleted_task_ids:
                # Filtrar tareas recién creadas (menos de 5 minutos) para no eliminarlas
                now = datetime.now()
                recently_created_tasks = db.query(Task).filter(
                    Task.clickup_id.in_(deleted_task_ids),
                    Task.created_at >= now - timedelta(minutes=5)  # No eliminar tareas recién creadas
                ).all()
                
                # Solo eliminar tareas que no son recién creadas
                safe_to_delete_ids = deleted_task_ids - {task.clickup_id for task in recently_created_tasks}
                
                if safe_to_delete_ids:
                    deleted_count = db.query(Task).filter(
                        Task.clickup_id.in_(safe_to_delete_ids)
                    ).delete(synchronize_session=False)
                    
                    db.commit()
                    sync_logger.info(f"🗑️ Eliminadas {deleted_count} tareas que ya no existen en ClickUp")
                    
                    # Log de tareas recién creadas que se preservaron
                    if recently_created_tasks:
                        sync_logger.info(f"🆕 Preservadas {len(recently_created_tasks)} tareas recién creadas (menos de 5 minutos)")
                        for task in recently_created_tasks:
                            sync_logger.info(f"   📝 Preservada: {task.name} (ID: {task.clickup_id}, Creada: {task.created_at})")
                    
                    return deleted_count
                else:
                    sync_logger.info(f"🆕 Todas las tareas aparentemente 'eliminadas' son recién creadas, preservándolas")
                    return 0
            
            return 0
            
        finally:
            db.close()
    
    def _add_to_history(self, result: SyncResult):
        """Agregar resultado al historial"""
        self.sync_history.append(result)
        
        # Mantener solo los ultimos resultados
        if len(self.sync_history) > self.max_history:
            self.sync_history = self.sync_history[-self.max_history:]
    
    def get_sync_stats(self) -> dict:
        """Get estadisticas de sincronizacion"""
        if not self.sync_history:
            return {"no_syncs": True}
        
        recent_syncs = self.sync_history[-10:]  # Ultimas 10 sincronizaciones
        
        total_processed = sum(s.items_processed for s in recent_syncs)
        total_errors = sum(len(s.errors) for s in recent_syncs)
        avg_duration = sum(s.duration for s in recent_syncs) / len(recent_syncs)
        
        return {
            "total_syncs": len(self.sync_history),
            "recent_syncs": len(recent_syncs),
            "total_processed": total_processed,
            "total_errors": total_errors,
            "success_rate": (len([s for s in recent_syncs if s.success]) / len(recent_syncs)) * 100,
            "avg_duration": avg_duration,
            "last_sync": recent_syncs[-1].timestamp.isoformat() if recent_syncs else None,
            "cache_stats": self.cache.get_stats(),
            "rate_limiter_stats": self.rate_limiter.get_stats()
        }
    
    def clear_cache(self):
        """Limpiar cache"""
        self.cache.clear()
        sync_logger.info("ðŸ§¹ Cache limpiado")


# Instancia global del servicio de sincronizacion
sync_service = AdvancedSyncService()
