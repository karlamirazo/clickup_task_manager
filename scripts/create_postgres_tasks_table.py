#!/usr/bin/env python3
"""
Script para crear la tabla tasks con la estructura correcta en PostgreSQL de Railway
"""

import os
import psycopg2
from datetime import datetime

def create_postgres_tasks_table():
    """Crear la tabla tasks con la estructura correcta en PostgreSQL"""
    
    # Obtener DATABASE_URL de Railway
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL no está configurado")
        return
    
    print(f"🔨 Creando tabla tasks en PostgreSQL...")
    print(f"📊 URL de base de datos: {database_url[:50]}...")
    
    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Verificar si la tabla ya existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'tasks'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print(f"⚠️ La tabla 'tasks' ya existe. ¿Deseas recrearla? (y/N): ", end="")
            response = input().strip().lower()
            if response != 'y':
                print("❌ Operación cancelada")
                return
            
            # Eliminar tabla existente
            print(f"🗑️ Eliminando tabla existente...")
            cursor.execute("DROP TABLE IF EXISTS tasks CASCADE;")
            conn.commit()
            print(f"✅ Tabla eliminada")
        
        # Crear tabla con estructura correcta
        print(f"🏗️ Creando tabla tasks...")
        
        create_table_sql = """
        CREATE TABLE tasks (
            id SERIAL PRIMARY KEY,
            clickup_id VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(500) NOT NULL,
            description TEXT,
            status VARCHAR(100) NOT NULL DEFAULT 'to_do',
            priority INTEGER DEFAULT 3,
            due_date TIMESTAMP,
            start_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            workspace_id VARCHAR(255) NOT NULL,
            list_id VARCHAR(255) NOT NULL,
            assignee_id VARCHAR(255),
            creator_id VARCHAR(255) DEFAULT 'system',
            tags JSONB,
            custom_fields JSONB,
            attachments JSONB,
            comments JSONB,
            is_synced BOOLEAN DEFAULT FALSE,
            last_sync TIMESTAMP
        );
        """
        
        cursor.execute(create_table_sql)
        
        # Crear índices para mejor rendimiento
        print(f"📊 Creando índices...")
        cursor.execute("CREATE INDEX idx_tasks_clickup_id ON tasks(clickup_id);")
        cursor.execute("CREATE INDEX idx_tasks_workspace_id ON tasks(workspace_id);")
        cursor.execute("CREATE INDEX idx_tasks_list_id ON tasks(list_id);")
        cursor.execute("CREATE INDEX idx_tasks_status ON tasks(status);")
        cursor.execute("CREATE INDEX idx_tasks_priority ON tasks(priority);")
        cursor.execute("CREATE INDEX idx_tasks_is_synced ON tasks(is_synced);")
        
        # Commit de la transacción
        conn.commit()
        
        print(f"✅ Tabla 'tasks' creada exitosamente!")
        print(f"✅ Índices creados para mejor rendimiento")
        
        # Verificar la estructura creada
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'tasks' 
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"\n🏗️ Estructura de la tabla 'tasks' creada:")
        print(f"{'Columna':<20} {'Tipo':<15} {'Nullable':<10} {'Default'}")
        print("-" * 60)
        
        for col in columns:
            col_name, data_type, nullable, default = col
            print(f"{col_name:<20} {data_type:<15} {nullable:<10} {default or 'N/A'}")
        
        cursor.close()
        conn.close()
        
        print(f"\n🎉 ¡Tabla 'tasks' creada exitosamente en PostgreSQL!")
        
    except Exception as e:
        print(f"❌ Error creando tabla: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    create_postgres_tasks_table()
