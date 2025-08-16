#!/usr/bin/env python3
"""
Script de debugging para probar la conexión con ClickUp
"""

import asyncio
import os
from core.clickup_client import ClickUpClient
from core.config import settings

async def test_clickup_connection():
    """Probar conexión con ClickUp"""
    print("🔍 Probando conexión con ClickUp...")
    
    # Verificar configuración
    print(f"📋 Token configurado: {'✅' if settings.CLICKUP_API_TOKEN else '❌'}")
    print(f"📋 Longitud del token: {len(settings.CLICKUP_API_TOKEN) if settings.CLICKUP_API_TOKEN else 0}")
    print(f"📋 URL base: {settings.CLICKUP_API_BASE_URL}")
    
    if not settings.CLICKUP_API_TOKEN:
        print("❌ No hay token configurado")
        return
    
    # Crear cliente
    client = ClickUpClient()
    print(f"🔧 Cliente creado con token: {client.api_token[:10]}...")
    
    try:
        # Probar conexión
        print("🔄 Probando endpoint /team...")
        workspaces = await client.get_workspaces()
        print(f"✅ Conexión exitosa! Workspaces encontrados: {len(workspaces)}")
        
        if workspaces:
            print("📋 Primer workspace:")
            print(f"   ID: {workspaces[0].get('id')}")
            print(f"   Nombre: {workspaces[0].get('name')}")
            
    except Exception as e:
        print(f"❌ Error en la conexión: {e}")
        print(f"❌ Tipo de error: {type(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_clickup_connection())
