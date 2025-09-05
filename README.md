# ClickUp Project Manager - Agente Inteligente

Un módulo completo de gestión de tareas con la API de ClickUp que incluye automatización, reportes e integraciones.

## 🚀 Características

### Gestión de Tareas
- ✅ Crear, actualizar y eliminar tareas
- ✅ Gestión de espacios de trabajo, listas y usuarios
- ✅ Búsqueda y filtrado avanzado
- ✅ Operaciones masivas (bulk operations)
- ✅ Sincronización bidireccional con ClickUp

### Automatización
- ✅ Reglas de automatización personalizables
- ✅ Triggers basados en eventos de tareas
- ✅ Acciones automáticas (asignaciones, fechas límite, etiquetas)
- ✅ Ejecución manual y programada
- ✅ Monitoreo de ejecuciones y errores

### Reportes
- ✅ Resumen de tareas por estado y prioridad
- ✅ Análisis de rendimiento de usuarios
- ✅ Línea de tiempo de tareas
- ✅ Vista general del workspace
- ✅ Reportes personalizables con filtros
- ✅ Exportación en formato JSON

### Integraciones
- ✅ CRMs (Salesforce, HubSpot, Pipedrive)
- ✅ Bases de datos (PostgreSQL, MySQL, MongoDB)
- ✅ Herramientas de productividad (Slack, Teams, Google Workspace)
- ✅ Gestión de proyectos (Jira, Asana, Trello)
- ✅ Pruebas de conexión y sincronización

### 🆕 **Nueva Funcionalidad: Notificaciones por WhatsApp**
- ✅ Campo de teléfono en formulario de creación de tareas
- ✅ Integración automática del teléfono en descripción de ClickUp
- ✅ Sistema de notificaciones por WhatsApp configurado
- ✅ Preview en tiempo real de la descripción final
- ✅ Validación automática del formato del número

## 🏗️ Arquitectura

```
ClickUp Project Manager/
├── app/                   # Aplicación principal
│   └── main.py           # Punto de entrada de la aplicación
├── auth/                  # Sistema de autenticación
│   └── auth.py           # Módulo de autenticación
├── integrations/          # Integraciones externas
│   ├── clickup/          # Integración con ClickUp API
│   ├── whatsapp/         # Integración con WhatsApp Evolution API
│   └── evolution_api/    # Configuración Evolution API
├── monitoring/            # Monitoreo y alertas
│   ├── railway/          # Monitoreo de Railway
│   └── health/           # Health checks
├── search/               # Motor de búsqueda
│   └── engine.py         # Motor de búsqueda semántica
├── notifications/        # Sistema de notificaciones
│   ├── email/           # Plantillas de email
│   └── whatsapp/        # Notificaciones WhatsApp
├── scripts/             # Scripts organizados por categoría
│   ├── clickup/         # Scripts ClickUp
│   ├── whatsapp/        # Scripts WhatsApp
│   ├── railway/         # Scripts Railway
│   └── database/        # Scripts de base de datos
├── api/                 # API REST con FastAPI
│   ├── routes/          # Endpoints de la API
│   └── schemas/         # Esquemas Pydantic
├── core/                # Núcleo del sistema
│   ├── config.py         # Configuración de la aplicación
│   ├── database.py       # Configuración de base de datos
│   └── clickup_client.py # Cliente de ClickUp API
├── models/               # Modelos de SQLAlchemy
├── utils/                # Utilidades y helpers
├── data/                 # Datos y reportes generados
├── logs/                 # Archivos de log
├── static/               # Archivos estáticos (Dashboard HTML)
├── templates/            # Plantillas HTML
└── tests/                # Tests unitarios y de integración
```

## 🛠️ Tecnologías

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Base de datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **API**: ClickUp API v2
- **Autenticación**: JWT
- **Documentación**: OpenAPI/Swagger
- **Tests**: pytest, pytest-asyncio
- **Frontend**: HTML5, CSS3, JavaScript (Dashboard responsivo)

## 📦 Instalación

### Prerrequisitos

- Python 3.8+
- pip
- ClickUp API Token

### Pasos de instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/karlamirazo/clickup_task_manager.git
cd clickup_task_manager
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp env.example .env
# Editar .env con tus credenciales de ClickUp
```

5. **Inicializar base de datos**
```bash
python -c "from core.database import init_db; import asyncio; asyncio.run(init_db())"
```

6. **Ejecutar la aplicación**
```bash
uvicorn app.main:app --reload
```

La aplicación estará disponible en `http://localhost:8000`

## 🎯 Configuración

### Variables de entorno principales

