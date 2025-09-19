#!/usr/bin/env python3
"""
Script para configurar OAuth con URL raíz (sin /callback)
ClickUp no guarda el /callback, así que usamos solo el dominio raíz
"""

import os
import re
from datetime import datetime

def print_header():
    """Imprimir cabecera del script"""
    print("=" * 80)
    print("🌐 CONFIGURACIÓN OAUTH CON URL RAÍZ")
    print("=" * 80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def update_env_files():
    """Actualizar archivos .env con URL raíz"""
    print("📝 ACTUALIZANDO ARCHIVOS .ENV...")
    print("-" * 60)
    
    # URL raíz (sin /callback)
    root_url = "https://ctm-pro.up.railway.app"
    
    env_files = ['.env', 'env.production', 'env.oauth.simple']
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"📄 Actualizando {env_file}...")
            
            # Leer contenido actual
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Reemplazar URLs con /callback por URL raíz
            patterns = [
                r'CLICKUP_OAUTH_REDIRECT_URI=https://ctm-pro\.up\.railway\.app/callback',
                r'CLICKUP_OAUTH_REDIRECT_URI=https://ctm-pro\.up\.railway\.app'
            ]
            
            updated = False
            for pattern in patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, f'CLICKUP_OAUTH_REDIRECT_URI={root_url}', content)
                    updated = True
            
            if updated:
                # Escribir archivo actualizado
                with open(env_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   ✅ {env_file} actualizado con URL raíz")
            else:
                print(f"   ℹ️ {env_file} no necesita actualización")
        else:
            print(f"   ⚠️ {env_file} no existe")

def print_solution_info():
    """Imprimir información de la solución"""
    print("\n🎯 SOLUCIÓN IMPLEMENTADA...")
    print("-" * 60)
    print("✅ Endpoint raíz (/) ahora maneja OAuth callback")
    print("✅ URL simplificada: https://ctm-pro.up.railway.app")
    print("✅ ClickUp puede guardar esta URL sin problemas")
    print("✅ Funciona tanto como página principal como callback OAuth")
    print()
    print("🔧 FUNCIONAMIENTO:")
    print("   • Si vienen parámetros OAuth (code, state) → Maneja callback")
    print("   • Si no vienen parámetros → Redirige a login")
    print("   • Mantiene compatibilidad con /callback también")

def print_instructions():
    """Imprimir instrucciones para ClickUp"""
    print("\n📋 INSTRUCCIONES PARA CLICKUP...")
    print("-" * 60)
    print("🌐 Usa esta URL SIMPLE en ClickUp:")
    print()
    print("🔗 URL PARA CLICKUP (SIN /callback):")
    print("   📍 https://ctm-pro.up.railway.app")
    print()
    print("✅ VENTAJAS:")
    print("   • ClickUp la guarda sin problemas")
    print("   • No se corta ni divide")
    print("   • Funciona igual de bien")
    print("   • Más simple y elegante")
    print()
    print("🎯 PASOS EN CLICKUP:")
    print("1. Ve a: https://app.clickup.com/settings/apps")
    print("2. Busca 'ClickUp Project Manager v2'")
    print("3. Edita la aplicación")
    print("4. En 'Redirect URI', pon SOLO:")
    print("   https://ctm-pro.up.railway.app")
    print("5. NO agregues /callback al final")
    print("6. Guarda los cambios")

def main():
    """Función principal"""
    print_header()
    
    # Actualizar archivos
    update_env_files()
    
    # Mostrar información
    print_solution_info()
    print_instructions()
    
    print("\n" + "=" * 80)
    print("✅ CONFIGURACIÓN OAUTH RAÍZ COMPLETADA")
    print("=" * 80)
    print("🚀 Haz commit, push y usa SOLO el dominio raíz en ClickUp")
    print("📱 Ahora ClickUp debería guardar la URL sin problemas")

if __name__ == "__main__":
    main()
