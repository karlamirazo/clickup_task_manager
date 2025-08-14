"""
Motor de búsqueda contextual RAG para tareas
Permite búsqueda semántica por nombre, descripción, usuario, notas, etc.
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class TaskSearchEngine:
    """Motor de búsqueda contextual para tareas usando RAG"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Inicializar el motor de búsqueda"""
        self.model_name = model_name
        self.model = None
        self.index = None
        self.task_texts = []
        self.task_ids = []
        self.is_initialized = False
        
    async def initialize(self):
        """Inicializar el modelo y cargar embeddings"""
        try:
            logger.info(f"🔍 Inicializando motor de búsqueda con modelo: {self.model_name}")
            # Importar dependencias pesadas solo cuando se inicializa
            from sentence_transformers import SentenceTransformer  # type: ignore
            self.model = SentenceTransformer(self.model_name)
            self.is_initialized = True
            logger.info("✅ Motor de búsqueda inicializado correctamente")
        except Exception as e:
            logger.error(f"❌ Error inicializando motor de búsqueda: {e}")
            self.is_initialized = False
    
    def _prepare_task_text(self, task: Dict[str, Any]) -> str:
        """Preparar texto de tarea para embeddings - VERSION MEJORADA"""
        text_parts = []
        
        # Nombre de la tarea
        if task.get('name'):
            text_parts.append(f"Nombre: {task['name']}")
        
        # Descripción
        if task.get('description'):
            text_parts.append(f"Descripción: {task['description']}")
        
        # Usuario asignado - MEJORADO para incluir ID y nombre
        if task.get('assignee_name'):
            text_parts.append(f"Usuario: {task['assignee_name']}")
            # También agregar el nombre como texto simple para búsquedas
            text_parts.append(f"{task['assignee_name']}")
        
        if task.get('assignee_id'):
            text_parts.append(f"UsuarioID: {task['assignee_id']}")
            # También agregar el ID como texto simple para búsquedas
            text_parts.append(f"{task['assignee_id']}")
        
        # Estado
        if task.get('status'):
            text_parts.append(f"Estado: {task['status']}")
        
        # Prioridad
        if task.get('priority'):
            text_parts.append(f"Prioridad: {task['priority']}")
        
        # Campos personalizados
        if task.get('custom_fields'):
            custom_fields = task['custom_fields']
            if isinstance(custom_fields, dict):
                for field_name, field_value in custom_fields.items():
                    if field_value:
                        text_parts.append(f"{field_name}: {field_value}")
            elif isinstance(custom_fields, list):
                for field in custom_fields:
                    if isinstance(field, dict) and field.get('value'):
                        text_parts.append(f"Campo: {field['value']}")
        
        # Tags
        if task.get('tags'):
            text_parts.append(f"Tags: {', '.join(task['tags'])}")
        
        # Lista y workspace
        if task.get('list_name'):
            text_parts.append(f"Lista: {task['list_name']}")
        
        if task.get('workspace_name'):
            text_parts.append(f"Workspace: {task['workspace_name']}")
        
        # Fechas
        if task.get('due_date'):
            text_parts.append(f"Fecha límite: {task['due_date']}")
        
        if task.get('created_at'):
            text_parts.append(f"Creada: {task['created_at']}")
        
        final_text = " | ".join(text_parts)
        logger.debug(f"🔍 Texto preparado para tarea {task.get('id', 'unknown')}: {final_text[:200]}...")
        
        return final_text
    
    def build_search_index(self, tasks: List[Dict[str, Any]]):
        """Construir índice de búsqueda desde las tareas"""
        if not self.is_initialized:
            logger.warning("⚠️ Motor de búsqueda no inicializado")
            return
        
        try:
            # Importar dependencias pesadas aquí para evitar fallos en import del módulo
            import numpy as np  # type: ignore
            import faiss  # type: ignore
            logger.info(f"🔍 Construyendo índice de búsqueda para {len(tasks)} tareas")
            
            # Preparar textos de tareas
            self.task_texts = []
            self.task_ids = []
            
            for i, task in enumerate(tasks):
                task_id = task.get('id') or task.get('clickup_id')
                logger.info(f"🔍 Procesando tarea {i+1}/{len(tasks)}: {task_id}")
                
                task_text = self._prepare_task_text(task)
                if task_text.strip():
                    self.task_texts.append(task_text)
                    self.task_ids.append(task_id)
                    logger.info(f"✅ Tarea {task_id} indexada con {len(task_text)} caracteres")
                else:
                    logger.warning(f"⚠️ Tarea {task_id} no tiene texto válido")
            
            if not self.task_texts:
                logger.warning("⚠️ No hay textos válidos para indexar")
                return
            
            logger.info(f"🔍 Total de tareas a indexar: {len(self.task_texts)}")
            logger.info(f"🔍 IDs de tareas: {self.task_ids}")
            
            # Generar embeddings
            logger.info("📊 Generando embeddings...")
            embeddings = self.model.encode(self.task_texts, show_progress_bar=True)
            
            # Normalizar embeddings
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            
            # Crear índice FAISS
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner Product para similitud coseno
            self.index.add(embeddings.astype('float32'))
            
            logger.info(f"✅ Índice de búsqueda construido: {len(self.task_texts)} tareas indexadas")
            
        except Exception as e:
            logger.error(f"❌ Error construyendo índice de búsqueda: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
    
    def search_tasks(self, query: str, top_k: int = 10, threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Buscar tareas usando similitud semántica - VERSION ULTRA SIMPLIFICADA"""
        if not self.is_initialized or self.index is None:
            logger.warning("⚠️ Motor de búsqueda no inicializado o índice no construido")
            return []
        
        try:
            logger.info(f"🔍 Iniciando búsqueda ULTRA SIMPLIFICADA para: '{query}'")
            logger.info(f"🔍 Tareas indexadas: {len(self.task_texts)}")
            logger.info(f"🔍 IDs de tareas: {self.task_texts[:2] if self.task_texts else 'Ninguna'}")
            
            # BÚSQUEDA ULTRA SIMPLIFICADA: Devolver TODAS las tareas para debug
            results = []
            
            # Por ahora, devolver todas las tareas para ver qué está pasando
            for i, (task_id, task_text) in enumerate(zip(self.task_ids, self.task_texts)):
                logger.info(f"🔍 Procesando tarea {i+1}: {task_id}")
                logger.info(f"🔍 Texto de tarea: {task_text[:100]}...")
                
                # Asignar un score simple basado en el índice
                score = 1.0 - (i * 0.1)  # Score decreciente
                
                results.append({
                    'task_id': task_id,
                    'score': score,
                    'text': task_text
                })
                logger.info(f"✅ Tarea {task_id} agregada con score {score}")
            
            # Ordenar por score
            results.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"🔍 Búsqueda ULTRA SIMPLIFICADA completada: {len(results)} resultados para '{query}'")
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda ULTRA SIMPLIFICADA: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return []
    
    def _is_user_query(self, query: str) -> bool:
        """Detectar si la consulta es para buscar por usuario - VERSION MEJORADA"""
        # Si es solo números, probablemente es un ID de usuario
        if query.isdigit():
            logger.info(f"🔍 Query '{query}' detectado como ID numérico")
            return True
        
        # Si contiene palabras clave de usuario
        user_keywords = ['usuario', 'user', 'asignado', 'assigned', 'member', 'miembro']
        query_lower = query.lower()
        
        for keyword in user_keywords:
            if keyword in query_lower:
                logger.info(f"🔍 Query '{query}' detectado como palabra clave de usuario: {keyword}")
                return True
        
        # Si es un nombre típico (primera letra mayúscula, sin espacios, longitud razonable)
        if query and query[0].isupper() and ' ' not in query and 2 <= len(query) <= 15:
            # Excluir palabras comunes que no son nombres
            common_words = ['escoger', 'task', 'tarea', 'módulo', 'proyecto', 'lista', 'workspace']
            if query.lower() not in common_words:
                logger.info(f"🔍 Query '{query}' detectado como nombre de usuario")
                return True
        
        logger.info(f"🔍 Query '{query}' NO detectado como búsqueda por usuario")
        return False
    
    def search_by_criteria(self, 
                          name: Optional[str] = None,
                          description: Optional[str] = None,
                          user: Optional[str] = None,
                          status: Optional[str] = None,
                          priority: Optional[str] = None,
                          tags: Optional[List[str]] = None,
                          custom_fields: Optional[Dict[str, str]] = None,
                          top_k: int = 20) -> List[Dict[str, Any]]:
        """Búsqueda avanzada por criterios específicos"""
        
        # Construir consulta compuesta
        query_parts = []
        
        if name:
            query_parts.append(f"nombre: {name}")
        
        if description:
            query_parts.append(f"descripción: {description}")
        
        # Mejorar búsqueda por usuario - incluir tanto nombre como ID
        if user:
            query_parts.append(f"usuario: {user}")
            query_parts.append(f"UsuarioID: {user}")
        
        if status:
            query_parts.append(f"estado: {status}")
        
        if priority:
            query_parts.append(f"prioridad: {priority}")
        
        if tags:
            query_parts.append(f"tags: {', '.join(tags)}")
        
        if custom_fields:
            for field_name, field_value in custom_fields.items():
                query_parts.append(f"{field_name}: {field_value}")
        
        if not query_parts:
            return []
        
        query = " | ".join(query_parts)
        return self.search_tasks(query, top_k=top_k)
    
    def get_search_suggestions(self, partial_query: str, max_suggestions: int = 5) -> List[str]:
        """Obtener sugerencias de búsqueda basadas en consulta parcial"""
        if not self.is_initialized or not self.task_texts:
            return []
        
        try:
            suggestions = []
            partial_lower = partial_query.lower()
            
            # Buscar en textos de tareas
            for text in self.task_texts:
                words = text.lower().split()
                for word in words:
                    if word.startswith(partial_lower) and len(word) > len(partial_lower):
                        if word not in suggestions:
                            suggestions.append(word)
                            if len(suggestions) >= max_suggestions:
                                break
                if len(suggestions) >= max_suggestions:
                    break
            
            return suggestions[:max_suggestions]
            
        except Exception as e:
            logger.error(f"❌ Error generando sugerencias: {e}")
            return []
    
    def update_task(self, task_id: str, task_data: Dict[str, Any]):
        """Actualizar una tarea en el índice (para búsquedas en tiempo real)"""
        # Nota: Para implementación completa, se necesitaría reconstruir el índice
        # o implementar actualizaciones incrementales
        logger.info(f"🔄 Actualizando tarea {task_id} en índice de búsqueda")
        # Por ahora, marcamos que se necesita reconstruir el índice
        self.index = None
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del motor de búsqueda"""
        return {
            'is_initialized': self.is_initialized,
            'model_name': self.model_name,
            'indexed_tasks': len(self.task_texts) if self.task_texts else 0,
            'index_exists': self.index is not None,
            'last_update': datetime.now().isoformat()
        }
    
    def search_by_user(self, user_query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """Búsqueda especializada por usuario (nombre o ID) - VERSION MEJORADA"""
        if not self.is_initialized or self.index is None:
            logger.warning("⚠️ Motor de búsqueda no inicializado para búsqueda por usuario")
            return []
        
        try:
            logger.info(f"🔍 Iniciando búsqueda especializada por usuario: {user_query}")
            
            # Crear consultas específicas para usuario con diferentes estrategias
            user_queries = []
            
            # Si es un ID numérico
            if user_query.isdigit():
                user_queries.extend([
                    f"UsuarioID: {user_query}",
                    f"Usuario: {user_query}",
                    f"asignado {user_query}"
                ])
                logger.info(f"🔍 Consultas para ID numérico: {user_queries}")
            else:
                # Si es un nombre
                user_queries.extend([
                    f"Usuario: {user_query}",
                    f"usuario {user_query}",
                    f"asignado {user_query}",
                    f"UsuarioID: {user_query}"  # Por si acaso
                ])
                logger.info(f"🔍 Consultas para nombre: {user_queries}")
            
            all_results = []
            for i, query in enumerate(user_queries):
                try:
                    logger.info(f"🔍 Ejecutando consulta {i+1}/{len(user_queries)}: '{query}'")
                    # Usar búsqueda directa para evitar recursión infinita
                    results = self._direct_search(query, top_k=top_k, threshold=0.1)
                    logger.info(f"🔍 Consulta '{query}' devolvió {len(results)} resultados")
                    all_results.extend(results)
                except Exception as e:
                    logger.warning(f"⚠️ Error en consulta '{query}': {e}")
                    continue
            
            # Eliminar duplicados y ordenar por score
            seen_ids = set()
            unique_results = []
            for result in all_results:
                if result['task_id'] not in seen_ids:
                    seen_ids.add(result['task_id'])
                    unique_results.append(result)
            
            # Ordenar por score
            unique_results.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"🔍 Búsqueda por usuario completada: {len(unique_results)} resultados únicos para '{user_query}'")
            return unique_results[:top_k]
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda por usuario: {e}")
            return []
    
    def _direct_search(self, query: str, top_k: int = 10, threshold: float = 0.1) -> List[Dict[str, Any]]:
        """Búsqueda directa sin detección automática de tipo - VERSION MEJORADA"""
        try:
            logger.info(f"🔍 Búsqueda directa para: '{query}' (threshold: {threshold})")
            
            # Generar embedding de la consulta
            import numpy as np  # type: ignore
            query_embedding = self.model.encode([query])
            query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
            logger.info(f"🔍 Embedding generado para consulta: {query_embedding.shape}")
            
            # Buscar en el índice
            scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
            logger.info(f"🔍 Búsqueda en índice: {len(scores[0])} scores, {len(indices[0])} índices")
            
            # Filtrar por umbral de similitud
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                logger.info(f"🔍 Score {i+1}: {score:.4f}, Índice: {idx}")
                if score >= threshold and idx < len(self.task_ids):
                    task_id = self.task_ids[idx]
                    task_text = self.task_texts[idx][:100] + "..." if len(self.task_texts[idx]) > 100 else self.task_texts[idx]
                    results.append({
                        'task_id': task_id,
                        'score': float(score),
                        'text': self.task_texts[idx]
                    })
                    logger.info(f"✅ Tarea {task_id} agregada (score: {score:.4f})")
                else:
                    if score < threshold:
                        logger.info(f"❌ Score {score:.4f} < threshold {threshold}")
                    if idx >= len(self.task_ids):
                        logger.info(f"❌ Índice {idx} >= {len(self.task_ids)} tareas")
            
            logger.info(f"🔍 Búsqueda directa completada: {len(results)} resultados para '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda directa: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return []

# Instancia global del motor de búsqueda
search_engine = TaskSearchEngine()
