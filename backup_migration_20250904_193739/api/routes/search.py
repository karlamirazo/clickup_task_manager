"""
Endpoint de busqueda contextual RAG para tareas
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from core.database import get_db
from langgraph_tools.rag_search_workflow import run_rag_search_workflow, rebuild_search_index, get_search_stats
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TaskResponse(BaseModel):
    """Modelo de respuesta para tareas en busqueda"""
    id: int
    clickup_id: str
    name: str
    description: Optional[str]
    status: str
    priority: int
    due_date: Optional[datetime]
    workspace_id: str
    list_id: str
    assignee_id: Optional[str]
    creator_id: Optional[str]
    custom_fields: Optional[dict]
    is_synced: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def search_tasks(
    query: str = Query(..., description="Consulta de búsqueda"),
    top_k: int = Query(10, description="Número máximo de resultados"),
    threshold: float = Query(0.1, description="Umbral de similitud (0.0 - 1.0)")
):
    """Búsqueda semántica de tareas usando LangGraph workflow"""
    try:
        print(f"🔍 Búsqueda solicitada: '{query}' (top_k: {top_k}, threshold: {threshold})")
        
        # Ejecutar workflow de búsqueda RAG
        result = await run_rag_search_workflow(query)
        
        print(f"✅ Búsqueda completada: {result['total_results']} resultados")
        
        return result
        
    except Exception as e:
        error_msg = f"Error en búsqueda: {str(e)}"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/rebuild-index")
async def rebuild_search_index_endpoint():
    """Reconstruir el índice de búsqueda"""
    try:
        print("🔍 Reconstruyendo índice de búsqueda...")
        
        result = rebuild_search_index()
        
        if result["success"]:
            print(f"✅ Índice reconstruido: {result['indexed_tasks']} tareas")
        else:
            print(f"❌ Error reconstruyendo índice: {result['message']}")
        
        return result
        
    except Exception as e:
        error_msg = f"Error reconstruyendo índice: {str(e)}"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/stats")
async def get_search_stats_endpoint():
    """Obtener estadísticas del motor de búsqueda"""
    try:
        stats = get_search_stats()
        print(f"📊 Estadísticas del motor: {stats}")
        return stats
        
    except Exception as e:
        error_msg = f"Error obteniendo estadísticas: {str(e)}"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
