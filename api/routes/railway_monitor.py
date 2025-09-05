#!/usr/bin/env python3
"""
API endpoints para el sistema de monitoreo de Railway
Integra con el dashboard web y proporciona datos en tiempo real
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

# Configurar path para importar módulos del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from monitoring.railway.log_monitor import RailwayLogMonitor
from monitoring.railway.alerts import alerts_manager, Alert, AlertLevel, AlertType
from core.config import settings

# Crear router
router = APIRouter(prefix="/api/v1/railway", tags=["Railway Monitor"])

# Instancia global del monitor
monitor_instance: Optional[RailwayLogMonitor] = None
background_monitoring_task = None

# Modelos Pydantic
class MonitoringConfig(BaseModel):
    """Configuración del monitoreo"""
    interval: int = 30
    duration_hours: Optional[int] = None
    enable_alerts: bool = True
    alert_threshold_errors: int = 5
    alert_threshold_response_time: float = 5.0

class AlertCreate(BaseModel):
    """Crear alerta personalizada"""
    level: str
    title: str
    message: str
    details: Dict[str, Any] = {}

class SystemMetrics(BaseModel):
    """Métricas del sistema"""
    timestamp: datetime
    response_time: float
    error_rate: int
    cpu_usage: float
    memory_usage: float
    active_alerts: int
    system_status: str

# Endpoints principales

@router.get("/status", response_model=Dict[str, Any])
async def get_system_status():
    """Obtener estado actual del sistema"""
    try:
        # Simular datos del sistema (en producción, obtener datos reales)
        current_time = datetime.now()
        
        # Obtener alertas activas
        active_alerts = alerts_manager.get_active_alerts()
        
        # Determinar estado del sistema
        system_status = "healthy"
        if any(alert["level"] == "critical" for alert in active_alerts):
            system_status = "critical"
        elif any(alert["level"] == "error" for alert in active_alerts):
            system_status = "error"
        elif any(alert["level"] == "warning" for alert in active_alerts):
            system_status = "warning"
        
        return {
            "timestamp": current_time.isoformat(),
            "system_status": system_status,
            "railway_url": "https://clickuptaskmanager-production.up.railway.app",
            "monitoring_active": monitor_instance is not None,
            "active_alerts_count": len(active_alerts),
            "environment": settings.ENVIRONMENT,
            "version": settings.VERSION
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")

@router.get("/metrics", response_model=SystemMetrics)
async def get_current_metrics():
    """Obtener métricas actuales del sistema"""
    try:
        # En producción, obtener métricas reales del monitor
        if monitor_instance and monitor_instance.metrics_buffer:
            latest_metrics = monitor_instance.metrics_buffer[-1]
            response_time = latest_metrics.response_time
            cpu_usage = latest_metrics.cpu_percent
            memory_usage = latest_metrics.memory_percent
        else:
            # Datos simulados para demo
            import random
            response_time = random.uniform(100, 800)
            cpu_usage = random.uniform(20, 80)
            memory_usage = random.uniform(40, 85)
        
        # Obtener errores recientes (simulado)
        error_rate = len([
            entry for entry in (monitor_instance.log_buffer if monitor_instance else [])
            if entry.level in ["ERROR", "CRITICAL"] and 
               entry.timestamp >= datetime.now() - timedelta(hours=1)
        ])
        
        active_alerts = len(alerts_manager.get_active_alerts())
        
        # Determinar estado
        if error_rate > 10 or response_time > 2000:
            system_status = "critical"
        elif error_rate > 5 or response_time > 1000 or cpu_usage > 80:
            system_status = "warning"
        else:
            system_status = "healthy"
        
        return SystemMetrics(
            timestamp=datetime.now(),
            response_time=response_time,
            error_rate=error_rate,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            active_alerts=active_alerts,
            system_status=system_status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo métricas: {str(e)}")

@router.get("/metrics/history")
async def get_metrics_history(hours: int = Query(24, ge=1, le=168)):
    """Obtener historial de métricas"""
    try:
        # En producción, cargar desde archivos de logs o base de datos
        # Por ahora, generar datos simulados
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        # Generar puntos de datos cada 30 minutos
        data_points = []
        current_time = start_time
        
        while current_time <= end_time:
            import random
            data_points.append({
                "timestamp": current_time.isoformat(),
                "response_time": random.uniform(100, 800),
                "cpu_usage": random.uniform(20, 80),
                "memory_usage": random.uniform(40, 85),
                "error_rate": random.randint(0, 8)
            })
            current_time += timedelta(minutes=30)
        
        return {
            "period_hours": hours,
            "data_points": len(data_points),
            "metrics": data_points
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo historial: {str(e)}")

@router.get("/alerts")
async def get_alerts(active_only: bool = Query(False), hours: int = Query(24)):
    """Obtener alertas del sistema"""
    try:
        if active_only:
            alerts = alerts_manager.get_active_alerts()
        else:
            alerts = alerts_manager.get_alert_history(hours=hours)
        
        return {
            "active_only": active_only,
            "period_hours": hours if not active_only else None,
            "count": len(alerts),
            "alerts": alerts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo alertas: {str(e)}")

@router.post("/alerts", response_model=Dict[str, Any])
async def create_custom_alert(alert_data: AlertCreate):
    """Crear alerta personalizada"""
    try:
        # Validar nivel de alerta
        try:
            alert_level = AlertLevel(alert_data.level.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail="Nivel de alerta inválido")
        
        # Crear alerta
        await alerts_manager._create_alert(
            level=alert_level,
            alert_type=AlertType.SYSTEM_DOWN,  # Tipo genérico para alertas personalizadas
            title=alert_data.title,
            message=alert_data.message,
            details=alert_data.details
        )
        
        return {
            "status": "success",
            "message": "Alerta creada correctamente",
            "alert_level": alert_data.level,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando alerta: {str(e)}")

@router.get("/logs")
async def get_recent_logs(limit: int = Query(100, ge=1, le=1000), level: Optional[str] = Query(None)):
    """Obtener logs recientes"""
    try:
        logs = []
        
        # Obtener logs del monitor si está activo
        if monitor_instance and monitor_instance.log_buffer:
            for entry in monitor_instance.log_buffer[-limit:]:
                if level and entry.level.lower() != level.lower():
                    continue
                    
                logs.append({
                    "timestamp": entry.timestamp.isoformat(),
                    "level": entry.level,
                    "message": entry.message,
                    "source": entry.source,
                    "details": entry.details
                })
        else:
            # Logs simulados
            import random
            levels = ["INFO", "WARNING", "ERROR"]
            sources = ["health_monitor", "database_monitor", "railway_monitor"]
            
            for i in range(min(limit, 20)):
                level_choice = random.choice(levels)
                logs.append({
                    "timestamp": (datetime.now() - timedelta(minutes=i*5)).isoformat(),
                    "level": level_choice,
                    "message": f"Log message {i+1} - {level_choice}",
                    "source": random.choice(sources),
                    "details": {"sample": True, "index": i}
                })
        
        return {
            "limit": limit,
            "level_filter": level,
            "count": len(logs),
            "logs": logs
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo logs: {str(e)}")

@router.post("/monitoring/start")
async def start_monitoring(background_tasks: BackgroundTasks, config: MonitoringConfig):
    """Iniciar monitoreo del sistema"""
    global monitor_instance, background_monitoring_task
    
    try:
        if monitor_instance and monitor_instance.monitoring_active:
            return {
                "status": "warning",
                "message": "El monitoreo ya está activo",
                "timestamp": datetime.now().isoformat()
            }
        
        # Crear nueva instancia del monitor
        monitor_instance = RailwayLogMonitor()
        
        # Configurar thresholds de alertas
        alerts_manager.thresholds["error_rate_per_hour"] = config.alert_threshold_errors
        alerts_manager.thresholds["response_time_seconds"] = config.alert_threshold_response_time
        
        # Iniciar monitoreo en background
        async def run_monitoring():
            try:
                await monitor_instance.start_monitoring(
                    interval=config.interval,
                    duration_hours=config.duration_hours
                )
            except Exception as e:
                print(f"❌ Error en monitoreo background: {e}")
        
        background_monitoring_task = asyncio.create_task(run_monitoring())
        
        return {
            "status": "success",
            "message": "Monitoreo iniciado correctamente",
            "config": config.dict(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error iniciando monitoreo: {str(e)}")

@router.post("/monitoring/stop")
async def stop_monitoring():
    """Detener monitoreo del sistema"""
    global monitor_instance, background_monitoring_task
    
    try:
        if not monitor_instance or not monitor_instance.monitoring_active:
            return {
                "status": "warning",
                "message": "El monitoreo no está activo",
                "timestamp": datetime.now().isoformat()
            }
        
        # Detener monitor
        monitor_instance.stop_monitoring()
        
        # Cancelar tarea de background si existe
        if background_monitoring_task and not background_monitoring_task.done():
            background_monitoring_task.cancel()
            try:
                await background_monitoring_task
            except asyncio.CancelledError:
                pass
        
        return {
            "status": "success",
            "message": "Monitoreo detenido correctamente",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deteniendo monitoreo: {str(e)}")

@router.get("/monitoring/status")
async def get_monitoring_status():
    """Obtener estado del monitoreo"""
    try:
        is_active = monitor_instance and monitor_instance.monitoring_active
        
        status_info = {
            "monitoring_active": is_active,
            "timestamp": datetime.now().isoformat()
        }
        
        if is_active and monitor_instance:
            status_info.update({
                "log_buffer_size": len(monitor_instance.log_buffer),
                "metrics_buffer_size": len(monitor_instance.metrics_buffer),
                "railway_url": monitor_instance.railway_url,
                "error_threshold": monitor_instance.error_threshold
            })
        
        return status_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado de monitoreo: {str(e)}")

@router.post("/test/notifications")
async def test_notification_system():
    """Probar sistema de notificaciones"""
    try:
        await alerts_manager.test_notifications()
        
        return {
            "status": "success",
            "message": "Notificación de prueba enviada",
            "timestamp": datetime.now().isoformat(),
            "channels": {
                "email": settings.SMTP_HOST is not None,
                "whatsapp": settings.WHATSAPP_ENABLED
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error probando notificaciones: {str(e)}")

@router.get("/export/logs")
async def export_logs(date: Optional[str] = Query(None), format: str = Query("json")):
    """Exportar logs del sistema"""
    try:
        # Validar formato
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Formato no soportado. Use 'json' o 'csv'")
        
        # Determinar fecha
        if date:
            try:
                export_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
        else:
            export_date = datetime.now()
        
        # Generar nombre de archivo
        date_str = export_date.strftime("%Y%m%d")
        filename = f"railway_logs_{date_str}.{format}"
        filepath = f"logs/{filename}"
        
        # Verificar si el archivo existe
        if not os.path.exists(filepath):
            # Crear archivo con datos de ejemplo si no existe
            sample_data = {
                "export_date": export_date.isoformat(),
                "total_logs": 0,
                "logs": [],
                "note": "No hay logs disponibles para esta fecha"
            }
            
            os.makedirs("logs", exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(sample_data, f, indent=2, ensure_ascii=False)
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exportando logs: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check del sistema de monitoreo"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "monitoring_available": True,
            "alerts_manager_active": alerts_manager is not None
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# Eventos de startup/shutdown
@router.on_event("startup")
async def startup_event():
    """Inicialización del sistema de monitoreo"""
    print("🚀 Inicializando sistema de monitoreo de Railway...")

@router.on_event("shutdown")
async def shutdown_event():
    """Limpieza al cerrar"""
    global monitor_instance, background_monitoring_task
    
    if monitor_instance:
        monitor_instance.stop_monitoring()
    
    if background_monitoring_task and not background_monitoring_task.done():
        background_monitoring_task.cancel()
    
    print("⏹️ Sistema de monitoreo detenido")
