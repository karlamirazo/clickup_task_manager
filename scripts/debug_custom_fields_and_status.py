#!/usr/bin/env python3
"""
Script para diagnosticar problemas con campos personalizados y estado en ClickUp
"""

import requests
import json
from datetime import datetime, timedelta

def debug_custom_fields_and_status():
    """Diagnosticar problemas con campos personalizados y estado"""
    print("🔍 DIAGNÓSTICO DE CAMPOS PERSONALIZADOS Y ESTADO")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # IDs reales obtenidos
    list_id = "901411770471"  # PROYECTO 1
    user_id = "88425547"      # Karla Rosas
    
    # PASO 1: Obtener información de la lista para ver campos personalizados
    print("📋 PASO 1: Obtener información de la lista")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/v1/lists/{list_id}", timeout=10)
        
        if response.status_code == 200:
            list_info = response.json()
            print(f"✅ Información de la lista obtenida")
            print(f"📝 Nombre: {list_info.get('name', 'N/A')}")
            print(f"🆔 ID: {list_info.get('id', 'N/A')}")
            
            # Verificar campos personalizados
            custom_fields = list_info.get("custom_fields", [])
            print(f"🔧 Campos personalizados en la lista: {len(custom_fields)}")
            
            for field in custom_fields:
                print(f"   📝 Campo: {field.get('name', 'N/A')} - ID: {field.get('id', 'N/A')} - Tipo: {field.get('type', 'N/A')}")
                
                # Buscar campos específicos
                field_name = field.get('name', '').lower()
                if 'email' in field_name:
                    print(f"      🎯 ¡CAMPO EMAIL ENCONTRADO! ID: {field.get('id')}")
                if 'celular' in field_name or 'phone' in field_name or 'teléfono' in field_name:
                    print(f"      🎯 ¡CAMPO CELULAR ENCONTRADO! ID: {field.get('id')}")
        else:
            print(f"❌ Error obteniendo información de la lista: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # PASO 2: Crear tarea con campos personalizados específicos
    print(f"\n🧪 PASO 2: Crear tarea con campos personalizados específicos")
    print("-" * 40)
    
    # Intentar diferentes formatos de campos personalizados
    test_formats = [
        {
            "name": "Formato 1: Campos con IDs específicos",
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
        print(f"\n🧪 Prueba {i}: {test_format['name']}")
        
        test_task_data = {
            "name": f"Tarea de diagnóstico {i} - {datetime.now().strftime('%H:%M:%S')}",
            "description": f"Tarea para diagnosticar campos personalizados - {test_format['name']}",
            "status": "in progress",  # Estado específico para probar
            "priority": 2,  # Alta prioridad
            "due_date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "assignee_id": user_id,
            "list_id": list_id,
            "workspace_id": "9014943317"
        }
        
        # Agregar campos personalizados según el formato
        if test_format["custom_fields"]:
            test_task_data["custom_fields"] = test_format["custom_fields"]
        
        print(f"📋 Datos de la tarea:")
        print(f"   📝 Nombre: {test_task_data['name']}")
        print(f"   📊 Estado: {test_task_data['status']}")
        print(f"   ⚡ Prioridad: {test_task_data['priority']}")
        print(f"   📧 Campos personalizados: {test_task_data.get('custom_fields', 'Ninguno')}")
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/tasks/",
                json=test_task_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"📡 Respuesta del servidor: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Tarea creada exitosamente")
                print(f"🆔 ID ClickUp: {result.get('clickup_id', 'N/A')}")
                print(f"📊 Estado guardado: {result.get('status', 'N/A')}")
                print(f"📧 Campos personalizados guardados: {result.get('custom_fields', 'N/A')}")
                
                # Verificar si los campos se guardaron correctamente
                if result.get('custom_fields'):
                    print(f"✅ Campos personalizados se guardaron en BD local")
                else:
                    print(f"⚠️ Campos personalizados NO se guardaron en BD local")
                    
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # PASO 3: Verificar errores en la interfaz
    print(f"\n🌐 PASO 3: Verificar errores en la interfaz")
    print("-" * 40)
    
    # Probar endpoints que pueden estar causando errores 500
    endpoints_to_test = [
        "/api/v1/lists",
        "/api/v1/users",
        "/api/v1/workspaces",
        "/api/v1/tasks/",
        "/api/v1/tasks/sync"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            print(f"🔍 Probando: {endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 500:
                print(f"   ❌ ERROR 500 detectado!")
                print(f"   📄 Respuesta: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_clickup_api_directly():
    """Probar la API de ClickUp directamente"""
    print(f"\n🔗 PASO 4: Probar API de ClickUp directamente")
    print("-" * 40)
    
    # Nota: Esto requeriría el CLICKUP_API_TOKEN
    print("⚠️ Para probar directamente la API de ClickUp, necesitaríamos el CLICKUP_API_TOKEN")
    print("💡 Esto nos permitiría ver exactamente qué está enviando nuestra aplicación")
    
    # Simular lo que debería enviarse a ClickUp
    print(f"\n📤 Lo que debería enviarse a ClickUp:")
    print(f"   📋 Lista ID: 901411770471")
    print(f"   📝 Nombre: Tarea de prueba")
    print(f"   📄 Descripción: Descripción de prueba")
    print(f"   📊 Estado: in progress")
    print(f"   ⚡ Prioridad: 2")
    print(f"   👤 Assignees: [88425547]")
    print(f"   📅 Due Date: timestamp en milisegundos")
    print(f"   📧 Custom Fields: [{'id': 'field_id', 'value': 'test@email.com'}]")

def main():
    """Función principal"""
    print("🔍 DIAGNÓSTICO COMPLETO DE CAMPOS PERSONALIZADOS Y ESTADO")
    print("=" * 70)
    
    # Diagnóstico principal
    debug_custom_fields_and_status()
    
    # Prueba directa de API
    test_clickup_api_directly()
    
    # Resumen
    print(f"\n📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 70)
    
    print(f"🔍 Problemas identificados:")
    print(f"   1. Campos personalizados pueden no estar en el formato correcto")
    print(f"   2. Estados pueden no estar mapeando correctamente")
    print(f"   3. Errores 500 en la interfaz pueden estar relacionados")
    
    print(f"\n💡 Soluciones sugeridas:")
    print(f"   1. Verificar el formato de campos personalizados en ClickUp")
    print(f"   2. Revisar el mapeo de estados")
    print(f"   3. Corregir errores 500 en endpoints de la interfaz")
    print(f"   4. Verificar que los IDs de campos personalizados sean correctos")
    
    print(f"\n🕐 Diagnóstico completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
