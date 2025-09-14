# 🔧 CONFIGURAR PERMISOS EN CLICKUP

## 🎯 Problema Identificado
ClickUp no solicitó permisos específicos al crear la aplicación OAuth, lo que causa que el callback falle.

## 📋 Pasos para Solucionar

### 1️⃣ Ir a la configuración de la app
1. Ve a: https://app.clickup.com/settings/apps
2. Busca tu aplicación "clickuptaskmanager"
3. Haz clic en "Edit" o "Configurar"

### 2️⃣ Configurar permisos
En la sección **"Permissions"** o **"Permisos"**, asegúrate de tener:

- ✅ **read:user** - Leer información del usuario
- ✅ **read:workspace** - Leer información del workspace  
- ✅ **read:task** - Leer tareas
- ✅ **write:task** - Crear/editar tareas

### 3️⃣ Verificar Redirect URI
En la sección **"Redirect URI"** o **"URI de redirección"**, debe ser exactamente:
```
http://localhost:8000/api/auth/callback
```

### 4️⃣ Guardar cambios
1. Haz clic en "Save" o "Guardar"
2. Espera a que se actualice la configuración

## 🧪 Probar la configuración

### Después de configurar los permisos:

1. **Ve a:** http://localhost:8000/api/auth/login
2. **Haz clic en "Iniciar con ClickUp"**
3. **ClickUp debería mostrar una pantalla de permisos** (esto es lo que faltaba)
4. **Acepta los permisos**
5. **ClickUp te redirigirá al dashboard**

## ✅ Verificación

Si todo está configurado correctamente, deberías ver:
- Una pantalla de permisos en ClickUp
- Una redirección automática al dashboard
- Un token de acceso válido

## 🚨 Si sigue sin funcionar

1. **Verifica que la aplicación esté ejecutándose:** `python main_simple.py`
2. **Verifica que el puerto 8000 esté libre**
3. **Revisa los logs de la aplicación**
4. **Asegúrate de que la Redirect URI sea exactamente:** `http://localhost:8000/api/auth/callback`

## 📞 Soporte

Si necesitas ayuda adicional, revisa:
- Los logs de la aplicación en la terminal
- La configuración de la app en ClickUp
- La documentación de ClickUp OAuth
