#!/usr/bin/env python3
"""
Script para configurar PostgreSQL en Railway
"""

import os
import sys

def setup_railway_postgres():
    """Configurar PostgreSQL en Railway"""
    
    print("🚀 CONFIGURANDO POSTGRESQL EN RAILWAY")
    print("=" * 50)
    
    print("\n📋 PASOS PARA CONFIGURAR POSTGRESQL EN RAILWAY:")
    print("\n1️⃣ Crear base de datos PostgreSQL:")
    print("   • Ve a tu proyecto en Railway")
    print("   • Haz clic en 'New Service'")
    print("   • Selecciona 'Database'")
    print("   • Elige 'PostgreSQL'")
    print("   • Dale un nombre (ej: 'clickup-postgres')")
    print("   • Espera a que se cree")
    
    print("\n2️⃣ Configurar variables de entorno:")
    print("   • En tu servicio principal, ve a 'Variables'")
    print("   • Railway automáticamente agrega DATABASE_URL")
    print("   • Verifica que CLICKUP_API_TOKEN esté configurado")
    
    print("\n3️⃣ Ejecutar migración:")
    print("   • Una vez creada la BD, ejecuta:")
    print("   • python migrate_to_postgres.py")
    
    print("\n4️⃣ Verificar conexión:")
    print("   • Visita: /api/v1/tasks/debug-db")
    print("   • Debería mostrar 'PostgreSQL' como tipo de BD")
    
    print("\n" + "=" * 50)
    print("💡 CONSEJOS:")
    print("   • Railway automáticamente conecta tu servicio con la BD")
    print("   • La variable DATABASE_URL se configura automáticamente")
    print("   • No necesitas configurar host, puerto, usuario, etc.")
    print("   • La migración es automática y preserva todos los datos")
    
    return True

if __name__ == "__main__":
    setup_railway_postgres()
