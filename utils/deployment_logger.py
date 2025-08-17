#!/usr/bin/env python3
"""
Utilidad para logging automático de problemas de deployment
Registra errores tanto en PostgreSQL como en DEPLOYMENT_SUMMARY.txt
"""

import os
import asyncio
from datetime import datetime
from typing import Dict, Optional, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

class DeploymentLogger:
    """Clase para logging automático de problemas de deployment"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Inicializar el logger
        
        Args:
            database_url: URL de la base de datos (opcional, se detecta automáticamente)
        """
        self.database_url = database_url or os.getenv("DATABASE_URL", "sqlite:///./clickup_tasks.db")
        self.engine = None
        
    async def _get_engine(self):
        """Obtener engine de base de datos"""
        if not self.engine:
            if self.database_url.startswith("postgresql"):
                # Convertir URL de PostgreSQL a formato asyncio
                async_database_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://")
                self.engine = create_async_engine(async_database_url, echo=False)
            else:
                # SQLite para desarrollo local
                self.engine = create_async_engine("sqlite+aiosqlite:///./clickup_tasks.db", echo=False)
        return self.engine
    
    async def log_error(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        """
        Registrar un error en la base de datos y en DEPLOYMENT_SUMMARY.txt
        
        Args:
            inputs: Diccionario con información del error
                - error_description: Descripción del problema
                - solution_description: Solución implementada
                - context_info: Información adicional del contexto
                - deployment_id: ID del deployment (opcional)
                - environment: Entorno (opcional, default: 'production')
                - severity: Severidad (opcional, default: 'medium')
                - status: Estado (opcional, default: 'resolved')
        
        Returns:
            Dict con status de la operación
        """
        # Valores por defecto
        error = inputs.get("error_description", "Error no especificado")
        solution = inputs.get("solution_description", "Solución no documentada")
        context = inputs.get("context_info", "Sin contexto")
        deployment_id = inputs.get("deployment_id")
        environment = inputs.get("environment", "production")
        severity = inputs.get("severity", "medium")
        status = inputs.get("status", "resolved")
        timestamp = datetime.now()
        
        print(f"🚨 Registrando error de deployment: {error[:50]}...")
        
        try:
            # 1. Registrar en la base de datos
            await self._log_to_database(
                error, solution, context, deployment_id, 
                environment, severity, status, timestamp
            )
            
            # 2. Registrar en DEPLOYMENT_SUMMARY.txt
            await self._log_to_summary(
                error, solution, context, timestamp
            )
            
            print(f"✅ Error registrado exitosamente en ambos sistemas")
            return {"status": "documentado", "timestamp": timestamp.isoformat()}
            
        except Exception as e:
            print(f"❌ Error registrando log: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _log_to_database(self, error: str, solution: str, context: str, 
                              deployment_id: Optional[str], environment: str, 
                              severity: str, status: str, timestamp: datetime):
        """Registrar error en la base de datos"""
        try:
            engine = await self._get_engine()
            
            async with engine.begin() as conn:
                # Verificar si la tabla existe, si no, crearla
                await self._ensure_table_exists(conn)
                
                # Insertar el log
                insert_sql = """
                INSERT INTO deployment_logs (
                    timestamp, error_description, solution_description, context_info,
                    deployment_id, environment, severity, status
                ) VALUES (
                    :timestamp, :error_description, :solution_description, :context_info,
                    :deployment_id, :environment, :severity, :status
                );
                """
                
                await conn.execute(text(insert_sql), {
                    "timestamp": timestamp,
                    "error_description": error,
                    "solution_description": solution,
                    "context_info": context,
                    "deployment_id": deployment_id,
                    "environment": environment,
                    "severity": severity,
                    "status": status
                })
                
                print(f"   ✅ Registrado en base de datos")
                
        except Exception as e:
            print(f"   ❌ Error registrando en BD: {e}")
            raise
    
    async def _ensure_table_exists(self, conn):
        """Asegurar que la tabla deployment_logs existe"""
        try:
            # Intentar crear la tabla si no existe
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
            
            # Crear índices si no existen
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_deployment_logs_timestamp ON deployment_logs(timestamp);",
                "CREATE INDEX IF NOT EXISTS idx_deployment_logs_severity ON deployment_logs(severity);",
                "CREATE INDEX IF NOT EXISTS idx_deployment_logs_status ON deployment_logs(status);",
                "CREATE INDEX IF NOT EXISTS idx_deployment_logs_deployment_id ON deployment_logs(deployment_id);"
            ]
            
            for index_sql in indexes:
                await conn.execute(text(index_sql))
                
        except Exception as e:
            print(f"   ⚠️ Error creando tabla: {e}")
            # Continuar, la tabla podría ya existir
    
    async def _log_to_summary(self, error: str, solution: str, context: str, timestamp: datetime):
        """Registrar error en DEPLOYMENT_SUMMARY.txt"""
        try:
            # Formatear entrada para el archivo
            entry = f"""
## [{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] Error detectado
**Descripción del problema**: {error}
**Solución implementada**: {solution}
**Contexto**: {context}
**Timestamp**: {timestamp.isoformat()}
---
"""
            
            # Escribir en DEPLOYMENT_SUMMARY.txt
            with open("DEPLOYMENT_SUMMARY.txt", "a", encoding="utf-8") as f:
                f.write(entry)
            
            print(f"   ✅ Registrado en DEPLOYMENT_SUMMARY.txt")
            
        except Exception as e:
            print(f"   ❌ Error registrando en archivo: {e}")
            raise
    
    async def get_recent_logs(self, limit: int = 10) -> list:
        """Obtener logs recientes de la base de datos"""
        try:
            engine = await self._get_engine()
            
            async with engine.begin() as conn:
                result = await conn.execute(text("""
                    SELECT timestamp, severity, error_description, status
                    FROM deployment_logs 
                    ORDER BY timestamp DESC 
                    LIMIT :limit;
                """), {"limit": limit})
                
                logs = result.fetchall()
                return [
                    {
                        "timestamp": log[0],
                        "severity": log[1],
                        "error_description": log[2],
                        "status": log[3]
                    }
                    for log in logs
                ]
                
        except Exception as e:
            print(f"❌ Error obteniendo logs: {e}")
            return []
    
    async def close(self):
        """Cerrar conexiones"""
        if self.engine:
            await self.engine.dispose()

