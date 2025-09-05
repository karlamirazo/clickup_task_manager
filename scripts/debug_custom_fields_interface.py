#!/usr/bin/env python3
"""
Script para debuggear campos personalizados en la interfaz
"""

import os
import sys
import asyncio

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.clickup.client import ClickUpClient
from core.config import settings

async def debug_custom_fields_interface():
    """Debuggear campos personalizados en la interfaz"""
    print("🔍 DEBUGGEANDO CAMPOS PERSONALIZADOS EN LA INTERFAZ")
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
                
                # Mostrar TODOS los campos (no solo personalizados)
                print("\n📋 TODOS LOS CAMPOS ENCONTRADOS:")
                print("-" * 50)
                
                for field in fields:
                    field_name = field.get("name", "Sin nombre")
                    field_id = field.get("id", "Sin ID")
                    field_type = field.get("type", "Desconocido")
                    field_required = field.get("required", False)
                    
                    print(f"   📝 {field_name}")
                    print(f"      🆔 ID: {field_id}")
                    print(f"      🔧 Tipo: {field_type}")
                    print(f"      ⚠️ Requerido: {field_required}")
                    print()
                
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
                
                print(f"🎯 CAMPOS PERSONALIZADOS: {len(custom_fields)}")
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
                
                # Verificar si hay campos que se están enviando pero no existen
                print("\n🚨 VERIFICACIÓN DE CAMPOS:")
                print("-" * 50)
                
                # Campos que se están enviando desde la interfaz
                interface_fields = ["Email", "Celular", "Nombre"]
                
                for interface_field in interface_fields:
                    found = False
                    for custom_field in custom_fields:
                        if custom_field["name"] == interface_field:
                            found = True
                            print(f"✅ {interface_field}: Encontrado (ID: {custom_field['id']})")
                            break
                    
                    if not found:
                        print(f"❌ {interface_field}: NO EXISTE en ClickUp")
                        print(f"   💡 SOLUCIÓN: Eliminar de la interfaz o crear en ClickUp")
                
            else:
                print("❌ No se encontraron campos en la respuesta")
                print(f"📋 Respuesta completa: {fields_response}")
                
        except Exception as e:
            print(f"❌ Error obteniendo campos: {e}")
            print(f"🔍 Tipo de error: {type(e).__name__}")
    
    except Exception as e:
        print(f"❌ Error general: {e}")
        print(f"🔍 Tipo de error: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(debug_custom_fields_interface())
