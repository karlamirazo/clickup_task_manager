#!/usr/bin/env python3
"""
Prueba de notificaciones WhatsApp simulando creación de tareas
"""

import asyncio
import json
from datetime import datetime

async def test_whatsapp_notification():
    """Probar notificaciones WhatsApp simulando creación de tareas"""
    print("🧪 PRUEBA DE NOTIFICACIONES WHATSAPP")
    print("=" * 50)
    
    # Simular datos de tarea como los recibiría la API
    task_data = {
        "name": "Tarea de Prueba - Notificaciones WhatsApp",
        "description": "Esta es una tarea de prueba para verificar que las notificaciones funcionen correctamente.",
        "custom_fields": {
            "Número de Celular": "+522211500775",
            "Prioridad": "Alta",
            "Departamento": "Desarrollo"
        }
    }
    
    print(f"📋 DATOS DE LA TAREA:")
    print(f"   📝 Nombre: {task_data['name']}")
    print(f"   📄 Descripción: {task_data['description']}")
    print(f"   📱 Campo Número de Celular: {task_data['custom_fields']['Número de Celular']}")
    
    try:
        # 1. Probar la extracción de números
        print(f"\n1️⃣ PROBANDO EXTRACCIÓN DE NÚMEROS...")
        
        from core.phone_extractor import extract_whatsapp_numbers_from_task_with_custom_fields
        
        whatsapp_numbers = extract_whatsapp_numbers_from_task_with_custom_fields(
            task_description=task_data['description'],
            task_title=task_data['name'],
            custom_fields=task_data['custom_fields']
        )
        
        if whatsapp_numbers:
            print(f"   ✅ Números encontrados: {whatsapp_numbers}")
            print(f"   📊 Cantidad: {len(whatsapp_numbers)}")
        else:
            print(f"   ❌ NO se encontraron números de WhatsApp")
            return
        
    except Exception as e:
        print(f"   ❌ Error en extracción de números: {e}")
        return
    
    try:
        # 2. Probar el servicio robusto de WhatsApp
        print(f"\n2️⃣ PROBANDO SERVICIO ROBUSTO DE WHATSAPP...")
        
        from integrations.whatsapp.service import get_robust_whatsapp_service
        
        whatsapp_service = await get_robust_whatsapp_service()
        
        if whatsapp_service.enabled:
            print(f"   ✅ Servicio habilitado")
            print(f"   📱 Configuración: {whatsapp_service.whatsapp_service.__class__.__name__}")
        else:
            print(f"   ❌ Servicio deshabilitado")
            return
        
    except Exception as e:
        print(f"   ❌ Error obteniendo servicio: {e}")
        return
    
    try:
        # 3. Probar envío de notificación
        print(f"\n3️⃣ PROBANDO ENVÍO DE NOTIFICACIÓN...")
        
        for phone_number in whatsapp_numbers:
            print(f"   📤 Enviando a: {phone_number}")
            
            try:
                result = await whatsapp_service.send_message_with_retries(
                    phone_number=phone_number,
                    message=task_data['description'],
                    message_type="text",
                    notification_type="created",
                    task_name=task_data['name'],
                    due_date=None,
                    assignee_name="Usuario de Prueba"
                )
                
                if result.success:
                    print(f"      ✅ Mensaje enviado exitosamente")
                    if result.used_fallback:
                        print(f"         🔄 Usado simulador como fallback")
                    print(f"         📊 Intentos: {len(result.attempts)}")
                    print(f"         ⏱️ Duración: {result.total_duration_ms:.0f}ms")
                else:
                    print(f"      ❌ Error enviando mensaje: {result.error_summary}")
                    print(f"         📊 Intentos: {len(result.attempts)}")
                    print(f"         ⏱️ Duración: {result.total_duration_ms:.0f}ms")
                    
            except Exception as whatsapp_error:
                print(f"      ❌ Error enviando WhatsApp: {whatsapp_error}")
                
    except Exception as e:
        print(f"   ❌ Error en envío de notificaciones: {e}")
    
    print(f"\n" + "=" * 50)
    print("✅ PRUEBA COMPLETADA")
    print(f"📱 Verifica si recibiste la notificación en: {whatsapp_numbers}")

if __name__ == "__main__":
    print("🚀 Iniciando prueba de notificaciones WhatsApp...")
    asyncio.run(test_whatsapp_notification())
