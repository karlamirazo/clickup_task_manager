# 📱 Configuración Manual de WhatsApp Real

## 🎯 Información de Acceso

- **URL Evolution API**: https://evolution-whatsapp-api-production.up.railway.app/manager
- **API Key**: `clickup-whatsapp-2024`
- **Instancia recomendada**: `clickup-manager-final`

## 📋 Pasos para Configuración Manual

### 1. Acceder a la Interfaz Web
1. Ve a: https://evolution-whatsapp-api-production.up.railway.app/manager
2. Si pide autenticación, usa el API Key: `clickup-whatsapp-2024`

### 2. Crear Nueva Instancia
1. Busca el botón "Create Instance" o "Nueva Instancia"
2. Usa estos datos:
   - **Instance Name**: `clickup-manager-final`
   - **Integration**: WhatsApp-Baileys (o similar)
   - **QR Code**: ✅ Habilitado
   - **Webhook**: ❌ Deshabilitado (por ahora)

### 3. Generar Código QR
1. Una vez creada la instancia, busca "Connect" o "Conectar"
2. Debería aparecer un código QR
3. Escanéalo con tu WhatsApp:
   - Abre WhatsApp en tu teléfono
   - Ve a Configuración → Dispositivos vinculados
   - Toca "Vincular dispositivo"
   - Escanea el QR

### 4. Verificar Conexión
1. Una vez escaneado, el estado debería cambiar a "Connected" o "Conectado"
2. Deberías ver tu número de teléfono en la interfaz

## 🔧 Configuración de la Aplicación

Tu aplicación ClickUp ya está configurada con:

```env
WHATSAPP_ENABLED=true
WHATSAPP_SIMULATOR_ENABLED=false
WHATSAPP_EVOLUTION_URL=https://evolution-whatsapp-api-production.up.railway.app
WHATSAPP_EVOLUTION_API_KEY=clickup-whatsapp-2024
WHATSAPP_INSTANCE_NAME=clickup-manager-final
```

## 🧪 Probar Notificaciones

Una vez conectado WhatsApp, puedes probar creando una tarea en ClickUp que incluya un número de teléfono en la descripción:

```
Descripción de tarea: "Contactar cliente en +1234567890 para seguimiento"
```

## ⚠️ Troubleshooting

### Si no aparece el QR:
1. Elimina la instancia y créala de nuevo
2. Espera 2-3 minutos después de crear la instancia
3. Refesca la página

### Si el QR no funciona:
1. Verifica que tu teléfono tenga internet
2. Asegúrate de usar WhatsApp Business si es una cuenta business
3. Intenta con una ventana incógnita del navegador

### Si la conexión se pierde:
1. Ve a la interfaz web
2. Busca tu instancia
3. Presiona "Reconnect" o "Reconectar"

## 📞 Estado de las Notificaciones

Una vez conectado, tu aplicación ClickUp enviará notificaciones WhatsApp automáticamente cuando:

1. ✅ Se cree una nueva tarea con número de teléfono en la descripción
2. ✅ Se asigne una tarea a un usuario
3. ✅ Se actualice el estado de una tarea
4. ✅ Se acerque una fecha límite

Las notificaciones aparecerán como mensajes desde tu número de WhatsApp conectado.
