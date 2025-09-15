"""
Stub para rag_search_workflow sin dependencias de langgraph
"""
import logging

def run_rag_search_workflow(query: str, context: dict = None):
    """
    Stub function para workflow de búsqueda RAG sin langgraph
    """
    logger = logging.getLogger(__name__)
    logger.info(f"RAG search workflow ejecutado (stub) - Query: {query}")
    return {"results": [], "status": "success", "message": "RAG search ejecutado (stub)"}

def rebuild_search_index():
    """
    Stub function para reconstruir índice de búsqueda sin langgraph
    """
    logger = logging.getLogger(__name__)
    logger.info("Search index rebuild ejecutado (stub)")
    return {"status": "success", "message": "Índice reconstruido (stub)"}

def get_search_stats():
    """
    Stub function para obtener estadísticas de búsqueda sin langgraph
    """
    logger = logging.getLogger(__name__)
    logger.info("Search stats obtenidas (stub)")
    return {"total_documents": 0, "index_size": 0, "status": "success"}