"""
Rutas de diagnóstico para WhatsApp Evolution API
Permite probar conectividad, verificar estado y diagnosticar problemas
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

from integrations.whatsapp.service import get_robust_whatsapp_service, RobustWhatsAppService
from integrations.evolution_api.config import get_evolution_config
from core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(prefix="/whatsapp-diagnostics", tags=["WhatsApp Diagnostics"])

# Modelos Pydantic
class TestMessageRequest(BaseModel):
    """Modelo para solicitudes de prueba de mensajes"""
    phone_number: str = Field(..., description="Número de teléfono para probar")
    message: str = Field(default="🧪 Mensaje de prueba - ClickUp Project Manager", description="Mensaje de prueba")
    use_fallback: bool = Field(default=False, description="Usar simulador como fallback inmediatamente")

class HealthCheckResponse(BaseModel):
    """Modelo para respuestas de health check"""
    status: str
    timestamp: str
    evolution_api: Dict[str, Any]
    simulator: Dict[str, Any]
    statistics: Dict[str, Any]

# Dependencias
async def get_whatsapp_service() -> RobustWhatsAppService:
    """Obtiene el servicio robusto de WhatsApp"""
    return await get_robust_whatsapp_service()

# Rutas de diagnóstico
@router.get("/health", response_model=HealthCheckResponse)
async def get_whatsapp_health(
    service: RobustWhatsAppService = Depends(get_whatsapp_service)
):
    """Obtiene el estado de salud completo de WhatsApp"""
    try:
        logger.info("🔍 Verificando salud de WhatsApp...")
        
        health_status = await service.health_check()
        
        logger.info(f"✅ Health check completado: {health_status['status']}")
        
        return JSONResponse(content=health_status, status_code=200)
        
    except Exception as e:
        logger.error(f"❌ Error en health check: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error en health check: {str(e)}"
        )

@router.get("/status")
async def get_whatsapp_status():
    """Obtiene el estado básico de WhatsApp"""
    try:
        logger.info("📊 Obteniendo estado de WhatsApp...")
        
        evolution_config = get_evolution_config()
        
        status_info = {
            "whatsapp_enabled": settings.WHATSAPP_ENABLED,
            "evolution_api": {
                "url": evolution_config.base_url,
                "instance": evolution_config.instance_name,
                "api_key": evolution_config.api_key[:10] + "..." if evolution_config.api_key else None,
                "production_mode": evolution_config.production_mode,
                "fallback_enabled": evolution_config.fallback_to_simulator
            },
            "simulator": {
                "enabled": settings.WHATSAPP_SIMULATOR_ENABLED,
                "delay": settings.WHATSAPP_SIMULATOR_DELAY
            },
            "notifications": {
                "task_created": settings.WHATSAPP_TASK_CREATED,
                "task_updated": settings.WHATSAPP_TASK_UPDATED,
                "task_completed": settings.WHATSAPP_TASK_COMPLETED
            }
        }
        
        logger.info("✅ Estado de WhatsApp obtenido exitosamente")
        
        return JSONResponse(content=status_info, status_code=200)
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estado: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error obteniendo estado: {str(e)}"
        )

@router.post("/test-message")
async def test_whatsapp_message(
    test_request: TestMessageRequest,
    service: RobustWhatsAppService = Depends(get_whatsapp_service)
):
    """Prueba el envío de un mensaje de WhatsApp"""
    try:
        logger.info(f"🧪 Probando mensaje WhatsApp a {test_request.phone_number}")
        logger.info(f"   📝 Mensaje: {test_request.message}")
        logger.info(f"   🔄 Fallback: {test_request.use_fallback}")
        
        if test_request.use_fallback:
            # Usar simulador directamente
            logger.info("🔄 Usando simulador directamente para prueba")
            from integrations.whatsapp.simulator import WhatsAppSimulator
            
            simulator = WhatsAppSimulator()
            result = await simulator.send_message(
                phone_number=test_request.phone_number,
                message=test_request.message,
                message_type="text"
            )
            
            return JSONResponse(content={
                "success": result.success,
                "message": "Prueba con simulador completada",
                "phone_number": test_request.phone_number,
                "used_fallback": True,
                "response": {
                    "success": result.success,
                    "message": result.message,
                    "error": result.error
                }
            }, status_code=200)
        else:
            # Usar servicio robusto con reintentos
            result = await service.send_message_with_retries(
                phone_number=test_request.phone_number,
                message=test_request.message,
                message_type="text",
                notification_type="test"
            )
            
            # Convertir resultado a formato JSON serializable
            attempts_data = []
            for attempt in result.attempts:
                attempt_data = {
                    "attempt_number": attempt.attempt_number,
                    "timestamp": attempt.timestamp.isoformat(),
                    "status": attempt.status.value,
                    "duration_ms": attempt.duration_ms,
                    "error": attempt.error
                }
                if attempt.response:
                    attempt_data["response"] = {
                        "success": attempt.response.success,
                        "message": attempt.response.message,
                        "error": attempt.response.error
                    }
                attempts_data.append(attempt_data)
            
            response_data = {
                "success": result.success,
                "message": "Prueba con servicio robusto completada",
                "phone_number": result.phone_number,
                "final_status": result.final_status.value,
                "used_fallback": result.used_fallback,
                "total_duration_ms": result.total_duration_ms,
                "attempts": attempts_data,
                "error_summary": result.error_summary
            }
            
            if result.final_response:
                response_data["final_response"] = {
                    "success": result.final_response.success,
                    "message": result.final_response.message,
                    "error": result.final_response.error
                }
            
            logger.info(f"✅ Prueba completada: {result.success}")
            
            return JSONResponse(content=response_data, status_code=200)
            
    except Exception as e:
        logger.error(f"❌ Error en prueba de mensaje: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error en prueba de mensaje: {str(e)}"
        )

@router.get("/statistics")
async def get_whatsapp_statistics(
    service: RobustWhatsAppService = Depends(get_whatsapp_service)
):
    """Obtiene estadísticas del servicio de WhatsApp"""
    try:
        logger.info("📊 Obteniendo estadísticas de WhatsApp...")
        
        stats = service.get_statistics()
        
        logger.info("✅ Estadísticas obtenidas exitosamente")
        
        return JSONResponse(content=stats, status_code=200)
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )

@router.post("/reset-statistics")
async def reset_whatsapp_statistics(
    service: RobustWhatsAppService = Depends(get_whatsapp_service)
):
    """Reinicia las estadísticas del servicio de WhatsApp"""
    try:
        logger.info("🔄 Reiniciando estadísticas de WhatsApp...")
        
        # Reiniciar estadísticas
        service.total_messages_sent = 0
        service.successful_messages = 0
        service.failed_messages = 0
        service.fallback_messages = 0
        service.total_retries = 0
        service.message_timestamps.clear()
        
        logger.info("✅ Estadísticas reiniciadas exitosamente")
        
        return JSONResponse(content={
            "message": "Estadísticas reiniciadas exitosamente",
            "timestamp": "2025-01-17T00:00:00Z"
        }, status_code=200)
        
    except Exception as e:
        logger.error(f"❌ Error reiniciando estadísticas: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error reiniciando estadísticas: {str(e)}"
        )

@router.get("/evolution-api-test")
async def test_evolution_api_connection():
    """Prueba la conectividad directa con Evolution API"""
    try:
        logger.info("🔍 Probando conectividad con Evolution API...")
        
        evolution_config = get_evolution_config()
        
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            # Probar endpoint básico
            try:
                async with session.get(
                    f"{evolution_config.base_url}/",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    basic_status = response.status
                    basic_text = await response.text()
            except Exception as e:
                basic_status = None
                basic_text = f"Error: {str(e)}"
            
            # Probar endpoint de instancia
            try:
                headers = {"apikey": evolution_config.api_key} if evolution_config.api_key else {}
                async with session.get(
                    f"{evolution_config.base_url}/instance/connectionState/{evolution_config.instance_name}",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    instance_status = response.status
                    instance_text = await response.text()
            except Exception as e:
                instance_status = None
                instance_text = f"Error: {str(e)}"
        
        test_results = {
            "evolution_api_url": evolution_config.base_url,
            "instance_name": evolution_config.instance_name,
            "api_key_configured": bool(evolution_config.api_key),
            "basic_endpoint": {
                "status": basic_status,
                "response": basic_text[:200] + "..." if len(basic_text) > 200 else basic_text
            },
            "instance_endpoint": {
                "status": instance_status,
                "response": instance_text[:200] + "..." if len(instance_text) > 200 else instance_text
            },
            "timestamp": "2025-01-17T00:00:00Z"
        }
        
        logger.info("✅ Prueba de conectividad completada")
        
        return JSONResponse(content=test_results, status_code=200)
        
    except Exception as e:
        logger.error(f"❌ Error en prueba de conectividad: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error en prueba de conectividad: {str(e)}"
        )

@router.post("/force-fallback")
async def force_whatsapp_fallback(
    test_request: TestMessageRequest,
    service: RobustWhatsAppService = Depends(get_whatsapp_service)
):
    """Fuerza el uso del simulador como fallback"""
    try:
        logger.info(f"🔄 Forzando fallback al simulador para {test_request.phone_number}")
        
        # Usar simulador directamente
        from integrations.whatsapp.simulator import WhatsAppSimulator
        
        simulator = WhatsAppSimulator()
        result = await simulator.send_message(
            phone_number=test_request.phone_number,
            message=test_request.message,
            message_type="text"
        )
        
        logger.info(f"✅ Fallback forzado completado: {result.success}")
        
        return JSONResponse(content={
            "success": result.success,
            "message": "Fallback forzado completado",
            "phone_number": test_request.phone_number,
            "used_fallback": True,
            "response": {
                "success": result.success,
                "message": result.message,
                "error": result.error
            }
        }, status_code=200)
        
    except Exception as e:
        logger.error(f"❌ Error en fallback forzado: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error en fallback forzado: {str(e)}"
        )
