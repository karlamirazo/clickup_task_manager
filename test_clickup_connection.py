#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión con la API de ClickUp
"""

import asyncio
import os
from core.clickup_client import ClickUpClient

async def test_clickup_connection():
    """Probar la conexión con ClickUp API"""
    
    # Configurar el token directamente para la prueba
    api_token = "pk_156221125_F8RNYI1M5XOASGLBUF9SFJW16QVNV2P3"
    
    print("🔗 Probando conexión con ClickUp API...")
    print(f"📝 Token: {api_token[:20]}...{api_token[-10:]}")
    
    try:
        # Crear cliente con el token
        client = ClickUpClient(api_token=api_token)
        
        print("\n📋 Obteniendo workspaces...")
        workspaces = await client.get_workspaces()
        
        if workspaces:
            print(f"✅ Conexión exitosa! Se encontraron {len(workspaces)} workspace(s):")
            for workspace in workspaces:
                print(f"   - {workspace.get('name', 'Sin nombre')} (ID: {workspace.get('id', 'N/A')})")
                
                # Obtener spaces del primer workspace
                if workspace.get('id'):
                    print(f"\n🏢 Obteniendo spaces del workspace '{workspace['name']}'...")
                    try:
                        spaces = await client.get_spaces(workspace['id'])
                        print(f"   📁 Se encontraron {len(spaces)} space(s):")
                        for space in spaces[:3]:  # Mostrar solo los primeros 3
                            print(f"      - {space.get('name', 'Sin nombre')} (ID: {space.get('id', 'N/A')})")
                        if len(spaces) > 3:
                            print(f"      ... y {len(spaces) - 3} más")
                    except Exception as e:
                        print(f"   ❌ Error obteniendo spaces: {e}")
                    break  # Solo probar con el primer workspace
        else:
            print("⚠️  No se encontraron workspaces")
            
    except Exception as e:
        print(f"❌ Error en la conexión: {e}")
        print(f"🔍 Detalles del error: {type(e).__name__}")
        
        # Verificar si es un error de autenticación
        if "401" in str(e) or "unauthorized" in str(e).lower():
            print("🔐 Error de autenticación - Verifica que el token sea válido")
        elif "403" in str(e) or "forbidden" in str(e).lower():
            print("🚫 Error de permisos - El token no tiene permisos suficientes")
        elif "rate limit" in str(e).lower():
            print("⏱️  Rate limit alcanzado - Espera un momento antes de reintentar")

if __name__ == "__main__":
    print("🚀 Iniciando prueba de conexión con ClickUp API")
    print("=" * 50)
    
    # Ejecutar la prueba
    asyncio.run(test_clickup_connection())
    
    print("\n" + "=" * 50)
    print("🏁 Prueba completada")
