"""
RAG Search Engine for ClickUp Project Manager
Allows semantic search by name, description, user, notes, etc.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGSearchEngine:
    """RAG Search Engine for semantic search in tasks"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.is_initialized = False
        self.task_texts = []
        self.task_ids = []
        self.embeddings = None
        self.index = None
        
    async def initialize(self):
        """Initialize the search engine model"""
        try:
            logger.info(f"🔍 Initializing search engine with model: {self.model_name}")
            # Import heavy dependencies here to avoid import failures
            from sentence_transformers import SentenceTransformer  # type: ignore
            self.model = SentenceTransformer(self.model_name)
            self.is_initialized = True
            logger.info("✅ Search engine initialized successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing search engine: {e}")
            self.is_initialized = False
    
    def _prepare_task_text(self, task: Dict[str, Any]) -> str:
        """Prepare task text for embeddings - SIMPLIFIED VERSION"""
        text_parts = []
        
        # Task name (most important)
        if task.get('name'):
            text_parts.append(task['name'])
        
        # Description
        if task.get('description'):
            text_parts.append(task['description'])
        
        # Assigned user
        if task.get('assignee_name'):
            text_parts.append(f"assigned to {task['assignee_name']}")
        
        if task.get('assignee_id'):
            text_parts.append(f"user {task['assignee_id']}")
        
        # Status
        if task.get('status'):
            text_parts.append(f"status {task['status']}")
        
        # Priority
        if task.get('priority'):
            text_parts.append(f"priority {task['priority']}")
        
        # Custom fields
        if task.get('custom_fields'):
            custom_fields = task['custom_fields']
            if isinstance(custom_fields, dict):
                for field_name, field_value in custom_fields.items():
                    if field_value:
                        text_parts.append(f"{field_name} {field_value}")
            elif isinstance(custom_fields, list):
                for field in custom_fields:
                    if isinstance(field, dict) and field.get('value'):
                        text_parts.append(f"field {field['value']}")
        
        # List and workspace
        if task.get('list_name'):
            text_parts.append(f"list {task['list_name']}")
        
        if task.get('workspace_name'):
            text_parts.append(f"workspace {task['workspace_name']}")
        
        # Join all parts with spaces
        final_text = " ".join(text_parts)
        
        # Ensure we have at least some text
        if not final_text.strip():
            final_text = f"task {task.get('id', 'unknown')}"
        
        logger.debug(f"🔍 Text prepared for task {task.get('id', 'unknown')}: {final_text[:200]}...")
        
        return final_text
    
    def build_search_index(self, tasks: List[Dict[str, Any]]):
        """Build search index from tasks - SIMPLIFIED VERSION"""
        logger.info(f"🔍 Building simplified search index for {len(tasks)} tasks")
        
        try:
            # Prepare task texts
            self.task_texts = []
            self.task_ids = []
            
            for i, task in enumerate(tasks):
                task_id = task.get('id') or task.get('clickup_id')
                logger.info(f"🔍 Processing task {i+1}/{len(tasks)}: {task_id}")
                
                task_text = self._prepare_task_text(task)
                if task_text.strip():
                    self.task_texts.append(task_text)
                    self.task_ids.append(task_id)
                    logger.info(f"✅ Task {task_id} indexed with {len(task_text)} characters")
                else:
                    logger.warning(f"⚠️ Task {task_id} has no valid text")
            
            if not self.task_texts:
                logger.warning("⚠️ No valid texts to index")
                return
            
            logger.info(f"🔍 Total tasks to index: {len(self.task_texts)}")
            logger.info(f"🔍 Task IDs: {self.task_ids}")
            logger.info(f"🔍 Sample task text: {self.task_texts[0][:100]}...")
            
            # Mark index as built
            self.index = True  # Simple flag for simplified version
            
            logger.info(f"✅ Simplified search index built: {len(self.task_texts)} tasks indexed")
            logger.info(f"✅ Index exists: {self.index is not None}")
            logger.info(f"✅ Task texts count: {len(self.task_texts)}")
            logger.info(f"✅ Task IDs count: {len(self.task_ids)}")
            
        except Exception as e:
            logger.error(f"❌ Error building simplified search index: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
    
    def search_tasks(self, query: str, top_k: int = 10, threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Search tasks using simple text matching - SIMPLIFIED VERSION"""
        logger.info(f"🔍 Starting simplified search for: '{query}'")
        logger.info(f"🔍 Tasks indexed: {len(self.task_texts) if self.task_texts else 0}")
        
        if not self.task_texts or not self.task_ids:
            logger.warning("⚠️ No task texts or IDs available")
            return []
        
        try:
            # Simple text-based search
            query_lower = query.lower()
            results = []
            
            for i, (task_id, task_text) in enumerate(zip(self.task_ids, self.task_texts)):
                # Calculate simple similarity score
                task_lower = task_text.lower()
                
                # Check if query words are in task text
                query_words = query_lower.split()
                matches = 0
                total_words = len(query_words)
                
                for word in query_words:
                    if word in task_lower:
                        matches += 1
                
                # Calculate score based on word matches
                if total_words > 0:
                    score = matches / total_words
                else:
                    score = 0.0
                
                # Add bonus for exact matches
                if query_lower in task_lower:
                    score += 0.5
                
                # Filter by threshold
                if score >= threshold:
                    results.append({
                        'task_id': task_id,
                        'score': score,
                        'text': task_text
                    })
                    
                    logger.info(f"✅ Task {task_id} found (score: {score:.4f})")
            
            # Sort by score
            results.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"🔍 Simplified search completed: {len(results)} results for '{query}'")
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"❌ Error in simplified search: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return []
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        return {
            "is_initialized": self.is_initialized,
            "model_name": self.model_name,
            "indexed_tasks": len(self.task_texts) if self.task_texts else 0,
            "index_exists": self.index is not None,
            "last_update": datetime.now().isoformat()
        }
    
    def _is_user_query(self, query: str) -> bool:
        """Detect if the query is for user search - IMPROVED VERSION"""
        # If it's only numbers, it's likely a user ID
        if query.isdigit():
            logger.info(f"üîç Query '{query}' detected as numeric ID")
            return True
        
        # If it contains user keywords
        user_keywords = ['user', 'assigned', 'assigned', 'member', 'member']
        query_lower = query.lower()
        
        for keyword in user_keywords:
            if keyword in query_lower:
                logger.info(f"üîç Query '{query}' detected as user keyword: {keyword}")
                return True
        
        # If it's a typical name (first letter uppercase, no spaces, reasonable length)
        if query and query[0].isupper() and ' ' not in query and 2 <= len(query) <= 15:
            # Exclude common words that are not names
            common_words = ['choose', 'task', 'task', 'module', 'project', 'list', 'workspace']
            if query.lower() not in common_words:
                logger.info(f"üîç Query '{query}' detected as user name")
                return True
        
        logger.info(f"üîç Query '{query}' NOT detected as user search")
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
        """Advanced search by specific criteria"""
        
        # Construct composite query
        query_parts = []
        
        if name:
            query_parts.append(f"name: {name}")
        
        if description:
            query_parts.append(f"description: {description}")
        
        # Improve user search - include both name and ID
        if user:
            query_parts.append(f"user: {user}")
            query_parts.append(f"UserID: {user}")
        
        if status:
            query_parts.append(f"status: {status}")
        
        if priority:
            query_parts.append(f"priority: {priority}")
        
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
        """Get search suggestions based on partial query"""
        if not self.is_initialized or not self.task_texts:
            return []
        
        try:
            suggestions = []
            partial_lower = partial_query.lower()
            
            # Search in task texts
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
            logger.error(f"‚ùå Error generating suggestions: {e}")
            return []
    
    def update_task(self, task_id: str, task_data: Dict[str, Any]):
        """Update a task in the index (for real-time searches)"""
        # Note: For full implementation, the index would need to be rebuilt
        # or incremental updates would need to be implemented
        logger.info(f"üîÑ Updating task {task_id} in search index")
        # For now, we mark that the index needs to be rebuilt
        self.index = None
    
    def search_by_user(self, user_query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """Specialized user search (name or ID) - IMPROVED VERSION"""
        if not self.is_initialized or self.index is None:
            logger.warning("‚ö†Ô∏è Search engine not initialized for user search")
            return []
        
        try:
            logger.info(f"üîç Starting specialized user search: {user_query}")
            
            # Create specific queries for user with different strategies
            user_queries = []
            
            # If it's a numeric ID
            if user_query.isdigit():
                user_queries.extend([
                    f"UserID: {user_query}",
                    f"User: {user_query}",
                    f"assigned {user_query}"
                ])
                logger.info(f"üîç Numeric ID queries: {user_queries}")
            else:
                # If it's a name
                user_queries.extend([
                    f"User: {user_query}",
                    f"user {user_query}",
                    f"assigned {user_query}",
                    f"UserID: {user_query}"  # Just in case
                ])
                logger.info(f"üîç Name queries: {user_queries}")
            
            all_results = []
            for i, query in enumerate(user_queries):
                try:
                    logger.info(f"üîç Executing query {i+1}/{len(user_queries)}: '{query}'")
                    # Use direct search to avoid infinite recursion
                    results = self._direct_search(query, top_k=top_k, threshold=0.1)
                    logger.info(f"üîç Query '{query}' returned {len(results)} results")
                    all_results.extend(results)
                except Exception as e:
                    logger.warning(f"‚ö†Ô∏è Error in query '{query}': {e}")
                    continue
            
            # Remove duplicates and sort by score
            seen_ids = set()
            unique_results = []
            for result in all_results:
                if result['task_id'] not in seen_ids:
                    seen_ids.add(result['task_id'])
                    unique_results.append(result)
            
            # Sort by score
            unique_results.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"üîç User search completed: {len(unique_results)} unique results for '{user_query}'")
            return unique_results[:top_k]
            
        except Exception as e:
            logger.error(f"‚ùå Error in user search: {e}")
            return []
    
    def _direct_search(self, query: str, top_k: int = 10, threshold: float = 0.1) -> List[Dict[str, Any]]:
        """Direct search without automatic type detection - IMPROVED VERSION"""
        try:
            logger.info(f"üîç Direct search for: '{query}' (threshold: {threshold})")
            
            # Generate embedding for the query
            import numpy as np  # type: ignore
            query_embedding = self.model.encode([query])
            query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
            logger.info(f"üîç Generated embedding for query: {query_embedding.shape}")
            
            # Search in the index
            scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
            logger.info(f"üîç Search in index: {len(scores[0])} scores, {len(indices[0])} indices")
            
            # Filter by similarity threshold
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                logger.info(f"üîç Score {i+1}: {score:.4f}, Index: {idx}")
                if score >= threshold and idx < len(self.task_ids):
                    task_id = self.task_ids[idx]
                    task_text = self.task_texts[idx][:100] + "..." if len(self.task_texts[idx]) > 100 else self.task_texts[idx]
                    results.append({
                        'task_id': task_id,
                        'score': float(score),
                        'text': self.task_texts[idx]
                    })
                    logger.info(f"✅ Task {task_id} added (score: {score:.4f})")
                else:
                    if score < threshold:
                        logger.info(f"‚ùå Score {score:.4f} < threshold {threshold}")
                    if idx >= len(self.task_ids):
                        logger.info(f"‚ùå Index {idx} >= {len(self.task_ids)} tasks")
            
            logger.info(f"üîç Direct search completed: {len(results)} results for '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"‚ùå Error in direct search: {e}")
            import traceback
            logger.error(f"‚ùå Traceback: {traceback.format_exc()}")
            return []

# Global search engine instance
search_engine = None

def get_search_engine():
    """Get or create the global search engine instance"""
    global search_engine
    if search_engine is None:
        search_engine = RAGSearchEngine()
    return search_engine

# Initialize the global instance
search_engine = get_search_engine()
