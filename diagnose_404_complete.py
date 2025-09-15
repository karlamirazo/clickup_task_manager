#!/usr/bin/env python3
"""
Diagnóstico completo del error 404 de ClickUp
"""

import requests
import webbrowser
from urllib.parse import urlencode

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO COMPLETO ERROR 404 CLICKUP")
    print("=" * 60)
    print()

def test_app_directly():
    """Probar la aplicación directamente"""
    print("🌐 PROBANDO APLICACIÓN DIRECTAMENTE:")
    print("-" * 40)
    
    try:
        response = requests.get("https://clickuptaskmanager-production.up.railway.app", timeout=10)
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Content-Length: {len(response.text)}")
        
        if "ClickUp OAuth Test" in response.text:
            print("✅ Aplicación funcionando correctamente")
            return True
        else:
            print("⚠️  Aplicación responde pero contenido inesperado")
            print("📄 Primeros 200 caracteres:")
            print(response.text[:200])
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_oauth_endpoint():
    """Probar el endpoint OAuth"""
    print("\n🔗 PROBANDO ENDPOINT OAUTH:")
    print("-" * 35)
    
    try:
        response = requests.get("https://clickuptaskmanager-production.up.railway.app/oauth", timeout=10)
        print(f"✅ OAuth endpoint status: {response.status_code}")
        
        if response.status_code in [200, 302, 307]:
            print("✅ OAuth endpoint funcionando")
            return True
        else:
            print("⚠️  OAuth endpoint no responde correctamente")
            return False
            
    except Exception as e:
        print(f"❌ Error en OAuth endpoint: {e}")
        return False

def generate_clickup_test_url():
    """Generar URL de prueba para ClickUp"""
    print("\n🧪 GENERANDO URL DE PRUEBA CLICKUP:")
    print("-" * 45)
    
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
    print("📝 FLUJO ESPERADO:")
    print("1. ClickUp redirigirá a: https://clickuptaskmanager-production.up.railway.app?code=...")
    print("2. Tu app debería interceptar esto y mostrar el código")
    print()
    
    return auth_url

def test_callback_simulation():
    """Simular callback de OAuth"""
    print("\n🧪 SIMULANDO CALLBACK OAUTH:")
    print("-" * 35)
    
    # Simular URL de callback real
    callback_url = "https://clickuptaskmanager-production.up.railway.app?code=test123&state=test456"
    
    try:
        response = requests.get(callback_url, timeout=10)
        print(f"✅ Callback simulation - Status: {response.status_code}")
        
        if response.status_code == 200:
            if "OAuth Exitoso" in response.text:
                print("✅ La aplicación maneja correctamente el callback")
                return True
            else:
                print("⚠️  La aplicación responde pero no muestra el callback correctamente")
                print("📄 Primeros 200 caracteres:")
                print(response.text[:200])
                return False
        else:
            print(f"⚠️  La aplicación no maneja correctamente el callback (Status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Error en callback simulation: {e}")
        return False

def show_clickup_config_instructions():
    """Mostrar instrucciones de configuración de ClickUp"""
    print("\n🔧 CONFIGURACIÓN EXACTA EN CLICKUP:")
    print("-" * 45)
    print("1. Ve a: https://app.clickup.com/settings/apps")
    print("2. Busca tu aplicación OAuth")
    print("3. En 'Redireccionamiento de URL' pon EXACTAMENTE:")
    print()
    print("   clickuptaskmanager-production.up.railway.app")
    print()
    print("4. NO incluyas https://")
    print("5. NO incluyas espacios")
    print("6. Guarda los cambios")
    print("7. Espera 30 segundos")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Probar aplicación directamente
    app_ok = test_app_directly()
    
    # Probar endpoint OAuth
    oauth_ok = test_oauth_endpoint()
    
    # Simular callback
    callback_ok = test_callback_simulation()
    
    # Generar URL de prueba
    auth_url = generate_clickup_test_url()
    
    # Mostrar configuración de ClickUp
    show_clickup_config_instructions()
    
    print("\n📊 RESUMEN DEL DIAGNÓSTICO:")
    print("-" * 35)
    print(f"Aplicación principal: {'✅ OK' if app_ok else '❌ ERROR'}")
    print(f"Endpoint OAuth: {'✅ OK' if oauth_ok else '❌ ERROR'}")
    print(f"Callback simulation: {'✅ OK' if callback_ok else '❌ ERROR'}")
    
    if app_ok and oauth_ok and callback_ok:
        print("\n🎉 ¡Todo funciona correctamente!")
        print("💡 El problema está en la configuración de ClickUp")
        print("🔧 Verifica que la URL de redirección sea exactamente:")
        print("   clickuptaskmanager-production.up.railway.app")
    else:
        print("\n❌ Hay problemas con la aplicación")
        print("💡 Revisa los logs de Railway")
    
    print("\n🧪 PRUEBA FINAL:")
    print("-" * 20)
    response = input("¿Quieres abrir la URL de prueba de ClickUp? (s/n): ").lower()
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        try:
            webbrowser.open(auth_url)
            print("✅ URL abierta en el navegador")
            print("🔍 Si ves error 404, el problema está en ClickUp")
            print("🔍 Si ves la página de autorización, el problema está en la redirección")
        except Exception as e:
            print(f"❌ Error abriendo navegador: {e}")
    
    print("\n✅ Diagnóstico completado!")

if __name__ == "__main__":
    main()
