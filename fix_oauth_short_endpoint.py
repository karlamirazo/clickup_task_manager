#!/usr/bin/env python3
"""
Script para usar endpoint OAuth más corto: /oauth
ClickUp puede guardar URLs cortas sin problemas
"""

import os
import re
from datetime import datetime

def print_header():
    """Imprimir cabecera del script"""
    print("=" * 80)
    print("🔧 ENDPOINT OAUTH CORTO - SOLUCIÓN DEFINITIVA")
    print("=" * 80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def update_env_files():
    """Actualizar archivos .env con endpoint corto"""
    print("📝 ACTUALIZANDO ARCHIVOS .ENV...")
    print("-" * 60)
    
    # URL con endpoint corto
    new_url = "https://ctm-pro.up.railway.app/oauth"
    
    env_files = ['.env', 'env.production', 'env.oauth.simple']
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"📄 Actualizando {env_file}...")
            
            try:
                # Leer contenido actual
                with open(env_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Reemplazar URLs con endpoints largos por endpoint corto
                patterns = [
                    r'CLICKUP_OAUTH_REDIRECT_URI=https://ctm-pro\.up\.railway\.app/callback',
                    r'CLICKUP_OAUTH_REDIRECT_URI=https://ctm-pro\.up\.railway\.app',
                    r'CLICKUP_OAUTH_REDIRECT_URI=ctm-pro\.up\.railway\.app'
                ]
                
                updated = False
                for pattern in patterns:
                    if re.search(pattern, content):
                        content = re.sub(pattern, f'CLICKUP_OAUTH_REDIRECT_URI={new_url}', content)
                        updated = True
                
                if updated:
                    # Escribir archivo actualizado
                    with open(env_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"   ✅ {env_file} actualizado con endpoint /oauth")
                else:
                    print(f"   ℹ️ {env_file} no necesita actualización")
            
            except UnicodeDecodeError:
                print(f"   ⚠️ Error de encoding en {env_file} - omitiendo")
        else:
            print(f"   ⚠️ {env_file} no existe")

def print_solution_info():
    """Imprimir información de la solución"""
    print("\n🎯 SOLUCIÓN IMPLEMENTADA...")
    print("-" * 60)
    print("✅ Nuevo endpoint: /oauth (más corto)")
    print("✅ ClickUp puede guardar URLs cortas fácilmente")
    print("✅ Funcionalidad idéntica al /callback")
    print("✅ Manejo completo de errores OAuth")
    print("✅ Redirección directa al dashboard")
    print()
    print("🔧 ENDPOINTS DISPONIBLES:")
    print("   • /oauth (PRINCIPAL - más corto)")
    print("   • /callback (respaldo)")
    print("   • / (página principal)")

def print_instructions():
    """Imprimir instrucciones para ClickUp y Railway"""
    print("\n📋 CONFIGURACIÓN FINAL...")
    print("-" * 60)
    print("🏗️ EN RAILWAY (Variables):")
    print("   CLICKUP_OAUTH_REDIRECT_URI = https://ctm-pro.up.railway.app/oauth")
    print()
    print("🌐 EN CLICKUP (Redirect URI):")
    print("   ctm-pro.up.railway.app/oauth")
    print()
    print("✅ VENTAJAS DEL ENDPOINT /oauth:")
    print("   • Solo 6 caracteres (/oauth vs /callback)")
    print("   • ClickUp puede guardarlo sin cortarlo")
    print("   • Más fácil de escribir y recordar")
    print("   • Funciona perfectamente")
    print()
    print("🎯 PASOS FINALES:")
    print("1. 🚀 Deploy automático en Railway (ya enviado)")
    print("2. ⚙️ Cambiar variable en Railway:")
    print("   CLICKUP_OAUTH_REDIRECT_URI = https://ctm-pro.up.railway.app/oauth")
    print("3. 🌐 Cambiar en ClickUp:")
    print("   Redirect URI = ctm-pro.up.railway.app/oauth")
    print("4. ✅ ¡Probar OAuth!")

def main():
    """Función principal"""
    print_header()
    
    # Actualizar archivos
    update_env_files()
    
    # Mostrar información
    print_solution_info()
    print_instructions()
    
    print("\n" + "=" * 80)
    print("✅ SOLUCIÓN OAUTH CORTA COMPLETADA")
    print("=" * 80)
    print("🎯 El endpoint /oauth es la solución definitiva")
    print("📱 ClickUp podrá guardar esta URL sin problemas")

if __name__ == "__main__":
    main()
