"""
Simulador de WhatsApp para pruebas de integración
"""

import asyncio
import logging
import qrcode
from io import BytesIO
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from PIL import Image

logger = logging.getLogger(__name__)

@dataclass
class SimulatedMessage:
    """Mensaje simulado de WhatsApp"""
    id: str
    phone_number: str
    message: str
    timestamp: datetime
    status: str = "sent"
    media_url: Optional[str] = None

class WhatsAppSimulator:
    """Simulador completo de WhatsApp"""
    
    def __init__(self):
        self.is_connected = False
        self.connection_status = "disconnected"
        self.messages_sent: List[SimulatedMessage] = []
        self.connection_time = None
        self.instance_name = "whatsapp-simulator"
        
    async def connect(self) -> Dict[str, Any]:
        """Simula la conexión a WhatsApp"""
        logger.info("🔄 Simulando conexión a WhatsApp...")
        
        # Simular tiempo de conexión
        await asyncio.sleep(2)
        
        self.is_connected = True
        self.connection_status = "connected"
        self.connection_time = datetime.now()
        
        logger.info("✅ WhatsApp Simulator conectado exitosamente")
        
        return {
            "status": "success",
            "message": "WhatsApp Simulator conectado",
            "instance": self.instance_name,
            "connected": True,
            "timestamp": self.connection_time.isoformat()
        }
    
    async def disconnect(self) -> Dict[str, Any]:
        """Simula la desconexión de WhatsApp"""
        logger.info("🔄 Simulando desconexión de WhatsApp...")
        
        await asyncio.sleep(1)
        
        self.is_connected = False
        self.connection_status = "disconnected"
        self.connection_time = None
        
        logger.info("✅ WhatsApp Simulator desconectado")
        
        return {
            "status": "success",
            "message": "WhatsApp Simulator desconectado",
            "instance": self.instance_name,
            "connected": False,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_connection_status(self) -> Dict[str, Any]:
        """Obtiene el estado de conexión"""
        return {
            "instance": self.instance_name,
            "status": self.connection_status,
            "connected": self.is_connected,
            "connection_time": self.connection_time.isoformat() if self.connection_time else None,
            "messages_sent": len(self.messages_sent)
        }
    
    async def send_text_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Simula el envío de un mensaje de texto"""
        if not self.is_connected:
            return {
                "status": "error",
                "message": "WhatsApp Simulator no está conectado",
                "error": "NOT_CONNECTED"
            }
        
        logger.info(f"📱 Simulando envío de mensaje a {phone_number}")
        
        # Simular tiempo de envío
        await asyncio.sleep(0.5)
        
        # Crear mensaje simulado
        simulated_message = SimulatedMessage(
            id=f"msg_{len(self.messages_sent) + 1}_{int(datetime.now().timestamp())}",
            phone_number=phone_number,
            message=message,
            timestamp=datetime.now()
        )
        
        self.messages_sent.append(simulated_message)
        
        logger.info(f"✅ Mensaje simulado enviado a {phone_number}")
        
        return {
            "status": "success",
            "message": "Mensaje enviado exitosamente (simulado)",
            "message_id": simulated_message.id,
            "phone_number": phone_number,
            "timestamp": simulated_message.timestamp.isoformat(),
            "simulated": True
        }
    
    async def send_media_message(self, phone_number: str, media_url: str, caption: str = "") -> Dict[str, Any]:
        """Simula el envío de un mensaje multimedia"""
        if not self.is_connected:
            return {
                "status": "error",
                "message": "WhatsApp Simulator no está conectado",
                "error": "NOT_CONNECTED"
            }
        
        logger.info(f"📱 Simulando envío de media a {phone_number}")
        
        # Simular tiempo de envío
        await asyncio.sleep(1)
        
        # Crear mensaje simulado
        simulated_message = SimulatedMessage(
            id=f"media_{len(self.messages_sent) + 1}_{int(datetime.now().timestamp())}",
            phone_number=phone_number,
            message=caption or "Archivo multimedia",
            timestamp=datetime.now(),
            media_url=media_url
        )
        
        self.messages_sent.append(simulated_message)
        
        logger.info(f"✅ Media simulado enviado a {phone_number}")
        
        return {
            "status": "success",
            "message": "Media enviado exitosamente (simulado)",
            "message_id": simulated_message.id,
            "phone_number": phone_number,
            "media_url": media_url,
            "caption": caption,
            "timestamp": simulated_message.timestamp.isoformat(),
            "simulated": True
        }
    
    async def send_bulk_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simula el envío masivo de mensajes"""
        if not self.is_connected:
            return [{
                "status": "error",
                "message": "WhatsApp Simulator no está conectado",
                "error": "NOT_CONNECTED"
            }] * len(messages)
        
        logger.info(f"📱 Simulando envío masivo de {len(messages)} mensajes")
        
        results = []
        
        for i, msg_data in enumerate(messages):
            phone_number = msg_data.get("phone_number")
            message = msg_data.get("message")
            
            if phone_number and message:
                result = await self.send_text_message(phone_number, message)
                results.append(result)
                
                # Simular delay entre mensajes
                if i < len(messages) - 1:
                    await asyncio.sleep(0.2)
            else:
                results.append({
                    "status": "error",
                    "message": "Datos de mensaje incompletos",
                    "error": "INVALID_DATA"
                })
        
        logger.info(f"✅ Envío masivo simulado completado: {len(results)} mensajes")
        return results
    
    async def get_message_history(self, phone_number: str = None, limit: int = 50) -> Dict[str, Any]:
        """Obtiene el historial de mensajes"""
        if phone_number:
            filtered_messages = [msg for msg in self.messages_sent if msg.phone_number == phone_number]
        else:
            filtered_messages = self.messages_sent
        
        # Limitar resultados
        limited_messages = filtered_messages[-limit:] if limit > 0 else filtered_messages
        
        return {
            "status": "success",
            "messages": [
                {
                    "id": msg.id,
                    "phone_number": msg.phone_number,
                    "message": msg.message,
                    "timestamp": msg.timestamp.isoformat(),
                    "status": msg.status,
                    "media_url": msg.media_url
                }
                for msg in limited_messages
            ],
            "total": len(filtered_messages),
            "returned": len(limited_messages)
        }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del simulador"""
        total_messages = len(self.messages_sent)
        text_messages = len([msg for msg in self.messages_sent if not msg.media_url])
        media_messages = len([msg for msg in self.messages_sent if msg.media_url])
        
        # Agrupar por número de teléfono
        phone_stats = {}
        for msg in self.messages_sent:
            if msg.phone_number not in phone_stats:
                phone_stats[msg.phone_number] = 0
            phone_stats[msg.phone_number] += 1
        
        return {
            "status": "success",
            "statistics": {
                "total_messages": total_messages,
                "text_messages": text_messages,
                "media_messages": media_messages,
                "unique_phones": len(phone_stats),
                "connection_status": self.connection_status,
                "connected_since": self.connection_time.isoformat() if self.connection_time else None,
                "phone_distribution": phone_stats
            }
        }
    
    def generate_qr_code(self) -> BytesIO:
        """Genera un código QR simulado"""
        # Crear un código QR con información del simulador
        qr_data = f"whatsapp-simulator://{self.instance_name}/connect"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a BytesIO
        img_buffer = BytesIO()
        qr_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return img_buffer

# Instancia global del simulador
whatsapp_simulator = WhatsAppSimulator()

async def get_simulator_status() -> Dict[str, Any]:
    """Función de conveniencia para obtener el estado del simulador"""
    return await whatsapp_simulator.get_connection_status()

async def send_simulated_message(phone_number: str, message: str) -> Dict[str, Any]:
    """Función de conveniencia para enviar mensajes simulados"""
    return await whatsapp_simulator.send_text_message(phone_number, message)

