#!/usr/bin/env python3
"""
Workflow de LangGraph para búsqueda semántica RAG
Mantiene el estado del motor de búsqueda entre llamadas
"""

from langgraph.graph import StateGraph, END
from typing import Dict, Any, TypedDict, List, Optional
import os
import sys
import asyncio
from datetime import datetime
import logging

# Agregar el directorio raiz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import get_db
from models.task import Task
from utils.deployment_logger import log_error_sync

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Estado del workflow de búsqueda RAG
class RAGSearchState(TypedDict):
    """Estado del workflow de búsqueda RAG"""
    query: str
    search_results: List[Dict[str, Any]]
    search_status: str
    indexed_tasks_count: int
    search_time: str
    errors: List[str]
    logging_result: Dict[str, Any]

# Motor de búsqueda simplificado que mantiene estado
class SimpleRAGEngine:
    """Motor de búsqueda RAG simplificado que mantiene estado"""
    
    def __init__(self):
        self.task_texts = []
        self.task_ids = []
        self.task_data = []
        self.is_indexed = False
        self.last_update = None
    
    def build_index(self, tasks: List[Dict[str, Any]]) -> bool:
        """Construir índice de búsqueda"""
        try:
            logger.info(f"🔍 Construyendo índice para {len(tasks)} tareas")
            
            self.task_texts = []
            self.task_ids = []
            self.task_data = []
            
            for task in tasks:
                task_id = task.get('id') or task.get('clickup_id')
                if not task_id:
                    continue
                
                # Preparar texto para búsqueda
                text_parts = []
                
                # Nombre de la tarea (más importante)
                if task.get('name'):
                    text_parts.append(task['name'])
                
                # Descripción
                if task.get('description'):
                    text_parts.append(task['description'])
                
                # Usuario asignado
                if task.get('assignee_id'):
                    text_parts.append(f"usuario {task['assignee_id']}")
                
                # Estado
                if task.get('status'):
                    text_parts.append(f"estado {task['status']}")
                
                # Prioridad
                if task.get('priority'):
                    text_parts.append(f"prioridad {task['priority']}")
                
                # Campos personalizados
                if task.get('custom_fields'):
                    custom_fields = task['custom_fields']
                    if isinstance(custom_fields, dict):
                        for field_name, field_value in custom_fields.items():
                            if field_value:
                                text_parts.append(f"{field_name} {field_value}")
                    elif isinstance(custom_fields, list):
                        for field in custom_fields:
                            if isinstance(field, dict) and field.get('value'):
                                text_parts.append(f"campo {field['value']}")
                
                # Lista y workspace
                if task.get('list_id'):
                    text_parts.append(f"lista {task['list_id']}")
                
                if task.get('workspace_id'):
                    text_parts.append(f"workspace {task['workspace_id']}")
                
                # Unir todas las partes
                final_text = " ".join(text_parts)
                
                if final_text.strip():
                    self.task_texts.append(final_text)
                    self.task_ids.append(task_id)
                    self.task_data.append(task)
                    logger.info(f"✅ Tarea {task_id} indexada con {len(final_text)} caracteres")
            
            self.is_indexed = True
            self.last_update = datetime.now()
            
            logger.info(f"✅ Índice construido: {len(self.task_texts)} tareas indexadas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error construyendo índice: {e}")
            return False
    
    def search(self, query: str, top_k: int = 10, threshold: float = 0.1) -> List[Dict[str, Any]]:
        """Búsqueda semántica simplificada"""
        if not self.is_indexed or not self.task_texts:
            logger.warning("⚠️ Índice no construido o vacío")
            return []
        
        try:
            logger.info(f"🔍 Búsqueda para: '{query}' (threshold: {threshold})")
            
            query_lower = query.lower()
            results = []
            
            for i, (task_id, task_text, task_data) in enumerate(zip(self.task_ids, self.task_texts, self.task_data)):
                # Calcular puntuación de similitud
                task_lower = task_text.lower()
                
                # Verificar si las palabras de la consulta están en el texto de la tarea
                query_words = query_lower.split()
                matches = 0
                total_words = len(query_words)
                
                for word in query_words:
                    if word in task_lower:
                        matches += 1
                
                # Calcular puntuación basada en coincidencias de palabras
                if total_words > 0:
                    score = matches / total_words
                else:
                    score = 0.0
                
                # Bonificación para coincidencias exactas
                if query_lower in task_lower:
                    score += 0.5
                
                # Bonificación para coincidencias en el nombre
                if task_data.get('name') and query_lower in task_data['name'].lower():
                    score += 0.3
                
                # Filtrar por threshold
                if score >= threshold:
                    results.append({
                        'task_id': task_id,
                        'score': score,
                        'text': task_text,
                        'task_data': task_data
                    })
                    
                    logger.info(f"✅ Tarea {task_id} encontrada (puntuación: {score:.4f})")
            
            # Ordenar por puntuación
            results.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"🔍 Búsqueda completada: {len(results)} resultados para '{query}'")
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del motor de búsqueda"""
        return {
            "is_indexed": self.is_indexed,
            "indexed_tasks": len(self.task_texts),
            "last_update": self.last_update.isoformat() if self.last_update else None
        }

# Instancia global del motor de búsqueda
rag_engine = SimpleRAGEngine()

# Nodo de inicialización del índice
def initialize_search_index(state: RAGSearchState) -> RAGSearchState:
    """Inicializar el índice de búsqueda si es necesario"""
    try:
        logger.info("🔍 Verificando estado del índice de búsqueda...")
        
        if not rag_engine.is_indexed:
            logger.info("🔍 Construyendo índice de búsqueda...")
            
            # Obtener todas las tareas de la base de datos
            db = next(get_db())
            tasks = db.query(Task).all()
            
            if not tasks:
                logger.warning("⚠️ No hay tareas en la base de datos")
                state['search_status'] = 'no_tasks'
                return state
            
            # Convertir tareas a diccionarios
            task_dicts = []
            for task in tasks:
                task_dict = {
                    'id': task.id,
                    'clickup_id': task.clickup_id,
                    'name': task.name,
                    'description': task.description,
                    'status': task.status,
                    'priority': task.priority,
                    'assignee_id': task.assignee_id,
                    'workspace_id': task.workspace_id,
                    'list_id': task.list_id,
                    'custom_fields': task.custom_fields
                }
                task_dicts.append(task_dict)
            
            # Construir índice
            success = rag_engine.build_index(task_dicts)
            
            if success:
                state['indexed_tasks_count'] = len(task_dicts)
                state['search_status'] = 'ready'
                logger.info(f"✅ Índice construido con {len(task_dicts)} tareas")
            else:
                state['search_status'] = 'index_error'
                state['errors'].append("Error construyendo índice de búsqueda")
                logger.error("❌ Error construyendo índice")
        else:
            state['indexed_tasks_count'] = len(rag_engine.task_texts)
            state['search_status'] = 'ready'
            logger.info(f"✅ Índice ya está construido con {len(rag_engine.task_texts)} tareas")
        
    except Exception as e:
        error_msg = f"Error inicializando índice: {str(e)}"
        state['errors'].append(error_msg)
        state['search_status'] = 'error'
        logger.error(f"❌ {error_msg}")
    
    return state

# Nodo de búsqueda
def execute_search(state: RAGSearchState) -> RAGSearchState:
    """Ejecutar la búsqueda semántica"""
    try:
        if state['search_status'] != 'ready':
            logger.warning(f"⚠️ Estado no listo para búsqueda: {state['search_status']}")
            return state
        
        logger.info(f"🔍 Ejecutando búsqueda para: '{state['query']}'")
        
        # Ejecutar búsqueda
        results = rag_engine.search(state['query'], top_k=20, threshold=0.1)
        
        # Formatear resultados
        formatted_results = []
        for result in results:
            task_data = result['task_data']
            formatted_results.append({
                'id': task_data.get('id'),
                'clickup_id': task_data.get('clickup_id'),
                'name': task_data.get('name', 'Sin nombre'),
                'description': task_data.get('description', ''),
                'status': task_data.get('status', ''),
                'priority': task_data.get('priority', 3),
                'assignee_id': task_data.get('assignee_id', ''),
                'list_id': task_data.get('list_id', ''),
                'workspace_id': task_data.get('workspace_id', ''),
                'score': result['score'],
                'matched_text': result['text'][:200] + "..." if len(result['text']) > 200 else result['text']
            })
        
        state['search_results'] = formatted_results
        state['search_status'] = 'completed'
        state['search_time'] = datetime.now().isoformat()
        
        logger.info(f"✅ Búsqueda completada: {len(formatted_results)} resultados")
        
    except Exception as e:
        error_msg = f"Error ejecutando búsqueda: {str(e)}"
        state['errors'].append(error_msg)
        state['search_status'] = 'error'
        logger.error(f"❌ {error_msg}")
    
    return state

# Nodo de logging de errores (si los hay)
def log_errors_if_any(state: RAGSearchState) -> RAGSearchState:
    """Registrar errores en el sistema de logging si los hay"""
    if not state['errors']:
        return state
    
    logger.info("📝 Registrando errores en sistema de logging...")
    
    try:
        # Preparar datos para logging
        logging_inputs = {
            "error_description": f"Errores en búsqueda RAG: {'; '.join(state['errors'])}",
            "solution_description": "Revisar logs y reconstruir índice de búsqueda",
            "context_info": f"Query: {state['query']}, Estado: {state['search_status']}",
            "deployment_id": "rag_search_workflow",
            "environment": "production",
            "severity": "medium" if len(state['errors']) <= 2 else "high",
            "status": "resolved"
        }
        
        # Usar nuestro sistema de logging
        result = log_error_sync(logging_inputs)
        state['logging_result'] = result
        
        if result["status"] == "documentado":
            logger.info("   ✅ Errores registrados exitosamente")
        else:
            logger.warning(f"   ⚠️ Error en logging: {result.get('message', 'Error desconocido')}")
            
    except Exception as e:
        error_msg = f"Error en logging: {str(e)}"
        logger.error(f"   ❌ {error_msg}")
        state['logging_result'] = {"status": "error", "message": error_msg}
    
    return state

# Crear el workflow
def create_rag_search_workflow() -> StateGraph:
    """Crear el workflow de búsqueda RAG"""
    workflow = StateGraph(RAGSearchState)
    
    # Agregar nodos
    workflow.add_node("initialize_search_index", initialize_search_index)
    workflow.add_node("execute_search", execute_search)
    workflow.add_node("log_errors_if_any", log_errors_if_any)
    
    # Definir flujo
    workflow.set_entry_point("initialize_search_index")
    workflow.add_edge("initialize_search_index", "execute_search")
    workflow.add_edge("execute_search", "log_errors_if_any")
    workflow.add_edge("log_errors_if_any", END)
    
    return workflow

# Función principal para ejecutar la búsqueda RAG
async def run_rag_search_workflow(query: str) -> Dict[str, Any]:
    """Ejecutar el workflow de búsqueda RAG"""
    workflow = create_rag_search_workflow()
    app = workflow.compile()
    
    # Estado inicial
    initial_state = {
        "query": query,
        "search_results": [],
        "search_status": "",
        "indexed_tasks_count": 0,
        "search_time": "",
        "errors": [],
        "logging_result": {}
    }
    
    # Ejecutar workflow
    result = await app.ainvoke(initial_state)
    
    return {
        "query": query,
        "results": result["search_results"],
        "total_results": len(result["search_results"]),
        "status": result["search_status"],
        "indexed_tasks": result["indexed_tasks_count"],
        "errors": result["errors"]
    }

# Función para reconstruir el índice
def rebuild_search_index() -> Dict[str, Any]:
    """Reconstruir el índice de búsqueda"""
    try:
        logger.info("🔍 Reconstruyendo índice de búsqueda...")
        
        # Obtener todas las tareas de la base de datos
        db = next(get_db())
        tasks = db.query(Task).all()
        
        if not tasks:
            return {
                "success": False,
                "message": "No hay tareas en la base de datos",
                "indexed_tasks": 0
            }
        
        # Convertir tareas a diccionarios
        task_dicts = []
        for task in tasks:
            task_dict = {
                'id': task.id,
                'clickup_id': task.clickup_id,
                'name': task.name,
                'description': task.description,
                'status': task.status,
                'priority': task.priority,
                'assignee_id': task.assignee_id,
                'workspace_id': task.workspace_id,
                'list_id': task.list_id,
                'custom_fields': task.custom_fields
            }
            task_dicts.append(task_dict)
        
        # Construir índice
        success = rag_engine.build_index(task_dicts)
        
        if success:
            return {
                "success": True,
                "message": f"Índice reconstruido exitosamente con {len(task_dicts)} tareas",
                "indexed_tasks": len(task_dicts)
            }
        else:
            return {
                "success": False,
                "message": "Error construyendo índice",
                "indexed_tasks": 0
            }
        
    except Exception as e:
        error_msg = f"Error reconstruyendo índice: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "message": error_msg,
            "indexed_tasks": 0
        }

# Función para obtener estadísticas del motor
def get_search_stats() -> Dict[str, Any]:
    """Obtener estadísticas del motor de búsqueda"""
    return rag_engine.get_stats()
