#!/usr/bin/env python3
"""
Arreglar Railway para usar main_simple.py
"""

import os
import shutil

def fix_railway_main():
    """Arreglar Railway para usar main_simple.py"""
    print("🛠️  ARREGLANDO RAILWAY PARA USAR MAIN_SIMPLE.PY")
    print("=" * 60)
    
    # 1. Verificar que main_simple.py existe
    if not os.path.exists('main_simple.py'):
        print("❌ main_simple.py no encontrado")
        return
    
    print("✅ main_simple.py encontrado")
    
    # 2. Crear main.py que importe main_simple
    print("2. Creando main.py que importe main_simple...")
    
    main_content = '''#!/usr/bin/env python3
"""
Main entry point for Railway - imports main_simple
"""

# Importar la aplicación desde main_simple
from main_simple import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
'''
    
    with open('main.py', 'w') as f:
        f.write(main_content)
    
    print("✅ main.py creado")
    
    # 3. Actualizar railway.json
    print("3. Actualizando railway.json...")
    
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
    
    import json
    with open('railway.json', 'w') as f:
        json.dump(railway_config, f, indent=2)
    
    print("✅ railway.json actualizado")
    
    # 4. Actualizar Procfile
    print("4. Actualizando Procfile...")
    
    with open('Procfile', 'w') as f:
        f.write("web: python main.py")
    
    print("✅ Procfile actualizado")
    
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
    
    # 6. Crear runtime.txt
    print("6. Creando runtime.txt...")
    
    with open('runtime.txt', 'w') as f:
        f.write("python-3.11")
    
    print("✅ runtime.txt creado")
    
    print(f"\n🎉 ¡Configuración completada!")
    print(f"   Archivos actualizados:")
    print(f"   - main.py (importa main_simple)")
    print(f"   - railway.json")
    print(f"   - Procfile")
    print(f"   - requirements.txt")
    print(f"   - runtime.txt")

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

def main():
    """Función principal"""
    print("🛠️  ARREGLAR RAILWAY PARA USAR MAIN_SIMPLE.PY")
    print("=" * 70)
    
    # Arreglar configuración
    fix_railway_main()
    
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

