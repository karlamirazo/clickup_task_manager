#!/usr/bin/env python3
"""
Script para obtener los estados validos que ClickUp reconoce
"""

import asyncio
import os
import sys
from datetime import datetime

# Agregar el directorio raiz al path para importar modulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.clickup.client import ClickUpClient

async def get_clickup_statuses():
    """Get los estados validos que ClickUp reconoce"""
    
    print("ğŸ”� OBTENIENDO ESTADOS VALIDOS DE CLICKUP")
    print("=" * 50)
    
    list_id = "901411770471"  # PROYECTO 1
    
    try:
        # Inicializar cliente ClickUp
        client = ClickUpClient()
        
        print(f"ğŸ“‹ Obteniendo estados para lista: {list_id}")
        
        # Get la lista para ver sus estados
        try:
            list_details = await client._make_request("GET", f"list/{list_id}")
            print(f"âœ… Lista obtenida exitosamente")
            
            # Extraer estados de la lista
            if 'status' in list_details:
                print(f"\nğŸ“Š ESTADOS DISPONIBLES EN LA LISTA:")
                for status in list_details['status']:
                    status_id = status.get('id')
                    status_name = status.get('status')
                    status_color = status.get('color')
                    status_type = status.get('type')
                    
                    print(f"   ğŸ�¯ {status_name} (ID: {status_id}, Color: {status_color}, Tipo: {status_type})")
                
                # Mostrar recomendaciones
                print(f"\nğŸ�¯ RECOMENDACIONES:")
                print(f"   âœ… Usar estos nombres exactos para el campo 'status':")
                for status in list_details['status']:
                    print(f"      - '{status.get('status')}'")
                
                return list_details['status']
            
            else:
                print(f"â�Œ No se encontraron estados en la lista")
                return []
        
        except Exception as e:
            print(f"â�Œ Error getting lista: {e}")
            return []
    
    except Exception as e:
        print(f"â�Œ Error: {e}")
        return []

if __name__ == "__main__":
    asyncio.run(get_clickup_statuses())
