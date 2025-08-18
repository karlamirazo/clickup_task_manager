#!/usr/bin/env python3
"""
Script para obtener los IDs de los campos personalizados de ClickUp
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def get_custom_field_ids():
    """Obtener los IDs de los campos personalizados de ClickUp"""
    
    print("🔍 OBTENIENDO IDs DE CAMPOS PERSONALIZADOS")
    print("=" * 60)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Obtener listas para ver sus campos personalizados
            print("📋 Obteniendo listas...")
            async with session.get(f"{base_url}/api/v1/lists?space_id=901411770471") as response:
                print(f"📡 Status: {response.status}")
                response_text = await response.text()
                print(f"📄 Respuesta: {response_text}")
                
                if response.status == 200:
                    try:
                        response_data = json.loads(response_text)
                        lists_data = response_data.get("lists", [])
                        print(f"✅ Listas obtenidas: {len(lists_data)}")
                        
                        for list_info in lists_data:
                            if isinstance(list_info, dict):
                                list_id = list_info.get("id")
                                list_name = list_info.get("name")
                                print(f"\n📋 Lista: {list_name} (ID: {list_id})")
                                
                                # Intentar obtener campos personalizados de esta lista
                                print(f"🔍 Obteniendo campos personalizados...")
                                try:
                                    async with session.get(f"{base_url}/api/v1/lists/{list_id}/custom-fields") as cf_response:
                                        print(f"📡 Status campos personalizados: {cf_response.status}")
                                        cf_text = await cf_response.text()
                                        print(f"📄 Respuesta campos personalizados: {cf_text}")
                                        
                                        if cf_response.status == 200:
                                            try:
                                                custom_fields = json.loads(cf_text)
                                                if isinstance(custom_fields, list):
                                                    print(f"✅ Campos personalizados encontrados: {len(custom_fields)}")
                                                    
                                                    for field in custom_fields:
                                                        if isinstance(field, dict):
                                                            field_id = field.get("id")
                                                            field_name = field.get("name")
                                                            field_type = field.get("type")
                                                            print(f"   📧 {field_name} (ID: {field_id}, Tipo: {field_type})")
                                                else:
                                                    print(f"⚠️ Respuesta inesperada: {custom_fields}")
                                            except json.JSONDecodeError:
                                                print(f"❌ Error parseando JSON: {cf_text}")
                                        else:
                                            print(f"❌ Error obteniendo campos personalizados: {cf_response.status}")
                                except Exception as e:
                                    print(f"❌ Error: {e}")
                            else:
                                print(f"⚠️ Formato inesperado: {list_info}")
                    except json.JSONDecodeError:
                        print(f"❌ Error parseando JSON de listas: {response_text}")
                else:
                    print(f"❌ Error obteniendo listas: {response.status}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_custom_field_ids())
