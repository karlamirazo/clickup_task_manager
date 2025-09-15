#!/usr/bin/env python3
"""
Probar OAuth con URL temporal
"""

import requests
import webbrowser

def print_banner():
    """Mostrar banner"""
    print("=" * 60)
    print("🔧 SOLUCIÓN TEMPORAL PARA OAUTH")
    print("=" * 60)
    print()

def get_temp_webhook_url():
    """Obtener URL temporal de webhook.site"""
    print("1️⃣ OBTENIENDO URL TEMPORAL...")
    
    try:
        # Usar webhook.site para obtener una URL temporal
        response = requests.get("https://webhook.site/token")
        if response.status_code == 200:
            token = response.text.strip()
            webhook_url = f"https://webhook.site/{token}"
            print(f"   ✅ URL temporal obtenida: {webhook_url}")
            return webhook_url
        else:
            print("   ❌ Error obteniendo URL temporal")
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def show_clickup_config_with_temp_url(webhook_url):
    """Mostrar instrucciones para configurar ClickUp con URL temporal"""
    print("\n2️⃣ CONFIGURAR CLICKUP CON URL TEMPORAL:")
    print("=" * 50)
    print("1. Ve a: https://app.clickup.com/settings/apps")
    print("2. Busca tu aplicación 'clickuptaskmanager'")
    print("3. Haz clic en 'Edit' o 'Configurar'")
    print("4. En 'Redireccionamiento de URL', cambia a:")
    print(f"   {webhook_url}")
    print("5. Guarda los cambios")
    print()
    print("🔧 PERMISOS NECESARIOS:")
    print("   - read:user")
    print("   - read:workspace")
    print("   - read:task")
    print("   - write:task")
    print()

def test_oauth_flow():
    """Probar flujo OAuth"""
    print("\n3️⃣ PROBAR FLUJO OAUTH:")
    print("=" * 50)
    print("1. Ve a: http://localhost:8000/api/auth/login")
    print("2. Haz clic en 'Iniciar con ClickUp'")
    print("3. ClickUp te redirigirá a la URL temporal")
    print("4. Copia la URL completa del callback")
    print("5. Úsala para probar manualmente")
    print()

def show_manual_callback_test():
    """Mostrar cómo probar el callback manualmente"""
    print("\n4️⃣ PROBAR CALLBACK MANUALMENTE:")
    print("=" * 50)
    print("Después de que ClickUp redirija a la URL temporal:")
    print("1. Copia la URL completa (incluye code= y state=)")
    print("2. Reemplaza la URL temporal por localhost:")
    print("   http://localhost:8000/api/auth/callback?code=...&state=...")
    print("3. Abre esa URL en el navegador")
    print("4. ¡Deberías ser redirigido al dashboard!")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Obtener URL temporal
    webhook_url = get_temp_webhook_url()
    
    if webhook_url:
        # Mostrar instrucciones
        show_clickup_config_with_temp_url(webhook_url)
        test_oauth_flow()
        show_manual_callback_test()
        
        print("\n" + "=" * 60)
        print("🎉 ¡CONFIGURACIÓN COMPLETA!")
        print("=" * 60)
        print(f"🌐 URL Temporal: {webhook_url}")
        print(f"🔗 Redirect URI: {webhook_url}")
        print()
        print("⚠️  IMPORTANTE:")
        print("   - Esta URL es temporal")
        print("   - Solo funciona por unas horas")
        print("   - Para producción, usa ngrok o un dominio real")
    else:
        print("\n❌ No se pudo obtener URL temporal")
        print("💡 Intenta con ngrok o usa un dominio real")

if __name__ == "__main__":
    main()

