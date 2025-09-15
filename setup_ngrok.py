#!/usr/bin/env python3
"""
Configurar ngrok para OAuth con ClickUp
"""

import subprocess
import time
import requests
import webbrowser

def print_banner():
    """Mostrar banner"""
    print("=" * 60)
    print("🌐 CONFIGURADOR DE NGROK PARA OAUTH")
    print("=" * 60)
    print()

def check_ngrok_installed():
    """Verificar si ngrok está instalado"""
    print("1️⃣ VERIFICANDO NGROK...")
    
    try:
        result = subprocess.run(["ngrok", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ ngrok está instalado")
            print(f"   📋 Versión: {result.stdout.strip()}")
            return True
        else:
            print("   ❌ ngrok no está instalado")
            return False
    except FileNotFoundError:
        print("   ❌ ngrok no está instalado")
        return False

def install_ngrok_instructions():
    """Mostrar instrucciones para instalar ngrok"""
    print("\n📥 INSTRUCCIONES PARA INSTALAR NGROK:")
    print("=" * 50)
    print("1. Ve a: https://ngrok.com/download")
    print("2. Descarga ngrok para Windows")
    print("3. Extrae el archivo ngrok.exe")
    print("4. Colócalo en una carpeta (ej: C:\\ngrok\\)")
    print("5. Agrega esa carpeta al PATH de Windows")
    print("6. O copia ngrok.exe a la carpeta del proyecto")
    print()
    print("🔑 DESPUÉS DE INSTALAR:")
    print("1. Crea una cuenta gratuita en ngrok.com")
    print("2. Obtén tu authtoken")
    print("3. Ejecuta: ngrok config add-authtoken TU_TOKEN")
    print()

def start_ngrok_tunnel():
    """Iniciar túnel de ngrok"""
    print("\n2️⃣ INICIANDO TÚNEL NGROK...")
    
    try:
        # Iniciar ngrok en segundo plano
        process = subprocess.Popen(
            ["ngrok", "http", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("   ⏳ Esperando que ngrok se inicie...")
        time.sleep(3)
        
        # Obtener la URL pública
        try:
            response = requests.get("http://localhost:4040/api/tunnels")
            if response.status_code == 200:
                data = response.json()
                tunnels = data.get("tunnels", [])
                
                if tunnels:
                    public_url = tunnels[0]["public_url"]
                    print(f"   ✅ Túnel creado: {public_url}")
                    return public_url, process
                else:
                    print("   ❌ No se pudo obtener la URL del túnel")
                    return None, process
            else:
                print("   ❌ No se pudo conectar a ngrok")
                return None, process
        except Exception as e:
            print(f"   ❌ Error obteniendo URL: {e}")
            return None, process
            
    except Exception as e:
        print(f"   ❌ Error iniciando ngrok: {e}")
        return None, None

def show_clickup_config_instructions(public_url):
    """Mostrar instrucciones para configurar ClickUp"""
    print("\n3️⃣ CONFIGURAR CLICKUP CON NGROK:")
    print("=" * 50)
    print("1. Ve a: https://app.clickup.com/settings/apps")
    print("2. Busca tu aplicación 'clickuptaskmanager'")
    print("3. Haz clic en 'Edit' o 'Configurar'")
    print("4. En 'Redireccionamiento de URL', cambia a:")
    print(f"   {public_url}/api/auth/callback")
    print("5. Guarda los cambios")
    print()
    print("🔧 PERMISOS NECESARIOS:")
    print("   - read:user")
    print("   - read:workspace")
    print("   - read:task")
    print("   - write:task")
    print()

def test_oauth_with_ngrok(public_url):
    """Probar OAuth con ngrok"""
    print("\n4️⃣ PROBAR OAUTH CON NGROK:")
    print("=" * 50)
    print("1. Ve a: http://localhost:8000/api/auth/login")
    print("2. Haz clic en 'Iniciar con ClickUp'")
    print("3. ClickUp te redirigirá a ngrok")
    print("4. ngrok te redirigirá a tu aplicación local")
    print("5. ¡Serás redirigido al dashboard!")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Verificar ngrok
    if not check_ngrok_installed():
        install_ngrok_instructions()
        return
    
    # Iniciar túnel
    public_url, process = start_ngrok_tunnel()
    
    if public_url:
        # Mostrar instrucciones
        show_clickup_config_instructions(public_url)
        test_oauth_with_ngrok(public_url)
        
        print("\n" + "=" * 60)
        print("🎉 ¡CONFIGURACIÓN COMPLETA!")
        print("=" * 60)
        print(f"🌐 URL Pública: {public_url}")
        print(f"🔗 Redirect URI: {public_url}/api/auth/callback")
        print()
        print("⚠️  IMPORTANTE:")
        print("   - Mantén ngrok ejecutándose")
        print("   - No cierres esta ventana")
        print("   - Configura ClickUp con la URL de arriba")
        print()
        print("🛑 Para detener ngrok: Ctrl+C")
        
        try:
            # Mantener ngrok ejecutándose
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo ngrok...")
            process.terminate()
    else:
        print("\n❌ No se pudo crear el túnel de ngrok")
        print("💡 Verifica que ngrok esté instalado y configurado correctamente")

if __name__ == "__main__":
    main()

