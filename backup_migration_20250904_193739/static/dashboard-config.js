/**
 * Configuración del Dashboard
 * ClickUp Project Manager
 */

// Configuración global del dashboard
window.dashboardConfig = {
    // Configuración de actualización automática
    autoRefresh: {
        enabled: false,  // Deshabilitado según los requerimientos
        interval: 30000  // 30 segundos (no se usa)
    },
    
    // Configuración de sincronización
    sync: {
        manualOnly: true,  // Solo sincronización manual
        autoSyncDisabled: true
    },
    
    // Configuración de gráficos
    charts: {
        enabled: true,
        defaultPeriod: '1h'
    },
    
    // Configuración de notificaciones
    notifications: {
        enabled: true,
        limit: 50
    },
    
    // Configuración de la tabla de tareas
    taskTable: {
        enabled: true,
        limit: 100,
        includeCompleted: true
    },
    
    // URLs de la API
    api: {
        baseUrl: '/api/v1',
        endpoints: {
            dashboard: '/dashboard',
            tasks: '/tasks',
            sync: '/tasks/sync'
        }
    }
};

console.log('✅ Dashboard config loaded');