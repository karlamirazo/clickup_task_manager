#!/usr/bin/env python3
"""
Script para diagnosticar problemas con campos personalizados y estado en ClickUp
"""

import requests
import json
from datetime import datetime, timedelta

def debug_custom_fields_and_status():
    """Diagnosticar problemas con campos personalizados y estado"""
    print("ğŸ”� DIAGNOSTICO DE CAMPOS PERSONALIZADOS Y ESTADO")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # IDs reales obtenidos
    list_id = "901411770471"  # PROYECTO 1
    user_id = "88425547"      # Karla Rosas
    
    # PASO 1: Get informacion de la lista para ver campos personalizados
    print("ğŸ“‹ PASO 1: Get informacion de la lista")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/v1/lists/{list_id}", timeout=10)
        
        if response.status_code == 200:
            list_info = response.json()
            print(f"âœ… Informacion de la lista obtenida")
            print(f"ğŸ“� Nombre: {list_info.get('name', 'N/A')}")
            print(f"ğŸ†” ID: {list_info.get('id', 'N/A')}")
            
            # Verificar campos personalizados
            custom_fields = list_info.get("custom_fields", [])
            print(f"ğŸ”§ Campos personalizados en la lista: {len(custom_fields)}")
            
            for field in custom_fields:
                print(f"   ğŸ“� Campo: {field.get('name', 'N/A')} - ID: {field.get('id', 'N/A')} - Tipo: {field.get('type', 'N/A')}")
                
                # Buscar campos especificos
                field_name = field.get('name', '').lower()
                if 'email' in field_name:
                    print(f"      ğŸ�¯ Â¡CAMPO EMAIL ENCONTRADO! ID: {field.get('id')}")
                if 'celular' in field_name or 'phone' in field_name or 'telefono' in field_name:
                    print(f"      ğŸ�¯ Â¡CAMPO CELULAR ENCONTRADO! ID: {field.get('id')}")
        else:
            print(f"â�Œ Error getting informacion de la lista: {response.status_code}")
            
    except Exception as e:
        print(f"â�Œ Error: {e}")
    
    # PASO 2: Create tarea con campos personalizados especificos
    print(f"\nğŸ§ª PASO 2: Create tarea con campos personalizados especificos")
    print("-" * 40)
    
    # Intentar diferentes formatos de campos personalizados
    test_formats = [
        {
            "name": "Formato 1: Campos con IDs especificos",
            "custom_fields": [
                {"id": "email_field_id", "value": "test@email.com"},
                {"id": "celular_field_id", "value": "+52 55 9999 8888"}
            ]
        },
        {
            "name": "Formato 2: Campos con nombres",
            "custom_fields": {
                "Email": "test@email.com",
                "Celular": "+52 55 9999 8888"
            }
        },
        {
            "name": "Formato 3: Sin campos personalizados",
            "custom_fields": None
        }
    ]
    
    for i, test_format in enumerate(test_formats, 1):
        print(f"\nğŸ§ª Prueba {i}: {test_format['name']}")
        
        test_task_data = {
            "name": f"Tarea de diagnostico {i} - {datetime.now().strftime('%H:%M:%S')}",
            "description": f"Tarea para diagnosticar campos personalizados - {test_format['name']}",
            "status": "in progress",  # Estado especifico para probar
            "priority": 2,  # Alta prioridad
            "due_date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "assignee_id": user_id,
            "list_id": list_id,
            "workspace_id": "9014943317"
        }
        
        # Agregar campos personalizados segun el formato
        if test_format["custom_fields"]:
            test_task_data["custom_fields"] = test_format["custom_fields"]
        
        print(f"ğŸ“‹ Datos de la tarea:")
        print(f"   ğŸ“� Nombre: {test_task_data['name']}")
        print(f"   ğŸ“Š Estado: {test_task_data['status']}")
        print(f"   âš¡ Prioridad: {test_task_data['priority']}")
        print(f"   ğŸ“§ Campos personalizados: {test_task_data.get('custom_fields', 'Ninguno')}")
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/tasks/",
                json=test_task_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"ğŸ“¡ Respuesta del servidor: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                print(f"âœ… Tarea creada exitosamente")
                print(f"ğŸ†” ID ClickUp: {result.get('clickup_id', 'N/A')}")
                print(f"ğŸ“Š Estado guardado: {result.get('status', 'N/A')}")
                print(f"ğŸ“§ Campos personalizados guardados: {result.get('custom_fields', 'N/A')}")
                
                # Verificar si los campos se guardaron correctamente
                if result.get('custom_fields'):
                    print(f"âœ… Campos personalizados se guardaron en BD local")
                else:
                    print(f"âš ï¸� Campos personalizados NO se guardaron en BD local")
                    
            else:
                print(f"â�Œ Error: {response.text}")
                
        except Exception as e:
            print(f"â�Œ Error: {e}")
    
    # PASO 3: Verificar errores en la interfaz
    print(f"\nğŸŒ� PASO 3: Verificar errores en la interfaz")
    print("-" * 40)
    
    # Test endpoints que pueden estar causando errores 500
    endpoints_to_test = [
        "/api/v1/lists",
        "/api/v1/users",
        "/api/v1/workspaces",
        "/api/v1/tasks/",
        "/api/v1/tasks/sync"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            print(f"ğŸ”� Probando: {endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"   ğŸ“Š Status: {response.status_code}")
            
            if response.status_code == 500:
                print(f"   â�Œ ERROR 500 detectado!")
                print(f"   ğŸ“„ Respuesta: {response.text[:200]}")
                
        except Exception as e:
            print(f"   â�Œ Error: {e}")

def test_clickup_api_directly():
    """Test la API de ClickUp directamente"""
    print(f"\nğŸ”— PASO 4: Test API de ClickUp directamente")
    print("-" * 40)
    
    # Nota: Esto requeriria el CLICKUP_API_TOKEN
    print("âš ï¸� Para probar directamente la API de ClickUp, necesitariamos el CLICKUP_API_TOKEN")
    print("ğŸ’¡ Esto nos permitiria ver exactamente que esta enviando nuestra aplicacion")
    
    # Simular lo que deberia enviarse a ClickUp
    print(f"\nğŸ“¤ Lo que deberia enviarse a ClickUp:")
    print(f"   ğŸ“‹ Lista ID: 901411770471")
    print(f"   ğŸ“� Nombre: Tarea de prueba")
    print(f"   ğŸ“„ Descripcion: Descripcion de prueba")
    print(f"   ğŸ“Š Estado: in progress")
    print(f"   âš¡ Prioridad: 2")
    print(f"   ğŸ‘¤ Assignees: [88425547]")
    print(f"   ğŸ“… Due Date: timestamp en milisegundos")
    print(f"   ğŸ“§ Custom Fields: [{'id': 'field_id', 'value': 'test@email.com'}]")

def main():
    """Funcion principal"""
    print("ğŸ”� DIAGNOSTICO COMPLETO DE CAMPOS PERSONALIZADOS Y ESTADO")
    print("=" * 70)
    
    # Diagnostico principal
    debug_custom_fields_and_status()
    
    # Prueba directa de API
    test_clickup_api_directly()
    
    # Resumen
    print(f"\nğŸ“Š RESUMEN DEL DIAGNOSTICO")
    print("=" * 70)
    
    print(f"ğŸ”� Problemas identificados:")
    print(f"   1. Campos personalizados pueden no estar en el formato correcto")
    print(f"   2. Estados pueden no estar mapeando correctamente")
    print(f"   3. Errores 500 en la interfaz pueden estar relacionados")
    
    print(f"\nğŸ’¡ Soluciones sugeridas:")
    print(f"   1. Verificar el formato de campos personalizados en ClickUp")
    print(f"   2. Revisar el mapeo de estados")
    print(f"   3. Corregir errores 500 en endpoints de la interfaz")
    print(f"   4. Verificar que los IDs de campos personalizados sean correctos")
    
    print(f"\nğŸ•� Diagnostico completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
