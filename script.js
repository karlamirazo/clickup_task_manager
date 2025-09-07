// Variables globales
let currentTab = 'dashboard';
let tasks = [];
let workspaces = [];

// Interceptor de fetch para forzar HTTPS en Railway
if (window.location.hostname.includes('railway.app')) {
    console.log('INFO: Aplicando interceptor de fetch para Railway...');
    
    // Guardar el fetch original
    const originalFetch = window.fetch;
    
    // Crear interceptor personalizado
    window.fetch = function(url, options = {}) {
        // Convertir URL a string si es necesario
        let urlString = url.toString();
        
        console.log('INFO: Interceptando fetch para URL:', urlString);
        
        // Si la URL es HTTP, convertir a HTTPS
        if (urlString.startsWith('http://')) {
            urlString = urlString.replace('http://', 'https://');
            console.log('INFO: URL convertida a HTTPS:', urlString);
        }
        
        // Si la URL es relativa y estamos en Railway, hacerla absoluta HTTPS
        if (urlString.startsWith('/')) {
            urlString = `https://${window.location.host}${urlString}`;
            console.log('INFO: URL relativa convertida a HTTPS absoluta:', urlString);
        }
        
        console.log('INFO: Realizando fetch a:', urlString);
        
        // Agregar headers para forzar HTTPS
        const httpsOptions = {
            ...options,
            headers: {
                ...options.headers,
                'Upgrade-Insecure-Requests': '1'
            }
        };
        
        // Llamar al fetch original con la URL modificada
        return originalFetch(urlString, httpsOptions);
    };
    
    console.log('SUCCESS: Interceptor de fetch aplicado exitosamente');
}

// Variables globales para reportes
let reportCharts = {};

// Función simple para reconstruir índice de búsqueda
window.rebuildSearchIndex = function() {
    console.log('INFO: Reconstruyendo índice de búsqueda...');
    // Esta función se implementará más adelante
    alert('Función de reconstrucción de índice en desarrollo');
};

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Inicializar la aplicación
async function initializeApp() {
    console.log('INFO: Inicializando ClickUp Project Manager...');
    
    // Configurar navegación por tabs
    setupTabNavigation();
    
    // Verificar estado del sistema
    await checkSystemStatus();
    
    // Cargar datos iniciales
    await loadInitialData();
    
    // Cargar workspaces para el formulario de tareas
    console.log('INFO: Cargando workspaces para formulario de tareas...');
    try {
        console.log('DEBUG: Antes de llamar a loadWorkspacesForTask');
        await loadWorkspacesForTask();
        console.log('SUCCESS: Workspaces cargados exitosamente');
        
        // Verificar que se estableció el workspace por defecto
        const workspaceSelect = document.getElementById('task-workspace');
        if (workspaceSelect) {
            console.log('DEBUG: Después de cargar workspaces - Valor del select:', workspaceSelect.value);
            console.log('DEBUG: Después de cargar workspaces - Opciones disponibles:', workspaceSelect.options.length);
        }
    } catch (error) {
        console.error('ERROR: Error cargando workspaces:', error);
    }
    
    // Configurar eventos
    setupEventListeners();
    
    // Cargar tareas al inicio para asegurar que se muestren
    console.log('INFO: Cargando tareas al inicio...');
    await loadTasks();
    
    // Mostrar el tab de tareas por defecto
    console.log('INFO: Mostrando tab de tareas por defecto...');
    switchTab('tasks');
}

// Configurar navegación por tabs
function setupTabNavigation() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            switchTab(targetTab);
        });
    });
}

// Cambiar de tab
function switchTab(tabName) {
    // Actualizar botones
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Actualizar contenido
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');
    
    currentTab = tabName;
    
    // Cargar datos específicos del tab
    loadTabData(tabName);
}

// Cargar datos específicos del tab
async function loadTabData(tabName) {
    switch(tabName) {
        case 'dashboard':
            await loadDashboardData();
            break;
        case 'tasks':
            await loadTasks();
            break;
        case 'workspaces':
            await loadWorkspaces();
            break;
        case 'automation':
            await loadAutomations();
            break;
        case 'reports':
            await loadReports();
            break;
    }
}

// Verificar estado del sistema
async function checkSystemStatus() {
    console.log('INFO: Verificando estado del sistema...');
    
    // Verificar servidor
    try {
        const response = await fetch('/health');
        if (response.ok) {
            updateStatus('server-status', 'success', 'Conectado');
            updateConnectionStatus('connected', 'Conectado');
        } else {
            updateStatus('server-status', 'error', 'Error');
            updateConnectionStatus('error', 'Error de conexión');
        }
    } catch (error) {
        updateStatus('server-status', 'error', 'Sin conexión');
        updateConnectionStatus('error', 'Sin conexión');
    }
    
    // Verificar ClickUp API
    try {
        const response = await fetch('/api/v1/workspaces/');
        if (response.ok) {
            updateStatus('clickup-status', 'success', 'Conectado');
        } else {
            updateStatus('clickup-status', 'error', 'Error');
        }
    } catch (error) {
        updateStatus('clickup-status', 'error', 'Sin conexión');
    }
    
    // Verificar base de datos
    try {
        const response = await fetch('/api/v1/dashboard/health');
        if (response.ok) {
            const healthData = await response.json();
            if (healthData.services && healthData.services.database && healthData.services.database.status === 'healthy') {
                updateStatus('db-status', 'success', 'Conectado');
            } else {
                updateStatus('db-status', 'error', 'Error en BD');
            }
        } else {
            updateStatus('db-status', 'error', 'Error');
        }
    } catch (error) {
        updateStatus('db-status', 'error', 'Sin conexión');
    }
}

// Actualizar estado
function updateStatus(elementId, status, text) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = text;
        element.className = `status ${status}`;
    }
}

// Actualizar estado de conexión
function updateConnectionStatus(status, text) {
    const element = document.getElementById('connection-status');
    if (element) {
        element.textContent = text;
        element.className = `status-badge ${status}`;
    }
}

// Cargar datos iniciales
async function loadInitialData() {
    console.log('INFO: Cargando datos iniciales...');
    
    // Cargar estadísticas del dashboard
    await loadDashboardData();
}

// Cargar datos del dashboard
async function loadDashboardData() {
    try {
        // Cargar TODAS las tareas (incluidas completadas), paginando hasta 100 por página
        const allTasks = await fetchAllTasksForDashboard();
        updateDashboardStats(allTasks);
    } catch (error) {
        console.error('Error cargando datos del dashboard:', error);
    }
}

// Actualizar estadísticas del dashboard
function updateDashboardStats(tasksArray) {
    const tasks = Array.isArray(tasksArray)
        ? tasksArray
        : (tasksArray && Array.isArray(tasksArray.tasks) ? tasksArray.tasks : []);

    const totalTasks = tasks.length;
    const completedTasks = tasks.filter(t => (t.status || '').toLowerCase() === 'complete').length;
    const pendingTasks = totalTasks - completedTasks;

    const totalEl = document.getElementById('total-tasks');
    const pendingEl = document.getElementById('pending-tasks');
    const completedEl = document.getElementById('completed-tasks');
    if (totalEl) totalEl.textContent = totalTasks;
    if (pendingEl) pendingEl.textContent = pendingTasks;
    if (completedEl) completedEl.textContent = completedTasks;
}

// Función para actualizar manualmente los contadores del dashboard
async function refreshDashboardCounters() {
    console.log('INFO: Actualizando contadores del dashboard...');
    
    try {
        // Mostrar indicador de carga en el botón
        const refreshBtn = document.querySelector('[onclick="refreshDashboardCounters()"]');
        if (refreshBtn) {
            const originalContent = refreshBtn.innerHTML;
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            
            // Actualizar contadores
            await loadDashboardData();
            
            // Restaurar botón
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = originalContent;
            
            showNotification('Contadores actualizados correctamente', 'success');
        }
    } catch (error) {
        console.error('Error actualizando contadores:', error);
        showNotification('Error al actualizar contadores', 'error');
        
        // Restaurar botón en caso de error
        const refreshBtn = document.querySelector('[onclick="refreshDashboardCounters()"]');
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
        }
    }
}

// Obtener todas las tareas para el dashboard (incluye completadas)
async function fetchAllTasksForDashboard() {
    const all = [];
    let page = 0;
    const limit = 100; // máximo permitido por el backend
    while (true) {
        const resp = await fetch(`/api/v1/tasks/?include_closed=true&page=${page}&limit=${limit}`);
        if (!resp.ok) break;
        const data = await resp.json();
        const batch = data.tasks || [];
        all.push(...batch);
        if (!data.has_more) break;
        page += 1;
    }
    return all;
}

