#!/usr/bin/env python3
"""
Script de prueba para verificar la conexion con la API de ClickUp
"""

import asyncio
import os
from core.clickup_client import ClickUpClient

async def test_clickup_connection():
    """Test la conexion con ClickUp API"""
    
    # Configurar el token directamente para la prueba
    api_token = "pk_156221125_F8RNYI1M5XOASGLBUF9SFJW16QVNV2P3"
    
    print("ğŸ”— Probando conexion con ClickUp API...")
    print(f"ğŸ“� Token: {api_token[:20]}...{api_token[-10:]}")
    
    try:
        # Create cliente con el token
        client = ClickUpClient(api_token=api_token)
        
        print("\nğŸ“‹ Obteniendo workspaces...")
        workspaces = await client.get_workspaces()
        
        if workspaces:
            print(f"âœ… Connection successful! Se encontraron {len(workspaces)} workspace(s):")
            for workspace in workspaces:
                print(f"   - {workspace.get('name', 'Sin nombre')} (ID: {workspace.get('id', 'N/A')})")
                
                # Get spaces del primer workspace
                if workspace.get('id'):
                    print(f"\nğŸ�¢ Obteniendo spaces del workspace '{workspace['name']}'...")
                    try:
                        spaces = await client.get_spaces(workspace['id'])
                        print(f"   ğŸ“� Se encontraron {len(spaces)} space(s):")
                        for space in spaces[:3]:  # Mostrar solo los primeros 3
                            print(f"      - {space.get('name', 'Sin nombre')} (ID: {space.get('id', 'N/A')})")
                        if len(spaces) > 3:
                            print(f"      ... y {len(spaces) - 3} mas")
                    except Exception as e:
                        print(f"   â�Œ Error getting spaces: {e}")
                    break  # Solo probar con el primer workspace
        else:
            print("âš ï¸�  No se encontraron workspaces")
            
    except Exception as e:
        print(f"â�Œ Error en la conexion: {e}")
        print(f"ğŸ”� Detalles del error: {type(e).__name__}")
        
        # Verificar si es un error de autenticacion
        if "401" in str(e) or "unauthorized" in str(e).lower():
            print("ğŸ”� Error de autenticacion - Verifica que el token sea valido")
        elif "403" in str(e) or "forbidden" in str(e).lower():
            print("ğŸš« Error de permisos - El token no tiene permisos suficientes")
        elif "rate limit" in str(e).lower():
            print("â�±ï¸�  Rate limit alcanzado - Espera un momento antes de reintentar")

if __name__ == "__main__":
    print("ğŸš€ Iniciando prueba de conexion con ClickUp API")
    print("=" * 50)
    
    # Execute la prueba
    asyncio.run(test_clickup_connection())
    
    print("\n" + "=" * 50)
    print("ğŸ�� Prueba completada")
