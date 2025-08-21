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
    """Test notificaciones directamente"""
    print("ğŸ§ª Iniciando prueba de notificaciones...")
    print("=" * 50)
    
    # Datos de prueba
    task_data = {
        "action": "created",
        "task_id": "TEST123456",
        "name": "ğŸ�‰ Prueba de notificaciones",
        "status": "to_do",
        "priority": 2,
        "assignee_name": "Karla Ve",
        "due_date_iso": "2024-01-15T10:00:00Z"
    }
    
    print(f"ğŸ“‹ Tarea de prueba: {task_data['name']}")
    print(f"ğŸ†” ID: {task_data['task_id']}")
    
    # 1. Test Email
    print("\nğŸ“§ Probando email...")
    try:
        subject, text_body, html_body = build_task_email_content(**task_data)
        print(f"   âœ… Asunto: {subject}")
        
        await send_email_async(
            to_addresses=["karlamirazo@gmail.com"],
            subject=subject,
            text_body=text_body,
            html_body=html_body
        )
        print("   âœ… Email enviado correctamente")
    except Exception as e:
        print(f"   â�Œ Error en email: {e}")
    
    # 2. Test Telegram
    print("\nğŸ¤– Probando Telegram...")
    try:
        telegram_msg = build_task_telegram_message(**task_data)
        print(f"   ğŸ“� Mensaje: {telegram_msg[:50]}...")
        
        await send_telegram_async(
            to_chat_ids=["837060200"],
            message=telegram_msg
        )
        print("   âœ… Telegram enviado correctamente")
    except Exception as e:
        print(f"   â�Œ Error en Telegram: {e}")
    
    print("\n" + "ğŸ�‰" * 25)
    print("ğŸ�‰ PRUEBA COMPLETADA!")
    print("ğŸ�‰" * 25)
    print("ğŸ“± Revisa tu Telegram y email")
    print("ğŸ“§ karlamirazo@gmail.com")
    print("ğŸ¤– Chat ID: 837060200")

if __name__ == "__main__":
    asyncio.run(test_notifications())

