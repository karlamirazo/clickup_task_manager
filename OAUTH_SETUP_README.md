# 🔐 Configuración de Autenticación OAuth con ClickUp

Este documento explica cómo configurar y usar la autenticación OAuth 2.0 con ClickUp en el ClickUp Project Manager.

## 📋 Requisitos Previos

- Python 3.8 o superior
- PostgreSQL ejecutándose
- Cuenta de ClickUp con permisos de administrador
- Acceso a la configuración de aplicaciones de ClickUp

## 🚀 Configuración Rápida

### 1. Configurar OAuth en ClickUp

1. Ve a [https://app.clickup.com/settings/apps](https://app.clickup.com/settings/apps)
2. Haz clic en **"Create App"**
3. Completa la información:
   - **App Name**: `ClickUp Project Manager`
   - **Description**: `Gestión de proyectos con ClickUp`
   - **Redirect URI**: `http://localhost:8000/api/auth/callback`
4. Selecciona los siguientes permisos:
   - ✅ `read:user` - Leer información del usuario
   - ✅ `read:workspace` - Leer información del workspace
   - ✅ `read:task` - Leer tareas
   - ✅ `write:task` - Crear y modificar tareas
5. Copia el **Client ID** y **Client Secret**

### 2. Configurar Variables de Entorno

```bash
# Copia el archivo de ejemplo
cp env.oauth.local.example .env

# Edita el archivo .env con tus credenciales
nano .env
```

Configura las siguientes variables:

```env
# OAuth de ClickUp
CLICKUP_OAUTH_CLIENT_ID=tu_client_id_aqui
CLICKUP_OAUTH_CLIENT_SECRET=tu_client_secret_aqui
CLICKUP_OAUTH_REDIRECT_URI=http://localhost:8000/api/auth/callback

# Base de datos
DATABASE_URL=postgresql://postgres:admin123@localhost:5432/clickup_project_manager

# Seguridad
JWT_SECRET_KEY=tu-clave-secreta-super-segura-aqui
```

### 3. Iniciar la Aplicación

```bash
# Opción 1: Script de inicio rápido
python start_oauth_app.py

# Opción 2: Inicio manual
python -m uvicorn app.main:app --reload
```

### 4. Probar la Autenticación

1. Ve a [http://localhost:8000/api/auth/login](http://localhost:8000/api/auth/login)
2. Haz clic en **"Iniciar con ClickUp"**
3. Completa la autorización en ClickUp
4. Serás redirigido de vuelta al dashboard

## 🧪 Scripts de Prueba

### Verificar Configuración

```bash
# Verificar configuración OAuth
python setup_oauth.py

# Probar endpoints de autenticación
python test_oauth_auth.py
```

### Configuración Automática

```bash
# Configurar OAuth paso a paso
python setup_oauth.py
```

## 🔧 Funcionalidades Implementadas

### ✅ Autenticación OAuth 2.0
- Integración completa con ClickUp OAuth
- Generación automática de URLs de autorización
- Manejo seguro de estados OAuth
- Redirección automática después de la autenticación

### ✅ Gestión de Usuarios
- Creación automática de usuarios desde ClickUp
- Sincronización de datos de perfil
- Actualización de información de usuario
- Gestión de roles y permisos

### ✅ Interfaz de Usuario
- Página de login moderna y responsive
- Soporte para autenticación tradicional y OAuth
- Manejo de errores y mensajes informativos
- Redirección automática después del login

### ✅ Seguridad
- Validación de estados OAuth
- Tokens JWT seguros
- Manejo de errores de autenticación
- Configuración de CORS apropiada

## 📁 Archivos Modificados

- `core/config.py` - Configuración OAuth dinámica
- `static/auth.html` - Interfaz de autenticación mejorada
- `api/routes/auth.py` - Rutas de autenticación actualizadas
- `auth/oauth.py` - Lógica OAuth existente (sin cambios)

## 📁 Archivos Nuevos

- `env.oauth.local.example` - Plantilla de configuración
- `test_oauth_auth.py` - Script de pruebas
- `start_oauth_app.py` - Script de inicio rápido
- `OAUTH_SETUP_README.md` - Esta documentación

## 🔍 Solución de Problemas

### Error: "OAuth no configurado"
- Verifica que las variables `CLICKUP_OAUTH_CLIENT_ID` y `CLICKUP_OAUTH_CLIENT_SECRET` estén configuradas en `.env`

### Error: "State inválido o expirado"
- Los estados OAuth expiran en 5 minutos
- Intenta autenticarte nuevamente

### Error: "Error de conexión con ClickUp"
- Verifica tu conexión a internet
- Confirma que las credenciales de ClickUp sean correctas

### Error: "No se puede conectar al servidor"
- Asegúrate de que la aplicación esté ejecutándose en el puerto 8000
- Verifica que no haya otros procesos usando el puerto

## 🌐 Configuración para Producción

Para desplegar en producción:

1. Cambia la URL de redirección en ClickUp a tu dominio de producción
2. Actualiza `CLICKUP_OAUTH_REDIRECT_URI` en las variables de entorno
3. Configura una clave JWT segura
4. Habilita HTTPS

```env
# Producción
CLICKUP_OAUTH_REDIRECT_URI=https://tu-dominio.com/api/auth/callback
JWT_SECRET_KEY=clave-super-segura-para-produccion
ENVIRONMENT=production
```

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs de la aplicación
2. Ejecuta `python test_oauth_auth.py` para diagnosticar
3. Verifica la configuración de ClickUp
4. Consulta la documentación de la API de ClickUp

---

**¡La autenticación OAuth con ClickUp está lista para usar!** 🎉

