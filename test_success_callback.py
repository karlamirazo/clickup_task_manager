#!/usr/bin/env python3
"""
Simular callback exitoso para probar la redirección
"""

import requests

def test_success_callback():
    """Probar callback con datos simulados exitosos"""
    print("🎯 PROBANDO CALLBACK EXITOSO")
    print("=" * 40)
    
    # Simular callback exitoso
    callback_url = "http://localhost:8000/api/auth/callback"
    params = {
        'code': 'simulated_success_code_12345',
        'state': 'simulated_state_67890'
    }
    
    print(f"📤 Enviando callback a: {callback_url}")
    print(f"📋 Parámetros: {params}")
    
    try:
        response = requests.get(callback_url, params=params, allow_redirects=False)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if 'Location' in response.headers:
            redirect_url = response.headers['Location']
            print(f"🔄 Redirect URL: {redirect_url}")
            
            if '/dashboard' in redirect_url:
                print("✅ ¡Redirección al dashboard exitosa!")
                return True
            elif '/api/auth/login' in redirect_url:
                print("❌ Redirigiendo a login (error)")
                return False
            else:
                print(f"⚠️  Redirección inesperada: {redirect_url}")
                return False
        else:
            print("❌ No hay redirección")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_dashboard_direct():
    """Probar acceso directo al dashboard"""
    print("\n🏠 PROBANDO ACCESO DIRECTO AL DASHBOARD")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8000/dashboard")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Dashboard accesible directamente")
            return True
        else:
            print(f"❌ Dashboard no accesible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_instructions():
    """Mostrar instrucciones para el usuario"""
    print("\n📋 INSTRUCCIONES PARA PROBAR OAUTH REAL")
    print("=" * 50)
    print("1. Ve a: http://localhost:8000/api/auth/login")
    print("2. Haz clic en 'Iniciar con ClickUp'")
    print("3. En ClickUp, haz clic en 'Continue on web anyway'")
    print("4. Completa la autorización")
    print("5. ClickUp te redirigirá automáticamente")
    print()
    print("🔧 Si sigue sin funcionar:")
    print("   - Verifica que la aplicación esté ejecutándose")
    print("   - Verifica que el puerto 8000 esté libre")
    print("   - Revisa los logs de la aplicación")

def main():
    """Función principal"""
    print("🎯 DIAGNÓSTICO DE REDIRECCIÓN OAUTH")
    print("=" * 50)
    
    # Probar callback simulado
    callback_ok = test_success_callback()
    
    # Probar dashboard directo
    dashboard_ok = test_dashboard_direct()
    
    # Mostrar instrucciones
    show_instructions()
    
    print("\n" + "=" * 50)
    print("📊 RESULTADO")
    print("=" * 50)
    print(f"Callback Simulado: {'✅ OK' if callback_ok else '❌ ERROR'}")
    print(f"Dashboard Directo: {'✅ OK' if dashboard_ok else '❌ ERROR'}")
    
    if callback_ok and dashboard_ok:
        print("\n🎉 ¡TODO FUNCIONANDO!")
        print("   El OAuth debería funcionar correctamente")
    else:
        print("\n❌ HAY PROBLEMAS")
        print("   Revisa la configuración de la aplicación")

if __name__ == "__main__":
    main()
