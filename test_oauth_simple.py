#!/usr/bin/env python3
"""
Probar OAuth con configuración simple
"""

import requests

def test_oauth():
    """Probar OAuth con 127.0.0.1:8000"""
    print("🧪 PROBANDO OAUTH CON CONFIGURACIÓN SIMPLE")
    print("=" * 50)
    
    try:
        # Probar URL de OAuth
        response = requests.get("http://127.0.0.1:8000/api/auth/clickup", allow_redirects=False)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 307:
            redirect_url = response.headers.get('Location', '')
            print(f"✅ URL generada: {redirect_url}")
            
            if '127.0.0.1:8000' in redirect_url:
                print("✅ URL usa 127.0.0.1:8000 correctamente")
                return True
            else:
                print("❌ URL no usa 127.0.0.1:8000")
                return False
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_clickup_instructions():
    """Mostrar instrucciones para ClickUp"""
    print("\n📋 CONFIGURAR CLICKUP")
    print("=" * 50)
    print("1. Ve a: https://app.clickup.com/settings/apps")
    print("2. Busca 'clickuptaskmanager'")
    print("3. Haz clic en 'Edit'")
    print("4. Cambia Redirect URI a:")
    print("   http://127.0.0.1:8000")
    print("5. Guarda los cambios")
    print()
    print("🔧 PERMISOS NECESARIOS:")
    print("   - read:user")
    print("   - read:workspace")
    print("   - read:task")
    print("   - write:task")

def main():
    """Función principal"""
    if test_oauth():
        print("\n🎉 ¡CONFIGURACIÓN FUNCIONANDO!")
        print("=" * 60)
        print("✅ OAuth generando URL correcta")
        print("✅ ClickUp debería aceptar esta URL")
        print()
        show_clickup_instructions()
        print()
        print("📋 PRÓXIMOS PASOS:")
        print("1. Configura ClickUp con: http://127.0.0.1:8000")
        print("2. Prueba el OAuth completo")
        print("3. ¡Debería funcionar ahora!")
    else:
        print("\n❌ Error en la configuración")

if __name__ == "__main__":
    main()

