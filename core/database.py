"""
Configuración de la base de datos
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from core.config import settings
import os

def get_database_url():
    """Obtener URL de base de datos con fallback inteligente"""
    
    # Si Railway proporciona DATABASE_URL (PostgreSQL), usarlo
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")
    
    # Si no, usar SQLite local
    return settings.DATABASE_URL

# Crear engine de base de datos
database_url = get_database_url()

if database_url.startswith("sqlite"):
    # Configuración para SQLite
    engine = create_engine(
        database_url,
        connect_args={
            "check_same_thread": False,
            "timeout": 30
        },
        poolclass=StaticPool,
        echo=False,  # Desactivar logs SQL para evitar problemas de codificación
    )
    print("🗄️ Usando base de datos SQLite local")
else:
    # Configuración para PostgreSQL
    engine = create_engine(
        database_url,
        echo=False,  # Desactivar logs SQL para evitar problemas de codificación
        pool_pre_ping=True,  # Verificar conexión antes de usar
        pool_recycle=300,    # Reciclar conexiones cada 5 minutos
    )
    print("🗄️ Usando base de datos PostgreSQL")
    print(f"🔗 Host: {os.getenv('PGHOST', 'N/A')}")
    print(f"📊 Base de datos: {os.getenv('PGDATABASE', 'N/A')}")

# Crear sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

def get_db():
    """Obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Inicializar base de datos"""
    try:
        from models import task, workspace, user, automation, report, integration
        
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print(f"⚠️  Error inicializando base de datos: {e}")
        # No lanzar excepción para evitar que el servidor falle
        pass
