"""
Gestor de Webhooks de ClickUp
Intenta crear webhooks via API y usa polling como respaldo
"""

import asyncio
import logging
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .config import settings

logger = logging.getLogger(__name__)

@dataclass
class ClickUpWebhook:
    """Configuración de webhook de ClickUp"""
    id: str
    endpoint: str
    events: List[str]
    space_id: str
    status: str = "active"

class ClickUpWebhookManager:
    """Gestor de webhooks de ClickUp"""
    
    def __init__(self):
        self.api_token = settings.CLICKUP_API_TOKEN
        self.workspace_id = settings.CLICKUP_WORKSPACE_ID
        self.base_url = settings.CLICKUP_API_BASE_URL
        self.webhooks: List[ClickUpWebhook] = []
        self.polling_enabled = False
        self.last_poll = None
        self.poll_interval = 60  # segundos
        
    async def setup_webhooks(self, webhook_url: str) -> bool:
        """
        Intenta configurar webhooks via API
        
        Args:
            webhook_url: URL donde recibir los webhooks
            
        Returns:
            True si se configuraron webhooks, False si se usa polling
        """
        try:
            # Intentar crear webhook via API
            success = await self._create_webhook_via_api(webhook_url)
            
            if success:
                logger.info("✅ Webhooks configurados exitosamente via API")
                return True
            else:
                logger.warning("⚠️ No se pudieron crear webhooks via API, usando polling")
                self.polling_enabled = True
                return False
                
        except Exception as e:
            logger.error(f"Error configurando webhooks: {e}")
            logger.info("🔄 Usando sistema de polling como respaldo")
            self.polling_enabled = True
            return False
    
    async def _create_webhook_via_api(self, webhook_url: str) -> bool:
        """Intenta crear un webhook usando la API de ClickUp"""
        try:
            headers = {
                "Authorization": self.api_token,
                "Content-Type": "application/json"
            }
            
            webhook_data = {
                "endpoint": webhook_url,
                "events": ["taskCreated", "taskUpdated", "taskCompleted", "taskDeleted"],
                "space_id": self.workspace_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/webhook",
                    headers=headers,
                    json=webhook_data
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        webhook = ClickUpWebhook(
                            id=result.get("id", ""),
                            endpoint=webhook_url,
                            events=webhook_data["events"],
                            space_id=self.workspace_id
                        )
                        self.webhooks.append(webhook)
                        return True
                    else:
                        logger.warning(f"API retornó código {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error creando webhook via API: {e}")
            return False
    
    async def get_webhooks(self) -> List[ClickUpWebhook]:
        """Obtiene la lista de webhooks configurados"""
        try:
            headers = {"Authorization": self.api_token}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/webhook",
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        webhooks = []
                        
                        for webhook_data in result.get("webhooks", []):
                            webhook = ClickUpWebhook(
                                id=webhook_data.get("id", ""),
                                endpoint=webhook_data.get("endpoint", ""),
                                events=webhook_data.get("events", []),
                                space_id=webhook_data.get("space_id", ""),
                                status=webhook_data.get("status", "unknown")
                            )
                            webhooks.append(webhook)
                        
                        self.webhooks = webhooks
                        return webhooks
                    else:
                        logger.warning(f"No se pudieron obtener webhooks: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error obteniendo webhooks: {e}")
            return []
    
    async def delete_webhook(self, webhook_id: str) -> bool:
        """Elimina un webhook específico"""
        try:
            headers = {"Authorization": self.api_token}
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.base_url}/webhook/{webhook_id}",
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        # Remover de la lista local
                        self.webhooks = [w for w in self.webhooks if w.id != webhook_id]
                        logger.info(f"Webhook {webhook_id} eliminado exitosamente")
                        return True
                    else:
                        logger.warning(f"Error eliminando webhook: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error eliminando webhook: {e}")
            return False
    
    async def start_polling(self, callback_function) -> None:
        """
        Inicia el sistema de polling como respaldo
        
        Args:
            callback_function: Función a llamar cuando se detecten cambios
        """
        if not self.polling_enabled:
            logger.info("Polling no está habilitado")
            return
        
        logger.info("🔄 Iniciando sistema de polling...")
        
        while self.polling_enabled:
            try:
                # Obtener tareas recientes
                recent_tasks = await self._get_recent_tasks()
                
                if recent_tasks:
                    # Llamar a la función de callback con las tareas
                    await callback_function(recent_tasks)
                
                # Esperar antes de la siguiente consulta
                await asyncio.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error(f"Error en polling: {e}")
                await asyncio.sleep(self.poll_interval)
    
    async def _get_recent_tasks(self) -> List[Dict[str, Any]]:
        """Obtiene tareas recientes del workspace"""
        try:
            headers = {"Authorization": self.api_token}
            
            # Calcular fecha límite (últimas 24 horas)
            since = datetime.now() - timedelta(hours=24)
            since_timestamp = int(since.timestamp() * 1000)
            
            # Obtener tareas directamente del equipo
            async with aiohttp.ClientSession() as session:
                # Obtener tareas del equipo
                tasks_response = await session.get(
                    f"{self.base_url}/team/{self.workspace_id}/task",
                    headers=headers,
                    params={
                        "due_date_gt": since_timestamp,
                        "include_closed": "true",
                        "limit": 100
                    }
                )
                
                if tasks_response.status == 200:
                    result = await tasks_response.json()
                    return result.get("tasks", [])
                else:
                    logger.warning(f"Error obteniendo tareas: {tasks_response.status}")
                    return []
                        
        except Exception as e:
            logger.error(f"Error obteniendo tareas recientes: {e}")
            return []
    
    def stop_polling(self) -> None:
        """Detiene el sistema de polling"""
        self.polling_enabled = False
        logger.info("🛑 Sistema de polling detenido")
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado del gestor de webhooks"""
        return {
            "webhooks_configured": len(self.webhooks),
            "polling_enabled": self.polling_enabled,
            "last_poll": self.last_poll.isoformat() if self.last_poll else None,
            "poll_interval": self.poll_interval,
            "workspace_id": self.workspace_id,
            "api_token_configured": bool(self.api_token)
        }

# Instancia global del gestor
webhook_manager = ClickUpWebhookManager()

async def setup_clickup_integration(webhook_url: str) -> bool:
    """
    Función de conveniencia para configurar la integración con ClickUp
    
    Args:
        webhook_url: URL donde recibir los webhooks
        
    Returns:
        True si se configuraron webhooks, False si se usa polling
    """
    return await webhook_manager.setup_webhooks(webhook_url)

async def start_clickup_monitoring(callback_function) -> None:
    """
    Inicia el monitoreo de ClickUp (webhooks o polling)
    
    Args:
        callback_function: Función a llamar cuando se detecten cambios
    """
    if webhook_manager.polling_enabled:
        await webhook_manager.start_polling(callback_function)
    else:
        logger.info("✅ Monitoreo via webhooks activo")
