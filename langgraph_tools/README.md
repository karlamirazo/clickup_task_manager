# ðŸš€ Sistema de Logging de Errores con LangGraph

Este directorio contiene workflows de LangGraph para logging automÃ¡tico de errores de deployment, integrando con el sistema de logging dual (PostgreSQL + DEPLOYMENT_SUMMARY.txt).

## ðŸ“‹ **Componentes del Sistema**

### 1. **Sistema Base de Logging** (`utils/deployment_logger.py`)
- Clase `DeploymentLogger` para logging automÃ¡tico
- Funciones de conveniencia: `log_error_sync()`, `log_error_to_postgres_and_summary()`
- Soporte para PostgreSQL y SQLite
- Logging dual: base de datos + archivo de texto

### 2. **Workflow Simple** (`simple_error_logging.py`)
- Grafo de un solo nodo para logging directo
- Ideal para integraciÃ³n simple en workflows existentes
- PatrÃ³n: `log_error â†’ END`

### 3. **Workflow Avanzado** (`advanced_error_workflow.py`)
- Workflow completo con mÃºltiples nodos
- Flujo: `error_handler â†’ log_error â†’ notify_team â†’ resolve_error â†’ END`
- ClasificaciÃ³n automÃ¡tica por severidad
- Notificaciones automÃ¡ticas al equipo

### 4. **Workflow Completo** (`error_logging_workflow.py`)
- Workflow con validaciÃ³n, logging y reportes
- Manejo de errores del workflow
- GeneraciÃ³n de reportes estructurados

## ðŸŽ¯ **Casos de Uso**

### **Caso 1: Logging Simple**
```python
from langgraph_tools.simple_error_logging import log_error_with_graph

error_data = {
    "error_description": "Error en endpoint /tasks",
    "solution_description": "Corregir validaciÃ³n de modelo",
    "context_info": "Problema en creaciÃ³n de tareas",
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

# El workflow maneja automÃ¡ticamente:
# 1. ClasificaciÃ³n del error
# 2. Logging en BD y archivo
# 3. NotificaciÃ³n al equipo
# 4. ResoluciÃ³n del error

result = run_error_workflow(error_data)
```

### **Caso 3: IntegraciÃ³n en Workflows Existentes**
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

## ðŸ”§ **ConfiguraciÃ³n**

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

## ðŸ“Š **Estructura de Datos**

### **Input del Error**
```python
error_data = {
    "error_description": "DescripciÃ³n del problema",
    "solution_description": "SoluciÃ³n implementada",
    "context_info": "InformaciÃ³n adicional del contexto",
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

## ðŸš¨ **Manejo de Errores**

### **Errores del Sistema de Logging**
- Si falla PostgreSQL, se intenta SQLite
- Si falla la base de datos, se escribe solo en archivo
- Errores del workflow se registran automÃ¡ticamente

### **Errores del Workflow**
- ValidaciÃ³n de campos obligatorios
- Manejo de excepciones en cada nodo
- Logging automÃ¡tico de fallos del workflow

## ðŸ“ˆ **Monitoreo y Reportes**

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
- `DEPLOYMENT_SUMMARY.txt` se actualiza automÃ¡ticamente
- Formato Markdown para fÃ¡cil lectura
- Historial completo de problemas y soluciones

## ðŸ”„ **Flujos de Trabajo**

### **Flujo Simple**
```
Input â†’ log_error â†’ END
```

### **Flujo Avanzado**
```
Input â†’ error_handler â†’ log_error â†’ notify_team â†’ resolve_error â†’ END
```

### **Flujo Completo**
```
Input â†’ validate â†’ log_error â†’ generate_report â†’ END
```

## ðŸ’¡ **Mejores PrÃ¡cticas**

1. **Siempre incluir `error_description`** - Campo obligatorio
2. **Usar `solution_description`** - Documentar la soluciÃ³n implementada
3. **Especificar `environment`** - Para filtrado y anÃ¡lisis
4. **Clasificar `severity`** - Para priorizaciÃ³n de problemas
5. **Actualizar `status`** - Mantener estado actualizado

## ðŸ§ª **Testing**

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

## ðŸš€ **Deployment en Railway**

1. **Commit y Push** de todos los archivos
2. **Railway detecta cambios** automÃ¡ticamente
3. **Deployment automÃ¡tico** con nueva funcionalidad
4. **Verificar logs** en Railway para confirmar funcionamiento

## ðŸ“ž **Soporte**

- **DocumentaciÃ³n**: Este archivo README
- **Ejemplos**: Archivos de prueba incluidos
- **Logs**: Sistema de logging dual para debugging
- **Workflows**: MÃºltiples patrones para diferentes necesidades

---

**ðŸŽ¯ El sistema estÃ¡ diseÃ±ado para ser robusto, flexible y fÃ¡cil de integrar en cualquier workflow de LangGraph existente.**
