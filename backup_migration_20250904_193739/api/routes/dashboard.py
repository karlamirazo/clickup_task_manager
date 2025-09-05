"""
Dashboard for monitoring notifications and system statistics
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

from fastapi import APIRouter, Depends, Query
from fastapi import status as http_status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_

from core.database import get_db
from models.notification_log import NotificationLog
from models.task import Task
from models.user import User
from utils.advanced_notifications import notification_service
from core.advanced_sync import sync_service

dashboard_logger = logging.getLogger("dashboard")

router = APIRouter()


@router.get("/stats", status_code=http_status.HTTP_200_OK)
async def get_dashboard_stats(
    period: str = Query("24h", description="Time period: 1h, 24h, 7d, 30d"),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics
    """
    try:
        # Calcular periodo
        now = datetime.now()
        period_delta = {
            "1h": timedelta(hours=1),
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30)
        }.get(period, timedelta(hours=24))
        
        since = now - period_delta
        
        # Statistics for notificaciones
        notification_stats = await _get_notification_stats(db, since)
        
        # Statistics for tareas
        task_stats = await _get_task_stats(db, since)
        
        # Sync statistics (with fallback)
        try:
            sync_stats = sync_service.get_sync_stats()
        except Exception as e:
            dashboard_logger.warning(f"Servicio de sync no disponible: {e}")
            sync_stats = {"total_syncs": 0, "success_rate": 100}
        
        # Statistics forl servicio de notificaciones (con fallback)
        try:
            service_stats = notification_service.get_stats()
        except Exception as e:
            dashboard_logger.warning(f"Servicio de notificaciones no disponible: {e}")
            service_stats = {"total_sent": 0, "success_rate": 100}
        
        # Statistics for usuarios
        user_stats = await _get_user_stats(db)
        
        return {
            "period": period,
            "since": since.isoformat(),
            "timestamp": now.isoformat(),
            "notifications": notification_stats,
            "tasks": task_stats,
            "sync": sync_stats,
            "service": service_stats,
            "users": user_stats
        }
        
    except Exception as e:
        dashboard_logger.error(f"Error getting dashboard statistics: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/notifications", status_code=http_status.HTTP_200_OK)
