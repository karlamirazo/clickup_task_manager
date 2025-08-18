#!/usr/bin/env python3
"""
Script para crear campos personalizados Email y Celular en ClickUp
"""

import requests
import json
from datetime import datetime

def create_custom_fields_in_clickup():
    """Crear campos personalizados Email y Celular en ClickUp"""
    print("🔧 CREACIÓN DE CAMPOS PERSONALIZADOS EN CLICKUP")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # IDs reales
    list_id = "901411770471"  # PROYECTO 1
    
    print(f"📋 Lista objetivo: PROYECTO 1 (ID: {list_id})")
    
    # PASO 1: Verificar campos existentes
    print(f"\n📋 PASO 1: Verificar campos existentes")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/v1/lists/{list_id}", timeout=10)
        
        if response.status_code == 200:
            list_info = response.json()
            print(f"✅ Información de la lista obtenida")
            print(f"📝 Nombre: {list_info.get('name', 'N/A')}")
            
            custom_fields = list_info.get("custom_fields", [])
            print(f"🔧 Campos personalizados existentes: {len(custom_fields)}")
            
            for field in custom_fields:
                print(f"   📝 Campo: {field.get('name', 'N/A')} - ID: {field.get('id', 'N/A')} - Tipo: {field.get('type', 'N/A')}")
                
                # Verificar si ya existen los campos que necesitamos
                field_name = field.get('name', '').lower()
                if 'email' in field_name:
                    print(f"      ✅ Campo Email ya existe")
                if 'celular' in field_name or 'phone' in field_name or 'teléfono' in field_name:
                    print(f"      ✅ Campo Celular ya existe")
        else:
            print(f"❌ Error obteniendo información de la lista: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # PASO 2: Crear campos personalizados si no existen
    print(f"\n🔧 PASO 2: Crear campos personalizados")
    print("-" * 40)
    
    # Campos a crear
    fields_to_create = [
        {
            "name": "Email",
            "type": "email",
            "description": "Dirección de correo electrónico del contacto"
        },
        {
            "name": "Celular",
            "type": "phone",
            "description": "Número de teléfono celular del contacto"
        }
    ]
    
    for field_config in fields_to_create:
        print(f"🔧 Creando campo: {field_config['name']}")
        
        # Nota: La API de ClickUp no permite crear campos personalizados directamente
        # Estos deben crearse manualmente en la interfaz de ClickUp
        print(f"   ⚠️ Campo '{field_config['name']}' debe crearse manualmente en ClickUp")
        print(f"   📝 Tipo: {field_config['type']}")
        print(f"   📄 Descripción: {field_config['description']}")
    
    # PASO 3: Instrucciones para crear campos manualmente
    print(f"\n📋 PASO 3: Instrucciones para crear campos manualmente")
    print("-" * 40)
    
    print(f"🔧 Para crear los campos personalizados en ClickUp:")
    print(f"   1. Ir a ClickUp y abrir la lista 'PROYECTO 1'")
    print(f"   2. Hacer clic en 'Configuración de la lista' (ícono de engranaje)")
    print(f"   3. Ir a la pestaña 'Campos personalizados'")
    print(f"   4. Hacer clic en 'Agregar campo'")
    print(f"   5. Crear campo 'Email' de tipo 'Email'")
    print(f"   6. Crear campo 'Celular' de tipo 'Teléfono'")
    print(f"   7. Guardar los cambios")
    
    # PASO 4: Probar creación de tarea después de crear campos
    print(f"\n🧪 PASO 4: Probar creación de tarea después de crear campos")
    print("-" * 40)
    
    print(f"⚠️ IMPORTANTE: Después de crear los campos personalizados en ClickUp:")
    print(f"   1. Ejecutar este script nuevamente para verificar que los campos se crearon")
    print(f"   2. Probar la creación de tareas con campos personalizados")
    print(f"   3. Verificar que los campos se muestran correctamente en ClickUp")
    
    # PASO 5: Verificar endpoints de la interfaz
    print(f"\n🌐 PASO 5: Verificar endpoints de la interfaz")
    print("-" * 40)
    
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
            elif response.status_code == 422:
                print(f"   ⚠️ Error 422 (parámetros faltantes)")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    """Función principal"""
    print("🔧 CREACIÓN DE CAMPOS PERSONALIZADOS EN CLICKUP")
    print("=" * 70)
    
    # Crear campos personalizados
    create_custom_fields_in_clickup()
    
    # Resumen
    print(f"\n📊 RESUMEN")
    print("=" * 70)
    
    print(f"🔧 Campos personalizados necesarios:")
    print(f"   📧 Email (tipo: email)")
    print(f"   📱 Celular (tipo: phone)")
    
    print(f"\n⚠️ IMPORTANTE:")
    print(f"   Los campos personalizados deben crearse MANUALMENTE en ClickUp")
    print(f"   La API de ClickUp no permite crear campos personalizados programáticamente")
    print(f"   Una vez creados, las tareas podrán usar estos campos correctamente")
    
    print(f"\n💡 Próximos pasos:")
    print(f"   1. Crear campos personalizados en ClickUp manualmente")
    print(f"   2. Ejecutar este script nuevamente para verificar")
    print(f"   3. Probar creación de tareas con campos personalizados")
    print(f"   4. Verificar que los campos se muestran en ClickUp")
    
    print(f"\n🕐 Proceso completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
