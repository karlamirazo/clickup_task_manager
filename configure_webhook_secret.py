#!/usr/bin/env python3
"""
Script para configurar el secreto del webhook de ClickUp
"""

import secrets
import string

def generate_webhook_secret(length=32):
    """Genera un secreto seguro para el webhook"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    print("🔐 CONFIGURACIÓN DE WEBHOOK SECRET")
    print("=" * 50)
    
    # Generar secreto
    webhook_secret = generate_webhook_secret()
    
    print(f"✅ Secreto generado: {webhook_secret}")
    print()
    print("📋 INSTRUCCIONES:")
    print("1. Copia el secreto generado arriba")
    print("2. Ve a Railway Dashboard")
    print("3. Selecciona tu proyecto")
    print("4. Ve a Variables")
    print("5. Agrega la variable: CLICKUP_WEBHOOK_SECRET")
    print("6. Pega el valor del secreto")
    print("7. Guarda los cambios")
    print()
    print("🔗 URL del webhook para ClickUp:")
    print("https://clickuptaskmanager-production.up.railway.app/api/v1/webhooks/clickup")
    print()
    print("⚠️  IMPORTANTE:")
    print("- Usa este mismo secreto en la configuración del webhook en ClickUp")
    print("- El webhook debe apuntar a la URL mostrada arriba")
    print("- Una vez configurado, las notificaciones de WhatsApp funcionarán automáticamente")

if __name__ == "__main__":
    main()
