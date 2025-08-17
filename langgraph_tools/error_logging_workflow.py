#!/usr/bin/env python3
"""
Workflow de LangGraph para logging automático de errores de deployment
Integra con el sistema de logging para documentar problemas y soluciones
"""

from langgraph.graph import StateGraph, END
from datetime import datetime
from typing import Dict, Any, TypedDict
import os
import sys

# Agregar el directorio raíz al path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.deployment_logger import log_error_sync

# Definir el estado del workflow
class ErrorLoggingState(TypedDict):
    """Estado del workflow de logging de errores"""
    error_description: str
    solution_description: str
    context_info: str
    deployment_id: str
    environment: str
    severity: str
    status: str
    timestamp: str
    logging_result: Dict[str, Any]
    workflow_status: str

# Nodos del workflow
def validate_error_inputs(state: ErrorLoggingState) -> ErrorLoggingState:
    """Validar y normalizar los inputs del error"""
    
    print("🔍 Validando inputs del error...")
    
    # Valores por defecto
    state["error_description"] = state.get("error_description", "Error no especificado")
    state["solution_description"] = state.get("solution_description", "Solución no documentada")
    state["context_info"] = state.get("context_info", "Sin contexto")
    state["deployment_id"] = state.get("deployment_id", "unknown")
    state["environment"] = state.get("environment", "production")
    state["severity"] = state.get("severity", "medium")
    state["status"] = state.get("status", "resolved")
    state["timestamp"] = datetime.now().isoformat()
    
    # Validar campos obligatorios
    if not state["error_description"] or state["error_description"] == "Error no especificado":
        state["workflow_status"] = "error"
        state["logging_result"] = {"error": "error_description es obligatorio"}
        return state
    
    if not state["solution_description"] or state["solution_description"] == "Solución no documentada":
        state["workflow_status"] = "warning"
        print("⚠️ Advertencia: solution_description no especificada")
    
    print(f"✅ Inputs validados:")
    print(f"   - Error: {state['error_description'][:50]}...")
    print(f"   - Solución: {state['solution_description'][:50]}...")
    print(f"   - Entorno: {state['environment']}")
    print(f"   - Severidad: {state['severity']}")
    
    state["workflow_status"] = "validated"
    return state

def log_error_to_postgres_and_summary(state: ErrorLoggingState) -> ErrorLoggingState:
    """Registrar el error en PostgreSQL y DEPLOYMENT_SUMMARY.txt"""
    
    print("🚨 Registrando error en sistema de logging...")
    
    try:
        # Preparar datos para logging
        logging_inputs = {
            "error_description": state["error_description"],
            "solution_description": state["solution_description"],
            "context_info": state["context_info"],
            "deployment_id": state["deployment_id"],
            "environment": state["environment"],
            "severity": state["severity"],
            "status": state["status"]
        }
        
        # Usar nuestro sistema de logging
        result = log_error_sync(logging_inputs)
        
        if result["status"] == "documentado":
            state["logging_result"] = result
            state["workflow_status"] = "completed"
            print("✅ Error registrado exitosamente en ambos sistemas")
        else:
            state["logging_result"] = result
            state["workflow_status"] = "error"
            print(f"❌ Error en logging: {result.get('message', 'Error desconocido')}")
            
    except Exception as e:
        error_msg = f"Error en logging: {str(e)}"
        print(f"❌ {error_msg}")
        state["logging_result"] = {"status": "error", "message": error_msg}
        state["workflow_status"] = "error"
    
    return state

def generate_summary_report(state: ErrorLoggingState) -> ErrorLoggingState:
    """Generar reporte de resumen del error"""
    
    print("📊 Generando reporte de resumen...")
    
    try:
        # Crear reporte estructurado
        report = {
            "timestamp": state["timestamp"],
            "error_summary": state["error_description"][:100] + "..." if len(state["error_description"]) > 100 else state["error_description"],
            "solution_summary": state["solution_description"][:100] + "..." if len(state["solution_description"]) > 100 else state["solution_description"],
            "environment": state["environment"],
            "severity": state["severity"],
            "status": state["status"],
            "logging_success": state["logging_result"].get("status") == "documentado"
        }
        
        # Agregar al estado
        state["summary_report"] = report
        state["workflow_status"] = "completed"
        
        print("✅ Reporte generado exitosamente")
        print(f"   - Resumen: {report['error_summary']}")
        print(f"   - Estado: {report['status']}")
        print(f"   - Logging: {'✅ Exitoso' if report['logging_success'] else '❌ Fallido'}")
        
    except Exception as e:
        print(f"❌ Error generando reporte: {e}")
        state["workflow_status"] = "error"
    
    return state

