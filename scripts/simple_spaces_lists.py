#!/usr/bin/env python3
"""
Script simple para obtener espacios y listas
"""

import asyncio
import aiohttp
import json

async def get_spaces_and_lists():
    """Obtener espacios y listas de manera simple"""
    
    print("🔍 OBTENIENDO ESPACIOS Y LISTAS")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Obtener workspaces
            print("📁 Obteniendo workspaces...")
            async with session.get(f"{base_url}/api/v1/workspaces") as response:
                print(f"📡 Status: {response.status}")
                response_text = await response.text()
                print(f"📄 Respuesta: {response_text}")
                
                if response.status == 200:
                    workspaces_data = json.loads(response_text)
                    workspaces = workspaces_data.get("workspaces", [])
                    print(f"✅ Workspaces obtenidos: {len(workspaces)}")
                    
                    for workspace in workspaces:
                        workspace_id = workspace.get("id")
                        workspace_name = workspace.get("name")
                        print(f"\n📁 Workspace: {workspace_name} (ID: {workspace_id})")
                        
                        # Obtener espacios
                        print(f"🔍 Obteniendo espacios...")
                        async with session.get(f"{base_url}/api/v1/spaces?workspace_id={workspace_id}") as spaces_response:
                            print(f"📡 Status espacios: {spaces_response.status}")
                            spaces_text = await spaces_response.text()
                            print(f"📄 Respuesta espacios: {spaces_text}")
                            
                            if spaces_response.status == 200:
                                spaces_data = json.loads(spaces_text)
                                spaces = spaces_data.get("spaces", [])
                                print(f"✅ Espacios obtenidos: {len(spaces)}")
                                
                                for space in spaces:
                                    space_id = space.get("id")
                                    space_name = space.get("name")
                                    print(f"\n   📂 Espacio: {space_name} (ID: {space_id})")
                                    
                                    # Obtener listas
                                    print(f"   🔍 Obteniendo listas...")
                                    async with session.get(f"{base_url}/api/v1/lists?space_id={space_id}") as lists_response:
                                        print(f"   📡 Status listas: {lists_response.status}")
                                        lists_text = await lists_response.text()
                                        print(f"   📄 Respuesta listas: {lists_text}")
                                        
                                        if lists_response.status == 200:
                                            lists_data = json.loads(lists_text)
                                            lists = lists_data.get("lists", [])
                                            print(f"   ✅ Listas obtenidas: {len(lists)}")
                                            
                                            for list_info in lists:
                                                list_id = list_info.get("id")
                                                list_name = list_info.get("name")
                                                print(f"      📋 Lista: {list_name} (ID: {list_id})")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_spaces_and_lists())