// Cargar tareas
async function loadTasks() {
    console.log('INFO: Cargando tareas...');
    
    try {
        const response = await fetch('/api/v1/tasks/?include_closed=true&page=0&limit=100');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const tasks = await response.json();
        console.log('SUCCESS: Tareas cargadas:', tasks.length);
        
        // Mostrar las tareas
        displayTasks(tasks);
        
        // Actualizar contadores del dashboard
        await updateDashboardCounters();
        
        // Actualizar estadísticas específicas si estamos en el dashboard
        if (document.getElementById('total-tasks')) {
            document.getElementById('total-tasks').textContent = tasks.length;
            
            // Contar tareas por estado
            const pendingTasks = tasks.filter(t => t.status === 'to do' || t.status === 'todo').length;
            const completedTasks = tasks.filter(t => t.status === 'complete' || t.status === 'completed').length;
            
            document.getElementById('pending-tasks').textContent = pendingTasks;
            document.getElementById('completed-tasks').textContent = completedTasks;
        }
        
    } catch (error) {
        console.error('ERROR: Error cargando tareas:', error);
        showNotification(
            `Error cargando tareas: ${error.message}`,
            'error'
        );
        
        // Mostrar mensaje de error en la interfaz
        const tasksList = document.getElementById('tasks-list');
        if (tasksList) {
            tasksList.innerHTML = `
                <div class="error">
                    <i class="fas fa-exclamation-triangle"></i>
                    Error cargando tareas: ${error.message}
                </div>
            `;
        }
    }
}

async function syncAllTasks() {
    console.log('INFO: Sincronizando tareas con ClickUp...');
    
    try {
        const button = document.querySelector('[onclick="syncAllTasks()"]');
        if (button) {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sincronizando...';
        }
        
        // Obtener el workspace_id del select o usar el por defecto
        let workspaceId = '9014943317'; // Workspace ID por defecto
        
        // Intentar obtener del select si existe
        const workspaceSelect = document.getElementById('task-workspace');
        if (workspaceSelect && workspaceSelect.value) {
            workspaceId = workspaceSelect.value;
        }
        
        // Si no hay workspace_id válido, intentar obtener el primero disponible
        if (!workspaceId || workspaceId === '') {
            try {
                const workspacesResponse = await fetch('/api/v1/workspaces/');
                if (workspacesResponse.ok) {
                    const workspacesData = await workspacesResponse.json();
                    if (workspacesData.workspaces && workspacesData.workspaces.length > 0) {
                        workspaceId = workspacesData.workspaces[0].clickup_id;
                        console.log('DEBUG: Usando primer workspace disponible:', workspaceId);
                    }
                }
            } catch (error) {
                console.warn('WARNING: No se pudo obtener workspace automáticamente, usando por defecto');
            }
        }
        
        console.log('DEBUG: Workspace ID a usar para sincronización:', workspaceId);
        
        let response;
        
        // Intentar primero con el endpoint normal
        if (workspaceId && workspaceId !== '') {
            try {
                response = await fetch('/api/v1/tasks/sync?workspace_id=' + workspaceId, {
                    method: 'POST'
                });
                console.log('DEBUG: Usando endpoint normal con workspace_id:', workspaceId);
            } catch (error) {
                console.warn('WARNING: Error con endpoint normal, usando endpoint simple');
                response = await fetch('/api/v1/tasks/sync-simple', {
                    method: 'POST'
                });
            }
        } else {
            // Si no hay workspace_id, usar el endpoint simple
            console.log('DEBUG: Usando endpoint simple (sin workspace_id)');
            response = await fetch('/api/v1/tasks/sync-simple', {
                method: 'POST'
            });
        }
        
        if (response.ok) {
            const data = await response.json();
            console.log(`SUCCESS: Sincronización completada:`, data);
            
            // Obtener el número total de tareas sincronizadas
            const totalTasks = data.total_tasks_synced || 0;
            const newTasks = data.total_tasks_created || 0;
            const updatedTasks = data.total_tasks_updated || 0;
            
            // Mostrar notificación de éxito
            showNotification(
                `Sincronizadas ${totalTasks} tareas correctamente (${newTasks} nuevas, ${updatedTasks} actualizadas)`,
                'success'
            );
            
            // Recargar las tareas para mostrar los cambios
            await loadTasks();
            
            // Actualizar contadores del dashboard
            await updateDashboardCounters();
            
            // Actualizar contadores del Kanban Board si estamos en esa página
            if (typeof updateKanbanCounters === 'function') {
                await updateKanbanCounters();
            }
            
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error en la sincronización');
        }
        
    } catch (error) {
        console.error('ERROR: Error en sincronización:', error);
        showNotification(
            `Error en sincronización: ${error.message}`,
            'error'
        );
    } finally {
        // Restaurar el botón
        const button = document.querySelector('[onclick="syncAllTasks()"]');
        if (button) {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-sync-alt"></i> Sincronizar';
        }
    }
}

// Mostrar tareas
function displayTasks(tasksToShow) {
    console.log('INFO: displayTasks llamada con:', tasksToShow.length, 'tareas');
    
    const tasksList = document.getElementById('tasks-list');
    
    if (!tasksList) {
        console.error('ERROR: No se encontró el elemento tasks-list');
        return;
    }
    
    if (!Array.isArray(tasksToShow) || tasksToShow.length === 0) {
        console.log('INFO: No hay tareas para mostrar');
        tasksList.innerHTML = '<div class="empty-state">No hay tareas disponibles</div>';
        return;
    }
    
    console.log('SUCCESS: Generando HTML para', tasksToShow.length, 'tareas');
    
    const tasksHTML = tasksToShow.map(task => {
        console.log('DEBUG: Procesando tarea:', task.name, 'ID:', task.id || task.clickup_id);
        
        return `
            <div class="task-item">
                <div class="task-header">
                    <div>
                        <div class="task-title">${task.name || 'Sin título'}</div>
                        <div class="task-description">${task.description || 'Sin descripción'}</div>
                    </div>
                    <div class="task-actions">
                        <button class="btn btn-secondary" onclick="editTask('${task.clickup_id || task.id}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-danger" onclick="deleteTask('${task.clickup_id || task.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="task-meta">
                    <span><i class="fas fa-tag"></i> ${task.status || 'Sin estado'}</span>
                    <span><i class="fas fa-flag"></i> Prioridad ${task.priority || 'N/A'}</span>
                    <span><i class="fas fa-user"></i> ${task.assignee_name || task.assignee_id || 'Sin asignar'}</span>
                    <span><i class="fas fa-calendar"></i> ${formatDate(task.due_date)}</span>
                </div>
            </div>
        `;
    }).join('');
    
    console.log('SUCCESS: HTML generado, actualizando DOM');
    tasksList.innerHTML = tasksHTML;
    console.log('SUCCESS: Tareas mostradas correctamente');
}

// Cargar workspaces
async function loadWorkspaces() {
    console.log('INFO: Cargando workspaces...');
    
    const workspacesList = document.getElementById('workspaces-list');
    workspacesList.innerHTML = '<div class="loading">Cargando workspaces...</div>';
    
    try {
        const response = await fetch('/api/v1/workspaces/');
        if (response.ok) {
            const data = await response.json();
            workspaces = data.workspaces || data.items || [];
            displayWorkspaces(workspaces);
        } else {
            workspacesList.innerHTML = '<div class="error">Error cargando workspaces</div>';
        }
    } catch (error) {
        console.error('Error cargando workspaces:', error);
        workspacesList.innerHTML = '<div class="error">Error de conexión</div>';
    }
}

// Mostrar workspaces
function displayWorkspaces(workspacesToShow) {
    const workspacesList = document.getElementById('workspaces-list');
    
    if (workspacesToShow.length === 0) {
        workspacesList.innerHTML = '<div class="empty-state">No hay workspaces disponibles</div>';
        return;
    }
    
    const workspacesHTML = workspacesToShow.map(workspace => `
        <div class="workspace-item">
            <h3>${workspace.name || 'Sin nombre'}</h3>
            <p>ID: ${workspace.id || 'N/A'}</p>
            <div class="workspace-actions">
                <button class="btn btn-secondary" onclick="viewWorkspaceDetails('${workspace.id}')">
                    <i class="fas fa-eye"></i> Ver detalles
                </button>
            </div>
        </div>
    `).join('');
    
    workspacesList.innerHTML = workspacesHTML;
}

