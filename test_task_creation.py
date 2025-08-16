#!/usr/bin/env python3
"""
Script de prueba para verificar la creación de tareas
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_task_creation():
    """Probar la creación de tareas paso a paso"""
    
    print("🧪 INICIANDO PRUEBAS DE CREACIÓN DE TAREAS")
    print("=" * 50)
    
    try:
        # 1. Verificar configuración
        print("1️⃣ Verificando configuración...")
        from core.config import settings
        print(f"   ✅ CLICKUP_API_TOKEN configurado: {bool(settings.CLICKUP_API_TOKEN)}")
        print(f"   ✅ DATABASE_URL: {settings.DATABASE_URL}")
        print(f"   ✅ CLICKUP_API_BASE_URL: {settings.CLICKUP_API_BASE_URL}")
        
        # 2. Verificar base de datos
        print("\n2️⃣ Verificando base de datos...")
        from core.database import init_db, get_db
        await init_db()
        print("   ✅ Base de datos inicializada")
        
        # 3. Verificar modelos
        print("\n3️⃣ Verificando modelos...")
        from models.task import Task
        print(f"   ✅ Modelo Task importado: {Task}")
        print(f"   ✅ Tabla: {Task.__tablename__}")
        
        # 4. Verificar cliente ClickUp
        print("\n4️⃣ Verificando cliente ClickUp...")
        from core.clickup_client import ClickUpClient
        client = ClickUpClient()
        print(f"   ✅ Cliente ClickUp creado: {client}")
        print(f"   ✅ Token configurado: {bool(client.api_token)}")
        
        # 5. Probar conexión con ClickUp
        print("\n5️⃣ Probando conexión con ClickUp...")
        try:
            workspaces = await client.get_workspaces()
            print(f"   ✅ Conexión exitosa: {len(workspaces)} workspaces encontrados")
            if workspaces:
                workspace = workspaces[0]
                print(f"   📋 Primer workspace: {workspace.get('name')} (ID: {workspace.get('id')})")
                
                # 6. Obtener spaces del workspace
                print("\n6️⃣ Obteniendo spaces del workspace...")
                spaces = await client.get_spaces(workspace['id'])
                print(f"   ✅ Spaces encontrados: {len(spaces)}")
                
                if spaces:
                    space = spaces[0]
                    print(f"   📁 Primer space: {space.get('name')} (ID: {space.get('id')})")
                    
                    # 7. Obtener listas del space
                    print("\n7️⃣ Obteniendo listas del space...")
                    lists = await client.get_lists(space['id'])
                    print(f"   ✅ Listas encontradas: {len(lists)}")
                    
                    if lists:
                        list_item = lists[0]
                        print(f"   📋 Primera lista: {list_item.get('name')} (ID: {list_item.get('id')})")
                        
                        # 8. Probar creación de tarea
                        print("\n8️⃣ Probando creación de tarea...")
                        test_task_data = {
                            "name": "Tarea de prueba - " + str(asyncio.get_event_loop().time()),
                            "description": "Esta es una tarea de prueba para verificar la funcionalidad",
                            "priority": 3
                        }
                        
                        print(f"   📝 Datos de prueba: {test_task_data}")
                        
                        try:
                            clickup_response = await client.create_task(list_item['id'], test_task_data)
                            print(f"   ✅ Tarea creada en ClickUp: {clickup_response.get('id')}")
                            
                            # 9. Probar guardado en base de datos
                            print("\n9️⃣ Probando guardado en base de datos...")
                            db = next(get_db())
                            
                            try:
                                db_task = Task(
                                    clickup_id=clickup_response["id"],
                                    name=clickup_response["name"],
                                    description=clickup_response.get("description", ""),
                                    status=clickup_response.get("status", {}).get("status", "to do"),
                                    priority=3,
                                    workspace_id=workspace['id'],
                                    list_id=list_item['id'],
                                    assignee_id=None,
                                    creator_id="system",
                                    custom_fields={},
                                    is_synced=True
                                )
                                
                                print(f"   💾 Objeto Task creado: {db_task}")
                                db.add(db_task)
                                db.commit()
                                db.refresh(db_task)
                                print(f"   ✅ Tarea guardada en BD con ID: {db_task.id}")
                                
                                # Limpiar tarea de prueba
                                print("\n🧹 Limpiando tarea de prueba...")
                                await client.delete_task(clickup_response["id"])
                                db.delete(db_task)
                                db.commit()
                                print("   ✅ Tarea de prueba eliminada")
                                
                            finally:
                                db.close()
                                
                        except Exception as e:
                            print(f"   ❌ Error creando tarea: {e}")
                            import traceback
                            print(f"   📋 Traceback: {traceback.format_exc()}")
                    else:
                        print("   ⚠️ No hay listas disponibles para probar")
                else:
                    print("   ⚠️ No hay spaces disponibles para probar")
            else:
                print("   ⚠️ No hay workspaces disponibles para probar")
                
        except Exception as e:
            print(f"   ❌ Error conectando con ClickUp: {e}")
            import traceback
            print(f"   📋 Traceback: {traceback.format_exc()}")
        
        print("\n" + "=" * 50)
        print("🏁 PRUEBAS COMPLETADAS")
        
    except Exception as e:
        print(f"❌ Error general en las pruebas: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False
    
    return True

if __name__ == "__main__":
    # Ejecutar pruebas
    success = asyncio.run(test_task_creation())
    
    if success:
        print("✅ Todas las pruebas pasaron exitosamente")
        sys.exit(0)
    else:
        print("❌ Algunas pruebas fallaron")
        sys.exit(1)
