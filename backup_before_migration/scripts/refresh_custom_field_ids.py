#!/usr/bin/env python3
"""
Script para refrescar los IDs de campos personalizados desde ClickUp
"""

import os
import sys
import asyncio

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.clickup_client import ClickUpClient
from core.config import settings

async def refresh_custom_field_ids():
    """Refrescar IDs de campos personalizados desde ClickUp"""
    print("🔄 REFRESCANDO IDs DE CAMPOS PERSONALIZADOS")
    print("=" * 60)
    
    try:
        # Crear cliente ClickUp
        client = ClickUpClient()
        print("✅ Cliente ClickUp creado exitosamente")
        
        # Lista específica que estamos verificando
        list_id = "901411770471"
        print(f"🔍 Verificando lista: {list_id}")
        
        # Obtener campos de la lista
        try:
            fields_response = await client._make_request("GET", f"list/{list_id}/field")
            print("✅ Campos obtenidos exitosamente")
            
            if "fields" in fields_response:
                fields = fields_response["fields"]
                print(f"📊 Total de campos encontrados: {len(fields)}")
                
                # Filtrar solo campos personalizados
                custom_fields = []
                for field in fields:
                    if field.get("type") in ["text", "email", "phone", "number", "dropdown"]:
                        custom_fields.append({
                            "name": field.get("name", "Sin nombre"),
                            "id": field.get("id", "Sin ID"),
                            "type": field.get("type", "Desconocido"),
                            "required": field.get("required", False)
                        })
                
                print(f"🎯 Campos personalizados encontrados: {len(custom_fields)}")
                print("\n📋 DETALLE DE CAMPOS PERSONALIZADOS:")
                print("-" * 50)
                
                for field in custom_fields:
                    print(f"   📝 {field['name']}")
                    print(f"      🆔 ID: {field['id']}")
                    print(f"      🔧 Tipo: {field['type']}")
                    print(f"      ⚠️ Requerido: {field['required']}")
                    print()
                
                # Generar configuración actualizada
                print("🔧 CONFIGURACIÓN ACTUALIZADA PARA CUSTOM_FIELD_IDS:")
                print("-" * 50)
                print(f'"{list_id}": {{  # PROYECTO 1')
                
                for field in custom_fields:
                    field_name = field['name']
                    field_id = field['id']
                    print(f'    "{field_name}": "{field_id}",')
                
                print("},")
                
            else:
                print("❌ No se encontraron campos en la respuesta")
                print(f"📋 Respuesta completa: {fields_response}")
                
        except Exception as e:
            print(f"❌ Error obteniendo campos: {e}")
            print(f"🔍 Tipo de error: {type(e).__name__}")
            
            # Intentar obtener información de la lista
            try:
                list_info = await client._make_request("GET", f"list/{list_id}")
                print(f"📋 Información de la lista: {list_info.get('name', 'Sin nombre')}")
            except Exception as list_error:
                print(f"❌ Error obteniendo información de la lista: {list_error}")
    
    except Exception as e:
        print(f"❌ Error general: {e}")
        print(f"🔍 Tipo de error: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(refresh_custom_field_ids())
