#!/usr/bin/env python3
"""
Script para probar la corrección de OAuth
"""

import os
import webbrowser
from urllib.parse import urlencode

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🧪 PRUEBA DE CORRECCIÓN OAUTH CLICKUP")
    print("=" * 60)
    print()

def show_configuration():
    """Mostrar configuración actual"""
    print("📋 CONFIGURACIÓN ACTUAL:")
    print("-" * 30)
    
    client_id = "0J2LPSHXIM5PRB5VDE5CRJY7FJP86L0H"
    redirect_uri = "https://clickuptaskmanager-production.up.railway.app"
    
    print(f"Client ID: {client_id}")
    print(f"Redirect URI: {redirect_uri}")
    print()
    print("✅ ClickUp debe estar configurado con esta URL exacta")
    print("✅ La aplicación interceptará y redirigirá internamente")
    print()

def generate_test_url():
    """Generar URL de prueba"""
    client_id = "0J2LPSHXIM5PRB5VDE5CRJY7FJP86L0H"
    redirect_uri = "https://clickuptaskmanager-production.up.railway.app"
    
    auth_url = f"https://app.clickup.com/api/v2/oauth/authorize?" + urlencode({
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'read:user read:workspace read:task write:task'
    })
    
    return auth_url

def test_oauth_flow():
    """Probar el flujo de OAuth"""
    print("🔗 URL DE PRUEBA:")
    print("-" * 20)
    
    auth_url = generate_test_url()
    print(auth_url)
    print()
    
    print("📝 FLUJO ESPERADO:")
    print("1. ClickUp redirigirá a: https://clickuptaskmanager-production.up.railway.app?code=...")
    print("2. Nuestra app interceptará esto en la ruta '/'")
    print("3. Redirigirá internamente a: /api/auth/callback?code=...")
    print("4. El callback procesará la autenticación")
    print()
    
    response = input("¿Abrir URL de prueba en el navegador? (s/n): ").lower()
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        try:
            webbrowser.open(auth_url)
            print("✅ URL abierta en el navegador")
            print()
            print("🔍 VERIFICA:")
            print("- Si ves error 404: ClickUp no está configurado correctamente")
            print("- Si ves la página de autorización: ¡Perfecto!")
            print("- Si autorizas y te redirige correctamente: ¡Éxito total!")
        except Exception as e:
            print(f"❌ Error abriendo navegador: {e}")

def show_clickup_instructions():
    """Mostrar instrucciones para ClickUp"""
    print("🔧 CONFIGURACIÓN EN CLICKUP:")
    print("-" * 35)
    print("1. Ve a https://app.clickup.com/settings/apps")
    print("2. Busca 'ClickUp Project Manager v2'")
    print("3. En 'Redireccionamiento de URL' pon EXACTAMENTE:")
    print("   https://clickuptaskmanager-production.up.railway.app")
    print("4. NO incluyas /api/auth/callback")
    print("5. Guarda los cambios")
    print()

def main():
    """Función principal"""
    print_banner()
    
    show_configuration()
    show_clickup_instructions()
    
    response = input("¿Has configurado ClickUp con la URL correcta? (s/n): ").lower()
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        test_oauth_flow()
    else:
        print("⚠️  Primero configura ClickUp y luego ejecuta este script")
        print()
        show_clickup_instructions()
    
    print("\n✅ ¡Prueba completada!")
    print("🚀 Si todo funciona, tu OAuth está corregido")

if __name__ == "__main__":
    main()
