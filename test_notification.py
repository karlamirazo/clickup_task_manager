#!/usr/bin/env python3
"""
Script para probar las notificaciones de ClickUp
"""

import asyncio
import os
import json

# Configurar variables de entorno
os.environ.update({
    'CLICKUP_API_TOKEN': 'pk_156221125_VE0TJ0IMP8ZQ5U5QBCYGUQC2K94I8B48',
    'TELEGRAM_BOT_TOKEN': '7891645006:AAE3vsSBYWtjfkVnqhwlkSHYJyaLuKhLnRk',
    'TELEGRAM_CHAT_ID': '837060200',
    'SMTP_HOST': 'smtp.gmail.com',
    'SMTP_PORT': '587',
    'SMTP_USER': 'karlamirazo@gmail.com',
    'SMTP_PASSWORD': 'qirk suzf kjot jicz',
    'SMTP_FROM': 'karlamirazo@gmail.com',
    'SMTP_USE_TLS': 'True',
    'SMTP_USE_SSL': 'False',
    'TASK_EMAIL_FIELDS': 'Email',
    'TASK_TELEGRAM_FIELDS': 'Telegram',
    'DATABASE_URL': 'sqlite:///./clickup_manager.db'
})

from utils.notifications import (
    send_email_async,
    send_telegram_async,
    build_task_email_content,
    build_task_telegram_message
)

async def test_notifications():
    """Probar notificaciones directamente"""
    print("🧪 Iniciando prueba de notificaciones...")
    print("=" * 50)
    
    # Datos de prueba
    task_data = {
        "action": "created",
        "task_id": "TEST123456",
        "name": "🎉 Prueba de notificaciones",
        "status": "to_do",
        "priority": 2,
        "assignee_name": "Karla Ve",
        "due_date_iso": "2024-01-15T10:00:00Z"
    }
    
    print(f"📋 Tarea de prueba: {task_data['name']}")
    print(f"🆔 ID: {task_data['task_id']}")
    
    # 1. Probar Email
    print("\n📧 Probando email...")
    try:
        subject, text_body, html_body = build_task_email_content(**task_data)
        print(f"   ✅ Asunto: {subject}")
        
        await send_email_async(
            to_addresses=["karlamirazo@gmail.com"],
            subject=subject,
            text_body=text_body,
            html_body=html_body
        )
        print("   ✅ Email enviado correctamente")
    except Exception as e:
        print(f"   ❌ Error en email: {e}")
    
    # 2. Probar Telegram
    print("\n🤖 Probando Telegram...")
    try:
        telegram_msg = build_task_telegram_message(**task_data)
        print(f"   📝 Mensaje: {telegram_msg[:50]}...")
        
        await send_telegram_async(
            to_chat_ids=["837060200"],
            message=telegram_msg
        )
        print("   ✅ Telegram enviado correctamente")
    except Exception as e:
        print(f"   ❌ Error en Telegram: {e}")
    
    print("\n" + "🎉" * 25)
    print("🎉 PRUEBA COMPLETADA!")
    print("🎉" * 25)
    print("📱 Revisa tu Telegram y email")
    print("📧 karlamirazo@gmail.com")
    print("🤖 Chat ID: 837060200")

if __name__ == "__main__":
    asyncio.run(test_notifications())