// Cargar automatizaciones
async function loadAutomations() {
    console.log('INFO: Cargando automatizaciones...');
    
    const automationList = document.getElementById('automation-list');
    automationList.innerHTML = '<div class="loading">Cargando automatizaciones...</div>';
    
    try {
        const response = await fetch('/api/v1/automation');
        if (response.ok) {
            const data = await response.json();
            displayAutomations(data.items || []);
        } else {
            automationList.innerHTML = '<div class="error">Error cargando automatizaciones</div>';
        }
    } catch (error) {
        console.error('Error cargando automatizaciones:', error);
        automationList.innerHTML = '<div class="error">Error de conexión</div>';
    }
}

// Mostrar automatizaciones
function displayAutomations(automations) {
    const automationList = document.getElementById('automation-list');
    
    if (automations.length === 0) {
        automationList.innerHTML = '<div class="empty-state">No hay automatizaciones configuradas</div>';
        return;
    }
    
    const automationsHTML = automations.map(automation => `
        <div class="automation-item">
            <h3>${automation.name || 'Sin nombre'}</h3>
            <p>${automation.description || 'Sin descripción'}</p>
            <div class="automation-actions">
                <button class="btn btn-secondary" onclick="toggleAutomation('${automation.id}')">
                    <i class="fas fa-toggle-on"></i> ${automation.is_active ? 'Desactivar' : 'Activar'}
                </button>
                <button class="btn btn-danger" onclick="deleteAutomation('${automation.id}')">
                    <i class="fas fa-trash"></i> Eliminar
                </button>
            </div>
        </div>
    `).join('');
    
    automationList.innerHTML = automationsHTML;
}

// Cargar reportes
async function loadReports() {
    console.log('INFO: Cargando reportes...');
    
    const reportsList = document.getElementById('reports-list');
    reportsList.innerHTML = '<div class="loading">Cargando reportes...</div>';
    
    try {
        const response = await fetch('/api/v1/reports');
        if (response.ok) {
            const data = await response.json();
            const list = data.reports || data.items || [];
            displayReports(list);
        } else {
            reportsList.innerHTML = '<div class="error">Error cargando reportes</div>';
        }
    } catch (error) {
        console.error('Error cargando reportes:', error);
        reportsList.innerHTML = '<div class="error">Error de conexión</div>';
    }
}

// Mostrar reportes
function displayReports(reports) {
    const reportsList = document.getElementById('reports-list');
    
    if (reports.length === 0) {
        reportsList.innerHTML = '<div class="empty-state">No hay reportes generados</div>';
        return;
    }
    
    const reportsHTML = reports.map(report => `
        <div class="report-item">
            <h3>${report.name || 'Sin nombre'}</h3>
            <p>${report.description || 'Sin descripción'}</p>
            <div class="report-meta">
                <span>Tipo: ${report.report_type || report.type || 'N/A'}</span>
                <span>Generado: ${formatDate(report.created_at)}</span>
            </div>
            <div class="report-actions">
                <button class="btn btn-info" onclick="downloadReport('${report.id}')">
                    <i class="fas fa-download"></i> Descargar
                </button>
                <button class="btn btn-danger" onclick="deleteReport('${report.id}')">
                    <i class="fas fa-trash"></i> Eliminar
                </button>
            </div>
        </div>
    `).join('');
    
    reportsList.innerHTML = reportsHTML;
}

// Mostrar modal de crear tarea
async function showCreateTaskModal() {
    document.getElementById('create-task-modal').style.display = 'block';
    
    // Cargar workspaces y listas para los dropdowns
    await loadWorkspacesForTask();
}

async function loadWorkspacesForTask() {
    try {
        console.log('INFO: Iniciando carga de workspaces para tarea...');
        
        // Verificar que el elemento existe
        const workspaceSelect = document.getElementById('task-workspace');
        if (!workspaceSelect) {
            console.error('ERROR: Elemento task-workspace no encontrado en loadWorkspacesForTask');
            return;
        }
        console.log('SUCCESS: Elemento task-workspace encontrado en loadWorkspacesForTask');
        
        // Usar URL relativa - el interceptor se encarga de HTTPS en Railway
        const apiUrl = '/api/v1/workspaces';
        console.log('INFO: Usando URL relativa (interceptor manejará HTTPS):', apiUrl);
        const response = await fetch(apiUrl);
        console.log('INFO: Respuesta del servidor:', response.status, response.statusText);
        
        if (response.ok) {
            const data = await response.json();
            console.log('INFO: Datos recibidos:', data);
            
            const workspaceSelect = document.getElementById('task-workspace');
            const listSelect = document.getElementById('task-list');
            const assigneeSelect = document.getElementById('task-assignee');
            
            if (!workspaceSelect) {
                console.error('ERROR: No se encontró el elemento task-workspace');
                return;
            }
            
            // Limpiar opciones existentes
            workspaceSelect.innerHTML = '<option value="">Seleccionar workspace...</option>';
            listSelect.innerHTML = '<option value="">Seleccionar lista...</option>';
            assigneeSelect.innerHTML = '<option value="">Sin asignar</option>';
            
            // Agregar workspaces
            const workspaces = data.workspaces || data.items || [];
            console.log('INFO: Workspaces a agregar:', workspaces.length);
            
            workspaces.forEach(workspace => {
                const option = document.createElement('option');
                option.value = workspace.clickup_id;
                option.textContent = workspace.name;
                workspaceSelect.appendChild(option);
                console.log('INFO: Workspace agregado:', workspace.name, 'ID:', workspace.clickup_id);
            });
            
            // Establecer workspace por defecto si existe
            if (workspaces.length > 0) {
                const defaultWorkspace = workspaces.find(w => w.clickup_id === '9014943317') || workspaces[0];
                workspaceSelect.value = defaultWorkspace.clickup_id;
                console.log('INFO: Workspace por defecto establecido:', defaultWorkspace.name, 'ID:', defaultWorkspace.clickup_id);
                
                // Cargar listas y usuarios para el workspace por defecto
                loadListsForWorkspace(defaultWorkspace.clickup_id);
                loadUsersForWorkspace(defaultWorkspace.clickup_id);
            }
            
            // Agregar event listener para cargar listas y usuarios cuando se seleccione un workspace
            workspaceSelect.addEventListener('change', async function() {
                const workspaceId = this.value;
                console.log('INFO: Workspace seleccionado:', workspaceId);
                if (workspaceId) {
                    await loadListsForWorkspace(workspaceId);
                    await loadUsersForWorkspace(workspaceId);
                } else {
                    listSelect.innerHTML = '<option value="">Seleccionar lista...</option>';
                    assigneeSelect.innerHTML = '<option value="">Sin asignar</option>';
                }
            });
            
            console.log('INFO: Workspaces cargados exitosamente');
        } else {
            console.error('ERROR: Error en respuesta del servidor:', response.status, response.statusText);
        }
    } catch (error) {
        console.error('ERROR: Error cargando workspaces para tarea:', error);
    }
}

async function loadListsForWorkspace(workspaceId) {
    try {
        console.log('INFO: Cargando listas para workspace:', workspaceId);
        const apiUrl = `/api/v1/workspaces/${workspaceId}/spaces`;
        console.log('INFO: URL spaces (interceptor manejará HTTPS):', apiUrl);
        const response = await fetch(apiUrl);
        console.log('INFO: Respuesta spaces:', response.status, response.statusText);
        
        if (response.ok) {
            const data = await response.json();
            console.log('INFO: Spaces recibidos:', data);
            
            const listSelect = document.getElementById('task-list');
            
            // Limpiar opciones existentes
            listSelect.innerHTML = '<option value="">Seleccionar lista...</option>';
            
            // Para cada space, obtener sus listas
            console.log('INFO: Procesando', data.spaces.length, 'spaces');
            for (const space of data.spaces) {
                try {
                    console.log('INFO: Cargando listas para space:', space.name, space.id);
                    const listsUrl = `/api/v1/spaces/${space.id}/lists`;
                    const listsResponse = await fetch(listsUrl);
                    console.log('INFO: Respuesta listas:', listsResponse.status, listsResponse.statusText);
                    
                    if (listsResponse.ok) {
                        const listsData = await listsResponse.json();
                        console.log('INFO: Listas recibidas:', listsData);
                        
                        listsData.lists.forEach(list => {
                            const option = document.createElement('option');
                            option.value = list.id;
                            option.textContent = `${space.name} - ${list.name}`;
                            listSelect.appendChild(option);
                            console.log('INFO: Lista agregada:', list.name);
                        });
                    } else {
                        console.error('ERROR: Error obteniendo listas del space:', space.id);
                    }
                } catch (error) {
                    console.error(`ERROR: Error cargando listas para space ${space.id}:`, error);
                }
            }
            console.log('INFO: Listas cargadas exitosamente');
        } else {
            console.error('ERROR: Error obteniendo spaces del workspace:', workspaceId);
        }
    } catch (error) {
        console.error('ERROR: Error cargando listas para workspace:', error);
    }
}

