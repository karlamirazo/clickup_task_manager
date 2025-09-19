#!/usr/bin/env python3
"""
Sistema avanzado de monitoreo de logs para Railway
Integra con el sistema existente de ClickUp Project Manager
"""

import os
import sys
import json
import time
import logging
import asyncio
import aiohttp
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Configurar path para importar módulos del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.config import settings
from core.database import get_db
from utils.deployment_logger import log_error_sync
from langgraph_tools.simple_error_logging import log_error_with_graph

# Configuración de logging
def setup_logging():
    """Configura el logging con manejo inteligente de archivos"""
    handlers = [logging.StreamHandler()]  # Siempre log a consola
    
    # Solo intentar crear archivo de log si estamos en desarrollo
    try:
        log_dir = Path('logs')
        if not log_dir.exists():
            log_dir.mkdir(exist_ok=True)
        handlers.append(logging.FileHandler('logs/railway_monitor.log'))
    except (OSError, PermissionError):
        # En Railway u otros entornos de producción donde no podemos escribir archivos
        pass
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

setup_logging()

logger = logging.getLogger(__name__)

@dataclass
class LogEntry:
    """Estructura para entrada de log"""
    timestamp: datetime
    level: str
    message: str
    source: str
    details: Dict[str, Any]
    environment: str = "production"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class SystemMetrics:
    """Métricas del sistema"""
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    timestamp: datetime
    active_connections: int
    response_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        }

