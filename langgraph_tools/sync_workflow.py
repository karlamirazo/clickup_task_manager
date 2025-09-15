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