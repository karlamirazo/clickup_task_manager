#!/usr/bin/env python3
"""
Script para demostrar el logging automatico de errores usando el workflow simple
Ejemplo: Error de conexion con ClickUp API
"""

import sys
import os

# Agregar el directorio raiz al path para importar langgraph_tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph_tools.simple_error_logging import log_error_with_graph

def main():
    """Funcion principal para logging del error de ClickUp API"""
    
    print("üöÄ Iniciando logging automatico de error de ClickUp API...")
    print("=" * 60)
    
    # Datos del error a documentar
    inputs = {
        "error_description": "Fallo la conexion con ClickUp API",
        "solution_description": "Se regenero el token y se actualizo la variable de entorno",
        "context_info": "Nodo: sync_clickup_data",
        "deployment_id": "railway-deploy-123",
        "environment": "production",
        "severity": "high",
        "status": "resolved"
    }
    
    print("üìù Datos del error a documentar:")
    print(f"   - Error: {inputs['error_description']}")
    print(f"   - Solucion: {inputs['solution_description']}")
    print(f"   - Contexto: {inputs['context_info']}")
    print(f"   - Deployment: {inputs['deployment_id']}")
    print(f"   - Entorno: {inputs['environment']}")
    print(f"   - Severidad: {inputs['severity']}")
    print(f"   - Estado: {inputs['status']}")
    print("=" * 60)
    
    try:
        # Execute el workflow de logging
        print("üîÑ Ejecutando workflow de logging...")
        result = log_error_with_graph(inputs)
        
        print("\nüìã Resultado del workflow:")
        print(f"   - Status: {result['status']}")
        print(f"   - Estado final: {result.get('final_status', 'N/A')}")
        
        if result["logging_result"]:
            logging_status = result['logging_result'].get('status')
            print(f"   - Logging exitoso: {logging_status == 'documentado'}")
            
            if logging_status == 'documentado':
                timestamp = result['logging_result'].get('timestamp', 'N/A')
                print(f"   - Timestamp: {timestamp}")
                print("   ‚úÖ Error documentado exitosamente en ambos sistemas")
            else:
                print(f"   ‚ùå Error en logging: {result['logging_result'].get('message', 'Error desconocido')}")
        
        print("=" * 60)
        
        # Verificar que se registro correctamente
        if result['status'] == 'success' and result.get('final_status') == 'documentado':
            print("üéâ ¬°Logging completado exitosamente!")
            print("   - Error registrado en base de datos")
            print("   - Error documentado en DEPLOYMENT_SUMMARY.txt")
            print("   - Workflow ejecutado sin errores")
        else:
            print("‚ö†Ô∏è Logging completado con advertencias")
            print(f"   - Estado: {result.get('final_status', 'unknown')}")
            
    except Exception as e:
        print(f"‚ùå Error executing workflow: {e}")
        import traceback
        print(f"‚ùå Traceback: {traceback.format_exc()}")
        return False
    
    return True

if __name__ == "__main__":
    print("üß™ Script de logging automatico de errores")
    print("   ClickUp Task Manager - Railway Deployment")
    print("=" * 60)
    
    success = main()
    
    if success:
        print("\n‚úÖ Script ejecutado exitosamente")
        print("üîç Verifica los logs en:")
        print("   - Base de datos: python scripts/create_deployment_logs_table.py")
        print("   - Archivo: cat DEPLOYMENT_SUMMARY.txt")
    else:
        print("\n‚ùå Script fallo")
        print("üîç Revisa los errores arriba")
    
    print("=" * 60)
