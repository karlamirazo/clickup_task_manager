#!/usr/bin/env python3
"""
Script para probar el flujo completo de OAuth
"""

import requests
import sys
from urllib.parse import urlparse, parse_qs

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🔄 PRUEBA DE FLUJO OAUTH COMPLETO")
    print("=" * 60)
    print()

def test_oauth_flow():
    """Probar el flujo completo de OAuth"""
    base_url = "http://localhost:8000"
    
    print("🌐 Probando flujo OAuth...")
    
    # Paso 1: Obtener la página de login
    print("1️⃣ Obteniendo página de login...")
    try:
        response = requests.get(f"{base_url}/api/auth/login")
        if response.status_code == 200:
            print("   ✅ Página de login accesible")
        else:
            print(f"   ❌ Error en página de login: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error en página de login: {e}")
        return False
    
    # Paso 2: Probar endpoint OAuth
    print("2️⃣ Probando endpoint OAuth...")
    try:
        response = requests.get(f"{base_url}/api/auth/clickup", allow_redirects=False)
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            print(f"   ✅ Redirección a ClickUp: {redirect_url[:80]}...")
            
            # Verificar que la URL contiene los parámetros correctos
            parsed_url = urlparse(redirect_url)
            query_params = parse_qs(parsed_url.query)
            
            if 'client_id' in query_params:
                print(f"   ✅ Client ID presente: {query_params['client_id'][0][:20]}...")
            else:
                print("   ❌ Client ID no encontrado")
                return False
                
            if 'redirect_uri' in query_params:
                print(f"   ✅ Redirect URI: {query_params['redirect_uri'][0]}")
            else:
                print("   ❌ Redirect URI no encontrado")
                return False
                
        else:
            print(f"   ❌ Error en endpoint OAuth: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error en endpoint OAuth: {e}")
        return False
    
    # Paso 3: Probar dashboard
    print("3️⃣ Probando dashboard...")
    try:
        response = requests.get(f"{base_url}/dashboard")
        if response.status_code == 200:
            print("   ✅ Dashboard accesible")
        else:
            print(f"   ❌ Error en dashboard: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error en dashboard: {e}")
        return False
    
    return True

def show_instructions():
    """Mostrar instrucciones para el usuario"""
    print("\n" + "=" * 60)
    print("📋 INSTRUCCIONES PARA PROBAR OAUTH")
    print("=" * 60)
    print()
    print("1. Abre tu navegador")
    print("2. Ve a: http://localhost:8000/api/auth/login")
    print("3. Haz clic en 'Iniciar con ClickUp'")
    print("4. Completa la autorización en ClickUp")
    print("5. ¡Serás redirigido al dashboard!")
    print()
    print("🔧 CAMBIOS REALIZADOS:")
    print("   - Callback OAuth redirige a /dashboard")
    print("   - Dashboard maneja el token OAuth")
    print("   - Token se guarda en localStorage")
    print("   - Estado de conexión se actualiza")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Probar flujo
    if test_oauth_flow():
        print("\n✅ ¡Flujo OAuth funcionando correctamente!")
        show_instructions()
    else:
        print("\n❌ Hay problemas en el flujo OAuth")
        print("💡 Verifica que la aplicación esté ejecutándose:")
        print("   python main_simple.py")

if __name__ == "__main__":
    main()
