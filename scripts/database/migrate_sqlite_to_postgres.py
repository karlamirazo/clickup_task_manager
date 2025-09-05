#!/usr/bin/env python3
"""
Script para migrar datos desde SQLite local a PostgreSQL de Railway
"""

import os
import sqlite3
import psycopg2
from datetime import datetime
import json

def migrate_sqlite_to_postgres():
    """Migrar datos desde SQLite local a PostgreSQL de Railway"""
    
    # Verificar que exista la base de datos SQLite local
    sqlite_db_path = "clickup_task_manager.db"
    if not os.path.exists(sqlite_db_path):
        print(f"â�Œ Base de datos SQLite not found: {sqlite_db_path}")
        return
    
    # Get DATABASE_URL de Railway
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("â�Œ DATABASE_URL no esta configured")
        return
    
    print(f"ğŸ”„ Iniciando migracion de SQLite a PostgreSQL...")
    print(f"ğŸ“� SQLite: {sqlite_db_path}")
    print(f"ğŸ“Š PostgreSQL: {database_url[:50]}...")
    
    try:
        # Conectar a SQLite
        sqlite_conn = sqlite3.connect(sqlite_db_path)
        sqlite_cursor = sqlite_conn.cursor()
        
        # Conectar a PostgreSQL
        postgres_conn = psycopg2.connect(database_url)
        postgres_cursor = postgres_conn.cursor()
        
        # Verificar que la tabla tasks existe en PostgreSQL
        postgres_cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'tasks'
            );
        """)
        
        if not postgres_cursor.fetchone()[0]:
            print(f"â�Œ La tabla 'tasks' no existe en PostgreSQL. Ejecuta primero create_postgres_tasks_table.py")
            return
        
        # Get datos de SQLite
        print(f"ğŸ“¥ Obteniendo datos de SQLite...")
        sqlite_cursor.execute("SELECT * FROM tasks;")
        sqlite_tasks = sqlite_cursor.fetchall()
        
        print(f"ğŸ“Š Encontradas {len(sqlite_tasks)} tareas en SQLite")
        
        # Get estructura de columnas de SQLite
        sqlite_cursor.execute("PRAGMA table_info(tasks);")
        sqlite_columns = [col[1] for col in sqlite_cursor.fetchall()]
        print(f"ğŸ�—ï¸� Columnas en SQLite: {', '.join(sqlite_columns)}")
        
        # Get estructura de columnas de PostgreSQL
        postgres_cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'tasks' 
            ORDER BY ordinal_position;
        """)
        postgres_columns = [col[0] for col in postgres_cursor.fetchall()]
        print(f"ğŸ�—ï¸� Columnas en PostgreSQL: {', '.join(postgres_columns)}")
        
        # Migrar cada tarea
        migrated_count = 0
        error_count = 0
        
        for i, sqlite_task in enumerate(sqlite_tasks):
            try:
                # Create diccionario con datos de SQLite
                task_dict = dict(zip(sqlite_columns, sqlite_task))
                
                # Preparar datos para PostgreSQL
                postgres_data = {
                    'clickup_id': task_dict.get('clickup_id', f"migrated_{i}"),
                    'name': task_dict.get('name', 'Tarea migrada'),
                    'description': task_dict.get('description'),
                    'status': task_dict.get('status', 'to_do'),
                    'priority': task_dict.get('priority', 3),
                    'due_date': task_dict.get('due_date'),
                    'start_date': task_dict.get('start_date'),
                    'workspace_id': task_dict.get('workspace_id', 'unknown'),
                    'list_id': task_dict.get('list_id', 'unknown'),
                    'assignee_id': task_dict.get('assignee_id'),
                    'creator_id': task_dict.get('creator_id', 'system'),
                    'tags': json.dumps(task_dict.get('tags', [])) if task_dict.get('tags') else None,
                    'custom_fields': json.dumps(task_dict.get('custom_fields', {})) if task_dict.get('custom_fields') else None,
                    'attachments': json.dumps(task_dict.get('attachments', [])) if task_dict.get('attachments') else None,
                    'comments': json.dumps(task_dict.get('comments', [])) if task_dict.get('comments') else None,
                    'is_synced': task_dict.get('is_synced', True),
                    'last_sync': task_dict.get('last_sync') or datetime.now()
                }
                
                # Insertar en PostgreSQL
                columns = list(postgres_data.keys())
                placeholders = ', '.join([f'%({col})s' for col in columns])
                insert_sql = f"INSERT INTO tasks ({', '.join(columns)}) VALUES ({placeholders});"
                
                postgres_cursor.execute(insert_sql, postgres_data)
                migrated_count += 1
                
                if (i + 1) % 10 == 0:
                    print(f"   âœ… Migradas {i + 1}/{len(sqlite_tasks)} tareas...")
                
            except Exception as e:
                print(f"   â�Œ Error migrando tarea {i + 1}: {e}")
                error_count += 1
                continue
        
        # Commit de la transaccion
        postgres_conn.commit()
        
        print(f"\nğŸ�‰ Migracion completada!")
        print(f"âœ… Tareas migradas exitosamente: {migrated_count}")
        print(f"â�Œ Errores durante migracion: {error_count}")
        print(f"ğŸ“Š Total procesadas: {len(sqlite_tasks)}")
        
        # Verificar datos en PostgreSQL
        postgres_cursor.execute("SELECT COUNT(*) FROM tasks;")
        postgres_count = postgres_cursor.fetchone()[0]
        print(f"ğŸ“Š Total tareas en PostgreSQL: {postgres_count}")
        
        # Cerrar conexiones
        sqlite_cursor.close()
        sqlite_conn.close()
        postgres_cursor.close()
        postgres_conn.close()
        
        print(f"\nğŸ�‰ Â¡Migracion completada exitosamente!")
        
    except Exception as e:
        print(f"â�Œ Error durante migracion: {e}")
        import traceback
        print(f"ğŸ”� Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    migrate_sqlite_to_postgres()
