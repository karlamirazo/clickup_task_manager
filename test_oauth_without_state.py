#!/usr/bin/env python3
"""
Probar OAuth sin validación de state
"""

import requests
import webbrowser
from urllib.parse import urlencode

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🔄 PRUEBA OAUTH SIN VALIDACIÓN DE STATE")
    print("=" * 60)
    print()

def test_oauth_without_state_validation():
    """Probar OAuth deshabilitando la validación de state"""
    print("🎯 Probando OAuth sin validación de state...")
    
    # URL base de la aplicación
    base_url = "http://localhost:8000"
    
    # Simular callback con un state cualquiera
    callback_params = {
        'code': 'test_authorization_code_12345',
        'state': 'any_state_value'
    }
    
    # Construir URL de callback
    callback_url = f"{base_url}/api/auth/callback?" + urlencode(callback_params)
    print(f"   URL de callback: {callback_url}")
    
    # Probar el callback
    try:
        response = requests.get(callback_url, allow_redirects=False)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 307:  # Redirect
            redirect_url = response.headers.get('Location', '')
            print(f"   Redirige a: {redirect_url}")
            
            if '/dashboard' in redirect_url:
                print("   ✅ Redirección correcta al dashboard")
                return True
            elif 'error' in redirect_url:
                print("   ❌ Redirección con error")
                print(f"   Error: {redirect_url}")
                return False
            else:
                print("   ❌ Redirección inesperada")
                return False
        else:
            print(f"   ❌ No redirige (status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en callback: {e}")
        return False

def show_solution():
    """Mostrar solución temporal"""
    print("\n" + "=" * 60)
    print("💡 SOLUCIÓN TEMPORAL")
    print("=" * 60)
    print()
    print("Para probar rápidamente, voy a deshabilitar temporalmente")
    print("la validación de state en el callback OAuth.")
    print()
    print("Esto permitirá que el OAuth funcione sin problemas")
    print("mientras verificamos la configuración de ClickUp.")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Probar OAuth sin validación de state
    oauth_ok = test_oauth_without_state_validation()
    
    if not oauth_ok:
        print("\n❌ OAuth no funciona ni siquiera sin validación de state")
        print("💡 Hay un problema más profundo en la configuración")
    else:
        print("\n✅ OAuth funciona sin validación de state")
        print("💡 El problema está en la validación de state")
        show_solution()

if __name__ == "__main__":
    main()

