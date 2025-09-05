"""
Control de automatización de notificaciones
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from datetime import datetime
from typing import Dict, Any
import asyncio
import logging

from notifications.automated_manager import AutomatedNotificationManager
from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/automation", tags=["Automation Control"])

# Variable global para el gestor de automatización
automation_manager = None

@router.post("/start")
async def start_automation(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Inicia el sistema de automatización de notificaciones"""
    global automation_manager
    
    try:
        if automation_manager and automation_manager.is_running:
            return {
                "status": "warning",
                "message": "El sistema de automatización ya está ejecutándose",
                "timestamp": datetime.now().isoformat()
            }
        
        # Crear nuevo gestor de automatización
        automation_manager = AutomatedNotificationManager()
        
        # Iniciar en background
        background_tasks.add_task(automation_manager.start_automation)
        
        return {
            "status": "success",
            "message": "Sistema de automatización iniciado correctamente",
            "config": {
                "whatsapp_enabled": settings.WHATSAPP_ENABLED,
                "notifications_enabled": settings.WHATSAPP_NOTIFICATIONS_ENABLED,
                "automation_enabled": settings.AUTOMATION_ENABLED,
                "check_interval": settings.AUTOMATION_INTERVAL
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error iniciando automatización: {e}")
        raise HTTPException(status_code=500, detail=f"Error iniciando automatización: {str(e)}")

@router.post("/stop")
async def stop_automation() -> Dict[str, Any]:
    """Detiene el sistema de automatización de notificaciones"""
    global automation_manager
    
    try:
        if not automation_manager or not automation_manager.is_running:
            return {
                "status": "warning",
                "message": "El sistema de automatización no está ejecutándose",
                "timestamp": datetime.now().isoformat()
            }
        
        # Detener el gestor
        await automation_manager.stop_automation()
        automation_manager = None
        
        return {
            "status": "success",
            "message": "Sistema de automatización detenido correctamente",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error deteniendo automatización: {e}")
        raise HTTPException(status_code=500, detail=f"Error deteniendo automatización: {str(e)}")

@router.get("/status")
async def get_automation_status() -> Dict[str, Any]:
    """Obtiene el estado del sistema de automatización"""
    global automation_manager
    
    try:
        is_running = automation_manager and automation_manager.is_running
        
        return {
            "status": "success",
            "automation_running": is_running,
            "config": {
                "whatsapp_enabled": settings.WHATSAPP_ENABLED,
                "notifications_enabled": settings.WHATSAPP_NOTIFICATIONS_ENABLED,
                "automation_enabled": settings.AUTOMATION_ENABLED,
                "check_interval": settings.AUTOMATION_INTERVAL
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado de automatización: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")
