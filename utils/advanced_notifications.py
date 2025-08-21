"""
Sistema avanzado de notificaciones con reintentos, plantillas HTML y logging
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from email.message import EmailMessage
import logging

from core.config import settings
from utils.email_templates import get_email_template, get_summary_email_template

# Configurar logging especifico para notificaciones
logging.basicConfig(level=logging.INFO)
notification_logger = logging.getLogger("notifications")

# Importaciones condicionales
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class NotificationResult:
    """Clase para manejar resultados de notificaciones"""
    
    def __init__(self):
        self.total_sent = 0
        self.successful_emails = 0
        self.successful_sms = 0
        self.successful_telegram = 0
        self.failed_notifications = 0
        self.errors = []
        self.sent_to = []
        self.failed_to = []
        
    def add_success(self, channel: str, recipient: str):
        """Agregar notificacion exitosa"""
        self.total_sent += 1
        self.sent_to.append({"channel": channel, "recipient": recipient, "timestamp": datetime.now().isoformat()})
        
        if channel == "email":
            self.successful_emails += 1
        elif channel == "sms":
            self.successful_sms += 1
        elif channel == "telegram":
            self.successful_telegram += 1
    
    def add_failure(self, channel: str, recipient: str, error: str):
        """Agregar notificacion fallida"""
        self.failed_notifications += 1
        self.failed_to.append({
            "channel": channel, 
            "recipient": recipient, 
            "error": error, 
            "timestamp": datetime.now().isoformat()
        })
        self.errors.append(f"{channel} to {recipient}: {error}")
    
    def get_summary(self) -> dict:
        """Get resumen de resultados"""
        return {
            "total_sent": self.total_sent,
            "successful": {
                "emails": self.successful_emails,
                "sms": self.successful_sms,
                "telegram": self.successful_telegram,
                "total": self.successful_emails + self.successful_sms + self.successful_telegram
            },
            "failed": self.failed_notifications,
            "success_rate": (self.successful_emails + self.successful_sms + self.successful_telegram) / max(self.total_sent + self.failed_notifications, 1) * 100,
            "errors": self.errors,
            "sent_to": self.sent_to,
            "failed_to": self.failed_to
        }


class AdvancedNotificationService:
    """Servicio avanzado de notificaciones con reintentos y mejor logging"""
    
    def __init__(self):
        self.stats = {
            "total_notifications": 0,
            "successful_notifications": 0,
            "failed_notifications": 0,
            "last_reset": datetime.now()
        }
    
    async def send_task_notification(
        self,
        action: str,
        task_id: str,
        task_name: str,
        recipient_emails: List[str] = None,
        recipient_sms: List[str] = None,
        recipient_telegrams: List[str] = None,
        status: Optional[str] = None,
        priority: Optional[int] = None,
        assignee_name: Optional[str] = None,
        due_date: Optional[str] = None,
        description: Optional[str] = None
    ) -> NotificationResult:
        """
        Enviar notificacion completa de tarea con plantillas HTML y reintentos
        """
        result = NotificationResult()
        
        # Validar que tenemos destinatarios
        all_recipients = (recipient_emails or []) + (recipient_sms or []) + (recipient_telegrams or [])
        if not all_recipients:
            notification_logger.warning("No hay destinatarios para la notificacion")
            return result
        
        notification_logger.info(f"ðŸ”” Enviando notificacion de tarea {action}: {task_name}")
        
        # Generar plantilla HTML para email
        subject, html_body = get_email_template(
            action=action,
            task_name=task_name,
            task_id=task_id,
            status=status,
            priority=priority,
            assignee_name=assignee_name,
            due_date=due_date,
            description=description
        )
        
        # Generar texto plano para SMS/Telegram
        text_message = self._build_text_message(
            action=action,
            task_name=task_name,
            task_id=task_id,
            status=status,
            priority=priority,
            assignee_name=assignee_name,
            due_date=due_date
        )
        
        # Enviar notificaciones en paralelo
        tasks = []
        
        if recipient_emails:
            tasks.append(self._send_email_with_retry(recipient_emails, subject, text_message, html_body, result))
        
        if recipient_sms:
            tasks.append(self._send_sms_with_retry(recipient_sms, text_message, result))
        
        if recipient_telegrams:
            tasks.append(self._send_telegram_with_retry(recipient_telegrams, text_message, result))
        
        # Execute todas las notificaciones en paralelo
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Update estadisticas
        self._update_stats(result)
        
        # Log del resumen
        summary = result.get_summary()
        notification_logger.info(f"ðŸ“Š Notificacion completada: {summary['successful']['total']} exitosas, {summary['failed']} fallidas")
        
        return result
    
    async def _send_email_with_retry(
        self, 
        recipients: List[str], 
        subject: str, 
        text_body: str, 
        html_body: str, 
        result: NotificationResult,
        max_retries: int = 3
    ):
        """Enviar email con reintentos"""
        if not settings.SMTP_HOST or not recipients:
            return
        
        for attempt in range(max_retries):
            try:
                import aiosmtplib
                
                # Validar emails
                valid_emails = [email for email in recipients if email and "@" in email]
                
                for email in valid_emails:
                    try:
                        msg = EmailMessage()
                        msg["Subject"] = subject
                        msg["From"] = settings.SMTP_FROM
                        msg["To"] = email
                        msg.set_content(text_body)
                        msg.add_alternative(html_body, subtype="html")
                        
                        smtp = aiosmtplib.SMTP(
                            hostname=settings.SMTP_HOST, 
                            port=settings.SMTP_PORT,
                            use_tls=bool(settings.SMTP_USE_SSL),
                            timeout=30
                        )
                        
                        await smtp.connect()
                        if settings.SMTP_USE_TLS and not settings.SMTP_USE_SSL:
                            await smtp.starttls()
                        if settings.SMTP_USER and settings.SMTP_PASS:
                            await smtp.login(settings.SMTP_USER, settings.SMTP_PASS)
                        
                        await smtp.send_message(msg)
                        await smtp.quit()
                        
                        result.add_success("email", email)
                        notification_logger.info(f"âœ… Email enviado a: {email}")
                        
                    except Exception as email_error:
                        error_msg = f"Error enviando email a {email}: {email_error}"
                        notification_logger.error(error_msg)
                        if attempt == max_retries - 1:  # Ultimo intento
                            result.add_failure("email", email, str(email_error))
                
                break  # Salir del loop si todo fue exitoso
                
            except Exception as smtp_error:
                notification_logger.error(f"Intento {attempt + 1}/{max_retries} de SMTP fallo: {smtp_error}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Backoff exponencial
                else:
                    for email in recipients:
                        result.add_failure("email", email, str(smtp_error))
    
    async def _send_sms_with_retry(
        self, 
        recipients: List[str], 
        message: str, 
        result: NotificationResult,
        max_retries: int = 3
    ):
        """Enviar SMS con reintentos"""
        if not settings.SMS_ENABLED or not TWILIO_AVAILABLE or not recipients:
            return
        
        try:
            client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            for phone_number in recipients:
                for attempt in range(max_retries):
                    try:
                        # Formatear numero de telefono
                        clean_number = phone_number.strip()
                        if not clean_number.startswith("+"):
                            clean_number = f"+{clean_number}"
                        
                        message_obj = client.messages.create(
                            body=message,
                            from_=settings.TWILIO_SMS_FROM,
                            to=clean_number
                        )
                        
                        result.add_success("sms", phone_number)
                        notification_logger.info(f"âœ… SMS enviado a {phone_number}: {message_obj.sid}")
                        break
                        
                    except Exception as sms_error:
                        notification_logger.error(f"Intento {attempt + 1}/{max_retries} SMS a {phone_number}: {sms_error}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(1)
                        else:
                            result.add_failure("sms", phone_number, str(sms_error))
                            
        except Exception as twilio_error:
            notification_logger.error(f"Error general de Twilio: {twilio_error}")
            for phone in recipients:
                result.add_failure("sms", phone, str(twilio_error))
    
    async def _send_telegram_with_retry(
        self, 
        recipients: List[str], 
        message: str, 
        result: NotificationResult,
        max_retries: int = 3
    ):
        """Enviar Telegram con reintentos"""
        if not settings.TELEGRAM_ENABLED or not settings.TELEGRAM_BOT_TOKEN or not HTTPX_AVAILABLE or not recipients:
            notification_logger.info("ðŸš« Telegram deshabilitado en configuracion")
            return
        
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for chat_id in recipients:
                for attempt in range(max_retries):
                    try:
                        payload = {
                            "chat_id": str(chat_id).strip(),
                            "text": message,
                            "parse_mode": "HTML"
                        }
                        
                        response = await client.post(url, json=payload)
                        
                        if response.status_code == 200:
                            result.add_success("telegram", chat_id)
                            notification_logger.info(f"âœ… Telegram enviado a {chat_id}")
                            break
                        else:
                            error_msg = f"HTTP {response.status_code}: {response.text}"
                            notification_logger.error(f"Intento {attempt + 1}/{max_retries} Telegram a {chat_id}: {error_msg}")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(1)
                            else:
                                result.add_failure("telegram", chat_id, error_msg)
                                
                    except Exception as telegram_error:
                        error_msg = str(telegram_error)
                        notification_logger.error(f"Intento {attempt + 1}/{max_retries} Telegram a {chat_id}: {error_msg}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(1)
                        else:
                            result.add_failure("telegram", chat_id, error_msg)
    
    def _build_text_message(
        self,
        action: str,
        task_name: str,
        task_id: str,
        status: Optional[str] = None,
        priority: Optional[int] = None,
        assignee_name: Optional[str] = None,
        due_date: Optional[str] = None
    ) -> str:
        """Construir mensaje de texto para SMS/Telegram"""
        action_emoji = {
            "created": "ðŸ†•",
            "updated": "âœ�ï¸�", 
            "deleted": "ðŸ—‘ï¸�"
        }
        
        emoji = action_emoji.get(action, "ðŸ“‹")
        action_text = action.title().replace("_", " ")
        
        parts = [f"{emoji} {action_text}", f"ðŸ“� {task_name}", f"ðŸ†” {task_id}"]
        
        if status:
            parts.append(f"ðŸ“Š Estado: {status}")
        
        if priority is not None:
            priority_emoji = {1: "ðŸ”´", 2: "ðŸŸ ", 3: "ðŸŸ¡", 4: "ðŸŸ¢"}.get(priority, "âšª")
            parts.append(f"{priority_emoji} Prioridad: {priority}")
        
        if assignee_name:
            parts.append(f"ðŸ‘¤ Asignado: {assignee_name}")
        
        if due_date:
            parts.append(f"â�° Vence: {due_date}")
        
        return "\\n".join(parts)
    
    def _update_stats(self, result: NotificationResult):
        """Update estadisticas del servicio"""
        summary = result.get_summary()
        self.stats["total_notifications"] += summary["total_sent"] + summary["failed"]
        self.stats["successful_notifications"] += summary["successful"]["total"]
        self.stats["failed_notifications"] += summary["failed"]
    
    def get_stats(self) -> dict:
        """Get estadisticas del servicio"""
        return {
            **self.stats,
            "success_rate": (self.stats["successful_notifications"] / max(self.stats["total_notifications"], 1)) * 100,
            "uptime": datetime.now() - self.stats["last_reset"]
        }
    
    def reset_stats(self):
        """Resetear estadisticas"""
        self.stats = {
            "total_notifications": 0,
            "successful_notifications": 0,
            "failed_notifications": 0,
            "last_reset": datetime.now()
        }
    
    async def send_summary_email(self, admin_email: str):
        """Enviar email de resumen de notificaciones"""
        stats = self.get_stats()
        
        subject, html_body = get_summary_email_template(
            notifications_sent=stats["total_notifications"],
            successful_emails=0,  # Tendriamos que trackear esto por separado
            successful_sms=0,
            successful_telegram=0,
            failed_notifications=stats["failed_notifications"]
        )
        
        result = NotificationResult()
        await self._send_email_with_retry([admin_email], subject, "", html_body, result)
        return result


# Instancia global del servicio
notification_service = AdvancedNotificationService()
