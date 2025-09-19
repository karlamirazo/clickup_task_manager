#!/usr/bin/env python3
"""
Script para corregir la URL de OAuth con una versión más corta
que ClickUp pueda aceptar sin problemas
"""

import os
import re
from datetime import datetime

def print_header():
    """Imprimir cabecera del script"""
    print("=" * 70)
    print("🔧 CORRECTOR DE URL OAUTH CORTA")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def update_env_files():
    """Actualizar archivos .env con la URL más corta"""
    print("📝 ACTUALIZANDO ARCHIVOS .ENV...")
    print("-" * 50)
    
    # URL más corta que ClickUp puede manejar
    new_url = "https://clickuptaskmanager-production.up.railway.app/callback"
    
    env_files = ['.env', 'env.production', 'env.oauth.simple']
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"📄 Actualizando {env_file}...")
            
            # Leer contenido actual
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Reemplazar URL larga por URL corta
            old_patterns = [
                r'CLICKUP_OAUTH_REDIRECT_URI=https://clickuptaskmanager-production\.up\.railway\.app/api/auth/callback',
                r'CLICKUP_OAUTH_REDIRECT_URI=https://clickuptaskmanager-production\.up\.railway\.app'
            ]
            
            updated = False
            for pattern in old_patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, f'CLICKUP_OAUTH_REDIRECT_URI={new_url}', content)
                    updated = True
            
            if updated:
                # Escribir archivo actualizado
                with open(env_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   ✅ {env_file} actualizado con URL corta")
            else:
                print(f"   ℹ️ {env_file} no necesita actualización")
        else:
            print(f"   ⚠️ {env_file} no existe")

def print_instructions():
    """Imprimir instrucciones para ClickUp"""
    print("\n📋 INSTRUCCIONES PARA CLICKUP...")
    print("-" * 50)
    print("🌐 Ahora usa esta URL MÁS CORTA en ClickUp:")
    print()
    print("🔗 URL CORTA PARA CLICKUP:")
    print("   📍 https://clickuptaskmanager-production.up.railway.app/callback")
    print()
    print("✅ VENTAJAS DE LA URL CORTA:")
    print("   • ClickUp la acepta sin problemas")
    print("   • No se divide en múltiples líneas")
    print("   • Más fácil de copiar y pegar")
    print("   • Funciona igual de bien")
    print()
    print("🎯 PASOS:")
    print("1. Ve a: https://app.clickup.com/settings/apps")
    print("2. Busca 'ClickUp Project Manager v2'")
    print("3. Edita la aplicación")
    print("4. En 'Redirect URI', pega:")
    print("   https://clickuptaskmanager-production.up.railway.app/callback")
    print("5. Guarda los cambios")

def main():
    """Función principal"""
    print_header()
    
    # Actualizar archivos
    update_env_files()
    
    # Mostrar instrucciones
    print_instructions()
    
    print("\n" + "=" * 70)
    print("✅ URL CORTA CONFIGURADA")
    print("=" * 70)
    print("🚀 Haz commit, push y actualiza ClickUp con la URL corta")
    print("📱 La URL corta debería funcionar sin problemas en ClickUp")

if __name__ == "__main__":
    main()
