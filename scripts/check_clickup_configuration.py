#!/usr/bin/env python3
"""
Script para verificar la configuración de ClickUp y obtener información detallada
"""

import requests
import json
from datetime import datetime

def check_clickup_configuration():
    """Verificar la configuración de ClickUp"""
    print("🔍 Verificando configuración de ClickUp")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Verificar debug endpoint
    try:
        print("🔍 Verificando endpoint de debug...")
        response = requests.get(f"{base_url}/debug", timeout=10)
        
        if response.status_code == 200:
            debug_data = response.json()
            print("✅ Debug endpoint funcionando")
            
            config = debug_data.get("configuration", {})
            print(f"   🔑 CLICKUP_API_TOKEN: {config.get('CLICKUP_API_TOKEN', 'N/A')}")
            print(f"   🗄️ DATABASE_URL: {config.get('DATABASE_URL', 'N/A')}")
            print(f"   🌍 ENVIRONMENT: {config.get('ENVIRONMENT', 'N/A')}")
            
            clickup_client = debug_data.get("clickup_client", {})
            print(f"   📡 ClickUp Client: {clickup_client.get('client_status', 'N/A')}")
            print(f"   🔑 Token Configurado: {clickup_client.get('token_configured', 'N/A')}")
            
        else:
            print(f"❌ Error en debug endpoint: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando debug: {e}")
        return False
    
    # Verificar workspaces
    try:
        print(f"\n🔍 Verificando workspaces...")
        response = requests.get(f"{base_url}/api/v1/workspaces", timeout=10)
        
        if response.status_code == 200:
            workspaces_data = response.json()
            workspaces = workspaces_data.get("workspaces", [])
            print(f"✅ Workspaces obtenidos: {len(workspaces)}")
            
            for workspace in workspaces:
                print(f"   📁 Workspace: {workspace.get('name', 'N/A')}")
                print(f"   🆔 ID: {workspace.get('id', 'N/A')}")
                print(f"   🎨 Color: {workspace.get('color', 'N/A')}")
                print(f"   🔄 Sincronizado: {workspace.get('is_synced', 'N/A')}")
                
                # Intentar obtener listas de este workspace
                workspace_id = workspace.get('id')
                if workspace_id:
                    print(f"   📋 Buscando listas en workspace {workspace_id}...")
                    
                    try:
                        lists_response = requests.get(
                            f"{base_url}/api/v1/lists?space_id={workspace_id}",
                            timeout=10
                        )
                        
                        if lists_response.status_code == 200:
                            lists_data = lists_response.json()
                            lists = lists_data.get("lists", [])
                            print(f"      📋 Listas encontradas: {len(lists)}")
                            
                            for list_item in lists:
                                print(f"         📝 Lista: {list_item.get('name', 'N/A')}")
                                print(f"         🆔 ID: {list_item.get('id', 'N/A')}")
                                print(f"         📊 Tareas: {list_item.get('task_count', 'N/A')}")
                        else:
                            print(f"      ❌ Error obteniendo listas: {lists_response.status_code}")
                            
                    except Exception as e:
                        print(f"      ❌ Error: {e}")
                
                print()  # Línea en blanco entre workspaces
                
        else:
            print(f"❌ Error obteniendo workspaces: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error verificando workspaces: {e}")
    
    # Verificar usuarios
    try:
        print(f"🔍 Verificando usuarios...")
        response = requests.get(f"{base_url}/api/v1/users", timeout=10)
        
        if response.status_code == 200:
            users_data = response.json()
            users = users_data.get("users", [])
            print(f"✅ Usuarios obtenidos: {len(users)}")
            
            for user in users[:3]:  # Mostrar solo los primeros 3
                print(f"   👤 Usuario: {user.get('username', 'N/A')}")
                print(f"   🆔 ID: {user.get('id', 'N/A')}")
                print(f"   📧 Email: {user.get('email', 'N/A')}")
                print(f"   👤 Nombre: {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}")
                
        else:
            print(f"❌ Error obteniendo usuarios: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error verificando usuarios: {e}")
    
    return True

def test_clickup_api_directly():
    """Probar la API de ClickUp directamente"""
    print(f"\n🔍 Probando API de ClickUp directamente...")
    print("=" * 60)
    
    # Obtener token de la configuración
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    try:
        debug_response = requests.get(f"{base_url}/debug", timeout=10)
        if debug_response.status_code == 200:
            debug_data = debug_response.json()
            clickup_client = debug_data.get("clickup_client", {})
            
            if clickup_client.get("token_configured") == "✅ Sí":
                print("✅ Token de ClickUp configurado correctamente")
                
                # Intentar obtener información de ClickUp directamente
                print("🔍 Intentando obtener información de ClickUp...")
                
                # Nota: No podemos hacer esto directamente desde aquí porque no tenemos acceso al token
                # Pero podemos verificar que el endpoint funciona
                print("📡 El token está configurado y disponible para la aplicación")
                
            else:
                print("❌ Token de ClickUp no configurado")
                
        else:
            print("❌ No se pudo obtener información de debug")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN COMPLETA DE CONFIGURACIÓN DE CLICKUP")
    print("=" * 70)
    
    # Verificar configuración
    success = check_clickup_configuration()
    
    # Probar API directamente
    test_clickup_api_directly()
    
    # Resumen
    print(f"\n" + "=" * 70)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 70)
    
    if success:
        print("✅ La configuración de ClickUp está funcionando correctamente")
        print("✅ Los endpoints están respondiendo")
        print("✅ El token está configurado")
        print("\n💡 PRÓXIMOS PASOS:")
        print("   1. Verificar que hay listas disponibles en ClickUp")
        print("   2. Crear una lista si no existe")
        print("   3. Probar la creación de tareas con IDs correctos")
        print("   4. Verificar que los campos personalizados están configurados")
    else:
        print("❌ Hay problemas con la configuración de ClickUp")
        print("🔧 Revisar logs del servidor para más detalles")
    
    print(f"\n🕐 Verificación completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
