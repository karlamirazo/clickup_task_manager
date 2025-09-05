#!/usr/bin/env python3
"""
Script para verificar el estado del deployment en Railway
"""

import requests
import json
from datetime import datetime

def check_railway_deployment_status():
    """Verificar el estado del deployment en Railway"""
    print("üöÇ VERIFICACION DEL DEPLOYMENT EN RAILWAY")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # PASO 1: Verificar que la aplicacion responde
    print("üîç PASO 1: Verificar respuesta de la aplicacion")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"üì° Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("‚úÖ La aplicacion esta respondiendo correctamente")
            print(f"üìÑ Tamano de respuesta: {len(response.text)} caracteres")
        else:
            print(f"‚ùå La aplicacion no esta respondiendo correctamente")
            
    except Exception as e:
        print(f"‚ùå Error conectando a la aplicacion: {e}")
        return False
    
    # PASO 2: Verificar endpoints principales
    print(f"\nüîç PASO 2: Verificar endpoints principales")
    print("-" * 40)
    
    endpoints_to_test = [
        "/test-simple",
        "/api/v1/workspaces",
        "/api/v1/users",
        "/api/v1/tasks/",
        "/debug"
    ]
    
    working_endpoints = 0
    total_endpoints = len(endpoints_to_test)
    
    for endpoint in endpoints_to_test:
        try:
            print(f"üîç Probando: {endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"   üìä Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print(f"   ‚úÖ Funcionando")
                working_endpoints += 1
            elif response.status_code == 422:
                print(f"   ‚ö†Ô∏è Error 422 (parametros faltantes) - Normal para algunos endpoints")
            else:
                print(f"   ‚ùå Error {response.status_code}")
                
        except Exception as e:
            print(f"   ‚ùå Error: {e}")
    
    # PASO 3: Verificar funcionalidad de creacion de tareas
    print(f"\nüß™ PASO 3: Verificar creacion de tareas")
    print("-" * 40)
    
    test_task_data = {
        "name": f"Test Railway Deployment - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Tarea para verificar que el deployment en Railway funciona correctamente",
        "status": "to do",
        "priority": 3,
        "due_date": "2025-08-25",
        "assignee_id": "88425547",
        "list_id": "901411770471",
        "workspace_id": "9014943317",
        "custom_fields": {
            "Email": "test@railway.com",
            "Celular": "+52 55 9999 9999"
        }
    }
    
    try:
        print(f"üöÄ Enviando tarea de prueba...")
        response = requests.post(
            f"{base_url}/api/v1/tasks/",
            json=test_task_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"üì° Respuesta: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"‚úÖ ¬°EXITO! Tarea creada correctamente")
            print(f"üÜî ID ClickUp: {result.get('clickup_id', 'N/A')}")
            print(f"üìß Campos personalizados: {result.get('custom_fields', 'N/A')}")
            task_creation_working = True
        else:
            print(f"‚ùå Error creating tarea: {response.text}")
            task_creation_working = False
            
    except Exception as e:
        print(f"‚ùå Error: {e}")
        task_creation_working = False
    
    # PASO 4: Verificar logs de deployment
    print(f"\nüìã PASO 4: Verificar logs de deployment")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/debug", timeout=10)
        if response.status_code == 200:
            debug_info = response.json()
            print(f"‚úÖ Endpoint de debug funcionando")
            print(f"üìä Informacion del deployment:")
            print(f"   üïê Timestamp: {debug_info.get('timestamp', 'N/A')}")
            print(f"   üîß Status: {debug_info.get('status', 'N/A')}")
        else:
            print(f"‚ö†Ô∏è Endpoint de debug no disponible")
            
    except Exception as e:
        print(f"‚ùå Error accediendo a debug: {e}")
    
    # PASO 5: Resumen del estado
    print(f"\nüìä RESUMEN DEL ESTADO DEL DEPLOYMENT")
    print("=" * 60)
    
    print(f"üåê Aplicacion web:")
    print(f"   ‚úÖ URL: {base_url}")
    print(f"   ‚úÖ Respuesta: {'SI' if response.status_code == 200 else 'NO'}")
    
    print(f"\nüîå Endpoints:")
    print(f"   üìä Funcionando: {working_endpoints}/{total_endpoints}")
    print(f"   üìà Porcentaje: {(working_endpoints/total_endpoints)*100:.1f}%")
    
    print(f"\nüß™ Funcionalidad:")
    print(f"   üìù Creacion de tareas: {'‚úÖ FUNCIONANDO' if task_creation_working else '‚ùå NO FUNCIONA'}")
    print(f"   üìß Campos personalizados: {'‚úÖ FUNCIONANDO' if task_creation_working else '‚ùå NO FUNCIONA'}")
    
    print(f"\nüéØ Estado general:")
    if working_endpoints >= 3 and task_creation_working:
        print(f"   üéâ ¬°DEPLOYMENT FUNCIONANDO CORRECTAMENTE!")
        print(f"   ‚úÖ La aplicacion esta operativa")
        print(f"   ‚úÖ Los endpoints principales funcionan")
        print(f"   ‚úÖ La creacion de tareas funciona")
        print(f"   ‚úÖ Los campos personalizados funcionan")
    elif working_endpoints >= 2:
        print(f"   ‚ö†Ô∏è DEPLOYMENT PARCIALMENTE FUNCIONANDO")
        print(f"   ‚úÖ La aplicacion responde")
        print(f"   ‚ö†Ô∏è Algunos endpoints tienen problemas")
    else:
        print(f"   ‚ùå DEPLOYMENT CON PROBLEMAS")
        print(f"   ‚ùå La aplicacion no esta funcionando correctamente")
    
    print(f"\nüïê Verificacion completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Funcion principal"""
    print("üöÇ VERIFICACION COMPLETA DEL DEPLOYMENT EN RAILWAY")
    print("=" * 70)
    
    check_railway_deployment_status()

if __name__ == "__main__":
    main()
