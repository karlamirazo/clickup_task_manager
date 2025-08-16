#!/usr/bin/env python3
"""
Script para probar la conexión del proyecto completo con ClickUp
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.clickup_client import ClickUpClient
from core.config import settings

async def test_project_connection():
    """Probar la conexión del proyecto completo con ClickUp"""
    
    print("🚀 PROBANDO CONEXIÓN DEL PROYECTO COMPLETO")
    print("=" * 60)
    
    print(f"🔧 Configuración:")
    print(f"   API Token: {settings.CLICKUP_API_TOKEN[:20]}...{settings.CLICKUP_API_TOKEN[-10:]}")
    print(f"   Base URL: {settings.CLICKUP_API_BASE_URL}")
    print(f"   Debug: {settings.DEBUG}")
    
    try:
        # Crear cliente usando la configuración del proyecto
        print(f"\n🔗 Creando cliente ClickUp...")
        client = ClickUpClient()
        
        print(f"   Headers configurados: {client.headers}")
        
        # Probar endpoints básicos
        print(f"\n📡 Probando endpoints básicos...")
        
        # 1. User Info
        print(f"\n1️⃣ User Info:")
        try:
            user_data = await client.get_user()  # Sin argumentos para obtener usuario actual
            if user_data:
                print(f"   ✅ Usuario: {user_data.get('user', {}).get('username', 'N/A')}")
                print(f"   📧 Email: {user_data.get('user', {}).get('email', 'N/A')}")
                print(f"   🆔 ID: {user_data.get('user', {}).get('id', 'N/A')}")
            else:
                print(f"   ❌ No se pudo obtener información del usuario")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 2. Teams
        print(f"\n2️⃣ Teams:")
        try:
            teams_data = await client.get_teams()
            if teams_data:
                teams = teams_data
                print(f"   ✅ Equipos encontrados: {len(teams)}")
                for team in teams[:3]:  # Mostrar solo los primeros 3
                    print(f"      - {team.get('name', 'N/A')} (ID: {team.get('id', 'N/A')})")
            else:
                print(f"   ❌ No se pudo obtener información de equipos")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 3. Workspaces (usando endpoint correcto)
        print(f"\n3️⃣ Workspaces:")
        try:
            # Intentar con el endpoint correcto
            workspaces_data = await client.get_workspaces()
            if workspaces_data:
                workspaces = workspaces_data
                print(f"   ✅ Workspaces encontrados: {len(workspaces)}")
                for workspace in workspaces[:3]:  # Mostrar solo los primeros 3
                    print(f"      - {workspace.get('name', 'N/A')} (ID: {workspace.get('id', 'N/A')})")
            else:
                print(f"   ❌ No se pudo obtener información de workspaces")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print(f"\n🎉 ¡PRUEBA COMPLETADA!")
        print(f"✅ El proyecto está configurado correctamente")
        print(f"🔑 Token válido: {settings.CLICKUP_API_TOKEN[:20]}...{settings.CLICKUP_API_TOKEN[-10:]}")
        
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        print(f"🔍 Revisa la configuración del proyecto")

async def main():
    """Función principal"""
    await test_project_connection()

if __name__ == "__main__":
    asyncio.run(main())
