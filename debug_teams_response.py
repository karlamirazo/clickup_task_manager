#!/usr/bin/env python3
"""
Script para debuggear la respuesta de teams/workspaces
"""

import asyncio
import sys
import os
import json

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.clickup_client import ClickUpClient

async def debug_teams_response():
    """Debuggear la respuesta de teams/workspaces"""
    
    print("🔍 DEBUGGEANDO RESPUESTA DE TEAMS/WORKSPACES")
    print("=" * 60)
    
    try:
        client = ClickUpClient()
        
        # Hacer la petición directamente
        print("📡 Haciendo petición a /team...")
        response = await client._make_request("GET", "team")
        
        print(f"📊 Status: 200 (implícito)")
        print(f"📝 Tipo de respuesta: {type(response)}")
        print(f"🔍 Claves en respuesta: {list(response.keys()) if isinstance(response, dict) else 'No es dict'}")
        
        if isinstance(response, dict):
            print(f"\n📋 Contenido completo:")
            print(json.dumps(response, indent=2, ensure_ascii=False))
            
            # Verificar si hay teams
            if 'teams' in response:
                teams = response['teams']
                print(f"\n✅ Teams encontrados: {len(teams)}")
                for i, team in enumerate(teams[:3]):
                    print(f"   {i+1}. {team.get('name', 'N/A')} (ID: {team.get('id', 'N/A')})")
            else:
                print(f"\n❌ No se encontró la clave 'teams'")
                print(f"   Claves disponibles: {list(response.keys())}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    await debug_teams_response()

if __name__ == "__main__":
    asyncio.run(main())
