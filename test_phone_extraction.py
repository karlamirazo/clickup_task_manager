#!/usr/bin/env python3
"""
Script para probar la extracción de números de teléfono
"""

from core.phone_extractor import extract_whatsapp_numbers_from_task_with_custom_fields

def test_phone_extraction():
    """Probar extracción de números de teléfono"""
    
    print("🧪 PROBANDO EXTRACCIÓN DE NÚMEROS DE TELÉFONO")
    print("=" * 60)
    
    # Casos de prueba
    test_cases = [
        {
            "name": "Descripción con número",
            "description": "Esta es una tarea de prueba.\n\n📱 **Número de Celular para WhatsApp:** +525660576654",
            "title": "Tarea de prueba",
            "custom_fields": {}
        },
        {
            "name": "Descripción con número sin +",
            "description": "Tarea importante.\n\n📱 **Número de Celular para WhatsApp:** 525660576654",
            "title": "Tarea importante",
            "custom_fields": {}
        },
        {
            "name": "Custom fields con número",
            "description": "Tarea con campos personalizados",
            "title": "Tarea con campos",
            "custom_fields": {
                "Número de Celular": "+525660576654",
                "WhatsApp": "525660576654",
                "Teléfono": "+525660576654"
            }
        },
        {
            "name": "Múltiples números",
            "description": "Tarea con múltiples números.\n\n📱 **Número de Celular para WhatsApp:** +525660576654\nTeléfono: +525512345678",
            "title": "Tarea múltiple",
            "custom_fields": {}
        },
        {
            "name": "Sin números",
            "description": "Tarea sin números de teléfono",
            "title": "Tarea sin números",
            "custom_fields": {}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Caso {i}: {test_case['name']}")
        print(f"   📝 Descripción: {test_case['description'][:50]}...")
        print(f"   📱 Custom fields: {test_case['custom_fields']}")
        
        try:
            # Extraer números
            numbers = extract_whatsapp_numbers_from_task_with_custom_fields(
                task_description=test_case['description'],
                task_title=test_case['title'],
                custom_fields=test_case['custom_fields']
            )
            
            print(f"   🔍 Números encontrados: {numbers}")
            
            if numbers:
                print(f"   ✅ Extracción exitosa: {len(numbers)} número(s)")
                for j, number in enumerate(numbers, 1):
                    print(f"      {j}. {number}")
            else:
                print(f"   ⚠️ No se encontraron números")
                
        except Exception as e:
            print(f"   ❌ Error en extracción: {e}")
    
    print(f"\n🎯 PRUEBA ESPECÍFICA: Formato de la interfaz")
    print("=" * 40)
    
    # Simular exactamente lo que hace la interfaz
    interface_description = "Esta es una tarea de prueba.\n\n📱 **Número de Celular para WhatsApp:** +525660576654"
    
    print(f"📝 Descripción simulada:")
    print(f"   {interface_description}")
    
    try:
        numbers = extract_whatsapp_numbers_from_task_with_custom_fields(
            task_description=interface_description,
            task_title="Tarea de prueba",
            custom_fields={}
        )
        
        print(f"🔍 Números extraídos: {numbers}")
        
        if numbers:
            print(f"✅ ¡Extracción exitosa! El sistema debería funcionar correctamente")
        else:
            print(f"❌ No se extrajeron números. Hay un problema en el extractor")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("🧪 PRUEBA DE EXTRACCIÓN DE NÚMEROS DE TELÉFONO")
    print("=" * 60)
    
    test_phone_extraction()
    
    print(f"\n{'='*60}")
    print("✅ Prueba completada")

if __name__ == "__main__":
    main()
