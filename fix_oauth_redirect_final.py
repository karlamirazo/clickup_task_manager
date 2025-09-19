#!/usr/bin/env python3
"""
Script para corregir la configuración OAuth de ClickUp
Actualiza la URL de redireccionamiento y verifica la configuración
"""

import os
import sys
from datetime import datetime

def print_header():
    """Imprimir cabecera del script"""
    print("=" * 70)
    print("🔧 CORRECTOR DE CONFIGURACIÓN OAUTH CLICKUP")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def check_current_config():
    """Verificar configuración actual"""
    print("🔍 VERIFICANDO CONFIGURACIÓN ACTUAL...")
    print("-" * 50)
    
    # Verificar variables de entorno
    client_id = os.getenv('CLICKUP_OAUTH_CLIENT_ID', '')
    client_secret = os.getenv('CLICKUP_OAUTH_CLIENT_SECRET', '')
    redirect_uri = os.getenv('CLICKUP_OAUTH_REDIRECT_URI', '')
    
    print(f"✓ Client ID: {'✅ Configurado' if client_id else '❌ No configurado'}")
    print(f"✓ Client Secret: {'✅ Configurado' if client_secret else '❌ No configurado'}")
    print(f"✓ Redirect URI actual: {redirect_uri}")
    
    return client_id, client_secret, redirect_uri

def update_env_file():
    """Actualizar archivo .env con la configuración correcta"""
    print("\n📝 ACTUALIZANDO ARCHIVO .ENV...")
    print("-" * 50)
    
    # URL correcta con endpoint completo
    correct_redirect_uri = "https://ctm-pro.up.railway.app/api/auth/callback"
    
    env_files = ['.env', 'env.production', 'env.oauth.simple']
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"📄 Actualizando {env_file}...")
            
            # Leer contenido actual
            with open(env_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Actualizar líneas
            updated_lines = []
            redirect_uri_found = False
            
            for line in lines:
                if line.startswith('CLICKUP_OAUTH_REDIRECT_URI='):
                    updated_lines.append(f'CLICKUP_OAUTH_REDIRECT_URI={correct_redirect_uri}\n')
                    redirect_uri_found = True
                    print(f"   ✅ Actualizada CLICKUP_OAUTH_REDIRECT_URI")
                else:
                    updated_lines.append(line)
            
            # Si no se encontró, agregar al final
            if not redirect_uri_found:
                updated_lines.append(f'\n# OAuth Configuration\nCLICKUP_OAUTH_REDIRECT_URI={correct_redirect_uri}\n')
                print(f"   ✅ Agregada CLICKUP_OAUTH_REDIRECT_URI")
            
            # Escribir archivo actualizado
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)
            
            print(f"   ✅ {env_file} actualizado correctamente")
        else:
            print(f"   ⚠️ {env_file} no existe")

def update_config_file():
    """Actualizar core/config.py con la URL correcta"""
    print("\n🔧 ACTUALIZANDO CORE/CONFIG.PY...")
    print("-" * 50)
    
    config_file = "core/config.py"
    
    if os.path.exists(config_file):
        # Leer contenido actual
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar la URL incorrecta
        old_url = '"https://ctm-pro.up.railway.app"  # URL de Railway (solo dominio)'
        new_url = '"https://ctm-pro.up.railway.app/api/auth/callback"  # URL completa con endpoint'
        
        if old_url in content:
            content = content.replace(old_url, new_url)
            
            # Escribir archivo actualizado
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("   ✅ core/config.py actualizado correctamente")
        else:
            print("   ℹ️ core/config.py ya está actualizado")
    else:
        print("   ❌ core/config.py no encontrado")

def print_clickup_instructions():
    """Imprimir instrucciones para actualizar ClickUp"""
    print("\n📋 INSTRUCCIONES PARA CLICKUP...")
    print("-" * 50)
    print("🌐 Ahora debes actualizar la configuración en ClickUp:")
    print()
    print("1. 🔗 Ve a: https://app.clickup.com/settings/apps")
    print("2. 🔍 Busca tu aplicación 'ClickUp Project Manager v2'")
    print("3. ✏️ Haz clic en 'Editar' o el ícono de configuración")
    print("4. 📝 En 'Redirect URI', cambia la URL a:")
    print("   📍 https://ctm-pro.up.railway.app/api/auth/callback")
    print("5. 💾 Guarda los cambios")
    print("6. ✅ ¡Listo! Ahora el OAuth debería funcionar correctamente")
    print()
    print("⚠️ IMPORTANTE:")
    print("   • La URL debe incluir '/api/auth/callback' al final")
    print("   • NO uses solo el dominio sin el endpoint")
    print("   • Verifica que no haya espacios extra")

def print_oauth_flow_info():
    """Imprimir información sobre el flujo OAuth mejorado"""
    print("\n🔄 MEJORAS IMPLEMENTADAS...")
    print("-" * 50)
    print("✅ URL de redireccionamiento corregida")
    print("✅ Callback funcional que redirige al dashboard")
    print("✅ Parámetro 'prompt=select_account' para forzar selección de cuenta")
    print("✅ Manejo de errores mejorado")
    print("✅ Redirección automática al dashboard después del OAuth")
    print()
    print("🎯 AHORA CLICKUP DEBERÍA:")
    print("   • Preguntarte con qué cuenta quieres iniciar sesión")
    print("   • Redirigirte correctamente al dashboard después de autorizar")
    print("   • No mostrar más el error 404")

def main():
    """Función principal"""
    print_header()
    
    # Verificar configuración actual
    client_id, client_secret, redirect_uri = check_current_config()
    
    if not client_id or not client_secret:
        print("\n❌ ERROR: OAuth no está configurado completamente")
        print("   Configura CLICKUP_OAUTH_CLIENT_ID y CLICKUP_OAUTH_CLIENT_SECRET primero")
        return
    
    # Actualizar archivos
    update_env_file()
    update_config_file()
    
    # Mostrar instrucciones
    print_clickup_instructions()
    print_oauth_flow_info()
    
    print("\n" + "=" * 70)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("=" * 70)
    print("🚀 Reinicia la aplicación y prueba el OAuth nuevamente")
    print("📱 Ahora ClickUp te preguntará con qué cuenta quieres iniciar sesión")
    print("🎯 Después de autorizar, serás redirigido automáticamente al dashboard")

if __name__ == "__main__":
    main()