def handle_workflow_error(state: ErrorLoggingState) -> ErrorLoggingState:
    """Manejar errores del workflow"""
    
    print("🚨 Manejando error del workflow...")
    
    # Crear entrada de error del workflow
    workflow_error = {
        "error_description": f"Error en workflow de logging: {state.get('logging_result', {}).get('message', 'Error desconocido')}",
        "solution_description": "Revisar logs del sistema y verificar configuración",
        "context_info": f"Workflow falló para error: {state.get('error_description', 'N/A')}",
        "environment": state.get("environment", "unknown"),
        "severity": "high",
        "status": "pending"
    }
    
    try:
        # Intentar logging del error del workflow
        log_error_sync(workflow_error)
        print("✅ Error del workflow registrado en sistema de logging")
    except Exception as e:
        print(f"❌ No se pudo registrar error del workflow: {e}")
    
    return state

# Función de enrutamiento
def route_workflow(state: ErrorLoggingState) -> str:
    """Determinar el siguiente nodo basado en el estado"""
    
    if state["workflow_status"] == "error":
        return "handle_workflow_error"
    elif state["workflow_status"] == "validated":
        return "log_error_to_postgres_and_summary"
    elif state["workflow_status"] == "completed":
        return "generate_summary_report"
    else:
        return "validate_error_inputs"

# Crear el workflow
def create_error_logging_workflow() -> StateGraph:
    """Crear el workflow de logging de errores"""
    
    # Crear grafo
    workflow = StateGraph(ErrorLoggingState)
    
    # Agregar nodos
    workflow.add_node("validate_error_inputs", validate_error_inputs)
    workflow.add_node("log_error_to_postgres_and_summary", log_error_to_postgres_and_summary)
    workflow.add_node("generate_summary_report", generate_summary_report)
    workflow.add_node("handle_workflow_error", handle_workflow_error)
    
    # Agregar enrutamiento condicional
    workflow.add_conditional_edges(
        "validate_error_inputs",
        route_workflow,
        {
            "log_error_to_postgres_and_summary": "log_error_to_postgres_and_summary",
            "handle_workflow_error": "handle_workflow_error"
        }
    )
    
    workflow.add_conditional_edges(
        "log_error_to_postgres_and_summary",
        route_workflow,
        {
            "generate_summary_report": "generate_summary_report",
            "handle_workflow_error": "handle_workflow_error"
        }
    )
    
    workflow.add_conditional_edges(
        "generate_summary_report",
        route_workflow,
        {
            "END": END
        }
    )
    
    workflow.add_conditional_edges(
        "handle_workflow_error",
        route_workflow,
        {
            "END": END
        }
    )
    
    # Establecer nodo inicial
    workflow.set_entry_point("validate_error_inputs")
    
    return workflow

# Función de conveniencia para uso directo
def log_error_with_workflow(error_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Función de conveniencia para usar el workflow de logging
    
    Args:
        error_data: Diccionario con información del error
        
    Returns:
        Dict con resultado del workflow
    """
    try:
        # Crear workflow
        workflow = create_error_logging_workflow()
        app = workflow.compile()
        
        # Ejecutar workflow
        result = app.invoke(error_data)
        
        return {
            "status": "success",
            "workflow_result": result,
            "final_status": result.get("workflow_status", "unknown")
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error en workflow: {str(e)}",
            "workflow_result": None
        }

# Ejemplo de uso
if __name__ == "__main__":
    print("🧪 Probando workflow de logging de errores...")
    
    # Datos de ejemplo
    sample_error = {
        "error_description": "Error de conexión a base de datos PostgreSQL",
        "solution_description": "Verificar variables de entorno DATABASE_URL y reiniciar servicio",
        "context_info": "Problema durante deployment en Railway - base de datos no accesible",
        "deployment_id": "railway-deploy-123",
        "environment": "production",
        "severity": "high",
        "status": "resolved"
    }
    
    # Ejecutar workflow
    result = log_error_with_workflow(sample_error)
    
    print(f"\n📋 Resultado del workflow:")
    print(f"   - Status: {result['status']}")
    print(f"   - Estado final: {result.get('final_status', 'N/A')}")
    
    if result["workflow_result"]:
        print(f"   - Logging exitoso: {result['workflow_result'].get('logging_result', {}).get('status') == 'documentado'}")
        if "summary_report" in result["workflow_result"]:
            report = result["workflow_result"]["summary_report"]
            print(f"   - Resumen generado: {report['error_summary'][:50]}...")
