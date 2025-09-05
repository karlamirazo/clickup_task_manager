"""
Modelo de datos para tareas de ClickUp
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from core.database import Base

class Task(Base):
    """Modelo de tarea de ClickUp"""
    
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    clickup_id = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(100), nullable=False, default="to_do")
    priority = Column(Integer, default=3)  # 1=Urgente, 2=Alta, 3=Normal, 4=Baja
    
    # Fechas
    due_date = Column(DateTime, nullable=True)
    start_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    workspace_id = Column(String(255), nullable=False)
    list_id = Column(String(255), nullable=False)
    assignee_id = Column(String(255), nullable=True)
    creator_id = Column(String(255), nullable=True, default="system")
    
    # Metadatos
    tags = Column(JSON, nullable=True)  # Lista de etiquetas
    custom_fields = Column(JSON, nullable=True)  # Campos personalizados
    attachments = Column(JSON, nullable=True)  # Archivos adjuntos
    comments = Column(JSON, nullable=True)  # Comentarios
    
    # Estado de sincronizacion
    is_synced = Column(Boolean, default=False)
    last_sync = Column(DateTime, nullable=True)
    
    # Relaciones con otros modelos
    automation_rules = relationship("Automation", back_populates="task")
    
    def __repr__(self):
        return f"<Task(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            "id": self.id,
            "clickup_id": self.clickup_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "workspace_id": self.workspace_id,
            "list_id": self.list_id,
            "assignee_id": self.assignee_id,
            "creator_id": self.creator_id,
            "tags": self.tags,
            "custom_fields": self.custom_fields,
            "attachments": self.attachments,
            "comments": self.comments,
            "is_synced": self.is_synced,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None
        }
