#!/usr/bin/env python3
"""
SOLUCIÓN DEFINITIVA OAUTH - SOLO DOMINIO RAÍZ
ClickUp rechaza cualquier path después del dominio
"""

import os
import re
from datetime import datetime

def print_header():
    """Imprimir cabecera del script"""
    print("=" * 90)
    print("🎯 SOLUCIÓN OAUTH DEFINITIVA - SOLO DOMINIO RAÍZ")
    print("=" * 90)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def explain_problem():
    """Explicar el problema encontrado"""
    print("🔍 PROBLEMA IDENTIFICADO...")
    print("-" * 70)
    print("❌ ClickUp rechaza CUALQUIER path después del dominio:")
    print("   • ctm-pro.up.railway.app/oauth ❌")
    print("   • ctm-pro.up.railway.app/callback ❌") 
    print("   • ctm-pro.up.railway.app/auth ❌")
    print("   • ctm-pro.up.railway.app/cualquier-cosa ❌")
    print()
    print("✅ ClickUp SOLO acepta:")
    print("   • ctm-pro.up.railway.app ✅")
    print()
    print("🔧 CAUSA: Limitación de la interfaz web de ClickUp")
    print("   • Su API puede manejar paths, pero la UI los rechaza")
    print("   • Validación estricta en el frontend")
    print("   • No es problema de SSL ni certificados")

def explain_solution():
    """Explicar la solución implementada"""
    print("\n🎯 SOLUCIÓN IMPLEMENTADA...")
    print("-" * 70)
    print("✅ USAR ENDPOINT RAÍZ (/) COMO CALLBACK OAUTH")
    print()
    print("🔧 FUNCIONAMIENTO:")
    print("   1. ClickUp redirige a: https://ctm-pro.up.railway.app?code=xxx&state=yyy")
    print("   2. Endpoint raíz (/) detecta parámetros OAuth")
    print("   3. Si hay 'code' → Procesa OAuth y redirige al dashboard")
    print("   4. Si no hay parámetros → Muestra página de login normal")
    print()
    print("✅ VENTAJAS:")
    print("   • ClickUp puede guardar el dominio sin problemas")
    print("   • Funciona como página principal Y callback OAuth")
    print("   • Lógica inteligente que detecta el contexto")
    print("   • Logging detallado para debugging")
    print("   • Manejo completo de errores")

def update_env_files():
    """Actualizar archivos .env con dominio raíz"""
    print("\n📝 ACTUALIZANDO ARCHIVOS .ENV...")
    print("-" * 70)
    
    # URL solo dominio raíz
    root_url = "https://ctm-pro.up.railway.app"
    
    env_files = ['.env', 'env.production', 'env.oauth.simple']
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"📄 Actualizando {env_file}...")
            
            try:
                # Leer contenido actual
                with open(env_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Reemplazar cualquier URL con paths por dominio raíz
                patterns = [
                    r'CLICKUP_OAUTH_REDIRECT_URI=https://ctm-pro\.up\.railway\.app/[^\s\n]+',
                    r'CLICKUP_OAUTH_REDIRECT_URI=https://ctm-pro\.up\.railway\.app',
                    r'CLICKUP_OAUTH_REDIRECT_URI=ctm-pro\.up\.railway\.app'
                ]
                
                updated = False
                for pattern in patterns:
                    if re.search(pattern, content):
                        content = re.sub(pattern, f'CLICKUP_OAUTH_REDIRECT_URI={root_url}', content)
                        updated = True
                
                if updated:
                    # Escribir archivo actualizado
                    with open(env_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"   ✅ {env_file} actualizado con dominio raíz")
                else:
                    print(f"   ℹ️ {env_file} no necesita actualización")
            
            except UnicodeDecodeError:
                print(f"   ⚠️ Error de encoding en {env_file} - omitiendo")
        else:
            print(f"   ⚠️ {env_file} no existe")

def print_final_configuration():
    """Imprimir configuración final"""
    print("\n📋 CONFIGURACIÓN FINAL...")
    print("-" * 70)
    print("🏗️ EN RAILWAY (Variables):")
    print("   CLICKUP_OAUTH_REDIRECT_URI = https://ctm-pro.up.railway.app")
    print("   (SIN ningún path después)")
    print()
    print("🌐 EN CLICKUP (Redirect URI):")
    print("   ctm-pro.up.railway.app")
    print("   (SIN https:// y SIN paths)")
    print()
    print("🔄 FLUJO OAUTH COMPLETO:")
    print("   1. Usuario: 'Iniciar con ClickUp'")
    print("   2. ClickUp: Redirige a ctm-pro.up.railway.app?code=xxx")
    print("   3. Endpoint /: Detecta parámetros OAuth")
    print("   4. Aplicación: Procesa y redirige al dashboard")
    print("   5. Usuario: ¡Ve el dashboard! 🎉")

def print_testing_steps():
    """Imprimir pasos de prueba"""
    print("\n🧪 PASOS DE PRUEBA...")
    print("-" * 70)
    print("1. ✅ VERIFICAR DEPLOY (esperar 2-3 minutos)")
    print("2. 🔧 ACTUALIZAR RAILWAY:")
    print("   Variable: CLICKUP_OAUTH_REDIRECT_URI = https://ctm-pro.up.railway.app")
    print("3. 🌐 VERIFICAR CLICKUP:")
    print("   Redirect URI: ctm-pro.up.railway.app (ya debería estar guardado)")
    print("4. 🚀 PROBAR OAUTH:")
    print("   • Ir a: https://ctm-pro.up.railway.app")
    print("   • Clic: 'Iniciar con ClickUp'")
    print("   • Autorizar en ClickUp")
    print("   • ¡Debería redirigir al dashboard!")
    print()
    print("🔍 SI SIGUE FALLANDO:")
    print("   • Verificar logs en Railway")
    print("   • Comprobar que la variable esté bien configurada")
    print("   • Asegurar que ClickUp tenga solo el dominio")

def main():
    """Función principal"""
    print_header()
    
    # Explicar problema y solución
    explain_problem()
    explain_solution()
    
    # Actualizar archivos
    update_env_files()
    
    # Configuración final
    print_final_configuration()
    print_testing_steps()
    
    print("\n" + "=" * 90)
    print("✅ SOLUCIÓN OAUTH DEFINITIVA COMPLETADA")
    print("=" * 90)
    print("🎯 El endpoint raíz (/) es la única solución que funciona con ClickUp")
    print("📱 ClickUp solo acepta dominios sin paths - ahora lo sabemos")
    print("🚀 Esta configuración debería funcionar al 100%")

if __name__ == "__main__":
    main()
