#!/usr/bin/env python3
"""
Script para crear la tabla deployment_logs en PostgreSQL
Esta tabla almacenara el historial completo de problemas y soluciones de deployment
"""

import asyncio
import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Configuracion de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./clickup_tasks.db")

async def create_deployment_logs_table():
    """Create la tabla deployment_logs en PostgreSQL"""
    
    print("üöÄ Creando tabla deployment_logs...")
    engine = None
    
    try:
        # Create engine asincrono
        if DATABASE_URL.startswith("postgresql"):
            # Convertir URL de PostgreSQL a formato asyncio
            async_database_url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
            engine = create_async_engine(async_database_url, echo=True)
            print("‚úÖ Conectando a PostgreSQL...")
        else:
            print("‚ö†Ô∏è No se detecto PostgreSQL, usando SQLite para desarrollo local")
            engine = create_async_engine("sqlite+aiosqlite:///./clickup_tasks.db", echo=True)
            print("‚úÖ Conectando a SQLite...")
        
        async with engine.begin() as conn:
            # Create tabla deployment_logs
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
            
            # Create indices para mejor rendimiento
            create_indexes_sql = [
                "CREATE INDEX IF NOT EXISTS idx_deployment_logs_timestamp ON deployment_logs(timestamp);",
                "CREATE INDEX IF NOT EXISTS idx_deployment_logs_severity ON deployment_logs(severity);",
                "CREATE INDEX IF NOT EXISTS idx_deployment_logs_status ON deployment_logs(status);",
                "CREATE INDEX IF NOT EXISTS idx_deployment_logs_deployment_id ON deployment_logs(deployment_id);"
            ]
            
            for index_sql in create_indexes_sql:
                await conn.execute(text(index_sql))
            
            print("‚úÖ Tabla deployment_logs creada exitosamente")
            print("‚úÖ Indices creados para optimizar consultas")
            
            # Insertar registro inicial de creacion
            insert_initial_sql = """
            INSERT INTO deployment_logs (
                error_description, 
                solution_description, 
                context_info, 
                environment, 
                severity, 
                status
            ) VALUES (
                'Creacion inicial de la tabla deployment_logs',
                'Script de Python ejecutado para crear la estructura de logging',
                'Setup inicial del sistema de logs para deployment',
                'development',
                'info',
                'resolved'
            );
            """
            
            await conn.execute(text(insert_initial_sql))
            print("‚úÖ Registro inicial insertado")
            
    except Exception as e:
        print(f"‚ùå Error creating tabla: {e}")
        import traceback
        print(f"‚ùå Traceback: {traceback.format_exc()}")
        return False
    
    finally:
        if engine:
            await engine.dispose()
    
    return True

async def insert_sample_logs():
    """Insertar algunos logs de ejemplo basados en problemas reales resueltos"""
    
    print("\nüìù Insertando logs de ejemplo...")
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
                    "error_description": "Error 500 en creacion de tareas - workspace_id y list_id eran None",
                    "solution_description": "Corregir extraccion de datos de respuesta de ClickUp API - usar team_id y list.id",
                    "context_info": "Problema en api/routes/tasks.py - validacion de modelo fallaba al guardar en PostgreSQL",
                    "environment": "production",
                    "severity": "high",
                    "status": "resolved"
                },
                {
                    "error_description": "Cache persistente de Railway - codigo anterior seguia ejecutandose",
                    "solution_description": "Restart completo del servicio clickup_task_manager en Railway",
                    "context_info": "Multiples deploys exitosos pero codigo anterior persistia - problema de cache profundo",
                    "environment": "production", 
                    "severity": "medium",
                    "status": "resolved"
                },
                {
                    "error_description": "Funcion safe_timestamp_to_datetime no definida",
                    "solution_description": "Re-agregar funcion auxiliar eliminada accidentalmente durante reescritura",
                    "context_info": "Funcion eliminada durante reescritura completa de tasks.py",
                    "environment": "production",
                    "severity": "medium", 
                    "status": "resolved"
                },
                {
                    "error_description": "Sincronizacion entre interfaz y ClickUp no funcionaba",
                    "solution_description": "Implementar endpoint /sync y dashboard de tareas para sincronizacion bidireccional",
                    "context_info": "Tareas se creaban en ClickUp pero no aparecian en interfaz - falta de sincronizacion",
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
            
            print(f"‚úÖ {len(sample_logs)} logs de ejemplo insertados")
            
    except Exception as e:
        print(f"‚ùå Error insertando logs de ejemplo: {e}")
        return False
    
    finally:
        if engine:
            await engine.dispose()
    
    return True

async def verify_table():
    """Verificar que la tabla se creo correctamente"""
    
    print("\nüîç Verificando tabla deployment_logs...")
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
            
            print("üìä Estructura de la tabla deployment_logs:")
            if DATABASE_URL.startswith("postgresql"):
                for col in columns:
                    print(f"   - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            else:
                for col in columns:
                    print(f"   - {col[1]}: {col[2]} ({'NULL' if col[3] == 0 else 'NOT NULL'})")
            
            # Contar registros
            result = await conn.execute(text("SELECT COUNT(*) FROM deployment_logs;"))
            count = result.scalar()
            print(f"\nüìà Total de registros en la tabla: {count}")
            
            # Mostrar ultimos logs
            result = await conn.execute(text("""
                SELECT timestamp, severity, error_description 
                FROM deployment_logs 
                ORDER BY timestamp DESC 
                LIMIT 5;
            """))
            
            logs = result.fetchall()
            print(f"\nüìù Ultimos 5 logs:")
            for log in logs:
                print(f"   [{log[0]}] {log[1].upper()}: {log[2][:80]}...")
            
    except Exception as e:
        print(f"‚ùå Error verificando tabla: {e}")
        return False
    
    finally:
        if engine:
            await engine.dispose()
    
    return True

async def main():
    """Funcion principal"""
    
    print("=================================================================================")
    print("                    CREACION DE TABLA DEPLOYMENT_LOGS")
    print("                    ClickUp Task Manager - Railway")
    print("=================================================================================")
    print()
    
    # Create tabla
    if await create_deployment_logs_table():
        print("\n‚úÖ Tabla creada exitosamente")
        
        # Insertar logs de ejemplo
        if await insert_sample_logs():
            print("\n‚úÖ Logs de ejemplo insertados")
        
        # Verificar tabla
        await verify_table()
        
        print("\nüéâ Proceso completado exitosamente!")
        print("\nüìã La tabla deployment_logs esta lista para usar")
        print("   - Almacena historial de problemas y soluciones")
        print("   - Incluye contexto y severidad de cada problema")
        print("   - Permite rastreo completo de deployments")
        
    else:
        print("\n‚ùå Error en el proceso")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
