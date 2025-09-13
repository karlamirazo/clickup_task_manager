# 🔐 Sistema de Autenticación - ClickUp Project Manager

## 📋 Resumen

Este sistema implementa autenticación OAuth 2.0 con ClickUp, permitiendo a los usuarios acceder a sus tareas de manera segura y controlada. Incluye un sistema de roles y permisos granular para diferentes tipos de usuarios.

## 🚀 Características Principales

### ✅ Autenticación OAuth 2.0 con ClickUp
- Integración nativa con ClickUp
- Tokens seguros por usuario
- Renovación automática de tokens
- Redirección automática al login

### ✅ Sistema de Roles y Permisos
- **Administrador**: Acceso completo al sistema
- **Gerente**: Gestión de proyectos y equipos
- **Líder de Equipo**: Supervisión de equipo específico
- **Usuario**: Acceso a sus propias tareas
- **Visualizador**: Solo lectura de tareas asignadas

### ✅ Interfaz de Usuario Moderna
- Pantalla de login/registro responsive
- Integración con ClickUp OAuth
- Gestión de perfiles de usuario
- Dashboard personalizado por rol

## 🛠️ Configuración

### 1. Configurar OAuth en ClickUp

1. Ve a [ClickUp Apps](https://app.clickup.com/settings/apps)
2. Crea una nueva aplicación OAuth
3. Configura:
   - **App Name**: ClickUp Project Manager
   - **Redirect URI**: `http://localhost:8000/api/auth/callback`
   - **Permisos**: `read:user`, `read:workspace`, `read:task`, `write:task`

### 2. Configurar Variables de Entorno

Copia `env.oauth.example` como `.env` y configura:

```bash
# OAuth de ClickUp
CLICKUP_OAUTH_CLIENT_ID=tu_client_id_aqui
CLICKUP_OAUTH_CLIENT_SECRET=tu_client_secret_aqui
CLICKUP_OAUTH_REDIRECT_URI=http://localhost:8000/api/auth/callback

# Seguridad
JWT_SECRET_KEY=tu-clave-secreta-super-segura
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Base de datos
DATABASE_URL=postgresql://usuario:password@localhost:5432/clickup_project_manager
```

### 3. Ejecutar Script de Configuración

```bash
python setup_oauth.py
```

Este script:
- Verifica la configuración
- Prueba las conexiones
- Crea un usuario de prueba
- Genera URL de autorización

## 🔧 Uso

### Iniciar la Aplicación

```bash
python -m uvicorn app.main:app --reload
```

### Acceder al Sistema

1. **Página de Login**: `http://localhost:8000/api/auth/login`
2. **Dashboard**: `http://localhost:8000/dashboard`

### Métodos de Autenticación

#### 1. OAuth con ClickUp (Recomendado)
- Haz clic en "Iniciar con ClickUp"
- Autoriza la aplicación
- Acceso automático a tus tareas

#### 2. Login Tradicional
- Email: `test@example.com`
- Password: `test123`

## 👥 Sistema de Roles

### Administrador
```json
{
  "permissions": [
    "read_all_tasks", "write_all_tasks", "delete_all_tasks",
    "read_users", "write_users", "delete_users",
    "manage_user_roles", "manage_workspace",
    "read_settings", "write_settings",
    "manage_dashboard", "manage_notifications",
    "manage_webhooks", "manage_reports",
    "manage_integrations", "full_admin"
  ]
}
```

### Gerente de Proyecto
```json
{
  "permissions": [
    "read_all_tasks", "write_all_tasks",
    "read_users", "write_users",
    "read_workspace", "write_workspace",
    "read_dashboard", "read_notifications",
    "write_notifications", "read_reports",
    "write_reports"
  ]
}
```

### Usuario Regular
```json
{
  "permissions": [
    "read_own_tasks", "write_own_tasks",
    "read_assigned_tasks", "write_assigned_tasks",
    "read_notifications"
  ]
}
```

## 🔒 Seguridad

### Tokens JWT
- Algoritmo: HS256
- Expiración: 24 horas (configurable)
- Renovación automática

### OAuth 2.0
- State parameter para CSRF protection
- Tokens de acceso seguros
- Renovación automática de tokens

### Middleware de Autenticación
- Verificación automática de tokens
- Redirección a login si no autenticado
- Protección de rutas sensibles

## 📊 API Endpoints

### Autenticación
- `POST /api/auth/login` - Login tradicional
- `POST /api/auth/register` - Registro de usuario
- `GET /api/auth/clickup` - Iniciar OAuth con ClickUp
- `GET /api/auth/callback` - Callback de OAuth
- `GET /api/auth/me` - Información del usuario actual
- `POST /api/auth/logout` - Cerrar sesión
- `POST /api/auth/refresh` - Renovar token

### Permisos
- `GET /api/auth/roles` - Roles disponibles
- `GET /api/auth/permissions` - Permisos del usuario actual

### Perfil
- `PUT /api/auth/profile` - Actualizar perfil
- `POST /api/auth/change-password` - Cambiar contraseña

## 🎨 Interfaz de Usuario

### Pantalla de Login
- Diseño moderno y responsive
- Pestañas para login/registro
- Integración con ClickUp OAuth
- Información de roles disponibles

### Dashboard Personalizado
- Tareas según permisos del usuario
- Navegación basada en roles
- Notificaciones personalizadas

## 🔧 Desarrollo

### Estructura de Archivos
```
auth/
├── __init__.py
├── auth.py              # Autenticación básica
├── oauth.py             # OAuth 2.0 con ClickUp
├── permissions.py       # Sistema de permisos
└── middleware.py        # Middleware de autenticación

api/routes/
└── auth.py              # Rutas de autenticación

api/schemas/
└── auth.py              # Esquemas de datos

static/
└── auth.html            # Interfaz de login
```

### Agregar Nuevos Permisos

1. Definir en `auth/permissions.py`:
```python
class Permission(Enum):
    NEW_PERMISSION = "new_permission"
```

2. Asignar a roles en `PermissionManager.ROLES`

3. Usar en endpoints:
```python
from auth.permissions import Permission
from auth.middleware import require_permission_endpoint

@require_permission_endpoint(Permission.NEW_PERMISSION)
async def my_endpoint():
    pass
```

### Agregar Nuevos Roles

1. Definir en `auth/permissions.py`:
```python
"new_role": Role(
    name="new_role",
    display_name="Nuevo Rol",
    description="Descripción del rol",
    permissions={Permission.READ_OWN_TASKS, ...},
    level=50
)
```

## 🐛 Solución de Problemas

### Error: "OAuth no configurado"
- Verifica que `CLICKUP_OAUTH_CLIENT_ID` y `CLICKUP_OAUTH_CLIENT_SECRET` estén configurados
- Ejecuta `python setup_oauth.py` para verificar

### Error: "Token de ClickUp expirado"
- El token OAuth ha expirado
- Reauténticate con ClickUp OAuth

### Error: "Permiso requerido"
- El usuario no tiene permisos suficientes
- Verifica el rol del usuario en la base de datos

### Error de conexión a ClickUp
- Verifica que `CLICKUP_API_TOKEN` esté configurado
- Verifica la conectividad a internet

## 📈 Monitoreo

### Logs de Autenticación
- Intentos de login exitosos/fallidos
- Renovación de tokens
- Cambios de permisos

### Métricas de Uso
- Usuarios activos por rol
- Tareas accedidas por usuario
- Tiempo de sesión promedio

## 🚀 Despliegue en Producción

### Variables de Entorno
```bash
# OAuth
CLICKUP_OAUTH_CLIENT_ID=prod_client_id
CLICKUP_OAUTH_CLIENT_SECRET=prod_client_secret
CLICKUP_OAUTH_REDIRECT_URI=https://tu-dominio.com/api/auth/callback

# Seguridad
JWT_SECRET_KEY=clave-super-segura-produccion
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Base de datos
DATABASE_URL=postgresql://user:pass@host:port/db
```

### Configuración de ClickUp
- Actualiza la URL de redirección en ClickUp
- Configura permisos mínimos necesarios
- Habilita HTTPS en producción

## 📞 Soporte

Para problemas o preguntas:
1. Revisa los logs de la aplicación
2. Ejecuta `python setup_oauth.py` para diagnóstico
3. Verifica la configuración de OAuth en ClickUp
4. Consulta la documentación de la API de ClickUp

---

**¡Tu sistema de autenticación está listo! 🎉**
