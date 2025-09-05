#!/usr/bin/env python3
"""
Script para probar la funcionalidad de la tabla mejorada
"""

import requests
import json
import sys
import os

# Agregar el directorio raiz al path
sys.path.insert(0, os.getcwd())

def test_enhanced_table():
    """Test la tabla mejorada con datos enriquecidos"""
    
    print("ğŸ§ª Probando tabla mejorada...")
    
    try:
        # Test endpoint de tareas con datos enriquecidos
        response = requests.get("http://localhost:8000/api/v1/tasks/?include_closed=true&limit=10")
        
        if response.status_code == 200:
            data = response.json()
            tasks = data.get('tasks', [])
            
            print(f"âœ… Se obtuvieron {len(tasks)} tareas")
            
            if tasks:
                print("\nğŸ“‹ Detalles de la primera tarea:")
                task = tasks[0]
                
                print(f"   ğŸ“� Nombre: {task.get('name', 'N/A')}")
                print(f"   ğŸ“Š Estado: {task.get('status', 'N/A')}")
                print(f"   âš¡ Prioridad: {task.get('priority', 'N/A')}")
                print(f"   ğŸ‘¤ Asignado: {task.get('assignee_name', 'N/A')}")
                print(f"   ğŸ“… Fecha Creacion: {task.get('created_at', 'N/A')}")
                print(f"   ğŸ“‹ Lista: {task.get('list_name', 'N/A')}")
                print(f"   ğŸ�¢ Workspace: {task.get('workspace_name', 'N/A')}")
                print(f"   ğŸ†” ID: {task.get('clickup_id', 'N/A')}")
                
                # Verificar que los campos enriquecidos esten presentes
                enriched_fields = ['assignee_name', 'list_name', 'workspace_name']
                missing_fields = [field for field in enriched_fields if not task.get(field)]
                
                if missing_fields:
                    print(f"âš ï¸�  Campos faltantes: {missing_fields}")
                else:
                    print("âœ… Todos los campos enriquecidos estan presentes")
                
            else:
                print("âš ï¸�  No hay tareas para mostrar")
                
        else:
            print(f"â�Œ Error en la respuesta: {response.status_code}")
            print(f"   Detalle: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("â�Œ No se pudo conectar al servidor. Asegurate de que este ejecutandose en http://localhost:8000")
    except Exception as e:
        print(f"â�Œ Error inesperado: {e}")

def test_report_generation():
    """Test la generacion de reportes con la tabla mejorada"""
    
    print("\nğŸ“Š Probando generacion de reportes...")
    
    try:
        # Create un reporte
        report_data = {
            "name": "Test Enhanced Table",
            "description": "Reporte para probar la tabla mejorada",
            "workspace_id": None,
            "report_type": "task_summary"
        }
        
        response = requests.post("http://localhost:8000/api/v1/reports/", json=report_data)
        
        if response.status_code == 201:
            report = response.json()
            report_id = report.get('id')
            
            print(f"âœ… Reporte creado con ID: {report_id}")
            
            # Generar el reporte
            generate_response = requests.post(f"http://localhost:8000/api/v1/reports/{report_id}/generate")
            
            if generate_response.status_code == 200:
                report_data = generate_response.json()
                
                print("âœ… Reporte generado exitosamente")
                print(f"   ğŸ“Š Total tareas: {report_data.get('total_tasks', 0)}")
                print(f"   âœ… Completadas: {report_data.get('completed_tasks', 0)}")
                print(f"   â�³ Pendientes: {report_data.get('pending_tasks', 0)}")
                
                # Verificar que los datos de distribucion esten presentes
                if 'status_distribution' in report_data:
                    print(f"   ğŸ“ˆ Distribucion de estados: {report_data['status_distribution']}")
                
                if 'priority_distribution' in report_data:
                    print(f"   âš¡ Distribucion de prioridades: {report_data['priority_distribution']}")
                
                if 'assignee_distribution' in report_data:
                    print(f"   ğŸ‘¤ Distribucion de asignados: {report_data['assignee_distribution']}")
                
            else:
                print(f"â�Œ Error generando reporte: {generate_response.status_code}")
                print(f"   Detalle: {generate_response.text}")
        else:
            print(f"â�Œ Error creating reporte: {response.status_code}")
            print(f"   Detalle: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("â�Œ No se pudo conectar al servidor")
    except Exception as e:
        print(f"â�Œ Error inesperado: {e}")

if __name__ == "__main__":
    print("ğŸš€ Iniciando pruebas de tabla mejorada...\n")
    
    test_enhanced_table()
    test_report_generation()
    
    print("\nâœ¨ Pruebas completadas!")
