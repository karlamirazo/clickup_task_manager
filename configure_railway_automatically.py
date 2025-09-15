#!/usr/bin/env python3
"""
Configurar Railway automáticamente
"""

import os
import json

def configure_railway_automatically():
    """Configurar Railway automáticamente"""
    print("🔧 CONFIGURANDO RAILWAY AUTOMÁTICAMENTE")
    print("=" * 60)
    
    # 1. Crear railway.json con configuración específica
    print("1. Creando railway.json con configuración específica...")
    
    railway_config = {
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "python main.py",
            "healthcheckPath": "/health",
            "healthcheckTimeout": 100,
            "restartPolicyType": "ON_FAILURE",
            "restartPolicyMaxRetries": 10
        }
    }
    
    with open('railway.json', 'w') as f:
        json.dump(railway_config, f, indent=2)
    
    print("✅ railway.json creado")
    
    # 2. Crear Procfile
    print("2. Creando Procfile...")
    
    with open('Procfile', 'w') as f:
        f.write("web: python main.py")
    
    print("✅ Procfile creado")
    
    # 3. Crear runtime.txt
    print("3. Creando runtime.txt...")
    
    with open('runtime.txt', 'w') as f:
        f.write("python-3.11")
    
    print("✅ runtime.txt creado")
    
    # 4. Verificar que main.py existe y funciona
    print("4. Verificando main.py...")
    
    if os.path.exists('main.py'):
        print("✅ main.py existe")
        
        # Verificar que importa correctamente
        try:
            import main
            print("✅ main.py importa correctamente")
        except Exception as e:
            print(f"❌ Error al importar main.py: {e}")
            return
    else:
        print("❌ main.py no encontrado")
        return
    
    # 5. Crear requirements.txt si no existe
    print("5. Verificando requirements.txt...")
    
    if not os.path.exists('requirements.txt'):
        requirements = """fastapi==0.104.1
uvicorn[standard]==0.24.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
aiohttp==3.9.1
sqlalchemy==2.0.23
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
"""
        
        with open('requirements.txt', 'w') as f:
            f.write(requirements)
        
        print("✅ requirements.txt creado")
    else:
        print("✅ requirements.txt ya existe")
    
    print(f"\n🎉 ¡Configuración completada!")
    print(f"   Archivos creados/actualizados:")
    print(f"   - railway.json")
    print(f"   - Procfile")
    print(f"   - runtime.txt")
    print(f"   - requirements.txt")
    print(f"   - main.py (verificado)")

def show_railway_instructions():
    """Mostrar instrucciones para Railway"""
    print(f"\n📋 INSTRUCCIONES PARA RAILWAY:")
    print("=" * 40)
    print("1. Ve a: https://railway.app/dashboard")
    print("2. Busca tu proyecto 'clickuptaskmanager'")
    print("3. Haz clic en el servicio")
    print("4. Ve a la pestaña 'Settings'")
    print("5. En 'Start Command', cambia a: python main.py")
    print("6. En 'Health Check Path', cambia a: /health")
    print("7. Ve a la pestaña 'Variables' y verifica que estén configuradas:")
    print("   - CLICKUP_OAUTH_CLIENT_ID")
    print("   - CLICKUP_OAUTH_CLIENT_SECRET")
    print("   - CLICKUP_OAUTH_REDIRECT_URI")
    print("   - JWT_SECRET_KEY")
    print("   - ALLOWED_ORIGINS")
    print("8. Ve a la pestaña 'Deployments' y haz clic en 'Redeploy'")
    print("9. Espera a que termine el deploy")
    print("10. Prueba: https://clickuptaskmanager-production.up.railway.app/api/auth/login")

def main():
    """Función principal"""
    print("🔧 CONFIGURAR RAILWAY AUTOMÁTICAMENTE")
    print("=" * 70)
    
    # Configurar Railway
    configure_railway_automatically()
    
    # Mostrar instrucciones
    show_railway_instructions()
    
    print(f"\n" + "=" * 70)
    print("📋 PRÓXIMOS PASOS:")
    print("1. Haz commit y push de los cambios")
    print("2. Configura Railway según las instrucciones")
    print("3. Redespliega la aplicación")
    print("4. Prueba OAuth en producción")

if __name__ == "__main__":
    main()

