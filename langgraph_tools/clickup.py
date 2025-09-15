"""
Stub para clickup tools sin dependencias de langgraph
"""
import logging

class ClickUpTools:
    """
    Stub class para herramientas de ClickUp sin langgraph
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("ClickUpTools inicializado (stub)")
    
    def get_tasks(self, **kwargs):
        """Stub method para obtener tareas"""
        self.logger.info("get_tasks ejecutado (stub)")
        return {"tasks": [], "status": "success"}
    
    def create_task(self, **kwargs):
        """Stub method para crear tarea"""
        self.logger.info("create_task ejecutado (stub)")
        return {"task_id": "stub_task", "status": "success"}

def get_langgraph_tools():
    """
    Stub function para obtener herramientas de langgraph
    """
    logger = logging.getLogger(__name__)
    logger.info("LangGraph tools obtenidas (stub)")
    return {"tools": [], "status": "success"}