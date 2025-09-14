#!/usr/bin/env python3
"""
Configurar OAuth con webhook.site (solución temporal)
"""

import requests
import webbrowser
import time

def get_webhook_url():
    """Obtener URL temporal de webhook.site"""
    print("🌐 OBTENIENDO URL TEMPORAL DE WEBHOOK.SITE...")
    print("=" * 50)
    
    try:
        # Crear webhook temporal
        response = requests.get('https://webhook.site/token')
        if response.status_code == 200:
            data = response.json()
            webhook_url = f"https://webhook.site/{data['uuid']}"
            print(f"✅ URL temporal creada: {webhook_url}")
            return webhook_url
        else:
            print("❌ Error creando webhook")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def show_clickup_instructions(webhook_url):
    """Mostrar instrucciones para ClickUp"""
    print("\n📋 CONFIGURAR CLICKUP CON WEBHOOK.SITE")
    print("=" * 50)
    print("1. Ve a: https://app.clickup.com/settings/apps")
    print("2. Busca 'clickuptaskmanager'")
    print("3. Haz clic en 'Edit'")
    print("4. Cambia Redirect URI a:")
    print(f"   {webhook_url}")
    print("5. Guarda los cambios")
    print()
    print("🔧 PERMISOS NECESARIOS:")
    print("   - read:user")
    print("   - read:workspace")
    print("   - read:task")
    print("   - write:task")
    print()
    print("⚠️  IMPORTANTE:")
    print("   - Esta es una solución temporal para testing")
    print("   - La URL expira después de un tiempo")
    print("   - Para producción, usa un dominio fijo")

def test_webhook(webhook_url):
    """Probar webhook"""
    print("\n🧪 PROBANDO WEBHOOK...")
    print("=" * 50)
    
    try:
        # Probar webhook
        response = requests.get(webhook_url)
        if response.status_code == 200:
            print("✅ Webhook funcionando")
            return True
        else:
            print(f"❌ Error en webhook: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("🎯 CONFIGURANDO OAUTH CON WEBHOOK.SITE")
    print("=" * 60)
    
    # Obtener URL de webhook
    webhook_url = get_webhook_url()
    if not webhook_url:
        print("❌ No se pudo crear webhook")
        return
    
    # Probar webhook
    if not test_webhook(webhook_url):
        print("❌ Webhook no funciona")
        return
    
    # Mostrar instrucciones
    show_clickup_instructions(webhook_url)
    
    print("\n🎉 ¡CONFIGURACIÓN LISTA!")
    print("=" * 60)
    print("✅ Webhook temporal creado")
    print("✅ Instrucciones para ClickUp listas")
    print()
    print("📋 PRÓXIMOS PASOS:")
    print("1. Configura ClickUp con la URL de webhook")
    print("2. Prueba el OAuth")
    print("3. Para producción, usa un dominio fijo")
    print()
    print("🔗 Abriendo webhook en el navegador...")
    webbrowser.open(webhook_url)

if __name__ == "__main__":
    main()
