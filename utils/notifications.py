"""
Servicio de notificaciones (Email, Telegram y SMS) para ClickUp Project Manager
"""

from __future__ import annotations

import asyncio
from typing import List, Optional
from email.message import EmailMessage
from datetime import datetime

from core.config import settings

def log_notification(notification_type: str, recipient: str, status: str, 
                    task_id: str = None, task_name: str = None, 
                    error_message: str = None, delivery_time: float = None):
    """Registrar una notificación en los logs (best effort)"""
    try:
        from core.database import get_db
        from models.notification_log import NotificationLog
        
        db = next(get_db())
        
        log_entry = NotificationLog(
            notification_type=notification_type,
            action="task_created",  # o el action apropiado
            task_id=task_id or "unknown",  # Valor por defecto
            task_name=task_name or "Tarea sin nombre",  # Valor por defecto
            recipient=recipient,
            recipient_type="custom_field",
            status=status,
            error_message=error_message,
            delivery_time=delivery_time,
            sent_at=datetime.now() if status == "sent" else None,
            retry_count=0,
            webhook_source=False
        )
        
        db.add(log_entry)
        db.commit()
        db.close()
        
    except Exception as e:
        # No fallar si no se puede registrar el log
        print(f"⚠️ Error registrando log de notificación: {e}")

# Importación condicional de Twilio (solo si SMS está habilitado)
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False


