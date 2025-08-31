#!/usr/bin/env python3
"""
Script de prueba para el simulador de WhatsApp
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_whatsapp_simulator():
    """Prueba el simulador de WhatsApp"""
    print("🧪 Probando simulador de WhatsApp...")
    
    try:
        from core.whatsapp_simulator import WhatsAppSimulator
        
        # Crear instancia del simulador
        simulator = WhatsAppSimulator()
        
        # Conectar el simulador
        print("🔄 Conectando simulador...")
        connection_result = await simulator.connect()
        print(f"✅ Conexión: {connection_result}")
        
        # Verificar estado
        status = await simulator.get_connection_status()
        print(f"📊 Estado: {status}")
        
        # Enviar mensaje de prueba
        print("📱 Enviando mensaje de prueba...")
        message_result = await simulator.send_message(
            phone_number="+525660576654",
            message="🧪 **PRUEBA DEL SIMULADOR**\n\nEste es un mensaje de prueba para verificar que el simulador de WhatsApp esté funcionando correctamente.\n\n✅ Si ves este mensaje, el simulador está funcionando\n📱 Número: +525660576654\n🕐 Timestamp: Prueba del sistema",
            message_type="text"
        )
        
        print(f"📤 Resultado del envío: {message_result}")
        
        # Verificar estadísticas
        stats = await simulator.get_statistics()
        print(f"📈 Estadísticas: {stats}")
        
        print("✅ Prueba del simulador completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_whatsapp_simulator())
