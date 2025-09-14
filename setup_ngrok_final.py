#!/usr/bin/env python3
"""
Configurar OAuth con ngrok HTTPS para ClickUp
"""

import os
import subprocess
import time
import requests
import webbrowser
import json

def check_ngrok():
    """Verificar si ngrok está instalado"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok está instalado")
            return True
        else:
            print("❌ ngrok no está instalado")
            return False
    except FileNotFoundError:
        print("❌ ngrok no está instalado")
        return False

def install_ngrok_instructions():
    """Mostrar instrucciones para instalar ngrok"""
    print("📥 INSTALAR NGROK")
    print("=" * 50)
    print("1. Ve a: https://ngrok.com/download")
    print("2. Descarga ngrok para Windows")
    print("3. Extrae ngrok.exe a esta carpeta del proyecto")
    print("4. O agrega ngrok al PATH de Windows")
    print()
    print("🔑 CONFIGURAR NGROK:")
    print("1. Crea cuenta en: https://ngrok.com/signup")
    print("2. Obtén tu authtoken en: https://dashboard.ngrok.com/get-started/your-authtoken")
    print("3. Ejecuta: ngrok config add-authtoken TU_TOKEN")
    print()
    
    input("Presiona Enter cuando hayas instalado ngrok...")

def start_ngrok():
    """Iniciar ngrok en puerto 8000"""
    print("🚀 INICIANDO NGROK...")
    print("=" * 50)
    
    try:
        # Iniciar ngrok en background
        process = subprocess.Popen(['ngrok', 'http', '8000'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Esperar un poco para que ngrok se inicie
        time.sleep(5)
        
        # Obtener la URL pública
        try:
            response = requests.get('http://localhost:4040/api/tunnels')
            if response.status_code == 200:
                data = response.json()
                tunnels = data.get('tunnels', [])
                if tunnels:
                    # Buscar túnel HTTPS
                    https_tunnel = None
                    for tunnel in tunnels:
                        if tunnel.get('proto') == 'https':
                            https_tunnel = tunnel
                            break
                    
                    if https_tunnel:
                        public_url = https_tunnel['public_url']
                        print(f"✅ ngrok iniciado correctamente")
                        print(f"🌐 URL HTTPS: {public_url}")
                        return public_url, process
                    else:
                        print("❌ No se encontró túnel HTTPS")
                        return None, process
                else:
                    print("❌ No se encontraron túneles")
                    return None, process
            else:
                print("❌ Error obteniendo URL de ngrok")
                return None, process
        except Exception as e:
            print(f"❌ Error: {e}")
            return None, process
            
    except Exception as e:
        print(f"❌ Error iniciando ngrok: {e}")
        return None, None

def update_config_with_ngrok(ngrok_url):
    """Actualizar configuración con URL de ngrok"""
    print("🔧 ACTUALIZANDO CONFIGURACIÓN CON NGROK...")
    print("=" * 50)
    
    # URL completa del callback
    callback_url = f"{ngrok_url}/api/auth/callback"
    
    print(f"📝 URL de callback: {callback_url}")
    
    # Actualizar archivo .env
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar la URL de redirect
        updated_content = content.replace(
            "CLICKUP_OAUTH_REDIRECT_URI=http://127.0.0.1:8000",
            f"CLICKUP_OAUTH_REDIRECT_URI={callback_url}"
        )
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ Archivo .env actualizado")
        return callback_url
        
    except Exception as e:
        print(f"❌ Error actualizando .env: {e}")
        return None

def show_clickup_instructions(ngrok_url):
    """Mostrar instrucciones para ClickUp"""
    print("\n📋 CONFIGURAR CLICKUP CON NGROK")
    print("=" * 50)
    print("1. Ve a: https://app.clickup.com/settings/apps")
    print("2. Busca 'clickuptaskmanager'")
    print("3. Haz clic en 'Edit'")
    print("4. Cambia Redirect URI a:")
    print(f"   {ngrok_url}/api/auth/callback")
    print("5. Guarda los cambios")
    print()
    print("🔧 PERMISOS NECESARIOS:")
    print("   - read:user")
    print("   - read:workspace")
    print("   - read:task")
    print("   - write:task")
    print()
    print("⚠️  IMPORTANTE:")
    print("   - Mantén ngrok ejecutándose mientras uses la app")
    print("   - La URL de ngrok cambia cada vez que lo reinicias")
    print("   - Para producción, usa un dominio fijo")

def test_oauth_with_ngrok(ngrok_url):
    """Probar OAuth con ngrok"""
    print("\n🧪 PROBANDO OAUTH CON NGROK...")
    print("=" * 50)
    
    try:
        # Probar URL de login
        login_url = f"{ngrok_url}/api/auth/login"
        response = requests.get(login_url)
        
        if response.status_code == 200:
            print("✅ Página de login accesible")
            
            # Probar URL de OAuth
            oauth_url = f"{ngrok_url}/api/auth/clickup"
            oauth_response = requests.get(oauth_url, allow_redirects=False)
            
            if oauth_response.status_code == 307:
                redirect_url = oauth_response.headers.get('Location', '')
                print("✅ URL de OAuth funcionando")
                print(f"📊 Redirect URL: {redirect_url}")
                
                if ngrok_url.replace('https://', '') in redirect_url:
                    print("✅ URL de ngrok incluida correctamente")
                    return True
                else:
                    print("❌ URL de ngrok no incluida")
                    return False
            else:
                print(f"❌ Error en OAuth: {oauth_response.status_code}")
                return False
        else:
            print(f"❌ Error en login: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("🎯 CONFIGURANDO OAUTH CON NGROK HTTPS PARA CLICKUP")
    print("=" * 60)
    
    # Verificar si ngrok está instalado
    if not check_ngrok():
        install_ngrok_instructions()
        if not check_ngrok():
            print("❌ ngrok no está instalado. Instálalo primero.")
            return
    
    # Iniciar ngrok
    ngrok_url, ngrok_process = start_ngrok()
    if not ngrok_url:
        print("❌ No se pudo iniciar ngrok")
        return
    
    # Actualizar configuración
    callback_url = update_config_with_ngrok(ngrok_url)
    if not callback_url:
        print("❌ No se pudo actualizar configuración")
        return
    
    # Mostrar instrucciones
    show_clickup_instructions(ngrok_url)
    
    # Probar OAuth
    if test_oauth_with_ngrok(ngrok_url):
        print("\n🎉 ¡CONFIGURACIÓN COMPLETA!")
        print("=" * 60)
        print("✅ ngrok ejecutándose")
        print("✅ Configuración actualizada")
        print("✅ OAuth funcionando")
        print()
        print("📋 PRÓXIMOS PASOS:")
        print("1. Configura ClickUp con la URL de ngrok")
        print("2. Inicia tu aplicación: python main_simple.py")
        print("3. Ve a la URL de ngrok para probar")
        print()
        print("⚠️  MANTÉN NGROK EJECUTÁNDOSE")
        print("   Presiona Ctrl+C para detener ngrok")
        
        try:
            # Mantener ngrok ejecutándose
            ngrok_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo ngrok...")
            ngrok_process.terminate()
    else:
        print("\n❌ Error en la configuración")

if __name__ == "__main__":
    main()
