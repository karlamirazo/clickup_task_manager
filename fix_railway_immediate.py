#!/usr/bin/env python3
"""
Solución inmediata para Railway - Reemplazar main.py completamente
"""

import os
import shutil

def fix_railway_immediate():
    """Solución inmediata para Railway"""
    print("🚨 SOLUCIÓN INMEDIATA PARA RAILWAY")
    print("=" * 50)
    
    # 1. Hacer backup del main.py actual
    if os.path.exists('main.py'):
        shutil.copy('main.py', 'main_backup.py')
        print("✅ Backup de main.py creado")
    
    # 2. Reemplazar main.py con el contenido de main_simple.py
    print("2. Reemplazando main.py con main_simple.py...")
    
    if os.path.exists('main_simple.py'):
        shutil.copy('main_simple.py', 'main.py')
        print("✅ main.py reemplazado con main_simple.py")
    else:
        print("❌ main_simple.py no encontrado")
        return
    
    # 3. Verificar que main.py funciona
    print("3. Verificando que main.py funciona...")
    
    try:
        # Importar para verificar que no hay errores
        import main
        print("✅ main.py importa correctamente")
    except Exception as e:
        print(f"❌ Error al importar main.py: {e}")
        return
    
    # 4. Actualizar railway.json para usar main.py
    print("4. Actualizando railway.json...")
    
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
    
    # 5. Actualizar Procfile
    print("5. Actualizando Procfile...")
    
    with open('Procfile', 'w') as f:
        f.write("web: python main.py")
    
    print("✅ Procfile actualizado")
    
    print(f"\n🎉 ¡Solución aplicada!")
    print(f"   - main.py ahora es una copia de main_simple.py")
    print(f"   - railway.json configurado para usar main.py")
    print(f"   - Procfile actualizado")

def show_next_steps():
    """Mostrar próximos pasos"""
    print(f"\n📋 PRÓXIMOS PASOS:")
    print("=" * 30)
    print("1. Haz commit y push de los cambios")
    print("2. Ve a Railway y verifica que esté usando main.py")
    print("3. Redespliega la aplicación")
    print("4. Prueba OAuth en producción")

def main():
    """Función principal"""
    print("🚨 SOLUCIÓN INMEDIATA PARA RAILWAY")
    print("=" * 70)
    
    # Aplicar solución
    fix_railway_immediate()
    
    # Mostrar próximos pasos
    show_next_steps()
    
    print(f"\n" + "=" * 70)
    print("🎯 ESTO DEBERÍA ARREGLAR EL PROBLEMA INMEDIATAMENTE")

if __name__ == "__main__":
    main()
