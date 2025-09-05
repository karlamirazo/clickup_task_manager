#!/usr/bin/env python3
"""
Script para probar la funcionalidad de contadores del dashboard
"""

import requests
import json
import sys
import os

# Agregar el directorio raiz al path
sys.path.insert(0, os.getcwd())

def test_dashboard_counters():
    """Test la funcionalidad de contadores del dashboard"""

    print("ğŸ§ª Probando contadores del dashboard...")

    try:
        # Test endpoint de tareas para obtener estadisticas
        response = requests.get("http://localhost:8000/api/v1/tasks/?include_closed=true")

        if response.status_code == 200:
            data = response.json()
            tasks = data.get('tasks', [])

            print(f"âœ… Se obtuvieron {len(tasks)} tareas")

            # Calcular estadisticas manualmente
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if (t.get('status') or '').lower() == 'complete'])
            pending_tasks = total_tasks - completed_tasks

            print(f"\nğŸ“Š Estadisticas calculadas:")
            print(f"   ğŸ“‹ Total tareas: {total_tasks}")
            print(f"   âœ… Completadas: {completed_tasks}")
            print(f"   â�³ Pendientes: {pending_tasks}")

            # Verificar que hay tareas para mostrar
            if total_tasks > 0:
                print(f"\nâœ… Los contadores del dashboard deberian mostrar estos valores")
                print(f"   ğŸ’¡ Puedes hacer clic en el boton de actualizacion (ğŸ”„) en el dashboard")
                print(f"   ğŸ’¡ O navegar entre tabs para que se actualicen automaticamente")
            else:
                print(f"\nâš ï¸�  No hay tareas para mostrar en los contadores")
                print(f"   ğŸ’¡ Crea algunas tareas primero para ver los contadores en accion")

        else:
            print(f"â�Œ Error en la respuesta: {response.status_code}")
            print(f"   Detalle: {response.text}")

    except requests.exceptions.ConnectionError:
        print("â�Œ No se pudo conectar al servidor. Asegurate de que este ejecutandose en http://localhost:8000")
    except Exception as e:
        print(f"â�Œ Error inesperado: {e}")

def test_counter_updates():
    """Test que los contadores se actualizan despues de acciones"""

    print("\nğŸ”„ Probando actualizacion de contadores...")

    try:
        # Get contadores iniciales
        initial_response = requests.get("http://localhost:8000/api/v1/tasks/?include_closed=true")
        if initial_response.status_code == 200:
            initial_data = initial_response.json()
            initial_tasks = initial_data.get('tasks', [])
            initial_total = len(initial_tasks)

            print(f"ğŸ“Š Contadores iniciales:")
            print(f"   ğŸ“‹ Total tareas: {initial_total}")

            # Simular una accion que podria cambiar los contadores
            # (en este caso, solo verificamos que el endpoint responde)
            sync_response = requests.post("http://localhost:8000/api/v1/tasks/sync-all")
            
            if sync_response.status_code == 200:
                print(f"âœ… Sincronizacion completada")
                
                # Get contadores despues de la accion
                final_response = requests.get("http://localhost:8000/api/v1/tasks/?include_closed=true")
                if final_response.status_code == 200:
                    final_data = final_response.json()
                    final_tasks = final_data.get('tasks', [])
                    final_total = len(final_tasks)

                    print(f"ğŸ“Š Contadores despues de sincronizacion:")
                    print(f"   ğŸ“‹ Total tareas: {final_total}")

                    if final_total != initial_total:
                        print(f"ğŸ”„ Los contadores cambiaron: {initial_total} â†’ {final_total}")
                    else:
                        print(f"ğŸ“Š Los contadores se mantuvieron igual: {final_total}")

                else:
                    print(f"â�Œ Error getting contadores finales: {final_response.status_code}")
            else:
                print(f"â�Œ Error en sincronizacion: {sync_response.status_code}")

        else:
            print(f"â�Œ Error getting contadores iniciales: {initial_response.status_code}")

    except requests.exceptions.ConnectionError:
        print("â�Œ No se pudo conectar al servidor")
    except Exception as e:
        print(f"â�Œ Error inesperado: {e}")

if __name__ == "__main__":
    print("ğŸš€ Iniciando pruebas de contadores del dashboard...\n")

    test_dashboard_counters()
    test_counter_updates()

    print("\nâœ¨ Pruebas completadas!")
    print("\nğŸ’¡ Para probar manualmente:")
    print("   1. Abre http://localhost:8000 en tu navegador")
    print("   2. Ve al tab 'Dashboard'")
    print("   3. Haz clic en el boton de actualizacion (ğŸ”„) en 'Estadisticas Rapidas'")
    print("   4. Verifica que los contadores se actualicen correctamente")
    print("   5. Prueba crear, eliminar o sincronizar tareas y verifica que los contadores cambien")

