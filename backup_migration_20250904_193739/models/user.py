"""
Modelo de datos para usuarios de ClickUp
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from core.database import Base

class User(Base):
    """Modelo de usuario de ClickUp"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    clickup_id = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    
    # Informacion del perfil
    avatar = Column(String(500), nullable=True)  # URL del avatar
    title = Column(String(255), nullable=True)  # Titulo/cargo
    
    # Autenticacion y seguridad
    password_hash = Column(String(255), nullable=True)  # Hash de contrasena
    is_active = Column(Boolean, default=True)  # Usuario activo
    role = Column(String(50), default="user")  # admin, manager, user, viewer
    clickup_role = Column(String(100), nullable=True)  # Rol especifico en ClickUp
    
    # API Keys
    api_key = Column(String(255), nullable=True, unique=True)
    api_key_description = Column(String(255), nullable=True)
    api_key_active = Column(Boolean, default=False)
    api_key_created_at = Column(DateTime, nullable=True)
    
    # Informacion de contacto para notificaciones
    phone = Column(String(20), nullable=True)
    telegram_id = Column(String(100), nullable=True)
    
    # Configuracion
    active = Column(Boolean, default=True)  # Para compatibilidad con ClickUp
    timezone = Column(String(100), nullable=True)
    language = Column(String(10), nullable=True, default="en")
    
    # Fechas
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Metadatos
    preferences = Column(JSON, nullable=True)  # Preferencias del usuario
    workspaces = Column(JSON, nullable=True)  # Workspaces a los que pertenece
    
    # Estado de sincronizacion
    is_synced = Column(Boolean, default=False)
    last_sync = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            "id": self.id,
            "clickup_id": self.clickup_id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "avatar": self.avatar,
            "role": self.role,
            "title": self.title,
            "active": self.active,
            "timezone": self.timezone,
            "language": self.language,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "preferences": self.preferences,
            "workspaces": self.workspaces,
            "is_synced": self.is_synced,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None
        }
    
    @property
    def full_name(self):
        """Get nombre completo"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username
