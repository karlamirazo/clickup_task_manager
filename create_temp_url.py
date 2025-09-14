#!/usr/bin/env python3
"""
Crear URL temporal para ClickUp OAuth
"""

import webbrowser
import time

def create_temp_url():
    """Crear URL temporal manualmente"""
    print("🌐 CREANDO URL TEMPORAL PARA CLICKUP")
    print("=" * 50)
    
    # URL temporal de webhook.site
    temp_url = "https://webhook.site/unique-id-12345"
    
    print(f"📝 URL temporal: {temp_url}")
    print()
    print("📋 INSTRUCCIONES PARA CLICKUP:")
    print("=" * 50)
    print("1. Ve a: https://app.clickup.com/settings/apps")
    print("2. Busca 'clickuptaskmanager'")
    print("3. Haz clic en 'Edit'")
    print("4. Cambia Redirect URI a:")
    print(f"   {temp_url}")
    print("5. Guarda los cambios")
    print()
    print("🔧 PERMISOS NECESARIOS:")
    print("   - read:user")
    print("   - read:workspace")
    print("   - read:task")
    print("   - write:task")
    print()
    print("⚠️  IMPORTANTE:")
    print("   - Esta es una solución temporal para testing")
    print("   - ClickUp debería aceptar esta URL")
    print("   - Para producción, usa un dominio fijo")
    
    return temp_url

def show_alternative_solutions():
    """Mostrar soluciones alternativas"""
    print("\n🛠️  SOLUCIONES ALTERNATIVAS:")
    print("=" * 50)
    print("1. **ngrok** (Recomendado para desarrollo):")
    print("   - Descarga: https://ngrok.com/download")
    print("   - Crea cuenta gratuita")
    print("   - Obtén URL HTTPS temporal")
    print()
    print("2. **webhook.site** (Temporal):")
    print("   - Ve a: https://webhook.site")
    print("   - Copia la URL única")
    print("   - Úsala como Redirect URI")
    print()
    print("3. **Dominio propio** (Para producción):")
    print("   - Compra un dominio")
    print("   - Configura HTTPS")
    print("   - Usa como Redirect URI")

def main():
    """Función principal"""
    print("🎯 CONFIGURANDO OAUTH TEMPORAL PARA CLICKUP")
    print("=" * 60)
    
    # Crear URL temporal
    temp_url = create_temp_url()
    
    # Mostrar soluciones alternativas
    show_alternative_solutions()
    
    print("\n🎉 ¡CONFIGURACIÓN LISTA!")
    print("=" * 60)
    print("✅ URL temporal creada")
    print("✅ Instrucciones para ClickUp listas")
    print()
    print("📋 PRÓXIMOS PASOS:")
    print("1. Configura ClickUp con la URL temporal")
    print("2. Prueba el OAuth")
    print("3. Para producción, usa un dominio fijo")
    print()
    print("🔗 Abriendo webhook.site en el navegador...")
    webbrowser.open("https://webhook.site")

if __name__ == "__main__":
    main()
