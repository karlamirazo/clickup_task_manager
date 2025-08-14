"""
Modelo de datos para integraciones
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from core.database import Base

class Integration(Base):
    """Modelo de integración"""
    
    __tablename__ = "integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuración de la integración
    integration_type = Column(String(100), nullable=False)  # crm, database, productivity, etc.
    provider = Column(String(100), nullable=False)  # salesforce, hubspot, postgresql, etc.
    
    # Configuración de conexión
    config = Column(JSON, nullable=False)  # Configuración de la integración
    credentials = Column(JSON, nullable=True)  # Credenciales (encriptadas)
    
    # Estado
    active = Column(Boolean, default=True)
    enabled = Column(Boolean, default=True)
    connected = Column(Boolean, default=False)
    
    # Fechas
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync = Column(DateTime, nullable=True)
    
    # Metadatos
    workspace_id = Column(String(255), nullable=False)
    created_by = Column(String(255), nullable=False)
    
    # Estadísticas
    sync_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    
    # Configuración de sincronización
    sync_interval = Column(Integer, default=3600)  # Intervalo en segundos
    auto_sync = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Integration(id={self.id}, name='{self.name}', type='{self.integration_type}')>"
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "integration_type": self.integration_type,
            "provider": self.provider,
            "config": self.config,
            "credentials": self.credentials,
            "active": self.active,
            "enabled": self.enabled,
            "connected": self.connected,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "workspace_id": self.workspace_id,
            "created_by": self.created_by,
            "sync_count": self.sync_count,
            "error_count": self.error_count,
            "last_error": self.last_error,
            "sync_interval": self.sync_interval,
            "auto_sync": self.auto_sync
        }
