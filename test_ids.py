#!/usr/bin/env python3
"""
Script para obtener IDs de ClickUp (workspace_id, space_id, list_id)
"""

import asyncio
import os

# Configurar token de ClickUp
os.environ['CLICKUP_API_TOKEN'] = 'pk_156221125_VE0TJ0IMP8ZQ5U5QBCYGUQC2K94I8B48'

from core.clickup_client import ClickUpClient

async def main():
    """Obtener y mostrar todos los IDs de ClickUp"""
    print("🚀 Iniciando búsqueda de IDs de ClickUp...")
    print("=" * 60)
    
    client = ClickUpClient()
    
    try:
        print("🔍 Obteniendo workspaces...")
        workspaces = await client.get_workspaces()
        
        if not workspaces:
            print("❌ No se encontraron workspaces")
            return
        
        for i, ws in enumerate(workspaces, 1):
            print(f"\n📁 Workspace {i}: {ws['name']}")
            print(f"   🆔 ID: {ws['id']}")
            print(f"   📧 Miembros: {ws.get('members', 'N/A')}")
            
            workspace_id = ws['id']
            
            try:
                print(f"   🔍 Obteniendo spaces del workspace...")
                spaces = await client.get_spaces(workspace_id)
                
                if not spaces:
                    print("   ⚠️  No se encontraron spaces")
                    continue
                
                for j, space in enumerate(spaces[:3], 1):  # Solo primeros 3 spaces
                    print(f"\n     📂 Space {j}: {space['name']}")
                    print(f"        🆔 ID: {space['id']}")
                    
                    space_id = space['id']
                    
                    try:
                        print(f"        🔍 Obteniendo listas...")
                        lists = await client.get_lists(space_id)
                        
                        if not lists:
                            print("        ⚠️  No se encontraron listas")
                            continue
                        
                        for k, lst in enumerate(lists[:5], 1):  # Solo primeras 5 listas
                            print(f"\n          📋 Lista {k}: {lst['name']}")
                            print(f"             🆔 ID: {lst['id']}")
                            print(f"             📊 Tareas: {lst.get('task_count', 'N/A')}")
                            
                            # Guardar el primer set de IDs válidos para la prueba
                            if i == 1 and j == 1 and k == 1:
                                print("\n" + "🎯" * 20)
                                print("🎯 IDs PARA TU ARCHIVO .ENV:")
                                print("🎯" * 20)
                                print(f"WORKSPACE_ID_EJEMPLO={workspace_id}")
                                print(f"LIST_ID_EJEMPLO={lst['id']}")
                                print("🎯" * 20)
                        
                    except Exception as e:
                        print(f"        ❌ Error obteniendo listas: {e}")
                
            except Exception as e:
                print(f"   ❌ Error obteniendo spaces: {e}")
    
    except Exception as e:
        print(f"❌ Error conectando con ClickUp: {e}")
        print("🔧 Verifica tu token de API")
        return
    
    print("\n" + "✅" * 20)
    print("✅ LISTO PARA PROBAR!")
    print("✅" * 20)
    print("📋 Copia los IDs de arriba y úsalos para crear una tarea de prueba")

if __name__ == "__main__":
    asyncio.run(main())

