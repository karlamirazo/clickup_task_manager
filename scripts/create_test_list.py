#!/usr/bin/env python3
"""
Script para crear una lista de prueba en ClickUp
"""

import requests
import json
from datetime import datetime

def create_test_list():
    """Crear una lista de prueba en ClickUp"""
    print("📋 Creando lista de prueba en ClickUp")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Datos para crear la lista
    list_data = {
        "name": f"Lista de Prueba - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "description": "Lista creada automáticamente para pruebas de la aplicación",
        "workspace_id": "9014943317",  # ID del workspace que obtuvimos
        "space_id": "9014943317"  # Usar el mismo ID como space_id
    }
    
    print(f"📋 Datos de la lista:")
    print(f"   📝 Nombre: {list_data['name']}")
    print(f"   📄 Descripción: {list_data['description']}")
    print(f"   📁 Workspace ID: {list_data['workspace_id']}")
    print(f"   🏠 Space ID: {list_data['space_id']}")
    
    try:
        print(f"\n🚀 Enviando petición para crear lista...")
        
        # Intentar crear la lista usando el endpoint de creación de listas
        response = requests.post(
            f"{base_url}/api/v1/lists/",
            json=list_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📡 Respuesta del servidor:")
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ ¡Lista creada exitosamente!")
            print(f"📋 Respuesta completa:")
            print(json.dumps(result, indent=2, default=str))
            
            return True, result
            
        else:
            print(f"❌ Error creando la lista")
            print(f"📄 Respuesta de error: {response.text}")
            
            try:
                error_data = response.json()
                print(f"📋 Detalles del error:")
                print(json.dumps(error_data, indent=2))
            except:
                print(f"📄 Texto de error: {response.text}")
            
            return False, response.text
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False, str(e)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False, str(e)

def verify_list_creation():
    """Verificar que la lista se creó correctamente"""
    print(f"\n🔍 Verificando creación de la lista...")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    try:
        # Verificar listas disponibles
        response = requests.get(
            f"{base_url}/api/v1/lists?space_id=9014943317",
            timeout=10
        )
        
        if response.status_code == 200:
            lists_data = response.json()
            lists = lists_data.get("lists", [])
            print(f"✅ Listas disponibles: {len(lists)}")
            
            if lists:
                print(f"📋 Listas encontradas:")
                for list_item in lists:
                    print(f"   📝 Nombre: {list_item.get('name', 'N/A')}")
                    print(f"   🆔 ID: {list_item.get('id', 'N/A')}")
                    print(f"   📄 Descripción: {list_item.get('description', 'N/A')}")
                    print(f"   📊 Tareas: {list_item.get('task_count', 'N/A')}")
                    print(f"   🔄 Sincronizado: {list_item.get('is_synced', 'N/A')}")
                    print()
                
                return lists
            else:
                print("❌ No se encontraron listas")
                return []
        else:
            print(f"❌ Error obteniendo listas: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error verificando listas: {e}")
        return []

def main():
    """Función principal"""
    print("📋 CREACIÓN DE LISTA DE PRUEBA EN CLICKUP")
    print("=" * 70)
    
    # Crear lista de prueba
    print("\n" + "=" * 70)
    print("PASO 1: CREAR LISTA DE PRUEBA")
    print("=" * 70)
    
    success, result = create_test_list()
    
    # Verificar creación
    print("\n" + "=" * 70)
    print("PASO 2: VERIFICAR CREACIÓN")
    print("=" * 70)
    
    lists = verify_list_creation()
    
    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN")
    print("=" * 70)
    
    if success and lists:
        print("🎉 ¡Lista creada exitosamente!")
        print("✅ La lista está disponible para crear tareas")
        print("✅ Puedes usar el ID de la lista para crear tareas")
        
        # Mostrar información para usar en pruebas
        if lists:
            first_list = lists[0]
            print(f"\n💡 INFORMACIÓN PARA PRUEBAS:")
            print(f"   📋 Lista ID: {first_list.get('id', 'N/A')}")
            print(f"   📝 Nombre: {first_list.get('name', 'N/A')}")
            print(f"   📁 Workspace ID: 9014943317")
            
            print(f"\n🔧 COMANDO PARA PROBAR CREACIÓN DE TAREAS:")
            print(f"python scripts/test_task_creation_with_custom_fields.py")
            
    elif success:
        print("⚠️ Lista creada pero no se pudo verificar")
        print("✅ Intenta verificar manualmente en ClickUp")
        
    else:
        print("❌ Error creando la lista")
        print("🔧 Revisar logs del servidor para más detalles")
        print("💡 Verificar que el token de ClickUp tiene permisos para crear listas")
    
    print(f"\n🕐 Proceso completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
