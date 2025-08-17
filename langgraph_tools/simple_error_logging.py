#!/usr/bin/env python3
"""
Workflow simplificado de LangGraph para logging automático de errores
Integra directamente la función de logging como nodo del grafo
"""

from langgraph.graph import StateGraph, END
from typing import Dict, Any, TypedDict
import os
import sys

# Agregar el directorio raíz al path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.deployment_logger import log_error_sync

# Definir el estado del workflow
class ErrorState(TypedDict):
    """Estado simplificado para logging de errores"""
    error_description: str
    solution_description: str
    context_info: str
    deployment_id: str
    environment: str
    severity: str
    status: str
    logging_result: Dict[str, Any]

# Nodo de logging de errores
def log_error_to_postgres_and_summary(state: ErrorState) -> ErrorState:
    """Registrar el error en PostgreSQL y DEPLOYMENT_SUMMARY.txt"""
    
    print("🚨 Registrando error en sistema de logging...")
    
    try:
        # Preparar datos para logging
        logging_inputs = {
            "error_description": state.get("error_description", "Error no especificado"),
            "solution_description": state.get("solution_description", "Solución no documentada"),
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
            print("✅ Error registrado exitosamente en ambos sistemas")
        else:
            print(f"❌ Error en logging: {result.get('message', 'Error desconocido')}")
            
    except Exception as e:
        error_msg = f"Error en logging: {str(e)}"
        print(f"❌ {error_msg}")
        state["logging_result"] = {"status": "error", "message": error_msg}
    
    return state

# Crear el grafo simplificado
def create_simple_error_logging_graph() -> StateGraph:
    """Crear un grafo simple para logging de errores"""
    
    # Crear el grafo
    graph = StateGraph(ErrorState)
    
    # Agregar el nodo de logging
    graph.add_node("log_error", log_error_to_postgres_and_summary)
    
    # Conectar directamente al final
    graph.add_edge("log_error", END)
    
    # Establecer nodo inicial
    graph.set_entry_point("log_error")
    
    return graph

# Función de conveniencia para uso directo
def log_error_with_graph(error_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Función de conveniencia para usar el grafo de logging
    
    Args:
        error_data: Diccionario con información del error
        
    Returns:
        Dict con resultado del logging
    """
    try:
        # Crear y compilar el grafo
        graph = create_simple_error_logging_graph()
        deployment_graph = graph.compile()
        
        # Ejecutar el grafo
        result = deployment_graph.invoke(error_data)
        
        return {
            "status": "success",
            "logging_result": result.get("logging_result", {}),
            "final_status": result.get("logging_result", {}).get("status", "unknown")
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error en grafo: {str(e)}",
            "logging_result": None
        }

# Ejemplo de uso
if __name__ == "__main__":
    print("🧪 Probando grafo simplificado de logging...")
    
    # Datos de ejemplo
    sample_error = {
        "error_description": "Error de sintaxis en archivo Python",
        "solution_description": "Corregir indentación y verificar sintaxis",
        "context_info": "Problema durante desarrollo local - archivo main.py",
        "deployment_id": "local-dev-123",
        "environment": "development",
        "severity": "medium",
        "status": "resolved"
    }
    
    # Ejecutar grafo
    result = log_error_with_graph(sample_error)
    
    print(f"\n📋 Resultado del grafo:")
    print(f"   - Status: {result['status']}")
    print(f"   - Estado final: {result.get('final_status', 'N/A')}")
    
    if result["logging_result"]:
        print(f"   - Logging exitoso: {result['logging_result'].get('status') == 'documentado'}")
        if result['logging_result'].get('status') == 'documentado':
            print(f"   - Timestamp: {result['logging_result'].get('timestamp', 'N/A')}")