async function loadUsersForWorkspace(workspaceId) {
    try {
        console.log('INFO: Cargando usuarios para workspace:', workspaceId);
        const apiUrl = `/api/v1/users/?workspace_id=${workspaceId}`;
        console.log('INFO: URL users (interceptor manejará HTTPS):', apiUrl);
        const response = await fetch(apiUrl);
        console.log('INFO: Respuesta usuarios:', response.status, response.statusText);
        
        if (response.ok) {
            const data = await response.json();
            console.log('INFO: Usuarios recibidos:', data);
            
            const assigneeSelect = document.getElementById('task-assignee');
            assigneeSelect.innerHTML = '<option value="">Sin asignar</option>';
            
            if (data.users && data.users.length > 0) {
                console.log('INFO: Procesando', data.users.length, 'usuarios');
                data.users.forEach(user => {
                    // Construir nombre completo
                    let displayName = '';
                    if (user.first_name && user.last_name) {
                        displayName = `${user.first_name} ${user.last_name}`;
                    } else if (user.first_name) {
                        displayName = user.first_name;
                    } else if (user.username) {
                        displayName = user.username;
                    } else if (user.email) {
                        displayName = user.email;
                    } else {
                        displayName = `Usuario ${user.clickup_id}`;
                    }
                    
                    const option = document.createElement('option');
                    option.value = user.clickup_id;
                    option.textContent = displayName;
                    assigneeSelect.appendChild(option);
                    console.log('INFO: Usuario agregado:', displayName);
                });
                console.log('INFO: Usuarios cargados exitosamente');
            } else {
                console.log('INFO: No hay usuarios disponibles');
                // Si no hay usuarios, agregar un mensaje informativo
                const option = document.createElement('option');
                option.value = "";
                option.textContent = "No hay usuarios disponibles";
                option.disabled = true;
                assigneeSelect.appendChild(option);
            }
        } else {
            console.error('ERROR: Error en respuesta del servidor:', response.status);
            const assigneeSelect = document.getElementById('task-assignee');
            assigneeSelect.innerHTML = '<option value="">Error cargando usuarios</option>';
        }
    } catch (error) {
        console.error('ERROR: Error cargando usuarios del workspace:', error);
        const assigneeSelect = document.getElementById('task-assignee');
        assigneeSelect.innerHTML = '<option value="">Error de conexión</option>';
    }
}

// Cerrar modal
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Configurar eventos
function setupEventListeners() {
    // Formulario de crear tarea
    const createTaskForm = document.getElementById('create-task-form');
    if (createTaskForm) {
        createTaskForm.addEventListener('submit', handleCreateTask);
    }
    
    // Formulario de editar tarea
    const editTaskForm = document.getElementById('edit-task-form');
    if (editTaskForm) {
        editTaskForm.addEventListener('submit', handleEditTask);
    }
    
    // Búsqueda de tareas
    const taskSearch = document.getElementById('task-search');
    if (taskSearch) {
        taskSearch.addEventListener('input', handleTaskSearch);
    }
    
    // Filtro de estado
    const statusFilter = document.getElementById('status-filter');
    if (statusFilter) {
        statusFilter.addEventListener('change', handleStatusFilter);
    }
    
    // Cerrar modales al hacer clic fuera
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });
}

// Función para obtener campos personalizados de una lista
async function getListCustomFields(listId) {
    try {
        const response = await fetch(`/api/v1/lists/${listId}/fields`);
        if (response.ok) {
            const data = await response.json();
            return data.fields || [];
        }
        return [];
    } catch (error) {
        console.error('Error getting custom fields:', error);
        return [];
    }
}

// Manejar creación de tarea
async function handleCreateTask(event) {
    event.preventDefault();
    
    const listId = document.getElementById('task-list').value;
    
    // Obtener campos personalizados de la lista
    const listCustomFields = await getListCustomFields(listId);
    
    // Crear mapeo de nombres a IDs
    const fieldNameToId = {};
    listCustomFields.forEach(field => {
        fieldNameToId[field.name] = field.id;
    });
    
    // Recopilar custom_fields desde el formulario con nombres como claves
    const customFields = {};
    
    // Campo Email
    const emailValue = document.getElementById('task-email').value.trim();
    if (emailValue) {
        // Usar nombre visible común en ClickUp (case-insensitive más tarde)
        customFields['Email'] = emailValue;
    }
    
    // Campo Celular (teléfono/SMS)
    const phoneValue = document.getElementById('task-phone').value.trim();
    if (phoneValue) {
        customFields['Celular'] = phoneValue;
    }

    // Campo Nombre (si existe en la UI)
    const nameValue = document.getElementById('task-contact-name')?.value?.trim();
    if (nameValue) {
        customFields['Nombre'] = nameValue;
    }
    
    // Campo Nota eliminado - Telegram deshabilitado
    
    // Obtener fecha límite
    const dueDateValue = document.getElementById('task-due-date').value;
    let dueDate = null;
    if (dueDateValue) {
        // Forzar medianoche local y marcar como fecha sin hora en backend
        const parts = dueDateValue.split('-');
        const year = parseInt(parts[0], 10);
        const month = parseInt(parts[1], 10) - 1;
        const day = parseInt(parts[2], 10);
        const localMidnight = new Date(year, month, day, 0, 0, 0, 0);
        // ClickUp interpreta due_date con due_date_time=false en zona del workspace
        dueDate = dueDateValue;
        console.log('INFO: Fecha límite capturada:', {
            inputValue: dueDateValue,
            timestamp: dueDate,
            dateObject: localMidnight
        });
    } else {
        console.warn('WARNING: No se seleccionó fecha límite');
    }
    
    const formData = {
        name: document.getElementById('task-name').value,
        description: document.getElementById('task-description').value,
        workspace_id: document.getElementById('task-workspace').value,
        list_id: document.getElementById('task-list').value,
        status: document.getElementById('task-status').value || null,
        priority: (() => {
            const priorityValue = document.getElementById('task-priority').value;
            return priorityValue ? parseInt(priorityValue) : null;
        })(),
        assignee_id: document.getElementById('task-assignee').value || null,
        due_date: dueDate,
        custom_fields: Object.keys(customFields).length > 0 ? customFields : null
    };
    
            console.log('INFO: Datos que se enviarán al servidor:', formData);
            console.log('INFO: Custom fields preparados:', customFields);
    
    try {
        const response = await fetch('/api/v1/tasks/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('INFO: Tarea creada exitosamente:', result);
            
            closeModal('create-task-modal');
            event.target.reset();
            
            // Limpiar campos personalizados explícitamente
            document.getElementById('task-email').value = '';
            document.getElementById('task-phone').value = '';
            document.getElementById('task-due-date').value = '';
            
            // Recargar tareas
            if (currentTab === 'tasks') {
                await loadTasks();
            }
            
            // Actualizar dashboard
            await loadDashboardData();
            
            // Mostrar mensaje de éxito (solo uno)
            showNotification('INFO: Tarea creada exitosamente!', 'success');
        } else {
            const errorData = await response.json().catch(() => ({}));
            console.error('ERROR: Error del servidor:', response.status, response.statusText, errorData);
            showNotification(`Error creando tarea: ${errorData.detail || response.statusText}`, 'error');
        }
    } catch (error) {
        console.error('Error creando tarea:', error);
        showNotification('Error de conexión', 'error');
    }
}

