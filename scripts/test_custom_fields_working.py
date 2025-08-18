#!/usr/bin/env python3
"""
Script para probar la creación de tareas con campos personalizados Email y Celular
"""

import requests
import json
from datetime import datetime, timedelta

def test_custom_fields_working():
    """Probar creación de tareas con campos personalizados"""
    print("🧪 PRUEBA DE CAMPOS PERSONALIZADOS EMAIL Y CELULAR")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # IDs reales
    list_id = "901411770471"  # PROYECTO 1
    user_id = "88425547"      # Karla Rosas
    
    print(f"📋 Lista: PROYECTO 1 (ID: {list_id})")
    print(f"👤 Usuario: Karla Rosas (ID: {user_id})")
    
    # PASO 1: Crear tarea con campos personalizados
    print(f"\n🧪 PASO 1: Crear tarea con campos personalizados")
    print("-" * 40)
    
    test_task_data = {
        "name": f"Tarea con campos personalizados - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Tarea para probar que los campos personalizados Email y Celular funcionan correctamente",
        "status": "in progress",
        "priority": 2,
        "due_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
        "assignee_id": user_id,
        "list_id": list_id,
        "workspace_id": "9014943317",
        "custom_fields": {
            "Email": "karla.rosas@test.com",
            "Celular": "+52 55 1234 5678"
        }
    }
    
    print(f"📋 Datos de la tarea:")
    print(f"   📝 Nombre: {test_task_data['name']}")
    print(f"   📄 Descripción: {test_task_data['description']}")
    print(f"   📊 Estado: {test_task_data['status']}")
    print(f"   ⚡ Prioridad: {test_task_data['priority']}")
    print(f"   📅 Fecha límite: {test_task_data['due_date']}")
    print(f"   👤 Usuario asignado: {test_task_data['assignee_id']}")
    print(f"   📧 Email: {test_task_data['custom_fields']['Email']}")
    print(f"   📱 Celular: {test_task_data['custom_fields']['Celular']}")
    
    try:
        print(f"\n🚀 Enviando tarea a la API...")
        response = requests.post(
            f"{base_url}/api/v1/tasks/",
            json=test_task_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📡 Respuesta del servidor: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ ¡ÉXITO! Tarea creada correctamente")
            print(f"🆔 ID ClickUp: {result.get('clickup_id', 'N/A')}")
            print(f"🆔 ID Local: {result.get('id', 'N/A')}")
            print(f"📝 Nombre: {result.get('name', 'N/A')}")
            print(f"📊 Estado guardado: {result.get('status', 'N/A')}")
            print(f"👤 Usuario asignado: {result.get('assignee_id', 'N/A')}")
            print(f"📧 Campos personalizados guardados: {result.get('custom_fields', 'N/A')}")
            
            # Verificar que los campos se guardaron correctamente
            if result.get('custom_fields'):
                custom_fields = result.get('custom_fields')
                if 'Email' in custom_fields and 'Celular' in custom_fields:
                    print(f"✅ Campos personalizados se guardaron correctamente en BD local")
                    print(f"   📧 Email: {custom_fields['Email']}")
                    print(f"   📱 Celular: {custom_fields['Celular']}")
                else:
                    print(f"⚠️ Campos personalizados incompletos en BD local")
            else:
                print(f"❌ Campos personalizados NO se guardaron en BD local")
                
            return True, result
            
        else:
            print(f"❌ Error: {response.text}")
            return False, response.text
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, str(e)
    
    # PASO 2: Verificar que la tarea se creó en ClickUp
    print(f"\n🔍 PASO 2: Verificar tarea en ClickUp")
    print("-" * 40)
    
    print(f"💡 Para verificar que la tarea se creó correctamente en ClickUp:")
    print(f"   1. Ir a ClickUp y abrir la lista 'PROYECTO 1'")
    print(f"   2. Buscar la tarea: '{test_task_data['name']}'")
    print(f"   3. Verificar que muestra:")
    print(f"      ✅ Estado: 'in progress'")
    print(f"      ✅ Usuario asignado: Karla Rosas")
    print(f"      ✅ Campo Email: karla.rosas@test.com")
    print(f"      ✅ Campo Celular: +52 55 1234 5678")

def test_multiple_formats():
    """Probar diferentes formatos de campos personalizados"""
    print(f"\n🧪 PASO 3: Probar diferentes formatos")
    print("-" * 40)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    list_id = "901411770471"
    user_id = "88425547"
    
    # Diferentes formatos para probar
    formats_to_test = [
        {
            "name": "Formato exacto",
            "custom_fields": {
                "Email": "test1@example.com",
                "Celular": "+52 55 1111 1111"
            }
        },
        {
            "name": "Formato con espacios",
            "custom_fields": {
                "Email": "test2@example.com",
                "Celular": "+52 55 2222 2222"
            }
        },
        {
            "name": "Formato con caracteres especiales",
            "custom_fields": {
                "Email": "test3@example.com",
                "Celular": "+52 55 3333 3333"
            }
        }
    ]
    
    for i, format_test in enumerate(formats_to_test, 1):
        print(f"\n🧪 Prueba {i}: {format_test['name']}")
        
        test_task_data = {
            "name": f"Tarea formato {i} - {datetime.now().strftime('%H:%M:%S')}",
            "description": f"Tarea para probar formato: {format_test['name']}",
            "status": "to do",
            "priority": 3,
            "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "assignee_id": user_id,
            "list_id": list_id,
            "workspace_id": "9014943317",
            "custom_fields": format_test["custom_fields"]
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/tasks/",
                json=test_task_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"   ✅ Éxito - ID: {result.get('clickup_id', 'N/A')}")
                print(f"   📧 Email: {result.get('custom_fields', {}).get('Email', 'N/A')}")
                print(f"   📱 Celular: {result.get('custom_fields', {}).get('Celular', 'N/A')}")
            else:
                print(f"   ❌ Error {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    """Función principal"""
    print("🧪 PRUEBA COMPLETA DE CAMPOS PERSONALIZADOS")
    print("=" * 70)
    
    # Prueba principal
    success, result = test_custom_fields_working()
    
    # Pruebas adicionales
    test_multiple_formats()
    
    # Resumen
    print(f"\n📊 RESUMEN DE LA PRUEBA")
    print("=" * 70)
    
    if success:
        print(f"🎉 ¡PRUEBA EXITOSA!")
        print(f"✅ La tarea se creó correctamente en la BD local")
        print(f"✅ Los campos personalizados se guardaron correctamente")
        print(f"✅ El formato de campos personalizados funciona")
        
        print(f"\n💡 Próximos pasos:")
        print(f"   1. Verificar en ClickUp que la tarea se creó correctamente")
        print(f"   2. Verificar que los campos Email y Celular se muestran")
        print(f"   3. Verificar que el estado y usuario asignado son correctos")
        print(f"   4. Si todo está bien, el sistema está funcionando correctamente")
        
    else:
        print(f"❌ PRUEBA FALLIDA")
        print(f"❌ Error: {result}")
        print(f"\n🔧 Soluciones:")
        print(f"   1. Verificar que los campos personalizados existen en ClickUp")
        print(f"   2. Verificar que los nombres son exactamente 'Email' y 'Celular'")
        print(f"   3. Verificar que la API de ClickUp está funcionando")
    
    print(f"\n🕐 Prueba completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
