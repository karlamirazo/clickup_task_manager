#!/usr/bin/env python3
"""
Probar el manejo de state en OAuth
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🔍 PRUEBA DE MANEJO DE STATE OAUTH")
    print("=" * 60)
    print()

def test_state_creation():
    """Probar creación de state"""
    print("🔧 Probando creación de state...")
    
    try:
        from auth.oauth import oauth_state_manager
        
        # Crear un state
        state = oauth_state_manager.create_state()
        print(f"   State creado: {state[:20]}...")
        
        # Verificar que se almacenó
        state_data = oauth_state_manager.get_state_data(state)
        if state_data:
            print("   ✅ State almacenado correctamente")
            print(f"   Datos: {state_data}")
        else:
            print("   ❌ State no se almacenó")
            return False
        
        # Validar el state
        is_valid = oauth_state_manager.validate_state(state)
        if is_valid:
            print("   ✅ State válido")
        else:
            print("   ❌ State inválido")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_state_validation():
    """Probar validación de state"""
    print("\n✅ Probando validación de state...")
    
    try:
        from auth.oauth import oauth_state_manager
        
        # Crear un state
        state = oauth_state_manager.create_state()
        print(f"   State: {state[:20]}...")
        
        # Validar inmediatamente
        is_valid = oauth_state_manager.validate_state(state)
        if is_valid:
            print("   ✅ State válido inmediatamente")
        else:
            print("   ❌ State inválido inmediatamente")
            return False
        
        # Marcar como usado
        state_data = oauth_state_manager.get_state_data(state)
        if state_data:
            state_data['used'] = True
            print("   State marcado como usado")
        
        # Validar después de usar
        is_valid_after = oauth_state_manager.validate_state(state)
        if not is_valid_after:
            print("   ✅ State inválido después de usar (correcto)")
        else:
            print("   ❌ State válido después de usar (incorrecto)")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_oauth_flow():
    """Probar flujo completo de OAuth"""
    print("\n🔄 Probando flujo completo...")
    
    try:
        from auth.oauth import clickup_oauth, oauth_state_manager
        
        # Crear state
        state = oauth_state_manager.create_state()
        print(f"   State creado: {state[:20]}...")
        
        # Generar URL de autorización
        auth_url = clickup_oauth.get_authorization_url(state)
        print(f"   URL generada: {auth_url[:100]}...")
        
        # Verificar que el state en la URL es el mismo
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(auth_url)
        params = parse_qs(parsed.query)
        url_state = params.get('state', [None])[0]
        
        if url_state == state:
            print("   ✅ State en URL coincide")
        else:
            print("   ❌ State en URL no coincide")
            print(f"   URL state: {url_state}")
            print(f"   Original state: {state}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print_banner()
    
    # Probar creación de state
    creation_ok = test_state_creation()
    
    # Probar validación de state
    validation_ok = test_state_validation()
    
    # Probar flujo completo
    flow_ok = test_oauth_flow()
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO DE LAS PRUEBAS")
    print("=" * 60)
    print(f"✅ Creación de state: {'OK' if creation_ok else 'ERROR'}")
    print(f"✅ Validación de state: {'OK' if validation_ok else 'ERROR'}")
    print(f"✅ Flujo completo: {'OK' if flow_ok else 'ERROR'}")
    
    if creation_ok and validation_ok and flow_ok:
        print("\n✅ El manejo de state funciona correctamente")
        print("💡 El problema debe estar en otra parte")
    else:
        print("\n❌ Hay problemas en el manejo de state")
        print("💡 Necesitamos corregir la lógica de state")

if __name__ == "__main__":
    main()

