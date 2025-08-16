#!/usr/bin/env python3
"""
Script para migrar de SQLite a PostgreSQL
"""

import os
import sys
import asyncio
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def migrate_to_postgres():
    """Migrar datos de SQLite a PostgreSQL"""
    
    print("🔄 INICIANDO MIGRACIÓN DE SQLITE A POSTGRESQL")
    print("=" * 60)
    
    try:
        # 1. Verificar configuración
        print("1️⃣ Verificando configuración...")
        from core.config import settings
        
        # Verificar si tenemos DATABASE_URL de Railway
        railway_db_url = os.getenv("DATABASE_URL")
        if railway_db_url:
            print(f"   ✅ DATABASE_URL de Railway detectado")
            print(f"   🔗 URL: {railway_db_url[:50]}...")
        else:
            print("   ⚠️ No se detectó DATABASE_URL de Railway")
            print("   💡 Asegúrate de tener PostgreSQL configurado en Railway")
            return False
        
        # 2. Verificar SQLite local
        print("\n2️⃣ Verificando base de datos SQLite local...")
        sqlite_path = "./clickup_manager.db"
        if os.path.exists(sqlite_path):
            print(f"   ✅ Base de datos SQLite encontrada: {sqlite_path}")
            file_size = os.path.getsize(sqlite_path) / (1024 * 1024)  # MB
            print(f"   📊 Tamaño: {file_size:.2f} MB")
        else:
            print(f"   ❌ Base de datos SQLite no encontrada: {sqlite_path}")
            return False
        
        # 3. Conectar a SQLite
        print("\n3️⃣ Conectando a SQLite...")
        try:
            from core.database import engine as sqlite_engine
            # Crear engine temporal para SQLite
            import sqlalchemy as sa
            sqlite_engine_temp = sa.create_engine(
                f"sqlite:///{sqlite_path}",
                connect_args={"check_same_thread": False}
            )
            print("   ✅ Conexión a SQLite exitosa")
        except Exception as e:
            print(f"   ❌ Error conectando a SQLite: {e}")
            return False
        
        # 4. Conectar a PostgreSQL
        print("\n4️⃣ Conectando a PostgreSQL...")
        try:
            # Configurar PostgreSQL temporalmente
            os.environ["DATABASE_URL"] = railway_db_url
            
            from core.database import engine as postgres_engine
            print("   ✅ Conexión a PostgreSQL exitosa")
        except Exception as e:
            print(f"   ❌ Error conectando a PostgreSQL: {e}")
            return False
        
        # 5. Crear tablas en PostgreSQL
        print("\n5️⃣ Creando tablas en PostgreSQL...")
        try:
            from core.database import Base
            Base.metadata.create_all(bind=postgres_engine)
            print("   ✅ Tablas creadas en PostgreSQL")
        except Exception as e:
            print(f"   ❌ Error creando tablas: {e}")
            return False
        
        # 6. Migrar datos
        print("\n6️⃣ Migrando datos...")
        try:
            from sqlalchemy.orm import sessionmaker
            from models.task import Task
            from models.workspace import Workspace
            from models.user import User
            
            # Sesiones
            SQLiteSession = sessionmaker(bind=sqlite_engine_temp)
            PostgresSession = sessionmaker(bind=postgres_engine)
            
            sqlite_session = SQLiteSession()
            postgres_session = PostgresSession()
            
            # Migrar tareas
            print("   📋 Migrando tareas...")
            tasks = sqlite_session.query(Task).all()
            for task in tasks:
                # Crear nueva tarea en PostgreSQL
                new_task = Task(
                    clickup_id=task.clickup_id,
                    name=task.name,
                    description=task.description,
                    status=task.status,
                    priority=task.priority,
                    due_date=task.due_date,
                    start_date=task.start_date,
                    workspace_id=task.workspace_id,
                    list_id=task.list_id,
                    assignee_id=task.assignee_id,
                    creator_id=task.creator_id,
                    tags=task.tags,
                    custom_fields=task.custom_fields,
                    attachments=task.attachments,
                    comments=task.comments,
                    is_synced=task.is_synced,
                    last_sync=task.last_sync,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                )
                postgres_session.add(new_task)
            
            # Migrar workspaces
            print("   🏢 Migrando workspaces...")
            workspaces = sqlite_session.query(Workspace).all()
            for workspace in workspaces:
                new_workspace = Workspace(
                    clickup_id=workspace.clickup_id,
                    name=workspace.name,
                    description=workspace.description,
                    color=workspace.color,
                    private=workspace.private,
                    multiple_assignees=workspace.multiple_assignees,
                    settings=workspace.settings,
                    features=workspace.features,
                    is_synced=workspace.is_synced,
                    last_sync=workspace.last_sync,
                    created_at=workspace.created_at,
                    updated_at=workspace.updated_at
                )
                postgres_session.add(new_workspace)
            
            # Migrar usuarios
            print("   👥 Migrando usuarios...")
            users = sqlite_session.query(User).all()
            for user in users:
                new_user = User(
                    clickup_id=user.clickup_id,
                    username=user.username,
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    avatar=user.avatar,
                    role=user.role,
                    title=user.title,
                    active=user.active,
                    timezone=user.timezone,
                    language=user.language,
                    preferences=user.preferences,
                    workspaces=user.workspaces,
                    is_synced=user.is_synced,
                    last_sync=user.last_sync,
                    created_at=user.created_at,
                    updated_at=user.updated_at
                )
                postgres_session.add(new_user)
            
            # Commit de todos los cambios
            postgres_session.commit()
            print(f"   ✅ Datos migrados exitosamente:")
            print(f"      📋 Tareas: {len(tasks)}")
            print(f"      🏢 Workspaces: {len(workspaces)}")
            print(f"      👥 Usuarios: {len(users)}")
            
            # Cerrar sesiones
            sqlite_session.close()
            postgres_session.close()
            
        except Exception as e:
            print(f"   ❌ Error migrando datos: {e}")
            import traceback
            print(f"   📋 Traceback: {traceback.format_exc()}")
            return False
        
        # 7. Verificar migración
        print("\n7️⃣ Verificando migración...")
        try:
            postgres_session = PostgresSession()
            task_count = postgres_session.query(Task).count()
            workspace_count = postgres_session.query(Workspace).count()
            user_count = postgres_session.query(User).count()
            
            print(f"   ✅ Verificación exitosa:")
            print(f"      📋 Tareas en PostgreSQL: {task_count}")
            print(f"      🏢 Workspaces en PostgreSQL: {workspace_count}")
            print(f"      👥 Usuarios en PostgreSQL: {user_count}")
            
            postgres_session.close()
            
        except Exception as e:
            print(f"   ❌ Error verificando migración: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE!")
        print("\n📋 Resumen:")
        print("   ✅ Base de datos SQLite verificada")
        print("   ✅ Conexión a PostgreSQL establecida")
        print("   ✅ Tablas creadas en PostgreSQL")
        print("   ✅ Datos migrados completamente")
        print("   ✅ Verificación exitosa")
        print("\n🚀 Tu aplicación ahora usa PostgreSQL en Railway!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error general en la migración: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    # Ejecutar migración
    success = asyncio.run(migrate_to_postgres())
    
    if success:
        print("\n✅ Migración completada exitosamente")
        sys.exit(0)
    else:
        print("\n❌ La migración falló")
        sys.exit(1)
