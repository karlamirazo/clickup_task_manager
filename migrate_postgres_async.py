#!/usr/bin/env python3
"""
Script de migración de SQLite a PostgreSQL usando asyncpg
"""

import os
import sys
import sqlite3
import json
import asyncio
from datetime import datetime

async def test_postgres_connection():
    """Probar conexión a PostgreSQL usando asyncpg"""
    try:
        import asyncpg
        
        print("🔍 Probando conexión a PostgreSQL con asyncpg...")
        
        # Conectar a PostgreSQL
        conn = await asyncpg.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            port="5432"
        )
        
        print("✅ Conexión exitosa a PostgreSQL")
        
        # Verificar la versión
        version = await conn.fetchval("SELECT version();")
        print(f"📊 Versión de PostgreSQL: {version}")
        
        # Listar bases de datos
        databases = await conn.fetch("SELECT datname FROM pg_database;")
        print("🗄️ Bases de datos disponibles:")
        for db in databases:
            print(f"   - {db['datname']}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        print(f"   Tipo de error: {type(e).__name__}")
        return False

async def create_database():
    """Crear base de datos PostgreSQL si no existe"""
    try:
        import asyncpg
        
        print("\n🔍 Creando base de datos...")
        
        # Conectar a postgres (base de datos por defecto)
        conn = await asyncpg.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            port="5432"
        )
        
        # Verificar si la base de datos existe
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname=$1", 
            "clickup_manager"
        )
        
        if not exists:
            await conn.execute("CREATE DATABASE clickup_manager")
            print("✅ Base de datos 'clickup_manager' creada")
        else:
            print("✅ Base de datos 'clickup_manager' ya existe")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creando base de datos: {e}")
        return False

def get_sqlite_data():
    """Obtener todos los datos de SQLite"""
    try:
        # Buscar archivos de base de datos SQLite
        sqlite_files = [
            "clickup_manager.db",
            "clickup_project_manager.db",
            "clickup_manager_backup.db",
            "clickup_manager_backup_20250809_210854.db"
        ]
        
        sqlite_file = None
        for file in sqlite_files:
            if os.path.exists(file):
                sqlite_file = file
                break
        
        if not sqlite_file:
            print("❌ No se encontró archivo de base de datos SQLite")
            return None
        
        print(f"📁 Usando archivo SQLite: {sqlite_file}")
        
        # Conectar a SQLite
        conn = sqlite3.connect(sqlite_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Obtener lista de tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]
        
        data = {}
        for table in tables:
            print(f"📊 Leyendo tabla: {table}")
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            # Convertir filas a diccionarios
            table_data = []
            for row in rows:
                row_dict = {}
                for key in row.keys():
                    value = row[key]
                    # Convertir tipos de datos específicos
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    elif isinstance(value, str) and value.startswith('{') and value.endswith('}'):
                        try:
                            value = json.loads(value)
                        except:
                            pass
                    row_dict[key] = value
                table_data.append(row_dict)
            
            data[table] = table_data
            print(f"   ✅ {len(table_data)} registros leídos")
        
        cursor.close()
        conn.close()
        return data
        
    except Exception as e:
        print(f"❌ Error obteniendo datos de SQLite: {e}")
        return None

