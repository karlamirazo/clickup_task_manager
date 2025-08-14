"""
Endpoint de búsqueda contextual RAG para tareas
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from core.database import get_db
from core.search_engine import search_engine
from api.schemas.task import TaskResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/search")
async def search_tasks(
    query: str = Query(..., description="Consulta de búsqueda"),
    top_k: int = Query(10, description="Número máximo de resultados"),
    threshold: float = Query(0.3, description="Umbral de similitud (0.0-1.0)"),
    db: Session = Depends(get_db)
):
    """Búsqueda semántica de tareas usando RAG"""
    try:
        # Verificar que el motor de búsqueda esté inicializado
        if not search_engine.is_initialized:
            await search_engine.initialize()
        
        # Realizar búsqueda
        search_results = search_engine.search_tasks(query, top_k=top_k, threshold=threshold)
        
        # Obtener tareas completas desde la base de datos
        from api.routes.tasks import get_task
        
        tasks = []
        for result in search_results:
            try:
                task_response = await get_task(result['task_id'], db)
                if task_response and 'task' in task_response:
                    task = task_response['task']
                    # Agregar información de búsqueda
                    task_dict = task.__dict__
                    task_dict['search_score'] = result['score']
                    task_dict['search_text'] = result['text']
                    tasks.append(task_dict)
            except Exception as e:
                logger.warning(f"⚠️ No se pudo obtener tarea {result['task_id']}: {e}")
                continue
        
        return {
            "query": query,
            "total_results": len(tasks),
            "threshold": threshold,
            "tasks": tasks
        }
        
    except Exception as e:
        logger.error(f"❌ Error en búsqueda: {e}")
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {str(e)}")

@router.get("/search/advanced")
async def advanced_search(
    name: Optional[str] = Query(None, description="Nombre de la tarea"),
    description: Optional[str] = Query(None, description="Descripción de la tarea"),
    user: Optional[str] = Query(None, description="Usuario asignado"),
    status: Optional[str] = Query(None, description="Estado de la tarea"),
    priority: Optional[int] = Query(None, description="Prioridad de la tarea"),
    tags: Optional[str] = Query(None, description="Tags separados por coma"),
    custom_field_name: Optional[str] = Query(None, description="Nombre del campo personalizado"),
    custom_field_value: Optional[str] = Query(None, description="Valor del campo personalizado"),
    top_k: int = Query(20, description="Número máximo de resultados"),
    db: Session = Depends(get_db)
):
    """Búsqueda avanzada por criterios específicos"""
    try:
        # Verificar que el motor de búsqueda esté inicializado
        if not search_engine.is_initialized:
            await search_engine.initialize()
        
        # Preparar criterios de búsqueda
        custom_fields = None
        if custom_field_name and custom_field_value:
            custom_fields = {custom_field_name: custom_field_value}
        
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
        
        # Realizar búsqueda avanzada
        search_results = search_engine.search_by_criteria(
            name=name,
            description=description,
            user=user,
            status=status,
            priority=str(priority) if priority else None,
            tags=tag_list,
            custom_fields=custom_fields,
            top_k=top_k
        )
        
        # Obtener tareas completas
        from api.routes.tasks import get_task
        
        tasks = []
        for result in search_results:
            try:
                task_response = await get_task(result['task_id'], db)
                if task_response and 'task' in task_response:
                    task = task_response['task']
                    task_dict = task.__dict__
                    task_dict['search_score'] = result['score']
                    task_dict['search_text'] = result['text']
                    tasks.append(task_dict)
            except Exception as e:
                logger.warning(f"⚠️ No se pudo obtener tarea {result['task_id']}: {e}")
                continue
        
        return {
            "criteria": {
                "name": name,
                "description": description,
                "user": user,
                "status": status,
                "priority": priority,
                "tags": tag_list,
                "custom_fields": custom_fields
            },
            "total_results": len(tasks),
            "tasks": tasks
        }
        
    except Exception as e:
        logger.error(f"❌ Error en búsqueda avanzada: {e}")
        raise HTTPException(status_code=500, detail=f"Error en búsqueda avanzada: {str(e)}")

@router.get("/search/suggestions")
async def get_search_suggestions(
    partial_query: str = Query(..., description="Consulta parcial"),
    max_suggestions: int = Query(5, description="Número máximo de sugerencias")
):
    """Obtener sugerencias de búsqueda"""
    try:
        if not search_engine.is_initialized:
            await search_engine.initialize()
        
        suggestions = search_engine.get_search_suggestions(partial_query, max_suggestions)
        
        return {
            "partial_query": partial_query,
            "suggestions": suggestions,
            "total_suggestions": len(suggestions)
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo sugerencias: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo sugerencias: {str(e)}")

@router.post("/search/rebuild-index")
async def rebuild_search_index(db: Session = Depends(get_db)):
    """Reconstruir el índice de búsqueda"""
    try:
        if not search_engine.is_initialized:
            await search_engine.initialize()
        
        # Obtener todas las tareas directamente de la base de datos
        from models.task import Task
        all_tasks = db.query(Task).all()
        
        # Convertir a lista de diccionarios
        tasks_data = []
        for task in all_tasks:
            task_dict = task.__dict__
            # Remover atributos internos de SQLAlchemy
            task_dict.pop('_sa_instance_state', None)
            tasks_data.append(task_dict)
        
        # Reconstruir índice
        search_engine.build_search_index(tasks_data)
        
        stats = search_engine.get_search_stats()
        
        return {
            "message": "Índice de búsqueda reconstruido exitosamente",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Error reconstruyendo índice: {e}")
        raise HTTPException(status_code=500, detail=f"Error reconstruyendo índice: {str(e)}")

@router.get("/search/stats")
async def get_search_stats():
    """Obtener estadísticas del motor de búsqueda"""
    try:
        if not search_engine.is_initialized:
            await search_engine.initialize()
        
        stats = search_engine.get_search_stats()
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")

@router.get("/search/user")
async def search_by_user(
    user: str = Query(..., description="Usuario a buscar (nombre o ID)"),
    top_k: int = Query(20, description="Número máximo de resultados"),
    db: Session = Depends(get_db)
):
    """Búsqueda especializada por usuario"""
    try:
        # Verificar que el motor de búsqueda esté inicializado
        if not search_engine.is_initialized:
            await search_engine.initialize()
        
        # Realizar búsqueda por usuario
        search_results = search_engine.search_by_user(user, top_k=top_k)
        
        # Obtener tareas completas desde la base de datos
        from api.routes.tasks import get_task
        
        tasks = []
        for result in search_results:
            try:
                task_response = await get_task(result['task_id'], db)
                if task_response and 'task' in task_response:
                    task = task_response['task']
                    # Agregar información de búsqueda
                    task_dict = task.__dict__
                    task_dict['search_score'] = result['score']
                    task_dict['search_text'] = result['text']
                    tasks.append(task_dict)
            except Exception as e:
                logger.warning(f"⚠️ No se pudo obtener tarea {result['task_id']}: {e}")
                continue
        
        return {
            "user_query": user,
            "total_results": len(tasks),
            "tasks": tasks
        }
        
    except Exception as e:
        logger.error(f"❌ Error en búsqueda por usuario: {e}")
        raise HTTPException(status_code=500, detail=f"Error en búsqueda por usuario: {str(e)}")
