#!/usr/bin/env python3
"""
Script de prueba para verificar OAuth con credenciales reales
"""

import os
import sys
import asyncio
import aiohttp
from urllib.parse import urlencode

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🧪 PRUEBA OAUTH CON CREDENCIALES REALES")
    print("=" * 60)
    print()

def test_oauth_configuration():
    """Probar configuración OAuth"""
    print("🔐 Probando configuración OAuth...")
    
    try:
        from core.config import settings
        from auth.oauth import clickup_oauth
        
        print(f"   Client ID: {settings.CLICKUP_OAUTH_CLIENT_ID}")
        print(f"   Client Secret: {settings.CLICKUP_OAUTH_CLIENT_SECRET[:10]}...")
        print(f"   Redirect URI: {settings.CLICKUP_OAUTH_REDIRECT_URI}")
        
        # Generar URL de autorización
        auth_url = clickup_oauth.get_authorization_url()
        print(f"   URL de autorización: {auth_url[:100]}...")
        
        if auth_url and 'clickup.com' in auth_url and '7US6KJX26FOROTI3ZSOZYCAXBCG7W386' in auth_url:
            print("✅ Configuración OAuth correcta")
            return True
        else:
            print("❌ Error en la configuración OAuth")
            return False
            
    except Exception as e:
        print(f"❌ Error probando configuración: {e}")
        return False

async def test_oauth_flow():
    """Probar flujo OAuth completo"""
    print("\n🌐 Probando flujo OAuth...")
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        try:
            # Probar endpoint de OAuth
            print("   Probando /api/auth/clickup...")
            async with session.get(f"{base_url}/api/auth/clickup", allow_redirects=False) as response:
                if response.status == 302:
                    redirect_url = response.headers.get('Location', '')
                    print(f"   ✅ Redirección a ClickUp: {redirect_url[:100]}...")
                    
                    # Verificar que la URL contenga las credenciales correctas
                    if '7US6KJX26FOROTI3ZSOZYCAXBCG7W386' in redirect_url:
                        print("   ✅ Client ID correcto en la URL")
                    else:
                        print("   ❌ Client ID no encontrado en la URL")
                        return False
                    
                    if 'http://localhost:8000/api/auth/callback' in redirect_url:
                        print("   ✅ Redirect URI correcto")
                    else:
                        print("   ❌ Redirect URI incorrecto")
                        return False
                    
                    return True
                else:
                    print(f"   ❌ Error en OAuth: {response.status}")
                    return False
                    
        except aiohttp.ClientConnectorError:
            print("   ❌ No se puede conectar al servidor")
            print("   💡 Asegúrate de que la aplicación esté ejecutándose")
            return False
        except Exception as e:
            print(f"   ❌ Error inesperado: {e}")
            return False

def test_database_connection():
    """Probar conexión a la base de datos"""
    print("\n🗄️  Probando conexión a la base de datos...")
    
    try:
        from core.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Conexión a la base de datos exitosa")
            return True
            
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return False

def show_next_steps():
    """Mostrar próximos pasos"""
    print("\n🎯 PRÓXIMOS PASOS:")
    print("-" * 30)
    print("1. Inicia la aplicación:")
    print("   python start_with_oauth.py")
    print()
    print("2. Ve a la página de login:")
    print("   http://localhost:8000/api/auth/login")
    print()
    print("3. Haz clic en 'Iniciar con ClickUp'")
    print("4. Completa la autorización en ClickUp")
    print("5. Verifica que seas redirigido al dashboard")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Probar configuración OAuth
    if not test_oauth_configuration():
        print("\n❌ Error en la configuración OAuth")
        return
    
    # Probar conexión a la base de datos
    if not test_database_connection():
        print("\n❌ Error en la base de datos")
        return
    
    # Probar flujo OAuth
    print("\n🚀 Iniciando pruebas de flujo OAuth...")
    print("💡 Asegúrate de que la aplicación esté ejecutándose")
    
    try:
        result = asyncio.run(test_oauth_flow())
        if result:
            print("\n✅ ¡Todas las pruebas pasaron! OAuth está listo para usar")
            show_next_steps()
        else:
            print("\n❌ Algunas pruebas fallaron")
    except KeyboardInterrupt:
        print("\n⏹️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n❌ Error ejecutando pruebas: {e}")

if __name__ == "__main__":
    main()