// Manejar edición de tarea
async function handleEditTask(event) {
    event.preventDefault();
    
    const taskId = document.getElementById('edit-task-id').value;
    const listId = document.getElementById('edit-task-list-id').value || document.getElementById('task-list').value;
    
    // Obtener campos personalizados de la lista
    const listCustomFields = await getListCustomFields(listId);
    
    // Crear mapeo de nombres a IDs
    const fieldNameToId = {};
    listCustomFields.forEach(field => {
        fieldNameToId[field.name] = field.id;
    });
    
    // Recopilar custom_fields desde el formulario de edición con nombres como claves
    const customFields = {};
    
    // Campo Email
    const emailValue = document.getElementById('edit-task-email').value.trim();
    if (emailValue) {
        customFields['Email'] = emailValue;
    }
    
    // Campo Celular (teléfono/SMS)
    const phoneValue = document.getElementById('edit-task-phone').value.trim();
    if (phoneValue) {
        customFields['Celular'] = phoneValue;
    }

    // Campo Nombre en edición (si existe en la UI)
    const editNameValue = document.getElementById('edit-task-contact-name')?.value?.trim();
    if (editNameValue) {
        customFields['Nombre'] = editNameValue;
    }
    
    // Campo Nota (usuario de Telegram)
    // Campo Nota eliminado - Telegram deshabilitado
    
    // Obtener fecha límite
    const dueDateValue = document.getElementById('edit-task-due-date').value;
    let dueDate = null;
    if (dueDateValue) {
        const parts = dueDateValue.split('-');
        const year = parseInt(parts[0], 10);
        const month = parseInt(parts[1], 10) - 1;
        const day = parseInt(parts[2], 10);
        const localMidnight = new Date(year, month, day, 0, 0, 0, 0);
        dueDate = localMidnight.getTime();
        console.log('INFO: Fecha límite de edición capturada:', {
            inputValue: dueDateValue,
            timestamp: dueDate,
            dateObject: localMidnight
        });
    } else {
        console.warn('WARNING: No se seleccionó fecha límite en edición');
    }
    
    const formData = {
        name: document.getElementById('edit-task-name').value,
        description: document.getElementById('edit-task-description').value,
        status: document.getElementById('edit-task-status').value,
        priority: (() => {
            const priorityValue = document.getElementById('edit-task-priority').value;
            return priorityValue ? parseInt(priorityValue) : null;
        })(),
        due_date: dueDate,
        custom_fields: Object.keys(customFields).length > 0 ? customFields : null
    };
    
    try {
        const response = await fetch(`/api/v1/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            closeModal('edit-task-modal');
            
            // Mostrar mensaje de éxito
            showNotification('INFO: Tarea actualizada exitosamente con notificaciones!', 'success');
            
            // Recargar tareas
            if (currentTab === 'tasks') {
                await loadTasks();
            }
            
            // Actualizar dashboard
            await loadDashboardData();
            
            showNotification('Tarea actualizada exitosamente', 'success');
        } else {
            showNotification('Error actualizando tarea', 'error');
        }
    } catch (error) {
        console.error('Error actualizando tarea:', error);
        showNotification('Error de conexión', 'error');
    }
}

// Manejar búsqueda de tareas
function handleTaskSearch(event) {
    const searchTerm = event.target.value.toLowerCase();
    const filteredTasks = tasks.filter(task => 
        task.name.toLowerCase().includes(searchTerm) ||
        task.description.toLowerCase().includes(searchTerm)
    );
    displayTasks(filteredTasks);
}

// Manejar filtro de estado
function handleStatusFilter(event) {
    const statusFilter = event.target.value;
    let filteredTasks = tasks;
    
    if (statusFilter) {
        filteredTasks = tasks.filter(task => task.status === statusFilter);
    }
    
    displayTasks(filteredTasks);
}

// Generar reporte
let generatingReport = false;
async function generateReport() {
    if (generatingReport) {
        // Evitar múltiples clics duplicados
        return;
    }
    try {
        generatingReport = true;
        const btn = document.getElementById('dashboard-report-btn');
        if (btn) {
            btn.disabled = true;
            const originalText = btn.innerHTML;
            btn.setAttribute('data-original', originalText);
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generando...';
        }
        // Obtener workspace seleccionado si existe, o tomar el primero disponible
        let workspaceId = document.getElementById('task-workspace')?.value || null;
        if (!workspaceId && Array.isArray(workspaces) && workspaces.length > 0) {
            workspaceId = workspaces[0].clickup_id || workspaces[0].id;
        }
        if (!workspaceId) {
            // Cargar workspaces si aún no están
            try {
                const wsResp = await fetch('/api/v1/workspaces/');
                if (wsResp.ok) {
                    const wsData = await wsResp.json();
                    const list = wsData.workspaces || wsData.items || [];
                    if (list.length > 0) {
                        workspaceId = list[0].clickup_id || list[0].id;
                    }
                }
            } catch (e) {}
        }
        const response = await fetch('/api/v1/reports/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: 'Reporte de Tareas',
                description: 'Reporte automático de tareas',
                report_type: 'task_summary',
                workspace_id: workspaceId || 'default'
            })
        });
        
        if (response.ok) {
            const created = await response.json();
            // Disparar generación del reporte
            const gen = await fetch(`/api/v1/reports/${created.id}/generate`, { method: 'POST' });
            if (gen.ok) {
                showNotification('Reporte generado exitosamente', 'success');
                // Mostrar lista, sin descarga automática para evitar duplicados
                switchTab('reports');
                try { await loadReports(); } catch (_) {}
            } else {
                showNotification('Reporte creado, pero falló la generación', 'error');
            }
        } else {
            showNotification('Error generando reporte', 'error');
        }
    } catch (error) {
        console.error('Error generando reporte:', error);
        showNotification('Error de conexión', 'error');
    }
    finally {
        const btn = document.getElementById('dashboard-report-btn');
        if (btn) {
            btn.disabled = false;
            const originalText = btn.getAttribute('data-original');
            if (originalText) btn.innerHTML = originalText;
        }
        generatingReport = false;
    }
}

// Funciones auxiliares
function formatDate(dateString) {
    if (!dateString) return 'Sin fecha';
    
    try {
        // Normalizar: si es string numérico, convertir a número
        if (typeof dateString === 'string' && /^\d+$/.test(dateString)) {
            dateString = parseInt(dateString, 10);
        }
        // Si es un timestamp en milisegundos (número >= 1e12) o Date ISO
        if (typeof dateString === 'number') {
            // Si parece ser en segundos (10 dígitos), convertir a ms
            if (dateString < 1e11) {
                dateString = dateString * 1000;
            }
            const date = new Date(dateString);
            if (isNaN(date.getTime())) {
                return 'Fecha inválida';
            }
            return date.toLocaleDateString('es-ES');
        }
        
        // Si es una cadena de fecha ISO
        if (typeof dateString === 'string') {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) {
                return 'Fecha inválida';
            }
            return date.toLocaleDateString('es-ES');
        }
        
        // Si es un objeto Date
        if (dateString instanceof Date) {
            if (isNaN(dateString.getTime())) {
                return 'Fecha inválida';
            }
            return dateString.toLocaleDateString('es-ES');
        }
        
        return 'Formato de fecha no válido';
    } catch (error) {
        console.error('Error formateando fecha:', error, 'Valor:', dateString);
        return 'Error en fecha';
    }
}

function showNotification(message, type = 'info') {
    // Crear notificación temporal
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    if (type === 'success') {
        notification.style.background = '#48bb78';
    } else if (type === 'error') {
        notification.style.background = '#f56565';
    } else {
        notification.style.background = '#4299e1';
    }
    
    document.body.appendChild(notification);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Función para editar tarea
async function editTask(taskId) {
    try {
        // Obtener datos de la tarea
        const response = await fetch(`/api/v1/tasks/${taskId}`);
        if (!response.ok) {
            throw new Error('Error al obtener datos de la tarea');
        }
        
        const task = await response.json();
        
        // Llenar el formulario de edición
        document.getElementById('edit-task-id').value = task.clickup_id || task.id;
        document.getElementById('edit-task-name').value = task.name || '';
        document.getElementById('edit-task-description').value = task.description || '';
        // Mapear status de ClickUp a nuestros valores
        const statusMapping = {
            'to do': 'to do',
            'in progress': 'in progress', 
            'complete': 'complete',
            'done': 'complete',
            'open': 'to do',
            'closed': 'complete'
        };
        const mappedStatus = statusMapping[task.status?.toLowerCase()] || 'to do';
        document.getElementById('edit-task-status').value = mappedStatus;
        document.getElementById('edit-task-priority').value = task.priority || '3';
        
        // Llenar campo de fecha límite
        console.log('INFO: Llenando campo de fecha límite:', {
            taskDueDate: task.due_date,
            type: typeof task.due_date,
            isDate: task.due_date instanceof Date
        });
        
        if (task.due_date) {
            // Convertir timestamp a formato YYYY-MM-DD para el input date
            const dueDate = new Date(task.due_date);
            const formattedDate = dueDate.toISOString().split('T')[0];
            document.getElementById('edit-task-due-date').value = formattedDate;
            console.log('INFO: Fecha límite formateada:', {
                original: task.due_date,
                dateObject: dueDate,
                formatted: formattedDate
            });
        } else {
            document.getElementById('edit-task-due-date').value = '';
            console.log('INFO: No hay fecha límite en la tarea');
        }
        
        // Llenar campos de notificación desde custom_fields si existen
        if (task.custom_fields) {
            // Buscar campos Email, Celular y Nota en custom_fields
            let emailValue = '';
            let phoneValue = '';
            
            if (Array.isArray(task.custom_fields)) {
                // Si custom_fields es un array
                task.custom_fields.forEach(field => {
                    if (field.name === 'Email' && field.value) {
                        emailValue = field.value;
                    }
                    if (field.name === 'Celular' && field.value) {
                        phoneValue = field.value;
                    }
                });
            } else if (typeof task.custom_fields === 'object') {
                // Si custom_fields es un objeto
                emailValue = task.custom_fields.Email || task.custom_fields.email || '';
                phoneValue = task.custom_fields.Celular || task.custom_fields.celular || '';
            }
            
            document.getElementById('edit-task-email').value = emailValue;
            document.getElementById('edit-task-phone').value = phoneValue;
            // Campo Nota eliminado - Telegram deshabilitado
        }
        
        // Mostrar modal
        document.getElementById('edit-task-modal').style.display = 'block';
        
    } catch (error) {
        console.error('Error al cargar datos de la tarea:', error);
        showNotification('Error al cargar la tarea', 'error');
    }
}

async function deleteTask(taskClickupId) {
    if (!taskClickupId) {
        showNotification('ID de tarea inválido', 'error');
        return;
    }
    if (!confirm('¿Estás seguro de que quieres eliminar esta tarea?')) {
        return;
    }
    try {
        const resp = await fetch(`/api/v1/tasks/${taskClickupId}`, { method: 'DELETE' });
        if (resp.ok) {
            // Actualizar arreglo en memoria y UI
            tasks = (tasks || []).filter(t => (t.clickup_id || t.id) !== taskClickupId);
            displayTasks(tasks);
            showNotification('Tarea eliminada correctamente', 'success');
            // Refrescar estadísticas del dashboard
            await loadDashboardData();
        } else {
            showNotification('No se pudo eliminar la tarea', 'error');
        }
    } catch (e) {
        console.error('Error eliminando tarea:', e);
        showNotification('Error de conexión al eliminar', 'error');
    }
}

function viewWorkspaceDetails(workspaceId) {
    showNotification('Detalles del workspace en desarrollo', 'info');
}

function toggleAutomation(automationId) {
    showNotification('Función de toggle en desarrollo', 'info');
}

function deleteAutomation(automationId) {
    if (confirm('¿Estás seguro de que quieres eliminar esta automatización?')) {
        showNotification('Función de eliminación en desarrollo', 'info');
    }
}

function downloadReport(reportId) {
    if (!reportId) {
        showNotification('ID de reporte inválido', 'error');
        return;
    }
    // Intentar descargar como CSV (más fácil de abrir). Si falla, fallback a JSON.
    if (window.__downloadingReportId === reportId) {
        return;
    }
    window.__downloadingReportId = reportId;
    const csvUrl = `/api/v1/reports/${reportId}/download?format=csv`;
    const link = document.createElement('a');
    link.href = csvUrl;
    link.download = '';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setTimeout(() => { window.__downloadingReportId = null; }, 1500);
}

function deleteReport(reportId) {
    if (!reportId) {
        showNotification('ID de reporte inválido', 'error');
        return;
    }
    if (!confirm('¿Eliminar este reporte?')) return;
    fetch(`/api/v1/reports/${reportId}`, { method: 'DELETE' })
        .then(resp => {
            if (resp.status === 204) {
                showNotification('Reporte eliminado', 'success');
                try { loadReports(); } catch (_) {}
            } else {
                showNotification('No se pudo eliminar el reporte', 'error');
            }
        })
        .catch(() => showNotification('Error de conexión al eliminar', 'error'));
}

function showCreateAutomationModal() {
    showNotification('Modal de automatización en desarrollo', 'info');
}

// Función para generar reporte visual
async function generateVisualReport() {
    try {
        // Mostrar loading
        document.getElementById('report-loading').style.display = 'block';
        document.getElementById('report-container').style.display = 'none';
        document.getElementById('generate-visual-report').style.display = 'none';
        
        // Obtener todas las tareas para el reporte
        const allTasks = await fetchAllTasksForDashboard();
        
        // Generar estadísticas
        const reportData = generateReportData(allTasks);
        
        // Mostrar reporte
        displayVisualReport(reportData);
        
        // Ocultar loading y mostrar controles
        document.getElementById('report-loading').style.display = 'none';
        document.getElementById('report-container').style.display = 'block';
        document.getElementById('refresh-report').style.display = 'inline-block';
        
    } catch (error) {
        console.error('Error generando reporte visual:', error);
        showNotification('Error generando reporte visual', 'error');
        document.getElementById('report-loading').style.display = 'none';
        document.getElementById('generate-visual-report').style.display = 'inline-block';
    }
}

// Función para generar datos del reporte
function generateReportData(tasks) {
    const reportData = {
        total_tasks: tasks.length,
        completed_tasks: 0,
        pending_tasks: 0,
        status_distribution: {},
        priority_distribution: {},
        assignee_distribution: {},
        tasks_details: [],
        generated_at: new Date().toISOString()
    };
    
    tasks.forEach(task => {
        // Contar estados
        const status = task.status || 'pendiente';
        reportData.status_distribution[status] = (reportData.status_distribution[status] || 0) + 1;
        
        if (status === 'complete' || status === 'completada') {
            reportData.completed_tasks++;
        } else {
            reportData.pending_tasks++;
        }
        
        // Contar prioridades
        const priority = task.priority || 'sin prioridad';
        reportData.priority_distribution[priority] = (reportData.priority_distribution[priority] || 0) + 1;
        
        // Contar asignaciones
        const assignee = task.assignee_name || task.assignee_id || 'Sin asignar';
        reportData.assignee_distribution[assignee] = (reportData.assignee_distribution[assignee] || 0) + 1;
        
        // Agregar detalles
        reportData.tasks_details.push({
            name: task.name,
            status: status,
            priority: priority,
            assignee: assignee,
            created_at: task.created_at
        });
    });
    
    return reportData;
}

// Función para mostrar reporte visual
function displayVisualReport(reportData) {
    // Actualizar fecha
    const reportDate = new Date(reportData.generated_at).toLocaleString('es-ES');
    document.getElementById('report-date').textContent = reportDate;
    
    // Actualizar estadísticas principales
    const rt = document.getElementById('report-total-tasks');
    const rc = document.getElementById('report-completed-tasks');
    const rp = document.getElementById('report-pending-tasks');
    if (rt) rt.textContent = reportData.total_tasks;
    if (rc) rc.textContent = reportData.completed_tasks;
    if (rp) rp.textContent = reportData.pending_tasks;
    
    // Crear gráficos
    createStatusChart(reportData.status_distribution);
    createPriorityChart(reportData.priority_distribution);
    createAssigneeChart(reportData.assignee_distribution);
    
    // Llenar tabla de detalles
    fillReportTable(reportData.tasks_details);
}

// Función para crear gráfico de estados
function createStatusChart(statusData) {
    const ctx = document.getElementById('status-chart').getContext('2d');
    
    // Destruir gráfico existente si existe
    if (reportCharts.status) {
        reportCharts.status.destroy();
    }
    
    const labels = Object.keys(statusData);
    const data = Object.values(statusData);
    const colors = ['#28a745', '#007bff', '#ffc107', '#dc3545', '#6c757d'];
    
    reportCharts.status = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 10,
                        usePointStyle: true
                    }
                }
            }
        }
    });
}

// Función para crear gráfico de prioridades
function createPriorityChart(priorityData) {
    const ctx = document.getElementById('priority-chart').getContext('2d');
    
    // Destruir gráfico existente si existe
    if (reportCharts.priority) {
        reportCharts.priority.destroy();
    }
    
    const labels = Object.keys(priorityData).map(priority => {
        switch(priority) {
            case '1': return 'Urgente';
            case '2': return 'Alta';
            case '3': return 'Normal';
            case '4': return 'Baja';
            default: return 'Sin prioridad';
        }
    });
    const data = Object.values(priorityData);
    const colors = ['#dc3545', '#fd7e14', '#28a745', '#6c757d', '#17a2b8'];
    
    reportCharts.priority = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Cantidad',
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderColor: colors.slice(0, labels.length),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Función para crear gráfico de asignaciones
function createAssigneeChart(assigneeData) {
    const ctx = document.getElementById('assignee-chart').getContext('2d');
    
    // Destruir gráfico existente si existe
    if (reportCharts.assignee) {
        reportCharts.assignee.destroy();
    }
    
    const labels = Object.keys(assigneeData);
    const data = Object.values(assigneeData);
    const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe'];
    
    reportCharts.assignee = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 10,
                        usePointStyle: true
                    }
                }
            }
        }
    });
}

// Función para llenar tabla de detalles
function fillReportTable(tasksDetails) {
    const tbody = document.getElementById('report-table-body');
    tbody.innerHTML = '';
    
    tasksDetails.forEach(task => {
        const row = document.createElement('tr');
        
        // Clase CSS para prioridad
        const priorityClass = getPriorityClass(task.priority);
        const statusClass = getStatusClass(task.status);
        
        // Formatear datos adicionales
        const listName = task.list_name || 'N/A';
        const workspaceName = task.workspace_name || 'N/A';
        const taskId = task.clickup_id || task.id || 'N/A';
        const assigneeName = task.assignee_name || task.assignee || 'Sin asignar';
        
        row.innerHTML = `
            <td title="${task.name}">${truncateText(task.name, 30)}</td>
            <td class="${statusClass}">${formatStatus(task.status)}</td>
            <td class="${priorityClass}">${formatPriority(task.priority)}</td>
            <td title="${assigneeName}">${truncateText(assigneeName, 20)}</td>
            <td>${formatDate(task.created_at)}</td>
            <td title="${listName}">${truncateText(listName, 25)}</td>
            <td title="${workspaceName}">${truncateText(workspaceName, 25)}</td>
            <td>${taskId}</td>
        `;
        
        tbody.appendChild(row);
    });
}

// Función para truncar texto largo
function truncateText(text, maxLength) {
    if (!text) return 'N/A';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Función para obtener clase CSS de prioridad
function getPriorityClass(priority) {
    // Convertir a string si es número
    const priorityStr = String(priority);
    switch(priorityStr) {
        case '1': return 'priority-urgent';
        case '2': return 'priority-high';
        case '3': return 'priority-normal';
        case '4': return 'priority-low';
        default: return '';
    }
}

// Función para obtener clase CSS de estado
function getStatusClass(status) {
    switch(status) {
        case 'complete':
        case 'completada': return 'status-complete';
        case 'in progress':
        case 'en curso': return 'status-in-progress';
        case 'pending':
        case 'pendiente': return 'status-pending';
        default: return '';
    }
}

// Función para formatear prioridad
function formatPriority(priority) {
    // Convertir a string si es número
    const priorityStr = String(priority);
    switch(priorityStr) {
        case '1': return 'Urgente';
        case '2': return 'Alta';
        case '3': return 'Normal';
        case '4': return 'Baja';
        default: return 'Sin prioridad';
    }
}

// Función para formatear estado
function formatStatus(status) {
    switch(status) {
        case 'complete':
        case 'completada': return 'Completada';
        case 'in progress':
        case 'en curso': return 'En Curso';
        case 'pending':
        case 'pendiente': return 'Pendiente';
        default: return status;
    }
}

// (El formateador robusto de fecha está definido arriba)

// Función para actualizar reporte
async function refreshReport() {
    await generateVisualReport();
}

// Event listeners para reportes
document.addEventListener('DOMContentLoaded', function() {
    // Event listener para generar reporte visual
    const generateBtn = document.getElementById('generate-visual-report');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateVisualReport);
    }
    
    // Event listener para actualizar reporte
    const refreshBtn = document.getElementById('refresh-report');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshReport);
    }
});

// ========================================
// FUNCIONES DE BÚSQUEDA CONTEXTUAL RAG
// ========================================

// Variable para almacenar resultados de búsqueda
let searchResults = [];
let isSearchActive = false;

// Función principal de búsqueda
async function performSearch() {
    const searchInput = document.getElementById('task-search');
    const query = searchInput.value.trim();
    
    if (!query) {
        // Si no hay consulta, mostrar todas las tareas
        isSearchActive = false;
        await loadTasks();
        return;
    }
    
    try {
        showLoading('tasks-list', 'INFO: Buscando tareas...');
        
        const response = await fetch(`/api/v1/search?query=${encodeURIComponent(query)}&top_k=20&threshold=0.3`);
        
        if (response.ok) {
            const data = await response.json();
            searchResults = data.tasks || [];
            isSearchActive = true;
            
            displaySearchResults(data);
        } else {
            throw new Error(`Error en búsqueda: ${response.status}`);
        }
        
    } catch (error) {
        console.error('ERROR: Error en búsqueda:', error);
        showError('tasks-list', 'Error en búsqueda: ' + error.message);
    }
}

// La búsqueda por usuario ahora se maneja automáticamente en la búsqueda general
// No necesitamos una función separada

// Función de búsqueda avanzada
async function performAdvancedSearch(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const searchParams = new URLSearchParams();
    
    // Agregar parámetros de búsqueda
    const name = formData.get('search-name') || document.getElementById('search-name').value;
    const description = formData.get('search-description') || document.getElementById('search-description').value;
    const user = formData.get('search-user') || document.getElementById('search-user').value;
    const status = formData.get('search-status') || document.getElementById('search-status').value;
    const priority = formData.get('search-priority') || document.getElementById('search-priority').value;
    const tags = formData.get('search-tags') || document.getElementById('search-tags').value;
    const customFieldName = formData.get('search-custom-field-name') || document.getElementById('search-custom-field-name').value;
    const customFieldValue = formData.get('search-custom-field-value') || document.getElementById('search-custom-field-value').value;
    
    if (name) searchParams.append('name', name);
    if (description) searchParams.append('description', description);
    if (user) searchParams.append('user', user);
    if (status) searchParams.append('status', status);
    if (priority) searchParams.append('search-priority', priority);
    if (tags) searchParams.append('tags', tags);
    if (customFieldName) searchParams.append('custom_field_name', customFieldName);
    if (customFieldValue) searchParams.append('custom_field_value', customFieldValue);
    
    try {
        showLoading('tasks-list', 'INFO: Búsqueda avanzada en progreso...');
        
        const response = await fetch(`/api/v1/search/advanced?${searchParams.toString()}`);
        
        if (response.ok) {
            const data = await response.json();
            searchResults = data.tasks || [];
            isSearchActive = true;
            
            displaySearchResults(data);
            closeModal('advanced-search-modal');
        } else {
            throw new Error(`Error en búsqueda avanzada: ${response.status}`);
        }
        
    } catch (error) {
        console.error('ERROR: Error en búsqueda avanzada:', error);
        showError('tasks-list', 'Error en búsqueda avanzada: ' + error.message);
    }
}

// Mostrar resultados de búsqueda
function displaySearchResults(data) {
    const tasksList = document.getElementById('tasks-list');
    
    if (!data.tasks || data.tasks.length === 0) {
        tasksList.innerHTML = `
            <div class="no-results">
                <i class="fas fa-search"></i>
                <h3>No se encontraron resultados</h3>
                <p>Consulta: "${data.query || 'Búsqueda avanzada'}"</p>
                <button class="btn btn-outline-primary" onclick="clearSearch()">
                    <i class="fas fa-times"></i> Limpiar búsqueda
                </button>
            </div>
        `;
        return;
    }
    
    // Header de resultados de búsqueda
    const searchHeader = `
        <div class="search-results-header">
            <div class="search-results-count">
                <i class="fas fa-search"></i> 
                ${data.total_results} resultado${data.total_results !== 1 ? 's' : ''} encontrado${data.total_results !== 1 ? 's' : ''}
            </div>
            <div class="search-query">
                Consulta: "${data.query || 'Búsqueda avanzada'}"
            </div>
            <button class="btn btn-sm btn-outline-secondary" onclick="clearSearch()" style="margin-top: 10px;">
                <i class="fas fa-times"></i> Limpiar búsqueda
            </button>
        </div>
    `;
    
    // Generar lista de tareas con scores de búsqueda
    const tasksHtml = data.tasks.map(task => {
        const searchScore = task.search_score ? `<span class="search-score">${(task.search_score * 100).toFixed(1)}%</span>` : '';
        const searchText = task.search_text ? `<div class="search-match" style="font-size: 0.9rem; color: #718096; margin-top: 5px;">
            <i class="fas fa-lightbulb"></i> Coincidencia: ${task.search_text.substring(0, 100)}...
        </div>` : '';
        
        return `
            <div class="task-item">
                <div class="task-header">
                    <div>
                        <div class="task-title">${task.name} ${searchScore}</div>
                        <div class="task-description">${task.description || 'Sin descripción'}</div>
                        ${searchText}
                    </div>
                    <div class="task-actions">
                        <button class="btn btn-sm btn-outline-primary" onclick="editTask('${task.clickup_id || task.id}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteTask('${task.clickup_id || task.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="task-meta">
                    <span class="status ${getStatusClass(task.status)}">${formatStatus(task.status)}</span>
                    <span class="priority ${getPriorityClass(task.priority)}">${formatPriority(task.priority)}</span>
                    <span>${task.assignee_name || 'Sin asignar'}</span>
                    <span>${formatDate(task.created_at)}</span>
                </div>
            </div>
        `;
    }).join('');
    
    tasksList.innerHTML = searchHeader + tasksHtml;
}

// Limpiar búsqueda y mostrar todas las tareas
async function clearSearch() {
    isSearchActive = false;
    searchResults = [];
    document.getElementById('task-search').value = '';
    await loadTasks();
}

// Mostrar modal de búsqueda avanzada
function showAdvancedSearch() {
    document.getElementById('advanced-search-modal').style.display = 'block';
}

// Obtener sugerencias de búsqueda
async function getSearchSuggestions(partialQuery) {
    if (partialQuery.length < 2) {
        hideSearchSuggestions();
        return;
    }
    
    try {
        const response = await fetch(`/api/v1/search/suggestions?partial_query=${encodeURIComponent(partialQuery)}&max_suggestions=5`);
        
        if (response.ok) {
            const data = await response.json();
            displaySearchSuggestions(data.suggestions);
        }
    } catch (error) {
        console.error('ERROR: Error obteniendo sugerencias:', error);
    }
}

// Mostrar sugerencias de búsqueda
function displaySearchSuggestions(suggestions) {
    const suggestionsContainer = document.getElementById('search-suggestions');
    
    if (!suggestions || suggestions.length === 0) {
        hideSearchSuggestions();
        return;
    }
    
    const suggestionsHtml = suggestions.map(suggestion => `
        <div class="search-suggestion-item" onclick="selectSuggestion('${suggestion}')">
            <i class="fas fa-lightbulb"></i> ${suggestion}
        </div>
    `).join('');
    
    suggestionsContainer.innerHTML = suggestionsHtml;
    suggestionsContainer.style.display = 'block';
}

// Ocultar sugerencias de búsqueda
function hideSearchSuggestions() {
    document.getElementById('search-suggestions').style.display = 'none';
}

// Seleccionar sugerencia
function selectSuggestion(suggestion) {
    document.getElementById('task-search').value = suggestion;
    hideSearchSuggestions();
    performSearch();
}

// Reconstruir índice de búsqueda
async function rebuildSearchIndex() {
    try {
        showLoading('tasks-list', 'INFO: Reconstruyendo índice de búsqueda...');
        
        const response = await fetch('/api/v1/search/rebuild-index', {
            method: 'POST'
        });
        
        if (response.ok) {
            const data = await response.json();
            showSuccess('tasks-list', `INFO: Índice reconstruido: ${data.stats.indexed_tasks} tareas indexadas`);
            
            // Recargar tareas después de un breve delay
            setTimeout(async () => {
                await loadTasks();
            }, 2000);
        } else {
            throw new Error(`Error reconstruyendo índice: ${response.status}`);
        }
        
    } catch (error) {
        console.error('ERROR: Error reconstruyendo índice:', error);
        showError('tasks-list', 'Error reconstruyendo índice: ' + error.message);
    }
}

// Configurar eventos de búsqueda
function setupSearchEventListeners() {
    const searchInput = document.getElementById('task-search');
    const advancedSearchForm = document.getElementById('advanced-search-form');
    
    if (searchInput) {
        // Búsqueda en tiempo real con debounce
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                getSearchSuggestions(e.target.value);
            }, 300);
        });
        
        // Búsqueda al presionar Enter
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }
    
    if (advancedSearchForm) {
        advancedSearchForm.addEventListener('submit', performAdvancedSearch);
    }
}

// Agregar setup de búsqueda a la inicialización
document.addEventListener('DOMContentLoaded', function() {
    setupSearchEventListeners();
});

// ===== FUNCIONES DE BÚSQUEDA SIMPLIFICADAS =====
// Solo búsqueda de texto libre - sin filtros complejos

// Actualizar contadores del dashboard
async function updateDashboardCounters() {
    console.log('INFO: Actualizando contadores del dashboard...');
    
    try {
        // Obtener tareas para contar
        const response = await fetch('/api/v1/tasks/?include_closed=true&page=0&limit=1000');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const tasks = await response.json();
        console.log('SUCCESS: Tareas obtenidas para contadores:', tasks.length);
        
        // Contar tareas por estado
        const totalTasks = tasks.length;
        const pendingTasks = tasks.filter(t => 
            t.status === 'to do' || 
            t.status === 'todo' || 
            t.status === 'pending'
        ).length;
        const completedTasks = tasks.filter(t => 
            t.status === 'complete' || 
            t.status === 'completed' || 
            t.status === 'done'
        ).length;
        const inProgressTasks = tasks.filter(t => 
            t.status === 'in progress' || 
            t.status === 'in_progress' || 
            t.status === 'working'
        ).length;
        
        // Actualizar contadores en el dashboard principal
        const totalElement = document.getElementById('total-tasks');
        const pendingElement = document.getElementById('pending-tasks');
        const completedElement = document.getElementById('completed-tasks');
        
        if (totalElement) totalElement.textContent = totalTasks;
        if (pendingElement) pendingElement.textContent = pendingTasks;
        if (completedElement) completedElement.textContent = completedTasks;
        
        // Actualizar contadores en el dashboard de tareas si existe
        const dashboardTotalElement = document.getElementById('dashboard-total-tasks');
        const dashboardPendingElement = document.getElementById('dashboard-pending-tasks');
        const dashboardCompletedElement = document.getElementById('dashboard-completed-tasks');
        const dashboardInProgressElement = document.getElementById('dashboard-in-progress-tasks');
        
        if (dashboardTotalElement) dashboardTotalElement.textContent = totalTasks;
        if (dashboardPendingElement) dashboardPendingElement.textContent = pendingTasks;
        if (dashboardCompletedElement) dashboardCompletedElement.textContent = completedTasks;
        if (dashboardInProgressElement) dashboardInProgressElement.textContent = inProgressTasks;
        
        console.log('SUCCESS: Contadores actualizados:', {
            total: totalTasks,
            pending: pendingTasks,
            completed: completedTasks,
            inProgress: inProgressTasks
        });
        
        // Mostrar notificación de éxito si hay cambios
        if (totalTasks > 0) {
            showNotification(
                `Dashboard actualizado: ${totalTasks} tareas totales`,
                'success'
            );
        }
        
    } catch (error) {
        console.error('ERROR: Error actualizando contadores:', error);
        showNotification(
            `Error actualizando contadores: ${error.message}`,
            'error'
        );
    }
}

// Función para inicializar el dashboard
async function initializeDashboard() {
    console.log('INFO: Inicializando dashboard...');
    
    try {
        // Cargar tareas
        await loadTasks();
        
        // Actualizar contadores
        await updateDashboardCounters();
        
        // Verificar estado de conexión
        await checkConnectionStatus();
        
        console.log('SUCCESS: Dashboard inicializado correctamente');
        
    } catch (error) {
        console.error('ERROR: Error inicializando dashboard:', error);
        showNotification(
            `Error inicializando dashboard: ${error.message}`,
            'error'
        );
    }
}

// Verificar estado de conexión
async function checkConnectionStatus() {
    try {
        const response = await fetch('/api/v1/dashboard/health');
        if (response.ok) {
            const data = await response.json();
            
            // Actualizar indicador de estado
            const statusElement = document.getElementById('connection-status');
            if (statusElement) {
                statusElement.className = 'status-badge connected';
                statusElement.innerHTML = '<i class="fas fa-circle"></i> Conectado';
            }
            
            console.log('SUCCESS: Estado de conexión verificado');
        }
    } catch (error) {
        console.warn('WARNING: No se pudo verificar el estado de conexión:', error);
        
        // Mostrar estado desconectado
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.className = 'status-badge disconnected';
            statusElement.innerHTML = '<i class="fas fa-circle"></i> Desconectado';
        }
    }
}

// Inicializar cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    console.log('INFO: Página cargada, inicializando dashboard...');
    
    // Inicializar dashboard
    initializeDashboard();
    
    // Configurar actualización automática cada 30 segundos
    setInterval(async () => {
        try {
            await updateDashboardCounters();
        } catch (error) {
            console.warn('WARNING: Error en actualización automática:', error);
        }
    }, 30000);
    
    console.log('SUCCESS: Dashboard configurado para actualización automática');
});
