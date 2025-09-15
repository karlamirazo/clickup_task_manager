#!/usr/bin/env python3
"""
Arreglar configuración de la app de ClickUp
"""

import webbrowser
from core.config import settings

def fix_clickup_app_config():
    """Arreglar configuración de la app de ClickUp"""
    print("🔧 ARREGLANDO CONFIGURACIÓN DE LA APP DE CLICKUP")
    print("=" * 60)
    
    print("📋 PROBLEMA IDENTIFICADO:")
    print("   ClickUp está devolviendo HTML en lugar de JSON")
    print("   Esto significa que la app no está configurada correctamente")
    print()
    
    print("🛠️  SOLUCIÓN PASO A PASO:")
    print("=" * 40)
    
    print("1. 🗑️  ELIMINAR LA APP ACTUAL:")
    print("   - Ve a: https://app.clickup.com/settings/apps")
    print("   - Busca 'clickuptaskmanager'")
    print("   - Haz clic en 'Delete' o 'Eliminar'")
    print("   - Confirma la eliminación")
    print()
    
    print("2. 🆕 CREAR NUEVA APP:")
    print("   - Haz clic en 'Create New App' o 'Crear Nueva App'")
    print("   - Nombre: ClickUp Task Manager")
    print("   - Descripción: Sistema de gestión de tareas")
    print()
    
    print("3. 🔐 CONFIGURAR PERMISOS:")
    print("   - Selecciona estos permisos:")
    print("     ✅ read:user")
    print("     ✅ read:workspace") 
    print("     ✅ read:task")
    print("     ✅ write:task")
    print()
    
    print("4. 🌐 CONFIGURAR REDIRECT URI:")
    print(f"   - Redirect URI: {settings.CLICKUP_OAUTH_REDIRECT_URI}")
    print("   - Asegúrate de que sea EXACTAMENTE: http://127.0.0.1:8000")
    print("   - NO incluyas /api/auth/callback")
    print()
    
    print("5. 💾 GUARDAR Y OBTENER CREDENCIALES:")
    print("   - Guarda la app")
    print("   - Copia el Client ID y Client Secret")
    print("   - Actualiza el archivo .env con las nuevas credenciales")
    print()
    
    print("6. 🧪 PROBAR LA NUEVA APP:")
    print("   - Ejecuta: python test_clickup_oauth_direct.py")
    print("   - Debería devolver JSON en lugar de HTML")
    print()
    
    # Abrir ClickUp en el navegador
    print("🔗 Abriendo ClickUp en el navegador...")
    webbrowser.open("https://app.clickup.com/settings/apps")
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN:")
    print("1. Elimina la app actual")
    print("2. Crea una nueva app con los permisos correctos")
    print("3. Configura el Redirect URI exactamente como se muestra")
    print("4. Actualiza las credenciales en .env")
    print("5. Prueba la nueva configuración")
    print()
    print("¿Quieres que te ayude con algún paso específico?")

def update_env_with_new_credentials():
    """Actualizar .env con nuevas credenciales"""
    print("\n🔄 ACTUALIZANDO CREDENCIALES EN .ENV")
    print("=" * 40)
    
    print("📝 Ingresa las nuevas credenciales:")
    new_client_id = input("Client ID: ").strip()
    new_client_secret = input("Client Secret: ").strip()
    
    if not new_client_id or not new_client_secret:
        print("❌ Credenciales vacías, cancelando...")
        return
    
    # Leer .env actual
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
    except FileNotFoundError:
        print("❌ Archivo .env no encontrado")
        return
    
    # Actualizar credenciales
    lines = env_content.split('\n')
    updated_lines = []
    
    for line in lines:
        if line.startswith('CLICKUP_OAUTH_CLIENT_ID='):
            updated_lines.append(f'CLICKUP_OAUTH_CLIENT_ID={new_client_id}')
        elif line.startswith('CLICKUP_OAUTH_CLIENT_SECRET='):
            updated_lines.append(f'CLICKUP_OAUTH_CLIENT_SECRET={new_client_secret}')
        else:
            updated_lines.append(line)
    
    # Escribir .env actualizado
    with open('.env', 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print("✅ Credenciales actualizadas en .env")
    print("🧪 Ejecuta: python test_clickup_oauth_direct.py para probar")

def main():
    """Función principal"""
    print("🔧 ARREGLAR CONFIGURACIÓN DE CLICKUP")
    print("=" * 60)
    
    # Mostrar instrucciones
    fix_clickup_app_config()
    
    print("\n" + "=" * 60)
    print("¿Quieres actualizar las credenciales ahora? (y/n)")
    
    choice = input().lower()
    if choice == 'y':
        update_env_with_new_credentials()
    else:
        print("👋 ¡Hasta luego! Recuerda actualizar las credenciales cuando tengas la nueva app.")

if __name__ == "__main__":
    main()

