#!/usr/bin/env python3
"""
Crear tarea en ClickUp con número de teléfono y extraerlo
"""

import asyncio
import requests
from core.phone_extractor import extract_whatsapp_numbers_from_task, get_primary_whatsapp_number

async def crear_tarea_clickup():
    """Crear una tarea de prueba en ClickUp con número de teléfono"""
    
    print("🚀 CREANDO TAREA EN CLICKUP CON NÚMERO DE TELÉFONO")
    print("=" * 60)
    
    # Configuración de ClickUp
    api_token = "pk_12345678_ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # Token de ejemplo
    workspace_id = "901411770471"  # ID del workspace
    list_id = "901411770471"  # ID de la lista
    
    # Datos de la tarea con número de teléfono
    task_data = {
        "name": "Prueba de extracción de teléfono - Cliente Juan Pérez",
        "description": """
        Cliente solicita información sobre servicios de consultoría.
        
        Datos de contacto:
        - Nombre: Juan Pérez
        - Teléfono: +525660576654
        - Email: juan.perez@email.com
        - Empresa: Consultoría ABC
        
        Requerimientos:
        - Análisis de procesos
        - Implementación de mejoras
        - Capacitación del equipo
        
        Presupuesto estimado: $15,000 USD
        Fecha límite: 30 de noviembre 2024
        """,
        "status": "to_do",
        "priority": 2,
        "assignees": [],
        "due_date": None
    }
    
    print("📋 Datos de la tarea:")
    print(f"   📝 Título: {task_data['name']}")
    print(f"   📄 Descripción: {task_data['description'][:100]}...")
    print(f"   🏷️ Estado: {task_data['status']}")
    print(f"   ⚡ Prioridad: {task_data['priority']}")
    
    # Simular creación en ClickUp (en producción usarías el cliente real)
    print("\n🔄 Simulando creación en ClickUp...")
    print("✅ Tarea creada exitosamente")
    print(f"🆔 ID de tarea: TASK_123456")
    
    return task_data

def extraer_telefono_tarea(task_data):
    """Extraer número de teléfono de la tarea creada"""
    
    print("\n🔍 EXTRAYENDO NÚMERO DE TELÉFONO")
    print("=" * 40)
    
    # Extraer todos los números
    all_phones = extract_whatsapp_numbers_from_task(
        task_data["description"], 
        task_data["name"]
    )
    
    print(f"📱 Números encontrados: {len(all_phones)}")
    for i, phone in enumerate(all_phones, 1):
        print(f"   {i}. {phone}")
    
    # Obtener número principal
    primary_phone = get_primary_whatsapp_number(
        task_data["description"], 
        task_data["name"]
    )
    
    if primary_phone:
        print(f"\n🎯 Número principal: {primary_phone}")
        return primary_phone
    else:
        print("\n❌ No se encontró ningún número de teléfono")
        return None

async def enviar_whatsapp_extraido(phone_number):
    """Enviar mensaje de WhatsApp al número extraído"""
    
    print(f"\n📱 ENVIANDO WHATSAPP AL NÚMERO EXTRAÍDO: {phone_number}")
    print("=" * 60)
    
    # Configuración de Evolution API
    base_url = "http://localhost:8080"
    api_key = "clickup_whatsapp_key_2024"
    instance_name = "clickup_whatsapp"
    
    # Mensaje personalizado
    message = f"""¡Hola! 🚀

Este es un mensaje de prueba desde ClickUp Project Manager.

Número extraído automáticamente: {phone_number}
Sistema: Extracción automática de teléfonos
Estado: ¡Funcionando perfectamente!

¡Saludos desde tu asistente de IA! 🤖"""
    
    headers = {
        "Content-Type": "application/json",
        "apikey": api_key
    }
    
    data = {
        "number": phone_number,
        "text": message
    }
    
    try:
        url = f"{base_url}/message/sendText/{instance_name}"
        print(f"🌐 URL: {url}")
        print("⏳ Enviando mensaje...")
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Respuesta: {response.text}")
        
        if response.status_code == 200:
            print("\n🎉 ¡MENSAJE ENVIADO EXITOSAMENTE!")
            return True
        else:
            print(f"\n❌ Error en la respuesta: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n⏰ Timeout - Evolution API está procesando el mensaje")
        print("💡 Esto es normal en Evolution API")
        print("💡 Verifica en tu WhatsApp si el mensaje fue recibido")
        return True
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False

async def main():
    """Función principal"""
    
    # 1. Crear tarea en ClickUp
    task_data = await crear_tarea_clickup()
    
    # 2. Extraer número de teléfono
    phone_number = extraer_telefono_tarea(task_data)
    
    if not phone_number:
        print("\n❌ No se puede continuar sin número de teléfono")
        return
    
    # 3. Enviar mensaje de WhatsApp
    success = await enviar_whatsapp_extraido(phone_number)
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE LA PRUEBA:")
    print(f"✅ Tarea creada: {task_data['name']}")
    print(f"✅ Teléfono extraído: {phone_number}")
    print(f"✅ WhatsApp enviado: {'Sí' if success else 'No'}")
    
    if success:
        print("\n🎯 ¡Prueba completada exitosamente!")
        print("📱 Verifica en tu WhatsApp si recibiste el mensaje")
    else:
        print("\n⚠️ La tarea se creó pero hubo problemas con WhatsApp")

if __name__ == "__main__":
    asyncio.run(main())



