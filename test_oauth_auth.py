#!/usr/bin/env python3
"""
Script de prueba para verificar la autenticación OAuth
"""

import os
import sys
import asyncio
import aiohttp
from urllib.parse import urlencode

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🧪 PRUEBA DE AUTENTICACIÓN OAUTH")
    print("=" * 60)
    print()

def check_environment():
    """Verificar configuración del entorno"""
    print("🔍 Verificando configuración del entorno...")
    
    # Verificar si existe .env
    if not os.path.exists('.env'):
        print("❌ Archivo .env no encontrado")
        print("💡 Copia env.oauth.local.example como .env y configura las variables")
        return False
    
    # Verificar variables de OAuth
    from dotenv import load_dotenv
    load_dotenv()
    
    client_id = os.getenv('CLICKUP_OAUTH_CLIENT_ID')
    client_secret = os.getenv('CLICKUP_OAUTH_CLIENT_SECRET')
    redirect_uri = os.getenv('CLICKUP_OAUTH_REDIRECT_URI')
    
    if not client_id or client_id == 'tu_client_id_aqui':
        print("❌ CLICKUP_OAUTH_CLIENT_ID no configurado")
        return False
    
    if not client_secret or client_secret == 'tu_client_secret_aqui':
        print("❌ CLICKUP_OAUTH_CLIENT_SECRET no configurado")
        return False
    
    if not redirect_uri:
        print("⚠️  CLICKUP_OAUTH_REDIRECT_URI no configurado")
        return False
    
    print("✅ Configuración de OAuth encontrada")
    print(f"   Client ID: {client_id[:10]}...")
    print(f"   Redirect URI: {redirect_uri}")
    return True

async def test_auth_endpoints():
    """Probar endpoints de autenticación"""
    print("\n🌐 Probando endpoints de autenticación...")
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        try:
            # Probar endpoint de login
            print("   Probando /api/auth/login...")
            async with session.get(f"{base_url}/api/auth/login") as response:
                if response.status == 200:
                    print("   ✅ Página de login accesible")
                else:
                    print(f"   ❌ Error en página de login: {response.status}")
                    return False
            
            # Probar endpoint de OAuth
            print("   Probando /api/auth/clickup...")
            async with session.get(f"{base_url}/api/auth/clickup", allow_redirects=False) as response:
                if response.status == 302:
                    redirect_url = response.headers.get('Location', '')
                    if 'clickup.com' in redirect_url:
                        print("   ✅ Redirección a ClickUp correcta")
                        print(f"   🔗 URL: {redirect_url[:100]}...")
                    else:
                        print(f"   ⚠️  Redirección inesperada: {redirect_url}")
                else:
                    print(f"   ❌ Error en OAuth: {response.status}")
                    return False
            
            # Probar endpoint de roles
            print("   Probando /api/auth/roles...")
            async with session.get(f"{base_url}/api/auth/roles") as response:
                if response.status == 200:
                    data = await response.json()
                    print("   ✅ Roles disponibles:")
                    for role, name in data.get('roles', {}).items():
                        print(f"      - {role}: {name}")
                else:
                    print(f"   ❌ Error en roles: {response.status}")
            
            return True
            
        except aiohttp.ClientConnectorError:
            print("   ❌ No se puede conectar al servidor")
            print("   💡 Asegúrate de que la aplicación esté ejecutándose en http://localhost:8000")
            return False
        except Exception as e:
            print(f"   ❌ Error inesperado: {e}")
            return False

def test_oauth_url_generation():
    """Probar generación de URL de OAuth"""
    print("\n🔗 Probando generación de URL de OAuth...")
    
    try:
        from core.config import settings
        from auth.oauth import clickup_oauth
        
        # Generar URL de autorización
        auth_url = clickup_oauth.get_authorization_url()
        
        if auth_url and 'clickup.com' in auth_url:
            print("   ✅ URL de autorización generada correctamente")
            print(f"   🔗 URL: {auth_url[:100]}...")
            
            # Verificar parámetros
            if 'client_id=' in auth_url and 'redirect_uri=' in auth_url:
                print("   ✅ Parámetros de OAuth presentes")
            else:
                print("   ⚠️  Faltan parámetros en la URL")
            
            return True
        else:
            print("   ❌ Error generando URL de autorización")
            return False
            
    except Exception as e:
        print(f"   ❌ Error generando URL: {e}")
        return False

def show_test_instructions():
    """Mostrar instrucciones para probar manualmente"""
    print("\n📋 INSTRUCCIONES PARA PRUEBA MANUAL:")
    print("-" * 50)
    print("1. Inicia la aplicación:")
    print("   python -m uvicorn app.main:app --reload")
    print()
    print("2. Abre tu navegador y ve a:")
    print("   http://localhost:8000/api/auth/login")
    print()
    print("3. Haz clic en 'Iniciar con ClickUp'")
    print("4. Completa la autorización en ClickUp")
    print("5. Verifica que seas redirigido de vuelta al dashboard")
    print()
    print("6. Verifica que tu usuario se haya creado/actualizado en la base de datos")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Verificar configuración
    if not check_environment():
        print("\n❌ No se puede continuar sin configuración OAuth")
        print("💡 Ejecuta: python setup_oauth.py")
        return
    
    # Probar generación de URL
    if not test_oauth_url_generation():
        print("\n❌ Error en generación de URL OAuth")
        return
    
    # Probar endpoints
    print("\n🚀 Iniciando pruebas de endpoints...")
    print("💡 Asegúrate de que la aplicación esté ejecutándose")
    
    try:
        result = asyncio.run(test_auth_endpoints())
        if result:
            print("\n✅ Todas las pruebas pasaron correctamente!")
            show_test_instructions()
        else:
            print("\n❌ Algunas pruebas fallaron")
    except KeyboardInterrupt:
        print("\n⏹️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n❌ Error ejecutando pruebas: {e}")

if __name__ == "__main__":
    main()

