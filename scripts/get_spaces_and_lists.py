#!/usr/bin/env python3
"""
Script para obtener espacios y listas directamente
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def get_spaces_and_lists():
    """Obtener espacios y listas directamente"""
    
    print("🔍 OBTENIENDO ESPACIOS Y LISTAS")
    print("=" * 60)
    
    # URL de la API
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
                    try:
                        workspaces_data = json.loads(response_text)
                        workspaces = workspaces_data.get("workspaces", [])
                        print(f"✅ Workspaces obtenidos: {len(workspaces)}")
                        
                        for workspace in workspaces:
                            if isinstance(workspace, dict):
                                workspace_id = workspace.get("id")
                                workspace_name = workspace.get("name")
                                print(f"\n📁 Workspace: {workspace_name} (ID: {workspace_id})")
                                
                                # Obtener espacios de este workspace
                                print(f"🔍 Obteniendo espacios...")
                                try:
                                    async with session.get(f"{base_url}/api/v1/spaces?workspace_id={workspace_id}") as spaces_response:
                                        print(f"📡 Status espacios: {spaces_response.status}")
                                        spaces_text = await spaces_response.text()
                                        print(f"📄 Respuesta espacios: {spaces_text}")
                                        
                                        if spaces_response.status == 200:
                                            try:
                                                spaces_data = json.loads(spaces_text)
                                                spaces = spaces_data.get("spaces", [])
                                                print(f"✅ Espacios obtenidos: {len(spaces)}")
                                                
                                                for space in spaces:
                                                    if isinstance(space, dict):
                                                        space_id = space.get("id")
                                                        space_name = space.get("name")
                                                        print(f"\n   📂 Espacio: {space_name} (ID: {space_id})")
                                                        
                                                        # Obtener listas de este espacio
                                                        print(f"   🔍 Obteniendo listas...")
                                                        try:
                                                            async with session.get(f"{base_url}/api/v1/lists?space_id={space_id}") as lists_response:
                                                                print(f"   📡 Status listas: {lists_response.status}")
                                                                lists_text = await lists_response.text()
                                                                print(f"   📄 Respuesta listas: {lists_text}")
                                                                
                                                                if lists_response.status == 200:
                                                                    try:
                                                                        lists_data = json.loads(lists_text)
                                                                        lists = lists_data.get("lists", [])
                                                                        print(f"   ✅ Listas obtenidas: {len(lists)}")
                                                                        
                                                                        for list_info in lists:
                                                                            if isinstance(list_info, dict):
                                                                                list_id = list_info.get("id")
                                                                                list_name = list_info.get("name")
                                                                                print(f"      📋 Lista: {list_name} (ID: {list_id})")
                                                                                
                                                                                # Intentar obtener campos personalizados
                                                                                print(f"      🔍 Obteniendo campos personalizados...")
                                                                                try:
                                                                                    async with session.get(f"{base_url}/api/v1/lists/{list_id}/custom-fields") as cf_response:
                                                                                        print(f"      📡 Status campos personalizados: {cf_response.status}")
                                                                                        cf_text = await cf_response.text()
                                                                                        print(f"      📄 Respuesta campos personalizados: {cf_text}")
                                                                                        
                                                                                        if cf_response.status == 200:
                                                                                            try:
                                                                                                custom_fields = json.loads(cf_text)
                                                                                                if isinstance(custom_fields, list):
                                                                                                    print(f"      ✅ Campos personalizados encontrados: {len(custom_fields)}")
                                                                                                    
                                                                                                    for field in custom_fields:
                                                                                                        if isinstance(field, dict):
                                                                                                            field_id = field.get("id")
                                                                                                            field_name = field.get("name")
                                                                                                            field_type = field.get("type")
                                                                                                            print(f"         📧 {field_name} (ID: {field_id}, Tipo: {field_type})")
                                                                                                else:
                                                                                                    print(f"      ⚠️ Respuesta inesperada: {custom_fields}")
                                                                                            except json.JSONDecodeError:
                                                                                                print(f"      ❌ Error parseando JSON: {cf_text}")
                                                                                        else:
                                                                                            print(f"      ❌ Error obteniendo campos personalizados: {cf_response.status}")
                                                                                except Exception as e:
                                                                                    print(f"      ❌ Error: {e}")
                                                                            else:
                                                                                print(f"      ⚠️ Formato inesperado: {list_info}")
                                                                    except json.JSONDecodeError:
                                                                        print(f"   ❌ Error parseando JSON de listas: {lists_text}")
                                                                else:
                                                                    print(f"   ❌ Error obteniendo listas: {lists_response.status}")
                                                            except Exception as e:
                                                                print(f"   ❌ Error: {e}")
                                                    else:
                                                        print(f"   ⚠️ Formato inesperado: {space}")
                                            except json.JSONDecodeError:
                                                print(f"❌ Error parseando JSON de espacios: {spaces_text}")
                                        else:
                                            print(f"❌ Error obteniendo espacios: {spaces_response.status}")
                                    except Exception as e:
                                        print(f"❌ Error: {e}")
                            else:
                                print(f"⚠️ Formato inesperado: {workspace}")
                    except json.JSONDecodeError:
                        print(f"❌ Error parseando JSON de workspaces: {response_text}")
                else:
                    print(f"❌ Error obteniendo workspaces: {response.status}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_spaces_and_lists())
