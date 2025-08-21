#!/usr/bin/env python3
"""
Script para crear campos personalizados Email y Celular en ClickUp
"""

import requests
import json
from datetime import datetime

def create_custom_fields_in_clickup():
    """Create campos personalizados Email y Celular en ClickUp"""
    print("ğŸ”§ CREACION DE CAMPOS PERSONALIZADOS EN CLICKUP")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # IDs reales
    list_id = "901411770471"  # PROYECTO 1
    
    print(f"ğŸ“‹ Lista objetivo: PROYECTO 1 (ID: {list_id})")
    
    # PASO 1: Verificar campos existentes
    print(f"\nğŸ“‹ PASO 1: Verificar campos existentes")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/v1/lists/{list_id}", timeout=10)
        
        if response.status_code == 200:
            list_info = response.json()
            print(f"âœ… Informacion de la lista obtenida")
            print(f"ğŸ“� Nombre: {list_info.get('name', 'N/A')}")
            
            custom_fields = list_info.get("custom_fields", [])
            print(f"ğŸ”§ Campos personalizados existentes: {len(custom_fields)}")
            
            for field in custom_fields:
                print(f"   ğŸ“� Campo: {field.get('name', 'N/A')} - ID: {field.get('id', 'N/A')} - Tipo: {field.get('type', 'N/A')}")
                
                # Verificar si ya existen los campos que necesitamos
                field_name = field.get('name', '').lower()
                if 'email' in field_name:
                    print(f"      âœ… Campo Email ya existe")
                if 'celular' in field_name or 'phone' in field_name or 'telefono' in field_name:
                    print(f"      âœ… Campo Celular ya existe")
        else:
            print(f"â�Œ Error getting informacion de la lista: {response.status_code}")
            
    except Exception as e:
        print(f"â�Œ Error: {e}")
    
    # PASO 2: Create campos personalizados si no existen
    print(f"\nğŸ”§ PASO 2: Create campos personalizados")
    print("-" * 40)
    
    # Campos a crear
    fields_to_create = [
        {
            "name": "Email",
            "type": "email",
            "description": "Direccion de correo electronico del contacto"
        },
        {
            "name": "Celular",
            "type": "phone",
            "description": "Numero de telefono celular del contacto"
        }
    ]
    
    for field_config in fields_to_create:
        print(f"ğŸ”§ Creando campo: {field_config['name']}")
        
        # Nota: La API de ClickUp no permite crear campos personalizados directamente
        # Estos deben crearse manualmente en la interfaz de ClickUp
        print(f"   âš ï¸� Campo '{field_config['name']}' debe crearse manualmente en ClickUp")
        print(f"   ğŸ“� Tipo: {field_config['type']}")
        print(f"   ğŸ“„ Descripcion: {field_config['description']}")
    
    # PASO 3: Instrucciones para crear campos manualmente
    print(f"\nğŸ“‹ PASO 3: Instrucciones para crear campos manualmente")
    print("-" * 40)
    
    print(f"ğŸ”§ Para crear los campos personalizados en ClickUp:")
    print(f"   1. Ir a ClickUp y abrir la lista 'PROYECTO 1'")
    print(f"   2. Hacer clic en 'Configuracion de la lista' (icono de engranaje)")
    print(f"   3. Ir a la pestana 'Campos personalizados'")
    print(f"   4. Hacer clic en 'Agregar campo'")
    print(f"   5. Create campo 'Email' de tipo 'Email'")
    print(f"   6. Create campo 'Celular' de tipo 'Telefono'")
    print(f"   7. Guardar los cambios")
    
    # PASO 4: Test creacion de tarea despues de crear campos
    print(f"\nğŸ§ª PASO 4: Test creacion de tarea despues de crear campos")
    print("-" * 40)
    
    print(f"âš ï¸� IMPORTANTE: Despues de crear los campos personalizados en ClickUp:")
    print(f"   1. Execute este script nuevamente para verificar que los campos se crearon")
    print(f"   2. Test la creacion de tareas con campos personalizados")
    print(f"   3. Verificar que los campos se muestran correctamente en ClickUp")
    
    # PASO 5: Verificar endpoints de la interfaz
    print(f"\nğŸŒ� PASO 5: Verificar endpoints de la interfaz")
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
            print(f"ğŸ”� Probando: {endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"   ğŸ“Š Status: {response.status_code}")
            
            if response.status_code == 500:
                print(f"   â�Œ ERROR 500 detectado!")
                print(f"   ğŸ“„ Respuesta: {response.text[:200]}")
            elif response.status_code == 422:
                print(f"   âš ï¸� Error 422 (parametros faltantes)")
                
        except Exception as e:
            print(f"   â�Œ Error: {e}")

def main():
    """Funcion principal"""
    print("ğŸ”§ CREACION DE CAMPOS PERSONALIZADOS EN CLICKUP")
    print("=" * 70)
    
    # Create campos personalizados
    create_custom_fields_in_clickup()
    
    # Resumen
    print(f"\nğŸ“Š RESUMEN")
    print("=" * 70)
    
    print(f"ğŸ”§ Campos personalizados necesarios:")
    print(f"   ğŸ“§ Email (tipo: email)")
    print(f"   ğŸ“± Celular (tipo: phone)")
    
    print(f"\nâš ï¸� IMPORTANTE:")
    print(f"   Los campos personalizados deben crearse MANUALMENTE en ClickUp")
    print(f"   La API de ClickUp no permite crear campos personalizados programaticamente")
    print(f"   Una vez creados, las tareas podran usar estos campos correctamente")
    
    print(f"\nğŸ’¡ Proximos pasos:")
    print(f"   1. Create campos personalizados en ClickUp manualmente")
    print(f"   2. Execute este script nuevamente para verificar")
    print(f"   3. Test creacion de tareas con campos personalizados")
    print(f"   4. Verificar que los campos se muestran en ClickUp")
    
    print(f"\nğŸ•� Proceso completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
