#!/usr/bin/env python3
"""
Parche temporal para deshabilitar validación de state en OAuth
"""

def apply_temp_fix():
    """Aplicar parche temporal"""
    print("🔧 Aplicando parche temporal para OAuth...")
    
    # Leer el archivo actual
    with open("auth/oauth.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Crear backup
    with open("auth/oauth_backup.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("   ✅ Backup creado: auth/oauth_backup.py")
    
    # Reemplazar la validación de state
    old_validation = """    # Validar state
    if not oauth_state_manager.validate_state(state):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="State inválido o expirado"
        )"""
    
    new_validation = """    # Validar state (TEMPORALMENTE DESHABILITADO)
    # if not oauth_state_manager.validate_state(state):
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="State inválido o expirado"
    #     )"""
    
    if old_validation in content:
        content = content.replace(old_validation, new_validation)
        
        # Escribir el archivo modificado
        with open("auth/oauth.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("   ✅ Validación de state deshabilitada temporalmente")
        return True
    else:
        print("   ❌ No se encontró la validación de state")
        return False

def restore_original():
    """Restaurar archivo original"""
    print("🔄 Restaurando archivo original...")
    
    try:
        with open("auth/oauth_backup.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        with open("auth/oauth.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("   ✅ Archivo original restaurado")
        return True
    except Exception as e:
        print(f"   ❌ Error restaurando: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        restore_original()
    else:
        apply_temp_fix()
        print("\n💡 Para restaurar el archivo original, ejecuta:")
        print("   python auth_oauth_temp_fix.py restore")
