"""
Stub para simple_error_logging sin dependencias de langgraph
"""
import logging

def log_error_with_graph(error_message: str, context: dict = None):
    """
    Stub function para logging de errores sin langgraph
    """
    logger = logging.getLogger(__name__)
    logger.error(f"Error: {error_message}")
    if context:
        logger.error(f"Context: {context}")
    return True