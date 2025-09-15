#!/usr/bin/env python3
"""
Script para verificar y corregir la configuración de OAuth
"""

import os
import webbrowser
from urllib.parse import urlencode

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🔧 CORRECCIÓN DE CONFIGURACIÓN OAUTH CLICKUP")
    print("=" * 60)
    print()

def show_current_config():
    """Mostrar configuración actual"""
    print("📋 CONFIGURACIÓN ACTUAL:")
    print("-" * 30)
    
    # Configuración de la aplicación
    client_id = "0J2LPSHXIM5PRB5VDE5CRJY7FJP86L0H"
    redirect_uri = "https://clickuptaskmanager-production.up.railway.app/api/auth/callback"
    
    print(f"Client ID: {client_id}")
    print(f"Redirect URI: {redirect_uri}")
    print()

def show_clickup_config_instructions():
    """Mostrar instrucciones para configurar ClickUp"""
    print("🔧 INSTRUCCIONES PARA CORREGIR CLICKUP:")
    print("-" * 40)
    print("1. Ve a https://app.clickup.com/settings/apps")
    print("2. Busca tu aplicación 'ClickUp Project Manager v2'")
    print("3. Haz clic en el dropdown para expandir la configuración")
    print("4. En el campo 'Redireccionamiento de URL', cambia:")
    print("   ❌ clickuptaskmanager-production.up.railway.app")
    print("   ✅ https://clickuptaskmanager-production.up.railway.app/api/auth/callback")
    print("5. Haz clic en 'Guardar'")
    print()

def generate_oauth_url():
    """Generar URL de OAuth para probar"""
    client_id = "0J2LPSHXIM5PRB5VDE5CRJY7FJP86L0H"
    redirect_uri = "https://clickuptaskmanager-production.up.railway.app/api/auth/callback"
    
    auth_url = f"https://app.clickup.com/api/v2/oauth/authorize?" + urlencode({
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'read:user read:workspace read:task write:task'
    })
    
    print("🔗 URL DE PRUEBA OAUTH:")
    print("-" * 25)
    print(auth_url)
    print()
    
    return auth_url

def test_oauth_flow():
    """Probar el flujo de OAuth"""
    print("🧪 PROBANDO FLUJO OAUTH:")
    print("-" * 25)
    
    auth_url = generate_oauth_url()
    
    response = input("¿Abrir URL de prueba en el navegador? (s/n): ").lower()
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        try:
            webbrowser.open(auth_url)
            print("✅ URL abierta en el navegador")
            print()
            print("📝 INSTRUCCIONES DE PRUEBA:")
            print("1. Si ves un error 404, significa que ClickUp aún no está configurado correctamente")
            print("2. Si ves la página de autorización de ClickUp, ¡perfecto!")
            print("3. Autoriza la aplicación y verifica que te redirija correctamente")
        except Exception as e:
            print(f"❌ Error abriendo navegador: {e}")
            print("💡 Copia y pega la URL manualmente en tu navegador")

def show_troubleshooting():
    """Mostrar guía de solución de problemas"""
    print("🔍 SOLUCIÓN DE PROBLEMAS:")
    print("-" * 30)
    print("Si sigues viendo error 404 después de corregir la URL:")
    print("1. Verifica que guardaste los cambios en ClickUp")
    print("2. Espera 1-2 minutos para que los cambios se propaguen")
    print("3. Verifica que la URL sea exactamente:")
    print("   https://clickuptaskmanager-production.up.railway.app/api/auth/callback")
    print("4. Asegúrate de incluir 'https://' al inicio")
    print("5. Asegúrate de incluir '/api/auth/callback' al final")
    print()

def main():
    """Función principal"""
    print_banner()
    
    show_current_config()
    show_clickup_config_instructions()
    
    response = input("¿Has actualizado la configuración en ClickUp? (s/n): ").lower()
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        test_oauth_flow()
    else:
        print("⚠️  Primero actualiza la configuración en ClickUp y luego ejecuta este script nuevamente")
        print()
        show_clickup_config_instructions()
    
    show_troubleshooting()
    
    print("✅ Script completado!")
    print("🚀 ¡Tu OAuth debería funcionar correctamente ahora!")

if __name__ == "__main__":
    main()
