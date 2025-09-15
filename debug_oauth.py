#!/usr/bin/env python3
"""
Script para diagnosticar problemas de OAuth
"""

import requests
import json
from urllib.parse import urlencode

def test_oauth_configuration():
    """Probar configuración de OAuth"""
    print("🔍 DIAGNÓSTICO DE OAUTH")
    print("=" * 40)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Probar estado de OAuth
    try:
        response = requests.get(f"{base_url}/api/auth/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ Estado de OAuth:")
            print(f"   OAuth configurado: {data.get('oauth_configured')}")
            print(f"   Client ID configurado: {data.get('client_id_configured')}")
            print(f"   Client Secret configurado: {data.get('client_secret_configured')}")
            print(f"   Redirect URI: {data.get('redirect_uri')}")
            print(f"   Estado: {data.get('status')}")
            
            if data.get('oauth_configured'):
                # Probar redirección de OAuth
                print("\n🔗 Probando redirección de OAuth...")
                oauth_response = requests.get(f"{base_url}/api/auth/clickup", allow_redirects=False)
                print(f"   Código de respuesta: {oauth_response.status_code}")
                
                if oauth_response.status_code in [301, 302, 307, 308]:
                    location = oauth_response.headers.get('Location', '')
                    print(f"   URL de redirección: {location}")
                    
                    if 'clickup.com' in location:
                        print("✅ Redirección a ClickUp funcionando")
                        
                        # Verificar si la URL tiene el formato correcto
                        if 'client_id=' in location and 'redirect_uri=' in location:
                            print("✅ URL de autorización tiene formato correcto")
                        else:
                            print("❌ URL de autorización tiene formato incorrecto")
                    else:
                        print("❌ No se está redirigiendo a ClickUp")
                else:
                    print(f"❌ Error en redirección: {oauth_response.status_code}")
            else:
                print("❌ OAuth no está configurado correctamente")
        else:
            print(f"❌ Error obteniendo estado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")

def show_clickup_setup_instructions():
    """Mostrar instrucciones para configurar ClickUp"""
    print("\n📋 INSTRUCCIONES PARA CONFIGURAR CLICKUP:")
    print("-" * 50)
    print("1. Ve a https://app.clickup.com/settings/apps")
    print("2. Selecciona tu aplicación 'ClickUp Project Manager'")
    print("3. Verifica que la URL de redirección sea EXACTAMENTE:")
    print("   https://clickuptaskmanager-production.up.railway.app/api/auth/callback")
    print("4. Verifica que tenga estos permisos:")
    print("   ✅ read:user")
    print("   ✅ read:workspace")
    print("   ✅ read:task")
    print("   ✅ write:task")
    print("5. Si hay problemas, elimina la app y crea una nueva")

def main():
    """Función principal"""
    test_oauth_configuration()
    show_clickup_setup_instructions()

if __name__ == "__main__":
    main()


