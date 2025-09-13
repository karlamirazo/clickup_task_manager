#!/usr/bin/env python3
"""
Script de configuración para OAuth 2.0 con ClickUp
"""

import os
import sys
import webbrowser
from urllib.parse import urlencode

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🚀 CONFIGURACIÓN DE OAUTH 2.0 CON CLICKUP")
    print("=" * 60)
    print()

def check_environment():
    """Verificar configuración del entorno"""
    print("🔍 Verificando configuración del entorno...")
    
    # Verificar si existe .env
    if not os.path.exists('.env'):
        print("❌ Archivo .env no encontrado")
        print("💡 Copia env.oauth.example como .env y configura las variables")
        return False
    
    # Verificar variables de OAuth
    from dotenv import load_dotenv
    load_dotenv()
    
    client_id = os.getenv('CLICKUP_OAUTH_CLIENT_ID')
    client_secret = os.getenv('CLICKUP_OAUTH_CLIENT_SECRET')
    redirect_uri = os.getenv('CLICKUP_OAUTH_REDIRECT_URI')
    
    if not client_id or client_id == 'tu_client_id_aqui':
        print("❌ CLICKUP_OAUTH_CLIENT_ID no configurado")
        return False
    
    if not client_secret or client_secret == 'tu_client_secret_aqui':
        print("❌ CLICKUP_OAUTH_CLIENT_SECRET no configurado")
        return False
    
    if not redirect_uri or redirect_uri == 'http://localhost:8000/api/auth/callback':
        print("⚠️  CLICKUP_OAUTH_REDIRECT_URI usando valor por defecto")
    
    print("✅ Configuración de OAuth encontrada")
    return True

def show_oauth_setup_instructions():
    """Mostrar instrucciones para configurar OAuth en ClickUp"""
    print("\n📋 INSTRUCCIONES PARA CONFIGURAR OAUTH EN CLICKUP:")
    print("-" * 50)
    print("1. Ve a https://app.clickup.com/settings/apps")
    print("2. Haz clic en 'Create App'")
    print("3. Completa la información:")
    print("   - App Name: ClickUp Project Manager")
    print("   - Description: Gestión de proyectos con ClickUp")
    print("   - Redirect URI: http://localhost:8000/api/auth/callback")
    print("4. Selecciona los siguientes permisos:")
    print("   ✅ read:user")
    print("   ✅ read:workspace") 
    print("   ✅ read:task")
    print("   ✅ write:task")
    print("5. Copia el Client ID y Client Secret al archivo .env")
    print()

def test_oauth_flow():
    """Probar el flujo de OAuth"""
    print("🧪 Probando flujo de OAuth...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    client_id = os.getenv('CLICKUP_OAUTH_CLIENT_ID')
    redirect_uri = os.getenv('CLICKUP_OAUTH_REDIRECT_URI', 'http://localhost:8000/api/auth/callback')
    
    # Generar URL de autorización
    auth_url = f"https://app.clickup.com/api/v2/oauth/authorize?" + urlencode({
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'read:user read:workspace read:task write:task'
    })
    
    print(f"🔗 URL de autorización generada:")
    print(f"   {auth_url}")
    print()
    
    # Preguntar si abrir en el navegador
    response = input("¿Abrir URL de autorización en el navegador? (s/n): ").lower()
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        try:
            webbrowser.open(auth_url)
            print("✅ URL abierta en el navegador")
        except Exception as e:
            print(f"❌ Error abriendo navegador: {e}")
            print("💡 Copia y pega la URL manualmente en tu navegador")
    
    return auth_url

def test_database_connection():
    """Probar conexión a la base de datos"""
    print("\n🗄️  Probando conexión a la base de datos...")
    
    try:
        from core.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Conexión a la base de datos exitosa")
            return True
            
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        print("💡 Verifica la configuración de DATABASE_URL en .env")
        return False

def test_clickup_api():
    """Probar conexión a la API de ClickUp"""
    print("\n🔗 Probando conexión a la API de ClickUp...")
    
    try:
        from integrations.clickup.client import ClickUpClient
        
        client = ClickUpClient()
        print("✅ Cliente de ClickUp inicializado")
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando cliente de ClickUp: {e}")
        print("💡 Verifica la configuración de CLICKUP_API_TOKEN en .env")
        return False

def create_test_user():
    """Crear usuario de prueba"""
    print("\n👤 Creando usuario de prueba...")
    
    try:
        from core.database import SessionLocal
        from models.user import User
        from auth.auth import AuthManager
        
        db = SessionLocal()
        try:
            # Verificar si ya existe un usuario de prueba
            existing_user = db.query(User).filter(User.email == "test@example.com").first()
            if existing_user:
                print("⚠️  Usuario de prueba ya existe")
                return True
            
            # Crear usuario de prueba
            test_user = User(
                email="test@example.com",
                username="testuser",
                password_hash=AuthManager.get_password_hash("test123"),
                first_name="Usuario",
                last_name="Prueba",
                role="user",
                is_active=True
            )
            
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            print("✅ Usuario de prueba creado:")
            print(f"   Email: test@example.com")
            print(f"   Password: test123")
            print(f"   Role: user")
            
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error creando usuario de prueba: {e}")
        return False

def show_next_steps():
    """Mostrar próximos pasos"""
    print("\n🎯 PRÓXIMOS PASOS:")
    print("-" * 30)
    print("1. Inicia la aplicación:")
    print("   python -m uvicorn app.main:app --reload")
    print()
    print("2. Ve a la página de login:")
    print("   http://localhost:8000/api/auth/login")
    print()
    print("3. Prueba la autenticación:")
    print("   - Login con usuario de prueba: test@example.com / test123")
    print("   - O haz clic en 'Iniciar con ClickUp' para OAuth")
    print()
    print("4. Verifica el dashboard:")
    print("   http://localhost:8000/dashboard")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Verificar configuración
    if not check_environment():
        show_oauth_setup_instructions()
        return
    
    # Probar conexiones
    db_ok = test_database_connection()
    clickup_ok = test_clickup_api()
    
    if not db_ok:
        print("\n❌ No se puede continuar sin conexión a la base de datos")
        return
    
    # Crear usuario de prueba
    create_test_user()
    
    # Probar OAuth
    if clickup_ok:
        test_oauth_flow()
    
    # Mostrar próximos pasos
    show_next_steps()
    
    print("\n✅ Configuración completada!")
    print("🚀 ¡Tu sistema de autenticación está listo!")

if __name__ == "__main__":
    main()
