#!/usr/bin/env python3
"""
Configurar OAuth con 127.0.0.1:8000 (sin ruta)
"""

import os
import requests

def update_config_simple():
    """Actualizar configuración para usar solo 127.0.0.1:8000"""
    print("🔧 ACTUALIZANDO CONFIGURACIÓN PARA CLICKUP")
    print("=" * 50)
    
    # URL simple que ClickUp acepta
    simple_redirect = "http://127.0.0.1:8000"
    
    try:
        # Actualizar archivo .env
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar la URL de redirect
        updated_content = content.replace(
            "CLICKUP_OAUTH_REDIRECT_URI=http://127.0.0.1:8000/api/auth/callback",
            f"CLICKUP_OAUTH_REDIRECT_URI={simple_redirect}"
        )
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ Archivo .env actualizado")
        print(f"   Redirect URI: {simple_redirect}")
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando .env: {e}")
        return False

def update_main_simple():
    """Actualizar main_simple.py para manejar redirect simple"""
    print("\n🔧 ACTUALIZANDO MAIN_SIMPLE.PY...")
    print("=" * 50)
    
    try:
        with open('main_simple.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar y reemplazar la configuración de redirect
        old_config = 'redirect_uri = os.getenv(\'CLICKUP_OAUTH_REDIRECT_URI\', \'http://localhost:8000/api/auth/callback\')'
        new_config = 'redirect_uri = os.getenv(\'CLICKUP_OAUTH_REDIRECT_URI\', \'http://127.0.0.1:8000\')'
        
        if old_config in content:
            updated_content = content.replace(old_config, new_config)
            
            with open('main_simple.py', 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print("✅ main_simple.py actualizado")
            return True
        else:
            print("⚠️  No se encontró la configuración a actualizar")
            return False
            
    except Exception as e:
        print(f"❌ Error actualizando main_simple.py: {e}")
        return False

def add_root_redirect():
    """Agregar endpoint de redirect en la raíz"""
    print("\n🔧 AGREGANDO ENDPOINT DE REDIRECT EN LA RAÍZ...")
    print("=" * 50)
    
    try:
        with open('main_simple.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar la sección de endpoints
        if '@app.get("/")' in content:
            # Reemplazar el endpoint raíz para manejar OAuth callback
            old_root = '''@app.get("/")
async def root():
    """Página principal - redirigir a login"""
    return RedirectResponse(url="/api/auth/login")'''
            
            new_root = '''@app.get("/")
async def root():
    """Página principal - manejar OAuth callback o redirigir a login"""
    return RedirectResponse(url="/api/auth/login")

@app.get("/callback")
async def oauth_callback(code: str = None, state: str = None, error: str = None):
    """Callback de OAuth desde ClickUp"""
    if error:
        return {"error": f"OAuth error: {error}"}
    
    if not code:
        return {"error": "No authorization code received"}
    
    # Redirigir al callback real con los parámetros
    callback_url = f"/api/auth/callback?code={code}&state={state}"
    return RedirectResponse(url=callback_url)'''
            
            if old_root in content:
                updated_content = content.replace(old_root, new_root)
                
                with open('main_simple.py', 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                print("✅ Endpoint de callback agregado en la raíz")
                return True
            else:
                print("⚠️  No se encontró el endpoint raíz a actualizar")
                return False
        else:
            print("⚠️  No se encontró el endpoint raíz")
            return False
            
    except Exception as e:
        print(f"❌ Error actualizando main_simple.py: {e}")
        return False

def test_configuration():
    """Probar la configuración"""
    print("\n🧪 PROBANDO CONFIGURACIÓN...")
    print("=" * 50)
    
    try:
        # Probar URL de OAuth
        response = requests.get("http://127.0.0.1:8000/api/auth/clickup", allow_redirects=False)
        
        if response.status_code == 307:
            redirect_url = response.headers.get('Location', '')
            print(f"✅ URL de OAuth generada: {redirect_url}")
            
            if '127.0.0.1:8000' in redirect_url:
                print("✅ URL usa 127.0.0.1:8000 correctamente")
                return True
            else:
                print("❌ URL no usa 127.0.0.1:8000")
                return False
        else:
            print(f"❌ Error en OAuth: {response.status_code}")
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
    print("🎯 CONFIGURANDO OAUTH SIMPLE PARA CLICKUP")
    print("=" * 60)
    
    # Actualizar configuración
    if not update_config_simple():
        print("❌ Error actualizando configuración")
        return
    
    # Actualizar main_simple.py
    if not update_main_simple():
        print("❌ Error actualizando main_simple.py")
        return
    
    # Agregar endpoint de callback
    if not add_root_redirect():
        print("❌ Error agregando endpoint de callback")
        return
    
    # Probar configuración
    if test_configuration():
        print("\n🎉 ¡CONFIGURACIÓN COMPLETA!")
        print("=" * 60)
        print("✅ Configuración actualizada")
        print("✅ Endpoint de callback agregado")
        print("✅ OAuth funcionando")
        print()
        show_clickup_instructions()
        print()
        print("📋 PRÓXIMOS PASOS:")
        print("1. Configura ClickUp con: http://127.0.0.1:8000")
        print("2. Inicia la aplicación: python main_simple.py")
        print("3. Prueba el OAuth")
    else:
        print("\n❌ Error en la configuración")

if __name__ == "__main__":
    main()
