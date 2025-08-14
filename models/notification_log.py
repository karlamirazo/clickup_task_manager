"""
Modelo para el log de notificaciones
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.sql import func

from core.database import Base


class NotificationLog(Base):
    """Log de notificaciones enviadas"""
    
    __tablename__ = "notification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Información de la notificación
    notification_type = Column(String(50), nullable=False)  # email, sms, telegram
    action = Column(String(50), nullable=False)  # created, updated, deleted
    
    # Información de la tarea
    task_id = Column(String(50), nullable=False, index=True)
    task_name = Column(String(255), nullable=False)
    
    # Información del destinatario
    recipient = Column(String(255), nullable=False, index=True)
    recipient_type = Column(String(20), nullable=False)  # email, phone, chat_id
    
    # Estado de la notificación
    status = Column(String(20), nullable=False, default="pending")  # pending, sent, failed
    error_message = Column(Text, nullable=True)
    
    # Métricas
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivery_time = Column(Float, nullable=True)  # Tiempo en segundos
    retry_count = Column(Integer, default=0)
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Información adicional
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    webhook_source = Column(Boolean, default=False)  # Si vino de webhook o de la UI
    
    def __repr__(self):
        return f"<NotificationLog(id={self.id}, type={self.notification_type}, recipient={self.recipient}, status={self.status})>"
