#!/usr/bin/env python3
"""
Corregir Redirect URI para ClickUp
"""

def print_banner():
    """Mostrar banner"""
    print("=" * 60)
    print("🔧 CORREGIR REDIRECT URI PARA CLICKUP")
    print("=" * 60)
    print()

def show_clickup_config_options():
    """Mostrar opciones de configuración para ClickUp"""
    print("📋 OPCIONES PARA CONFIGURAR CLICKUP:")
    print("=" * 50)
    print()
    print("🎯 OPCIÓN 1: Usar 127.0.0.1 (Recomendado)")
    print("   Redirect URI: http://127.0.0.1:8000/api/auth/callback")
    print("   Ventajas: Funciona inmediatamente")
    print("   Desventajas: Solo funciona en tu máquina")
    print()
    print("🎯 OPCIÓN 2: Usar ngrok (Para pruebas)")
    print("   1. Instala ngrok: https://ngrok.com/download")
    print("   2. Ejecuta: ngrok http 8000")
    print("   3. Usa la URL que te da ngrok")
    print("   Ventajas: URL pública, funciona desde cualquier lugar")
    print("   Desventajas: Requiere instalación adicional")
    print()
    print("🎯 OPCIÓN 3: Usar un dominio temporal")
    print("   Redirect URI: https://webhook.site/tu-token-unico")
    print("   Ventajas: No requiere instalación")
    print("   Desventajas: URL temporal, solo para pruebas")
    print()

def show_step_by_step_instructions():
    """Mostrar instrucciones paso a paso"""
    print("📋 INSTRUCCIONES PASO A PASO:")
    print("=" * 50)
    print()
    print("1️⃣ CONFIGURAR CLICKUP:")
    print("   - Ve a: https://app.clickup.com/settings/apps")
    print("   - Busca 'clickuptaskmanager'")
    print("   - Haz clic en 'Edit'")
    print("   - Cambia Redirect URI a: http://127.0.0.1:8000/api/auth/callback")
    print("   - Guarda los cambios")
    print()
    print("2️⃣ CONFIGURAR PERMISOS:")
    print("   - Busca la sección 'Permissions' o 'Permisos'")
    print("   - Selecciona:")
    print("     ✅ read:user")
    print("     ✅ read:workspace")
    print("     ✅ read:task")
    print("     ✅ write:task")
    print("   - Guarda los cambios")
    print()
    print("3️⃣ PROBAR OAUTH:")
    print("   - Ve a: http://localhost:8000/api/auth/login")
    print("   - Haz clic en 'Iniciar con ClickUp'")
    print("   - ClickUp debería mostrar permisos")
    print("   - Acepta los permisos")
    print("   - ¡Serás redirigido al dashboard!")
    print()

def show_troubleshooting():
    """Mostrar solución de problemas"""
    print("🔧 SOLUCIÓN DE PROBLEMAS:")
    print("=" * 50)
    print()
    print("❌ Si ClickUp sigue rechazando la URL:")
    print("   1. Usa ngrok: ngrok http 8000")
    print("   2. Usa la URL de ngrok como Redirect URI")
    print("   3. Ejemplo: https://abc123.ngrok.io/api/auth/callback")
    print()
    print("❌ Si no aparecen los permisos:")
    print("   1. Verifica que la app esté activa en ClickUp")
    print("   2. Verifica que los permisos estén configurados")
    print("   3. Intenta crear una nueva app en ClickUp")
    print()
    print("❌ Si el callback falla:")
    print("   1. Verifica que la aplicación esté ejecutándose")
    print("   2. Verifica que el puerto 8000 esté libre")
    print("   3. Revisa los logs de la aplicación")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Mostrar opciones
    show_clickup_config_options()
    
    # Mostrar instrucciones
    show_step_by_step_instructions()
    
    # Mostrar solución de problemas
    show_troubleshooting()
    
    print("\n" + "=" * 60)
    print("🎉 ¡CONFIGURACIÓN COMPLETA!")
    print("=" * 60)
    print("💡 RECOMENDACIÓN: Usa 127.0.0.1 en lugar de localhost")
    print("🔗 Redirect URI: http://127.0.0.1:8000/api/auth/callback")

if __name__ == "__main__":
    main()

