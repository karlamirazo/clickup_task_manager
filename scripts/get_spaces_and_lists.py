#!/usr/bin/env python3
"""
Script para obtener espacios y listas directamente
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def get_spaces_and_lists():
    """Get espacios y listas directamente"""
    
    print("üîç OBTENIENDO ESPACIOS Y LISTAS")
    print("=" * 60)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get workspaces
            print("üìÅ Obteniendo workspaces...")
            async with session.get(f"{base_url}/api/v1/workspaces") as response:
                print(f"üì° Status: {response.status}")
                response_text = await response.text()
                print(f"üìÑ Respuesta: {response_text}")
                
                if response.status == 200:
                    try:
                        workspaces_data = json.loads(response_text)
                        workspaces = workspaces_data.get("workspaces", [])
                        print(f"‚úÖ Workspaces obtenidos: {len(workspaces)}")
                        
                        for workspace in workspaces:
                            if isinstance(workspace, dict):
                                workspace_id = workspace.get("id")
                                workspace_name = workspace.get("name")
                                print(f"\nüìÅ Workspace: {workspace_name} (ID: {workspace_id})")
                                
                                # Get espacios de este workspace
                                print(f"üîç Obteniendo espacios...")
                                try:
                                    async with session.get(f"{base_url}/api/v1/spaces?workspace_id={workspace_id}") as spaces_response:
                                        print(f"üì° Status espacios: {spaces_response.status}")
                                        spaces_text = await spaces_response.text()
                                        print(f"üìÑ Respuesta espacios: {spaces_text}")
                                        
                                        if spaces_response.status == 200:
                                            try:
                                                spaces_data = json.loads(spaces_text)
                                                spaces = spaces_data.get("spaces", [])
                                                print(f"‚úÖ Espacios obtenidos: {len(spaces)}")
                                                
                                                for space in spaces:
                                                    if isinstance(space, dict):
                                                        space_id = space.get("id")
                                                        space_name = space.get("name")
                                                        print(f"\n   üìÇ Espacio: {space_name} (ID: {space_id})")
                                                        
                                                        # Get listas de este espacio
                                                        print(f"   üîç Obteniendo listas...")
                                                        try:
                                                            async with session.get(f"{base_url}/api/v1/lists?space_id={space_id}") as lists_response:
                                                                print(f"   üì° Status listas: {lists_response.status}")
                                                                lists_text = await lists_response.text()
                                                                print(f"   üìÑ Respuesta listas: {lists_text}")
                                                                
                                                                if lists_response.status == 200:
                                                                    try:
                                                                        lists_data = json.loads(lists_text)
                                                                        lists = lists_data.get("lists", [])
                                                                        print(f"   ‚úÖ Listas obtenidas: {len(lists)}")
                                                                        
                                                                        for list_info in lists:
                                                                            if isinstance(list_info, dict):
                                                                                list_id = list_info.get("id")
                                                                                list_name = list_info.get("name")
                                                                                print(f"      üìã Lista: {list_name} (ID: {list_id})")
                                                                                
                                                                                # Intentar obtener campos personalizados
                                                                                print(f"      üîç Obteniendo campos personalizados...")
                                                                                try:
                                                                                    async with session.get(f"{base_url}/api/v1/lists/{list_id}/custom-fields") as cf_response:
                                                                                        print(f"      üì° Status campos personalizados: {cf_response.status}")
                                                                                        cf_text = await cf_response.text()
                                                                                        print(f"      üìÑ Respuesta campos personalizados: {cf_text}")
                                                                                        
                                                                                        if cf_response.status == 200:
                                                                                            try:
                                                                                                custom_fields = json.loads(cf_text)
                                                                                                if isinstance(custom_fields, list):
                                                                                                    print(f"      ‚úÖ Campos personalizados encontrados: {len(custom_fields)}")
                                                                                                    
                                                                                                    for field in custom_fields:
                                                                                                        if isinstance(field, dict):
                                                                                                            field_id = field.get("id")
                                                                                                            field_name = field.get("name")
                                                                                                            field_type = field.get("type")
                                                                                                            print(f"         üìß {field_name} (ID: {field_id}, Tipo: {field_type})")
                                                                                                else:
                                                                                                    print(f"      ‚ö†Ô∏è Respuesta inesperada: {custom_fields}")
                                                                                            except json.JSONDecodeError:
                                                                                                print(f"      ‚ùå Error parseando JSON: {cf_text}")
                                                                                        else:
                                                                                            print(f"      ‚ùå Error getting campos personalizados: {cf_response.status}")
                                                                                except Exception as e:
                                                                                    print(f"      ‚ùå Error: {e}")
                                                                            else:
                                                                                print(f"      ‚ö†Ô∏è Formato inesperado: {list_info}")
                                                                    except json.JSONDecodeError:
                                                                        print(f"   ‚ùå Error parseando JSON de listas: {lists_text}")
                                                                else:
                                                                    print(f"   ‚ùå Error getting listas: {lists_response.status}")
                                                            except Exception as e:
                                                                print(f"   ‚ùå Error: {e}")
                                                    else:
                                                        print(f"   ‚ö†Ô∏è Formato inesperado: {space}")
                                            except json.JSONDecodeError:
                                                print(f"‚ùå Error parseando JSON de espacios: {spaces_text}")
                                        else:
                                            print(f"‚ùå Error getting espacios: {spaces_response.status}")
                                    except Exception as e:
                                        print(f"‚ùå Error: {e}")
                            else:
                                print(f"‚ö†Ô∏è Formato inesperado: {workspace}")
                    except json.JSONDecodeError:
                        print(f"‚ùå Error parseando JSON de workspaces: {response_text}")
                else:
                    print(f"‚ùå Error getting workspaces: {response.status}")
    
    except Exception as e:
        print(f"‚ùå Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_spaces_and_lists())
