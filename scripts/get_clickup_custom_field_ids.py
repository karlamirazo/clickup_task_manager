#!/usr/bin/env python3
"""
Script para obtener los IDs de los campos personalizados directamente de ClickUp
"""

import asyncio
import os
import sys
from datetime import datetime

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.clickup_client import ClickUpClient
from core.config import settings

async def get_clickup_custom_field_ids():
    """Obtener los IDs de los campos personalizados directamente de ClickUp"""
    
    print("🔍 OBTENIENDO IDs DE CAMPOS PERSONALIZADOS DESDE CLICKUP")
    print("=" * 70)
    
    try:
        # Inicializar cliente ClickUp
        client = ClickUpClient()
        
        # Obtener workspaces
        print("📁 Obteniendo workspaces...")
        workspaces = await client.get_workspaces()
        print(f"✅ Workspaces obtenidos: {len(workspaces)}")
        
        for workspace in workspaces:
            workspace_id = workspace.get("id")
            workspace_name = workspace.get("name")
            print(f"\n📁 Workspace: {workspace_name} (ID: {workspace_id})")
            
            # Obtener espacios del workspace
            print(f"🔍 Obteniendo espacios...")
            spaces = await client.get_spaces(workspace_id)
            print(f"✅ Espacios obtenidos: {len(spaces)}")
            
            for space in spaces:
                space_id = space.get("id")
                space_name = space.get("name")
                print(f"\n   📂 Espacio: {space_name} (ID: {space_id})")
                
                # Obtener listas del espacio
                print(f"   🔍 Obteniendo listas...")
                lists = await client.get_lists(space_id)
                print(f"   ✅ Listas obtenidas: {len(lists)}")
                
                for list_info in lists:
                    list_id = list_info.get("id")
                    list_name = list_info.get("name")
                    print(f"\n      📋 Lista: {list_name} (ID: {list_id})")
                    
                    # Obtener campos personalizados de la lista
                    print(f"      🔍 Obteniendo campos personalizados...")
                    try:
                        custom_fields = await client.get_list_custom_fields(list_id)
                        print(f"      ✅ Campos personalizados encontrados: {len(custom_fields)}")
                        
                        for field in custom_fields:
                            field_id = field.get("id")
                            field_name = field.get("name")
                            field_type = field.get("type")
                            print(f"         📧 {field_name} (ID: {field_id}, Tipo: {field_type})")
                            
                            # Guardar en un archivo para uso posterior
                            if field_name in ["Email", "Celular"]:
                                with open("custom_field_ids.txt", "a") as f:
                                    f.write(f"{list_name}|{field_name}|{field_id}|{field_type}\n")
                                print(f"         💾 Guardado para uso posterior")
                    
                    except Exception as e:
                        print(f"      ❌ Error obteniendo campos personalizados: {e}")
        
        # Mostrar resumen de campos encontrados
        print(f"\n📊 RESUMEN DE CAMPOS PERSONALIZADOS")
        print("=" * 50)
        try:
            with open("custom_field_ids.txt", "r") as f:
                lines = f.readlines()
                if lines:
                    print("✅ Campos personalizados encontrados:")
                    for line in lines:
                        list_name, field_name, field_id, field_type = line.strip().split("|")
                        print(f"   📋 {list_name} - {field_name}: {field_id} ({field_type})")
                else:
                    print("❌ No se encontraron campos personalizados")
        except FileNotFoundError:
            print("❌ No se encontró el archivo de campos personalizados")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_clickup_custom_field_ids())
