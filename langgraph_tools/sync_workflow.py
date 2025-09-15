"""
Stub para sync_workflow sin dependencias de langgraph
"""
import logging

def run_sync_workflow(workflow_data: dict = None):
    """
    Stub function para workflow de sincronización sin langgraph
    """
    logger = logging.getLogger(__name__)
    logger.info("Sync workflow ejecutado (stub)")
    return {"status": "success", "message": "Workflow ejecutado (stub)"}

def create_sync_workflow(workflow_config: dict = None):
    """
    Stub function para crear workflow de sincronización sin langgraph
    """
    logger = logging.getLogger(__name__)
    logger.info("Sync workflow creado (stub)")
    return {"workflow_id": "stub_workflow", "status": "created"}