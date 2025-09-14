#!/usr/bin/env python3
"""
Simular el callback de ClickUp para probar la redirección
"""

import requests
import webbrowser
from urllib.parse import urlencode

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🔄 SIMULACIÓN DE CALLBACK OAUTH")
    print("=" * 60)
    print()

def simulate_clickup_callback():
    """Simular el callback que hace ClickUp"""
    print("🎯 Simulando callback de ClickUp...")
    
    # URL base de la aplicación
    base_url = "http://localhost:8000"
    
    # Parámetros que ClickUp envía de vuelta
    callback_params = {
        'code': 'test_authorization_code_12345',
        'state': 'test_state_67890'
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
            
            # Verificar si la redirección es correcta
            if '/dashboard' in redirect_url:
                print("   ✅ Redirección correcta al dashboard")
                return True
            else:
                print("   ❌ Redirección incorrecta")
                return False
        else:
            print(f"   ❌ No redirige (status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en callback: {e}")
        return False

def test_dashboard_access():
    """Probar acceso al dashboard"""
    print("\n🏠 Probando acceso al dashboard...")
    
    try:
        response = requests.get("http://localhost:8000/dashboard")
        if response.status_code == 200:
            print("   ✅ Dashboard accesible")
            return True
        else:
            print(f"   ❌ Dashboard no accesible (status: {response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ Error accediendo al dashboard: {e}")
        return False

def show_clickup_config_instructions():
    """Mostrar instrucciones para configurar ClickUp"""
    print("\n" + "=" * 60)
    print("🔧 CONFIGURACIÓN REQUERIDA EN CLICKUP")
    print("=" * 60)
    print()
    print("El problema es que la URL de redirección en ClickUp no está")
    print("configurada correctamente. Sigue estos pasos:")
    print()
    print("1. Ve a: https://app.clickup.com/settings/apps")
    print("2. Busca tu aplicación 'ClickUp Project Manager'")
    print("3. Haz clic en 'Edit' o 'Configurar'")
    print("4. En 'Redirect URI' asegúrate de que esté:")
    print("   http://localhost:8000/api/auth/callback")
    print("5. Guarda los cambios")
    print()
    print("⚠️  IMPORTANTE:")
    print("   - La URL debe ser EXACTAMENTE: http://localhost:8000/api/auth/callback")
    print("   - No debe tener '/' al final")
    print("   - Debe usar 'http' no 'https'")
    print("   - Debe usar 'localhost' no '127.0.0.1'")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Simular callback
    callback_ok = simulate_clickup_callback()
    
    # Probar dashboard
    dashboard_ok = test_dashboard_access()
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO DE LA SIMULACIÓN")
    print("=" * 60)
    print(f"✅ Callback: {'OK' if callback_ok else 'ERROR'}")
    print(f"✅ Dashboard: {'OK' if dashboard_ok else 'ERROR'}")
    
    if not callback_ok:
        print("\n❌ El callback no funciona correctamente")
        show_clickup_config_instructions()
    elif not dashboard_ok:
        print("\n❌ El dashboard no es accesible")
        print("💡 Verifica que la aplicación esté ejecutándose")
    else:
        print("\n✅ Todo funciona correctamente en la simulación")
        print("💡 El problema debe estar en la configuración de ClickUp")

if __name__ == "__main__":
    main()