```env
# ClickUp API
CLICKUP_API_TOKEN=your_clickup_api_token_here

# Base de datos
DATABASE_URL=sqlite:///./clickup_manager.db

# Configuración de la aplicación
DEBUG=True
HOST=0.0.0.0
PORT=8000

# WhatsApp Evolution API (NUEVO)
WHATSAPP_ENABLED=True
WHATSAPP_EVOLUTION_URL=http://localhost:8080
WHATSAPP_EVOLUTION_API_KEY=your_api_key_here
```

### Obtener API Token de ClickUp

1. Ve a [ClickUp Settings](https://app.clickup.com/settings)
2. Navega a "Apps" → "API Token"
3. Crea un nuevo token con los permisos necesarios
4. Copia el token a tu archivo `.env`

## 📱 Uso del Dashboard

### Acceder al Dashboard

1. Inicia el servidor: `python main.py`
2. Abre tu navegador en: `http://localhost:8000`
3. Navega al dashboard principal

### Crear Tarea con Notificaciones WhatsApp

1. Haz click en "Crear Nueva Tarea"
2. Llena el formulario incluyendo:
   - Nombre de la tarea
   - Descripción (opcional)
   - **📱 Número de Celular** ← **¡NUEVO!**
   - Usuario asignado
   - Estado, prioridad, fecha límite
   - Lista y workspace de ClickUp
3. El número de teléfono se incluirá automáticamente en la descripción
4. Las notificaciones por WhatsApp se enviarán automáticamente

## 🔌 Uso de la API

### Autenticación

La API utiliza autenticación basada en tokens. Incluye tu API token de ClickUp en el header:

```bash
Authorization: your_clickup_api_token_here
```

### Endpoints principales

#### Tareas
```bash
# Crear tarea
POST /api/v1/tasks/
{
  "name": "Nueva tarea",
  "description": "Descripción de la tarea",
  "list_id": "list_id",
  "workspace_id": "workspace_id",
  "assignee_id": "user_id",
  "priority": 3,
  "due_date": "2024-01-15T10:00:00Z"
}

# Obtener tareas
GET /api/v1/tasks/?workspace_id=workspace_id&status=in_progress

# Actualizar tarea
PUT /api/v1/tasks/{task_id}
{
  "status": "complete",
  "priority": 1
}

# Eliminar tarea
DELETE /api/v1/tasks/{task_id}
```

#### Workspaces
```bash
# Obtener workspaces
GET /api/v1/workspaces/

# Obtener workspace específico
GET /api/v1/workspaces/{workspace_id}

# Sincronizar workspace
POST /api/v1/workspaces/{workspace_id}/sync
```

## 🚀 Despliegue

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/clickup_manager
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: clickup_manager
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
  
  redis:
    image: redis:6-alpine
```

## 🧪 Testing

### Ejecutar tests

```bash
# Tests unitarios
pytest tests/unit/

# Tests de integración
pytest tests/integration/

# Todos los tests
pytest tests/

# Con cobertura
pytest --cov=. tests/
```

## 📊 Monitoreo y Logs

### Configuración de logs

```python
# En core/config.py
LOG_LEVEL = "INFO"
LOG_FILE = "logs/app.log"
```

### Niveles de log

- `DEBUG`: Información detallada para desarrollo
- `INFO`: Información general de la aplicación
- `WARNING`: Advertencias que no impiden la ejecución
- `ERROR`: Errores que afectan la funcionalidad
- `CRITICAL`: Errores críticos que pueden detener la aplicación

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

- **Documentación**: [Wiki del proyecto](link-to-wiki)
- **Issues**: [GitHub Issues](link-to-issues)
- **Email**: support@clickup-manager.com

## 🗺️ Roadmap

### Próximas características

- [x] Dashboard web con interfaz moderna
- [x] Campo de teléfono para notificaciones WhatsApp
- [x] Sistema de notificaciones automáticas
- [ ] Gráficos interactivos en tiempo real
- [ ] Notificaciones push en tiempo real
- [ ] Integración con más CRMs
- [ ] API GraphQL
- [ ] Mobile app
- [ ] Machine Learning para predicciones
- [ ] Workflows visuales para automatizaciones
- [ ] Exportación a Excel/PDF
- [ ] Integración con calendarios
- [ ] Sistema de permisos granular

### Mejoras técnicas

- [ ] Cache distribuido con Redis
- [ ] Background jobs con Celery
- [ ] Métricas con Prometheus
- [ ] Logs centralizados
- [ ] CI/CD pipeline
- [ ] Tests de carga
- [ ] Documentación automática
- [ ] Monitoreo de performance

---

**ClickUp Project Manager** - Potenciando la productividad con automatización inteligente 🚀

*Última actualización: Campo de teléfono para notificaciones WhatsApp implementado ✅*
