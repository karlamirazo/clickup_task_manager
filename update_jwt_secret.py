#!/usr/bin/env python3
"""
Actualizar JWT secret key en .env.production
"""

def update_jwt_secret():
    """Actualizar JWT secret key"""
    print("🔑 ACTUALIZANDO JWT SECRET KEY")
    print("=" * 40)
    
    jwt_secret = "dRq6HQ2oaXdvOMEMC3ir722xw3vZ-R594oONCchHeShZ2qSvKTdTf8h-c6oT5JFyDrsQi5F_1DPkt28ArGrP_g"
    
    try:
        # Leer .env.production
        with open('.env.production', 'r') as f:
            content = f.read()
        
        # Actualizar JWT_SECRET_KEY
        lines = content.split('\n')
        updated_lines = []
        
        for line in lines:
            if line.startswith('JWT_SECRET_KEY='):
                updated_lines.append(f'JWT_SECRET_KEY={jwt_secret}')
            else:
                updated_lines.append(line)
        
        # Escribir archivo actualizado
        with open('.env.production', 'w') as f:
            f.write('\n'.join(updated_lines))
        
        print("✅ JWT_SECRET_KEY actualizada en .env.production")
        
        # Mostrar configuración final
        print("\n📊 CONFIGURACIÓN FINAL:")
        print("=" * 30)
        print(f"Railway URL: https://clickuptaskmanager-production.up.railway.app")
        print(f"Redirect URI: https://clickuptaskmanager-production.up.railway.app/api/auth/callback")
        print(f"JWT Secret: {jwt_secret[:20]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    update_jwt_secret()
    
    print("\n🎉 ¡Configuración completada!")
    print("📋 Próximos pasos:")
    print("1. Haz commit y push de .env.production")
    print("2. Verifica que Railway esté usando las variables correctas")
    print("3. Prueba OAuth en producción")

if __name__ == "__main__":
    main()
