#!/usr/bin/env python3
"""
Workflow avanzado de LangGraph que demuestra la integracion del nodo de logging
con otros nodos del workflow, siguiendo el patron solicitado
"""

from langgraph.graph import StateGraph, END
from typing import Dict, Any, TypedDict
import os
import sys

# Agregar el directorio raiz al path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.deployment_logger import log_error_sync

# Definir el estado del workflow
class WorkflowState(TypedDict):
    """Estado del workflow avanzado"""
    error_description: str
    solution_description: str
    context_info: str
    deployment_id: str
    environment: str
    severity: str
    status: str
    logging_result: Dict[str, Any]
    workflow_step: str
    error_handled: bool

# Nodo de manejo de errores
def error_handler(state: WorkflowState) -> WorkflowState:
    """Manejar y clasificar el error"""
    
    print("ðŸš¨ Manejando error en workflow...")
    
    # Clasificar el error por severidad
    severity = state.get("severity", "medium")
    if severity == "high":
        print("   âš ï¸� Error de alta severidad detectado")
        state["workflow_step"] = "critical_error"
    elif severity == "medium":
        print("   âš ï¸� Error de severidad media detectado")
        state["workflow_step"] = "standard_error"
    else:
        print("   â„¹ï¸� Error de baja severidad detectado")
        state["workflow_step"] = "minor_error"
    
    state["error_handled"] = True
    print(f"   âœ… Error clasificado como: {state['workflow_step']}")
    
    return state

# Nodo de logging de errores
def log_error_to_postgres_and_summary(state: WorkflowState) -> WorkflowState:
    """Registrar el error en PostgreSQL y DEPLOYMENT_SUMMARY.txt"""
    
    print("ðŸ“� Registrando error en sistema de logging...")
    
    try:
        # Preparar datos para logging
        logging_inputs = {
            "error_description": state.get("error_description", "Error no especificado"),
            "solution_description": state.get("solution_description", "Solucion no documentada"),
            "context_info": state.get("context_info", "Sin contexto"),
            "deployment_id": state.get("deployment_id", "unknown"),
            "environment": state.get("environment", "production"),
            "severity": state.get("severity", "medium"),
            "status": state.get("status", "resolved")
        }
        
        # Usar nuestro sistema de logging
        result = log_error_sync(logging_inputs)
        
        # Agregar resultado al estado
        state["logging_result"] = result
        
        if result["status"] == "documentado":
            print("   âœ… Error registrado exitosamente en ambos sistemas")
            state["workflow_step"] = "logged"
        else:
            print(f"   â�Œ Error en logging: {result.get('message', 'Error desconocido')}")
            state["workflow_step"] = "error"
            
    except Exception as e:
        error_msg = f"Error en logging: {str(e)}"
        print(f"   â�Œ {error_msg}")
        state["logging_result"] = {"status": "error", "message": error_msg}
    
    return state

# Nodo de notificacion
def notify_team(state: WorkflowState) -> WorkflowState:
    """Notificar al equipo sobre el error"""
    
    print("ðŸ“¢ Notificando al equipo...")
    
    severity = state.get("severity", "medium")
    if severity == "high":
        print("   ðŸš¨ Notificacion URGENTE enviada al equipo")
    elif severity == "medium":
        print("   âš ï¸� Notificacion de advertencia enviada")
    else:
        print("   â„¹ï¸� Notificacion informativa enviada")
    
    state["workflow_step"] = "notified"
    return state

# Nodo de resolucion
def resolve_error(state: WorkflowState) -> WorkflowState:
    """Marcar el error como resuelto"""
    
    print("âœ… Resolviendo error...")
    
    # Update estado
    state["status"] = "resolved"
    state["workflow_step"] = "completed"
    
    print("   âœ… Error marcado como resuelto")
    
    return state

# Funcion de enrutamiento
def route_workflow(state: WorkflowState) -> str:
    """Determinar el siguiente nodo basado en el estado"""
    
    step = state.get("workflow_step", "start")
    
    if step == "start":
        return "error_handler"
    elif step == "critical_error":
        return "log_error"
    elif step == "standard_error":
        return "log_error"
    elif step == "minor_error":
        return "log_error"
    elif step == "logged":
        return "notify_team"
    elif step == "notified":
        return "resolve_error"
    elif step == "completed":
        return END
    else:
        return "log_error_to_postgres_and_summary"

# Create el grafo avanzado
def create_advanced_error_workflow() -> StateGraph:
    """Create el workflow avanzado de manejo de errores"""
    
    # Create el grafo
    graph = StateGraph(WorkflowState)
    
    # Agregar nodos
    graph.add_node("error_handler", error_handler)
    graph.add_node("log_error", log_error_to_postgres_and_summary)
    graph.add_node("notify_team", notify_team)
    graph.add_node("resolve_error", resolve_error)
    
    # Conectar nodos con enrutamiento condicional
    graph.add_conditional_edges(
        "error_handler",
        route_workflow,
        {
            "log_error": "log_error"
        }
    )
    
    graph.add_conditional_edges(
        "log_error",
        route_workflow,
        {
            "notify_team": "notify_team"
        }
    )
    
    graph.add_conditional_edges(
        "notify_team",
        route_workflow,
        {
            "resolve_error": "resolve_error"
        }
    )
    
    graph.add_conditional_edges(
        "resolve_error",
        route_workflow,
        {
            "END": END
        }
    )
    
    # Establecer nodo inicial
    graph.set_entry_point("error_handler")
    
    return graph

# Funcion de conveniencia para uso directo
def run_error_workflow(error_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute el workflow completo de manejo de errores
    
    Args:
        error_data: Diccionario con informacion del error
        
    Returns:
        Dict con resultado del workflow
    """
    try:
        # Create y compilar el grafo
        graph = create_advanced_error_workflow()
        deployment_graph = graph.compile()
        
        # Execute el workflow
        result = deployment_graph.invoke(error_data)
        
        return {
            "status": "success",
            "workflow_result": result,
            "final_step": result.get("workflow_step", "unknown"),
            "error_resolved": result.get("status") == "resolved"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error en workflow: {str(e)}",
            "workflow_result": None
        }

# Ejemplo de uso
if __name__ == "__main__":
    print("ðŸ§ª Probando workflow avanzado de manejo de errores...")
    
    # Datos de ejemplo
    sample_error = {
        "error_description": "Error critico en endpoint de autenticacion",
        "solution_description": "Reiniciar servicio de autenticacion y verificar tokens",
        "context_info": "Problema en produccion - usuarios no pueden iniciar sesion",
        "deployment_id": "railway-prod-456",
        "environment": "production",
        "severity": "high",
        "status": "pending"
    }
    
    # Execute workflow completo
    result = run_error_workflow(sample_error)
    
    print(f"\nðŸ“‹ Resultado del workflow:")
    print(f"   - Status: {result['status']}")
    print(f"   - Paso final: {result.get('final_step', 'N/A')}")
    print(f"   - Error resuelto: {result.get('error_resolved', False)}")
    
    if result["workflow_result"]:
        print(f"   - Logging exitoso: {result['workflow_result'].get('logging_result', {}).get('status') == 'documentado'}")
        print(f"   - Estado final: {result['workflow_result'].get('status', 'N/A')}")
