#!/usr/bin/env python3
"""
Script para probar las funciones de configuracion de campos personalizados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routes.tasks import get_custom_field_id, has_custom_fields, CUSTOM_FIELD_IDS

def test_config_functions():
    """Test las funciones de configuracion"""
    
    print("ğŸ§ª PROBANDO FUNCIONES DE CONFIGURACION")
    print("=" * 50)
    
    # Lista de prueba
    list_id = "901411770471"  # PROYECTO 1
    
    print(f"ğŸ“‹ Configuracion para lista {list_id}:")
    print(f"   {CUSTOM_FIELD_IDS.get(list_id, {})}")
    
    print(f"\nğŸ”� Probando has_custom_fields...")
    has_fields = has_custom_fields(list_id)
    print(f"   Â¿Tiene campos personalizados? {has_fields}")
    
    print(f"\nğŸ”� Probando get_custom_field_id...")
    
    # Test campo Email
    email_id = get_custom_field_id(list_id, "Email")
    print(f"   Email ID: {email_id}")
    
    # Test campo Celular
    celular_id = get_custom_field_id(list_id, "Celular")
    print(f"   Celular ID: {celular_id}")
    
    # Test campo inexistente
    fake_id = get_custom_field_id(list_id, "CampoInexistente")
    print(f"   Campo inexistente ID: {fake_id}")
    
    # Test lista sin campos personalizados
    list_id_2 = "901411770470"  # PROYECTO 2
    print(f"\nğŸ“‹ Configuracion para lista {list_id_2}:")
    print(f"   {CUSTOM_FIELD_IDS.get(list_id_2, {})}")
    
    has_fields_2 = has_custom_fields(list_id_2)
    print(f"   Â¿Tiene campos personalizados? {has_fields_2}")
    
    # Simular la logica del endpoint
    print(f"\nğŸ�¯ SIMULANDO LOGICA DEL ENDPOINT")
    custom_fields = {
        "Email": "test@example.com",
        "Celular": "+52 55 1234 5678"
    }
    
    print(f"   Campos personalizados a procesar: {custom_fields}")
    print(f"   Â¿Tiene campos personalizados? {bool(custom_fields)}")
    print(f"   Â¿Lista tiene campos personalizados? {has_custom_fields(list_id)}")
    
    if custom_fields and has_custom_fields(list_id):
        print(f"   âœ… Condicion cumplida - deberia actualizar campos")
        
        for field_name, field_value in custom_fields.items():
            field_id = get_custom_field_id(list_id, field_name)
            print(f"      ğŸ“§ {field_name}: ID={field_id}, Valor={field_value}")
    else:
        print(f"   â�Œ Condicion no cumplida - no deberia actualizar campos")

if __name__ == "__main__":
    test_config_functions()
