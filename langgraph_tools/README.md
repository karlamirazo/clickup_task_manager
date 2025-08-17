# 🚀 Sistema de Logging de Errores con LangGraph

Este directorio contiene workflows de LangGraph para logging automático de errores de deployment, integrando con el sistema de logging dual (PostgreSQL + DEPLOYMENT_SUMMARY.txt).

## 📋 **Componentes del Sistema**

### 1. **Sistema Base de Logging** (`utils/deployment_logger.py`)
- Clase `DeploymentLogger` para logging automático
- Funciones de conveniencia: `log_error_sync()`, `log_error_to_postgres_and_summary()`
- Soporte para PostgreSQL y SQLite
- Logging dual: base de datos + archivo de texto

### 2. **Workflow Simple** (`simple_error_logging.py`)
- Grafo de un solo nodo para logging directo
- Ideal para integración simple en workflows existentes
- Patrón: `log_error → END`

### 3. **Workflow Avanzado** (`advanced_error_workflow.py`)
- Workflow completo con múltiples nodos
- Flujo: `error_handler → log_error → notify_team → resolve_error → END`
- Clasificación automática por severidad
- Notificaciones automáticas al equipo

### 4. **Workflow Completo** (`error_logging_workflow.py`)
- Workflow con validación, logging y reportes
- Manejo de errores del workflow
- Generación de reportes estructurados

## 🎯 **Casos de Uso**

### **Caso 1: Logging Simple**
```python
from langgraph_tools.simple_error_logging import log_error_with_graph

error_data = {
    "error_description": "Error en endpoint /tasks",
    "solution_description": "Corregir validación de modelo",
    "context_info": "Problema en creación de tareas",
    "deployment_id": "railway-123",
    "environment": "production",
    "severity": "high",
    "status": "resolved"
}

result = log_error_with_graph(error_data)
```

### **Caso 2: Workflow Completo**
```python
from langgraph_tools.advanced_error_workflow import run_error_workflow

# El workflow maneja automáticamente:
# 1. Clasificación del error
# 2. Logging en BD y archivo
# 3. Notificación al equipo
# 4. Resolución del error

result = run_error_workflow(error_data)
```

### **Caso 3: Integración en Workflows Existentes**
```python
from langgraph.graph import StateGraph, END
from langgraph_tools.simple_error_logging import log_error_to_postgres_and_summary

# Crear el grafo
graph = StateGraph()

# Agregar nodos existentes
graph.add_node("process_data", process_data_function)
graph.add_node("log_error", log_error_to_postgres_and_summary)

# Conectar nodos
graph.add_edge("process_data", "log_error")
graph.add_edge("log_error", END)

# Compilar y usar
deployment_graph = graph.compile()
```

## 🔧 **Configuración**

### **Variables de Entorno**
```bash
# Para PostgreSQL (Railway)
DATABASE_URL=postgresql://user:pass@host:port/db

# Para SQLite (desarrollo local)
# No es necesario, se usa por defecto
```

### **Dependencias**
```bash
pip install langgraph sqlalchemy aiosqlite psycopg2-binary
```

## 📊 **Estructura de Datos**

### **Input del Error**
```python
error_data = {
    "error_description": "Descripción del problema",
    "solution_description": "Solución implementada",
    "context_info": "Información adicional del contexto",
    "deployment_id": "ID del deployment (opcional)",
    "environment": "production|development|staging",
    "severity": "high|medium|low|info",
    "status": "resolved|pending|investigating"
}
```

### **Output del Workflow**
```python
result = {
    "status": "success|error",
    "workflow_result": {...},  # Estado completo del workflow
    "final_step": "completed|error|unknown",
    "error_resolved": True|False
}
```

## 🚨 **Manejo de Errores**

### **Errores del Sistema de Logging**
- Si falla PostgreSQL, se intenta SQLite
- Si falla la base de datos, se escribe solo en archivo
- Errores del workflow se registran automáticamente

### **Errores del Workflow**
- Validación de campos obligatorios
- Manejo de excepciones en cada nodo
- Logging automático de fallos del workflow

## 📈 **Monitoreo y Reportes**

### **Base de Datos**
```sql
-- Ver logs recientes
SELECT * FROM deployment_logs 
ORDER BY timestamp DESC 
LIMIT 10;

-- Filtrar por severidad
SELECT * FROM deployment_logs 
WHERE severity = 'high' 
AND status = 'pending';
```

### **Archivo de Texto**
- `DEPLOYMENT_SUMMARY.txt` se actualiza automáticamente
- Formato Markdown para fácil lectura
- Historial completo de problemas y soluciones

## 🔄 **Flujos de Trabajo**

### **Flujo Simple**
```
Input → log_error → END
```

### **Flujo Avanzado**
```
Input → error_handler → log_error → notify_team → resolve_error → END
```

### **Flujo Completo**
```
Input → validate → log_error → generate_report → END
```

## 💡 **Mejores Prácticas**

1. **Siempre incluir `error_description`** - Campo obligatorio
2. **Usar `solution_description`** - Documentar la solución implementada
3. **Especificar `environment`** - Para filtrado y análisis
4. **Clasificar `severity`** - Para priorización de problemas
5. **Actualizar `status`** - Mantener estado actualizado

## 🧪 **Testing**

### **Ejecutar Tests Locales**
```bash
# Workflow simple
python langgraph_tools/simple_error_logging.py

# Workflow avanzado
python langgraph_tools/advanced_error_workflow.py

# Workflow completo
python langgraph_tools/error_logging_workflow.py
```

### **Verificar Logs**
```bash
# Verificar base de datos
python scripts/create_deployment_logs_table.py

# Verificar archivo de texto
cat DEPLOYMENT_SUMMARY.txt
```

## 🚀 **Deployment en Railway**

1. **Commit y Push** de todos los archivos
2. **Railway detecta cambios** automáticamente
3. **Deployment automático** con nueva funcionalidad
4. **Verificar logs** en Railway para confirmar funcionamiento

## 📞 **Soporte**

- **Documentación**: Este archivo README
- **Ejemplos**: Archivos de prueba incluidos
- **Logs**: Sistema de logging dual para debugging
- **Workflows**: Múltiples patrones para diferentes necesidades

---

**🎯 El sistema está diseñado para ser robusto, flexible y fácil de integrar en cualquier workflow de LangGraph existente.**