class RailwayLogMonitor:
    """Monitor principal de logs de Railway"""
    
    def __init__(self):
        self.railway_url = "https://ctm-pro.up.railway.app"
        self.monitoring_active = False
        self.log_buffer: List[LogEntry] = []
        self.metrics_buffer: List[SystemMetrics] = []
        self.error_threshold = 5  # Máximo de errores por minuto
        self.last_alert_time = datetime.now() - timedelta(hours=1)
        
        # Configurar directorio de logs
        Path("logs").mkdir(exist_ok=True)
        Path("logs/metrics").mkdir(exist_ok=True)
        
    async def start_monitoring(self, interval: int = 30, duration_hours: Optional[int] = None):
        """
        Iniciar monitoreo continuo
        
        Args:
            interval: Intervalo en segundos entre verificaciones
            duration_hours: Duración en horas (None = infinito)
        """
        self.monitoring_active = True
        start_time = datetime.now()
        
        logger.info("🚀 Iniciando monitoreo de Railway")
        logger.info(f"   📊 Intervalo: {interval} segundos")
        logger.info(f"   ⏰ Duración: {'Infinito' if not duration_hours else f'{duration_hours} horas'}")
        logger.info(f"   🔗 URL: {self.railway_url}")
        
        try:
            while self.monitoring_active:
                # Verificar duración
                if duration_hours:
                    elapsed = (datetime.now() - start_time).total_seconds() / 3600
                    if elapsed >= duration_hours:
                        logger.info(f"✅ Monitoreo completado - {duration_hours} horas transcurridas")
                        break
                
                # Ejecutar verificaciones
                await self._perform_health_check()
                await self._collect_system_metrics()
                await self._check_database_status()
                await self._analyze_error_patterns()
                
                # Procesar logs acumulados
                await self._process_log_buffer()
                
                # Esperar siguiente iteración
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("⏹️ Monitoreo detenido por el usuario")
        except Exception as e:
            logger.error(f"❌ Error en monitoreo: {e}")
            await self._log_critical_error("Monitor failure", str(e))
        finally:
            self.monitoring_active = False
            await self._generate_final_report()
    
    async def _perform_health_check(self):
        """Realizar verificación de salud del sistema"""
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                
                # Verificar endpoint principal
                async with session.get(f"{self.railway_url}/debug", timeout=10) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        await self._log_health_status("healthy", data, response_time)
                    else:
                        await self._log_health_status("degraded", {
                            "status_code": response.status,
                            "response_text": await response.text()
                        }, response_time)
                        
        except asyncio.TimeoutError:
            await self._log_health_status("timeout", {"error": "Request timeout"}, 10.0)
        except Exception as e:
            await self._log_health_status("error", {"error": str(e)}, 0.0)
    
    async def _collect_system_metrics(self):
        """Recolectar métricas del sistema"""
        try:
            # Obtener métricas del sistema local (aproximación)
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Crear entrada de métricas
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage=disk.percent,
                timestamp=datetime.now(),
                active_connections=len(psutil.net_connections()),
                response_time=0.0  # Se actualiza en health check
            )
            
            self.metrics_buffer.append(metrics)
            
            # Mantener solo las últimas 100 métricas
            if len(self.metrics_buffer) > 100:
                self.metrics_buffer = self.metrics_buffer[-100:]
                
            logger.debug(f"📊 Métricas: CPU {cpu_percent}%, RAM {memory.percent}%, Disco {disk.percent}%")
            
        except Exception as e:
            logger.error(f"❌ Error recolectando métricas: {e}")
    
    async def _check_database_status(self):
        """Verificar estado de la base de datos"""
        try:
            async with aiohttp.ClientSession() as session:
                # Verificar endpoints de base de datos
                endpoints = [
                    "/api/v1/tasks/debug",
                    "/api/v1/tasks/config"
                ]
                
                db_status = "healthy"
                errors = []
                
                for endpoint in endpoints:
                    try:
                        async with session.get(f"{self.railway_url}{endpoint}", timeout=5) as response:
                            if response.status != 200:
                                db_status = "degraded"
                                errors.append(f"{endpoint}: HTTP {response.status}")
                    except Exception as e:
                        db_status = "error"
                        errors.append(f"{endpoint}: {str(e)}")
                
                # Registrar estado de la base de datos
                log_entry = LogEntry(
                    timestamp=datetime.now(),
                    level="INFO" if db_status == "healthy" else "WARNING" if db_status == "degraded" else "ERROR",
                    message=f"Database status: {db_status}",
                    source="database_monitor",
                    details={
                        "status": db_status,
                        "errors": errors,
                        "endpoints_checked": len(endpoints)
                    }
                )
                
                self.log_buffer.append(log_entry)
                
        except Exception as e:
            logger.error(f"❌ Error verificando base de datos: {e}")
    
    async def _analyze_error_patterns(self):
        """Analizar patrones de errores"""
        try:
            # Contar errores en la última hora
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_errors = [
                entry for entry in self.log_buffer 
                if entry.timestamp >= one_hour_ago and entry.level in ["ERROR", "CRITICAL"]
            ]
            
            error_count = len(recent_errors)
            
            # Detectar picos de errores
            if error_count > self.error_threshold:
                await self._trigger_error_alert(error_count, recent_errors)
            
            # Analizar tipos de errores más comunes
            error_types = {}
            for error in recent_errors:
                error_type = error.details.get("error_type", "unknown")
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            if error_types:
                logger.warning(f"⚠️ Errores en última hora: {error_count}")
                for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                    logger.warning(f"   - {error_type}: {count} ocurrencias")
            
        except Exception as e:
            logger.error(f"❌ Error analizando patrones: {e}")
    
    async def _trigger_error_alert(self, error_count: int, recent_errors: List[LogEntry]):
        """Disparar alerta por exceso de errores"""
        # Evitar spam de alertas
        if datetime.now() - self.last_alert_time < timedelta(minutes=30):
            return
        
        self.last_alert_time = datetime.now()
        
        logger.critical(f"🚨 ALERTA: {error_count} errores detectados en la última hora")
        
        # Preparar datos para logging automático
        error_data = {
            "error_description": f"Pico de errores detectado: {error_count} errores en 1 hora",
            "solution_description": "Revisar logs detallados y verificar estado del sistema",
            "context_info": f"Tipos de errores: {[e.message[:50] for e in recent_errors[:5]]}",
            "deployment_id": f"railway-alert-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "environment": "production",
            "severity": "high",
            "status": "detected"
        }
        
        # Usar el workflow de LangGraph para logging
        result = log_error_with_graph(error_data)
        
        if result["status"] == "success":
            logger.info("✅ Alerta registrada en sistema de logging")
        else:
            logger.error(f"❌ Error registrando alerta: {result.get('message', 'Unknown')}")
    
    async def _log_health_status(self, status: str, details: Dict[str, Any], response_time: float):
        """Registrar estado de salud"""
        level = "INFO" if status == "healthy" else "WARNING" if status == "degraded" else "ERROR"
        
        log_entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            message=f"Health check: {status}",
            source="health_monitor",
            details={
                **details,
                "response_time": response_time,
                "status": status
            }
        )
        
        self.log_buffer.append(log_entry)
        
        # Actualizar tiempo de respuesta en métricas
        if self.metrics_buffer:
            self.metrics_buffer[-1].response_time = response_time
    
    async def _log_critical_error(self, error_type: str, error_message: str):
        """Registrar error crítico"""
        log_entry = LogEntry(
            timestamp=datetime.now(),
            level="CRITICAL",
            message=f"Critical error: {error_type}",
            source="railway_monitor",
            details={
                "error_type": error_type,
                "error_message": error_message,
                "system_metrics": self.metrics_buffer[-1].to_dict() if self.metrics_buffer else {}
            }
        )
        
        self.log_buffer.append(log_entry)
        
        # Usar workflow de logging automático
        error_data = {
            "error_description": f"{error_type}: {error_message}",
            "solution_description": "Revisar logs del monitor y verificar estado del sistema",
            "context_info": f"Error crítico en monitor de Railway - {datetime.now()}",
            "deployment_id": f"monitor-critical-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "environment": "production",
            "severity": "critical",
            "status": "active"
        }
        
        log_error_with_graph(error_data)
    
    async def _process_log_buffer(self):
        """Procesar buffer de logs acumulados"""
        if not self.log_buffer:
            return
        
        try:
            # Guardar logs en archivo
            log_file = f"logs/railway_monitor_{datetime.now().strftime('%Y%m%d')}.json"
            
            # Cargar logs existentes del día
            existing_logs = []
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        existing_logs = json.load(f)
                except:
                    existing_logs = []
            
            # Agregar nuevos logs
            new_logs = [entry.to_dict() for entry in self.log_buffer]
            all_logs = existing_logs + new_logs
            
            # Guardar logs actualizados
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(all_logs, f, indent=2, ensure_ascii=False, default=str)
            
            logger.debug(f"📝 {len(new_logs)} logs guardados en {log_file}")
            
            # Limpiar buffer
            self.log_buffer.clear()
            
        except Exception as e:
            logger.error(f"❌ Error procesando logs: {e}")
    
    async def _generate_final_report(self):
        """Generar reporte final del monitoreo"""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "monitoring_duration": "N/A",
                "total_logs": len(self.log_buffer),
                "total_metrics": len(self.metrics_buffer),
                "error_summary": {},
                "performance_summary": {},
                "recommendations": []
            }
            
            # Analizar logs por nivel
            log_levels = {}
            for entry in self.log_buffer:
                log_levels[entry.level] = log_levels.get(entry.level, 0) + 1
            
            report["error_summary"] = log_levels
            
            # Analizar métricas de performance
            if self.metrics_buffer:
                metrics_data = [m.to_dict() for m in self.metrics_buffer]
                avg_cpu = sum(m["cpu_percent"] for m in metrics_data) / len(metrics_data)
                avg_memory = sum(m["memory_percent"] for m in metrics_data) / len(metrics_data)
                avg_response = sum(m["response_time"] for m in metrics_data) / len(metrics_data)
                
                report["performance_summary"] = {
                    "average_cpu_percent": round(avg_cpu, 2),
                    "average_memory_percent": round(avg_memory, 2),
                    "average_response_time": round(avg_response, 3),
                    "total_samples": len(metrics_data)
                }
                
                # Generar recomendaciones
                if avg_cpu > 80:
                    report["recommendations"].append("CPU usage alto - considerar optimización")
                if avg_memory > 85:
                    report["recommendations"].append("Memoria alta - revisar consumo de memoria")
                if avg_response > 2.0:
                    report["recommendations"].append("Tiempo de respuesta lento - optimizar performance")
            
            # Guardar reporte
            report_file = f"logs/railway_monitor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📋 Reporte final guardado: {report_file}")
            logger.info(f"   📊 Total logs: {report['total_logs']}")
            logger.info(f"   📈 Total métricas: {report['total_metrics']}")
            
            if report["recommendations"]:
                logger.info("💡 Recomendaciones:")
                for rec in report["recommendations"]:
                    logger.info(f"   - {rec}")
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte: {e}")

    def stop_monitoring(self):
        """Detener monitoreo"""
        self.monitoring_active = False
        logger.info("⏹️ Deteniendo monitoreo...")

# Funciones de conveniencia
async def start_railway_monitoring(interval: int = 30, duration_hours: Optional[int] = None):
    """Iniciar monitoreo de Railway"""
    monitor = RailwayLogMonitor()
    await monitor.start_monitoring(interval=interval, duration_hours=duration_hours)

def create_quick_monitor_session(minutes: int = 60, interval: int = 30):
    """Crear sesión rápida de monitoreo"""
    async def run_monitor():
        duration_hours = minutes / 60
        await start_railway_monitoring(interval=interval, duration_hours=duration_hours)
    
    return run_monitor

# Script principal
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor de logs de Railway")
    parser.add_argument("--interval", type=int, default=30, help="Intervalo en segundos")
    parser.add_argument("--duration", type=int, help="Duración en horas (opcional)")
    parser.add_argument("--quick", type=int, help="Sesión rápida en minutos")
    
    args = parser.parse_args()
    
    if args.quick:
        # Sesión rápida
        monitor_func = create_quick_monitor_session(minutes=args.quick, interval=args.interval)
        asyncio.run(monitor_func())
    else:
        # Monitoreo estándar
        asyncio.run(start_railway_monitoring(
            interval=args.interval,
            duration_hours=args.duration
        ))