async def get_notification_history(
    limit: int = Query(100, description="Notification limit"),
    offset: int = Query(0, description="Offset for pagination"),
    status: Optional[str] = Query(None, description="Filter by status: sent, failed, pending"),
    notification_type: Optional[str] = Query(None, description="Filter by type: email, sms, telegram"),
    db: Session = Depends(get_db)
):
    """
    Get historial de notificaciones
    """
    try:
        query = db.query(NotificationLog)
        
        # Aplicar filtros
        if status:
            query = query.filter(NotificationLog.status == status)
        
        if notification_type:
            query = query.filter(NotificationLog.notification_type == notification_type)
        
        # Sort by date de creacion (most recent first)
        query = query.order_by(desc(NotificationLog.created_at))
        
        # Contar total
        total = query.count()
        
        # Apply pagination
        notifications = query.offset(offset).limit(limit).all()
        
        # Formatear resultados
        results = []
        for notif in notifications:
            results.append({
                "id": notif.id,
                "type": notif.notification_type,
                "action": notif.action,
                "task_id": notif.task_id,
                "task_name": notif.task_name,
                "recipient": notif.recipient,
                "recipient_type": notif.recipient_type,
                "status": notif.status,
                "error_message": notif.error_message,
                "sent_at": notif.sent_at.isoformat() if notif.sent_at else None,
                "delivery_time": notif.delivery_time,
                "retry_count": notif.retry_count,
                "created_at": notif.created_at.isoformat(),
                "webhook_source": notif.webhook_source
            })
        
        return {
            "notifications": results,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
        
    except Exception as e:
        dashboard_logger.error(f"Error getting historial de notificaciones: {e}")
        return {"error": str(e)}


@router.get("/charts/notifications", status_code=http_status.HTTP_200_OK)
async def get_notification_charts(
    period: str = Query("24h", description="Periodo: 1h, 24h, 7d, 30d"),
    db: Session = Depends(get_db)
):
    """
    Get datos para graficos de notificaciones
    """
    try:
        # Calcular periodo
        now = datetime.now()
        period_delta = {
            "1h": timedelta(hours=1),
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30)
        }.get(period, timedelta(hours=24))
        
        since = now - period_delta
        
        # Determine interval de agrupacion
        if period in ["1h", "24h"]:
            # Group by hora
            interval = "hour"
            group_by = func.date_trunc('hour', NotificationLog.created_at)
        elif period == "7d":
            # Group by dia
            interval = "day"
            group_by = func.date_trunc('day', NotificationLog.created_at)
        else:
            # Group by dia
            interval = "day"
            group_by = func.date_trunc('day', NotificationLog.created_at)
        
        # Grafico de notificaciones por tiempo
        time_series = db.query(
            group_by.label('period'),
            NotificationLog.notification_type,
            NotificationLog.status,
            func.count().label('count')
        ).filter(
            NotificationLog.created_at >= since
        ).group_by(
            group_by,
            NotificationLog.notification_type,
            NotificationLog.status
        ).order_by(group_by).all()
        
        # Distribution chart por tipo
        type_distribution = db.query(
            NotificationLog.notification_type,
            func.count().label('count')
        ).filter(
            NotificationLog.created_at >= since
        ).group_by(NotificationLog.notification_type).all()
        
        # Grafico de tasa de exito
        success_rate = db.query(
            NotificationLog.status,
            func.count().label('count')
        ).filter(
            NotificationLog.created_at >= since
        ).group_by(NotificationLog.status).all()
        
        # Top errores
        top_errors = db.query(
            NotificationLog.error_message,
            func.count().label('count')
        ).filter(
            and_(
                NotificationLog.created_at >= since,
                NotificationLog.status == 'failed',
                NotificationLog.error_message.isnot(None)
            )
        ).group_by(
            NotificationLog.error_message
        ).order_by(
            desc(func.count())
        ).limit(5).all()
        
        # Formatear datos
        return {
            "period": period,
            "interval": interval,
            "since": since.isoformat(),
            "charts": {
                "time_series": [
                    {
                        "period": item.period.isoformat() if item.period else None,
                        "type": item.notification_type,
                        "status": item.status,
                        "count": item.count
                    }
                    for item in time_series
                ],
                "type_distribution": [
                    {"type": item.notification_type, "count": item.count}
                    for item in type_distribution
                ],
                "success_rate": [
                    {"status": item.status, "count": item.count}
                    for item in success_rate
                ],
                "top_errors": [
                    {"error": item.error_message[:100] + "..." if len(item.error_message) > 100 else item.error_message, "count": item.count}
                    for item in top_errors
                ]
            }
        }
        
    except Exception as e:
        dashboard_logger.error(f"Error getting datos de graficos: {e}")
        return {"error": str(e)}


@router.get("/health", status_code=http_status.HTTP_200_OK)
async def get_system_health():
    """
    Get system health status
    """
    try:
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "services": {}
        }
        
        # Verificar base de datos
        try:
            from sqlalchemy import text
            db = next(get_db())
            db.execute(text("SELECT 1"))
            db.close()
            health_status["services"]["database"] = {"status": "healthy", "message": "Connection successful"}
        except Exception as e:
            health_status["services"]["database"] = {"status": "unhealthy", "message": str(e)}
            health_status["status"] = "degraded"
        
        # Verificar servicio de notificaciones
        notif_stats = notification_service.get_stats()
        if notif_stats.get("success_rate", 0) > 80:
            health_status["services"]["notifications"] = {"status": "healthy", "success_rate": notif_stats.get("success_rate")}
        else:
            health_status["services"]["notifications"] = {"status": "degraded", "success_rate": notif_stats.get("success_rate")}
            health_status["status"] = "degraded"
        
        # Check synchronization
        sync_stats = sync_service.get_sync_stats()
        if not sync_stats.get("no_syncs") and sync_stats.get("success_rate", 0) > 70:
            health_status["services"]["sync"] = {"status": "healthy", "success_rate": sync_stats.get("success_rate")}
        else:
            health_status["services"]["sync"] = {"status": "degraded", "success_rate": sync_stats.get("success_rate", 0)}
            if health_status["status"] == "healthy":
                health_status["status"] = "degraded"
        
        # Si todos los servicios estan mal, marcar como unhealthy
        unhealthy_count = sum(1 for service in health_status["services"].values() if service["status"] == "unhealthy")
        if unhealthy_count > 0:
            health_status["status"] = "unhealthy"
        
        return health_status
        
    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "unhealthy",
            "error": str(e)
        }


