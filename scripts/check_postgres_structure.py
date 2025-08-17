#!/usr/bin/env python3
"""
Script para verificar la estructura de la tabla tasks en PostgreSQL de Railway
"""

import os
import psycopg2
from datetime import datetime

def check_postgres_structure():
    """Verificar la estructura de la tabla tasks en PostgreSQL"""
    
    # Obtener DATABASE_URL de Railway
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL no está configurado")
        return
    
    print(f"🔍 Verificando estructura de tabla tasks en PostgreSQL...")
    print(f"📊 URL de base de datos: {database_url[:50]}...")
    
    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Verificar si la tabla tasks existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'tasks'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        print(f"📋 Tabla 'tasks' existe: {'✅ SÍ' if table_exists else '❌ NO'}")
        
        if table_exists:
            # Obtener estructura de la tabla
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'tasks' 
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print(f"\n🏗️ Estructura actual de la tabla 'tasks':")
            print(f"{'Columna':<20} {'Tipo':<15} {'Nullable':<10} {'Default'}")
            print("-" * 60)
            
            for col in columns:
                col_name, data_type, nullable, default = col
                print(f"{col_name:<20} {data_type:<15} {nullable:<10} {default or 'N/A'}")
            
            # Verificar columnas específicas que necesitamos
            required_columns = [
                'id', 'clickup_id', 'name', 'description', 'status', 'priority',
                'due_date', 'start_date', 'created_at', 'updated_at',
                'workspace_id', 'list_id', 'assignee_id', 'creator_id',
                'tags', 'custom_fields', 'attachments', 'comments',
                'is_synced', 'last_sync'
            ]
            
            existing_columns = [col[0] for col in columns]
            missing_columns = [col for col in required_columns if col not in existing_columns]
            
            print(f"\n🔍 Análisis de columnas:")
            print(f"✅ Columnas existentes: {len(existing_columns)}")
            print(f"❌ Columnas faltantes: {len(missing_columns)}")
            
            if missing_columns:
                print(f"📝 Columnas que faltan: {', '.join(missing_columns)}")
            else:
                print(f"🎉 Todas las columnas necesarias están presentes!")
        
        # Verificar si hay datos en la tabla
        if table_exists:
            cursor.execute("SELECT COUNT(*) FROM tasks;")
            count = cursor.fetchone()[0]
            print(f"\n📊 Datos en la tabla: {count} registros")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    check_postgres_structure()
