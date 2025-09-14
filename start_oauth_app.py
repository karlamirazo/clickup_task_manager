#!/usr/bin/env python3
"""
Script de inicio rápido para la aplicación con OAuth
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🚀 INICIAR APLICACIÓN CON OAUTH")
    print("=" * 60)
    print()

def check_requirements():
    """Verificar requisitos"""
    print("🔍 Verificando requisitos...")
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Verificar archivo .env
    if not os.path.exists('.env'):
        print("⚠️  Archivo .env no encontrado")
        print("💡 Copiando archivo de ejemplo...")
        
        if os.path.exists('env.oauth.local.example'):
            import shutil
            shutil.copy('env.oauth.local.example', '.env')
            print("✅ Archivo .env creado desde ejemplo")
            print("📝 Configura las variables de OAuth en .env")
        else:
            print("❌ Archivo de ejemplo no encontrado")
            return False
    else:
        print("✅ Archivo .env encontrado")
    
    return True

def check_database():
    """Verificar base de datos"""
    print("\n🗄️  Verificando base de datos...")
    
    try:
        from core.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Conexión a la base de datos exitosa")
            return True
            
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        print("💡 Asegúrate de que PostgreSQL esté ejecutándose")
        return False

def start_application():
    """Iniciar la aplicación"""
    print("\n🚀 Iniciando aplicación...")
    
    try:
        # Comando para iniciar la aplicación
        cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
        
        print("📡 Ejecutando:", " ".join(cmd))
        print("🌐 La aplicación estará disponible en: http://localhost:8000")
        print("🔐 Página de autenticación: http://localhost:8000/api/auth/login")
        print("\n⏹️  Presiona Ctrl+C para detener la aplicación")
        print("-" * 60)
        
        # Ejecutar la aplicación
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n⏹️  Aplicación detenida por el usuario")
    except Exception as e:
        print(f"\n❌ Error iniciando aplicación: {e}")

def show_quick_setup():
    """Mostrar configuración rápida"""
    print("\n⚡ CONFIGURACIÓN RÁPIDA:")
    print("-" * 30)
    print("1. Configura OAuth en ClickUp:")
    print("   - Ve a https://app.clickup.com/settings/apps")
    print("   - Crea una nueva aplicación")
    print("   - URL de redirección: http://localhost:8000/api/auth/callback")
    print()
    print("2. Edita el archivo .env:")
    print("   - CLICKUP_OAUTH_CLIENT_ID=tu_client_id")
    print("   - CLICKUP_OAUTH_CLIENT_SECRET=tu_client_secret")
    print()
    print("3. Reinicia la aplicación")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Verificar requisitos
    if not check_requirements():
        print("\n❌ No se pueden cumplir los requisitos")
        return
    
    # Verificar base de datos
    if not check_database():
        print("\n❌ No se puede conectar a la base de datos")
        print("💡 Configura PostgreSQL y ejecuta las migraciones")
        return
    
    # Mostrar configuración rápida si es necesario
    from dotenv import load_dotenv
    load_dotenv()
    
    client_id = os.getenv('CLICKUP_OAUTH_CLIENT_ID', '')
    if not client_id or client_id == 'tu_client_id_aqui':
        show_quick_setup()
        
        response = input("\n¿Continuar sin configuración OAuth? (s/n): ").lower()
        if response not in ['s', 'si', 'sí', 'y', 'yes']:
            print("👋 Configura OAuth y vuelve a ejecutar el script")
            return
    
    # Iniciar aplicación
    start_application()

if __name__ == "__main__":
    main()
