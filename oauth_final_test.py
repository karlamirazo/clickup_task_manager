#!/usr/bin/env python3
"""
Script final de verificación OAuth
"""

import os
import sys
import asyncio
import aiohttp

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🎯 VERIFICACIÓN FINAL OAUTH")
    print("=" * 60)
    print()

def test_oauth_configuration():
    """Probar configuración OAuth"""
    print("🔐 Verificando configuración OAuth...")
    
    try:
        from core.config import settings
        from auth.oauth import clickup_oauth
        
        print(f"   ✅ Client ID: {settings.CLICKUP_OAUTH_CLIENT_ID}")
        print(f"   ✅ Client Secret: {settings.CLICKUP_OAUTH_CLIENT_SECRET[:10]}...")
        print(f"   ✅ Redirect URI: {settings.CLICKUP_OAUTH_REDIRECT_URI}")
        
        # Generar URL de autorización
        auth_url = clickup_oauth.get_authorization_url()
        print(f"   ✅ URL de autorización: {auth_url[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_database():
    """Probar base de datos"""
    print("\n🗄️  Verificando base de datos...")
    
    try:
        from core.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("   ✅ Conexión a la base de datos exitosa")
            return True
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

async def test_application():
    """Probar aplicación"""
    print("\n🌐 Verificando aplicación...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Probar endpoint principal
            async with session.get("http://localhost:8000/") as response:
                if response.status == 200:
                    print("   ✅ Aplicación ejecutándose")
                    return True
                else:
                    print(f"   ❌ Error: {response.status}")
                    return False
                    
    except aiohttp.ClientConnectorError:
        print("   ❌ Aplicación no ejecutándose")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def show_instructions():
    """Mostrar instrucciones finales"""
    print("\n" + "=" * 60)
    print("🎉 ¡OAUTH CONFIGURADO EXITOSAMENTE!")
    print("=" * 60)
    print()
    print("📋 INSTRUCCIONES PARA USAR:")
    print("-" * 40)
    print("1. Inicia la aplicación:")
    print("   python -m uvicorn app.main:app --reload")
    print()
    print("2. Abre tu navegador y ve a:")
    print("   http://localhost:8000/api/auth/login")
    print()
    print("3. Haz clic en 'Iniciar con ClickUp'")
    print("4. Completa la autorización en ClickUp")
    print("5. ¡Serás redirigido al dashboard!")
    print()
    print("🔧 ARCHIVOS IMPORTANTES:")
    print("-" * 40)
    print("   • .env - Configuración de la aplicación")
    print("   • static/auth.html - Página de autenticación")
    print("   • auth/oauth.py - Lógica OAuth")
    print("   • api/routes/auth.py - Rutas de autenticación")
    print()
    print("🧪 SCRIPTS DE PRUEBA:")
    print("-" * 40)
    print("   • python diagnose_oauth.py - Diagnóstico completo")
    print("   • python test_real_oauth.py - Prueba OAuth")
    print("   • python setup_oauth.py - Configuración")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Verificar configuración OAuth
    oauth_ok = test_oauth_configuration()
    
    # Verificar base de datos
    db_ok = test_database()
    
    # Verificar aplicación
    app_ok = asyncio.run(test_application())
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN:")
    print("=" * 60)
    print(f"   Configuración OAuth: {'✅' if oauth_ok else '❌'}")
    print(f"   Base de datos: {'✅' if db_ok else '❌'}")
    print(f"   Aplicación: {'✅' if app_ok else '❌'}")
    
    if oauth_ok and db_ok:
        print("\n🎉 ¡OAuth está completamente configurado!")
        show_instructions()
    else:
        print("\n❌ Hay problemas que resolver")
        if not oauth_ok:
            print("   - Ejecuta: python diagnose_oauth.py")
        if not db_ok:
            print("   - Verifica la conexión a PostgreSQL")

if __name__ == "__main__":
    main()

