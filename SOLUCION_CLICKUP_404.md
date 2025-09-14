# 🔧 Solución para 404 en ClickUp OAuth

## 🔍 **Problema Identificado**

El 404 está ocurriendo en **ClickUp mismo** (`app.clickup.com/api/v2/oauth/authorize`), no en tu aplicación local. Esto indica que la aplicación OAuth en ClickUp no está configurada correctamente.

## ✅ **Diagnóstico Realizado**

- ✅ **URL generada correctamente** - La aplicación local genera la URL correcta
- ✅ **URL de ClickUp accesible** - La URL responde con status 200 en pruebas
- ❌ **404 en navegador** - ClickUp muestra 404 cuando accedes desde el navegador

## 🎯 **Causa del Problema**

La aplicación OAuth en ClickUp no está configurada correctamente o no existe. ClickUp rechaza la solicitud de autorización.

## 🛠️ **Solución Paso a Paso**

### **Paso 1: Verificar/Crear Aplicación en ClickUp**

1. **Ve a ClickUp Apps:**
   - Abre: https://app.clickup.com/settings/apps
   - Inicia sesión con tu cuenta de ClickUp

2. **Busca tu aplicación:**
   - Busca "ClickUp Project Manager"
   - Si no existe, crea una nueva

3. **Si NO existe la aplicación:**
   - Haz clic en "Create App"
   - Nombre: `ClickUp Project Manager`
   - Descripción: `Gestión de proyectos con ClickUp`
   - **Redirect URI:** `http://localhost:8000/api/auth/callback`

4. **Si SÍ existe la aplicación:**
   - Haz clic en "Edit" o "Configurar"
   - Verifica que la Redirect URI sea: `http://localhost:8000/api/auth/callback`

### **Paso 2: Configurar Permisos**

Selecciona estos permisos:
- ✅ **read:user** - Leer información del usuario
- ✅ **read:workspace** - Leer información del workspace
- ✅ **read:task** - Leer tareas
- ✅ **write:task** - Escribir/modificar tareas

### **Paso 3: Obtener Credenciales**

Después de crear/editar la aplicación:
1. **Copia el Client ID**
2. **Copia el Client Secret**
3. **Verifica la Redirect URI**

### **Paso 4: Actualizar Configuración Local**

Si las credenciales cambiaron, actualiza tu archivo `.env`:

```env
CLICKUP_OAUTH_CLIENT_ID=tu_nuevo_client_id
CLICKUP_OAUTH_CLIENT_SECRET=tu_nuevo_client_secret
CLICKUP_OAUTH_REDIRECT_URI=http://localhost:8000/api/auth/callback
```

### **Paso 5: Reiniciar Aplicación**

```bash
# Detener aplicación
taskkill /F /IM python.exe

# Iniciar aplicación
python main_simple.py
```

## ⚠️ **Verificaciones Importantes**

### **Redirect URI debe ser EXACTAMENTE:**
```
http://localhost:8000/api/auth/callback
```

**NO debe ser:**
- ❌ `https://localhost:8000/api/auth/callback` (no https)
- ❌ `http://127.0.0.1:8000/api/auth/callback` (no 127.0.0.1)
- ❌ `http://localhost:8000/api/auth/callback/` (no / al final)

### **Estado de la Aplicación:**
- ✅ **Activa** - La aplicación debe estar activa en ClickUp
- ✅ **Permisos configurados** - Los permisos deben estar seleccionados
- ✅ **Redirect URI correcta** - Debe coincidir exactamente

## 🧪 **Probar la Solución**

1. **Configura la aplicación en ClickUp** (pasos 1-3)
2. **Actualiza las credenciales** (paso 4)
3. **Reinicia la aplicación** (paso 5)
4. **Prueba OAuth:**
   - Ve a: http://localhost:8000/api/auth/login
   - Haz clic en "Iniciar con ClickUp"
   - **¡Debería funcionar!**

## 📞 **Si Sigue Sin Funcionar**

1. **Verifica que la aplicación esté activa** en ClickUp
2. **Verifica que los permisos estén seleccionados**
3. **Verifica que la Redirect URI sea exacta**
4. **Espera unos minutos** después de hacer cambios en ClickUp
5. **Limpia la caché del navegador**

## 🎯 **Resultado Esperado**

Después de configurar correctamente la aplicación en ClickUp:
- ✅ ClickUp se abre correctamente
- ✅ Puedes autorizar la aplicación
- ✅ Eres redirigido al dashboard
- ✅ **NO aparece más el 404**

**¡El problema está en la configuración de ClickUp, no en tu código!** 🎉
