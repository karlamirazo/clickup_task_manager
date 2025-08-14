#!/usr/bin/env python3
"""
Script para probar la funcionalidad de contadores del dashboard
"""

import requests
import json
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.getcwd())

def test_dashboard_counters():
    """Probar la funcionalidad de contadores del dashboard"""

    print("🧪 Probando contadores del dashboard...")

    try:
        # Probar endpoint de tareas para obtener estadísticas
        response = requests.get("http://localhost:8000/api/v1/tasks/?include_closed=true")

        if response.status_code == 200:
            data = response.json()
            tasks = data.get('tasks', [])

            print(f"✅ Se obtuvieron {len(tasks)} tareas")

            # Calcular estadísticas manualmente
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if (t.get('status') or '').lower() == 'complete'])
            pending_tasks = total_tasks - completed_tasks

            print(f"\n📊 Estadísticas calculadas:")
            print(f"   📋 Total tareas: {total_tasks}")
            print(f"   ✅ Completadas: {completed_tasks}")
            print(f"   ⏳ Pendientes: {pending_tasks}")

            # Verificar que hay tareas para mostrar
            if total_tasks > 0:
                print(f"\n✅ Los contadores del dashboard deberían mostrar estos valores")
                print(f"   💡 Puedes hacer clic en el botón de actualización (🔄) en el dashboard")
                print(f"   💡 O navegar entre tabs para que se actualicen automáticamente")
            else:
                print(f"\n⚠️  No hay tareas para mostrar en los contadores")
                print(f"   💡 Crea algunas tareas primero para ver los contadores en acción")

        else:
            print(f"❌ Error en la respuesta: {response.status_code}")
            print(f"   Detalle: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor. Asegúrate de que esté ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_counter_updates():
    """Probar que los contadores se actualizan después de acciones"""

    print("\n🔄 Probando actualización de contadores...")

    try:
        # Obtener contadores iniciales
        initial_response = requests.get("http://localhost:8000/api/v1/tasks/?include_closed=true")
        if initial_response.status_code == 200:
            initial_data = initial_response.json()
            initial_tasks = initial_data.get('tasks', [])
            initial_total = len(initial_tasks)

            print(f"📊 Contadores iniciales:")
            print(f"   📋 Total tareas: {initial_total}")

            # Simular una acción que podría cambiar los contadores
            # (en este caso, solo verificamos que el endpoint responde)
            sync_response = requests.post("http://localhost:8000/api/v1/tasks/sync-all")
            
            if sync_response.status_code == 200:
                print(f"✅ Sincronización completada")
                
                # Obtener contadores después de la acción
                final_response = requests.get("http://localhost:8000/api/v1/tasks/?include_closed=true")
                if final_response.status_code == 200:
                    final_data = final_response.json()
                    final_tasks = final_data.get('tasks', [])
                    final_total = len(final_tasks)

                    print(f"📊 Contadores después de sincronización:")
                    print(f"   📋 Total tareas: {final_total}")

                    if final_total != initial_total:
                        print(f"🔄 Los contadores cambiaron: {initial_total} → {final_total}")
                    else:
                        print(f"📊 Los contadores se mantuvieron igual: {final_total}")

                else:
                    print(f"❌ Error obteniendo contadores finales: {final_response.status_code}")
            else:
                print(f"❌ Error en sincronización: {sync_response.status_code}")

        else:
            print(f"❌ Error obteniendo contadores iniciales: {initial_response.status_code}")

    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de contadores del dashboard...\n")

    test_dashboard_counters()
    test_counter_updates()

    print("\n✨ Pruebas completadas!")
    print("\n💡 Para probar manualmente:")
    print("   1. Abre http://localhost:8000 en tu navegador")
    print("   2. Ve al tab 'Dashboard'")
    print("   3. Haz clic en el botón de actualización (🔄) en 'Estadísticas Rápidas'")
    print("   4. Verifica que los contadores se actualicen correctamente")
    print("   5. Prueba crear, eliminar o sincronizar tareas y verifica que los contadores cambien")

