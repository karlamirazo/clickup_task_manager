#!/usr/bin/env python3
"""
Script de diagnóstico para verificar la conectividad con ClickUp
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_clickup_connection():
    """Prueba la conectividad con ClickUp"""
    print("🧪 Probando conectividad con ClickUp...")
    
    try:
        from core.clickup_client import ClickUpClient
        from core.config import settings
        
        # Mostrar configuración
        print(f"🔑 Token de ClickUp: {settings.CLICKUP_API_TOKEN[:20]}...")
        print(f"🏢 Workspace ID: {settings.CLICKUP_WORKSPACE_ID}")
        print(f"📁 Space ID: {settings.CLICKUP_SPACE_ID}")
        print(f"🌐 API Base URL: {settings.CLICKUP_API_BASE_URL}")
        
        # Crear cliente de ClickUp
        client = ClickUpClient()
        
        # Verificar token
        if not client.api_token:
            print("❌ ERROR: No hay token de ClickUp configurado")
            return
        
        print(f"✅ Token de ClickUp configurado correctamente")
        
        # Probar obtener usuario actual
        print("👤 Probando obtener usuario actual...")
        try:
            user = await client.get_user()
            print(f"✅ Usuario obtenido: {user.get('user', {}).get('username', 'N/A')}")
        except Exception as e:
            print(f"❌ Error obteniendo usuario: {e}")
        
        # Probar obtener workspaces
        print("🏢 Probando obtener workspaces...")
        try:
            workspaces = await client.get_workspaces()
            print(f"✅ Workspaces obtenidos: {len(workspaces)}")
            for ws in workspaces:
                print(f"   - {ws.get('name', 'N/A')} (ID: {ws.get('id', 'N/A')})")
        except Exception as e:
            print(f"❌ Error obteniendo workspaces: {e}")
        
        # Probar obtener spaces del workspace
        print(f"📁 Probando obtener spaces del workspace {settings.CLICKUP_WORKSPACE_ID}...")
        try:
            spaces = await client.get_spaces(settings.CLICKUP_WORKSPACE_ID)
            print(f"✅ Spaces obtenidos: {len(spaces)}")
            for space in spaces:
                print(f"   - {space.get('name', 'N/A')} (ID: {space.get('id', 'N/A')})")
        except Exception as e:
            print(f"❌ Error obteniendo spaces: {e}")
        
        # Probar obtener listas del space
        print(f"📋 Probando obtener listas del space {settings.CLICKUP_SPACE_ID}...")
        try:
            lists = await client.get_lists(settings.CLICKUP_SPACE_ID)
            print(f"✅ Listas obtenidas: {len(lists)}")
            for list_item in lists[:5]:  # Mostrar solo las primeras 5
                print(f"   - {list_item.get('name', 'N/A')} (ID: {list_item.get('id', 'N/A')})")
        except Exception as e:
            print(f"❌ Error obteniendo listas: {e}")
        
        # Probar crear una tarea de prueba
        print("📝 Probando crear tarea de prueba...")
        try:
            # Usar la primera lista disponible
            if lists:
                test_list_id = lists[0]['id']
                print(f"   📋 Usando lista: {lists[0]['name']} (ID: {test_list_id})")
                
                test_task_data = {
                    "name": "🧪 TAREA DE PRUEBA - DIAGNÓSTICO",
                    "description": "Esta es una tarea de prueba para verificar la conectividad con ClickUp",
                    "status": "pendiente",
                    "priority": 3
                }
                
                print(f"   📤 Enviando datos: {test_task_data}")
                response = await client.create_task(test_list_id, test_task_data)
                
                if response and "id" in response:
                    print(f"✅ Tarea creada exitosamente en ClickUp!")
                    print(f"   🆔 ID de ClickUp: {response['id']}")
                    print(f"   📝 Nombre: {response.get('name', 'N/A')}")
                    print(f"   📋 Lista: {response.get('list', {}).get('name', 'N/A')}")
                    
                    # Intentar eliminar la tarea de prueba
                    print("🗑️ Eliminando tarea de prueba...")
                    try:
                        await client.delete_task(response['id'])
                        print("✅ Tarea de prueba eliminada exitosamente")
                    except Exception as delete_error:
                        print(f"⚠️ No se pudo eliminar la tarea de prueba: {delete_error}")
                else:
                    print(f"❌ Error creando tarea: {response}")
            else:
                print("⚠️ No hay listas disponibles para probar")
                
        except Exception as e:
            print(f"❌ Error creando tarea de prueba: {e}")
            import traceback
            traceback.print_exc()
        
        print("✅ Diagnóstico de ClickUp completado!")
        
    except Exception as e:
        print(f"❌ Error en el diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_clickup_connection())
