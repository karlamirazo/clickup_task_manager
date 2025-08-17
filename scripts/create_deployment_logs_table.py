#!/usr/bin/env python3
"""
Script para crear la tabla deployment_logs en PostgreSQL
Esta tabla almacenará el historial completo de problemas y soluciones de deployment
"""

import asyncio
import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./clickup_tasks.db")

async def create_deployment_logs_table():
    """Crear la tabla deployment_logs en PostgreSQL"""
    
    print("🚀 Creando tabla deployment_logs...")
    engine = None
    
    try:
        # Crear engine asíncrono
        if DATABASE_URL.startswith("postgresql"):
            # Convertir URL de PostgreSQL a formato asyncio
            async_database_url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
            engine = create_async_engine(async_database_url, echo=True)
            print("✅ Conectando a PostgreSQL...")
        else:
            print("⚠️ No se detectó PostgreSQL, usando SQLite para desarrollo local")
            engine = create_async_engine("sqlite+aiosqlite:///./clickup_tasks.db", echo=True)
            print("✅ Conectando a SQLite...")
        
        async with engine.begin() as conn:
            # Crear tabla deployment_logs
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS deployment_logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                error_description TEXT,
                solution_description TEXT,
                context_info TEXT,
                deployment_id VARCHAR(100),
                environment VARCHAR(50),
                severity VARCHAR(20) DEFAULT 'info',
                status VARCHAR(20) DEFAULT 'resolved'
            );
            """
            
            await conn.execute(text(create_table_sql))
            
            # Crear índices para mejor rendimiento
            create_indexes_sql = [
                "CREATE INDEX IF NOT EXISTS idx_deployment_logs_timestamp ON deployment_logs(timestamp);",
                "CREATE INDEX IF NOT EXISTS idx_deployment_logs_severity ON deployment_logs(severity);",
                "CREATE INDEX IF NOT EXISTS idx_deployment_logs_status ON deployment_logs(status);",
                "CREATE INDEX IF NOT EXISTS idx_deployment_logs_deployment_id ON deployment_logs(deployment_id);"
            ]
            
            for index_sql in create_indexes_sql:
                await conn.execute(text(index_sql))
            
            print("✅ Tabla deployment_logs creada exitosamente")
            print("✅ Índices creados para optimizar consultas")
            
            # Insertar registro inicial de creación
            insert_initial_sql = """
            INSERT INTO deployment_logs (
                error_description, 
                solution_description, 
                context_info, 
                environment, 
                severity, 
                status
            ) VALUES (
                'Creación inicial de la tabla deployment_logs',
                'Script de Python ejecutado para crear la estructura de logging',
                'Setup inicial del sistema de logs para deployment',
                'development',
                'info',
                'resolved'
            );
            """
            
            await conn.execute(text(insert_initial_sql))
            print("✅ Registro inicial insertado")
            
    except Exception as e:
        print(f"❌ Error creando tabla: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False
    
    finally:
        if engine:
            await engine.dispose()
    
    return True

async def insert_sample_logs():
    """Insertar algunos logs de ejemplo basados en problemas reales resueltos"""
    
    print("\n📝 Insertando logs de ejemplo...")
    engine = None
    
    try:
        if DATABASE_URL.startswith("postgresql"):
            async_database_url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
            engine = create_async_engine(async_database_url, echo=False)
        else:
            engine = create_async_engine("sqlite+aiosqlite:///./clickup_tasks.db", echo=False)
        
        async with engine.begin() as conn:
            # Logs de ejemplo basados en problemas reales
            sample_logs = [
                {
                    "error_description": "Error 500 en creación de tareas - workspace_id y list_id eran None",
                    "solution_description": "Corregir extracción de datos de respuesta de ClickUp API - usar team_id y list.id",
                    "context_info": "Problema en api/routes/tasks.py - validación de modelo fallaba al guardar en PostgreSQL",
                    "environment": "production",
                    "severity": "high",
                    "status": "resolved"
                },
                {
                    "error_description": "Cache persistente de Railway - código anterior seguía ejecutándose",
                    "solution_description": "Restart completo del servicio clickup_task_manager en Railway",
                    "context_info": "Múltiples deploys exitosos pero código anterior persistía - problema de cache profundo",
                    "environment": "production", 
                    "severity": "medium",
                    "status": "resolved"
                },
                {
                    "error_description": "Función safe_timestamp_to_datetime no definida",
                    "solution_description": "Re-agregar función auxiliar eliminada accidentalmente durante reescritura",
                    "context_info": "Función eliminada durante reescritura completa de tasks.py",
                    "environment": "production",
                    "severity": "medium", 
                    "status": "resolved"
                },
                {
                    "error_description": "Sincronización entre interfaz y ClickUp no funcionaba",
                    "solution_description": "Implementar endpoint /sync y dashboard de tareas para sincronización bidireccional",
                    "context_info": "Tareas se creaban en ClickUp pero no aparecían en interfaz - falta de sincronización",
                    "environment": "production",
                    "severity": "high",
                    "status": "resolved"
                }
            ]
            
            for log in sample_logs:
                insert_sql = """
                INSERT INTO deployment_logs (
                    error_description, 
                    solution_description, 
                    context_info, 
                    environment, 
                    severity, 
                    status
                ) VALUES (
                    :error_description,
                    :solution_description, 
                    :context_info,
                    :environment,
                    :severity,
                    :status
                );
                """
                
                await conn.execute(text(insert_sql), log)
            
            print(f"✅ {len(sample_logs)} logs de ejemplo insertados")
            
    except Exception as e:
        print(f"❌ Error insertando logs de ejemplo: {e}")
        return False
    
    finally:
        if engine:
            await engine.dispose()
    
    return True

async def verify_table():
    """Verificar que la tabla se creó correctamente"""
    
    print("\n🔍 Verificando tabla deployment_logs...")
    engine = None
    
    try:
        if DATABASE_URL.startswith("postgresql"):
            async_database_url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
            engine = create_async_engine(async_database_url, echo=False)
        else:
            engine = create_async_engine("sqlite+aiosqlite:///./clickup_tasks.db", echo=False)
        
        async with engine.begin() as conn:
            # Verificar estructura de la tabla
            if DATABASE_URL.startswith("postgresql"):
                result = await conn.execute(text("""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = 'deployment_logs'
                    ORDER BY ordinal_position;
                """))
            else:
                # Para SQLite
                result = await conn.execute(text("PRAGMA table_info(deployment_logs);"))
            
            columns = result.fetchall()
            
            print("📊 Estructura de la tabla deployment_logs:")
            if DATABASE_URL.startswith("postgresql"):
                for col in columns:
                    print(f"   - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            else:
                for col in columns:
                    print(f"   - {col[1]}: {col[2]} ({'NULL' if col[3] == 0 else 'NOT NULL'})")
            
            # Contar registros
            result = await conn.execute(text("SELECT COUNT(*) FROM deployment_logs;"))
            count = result.scalar()
            print(f"\n📈 Total de registros en la tabla: {count}")
            
            # Mostrar últimos logs
            result = await conn.execute(text("""
                SELECT timestamp, severity, error_description 
                FROM deployment_logs 
                ORDER BY timestamp DESC 
                LIMIT 5;
            """))
            
            logs = result.fetchall()
            print(f"\n📝 Últimos 5 logs:")
            for log in logs:
                print(f"   [{log[0]}] {log[1].upper()}: {log[2][:80]}...")
            
    except Exception as e:
        print(f"❌ Error verificando tabla: {e}")
        return False
    
    finally:
        if engine:
            await engine.dispose()
    
    return True

async def main():
    """Función principal"""
    
    print("=================================================================================")
    print("                    CREACIÓN DE TABLA DEPLOYMENT_LOGS")
    print("                    ClickUp Task Manager - Railway")
    print("=================================================================================")
    print()
    
    # Crear tabla
    if await create_deployment_logs_table():
        print("\n✅ Tabla creada exitosamente")
        
        # Insertar logs de ejemplo
        if await insert_sample_logs():
            print("\n✅ Logs de ejemplo insertados")
        
        # Verificar tabla
        await verify_table()
        
        print("\n🎉 Proceso completado exitosamente!")
        print("\n📋 La tabla deployment_logs está lista para usar")
        print("   - Almacena historial de problemas y soluciones")
        print("   - Incluye contexto y severidad de cada problema")
        print("   - Permite rastreo completo de deployments")
        
    else:
        print("\n❌ Error en el proceso")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
