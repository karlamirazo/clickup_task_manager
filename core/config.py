"""
Configuracion del proyecto ClickUp Project Manager
"""

import os
from typing import List
from pydantic_settings import BaseSettings
# from dotenv import load_dotenv
# load_dotenv()

class Settings(BaseSettings):
    """Configuraciones de la aplicacion"""
    
    # Configuracion de la aplicacion
    APP_NAME: str = "ClickUp Project Manager"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))  # Puerto principal con Waitress
    
    # Configuracion de ClickUp API
    CLICKUP_API_TOKEN: str = os.getenv("CLICKUP_API_TOKEN", "pk_156221125_GI1OKEUEW57LFWA8RYWHGIC54TL6XVVZ")
    CLICKUP_WEBHOOK_SECRET: str = os.getenv("CLICKUP_WEBHOOK_SECRET", "")
    
    # Configuracion de autenticacion
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 horas
    CLICKUP_API_BASE_URL: str = "https://api.clickup.com/api/v2"
    
    # Configuracion de base de datos - POSTGRESQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:admin123@localhost:5432/clickup_project_manager")
    # Para PostgreSQL: postgresql://user:password@localhost/clickup_project_manager
    # Railway automaticamente proporciona DATABASE_URL para PostgreSQL
    
    # Configuracion especifica de PostgreSQL
    POSTGRES_ENABLED: bool = os.getenv("POSTGRES_ENABLED", "True").lower() == "true"
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "clickup_project_manager")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "admin123")
    
    # Configuracion de Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Configuracion de CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:8000",  # Puerto unificado principal
        "http://127.0.0.1:8000",  # Puerto unificado principal
        "http://localhost:8001",  # Puerto alternativo
        "http://127.0.0.1:8001",  # Puerto alternativo
        "http://localhost:3000",   # Puerto alternativo
        "http://127.0.0.1:3000",  # Puerto alternativo
        "https://clickuptaskmanager-production.up.railway.app",
        "https://*.up.railway.app",
        "*"  # Temporal para debugging - remover en produccion
    ]
    
    # Configuracion de seguridad
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Configuracion de logs
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    
    # Configuracion de automatizacion
    AUTOMATION_ENABLED: bool = os.getenv("AUTOMATION_ENABLED", "True").lower() == "true"
    AUTOMATION_INTERVAL: int = int(os.getenv("AUTOMATION_INTERVAL", "300"))  # 5 minutos
    
    # Configuracion de reportes
    REPORTS_ENABLED: bool = os.getenv("REPORTS_ENABLED", "True").lower() == "true"
    REPORTS_STORAGE_PATH: str = os.getenv("REPORTS_STORAGE_PATH", "data/reports")
    
    # Configuracion de integraciones
    INTEGRATIONS_ENABLED: bool = os.getenv("INTEGRATIONS_ENABLED", "True").lower() == "true"

    # Configuracion de Email (SMTP)
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "karlamirazo@gmail.com")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "qirksuzfkjotjicz")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "karlamirazo@gmail.com")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "True").lower() == "true"
    SMTP_USE_SSL: bool = os.getenv("SMTP_USE_SSL", "False").lower() == "true"

    # Configuracion de Telegram Bot (DESHABILITADO)
    TELEGRAM_ENABLED: bool = os.getenv("TELEGRAM_ENABLED", "False").lower() == "true"
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")  # Chat ID por defecto (opcional)

    # Configuracion de SMS (Twilio) - ELIMINADO
    SMS_ENABLED: bool = os.getenv("SMS_ENABLED", "False").lower() == "true"
    # TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "") # Eliminado
    # TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "") # Eliminado
    # TWILIO_SMS_FROM: str = os.getenv("TWILIO_SMS_FROM", "") # Eliminado

    # Campos personalizados de ClickUp para obtener destinatarios desde tareas
    # Coma-separados; pueden ser nombres de campo o IDs de campo
    TASK_EMAIL_FIELDS: str = os.getenv("TASK_EMAIL_FIELDS", "Email")
    TASK_TELEGRAM_FIELDS: str = os.getenv("TASK_TELEGRAM_FIELDS", "")  # CAMPO ELIMINADO - Telegram deshabilitado
    TASK_SMS_FIELDS: str = os.getenv("TASK_SMS_FIELDS", "")  # Campo eliminado - SMS deshabilitado
    
    # Configuracion del motor de busqueda RAG
    SEARCH_ENGINE_ENABLED: bool = os.getenv("SEARCH_ENGINE_ENABLED", "True").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
