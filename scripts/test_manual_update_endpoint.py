#!/usr/bin/env python3
"""
Script para probar el endpoint de actualizacion manual
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_manual_update_endpoint():
    """Test el endpoint de actualizacion manual"""
    
    print("ğŸ§ª PROBANDO ENDPOINT DE ACTUALIZACION MANUAL")
    print("=" * 60)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # ID de la tarea que acabamos de crear
    task_id = "86b6agdar"
    list_id = "901411770471"  # PROYECTO 1
    
    # Datos para actualizar
    custom_fields = {
        "Email": "manual.update@test.com",
        "Celular": "+52 55 7777 7777"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"ğŸ“¤ Probando actualizacion manual...")
            print(f"   ğŸ†” Task ID: {task_id}")
            print(f"   ğŸ“‹ List ID: {list_id}")
            print(f"   ğŸ“§ Campos: {custom_fields}")
            
            # Test el endpoint de actualizacion manual
            async with session.post(
                f"{base_url}/api/v1/tasks/{task_id}/update-custom-fields",
                json={
                    "custom_fields": custom_fields,
                    "list_id": list_id
                },
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"\nğŸ“¡ Status de actualizacion: {response.status}")
                response_text = await response.text()
                print(f"ğŸ“„ Respuesta: {response_text}")
                
                if response.status == 200:
                    print(f"âœ… Actualizacion manual exitosa!")
                    update_response = json.loads(response_text)
                    
                    success_count = update_response.get('success_count', 0)
                    error_count = update_response.get('error_count', 0)
                    
                    print(f"\nğŸ“Š Resumen de actualizacion:")
                    print(f"   âœ… Campos actualizados: {success_count}")
                    print(f"   â�Œ Errores: {error_count}")
                    
                    if error_count > 0:
                        print(f"   ğŸ“‹ Errores: {update_response.get('errors', [])}")
                    
                    # Esperar un momento
                    print(f"\nâ�³ Esperando 5 segundos...")
                    await asyncio.sleep(5)
                    
                    print(f"\nğŸ�¯ INSTRUCCIONES PARA VERIFICAR EN CLICKUP:")
                    print(f"1. Ve a ClickUp y busca la tarea: 'FORZAR ACTUALIZACION - 15:42:02'")
                    print(f"2. Verifica que el campo 'Email' muestre: {custom_fields['Email']}")
                    print(f"3. Verifica que el campo 'Celular' muestre: {custom_fields['Celular']}")
                    
                    return True
                    
                else:
                    print(f"â�Œ Error en actualizacion manual: {response.status}")
                    print(f"ğŸ“„ Respuesta: {response_text}")
                    return False
    
    except Exception as e:
        print(f"â�Œ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_manual_update_endpoint())
    if success:
        print(f"\nğŸ”� Para verificar en ClickUp, usa el ID: 86b6agdar")
        print(f"ğŸ“‹ Puedes usar: python scripts/verify_clickup_task.py")
        print(f"   (Recuerda actualizar el task_id a: 86b6agdar)")
