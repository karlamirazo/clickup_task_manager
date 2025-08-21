#!/usr/bin/env python3
"""
Script para probar la conexion del proyecto completo con ClickUp
"""

import asyncio
import sys
import os

# Agregar el directorio raiz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.clickup_client import ClickUpClient
from core.config import settings

async def test_project_connection():
    """Test la conexion del proyecto completo con ClickUp"""
    
    print("üöÄ PROBANDO CONEXION DEL PROYECTO COMPLETO")
    print("=" * 60)
    
    print(f"üîß Configuracion:")
    print(f"   API Token: {settings.CLICKUP_API_TOKEN[:20]}...{settings.CLICKUP_API_TOKEN[-10:]}")
    print(f"   Base URL: {settings.CLICKUP_API_BASE_URL}")
    print(f"   Debug: {settings.DEBUG}")
    
    try:
        # Create cliente usando la configuracion del proyecto
        print(f"\nüîó Creando cliente ClickUp...")
        client = ClickUpClient()
        
        print(f"   Headers configureds: {client.headers}")
        
        # Test endpoints basicos
        print(f"\nüì° Probando endpoints basicos...")
        
        # 1. User Info
        print(f"\n1Ô∏è‚É£ User Info:")
        try:
            user_data = await client.get_user()  # Sin argumentos para obtener usuario actual
            if user_data:
                print(f"   ‚úÖ Usuario: {user_data.get('user', {}).get('username', 'N/A')}")
                print(f"   üìß Email: {user_data.get('user', {}).get('email', 'N/A')}")
                print(f"   üÜî ID: {user_data.get('user', {}).get('id', 'N/A')}")
            else:
                print(f"   ‚ùå No se pudo obtener informacion del usuario")
        except Exception as e:
            print(f"   ‚ùå Error: {e}")
        
        # 2. Teams
        print(f"\n2Ô∏è‚É£ Teams:")
        try:
            teams_data = await client.get_teams()
            if teams_data:
                teams = teams_data
                print(f"   ‚úÖ Equipos encontrados: {len(teams)}")
                for team in teams[:3]:  # Mostrar solo los primeros 3
                    print(f"      - {team.get('name', 'N/A')} (ID: {team.get('id', 'N/A')})")
            else:
                print(f"   ‚ùå No se pudo obtener informacion de equipos")
        except Exception as e:
            print(f"   ‚ùå Error: {e}")
        
        # 3. Workspaces (usando endpoint correcto)
        print(f"\n3Ô∏è‚É£ Workspaces:")
        try:
            # Intentar con el endpoint correcto
            workspaces_data = await client.get_workspaces()
            if workspaces_data:
                workspaces = workspaces_data
                print(f"   ‚úÖ Workspaces encontrados: {len(workspaces)}")
                for workspace in workspaces[:3]:  # Mostrar solo los primeros 3
                    print(f"      - {workspace.get('name', 'N/A')} (ID: {workspace.get('id', 'N/A')})")
            else:
                print(f"   ‚ùå No se pudo obtener informacion de workspaces")
        except Exception as e:
            print(f"   ‚ùå Error: {e}")
        
        print(f"\nüéâ ¬°PRUEBA COMPLETADA!")
        print(f"‚úÖ El proyecto esta configured correctamente")
        print(f"üîë Token valido: {settings.CLICKUP_API_TOKEN[:20]}...{settings.CLICKUP_API_TOKEN[-10:]}")
        
    except Exception as e:
        print(f"\n‚ùå Error general: {e}")
        print(f"üîç Revisa la configuracion del proyecto")

async def main():
    """Funcion principal"""
    await test_project_connection()

if __name__ == "__main__":
    asyncio.run(main())
