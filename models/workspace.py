"""
Modelo de datos para espacios de trabajo de ClickUp
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from core.database import Base

class Workspace(Base):
    """Modelo de espacio de trabajo de ClickUp"""
    
    __tablename__ = "workspaces"
    
    id = Column(Integer, primary_key=True, index=True)
    clickup_id = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuración
    color = Column(String(7), nullable=True)  # Código de color hex
    private = Column(Boolean, default=False)
    multiple_assignees = Column(Boolean, default=True)
    
    # Fechas
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadatos
    settings = Column(JSON, nullable=True)  # Configuraciones del workspace
    features = Column(JSON, nullable=True)  # Características habilitadas
    
    # Estado de sincronización
    is_synced = Column(Boolean, default=False)
    last_sync = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Workspace(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            "id": self.id,
            "clickup_id": self.clickup_id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "private": self.private,
            "multiple_assignees": self.multiple_assignees,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "settings": self.settings,
            "features": self.features,
            "is_synced": self.is_synced,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None
        }