async def create_tables():
    """Crear tablas en PostgreSQL"""
    try:
        import asyncpg
        
        print("\n🔍 Creando tablas en PostgreSQL...")
        
        conn = await asyncpg.connect(
            host="localhost",
            database="clickup_manager",
            user="postgres",
            password="postgres",
            port="5432"
        )
        
        # Crear tabla de tareas (la más importante)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                clickup_id VARCHAR(255) UNIQUE,
                name VARCHAR(500) NOT NULL,
                description TEXT,
                status VARCHAR(100),
                priority INTEGER DEFAULT 3,
                due_date TIMESTAMP,
                start_date TIMESTAMP,
                workspace_id VARCHAR(255),
                list_id VARCHAR(255),
                assignee_id VARCHAR(255),
                creator_id VARCHAR(255),
                tags JSONB,
                custom_fields JSONB,
                is_synced BOOLEAN DEFAULT FALSE,
                last_sync TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Crear tabla de usuarios
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                clickup_id VARCHAR(255) UNIQUE,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE,
                username VARCHAR(255),
                avatar VARCHAR(500),
                workspaces JSONB,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Crear tabla de workspaces
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS workspaces (
                id SERIAL PRIMARY KEY,
                clickup_id VARCHAR(255) UNIQUE,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                color VARCHAR(7),
                avatar VARCHAR(500),
                private BOOLEAN DEFAULT FALSE,
                status VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await conn.close()
        print("✅ Tablas de PostgreSQL creadas correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        return False

async def migrate_data(sqlite_data):
    """Migrar datos de SQLite a PostgreSQL"""
    try:
        import asyncpg
        
        print("\n🔍 Migrando datos a PostgreSQL...")
        
        conn = await asyncpg.connect(
            host="localhost",
            database="clickup_manager",
            user="postgres",
            password="postgres",
            port="5432"
        )
        
        # Migrar tareas (la más importante)
        if 'tasks' in sqlite_data:
            print("📋 Migrando tareas...")
            for task in sqlite_data['tasks']:
                try:
                    await conn.execute("""
                        INSERT INTO tasks (clickup_id, name, description, status, priority, due_date, start_date, 
                                        workspace_id, list_id, assignee_id, creator_id, tags, custom_fields, 
                                        is_synced, last_sync, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                        ON CONFLICT (clickup_id) DO UPDATE SET
                            name = EXCLUDED.name,
                            description = EXCLUDED.description,
                            status = EXCLUDED.status,
                            priority = EXCLUDED.priority,
                            due_date = EXCLUDED.due_date,
                            start_date = EXCLUDED.start_date,
                            workspace_id = EXCLUDED.workspace_id,
                            list_id = EXCLUDED.list_id,
                            assignee_id = EXCLUDED.assignee_id,
                            creator_id = EXCLUDED.creator_id,
                            tags = EXCLUDED.tags,
                            custom_fields = EXCLUDED.custom_fields,
                            is_synced = EXCLUDED.is_synced,
                            last_sync = EXCLUDED.last_sync,
                            updated_at = CURRENT_TIMESTAMP
                    """, 
                        task.get('clickup_id'),
                        task.get('name'),
                        task.get('description'),
                        task.get('status'),
                        task.get('priority'),
                        task.get('due_date'),
                        task.get('start_date'),
                        task.get('workspace_id'),
                        task.get('list_id'),
                        task.get('assignee_id'),
                        task.get('creator_id'),
                        json.dumps(task.get('tags', [])) if task.get('tags') else None,
                        json.dumps(task.get('custom_fields', {})) if task.get('custom_fields') else None,
                        task.get('is_synced', False),
                        task.get('last_sync'),
                        task.get('created_at'),
                        task.get('updated_at')
                    )
                except Exception as e:
                    print(f"   ⚠️ Error migrando tarea {task.get('clickup_id', 'unknown')}: {e}")
                    continue
        
        await conn.close()
        print("✅ Datos migrados correctamente a PostgreSQL")
        return True
        
    except Exception as e:
        print(f"❌ Error migrando datos: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_config():
    """Actualizar configuración para usar PostgreSQL"""
    try:
        # Crear archivo .env con configuración de PostgreSQL
        env_content = """# Configuración de PostgreSQL
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/clickup_manager

# Configuración de la aplicación
DEBUG=True
HOST=0.0.0.0
PORT=3000

# Configuración de ClickUp API
CLICKUP_API_TOKEN=pk_156221125_XB0BCWQCZ1ML1W7S88M0RCHX6WIZFY7O

# Configuración de seguridad
JWT_SECRET_KEY=your-secret-key-here-change-in-production
SECRET_KEY=your-secret-key-here

# Configuración de Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=karlamirazo@gmail.com
SMTP_PASSWORD=qirksuzfkjotjicz
SMTP_FROM=karlamirazo@gmail.com
SMTP_USE_TLS=True
SMTP_USE_SSL=False

# Configuración de SMS
SMS_ENABLED=True
TWILIO_ACCOUNT_SID=AC1eabd3bf2f333aa35d1d9a5839982d0c
TWILIO_AUTH_TOKEN=d6e1c52f782f7ed8b6c5134541621e5d
TWILIO_SMS_FROM=+19063230356
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Archivo .env creado con configuración de PostgreSQL")
        return True
        
    except Exception as e:
        print(f"❌ Error creando archivo .env: {e}")
        return False

async def main():
    """Función principal de migración"""
    print("🚀 Iniciando migración de SQLite a PostgreSQL usando asyncpg...")
    print("=" * 60)
    
    # Paso 1: Verificar conexión a PostgreSQL
    if not await test_postgres_connection():
        print("\n💡 Soluciones posibles:")
        print("1. Verificar que PostgreSQL esté ejecutándose")
        print("2. Verificar credenciales (usuario: postgres, contraseña: postgres)")
        print("3. Verificar que el puerto 5432 esté disponible")
        return
    
    # Paso 2: Crear base de datos
    if not await create_database():
        return
    
    # Paso 3: Crear tablas
    if not await create_tables():
        return
    
    # Paso 4: Obtener datos de SQLite
    sqlite_data = get_sqlite_data()
    if not sqlite_data:
        return
    
    # Paso 5: Migrar datos
    if not await migrate_data(sqlite_data):
        return
    
    # Paso 6: Actualizar configuración
    if not update_config():
        return
    
    print("\n🎉 ¡Migración completada exitosamente!")
    print("=" * 60)
    print("📋 Pasos siguientes:")
    print("1. Verifica que la base de datos esté funcionando")
    print("2. Reinicia el servidor: python main.py")
    print("3. Prueba la funcionalidad de campos personalizados")

if __name__ == "__main__":
    asyncio.run(main())


