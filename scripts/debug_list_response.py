#!/usr/bin/env python3
"""
Script para debuggear la respuesta completa del endpoint de lista
"""

import asyncio
import os
import sys
import json
from datetime import datetime

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.clickup_client import ClickUpClient

async def debug_list_response():
    """Debuggear la respuesta completa del endpoint de lista"""
    
    print("🔍 DEBUGGEANDO RESPUESTA DE LISTA")
    print("=" * 50)
    
    list_id = "901411770471"  # PROYECTO 1
    
    try:
        # Inicializar cliente ClickUp
        client = ClickUpClient()
        
        print(f"📋 Obteniendo lista: {list_id}")
        
        # Obtener la lista
        list_details = await client._make_request("GET", f"list/{list_id}")
        
        print(f"✅ Lista obtenida exitosamente")
        print(f"📄 Respuesta completa:")
        print(json.dumps(list_details, indent=2, ensure_ascii=False))
        
        # Buscar campos relacionados con estados
        print(f"\n🔍 BUSCANDO CAMPOS RELACIONADOS CON ESTADOS:")
        
        # Buscar en toda la respuesta
        def search_for_status_fields(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if 'status' in key.lower():
                        print(f"   📊 Encontrado en {current_path}: {value}")
                    elif isinstance(value, (dict, list)):
                        search_for_status_fields(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]"
                    search_for_status_fields(item, current_path)
        
        search_for_status_fields(list_details)
        
        # Verificar si hay algún campo que contenga estados
        print(f"\n🔍 VERIFICANDO CAMPOS ESPECÍFICOS:")
        for key in list_details.keys():
            print(f"   📋 {key}: {type(list_details[key])}")
            if key == 'status':
                print(f"      📊 Contenido: {list_details[key]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_list_response())
