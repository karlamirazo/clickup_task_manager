#!/usr/bin/env python3
"""
Script de diagnóstico para OAuth
"""

import os
import sys

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE CONFIGURACIÓN OAUTH")
    print("=" * 60)
    print()

def check_env_file():
    """Verificar archivo .env"""
    print("📁 Verificando archivo .env...")
    
    if os.path.exists('.env'):
        print("✅ Archivo .env encontrado")
        
        # Leer archivo .env
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar variables OAuth
        if 'CLICKUP_OAUTH_CLIENT_ID' in content:
            print("✅ CLICKUP_OAUTH_CLIENT_ID encontrado en .env")
        else:
            print("❌ CLICKUP_OAUTH_CLIENT_ID no encontrado en .env")
        
        if 'CLICKUP_OAUTH_CLIENT_SECRET' in content:
            print("✅ CLICKUP_OAUTH_CLIENT_SECRET encontrado en .env")
        else:
            print("❌ CLICKUP_OAUTH_CLIENT_SECRET no encontrado en .env")
        
        if 'CLICKUP_OAUTH_REDIRECT_URI' in content:
            print("✅ CLICKUP_OAUTH_REDIRECT_URI encontrado en .env")
        else:
            print("❌ CLICKUP_OAUTH_REDIRECT_URI no encontrado en .env")
        
        return True
    else:
        print("❌ Archivo .env no encontrado")
        return False

def check_environment_variables():
    """Verificar variables de entorno"""
    print("\n🌍 Verificando variables de entorno...")
    
    # Cargar dotenv
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ dotenv cargado correctamente")
    except ImportError:
        print("❌ dotenv no instalado")
        return False
    
    # Verificar variables
    client_id = os.getenv('CLICKUP_OAUTH_CLIENT_ID')
    client_secret = os.getenv('CLICKUP_OAUTH_CLIENT_SECRET')
    redirect_uri = os.getenv('CLICKUP_OAUTH_REDIRECT_URI')
    
    print(f"   CLICKUP_OAUTH_CLIENT_ID: {client_id}")
    print(f"   CLICKUP_OAUTH_CLIENT_SECRET: {client_secret[:10] if client_secret else 'None'}...")
    print(f"   CLICKUP_OAUTH_REDIRECT_URI: {redirect_uri}")
    
    if client_id and client_secret and redirect_uri:
        print("✅ Todas las variables OAuth están configuradas")
        return True
    else:
        print("❌ Faltan variables OAuth")
        return False

def check_settings():
    """Verificar configuración de settings"""
    print("\n⚙️  Verificando configuración de settings...")
    
    try:
        from core.config import settings
        
        print(f"   settings.CLICKUP_OAUTH_CLIENT_ID: {settings.CLICKUP_OAUTH_CLIENT_ID}")
        print(f"   settings.CLICKUP_OAUTH_CLIENT_SECRET: {settings.CLICKUP_OAUTH_CLIENT_SECRET[:10] if settings.CLICKUP_OAUTH_CLIENT_SECRET else 'None'}...")
        print(f"   settings.CLICKUP_OAUTH_REDIRECT_URI: {settings.CLICKUP_OAUTH_REDIRECT_URI}")
        
        if settings.CLICKUP_OAUTH_CLIENT_ID and settings.CLICKUP_OAUTH_CLIENT_SECRET and settings.CLICKUP_OAUTH_REDIRECT_URI:
            print("✅ Settings OAuth configurados correctamente")
            return True
        else:
            print("❌ Settings OAuth no configurados")
            return False
            
    except Exception as e:
        print(f"❌ Error cargando settings: {e}")
        return False

def check_oauth_class():
    """Verificar clase OAuth"""
    print("\n🔐 Verificando clase OAuth...")
    
    try:
        from auth.oauth import clickup_oauth
        
        print(f"   clickup_oauth.client_id: {clickup_oauth.client_id}")
        print(f"   clickup_oauth.client_secret: {clickup_oauth.client_secret[:10] if clickup_oauth.client_secret else 'None'}...")
        print(f"   clickup_oauth.redirect_uri: {clickup_oauth.redirect_uri}")
        
        if clickup_oauth.client_id and clickup_oauth.client_secret and clickup_oauth.redirect_uri:
            print("✅ Clase OAuth configurada correctamente")
            return True
        else:
            print("❌ Clase OAuth no configurada")
            return False
            
    except Exception as e:
        print(f"❌ Error cargando clase OAuth: {e}")
        return False

def test_oauth_url():
    """Probar generación de URL OAuth"""
    print("\n🔗 Probando generación de URL OAuth...")
    
    try:
        from auth.oauth import clickup_oauth
        
        auth_url = clickup_oauth.get_authorization_url()
        print(f"   URL generada: {auth_url[:100]}...")
        
        if auth_url and 'clickup.com' in auth_url:
            print("✅ URL OAuth generada correctamente")
            return True
        else:
            print("❌ Error generando URL OAuth")
            return False
            
    except Exception as e:
        print(f"❌ Error generando URL OAuth: {e}")
        return False

def create_fixed_env():
    """Crear archivo .env corregido"""
    print("\n🔧 Creando archivo .env corregido...")
    
    env_content = """# Configuración OAuth corregida
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
    
    print("✅ Archivo .env creado/actualizado")

def main():
    """Función principal"""
    print_banner()
    
    # Verificar archivo .env
    env_ok = check_env_file()
    
    # Verificar variables de entorno
    env_vars_ok = check_environment_variables()
    
    # Verificar settings
    settings_ok = check_settings()
    
    # Verificar clase OAuth
    oauth_ok = check_oauth_class()
    
    # Probar URL OAuth
    url_ok = test_oauth_url()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL DIAGNÓSTICO:")
    print("=" * 60)
    print(f"   Archivo .env: {'✅' if env_ok else '❌'}")
    print(f"   Variables de entorno: {'✅' if env_vars_ok else '❌'}")
    print(f"   Settings: {'✅' if settings_ok else '❌'}")
    print(f"   Clase OAuth: {'✅' if oauth_ok else '❌'}")
    print(f"   URL OAuth: {'✅' if url_ok else '❌'}")
    
    if not all([env_ok, env_vars_ok, settings_ok, oauth_ok, url_ok]):
        print("\n🔧 SOLUCIONANDO PROBLEMAS...")
        create_fixed_env()
        print("\n✅ Archivo .env corregido. Ejecuta el script nuevamente para verificar.")
    else:
        print("\n🎉 ¡Todo está configurado correctamente!")

if __name__ == "__main__":
    main()

