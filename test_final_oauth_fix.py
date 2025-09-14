#!/usr/bin/env python3
"""
Verificación final del OAuth después de corregir las URLs de Railway
"""

import requests
from urllib.parse import urlparse, parse_qs

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🎯 VERIFICACIÓN FINAL OAUTH - URLS CORREGIDAS")
    print("=" * 60)
    print()

def test_oauth_url():
    """Probar URL de OAuth"""
    print("🔗 Probando URL de OAuth...")
    
    try:
        response = requests.get("http://localhost:8000/api/auth/clickup", allow_redirects=False)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 307:
            redirect_url = response.headers.get('Location', '')
            print(f"   Redirect URL: {redirect_url}")
            
            # Verificar que la URL sea de ClickUp
            if 'app.clickup.com' in redirect_url:
                print("   ✅ URL de ClickUp generada correctamente")
                
                # Extraer parámetros
                parsed = urlparse(redirect_url)
                params = parse_qs(parsed.query)
                
                client_id = params.get('client_id', [None])[0]
                redirect_uri = params.get('redirect_uri', [None])[0]
                
                print(f"   Client ID: {client_id[:20] if client_id else 'None'}...")
                print(f"   Redirect URI: {redirect_uri}")
                
                # Verificar que la redirect_uri sea localhost
                if 'localhost:8000' in redirect_uri:
                    print("   ✅ Redirect URI es localhost (correcto)")
                    return True
                elif 'railway.app' in redirect_uri:
                    print("   ❌ Redirect URI es Railway (incorrecto)")
                    return False
                else:
                    print(f"   ⚠️  Redirect URI inesperada: {redirect_uri}")
                    return False
            else:
                print("   ❌ URL no es de ClickUp")
                return False
        else:
            print(f"   ❌ Error obteniendo URL: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_clickup_access():
    """Probar acceso a ClickUp"""
    print("\n🌐 Probando acceso a ClickUp...")
    
    try:
        # Obtener URL de OAuth
        response = requests.get("http://localhost:8000/api/auth/clickup", allow_redirects=False)
        
        if response.status_code == 307:
            clickup_url = response.headers.get('Location', '')
            
            # Probar la URL de ClickUp
            clickup_response = requests.get(clickup_url, allow_redirects=False)
            print(f"   ClickUp Status: {clickup_response.status_code}")
            
            if clickup_response.status_code == 200:
                print("   ✅ ClickUp accesible")
                return True
            elif clickup_response.status_code == 302:
                print("   ✅ ClickUp redirige (normal)")
                return True
            else:
                print(f"   ❌ Error en ClickUp: {clickup_response.status_code}")
                return False
        else:
            print("   ❌ No se pudo obtener URL de ClickUp")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def show_success_message():
    """Mostrar mensaje de éxito"""
    print("\n" + "=" * 60)
    print("🎉 ¡PROBLEMA RESUELTO!")
    print("=" * 60)
    print()
    print("✅ CAMBIOS APLICADOS:")
    print("   - URLs de Railway eliminadas de la configuración")
    print("   - Redirect URI configurada para localhost")
    print("   - OAuth configurado correctamente")
    print()
    print("🚀 PRÓXIMOS PASOS:")
    print("   1. Ve a: http://localhost:8000/api/auth/login")
    print("   2. Haz clic en 'Iniciar con ClickUp'")
    print("   3. Completa la autorización en ClickUp")
    print("   4. ¡Serás redirigido al dashboard!")
    print()
    print("🔧 CONFIGURACIÓN EN CLICKUP:")
    print("   - Redirect URI debe ser: http://localhost:8000/api/auth/callback")
    print("   - Permisos: read:user, read:workspace, read:task, write:task")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Probar URL de OAuth
    oauth_ok = test_oauth_url()
    
    # Probar acceso a ClickUp
    clickup_ok = test_clickup_access()
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL")
    print("=" * 60)
    print(f"✅ OAuth URL: {'OK' if oauth_ok else 'ERROR'}")
    print(f"✅ ClickUp Access: {'OK' if clickup_ok else 'ERROR'}")
    
    if oauth_ok and clickup_ok:
        print("\n🎉 ¡TODO FUNCIONANDO CORRECTAMENTE!")
        show_success_message()
    else:
        print("\n❌ Aún hay problemas")
        print("💡 Verifica que la aplicación esté ejecutándose")

if __name__ == "__main__":
    main()
