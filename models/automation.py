"""
Modelo de datos para automatizaciones
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from core.database import Base

class Automation(Base):
    """Modelo de automatización"""
    
    __tablename__ = "automations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuración de la automatización
    trigger_type = Column(String(100), nullable=False)  # task_created, task_updated, due_date, etc.
    trigger_conditions = Column(JSON, nullable=True)  # Condiciones del trigger
    
    # Acciones a ejecutar
    actions = Column(JSON, nullable=False)  # Lista de acciones a ejecutar
    
    # Estado
    active = Column(Boolean, default=True)
    enabled = Column(Boolean, default=True)
    
    # Fechas
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_executed = Column(DateTime, nullable=True)
    
    # Relaciones
    workspace_id = Column(String(255), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    
    # Metadatos
    execution_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    
    # Relaciones con otros modelos
    task = relationship("Task", back_populates="automation_rules")
    
    def __repr__(self):
        return f"<Automation(id={self.id}, name='{self.name}', trigger_type='{self.trigger_type}')>"
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "trigger_type": self.trigger_type,
            "trigger_conditions": self.trigger_conditions,
            "actions": self.actions,
            "active": self.active,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_executed": self.last_executed.isoformat() if self.last_executed else None,
            "workspace_id": self.workspace_id,
            "task_id": self.task_id,
            "execution_count": self.execution_count,
            "error_count": self.error_count,
            "last_error": self.last_error
        }
