#!/usr/bin/env python3
"""
Script simple para probar la aplicación
"""

import sys
import os

def test_imports():
    """Probar importaciones básicas"""
    print("🔍 Probando importaciones...")
    
    try:
        from app.main import app
        print("✅ Aplicación importada correctamente")
        return True
    except Exception as e:
        print(f"❌ Error importando aplicación: {e}")
        return False

def test_routes():
    """Probar rutas básicas"""
    print("🔍 Probando rutas...")
    
    try:
        from app.main import app
        
        # Obtener lista de rutas
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append({
                    'path': route.path,
                    'methods': list(route.methods) if route.methods else ['GET']
                })
        
        print(f"✅ {len(routes)} rutas encontradas")
        
        # Mostrar rutas importantes
        important_routes = [
            '/', '/login', '/dashboard', '/api', '/api/auth/login', 
            '/api/auth/clickup', '/api/auth/status'
        ]
        
        for route_path in important_routes:
            found = any(r['path'] == route_path for r in routes)
            status = "✅" if found else "❌"
            print(f"   {status} {route_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando rutas: {e}")
        return False

def test_config():
    """Probar configuración"""
    print("🔍 Probando configuración...")
    
    try:
        from core.config import settings
        
        print(f"✅ Puerto: {settings.PORT}")
        print(f"✅ Host: {settings.HOST}")
        print(f"✅ Entorno: {settings.ENVIRONMENT}")
        
        # Verificar OAuth
        oauth_configured = bool(
            getattr(settings, 'CLICKUP_OAUTH_CLIENT_ID', '') and 
            getattr(settings, 'CLICKUP_OAUTH_CLIENT_SECRET', '')
        )
        
        if oauth_configured:
            print("✅ OAuth de ClickUp configurado")
        else:
            print("⚠️  OAuth de ClickUp no configurado (opcional)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando configuración: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 PROBANDO APLICACIÓN CLICKUP PROJECT MANAGER")
    print("=" * 50)
    
    # Probar importaciones
    if not test_imports():
        print("\n❌ No se puede continuar - error en importaciones")
        return False
    
    print()
    
    # Probar configuración
    if not test_config():
        print("\n⚠️  Advertencias en configuración")
    
    print()
    
    # Probar rutas
    if not test_routes():
        print("\n❌ Error en rutas")
        return False
    
    print()
    print("✅ ¡Aplicación lista para usar!")
    print()
    print("🌐 Para iniciar la aplicación:")
    print("   python -m uvicorn app.main:app --reload")
    print()
    print("🔗 URLs importantes:")
    print("   http://localhost:8000/          - Página principal")
    print("   http://localhost:8000/login     - Página de login")
    print("   http://localhost:8000/dashboard - Dashboard")
    print("   http://localhost:8000/api       - API")
    print("   http://localhost:8000/api/auth/status - Estado de autenticación")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
