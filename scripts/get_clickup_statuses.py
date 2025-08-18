#!/usr/bin/env python3
"""
Script para obtener los estados válidos que ClickUp reconoce
"""

import asyncio
import os
import sys
from datetime import datetime

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.clickup_client import ClickUpClient

async def get_clickup_statuses():
    """Obtener los estados válidos que ClickUp reconoce"""
    
    print("🔍 OBTENIENDO ESTADOS VÁLIDOS DE CLICKUP")
    print("=" * 50)
    
    list_id = "901411770471"  # PROYECTO 1
    
    try:
        # Inicializar cliente ClickUp
        client = ClickUpClient()
        
        print(f"📋 Obteniendo estados para lista: {list_id}")
        
        # Obtener la lista para ver sus estados
        try:
            list_details = await client._make_request("GET", f"list/{list_id}")
            print(f"✅ Lista obtenida exitosamente")
            
            # Extraer estados de la lista
            if 'status' in list_details:
                print(f"\n📊 ESTADOS DISPONIBLES EN LA LISTA:")
                for status in list_details['status']:
                    status_id = status.get('id')
                    status_name = status.get('status')
                    status_color = status.get('color')
                    status_type = status.get('type')
                    
                    print(f"   🎯 {status_name} (ID: {status_id}, Color: {status_color}, Tipo: {status_type})")
                
                # Mostrar recomendaciones
                print(f"\n🎯 RECOMENDACIONES:")
                print(f"   ✅ Usar estos nombres exactos para el campo 'status':")
                for status in list_details['status']:
                    print(f"      - '{status.get('status')}'")
                
                return list_details['status']
            
            else:
                print(f"❌ No se encontraron estados en la lista")
                return []
        
        except Exception as e:
            print(f"❌ Error obteniendo lista: {e}")
            return []
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

if __name__ == "__main__":
    asyncio.run(get_clickup_statuses())
