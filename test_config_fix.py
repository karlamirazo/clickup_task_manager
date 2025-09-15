#!/usr/bin/env python3
"""
Test para verificar que el validador de ALLOWED_ORIGINS funcione correctamente
"""

import os
import sys

# Simular diferentes escenarios de ALLOWED_ORIGINS
test_cases = [
    ("", "String vacío"),
    ("   ", "String con espacios"),
    ("[]", "Array vacío"),
    ('["http://localhost:3000"]', "Array con un elemento"),
    ('["http://localhost:3000", "https://example.com"]', "Array con múltiples elementos"),
    ("invalid_json", "JSON inválido"),
    (None, "Valor None"),
]

print("🧪 Probando validador de ALLOWED_ORIGINS...")
print("=" * 50)

for test_value, description in test_cases:
    print(f"\n📝 Caso: {description}")
    print(f"   Valor: {repr(test_value)}")
    
    # Simular el entorno
    if test_value is not None:
        os.environ["ALLOWED_ORIGINS"] = str(test_value)
    elif "ALLOWED_ORIGINS" in os.environ:
        del os.environ["ALLOWED_ORIGINS"]
    
    try:
        # Importar y crear settings
        from core.config import Settings
        settings = Settings()
        print(f"   ✅ Resultado: {settings.ALLOWED_ORIGINS}")
        print(f"   ✅ Tipo: {type(settings.ALLOWED_ORIGINS)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Limpiar entorno
    if "ALLOWED_ORIGINS" in os.environ:
        del os.environ["ALLOWED_ORIGINS"]

print("\n🎉 Test completado!")
