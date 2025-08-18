#!/usr/bin/env python3
"""
Script para probar las funciones de configuración de campos personalizados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routes.tasks import get_custom_field_id, has_custom_fields, CUSTOM_FIELD_IDS

def test_config_functions():
    """Probar las funciones de configuración"""
    
    print("🧪 PROBANDO FUNCIONES DE CONFIGURACIÓN")
    print("=" * 50)
    
    # Lista de prueba
    list_id = "901411770471"  # PROYECTO 1
    
    print(f"📋 Configuración para lista {list_id}:")
    print(f"   {CUSTOM_FIELD_IDS.get(list_id, {})}")
    
    print(f"\n🔍 Probando has_custom_fields...")
    has_fields = has_custom_fields(list_id)
    print(f"   ¿Tiene campos personalizados? {has_fields}")
    
    print(f"\n🔍 Probando get_custom_field_id...")
    
    # Probar campo Email
    email_id = get_custom_field_id(list_id, "Email")
    print(f"   Email ID: {email_id}")
    
    # Probar campo Celular
    celular_id = get_custom_field_id(list_id, "Celular")
    print(f"   Celular ID: {celular_id}")
    
    # Probar campo inexistente
    fake_id = get_custom_field_id(list_id, "CampoInexistente")
    print(f"   Campo inexistente ID: {fake_id}")
    
    # Probar lista sin campos personalizados
    list_id_2 = "901411770470"  # PROYECTO 2
    print(f"\n📋 Configuración para lista {list_id_2}:")
    print(f"   {CUSTOM_FIELD_IDS.get(list_id_2, {})}")
    
    has_fields_2 = has_custom_fields(list_id_2)
    print(f"   ¿Tiene campos personalizados? {has_fields_2}")
    
    # Simular la lógica del endpoint
    print(f"\n🎯 SIMULANDO LÓGICA DEL ENDPOINT")
    custom_fields = {
        "Email": "test@example.com",
        "Celular": "+52 55 1234 5678"
    }
    
    print(f"   Campos personalizados a procesar: {custom_fields}")
    print(f"   ¿Tiene campos personalizados? {bool(custom_fields)}")
    print(f"   ¿Lista tiene campos personalizados? {has_custom_fields(list_id)}")
    
    if custom_fields and has_custom_fields(list_id):
        print(f"   ✅ Condición cumplida - debería actualizar campos")
        
        for field_name, field_value in custom_fields.items():
            field_id = get_custom_field_id(list_id, field_name)
            print(f"      📧 {field_name}: ID={field_id}, Valor={field_value}")
    else:
        print(f"   ❌ Condición no cumplida - no debería actualizar campos")

if __name__ == "__main__":
    test_config_functions()
