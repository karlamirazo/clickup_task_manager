#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema de logging de LangGraph con PostgreSQL
"""

import os
import sys
import asyncio
from datetime import datetime

# Agregar el directorio raiz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_simple_logging():
    """Test el workflow simple de logging"""
    print("üß™ Probando workflow simple de logging...")
    
    try:
        from langgraph_tools.simple_error_logging import log_error_with_graph
        
        # Datos de prueba
        test_error = {
            "error_description": "Prueba de sistema de logging con PostgreSQL",
            "solution_description": "Verificar que el logging funciona correctamente en Railway",
            "context_info": "Script de prueba: test_langgraph_logging.py",
            "deployment_id": "railway-test-123",
            "environment": "production",
            "severity": "info",
            "status": "resolved"
        }
        
        # Execute logging
        result = log_error_with_graph(test_error)
        
        print(f"‚úÖ Resultado del logging:")
        print(f"   - Status: {result['status']}")
        print(f"   - Estado final: {result.get('final_status', 'N/A')}")
        
        if result["logging_result"]:
            print(f"   - Logging exitoso: {result['logging_result'].get('status') == 'documentado'}")
            if result['logging_result'].get('status') == 'documentado':
                print(f"   - Timestamp: {result['logging_result'].get('timestamp', 'N/A')}")
        
        return result
        
    except Exception as e:
        print(f"‚ùå Error en prueba de logging simple: {e}")
        return {"status": "error", "message": str(e)}

def test_advanced_workflow():
    """Test el workflow avanzado"""
    print("\nüß™ Probando workflow avanzado...")
    
    try:
        from langgraph_tools.advanced_error_workflow import run_error_workflow
        
        # Datos de prueba
        test_error = {
            "error_description": "Prueba de workflow avanzado con PostgreSQL",
            "solution_description": "Verificar workflow completo de manejo de errores",
            "context_info": "Script de prueba: test_langgraph_logging.py - Workflow avanzado",
            "deployment_id": "railway-test-456",
            "environment": "production",
            "severity": "medium",
            "status": "pending"
        }
        
        # Execute workflow
        result = run_error_workflow(test_error)
        
        print(f"‚úÖ Resultado del workflow avanzado:")
        print(f"   - Status: {result['status']}")
        print(f"   - Paso final: {result.get('final_step', 'N/A')}")
        print(f"   - Error resuelto: {result.get('error_resolved', False)}")
        
        return result
        
    except Exception as e:
        print(f"‚ùå Error en prueba de workflow avanzado: {e}")
        return {"status": "error", "message": str(e)}

def test_complete_workflow():
    """Test el workflow completo"""
    print("\nüß™ Probando workflow completo...")
    
    try:
        from langgraph_tools.error_logging_workflow import log_error_with_workflow
        
        # Datos de prueba
        test_error = {
            "error_description": "Prueba de workflow completo con PostgreSQL",
            "solution_description": "Verificar workflow con validacion y reportes",
            "context_info": "Script de prueba: test_langgraph_logging.py - Workflow completo",
            "deployment_id": "railway-test-789",
            "environment": "production",
            "severity": "low",
            "status": "resolved"
        }
        
        # Execute workflow
        result = log_error_with_workflow(test_error)
        
        print(f"‚úÖ Resultado del workflow completo:")
        print(f"   - Status: {result['status']}")
        print(f"   - Estado final: {result.get('final_status', 'N/A')}")
        
        if result["workflow_result"] and "summary_report" in result["workflow_result"]:
            report = result["workflow_result"]["summary_report"]
            print(f"   - Resumen generado: {report['error_summary'][:50]}...")
        
        return result
        
    except Exception as e:
        print(f"‚ùå Error en prueba de workflow completo: {e}")
        return {"status": "error", "message": str(e)}

def test_direct_logging():
    """Test logging directo sin LangGraph"""
    print("\nüß™ Probando logging directo...")
    
    try:
        from utils.deployment_logger import log_error_sync
        
        # Datos de prueba
        test_error = {
            "error_description": "Prueba de logging directo con PostgreSQL",
            "solution_description": "Verificar logging directo sin LangGraph",
            "context_info": "Script de prueba: test_langgraph_logging.py - Logging directo",
            "deployment_id": "railway-test-direct",
            "environment": "production",
            "severity": "info",
            "status": "resolved"
        }
        
        # Execute logging directo
        result = log_error_sync(test_error)
        
        print(f"‚úÖ Resultado del logging directo:")
        print(f"   - Status: {result.get('status', 'N/A')}")
        print(f"   - Timestamp: {result.get('timestamp', 'N/A')}")
        
        return result
        
    except Exception as e:
        print(f"‚ùå Error en prueba de logging directo: {e}")
        return {"status": "error", "message": str(e)}

def main():
    """Funcion principal de pruebas"""
    print("üöÄ Iniciando pruebas del sistema de logging de LangGraph con PostgreSQL")
    print("=" * 70)
    
    # Verificar configuracion
    print("üîç Verificando configuracion...")
    database_url = os.getenv("DATABASE_URL", "")
    clickup_token = os.getenv("CLICKUP_API_TOKEN", "")
    
    print(f"   - DATABASE_URL: {'‚úÖ Configurado' if database_url else '‚ùå No configured'}")
    print(f"   - CLICKUP_API_TOKEN: {'‚úÖ Configurado' if clickup_token else '‚ùå No configured'}")
    
    if not database_url:
        print("‚ö†Ô∏è ADVERTENCIA: DATABASE_URL no esta configured")
        print("   El sistema usara SQLite como fallback")
    
    # Execute pruebas
    results = {}
    
    # Prueba 1: Logging simple
    results["simple"] = test_simple_logging()
    
    # Prueba 2: Workflow avanzado
    results["advanced"] = test_advanced_workflow()
    
    # Prueba 3: Workflow completo
    results["complete"] = test_complete_workflow()
    
    # Prueba 4: Logging directo
    results["direct"] = test_direct_logging()
    
    # Resumen de resultados
    print("\n" + "=" * 70)
    print("üìä RESUMEN DE PRUEBAS")
    print("=" * 70)
    
    for test_name, result in results.items():
        status = "‚úÖ EXITOSO" if result.get("status") == "success" else "‚ùå FALLIDO"
        print(f"   {test_name.upper()}: {status}")
        if result.get("status") != "success":
            print(f"      Error: {result.get('message', 'Error desconocido')}")
    
    # Verificar archivo de resumen
    print("\nüìÑ Verificando archivo DEPLOYMENT_SUMMARY.txt...")
    try:
        if os.path.exists("DEPLOYMENT_SUMMARY.txt"):
            with open("DEPLOYMENT_SUMMARY.txt", "r", encoding="utf-8") as f:
                content = f.read()
                entries = content.count("## [")
                print(f"   ‚úÖ Archivo existe con {entries} entradas de log")
        else:
            print("   ‚ùå Archivo DEPLOYMENT_SUMMARY.txt no encontrado")
    except Exception as e:
        print(f"   ‚ùå Error leyendo archivo: {e}")
    
    print("\nüéâ Pruebas completadas!")

if __name__ == "__main__":
    main()
