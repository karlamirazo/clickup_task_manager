#!/usr/bin/env python3
"""
Script de inicio rápido con OAuth ya configurado
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🚀 CLICKUP PROJECT MANAGER - OAUTH LISTO")
    print("=" * 60)
    print()

def setup_environment():
    """Configurar el entorno con las credenciales OAuth"""
    print("🔧 Configurando entorno con credenciales OAuth...")
    
    # Crear archivo .env si no existe
    if not os.path.exists('.env'):
        print("📝 Creando archivo .env con credenciales OAuth...")
        
        env_content = """# Configuración OAuth lista para usar
CLICKUP_OAUTH_CLIENT_ID=7US6KJX26FOROTI3ZSOZYCAXBCG7W386
CLICKUP_OAUTH_CLIENT_SECRET=H4M3AVO1L6OG7RDH8XMPUK756PB0X2R28E5KTIJBV8PDQNSORKRSAXI7ZGI5MCXC
CLICKUP_OAUTH_REDIRECT_URI=http://localhost:8000/api/auth/callback

# Base de datos
DATABASE_URL=postgresql://postgres:admin123@localhost:5432/clickup_project_manager

# Seguridad
JWT_SECRET_KEY=clickup-manager-jwt-secret-key-2025-super-secure
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Aplicación
ENVIRONMENT=development
PORT=8000
HOST=127.0.0.1

# ClickUp API
CLICKUP_API_TOKEN=pk_156221125_GI1OKEUEW57LFWA8RYWHGIC54TL6XVVZ
CLICKUP_WORKSPACE_ID=9014943317
CLICKUP_SPACE_ID=90143983983

# WhatsApp
WHATSAPP_ENABLED=True
WHATSAPP_EVOLUTION_URL=https://evolution-api-production-9d5d.up.railway.app
WHATSAPP_EVOLUTION_API_KEY=clickup-evolution-v223
WHATSAPP_INSTANCE_NAME=clickup-v23

# Otros
LOG_LEVEL=INFO
AUTOMATION_ENABLED=True
REPORTS_ENABLED=True
INTEGRATIONS_ENABLED=True
TASK_WHATSAPP_FIELDS=WhatsApp,Telefono,Phone
TASK_EMAIL_FIELDS=Email
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Archivo .env creado con credenciales OAuth")
    else:
        print("✅ Archivo .env ya existe")

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

def test_oauth_config():
    """Probar configuración OAuth"""
    print("\n🔐 Probando configuración OAuth...")
    
    try:
        from core.config import settings
        from auth.oauth import clickup_oauth
        
        # Verificar que las credenciales estén configuradas
        if settings.CLICKUP_OAUTH_CLIENT_ID and settings.CLICKUP_OAUTH_CLIENT_SECRET:
            print("✅ Credenciales OAuth configuradas")
            print(f"   Client ID: {settings.CLICKUP_OAUTH_CLIENT_ID[:10]}...")
            print(f"   Redirect URI: {settings.CLICKUP_OAUTH_REDIRECT_URI}")
            
            # Generar URL de autorización
            auth_url = clickup_oauth.get_authorization_url()
            if auth_url and 'clickup.com' in auth_url:
                print("✅ URL de autorización generada correctamente")
                return True
            else:
                print("❌ Error generando URL de autorización")
                return False
        else:
            print("❌ Credenciales OAuth no configuradas")
            return False
            
    except Exception as e:
        print(f"❌ Error probando OAuth: {e}")
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
        print("\n✨ ¡OAuth ya está configurado! Puedes autenticarte inmediatamente con ClickUp")
        print("\n⏹️  Presiona Ctrl+C para detener la aplicación")
        print("-" * 60)
        
        # Ejecutar la aplicación
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n⏹️  Aplicación detenida por el usuario")
    except Exception as e:
        print(f"\n❌ Error iniciando aplicación: {e}")

def show_quick_guide():
    """Mostrar guía rápida"""
    print("\n📋 GUÍA RÁPIDA:")
    print("-" * 30)
    print("1. La aplicación se iniciará en http://localhost:8000")
    print("2. Ve a http://localhost:8000/api/auth/login")
    print("3. Haz clic en 'Iniciar con ClickUp'")
    print("4. Completa la autorización en ClickUp")
    print("5. ¡Serás redirigido al dashboard!")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Configurar entorno
    setup_environment()
    
    # Verificar base de datos
    if not check_database():
        print("\n❌ No se puede conectar a la base de datos")
        print("💡 Configura PostgreSQL y ejecuta las migraciones")
        return
    
    # Probar configuración OAuth
    if not test_oauth_config():
        print("\n❌ Error en la configuración OAuth")
        return
    
    # Mostrar guía
    show_quick_guide()
    
    # Iniciar aplicación
    start_application()

if __name__ == "__main__":
    main()

