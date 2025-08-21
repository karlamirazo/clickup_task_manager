#!/usr/bin/env python3
"""
Script de debugging para probar la conexion con ClickUp
"""

import asyncio
import os
from core.clickup_client import ClickUpClient
from core.config import settings

async def test_clickup_connection():
    """Test conexion con ClickUp"""
    print("ğŸ”� Probando conexion con ClickUp...")
    
    # Verificar configuracion
    print(f"ğŸ“‹ Token configured: {'âœ…' if settings.CLICKUP_API_TOKEN else 'â�Œ'}")
    print(f"ğŸ“‹ Longitud del token: {len(settings.CLICKUP_API_TOKEN) if settings.CLICKUP_API_TOKEN else 0}")
    print(f"ğŸ“‹ URL base: {settings.CLICKUP_API_BASE_URL}")
    
    if not settings.CLICKUP_API_TOKEN:
        print("â�Œ No hay token configured")
        return
    
    # Create cliente
    client = ClickUpClient()
    print(f"ğŸ”§ Cliente creado con token: {client.api_token[:10]}...")
    
    try:
        # Test conexion
        print("ğŸ”„ Probando endpoint /team...")
        workspaces = await client.get_workspaces()
        print(f"âœ… Connection successful! Workspaces encontrados: {len(workspaces)}")
        
        if workspaces:
            print("ğŸ“‹ Primer workspace:")
            print(f"   ID: {workspaces[0].get('id')}")
            print(f"   Nombre: {workspaces[0].get('name')}")
            
    except Exception as e:
        print(f"â�Œ Error en la conexion: {e}")
        print(f"â�Œ Tipo de error: {type(e)}")
        import traceback
        print(f"â�Œ Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_clickup_connection())
