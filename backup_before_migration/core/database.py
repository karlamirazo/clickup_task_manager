"""
Database configuration for ClickUp Project Manager
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from core.config import settings
import os
from urllib.parse import urlparse

def get_database_url():
    """Get database URL with intelligent fallback"""
    
    # Use PostgreSQL with psycopg2 driver (synchronous)
    if os.getenv("DATABASE_URL"):
        # Ensure we're using psycopg2 driver
        db_url = os.getenv("DATABASE_URL")
        if db_url.startswith("postgresql://") and "psycopg2" not in db_url:
            db_url = db_url.replace("postgresql://", "postgresql+psycopg2://")
        return db_url
    
    # Default PostgreSQL connection with psycopg2
    return "postgresql+psycopg2://postgres:admin123@localhost:5432/clickup_project_manager"

# Create database engine
database_url = get_database_url()

if database_url.startswith("sqlite"):
    # SQLite configuration
    engine = create_engine(
        database_url,
        connect_args={
            "check_same_thread": False,
            "timeout": 30
        },
        poolclass=StaticPool,
        echo=False,  # Disable SQL logs to avoid encoding issues
    )
    print("🗄️ Using local SQLite database")
else:
    # PostgreSQL configuration with psycopg2 driver (synchronous)
    engine = create_engine(
        database_url,
        echo=False,  # Disable SQL logs to avoid encoding issues
        pool_pre_ping=True,  # Verify connection before using
        pool_recycle=300,    # Recycle connections every 5 minutes
        future=True,  # Enable SQLAlchemy 2.0 features
        connect_args={
            "client_encoding": "utf8",
            "options": "-c timezone=UTC -c client_min_messages=warning"
        }
    )
    print("🗄️ Using PostgreSQL database with psycopg2 driver")
    
    # Parse PostgreSQL URL to show useful information
    try:
        parsed_url = urlparse(database_url)
        print(f"🔗 Host: {parsed_url.hostname}")
        print(f"📊 Database: {parsed_url.path[1:] if parsed_url.path else 'N/A'}")
        print(f"👤 User: {parsed_url.username}")
        print(f"🔌 Port: {parsed_url.port or 5432}")
    except Exception as e:
        print(f"🔗 URL: {database_url[:50]}...")
        print(f"⚠️ Error parsing URL: {e}")

# Create database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session (synchronous)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Base for models
Base = declarative_base()

def init_db():
    """Initialize database"""
    try:
        # Import all models from the models package
        from models import Task, Workspace, User, Automation, Report, Integration, NotificationLog
        
        # Create all tables (synchronous for both SQLite and PostgreSQL)
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully")
        
        # Verify that notification_logs table was created
        try:
            with engine.connect() as conn:
                from sqlalchemy import text
                result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'notification_logs'"))
                if result.fetchone():
                    print("✅ notification_logs table created successfully")
                else:
                    print("❌ notification_logs table not found")
        except Exception as e:
            print(f"⚠️ Error verifying table creation: {e}")
            
    except Exception as e:
        print(f"⚠️  Error initializing database: {e}")
        # Don't raise exception to avoid server failure
        pass
