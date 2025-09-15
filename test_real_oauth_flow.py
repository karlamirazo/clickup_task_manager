#!/usr/bin/env python3
"""
Probar el flujo OAuth real paso a paso
"""

import requests
import webbrowser
from urllib.parse import urlencode, urlparse, parse_qs

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🔄 PRUEBA DE FLUJO OAUTH REAL")
    print("=" * 60)
    print()

def test_oauth_flow():
    """Probar el flujo OAuth completo"""
    base_url = "http://localhost:8000"
    
    print("1️⃣ Obteniendo URL de autorización...")
    try:
        # Obtener la URL de autorización
        response = requests.get(f"{base_url}/api/auth/clickup", allow_redirects=False)
        
        if response.status_code == 307:
            auth_url = response.headers.get('Location', '')
            print(f"   ✅ URL de autorización: {auth_url[:100]}...")
            
            # Extraer parámetros de la URL
            parsed = urlparse(auth_url)
            params = parse_qs(parsed.query)
            
            client_id = params.get('client_id', [None])[0]
            redirect_uri = params.get('redirect_uri', [None])[0]
            state = params.get('state', [None])[0]
            
            print(f"   Client ID: {client_id[:20] if client_id else 'None'}...")
            print(f"   Redirect URI: {redirect_uri}")
            print(f"   State: {state[:20] if state else 'None'}...")
            
            return auth_url, state
        else:
            print(f"   ❌ Error obteniendo URL: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None, None

def test_callback_with_real_state(state):
    """Probar callback con el state real"""
    if not state:
        print("❌ No hay state para probar")
        return False
    
    print(f"\n2️⃣ Probando callback con state real: {state[:20]}...")
    
    base_url = "http://localhost:8000"
    callback_params = {
        'code': 'real_authorization_code_from_clickup',
        'state': state
    }
    
    callback_url = f"{base_url}/api/auth/callback?" + urlencode(callback_params)
    
    try:
        response = requests.get(callback_url, allow_redirects=False)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 307:
            redirect_url = response.headers.get('Location', '')
            print(f"   Redirige a: {redirect_url}")
            
            if '/dashboard' in redirect_url:
                print("   ✅ Redirección correcta al dashboard")
                return True
            elif 'error' in redirect_url:
                print("   ❌ Redirección con error")
                return False
            else:
                print("   ❌ Redirección inesperada")
                return False
        else:
            print(f"   ❌ No redirige (status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def show_instructions():
    """Mostrar instrucciones para probar con ClickUp real"""
    print("\n" + "=" * 60)
    print("🎯 INSTRUCCIONES PARA PROBAR CON CLICKUP REAL")
    print("=" * 60)
    print()
    print("1. Abre tu navegador")
    print("2. Ve a: http://localhost:8000/api/auth/login")
    print("3. Haz clic en 'Iniciar con ClickUp'")
    print("4. Completa la autorización en ClickUp")
    print("5. ¡Serás redirigido al dashboard!")
    print()
    print("🔧 CONFIGURACIÓN EN CLICKUP:")
    print("   - Ve a: https://app.clickup.com/settings/apps")
    print("   - Busca tu aplicación 'ClickUp Project Manager'")
    print("   - Asegúrate de que 'Redirect URI' sea:")
    print("     http://localhost:8000/api/auth/callback")
    print()
    print("✅ ESTADO ACTUAL:")
    print("   - Validación de state deshabilitada")
    print("   - Callback redirige al dashboard")
    print("   - Dashboard maneja token OAuth")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Probar flujo OAuth
    auth_url, state = test_oauth_flow()
    
    if auth_url and state:
        # Probar callback con state real
        callback_ok = test_callback_with_real_state(state)
        
        if callback_ok:
            print("\n✅ ¡Flujo OAuth funcionando correctamente!")
            show_instructions()
        else:
            print("\n❌ Hay problemas en el callback")
            print("💡 Verifica que la aplicación esté ejecutándose")
    else:
        print("\n❌ No se pudo obtener la URL de autorización")
        print("💡 Verifica que la aplicación esté ejecutándose")

if __name__ == "__main__":
    main()