# Función de conveniencia para uso directo
async def log_error_to_postgres_and_summary(inputs: Dict[str, Any]) -> Dict[str, str]:
    """
    Función de conveniencia para logging rápido
    
    Args:
        inputs: Diccionario con información del error
        
    Returns:
        Dict con status de la operación
    """
    logger = DeploymentLogger()
    try:
        result = await logger.log_error(inputs)
        return result
    finally:
        await logger.close()

# Función síncrona para uso en scripts no-async
def log_error_sync(inputs: Dict[str, Any]) -> Dict[str, str]:
    """
    Versión síncrona para uso en scripts que no soportan async
    
    Args:
        inputs: Diccionario con información del error
        
    Returns:
        Dict con status de la operación
    """
    try:
        return asyncio.run(log_error_to_postgres_and_summary(inputs))
    except Exception as e:
        print(f"❌ Error en logging síncrono: {e}")
        return {"status": "error", "message": str(e)}

# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo de uso
    sample_error = {
        "error_description": "Error de conexión a base de datos",
        "solution_description": "Reiniciar servicio de base de datos",
        "context_info": "Problema durante deployment en Railway",
        "deployment_id": "test-123",
        "environment": "production",
        "severity": "high",
        "status": "resolved"
    }
    
    print("🧪 Probando sistema de logging...")
    result = log_error_sync(sample_error)
    print(f"Resultado: {result}")
