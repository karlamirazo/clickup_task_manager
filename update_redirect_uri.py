#!/usr/bin/env python3
"""
Actualizar Redirect URI a 127.0.0.1
"""

import os

def update_env_file():
    """Actualizar archivo .env con 127.0.0.1"""
    print("🔧 ACTUALIZANDO REDIRECT URI A 127.0.0.1")
    print("=" * 50)
    
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print("❌ Archivo .env no encontrado")
        return False
    
    try:
        # Leer archivo .env
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar localhost por 127.0.0.1
        updated_content = content.replace(
            "CLICKUP_OAUTH_REDIRECT_URI=http://localhost:8000/api/auth/callback",
            "CLICKUP_OAUTH_REDIRECT_URI=http://127.0.0.1:8000/api/auth/callback"
        )
        
        # Escribir archivo actualizado
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ Archivo .env actualizado correctamente")
        print("   Redirect URI cambiado a: http://127.0.0.1:8000/api/auth/callback")
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando archivo: {e}")
        return False

def test_oauth_url():
    """Probar URL de OAuth con 127.0.0.1"""
    print("\n🧪 PROBANDO URL DE OAUTH CON 127.0.0.1")
    print("=" * 50)
    
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/api/auth/clickup", allow_redirects=False)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 307:
            redirect_url = response.headers.get('Location', '')
            print(f"✅ URL generada: {redirect_url}")
            
            if '127.0.0.1' in redirect_url:
                print("✅ ¡URL usa 127.0.0.1 correctamente!")
                return True
            else:
                print("❌ URL no usa 127.0.0.1")
                return False
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_clickup_instructions():
    """Mostrar instrucciones para ClickUp"""
    print("\n📋 CONFIGURAR CLICKUP CON 127.0.0.1")
    print("=" * 50)
    print("1. Ve a: https://app.clickup.com/settings/apps")
    print("2. Busca 'clickuptaskmanager'")
    print("3. Haz clic en 'Edit'")
    print("4. Cambia Redirect URI a:")
    print("   http://127.0.0.1:8000/api/auth/callback")
    print("5. Guarda los cambios")
    print()
    print("🔧 PERMISOS NECESARIOS:")
    print("   - read:user")
    print("   - read:workspace")
    print("   - read:task")
    print("   - write:task")

def main():
    """Función principal"""
    print("🎯 ACTUALIZANDO CONFIGURACIÓN PARA CLICKUP")
    print("=" * 60)
    
    # Actualizar archivo .env
    if update_env_file():
        # Probar URL de OAuth
        if test_oauth_url():
            print("\n🎉 ¡CONFIGURACIÓN ACTUALIZADA CORRECTAMENTE!")
            print("=" * 60)
            print("✅ Redirect URI cambiado a 127.0.0.1")
            print("✅ URL de OAuth funcionando")
            print()
            show_clickup_instructions()
        else:
            print("\n❌ Error probando URL de OAuth")
    else:
        print("\n❌ Error actualizando configuración")

if __name__ == "__main__":
    main()

