#!/usr/bin/env python3
"""
Script para verificar TODOS los estados de tareas en la base de datos
y encontrar las 3 tareas faltantes que deberían ser "completadas"
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def check_task_states():
    """Verificar todos los estados de tareas en la base de datos"""
    
    # Configurar conexión a base de datos
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL no encontrada en variables de entorno")
        return
    
    try:
        # Crear conexión
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("CONSULTANDO TODOS LOS ESTADOS DE TAREAS...")
        print("=" * 60)
        
        # Consulta 1: Contar por estado
        result = session.execute(text("""
            SELECT status, COUNT(*) as count 
            FROM tasks 
            GROUP BY status 
            ORDER BY count DESC
        """))
        
        print("\nCONTEO POR ESTADO:")
        total_tasks = 0
        for row in result:
            print(f"   {row.status}: {row.count}")
            total_tasks += row.count
        
        print(f"\nTOTAL DE TAREAS: {total_tasks}")
        
        # Consulta 2: Ver estados únicos
        result2 = session.execute(text("""
            SELECT DISTINCT status 
            FROM tasks 
            ORDER BY status
        """))
        
        print("\nESTADOS UNICOS ENCONTRADOS:")
        all_states = []
        for row in result2:
            all_states.append(row.status)
            print(f"   - '{row.status}'")
        
        # Consulta 3: Buscar tareas que podrían ser "completadas"
        print("\nBUSCANDO POSIBLES ESTADOS DE 'COMPLETADO':")
        possible_completed = ['complete', 'done', 'finished', 'closed', 'resolved']
        
        for state in possible_completed:
            if state in all_states:
                result3 = session.execute(text(f"""
                    SELECT COUNT(*) as count 
                    FROM tasks 
                    WHERE status = :status
                """), {"status": state})
                
                count = result3.fetchone().count
                if count > 0:
                    print(f"   ENCONTRADO '{state}': {count} tareas")
        
        # Consulta 4: Ver algunas tareas de ejemplo
        print("\nEJEMPLOS DE TAREAS POR ESTADO:")
        for state in all_states[:5]:  # Solo primeros 5 estados
            result4 = session.execute(text("""
                SELECT id, name, status 
                FROM tasks 
                WHERE status = :status 
                LIMIT 2
            """), {"status": state})
            
            print(f"\n   Estado '{state}':")
            for row in result4:
                task_name = row.name[:50] + "..." if len(row.name) > 50 else row.name
                print(f"     - ID {row.id}: {task_name}")
        
        session.close()
        
        print("\n" + "=" * 60)
        print("ANALISIS COMPLETADO")
        
        # Sugerencias
        print("\nSUGERENCIAS:")
        print("   1. Revisa si hay estados como 'complete', 'done', 'closed'")
        print("   2. Las 3 tareas faltantes pueden tener un estado diferente")
        print("   3. Verifica en ClickUp que estados consideras 'completado'")
        
    except Exception as e:
        print(f"ERROR: {e}")
        return

if __name__ == "__main__":
    check_task_states()
