#!/usr/bin/env python3
"""
Script para configurar OAuth de ClickUp automáticamente
"""

import os
import webbrowser
from urllib.parse import urlencode

def print_banner():
    """Mostrar banner del script"""
    print("🔧 CONFIGURADOR DE OAUTH CON CLICKUP")
    print("=" * 50)
    print()

def get_oauth_credentials():
    """Obtener credenciales de OAuth del usuario"""
    print("📋 INSTRUCCIONES:")
    print("1. Ve a https://app.clickup.com/settings/apps")
    print("2. Crea una nueva aplicación OAuth")
    print("3. Configura la URL de redirección: http://localhost:8000/api/auth/callback")
    print("4. Selecciona los permisos: read:user, read:workspace, read:task, write:task")
    print("5. Copia el Client ID y Client Secret")
    print()
    
    # Preguntar si abrir ClickUp
    response = input("¿Abrir ClickUp Apps en el navegador? (s/n): ").lower()
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        try:
            webbrowser.open("https://app.clickup.com/settings/apps")
            print("✅ ClickUp Apps abierto en el navegador")
        except Exception as e:
            print(f"❌ Error abriendo navegador: {e}")
    
    print()
    print("📝 Ingresa las credenciales de ClickUp:")
    
    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()
    
    return client_id, client_secret

def update_env_file(client_id, client_secret):
    """Actualizar archivo .env con las credenciales"""
    env_file = ".env"
    
    # Leer archivo actual
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ Archivo {env_file} no encontrado")
        return False
    
    # Actualizar líneas
    updated_lines = []
    for line in lines:
        if line.startswith('CLICKUP_OAUTH_CLIENT_ID='):
            updated_lines.append(f'CLICKUP_OAUTH_CLIENT_ID={client_id}\n')
        elif line.startswith('CLICKUP_OAUTH_CLIENT_SECRET='):
            updated_lines.append(f'CLICKUP_OAUTH_CLIENT_SECRET={client_secret}\n')
        else:
            updated_lines.append(line)
    
    # Escribir archivo actualizado
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        print(f"✅ Archivo {env_file} actualizado correctamente")
        return True
    except Exception as e:
        print(f"❌ Error actualizando archivo: {e}")
        return False

def test_oauth_configuration():
    """Probar configuración de OAuth"""
    print("\n🧪 Probando configuración de OAuth...")
    
    try:
        from core.config import settings
        
        client_id = getattr(settings, 'CLICKUP_OAUTH_CLIENT_ID', '')
        client_secret = getattr(settings, 'CLICKUP_OAUTH_CLIENT_SECRET', '')
        redirect_uri = getattr(settings, 'CLICKUP_OAUTH_REDIRECT_URI', '')
        
        if client_id and client_secret:
            print("✅ OAuth configurado correctamente")
            print(f"   Client ID: {client_id[:10]}...")
            print(f"   Redirect URI: {redirect_uri}")
            
            # Generar URL de autorización de prueba
            auth_url = f"https://app.clickup.com/api/v2/oauth/authorize?" + urlencode({
                'client_id': client_id,
                'redirect_uri': redirect_uri,
                'response_type': 'code',
                'scope': 'read:user read:workspace read:task write:task'
            })
            
            print(f"\n🔗 URL de autorización generada:")
            print(f"   {auth_url}")
            
            # Preguntar si probar OAuth
            response = input("\n¿Probar OAuth ahora? (s/n): ").lower()
            if response in ['s', 'si', 'sí', 'y', 'yes']:
                try:
                    webbrowser.open(auth_url)
                    print("✅ URL de autorización abierta en el navegador")
                except Exception as e:
                    print(f"❌ Error abriendo navegador: {e}")
            
            return True
        else:
            print("❌ OAuth no configurado completamente")
            return False
            
    except Exception as e:
        print(f"❌ Error probando configuración: {e}")
        return False

def show_next_steps():
    """Mostrar próximos pasos"""
    print("\n🎯 PRÓXIMOS PASOS:")
    print("-" * 30)
    print("1. Reinicia la aplicación para aplicar los cambios:")
    print("   Ctrl+C para detener, luego:")
    print("   python -m uvicorn app.main:app --reload")
    print()
    print("2. Ve a la página de login:")
    print("   http://localhost:8000/login")
    print()
    print("3. Haz clic en 'Iniciar con ClickUp' para probar OAuth")
    print()
    print("4. Si todo funciona, verás la página de callback")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Obtener credenciales
    client_id, client_secret = get_oauth_credentials()
    
    if not client_id or not client_secret:
        print("❌ Credenciales no proporcionadas")
        return False
    
    # Actualizar archivo .env
    if not update_env_file(client_id, client_secret):
        return False
    
    # Probar configuración
    if test_oauth_configuration():
        show_next_steps()
        print("✅ ¡Configuración de OAuth completada!")
        return True
    else:
        print("❌ Error en la configuración")
        return False

if __name__ == "__main__":
    main()
