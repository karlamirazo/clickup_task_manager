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
    """Get y mostrar todos los IDs de ClickUp"""
    print("ğŸš€ Iniciando busqueda de IDs de ClickUp...")
    print("=" * 60)
    
    client = ClickUpClient()
    
    try:
        print("ğŸ”� Obteniendo workspaces...")
        workspaces = await client.get_workspaces()
        
        if not workspaces:
            print("â�Œ No se encontraron workspaces")
            return
        
        for i, ws in enumerate(workspaces, 1):
            print(f"\nğŸ“� Workspace {i}: {ws['name']}")
            print(f"   ğŸ†” ID: {ws['id']}")
            print(f"   ğŸ“§ Miembros: {ws.get('members', 'N/A')}")
            
            workspace_id = ws['id']
            
            try:
                print(f"   ğŸ”� Obteniendo spaces del workspace...")
                spaces = await client.get_spaces(workspace_id)
                
                if not spaces:
                    print("   âš ï¸�  No se encontraron spaces")
                    continue
                
                for j, space in enumerate(spaces[:3], 1):  # Solo primeros 3 spaces
                    print(f"\n     ğŸ“‚ Space {j}: {space['name']}")
                    print(f"        ğŸ†” ID: {space['id']}")
                    
                    space_id = space['id']
                    
                    try:
                        print(f"        ğŸ”� Obteniendo listas...")
                        lists = await client.get_lists(space_id)
                        
                        if not lists:
                            print("        âš ï¸�  No se encontraron listas")
                            continue
                        
                        for k, lst in enumerate(lists[:5], 1):  # Solo primeras 5 listas
                            print(f"\n          ğŸ“‹ Lista {k}: {lst['name']}")
                            print(f"             ğŸ†” ID: {lst['id']}")
                            print(f"             ğŸ“Š Tareas: {lst.get('task_count', 'N/A')}")
                            
                            # Guardar el primer set de IDs validos para la prueba
                            if i == 1 and j == 1 and k == 1:
                                print("\n" + "ğŸ�¯" * 20)
                                print("ğŸ�¯ IDs PARA TU ARCHIVO .ENV:")
                                print("ğŸ�¯" * 20)
                                print(f"WORKSPACE_ID_EJEMPLO={workspace_id}")
                                print(f"LIST_ID_EJEMPLO={lst['id']}")
                                print("ğŸ�¯" * 20)
                        
                    except Exception as e:
                        print(f"        â�Œ Error getting listas: {e}")
                
            except Exception as e:
                print(f"   â�Œ Error getting spaces: {e}")
    
    except Exception as e:
        print(f"â�Œ Error conectando con ClickUp: {e}")
        print("ğŸ”§ Verifica tu token de API")
        return
    
    print("\n" + "âœ…" * 20)
    print("âœ… LISTO PARA PROBAR!")
    print("âœ…" * 20)
    print("ğŸ“‹ Copia los IDs de arriba y usalos para crear una tarea de prueba")

if __name__ == "__main__":
    asyncio.run(main())