async def send_email_async(
    to_addresses: List[str],
    subject: str,
    text_body: str,
    html_body: Optional[str] = None,
) -> None:
    """Enviar correo electrónico usando SMTP (async)."""
    
    # Verificar configuración
    if not settings.SMTP_HOST:
        print("❌ SMTP_HOST no configurado")
        return
    if not settings.SMTP_FROM:
        print("❌ SMTP_FROM no configurado")
        return
    if not to_addresses:
        print("❌ No hay direcciones de email de destino")
        return
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("❌ Credenciales SMTP no configuradas")
        return

    print(f"📧 Enviando email a: {to_addresses}")
    print(f"   📤 SMTP Host: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
    print(f"   👤 SMTP User: {settings.SMTP_USER}")

    # Construir mensaje
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = ", ".join(to_addresses)
    msg.set_content(text_body or "")
    if html_body:
        msg.add_alternative(html_body, subtype="html")

    # Enviar con aiosmtplib
    try:
        import aiosmtplib

        use_ssl = bool(settings.SMTP_USE_SSL)
        use_tls = bool(settings.SMTP_USE_TLS)
        print(f"🔐 Conectando con SSL={use_ssl}, TLS={use_tls}")
        
        # Para Gmail, usar configuración estándar
        if settings.SMTP_HOST == "smtp.gmail.com" and settings.SMTP_PORT == 587:
            # Gmail requiere STARTTLS
            smtp = aiosmtplib.SMTP(hostname=settings.SMTP_HOST, port=settings.SMTP_PORT, start_tls=True)
        else:
            smtp = aiosmtplib.SMTP(hostname=settings.SMTP_HOST, port=settings.SMTP_PORT)
            
        await smtp.connect()
        print("✅ Conectado al servidor SMTP")
        
        await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        print("✅ Login SMTP exitoso")
        
        await smtp.send_message(msg)
        print(f"✅ Email enviado exitosamente a {len(to_addresses)} destinatarios")
        
        # Registrar log de éxito para cada destinatario
        for addr in to_addresses:
            log_notification("email", addr, "sent")
        
        await smtp.quit()
        
    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        print(f"   Host: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
        print(f"   User: {settings.SMTP_USER}")
        print(f"   To: {to_addresses}")
        
        # Registrar log de error para cada destinatario
        for addr in to_addresses:
            log_notification("email", addr, "failed", error_message=str(e))
        
        # No interrumpir el flujo si falla el correo
        return


async def send_telegram_async(
    to_chat_ids: List[str],
    message: str,
) -> None:
    """Enviar mensaje de Telegram usando Bot API.
    
    to_chat_ids puede contener:
    - Chat IDs numéricos: "123456789"
    - Usernames: "@username" 
    - Chat IDs extraídos de campos personalizados
    """
    if not settings.TELEGRAM_ENABLED or not settings.TELEGRAM_BOT_TOKEN or not to_chat_ids:
        print("🚫 Telegram deshabilitado en configuración")
        return

    try:
        import httpx
        
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for chat_id in to_chat_ids:
                if not chat_id:
                    continue
                    
                chat_id = str(chat_id).strip()
                
                # Si es username, debe empezar con @
                if not chat_id.startswith('@') and not chat_id.lstrip('-').isdigit():
                    # Asumir que es username sin @
                    chat_id = f"@{chat_id}"
                
                payload = {
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "HTML"  # Usar HTML en lugar de Markdown para mayor compatibilidad
                }
                
                try:
                    response = await client.post(url, json=payload)
                    if response.status_code != 200:
                        error_msg = response.text
                        print(f"Error enviando Telegram a {chat_id}: {response.status_code} - {error_msg}")
                        
                        # Información adicional para depuración
                        if "chat not found" in error_msg.lower():
                            if chat_id.startswith("@"):
                                print(f"💡 Username {chat_id}: El usuario debe iniciar conversación con el bot primero")
                                print(f"💡 Dile al usuario que envíe /start a @Clickup_tasks_bot en Telegram")
                            else:
                                print(f"💡 Chat ID {chat_id}: Verifica que el ID sea correcto")
                        elif "forbidden" in error_msg.lower():
                            print(f"💡 Usuario {chat_id} bloqueó el bot o nunca inició conversación")
                    else:
                        print(f"✅ Telegram enviado a {chat_id}")
                except Exception as e:
                    print(f"Error enviando Telegram a {chat_id}: {e}")
                    continue
                    
    except Exception as e:
        print(f"Error en Telegram API: {e}")
        return


def build_task_email_content(
    action: str,
    task_id: str,
    name: str,
    status: Optional[str] = None,
    priority: Optional[int] = None,
    assignee_name: Optional[str] = None,
    due_date_iso: Optional[str] = None,
) -> tuple[str, str, str]:
    """Construir asunto, cuerpo de texto y HTML para email de tarea."""
    action_map = {
        "created": "Nueva tarea creada",
        "updated": "Tarea actualizada",
        "deleted": "Tarea eliminada",
    }
    subject = f"[ClickUp] {action_map.get(action, 'Notificación de tarea')}: {name}"

    lines = [
        action_map.get(action, "Notificación de tarea"),
        f"Nombre: {name}",
        f"ID: {task_id}",
    ]
    if status:
        lines.append(f"Estado: {status}")
    if priority is not None:
        lines.append(f"Prioridad: {priority}")
    if assignee_name:
        lines.append(f"Asignado a: {assignee_name}")
    if due_date_iso:
        lines.append(f"Fecha límite: {due_date_iso}")
    text_body = "\n".join(lines)

    html_lines = [f"<p>{line}</p>" for line in lines]
    html_body = "".join(html_lines)
    return subject, text_body, html_body


def build_task_telegram_message(
    action: str,
    task_id: str,
    name: str,
    status: Optional[str] = None,
    priority: Optional[int] = None,
    assignee_name: Optional[str] = None,
    due_date_iso: Optional[str] = None,
) -> str:
    """Construir mensaje de Telegram para la tarea."""
    action_map = {
        "created": "🆕 Nueva tarea",
        "updated": "✏️ Tarea actualizada", 
        "deleted": "🗑️ Tarea eliminada",
    }
    
    # Usar formato HTML de Telegram (más compatible)
    parts = [f"<b>{action_map.get(action, '📋 Tarea')}</b>", f"📝 <b>{name}</b>", f"🆔 <code>{task_id}</code>"]
    if status:
        parts.append(f"📊 Estado: {status}")
    if priority is not None:
        priority_emoji = {1: "🔴", 2: "🟠", 3: "🟡", 4: "🟢"}.get(priority, "⚪")
        parts.append(f"{priority_emoji} Prioridad: {priority}")
    if assignee_name:
        parts.append(f"👤 Asignado: {assignee_name}")
    if due_date_iso:
        parts.append(f"⏰ Vence: {due_date_iso}")
    return "\n".join(parts)


async def send_sms_async(
    to_numbers: List[str],
    message: str,
) -> None:
    """Enviar SMS usando Twilio."""
    if not settings.SMS_ENABLED:
        print("🚫 SMS deshabilitado en configuración")
        return
        
    if not TWILIO_AVAILABLE:
        print("❌ Twilio no está disponible. Instala con: pip install twilio")
        return
    
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_SMS_FROM]):
        print("❌ Configuración de Twilio incompleta")
        return
    
    if not to_numbers:
        print("⚠️ No hay números de teléfono para SMS")
        return
    
    try:
        client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        for phone_number in to_numbers:
            try:
                # Enviar SMS
                message_obj = client.messages.create(
                    body=message,
                    from_=settings.TWILIO_SMS_FROM,
                    to=phone_number
                )
                print(f"✅ SMS enviado a {phone_number}: {message_obj.sid}")
                
                # Registrar log de éxito
                log_notification("sms", phone_number, "sent")
                
            except Exception as e:
                error_msg = str(e)
                if "unverified" in error_msg.lower():
                    print(f"❌ Error enviando SMS a {phone_number}:")
                    print(f"   📞 El número {phone_number} no está verificado en Twilio")
                    print(f"   🔧 Soluciones:")
                    print(f"      1. Verificar número en: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
                    print(f"      2. O comprar un número Twilio para enviar a números no verificados")
                elif "21608" in error_msg:
                    print(f"❌ Error 21608 - Número no verificado: {phone_number}")
                    print(f"   🔧 Verifica el número en Twilio Console")
                else:
                    print(f"❌ Error enviando SMS a {phone_number}: {e}")
                
                # Registrar log de error
                log_notification("sms", phone_number, "failed", error_message=str(e))
                
    except Exception as e:
        print(f"❌ Error configurando cliente Twilio: {e}")


def build_task_sms_message(
    action: str,
    task_id: str,
    name: str,
    status: Optional[str] = None,
    priority: Optional[int] = None,
    assignee_name: Optional[str] = None,
    due_date_iso: Optional[str] = None,
) -> str:
    """Construir mensaje SMS para la tarea (versión corta)."""
    action_map = {
        "created": "Nueva tarea",
        "updated": "Tarea actualizada", 
        "deleted": "Tarea eliminada",
    }
    
    # SMS debe ser corto (160 caracteres recomendado)
    message = f"{action_map.get(action, 'Tarea')}: {name[:50]}"
    
    if status:
        message += f" - {status}"
    if assignee_name:
        message += f" (@{assignee_name})"
    if due_date_iso:
        message += f" - Vence: {due_date_iso[:10]}"  # Solo fecha, no hora
        
    # Truncar si es muy largo
    if len(message) > 155:
        message = message[:152] + "..."
    
    return message


def extract_contacts_from_custom_fields(
    custom_fields: Optional[dict],
) -> tuple[list[str], list[str], list[str]]:
    """Extraer emails, chat IDs de Telegram y números de SMS desde campos personalizados de la tarea.

    Usa variables de entorno TASK_EMAIL_FIELDS, TASK_TELEGRAM_FIELDS y TASK_SMS_FIELDS (IDs o nombres de campos, separados por coma).
    
    Para el campo "Celular", acepta estos formatos:
    - Chat ID de Telegram: "837060200" 
    - Username de Telegram: "@karlamirazo" o "karlamirazo"
    - Número de teléfono para SMS: "+1234567890" o "1234567890"
    - Chat ID de grupo: "-1001234567890"
    - Formato híbrido: "+1234567890,@karlamirazo" (teléfono,telegram)
    
    NOTA: Los números de teléfono (+1234567890) se usan para SMS, pero NO 
    se pueden usar directamente con Telegram Bot API.
    
    Retorna listas: (emails, telegram_chat_ids, sms_numbers)
    """
    emails: list[str] = []
    telegram_chat_ids: list[str] = []
    sms_numbers: list[str] = []
    if not custom_fields or not isinstance(custom_fields, dict):
        return emails, telegram_chat_ids, sms_numbers

    email_keys = [k.strip() for k in (settings.TASK_EMAIL_FIELDS or "").split(",") if k.strip()]
    telegram_keys = [k.strip() for k in (settings.TASK_TELEGRAM_FIELDS or "").split(",") if k.strip()]
    sms_keys = [k.strip() for k in (settings.TASK_SMS_FIELDS or "").split(",") if k.strip()]

    def _try_add_email(value: Optional[str]):
        if not value:
            return
        v = str(value).strip()
        if "@" in v and "." in v:
            emails.append(v)

    def _try_add_telegram(value: Optional[str]):
        if not value:
            return
        v = str(value).strip()
        
        # Si contiene coma, separar número de teléfono y telegram
        if "," in v:
            parts = [p.strip() for p in v.split(",")]
            for part in parts:
                if part.startswith('@') or (part.isdigit() and len(part) > 6 and not part.startswith('+')):
                    telegram_chat_ids.append(part)
        else:
            # Verificar si es Chat ID de Telegram (números largos sin + al inicio)
            if v.isdigit() and len(v) > 6 and not v.startswith('+'):
                telegram_chat_ids.append(v)
            # Verificar si es username de Telegram
            elif v.startswith('@'):
                telegram_chat_ids.append(v)
            # Verificar si es Chat ID negativo (grupos)
            elif v.startswith('-') and v[1:].isdigit():
                telegram_chat_ids.append(v)
            # Si parece username sin @, agregarlo
            elif v and not v.isspace() and not v.startswith('+'):
                telegram_chat_ids.append(v)
            # Si es un número de teléfono (+1234567890), no agregarlo aquí
            # Los números de teléfono se manejan en _try_add_sms

    def _try_add_sms(value: Optional[str]):
        if not value:
            return
        v = str(value).strip()
        
        # Si contiene coma, separar número de teléfono y telegram
        if "," in v:
            parts = [p.strip() for p in v.split(",")]
            for part in parts:
                if part.startswith('+') or (part.isdigit() and len(part) >= 8):
                    # Normalizar número de teléfono
                    if not part.startswith('+'):
                        part = '+' + part
                    sms_numbers.append(part)
        else:
            # Verificar si es número de teléfono para SMS
            if v.startswith('+') and v[1:].isdigit() and len(v) >= 9:
                sms_numbers.append(v)
            elif v.isdigit() and len(v) >= 8:
                # Agregar + si es un número sin código de país
                sms_numbers.append('+' + v)

    # Coincidir por clave directa
    for key in email_keys:
        if key in custom_fields:
            _try_add_email(custom_fields.get(key))

    for key in telegram_keys:
        if key in custom_fields:
            _try_add_telegram(custom_fields.get(key))
            
    for key in sms_keys:
        if key in custom_fields:
            _try_add_sms(custom_fields.get(key))

    # Coincidir por id o name interno si la estructura viniera como lista de dicts
    # Algunas integraciones guardan custom_fields como lista; manejamos ambos
    if isinstance(custom_fields, list):
        for field in custom_fields:
            try:
                fid = str(field.get("id", "")).strip()
                fname = str(field.get("name", "")).strip()
                val = field.get("value")
                if fid in email_keys or fname in email_keys:
                    _try_add_email(val)
                if fid in telegram_keys or fname in telegram_keys:
                    _try_add_telegram(val)
                if fid in sms_keys or fname in sms_keys:
                    _try_add_sms(val)
            except Exception:
                continue

    # Devolver únicos
    return list(dict.fromkeys(emails)), list(dict.fromkeys(telegram_chat_ids)), list(dict.fromkeys(sms_numbers))


