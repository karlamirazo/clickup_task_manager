#!/usr/bin/env python3
"""
Script para activar OAuth cuando tengas plan de pago de ClickUp
"""

import os
import re
from datetime import datetime

def print_header():
    """Imprimir cabecera del script"""
    print("=" * 80)
    print("🔧 ACTIVAR OAUTH CUANDO TENGAS PLAN DE PAGO")
    print("=" * 80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def enable_oauth_in_files():
    """Activar OAuth en archivos de configuración"""
    print("🔄 ACTIVANDO OAUTH EN ARCHIVOS...")
    print("-" * 60)
    
    env_files = ['.env', 'env.production']
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"📄 Actualizando {env_file}...")
            
            # Leer contenido actual
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Cambiar CLICKUP_OAUTH_ENABLED a True
            if 'CLICKUP_OAUTH_ENABLED=False' in content:
                content = content.replace('CLICKUP_OAUTH_ENABLED=False', 'CLICKUP_OAUTH_ENABLED=True')
                
                # Escribir archivo actualizado
                with open(env_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   ✅ {env_file} - OAuth activado")
            else:
                print(f"   ℹ️ {env_file} - OAuth ya estaba activado o no se encontró la configuración")
        else:
            print(f"   ⚠️ {env_file} no existe")

def print_instructions():
    """Imprimir instrucciones para después de activar"""
    print("\n📋 INSTRUCCIONES DESPUÉS DE ACTIVAR OAUTH...")
    print("-" * 60)
    print("1. ✅ Asegúrate de tener un plan de pago de ClickUp")
    print("2. 🔑 Ve a: https://app.clickup.com/settings/apps")
    print("3. 📱 Verifica que tu aplicación OAuth esté activa")
    print("4. 🚀 Haz commit y push de los cambios:")
    print("   git add .")
    print("   git commit -m 'Enable OAuth for paid ClickUp plan'")
    print("   git push origin master")
    print("5. 🎯 Prueba el OAuth en tu aplicación")
    print()
    print("💡 BENEFICIOS DEL OAUTH:")
    print("   • Autenticación segura multi-usuario")
    print("   • No necesidad de compartir API tokens")
    print("   • Gestión de permisos granular")
    print("   • Mejor experiencia de usuario")

def print_disable_instructions():
    """Imprimir instrucciones para deshabilitar OAuth"""
    print("\n🔧 PARA DESHABILITAR OAUTH NUEVAMENTE...")
    print("-" * 60)
    print("Si necesitas deshabilitar OAuth:")
    print("1. Cambia CLICKUP_OAUTH_ENABLED=True a CLICKUP_OAUTH_ENABLED=False")
    print("2. Haz commit y push")
    print("3. La aplicación volverá a usar API Token")

def main():
    """Función principal"""
    print_header()
    
    # Mostrar estado actual
    print("📊 ESTADO ACTUAL:")
    print("   • OAuth: DESHABILITADO (plan gratuito)")
    print("   • Autenticación: API Token personal")
    print("   • Listo para: Activar cuando tengas plan de pago")
    print()
    
    # Preguntar confirmación
    response = input("¿Quieres activar OAuth ahora? (solo si tienes plan de pago) [y/N]: ")
    
    if response.lower() in ['y', 'yes', 'sí', 'si']:
        print("\n🚀 Activando OAuth...")
        enable_oauth_in_files()
        print_instructions()
    else:
        print("\n💡 OAuth permanece deshabilitado.")
        print("Ejecuta este script cuando tengas plan de pago de ClickUp.")
    
    print_disable_instructions()
    
    print("\n" + "=" * 80)
    print("✅ SCRIPT COMPLETADO")
    print("=" * 80)

if __name__ == "__main__":
    main()

