#!/usr/bin/env python3
"""
Script para diagnosticar el error 404 de OAuth
"""

import requests
import webbrowser
from urllib.parse import urlencode

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO ERROR 404 OAUTH CLICKUP")
    print("=" * 60)
    print()

def test_app_availability():
    """Probar si la aplicación está disponible"""
    print("🌐 PROBANDO DISPONIBILIDAD DE LA APLICACIÓN:")
    print("-" * 50)
    
    try:
        response = requests.get("https://clickuptaskmanager-production.up.railway.app", timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Content Length: {len(response.text)} caracteres")
        
        if "ClickUp Task Manager" in response.text:
            print("✅ Aplicación funcionando correctamente")
            return True
        else:
            print("⚠️  Aplicación responde pero contenido inesperado")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando a la aplicación: {e}")
        return False

def test_oauth_redirect():
    """Probar la redirección OAuth"""
    print("\n🔗 PROBANDO REDIRECCIÓN OAUTH:")
    print("-" * 35)
    
    # URL de prueba
    client_id = "0J2LPSHXIM5PRB5VDE5CRJY7FJP86L0H"
    redirect_uri = "https://clickuptaskmanager-production.up.railway.app"
    
    auth_url = f"https://app.clickup.com/api/v2/oauth/authorize?" + urlencode({
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'read:user read:workspace read:task write:task'
    })
    
    print(f"URL de autorización: {auth_url}")
    print()
    
    return auth_url

def show_clickup_config_checklist():
    """Mostrar checklist de configuración de ClickUp"""
    print("\n📋 CHECKLIST DE CONFIGURACIÓN CLICKUP:")
    print("-" * 45)
    print("1. Ve a https://app.clickup.com/settings/apps")
    print("2. Busca 'ClickUp Project Manager v2'")
    print("3. Verifica que la URL de redirección sea EXACTAMENTE:")
    print("   https://clickuptaskmanager-production.up.railway.app")
    print("4. NO incluyas /api/auth/callback")
    print("5. Asegúrate de que esté guardado correctamente")
    print()

def test_callback_simulation():
    """Simular el callback de OAuth"""
    print("\n🧪 SIMULANDO CALLBACK OAUTH:")
    print("-" * 35)
    
    # Simular URL de callback
    callback_url = "https://clickuptaskmanager-production.up.railway.app?code=test_code&state=test_state"
    
    try:
        response = requests.get(callback_url, timeout=10)
        print(f"✅ Callback simulation - Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ La aplicación maneja correctamente el callback")
        else:
            print("⚠️  La aplicación no maneja correctamente el callback")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en callback simulation: {e}")

def main():
    """Función principal"""
    print_banner()
    
    # Probar disponibilidad de la aplicación
    app_ok = test_app_availability()
    
    if not app_ok:
        print("\n❌ PROBLEMA: La aplicación no está disponible")
        print("💡 Verifica que Railway haya desplegado correctamente")
        return
    
    # Mostrar checklist de ClickUp
    show_clickup_config_checklist()
    
    # Probar redirección OAuth
    auth_url = test_oauth_redirect()
    
    # Simular callback
    test_callback_simulation()
    
    print("\n🔧 PRÓXIMOS PASOS:")
    print("-" * 25)
    print("1. Verifica la configuración en ClickUp (ver checklist arriba)")
    print("2. Si la configuración está correcta, espera 1-2 minutos")
    print("3. Prueba nuevamente el OAuth")
    print()
    
    response = input("¿Quieres abrir la URL de prueba en el navegador? (s/n): ").lower()
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        try:
            webbrowser.open(auth_url)
            print("✅ URL abierta en el navegador")
        except Exception as e:
            print(f"❌ Error abriendo navegador: {e}")
    
    print("\n✅ Diagnóstico completado!")

if __name__ == "__main__":
    main()