@router.post("/clear-logs", status_code=http_status.HTTP_200_OK)
async def clear_notification_logs(
    older_than_days: int = Query(30, description="Delete older logs que X dias"),
    db: Session = Depends(get_db)
):
    """
    Limpiar logs de notificaciones antiguos
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        
        deleted_count = db.query(NotificationLog).filter(
            NotificationLog.created_at < cutoff_date
        ).delete()
        
        db.commit()
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "cutoff_date": cutoff_date.isoformat(),
            "message": f"Deleted {deleted_count} older logs que {older_than_days} dias"
        }
        
    except Exception as e:
        dashboard_logger.error(f"Error cleaning logs: {e}")
        return {"error": str(e)}


@router.post("/init-db", status_code=http_status.HTTP_200_OK)
async def initialize_database(db: Session = Depends(get_db)):
    """
    Initialize database tables (temporary endpoint for Railway)
    """
    try:
        from core.database import init_db
        
        # Inicializar base de datos
        init_db()
        
        dashboard_logger.info("Database initialized successfully")
        
        return {
            "message": "Database initialized successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        dashboard_logger.error(f"Error initializing database: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


async def _get_notification_stats(db: Session, since: datetime) -> Dict[str, Any]:
    """Get estadisticas de notificaciones"""
    
    # Total de notificaciones
    total = db.query(NotificationLog).filter(NotificationLog.created_at >= since).count()
    
    # Por estado
    by_status = db.query(
        NotificationLog.status,
        func.count().label('count')
    ).filter(
        NotificationLog.created_at >= since
    ).group_by(NotificationLog.status).all()
    
    # Por tipo
    by_type = db.query(
        NotificationLog.notification_type,
        func.count().label('count')
    ).filter(
        NotificationLog.created_at >= since
    ).group_by(NotificationLog.notification_type).all()
    
    # Average time de entrega
    avg_delivery_time = db.query(
        func.avg(NotificationLog.delivery_time)
    ).filter(
        and_(
            NotificationLog.created_at >= since,
            NotificationLog.status == 'sent',
            NotificationLog.delivery_time.isnot(None)
        )
    ).scalar()
    
    # Retry rate
    retry_stats = db.query(
        func.avg(NotificationLog.retry_count),
        func.max(NotificationLog.retry_count)
    ).filter(
        NotificationLog.created_at >= since
    ).first()
    
    return {
        "total": total,
        "by_status": {item.status: item.count for item in by_status},
        "by_type": {item.notification_type: item.count for item in by_type},
        "avg_delivery_time": float(avg_delivery_time) if avg_delivery_time else None,
        "avg_retry_count": float(retry_stats[0]) if retry_stats[0] else 0,
        "max_retry_count": retry_stats[1] if retry_stats[1] else 0
    }


async def _get_task_stats(db: Session, since: datetime) -> Dict[str, Any]:
    """Get estadisticas de tareas"""
    
    # Total de tareas
    total = db.query(Task).count()
    
    # Tareas recientes
    recent = db.query(Task).filter(Task.last_sync >= since).count()
    
    # Por estado
    by_status = db.query(
        Task.status,
        func.count().label('count')
    ).group_by(Task.status).all()
    
    # Por prioridad
    by_priority = db.query(
        Task.priority,
        func.count().label('count')
    ).group_by(Task.priority).all()
    
    # Overdue tasks
    overdue = db.query(Task).filter(
        and_(
            Task.due_date < datetime.now(),
            Task.status != 'complete'
        )
    ).count()
    
    return {
        "total": total,
        "recent": recent,
        "overdue": overdue,
        "by_status": {item.status: item.count for item in by_status},
        "by_priority": {item.priority: item.count for item in by_priority}
    }


async def _get_user_stats(db: Session) -> Dict[str, Any]:
    """Get estadisticas de usuarios"""
    
    total = db.query(User).count()
    
    # Users with email configured
    with_email = db.query(User).filter(User.email.isnot(None)).count()
    
    # Users with Telegram configured
    with_telegram = db.query(User).filter(User.telegram_id.isnot(None)).count()
    
    # Users with telefono configured
    with_phone = db.query(User).filter(User.phone.isnot(None)).count()
    
    return {
        "total": total,
        "with_email": with_email,
        "with_telegram": with_telegram,
        "with_phone": with_phone
    }
