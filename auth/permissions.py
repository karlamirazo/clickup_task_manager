"""
Sistema de permisos avanzado para ClickUp Project Manager
"""

from typing import List, Dict, Any, Optional, Set
from enum import Enum
from dataclasses import dataclass
from sqlalchemy.orm import Session

from models.user import User
from models.task import Task
from models.workspace import Workspace

class Permission(Enum):
    """Permisos disponibles en el sistema"""
    
    # Permisos de tareas
    READ_OWN_TASKS = "read_own_tasks"
    WRITE_OWN_TASKS = "write_own_tasks"
    READ_ASSIGNED_TASKS = "read_assigned_tasks"
    WRITE_ASSIGNED_TASKS = "write_assigned_tasks"
    READ_ALL_TASKS = "read_all_tasks"
    WRITE_ALL_TASKS = "write_all_tasks"
    DELETE_ALL_TASKS = "delete_all_tasks"
    
    # Permisos de usuarios
    READ_USERS = "read_users"
    WRITE_USERS = "write_users"
    DELETE_USERS = "delete_users"
    MANAGE_USER_ROLES = "manage_user_roles"
    
    # Permisos de workspace
    READ_WORKSPACE = "read_workspace"
    WRITE_WORKSPACE = "write_workspace"
    MANAGE_WORKSPACE = "manage_workspace"
    
    # Permisos de configuración
    READ_SETTINGS = "read_settings"
    WRITE_SETTINGS = "write_settings"
    
    # Permisos de dashboard
    READ_DASHBOARD = "read_dashboard"
    MANAGE_DASHBOARD = "manage_dashboard"
    
    # Permisos de notificaciones
    READ_NOTIFICATIONS = "read_notifications"
    WRITE_NOTIFICATIONS = "write_notifications"
    MANAGE_NOTIFICATIONS = "manage_notifications"
    
    # Permisos de webhooks
    MANAGE_WEBHOOKS = "manage_webhooks"
    
    # Permisos de reportes
    READ_REPORTS = "read_reports"
    WRITE_REPORTS = "write_reports"
    MANAGE_REPORTS = "manage_reports"
    
    # Permisos de integraciones
    MANAGE_INTEGRATIONS = "manage_integrations"
    
    # Permisos de administración
    FULL_ADMIN = "full_admin"

@dataclass
class Role:
    """Definición de rol con permisos"""
    name: str
    display_name: str
    description: str
    permissions: Set[Permission]
    level: int  # Nivel jerárquico (mayor = más permisos)

class PermissionManager:
    """Gestor de permisos del sistema"""
    
    # Definición de roles del sistema
    ROLES = {
        "admin": Role(
            name="admin",
            display_name="Administrador",
            description="Acceso completo al sistema",
            permissions={
                Permission.READ_ALL_TASKS,
                Permission.WRITE_ALL_TASKS,
                Permission.DELETE_ALL_TASKS,
                Permission.READ_USERS,
                Permission.WRITE_USERS,
                Permission.DELETE_USERS,
                Permission.MANAGE_USER_ROLES,
                Permission.READ_WORKSPACE,
                Permission.WRITE_WORKSPACE,
                Permission.MANAGE_WORKSPACE,
                Permission.READ_SETTINGS,
                Permission.WRITE_SETTINGS,
                Permission.READ_DASHBOARD,
                Permission.MANAGE_DASHBOARD,
                Permission.READ_NOTIFICATIONS,
                Permission.WRITE_NOTIFICATIONS,
                Permission.MANAGE_NOTIFICATIONS,
                Permission.MANAGE_WEBHOOKS,
                Permission.READ_REPORTS,
                Permission.WRITE_REPORTS,
                Permission.MANAGE_REPORTS,
                Permission.MANAGE_INTEGRATIONS,
                Permission.FULL_ADMIN
            },
            level=100
        ),
        "manager": Role(
            name="manager",
            display_name="Gerente de Proyecto",
            description="Gestión de proyectos y equipos",
            permissions={
                Permission.READ_ALL_TASKS,
                Permission.WRITE_ALL_TASKS,
                Permission.READ_USERS,
                Permission.WRITE_USERS,
                Permission.READ_WORKSPACE,
                Permission.WRITE_WORKSPACE,
                Permission.READ_DASHBOARD,
                Permission.READ_NOTIFICATIONS,
                Permission.WRITE_NOTIFICATIONS,
                Permission.READ_REPORTS,
                Permission.WRITE_REPORTS
            },
            level=80
        ),
        "team_lead": Role(
            name="team_lead",
            display_name="Líder de Equipo",
            description="Supervisión de equipo específico",
            permissions={
                Permission.READ_ALL_TASKS,
                Permission.WRITE_ALL_TASKS,
                Permission.READ_USERS,
                Permission.READ_WORKSPACE,
                Permission.READ_DASHBOARD,
                Permission.READ_NOTIFICATIONS,
                Permission.WRITE_NOTIFICATIONS,
                Permission.READ_REPORTS
            },
            level=60
        ),
        "user": Role(
            name="user",
            display_name="Usuario",
            description="Acceso a sus propias tareas",
            permissions={
                Permission.READ_OWN_TASKS,
                Permission.WRITE_OWN_TASKS,
                Permission.READ_ASSIGNED_TASKS,
                Permission.WRITE_ASSIGNED_TASKS,
                Permission.READ_NOTIFICATIONS
            },
            level=40
        ),
        "viewer": Role(
            name="viewer",
            display_name="Visualizador",
            description="Solo lectura de tareas asignadas",
            permissions={
                Permission.READ_OWN_TASKS,
                Permission.READ_ASSIGNED_TASKS,
                Permission.READ_NOTIFICATIONS
            },
            level=20
        )
    }
    
    @classmethod
    def has_permission(cls, user_role: str, permission: Permission) -> bool:
        """Verificar si un rol tiene un permiso específico"""
        role = cls.ROLES.get(user_role)
        if not role:
            return False
        return permission in role.permissions
    
    @classmethod
    def has_any_permission(cls, user_role: str, permissions: List[Permission]) -> bool:
        """Verificar si un rol tiene alguno de los permisos especificados"""
        role = cls.ROLES.get(user_role)
        if not role:
            return False
        return any(permission in role.permissions for permission in permissions)
    
    @classmethod
    def has_all_permissions(cls, user_role: str, permissions: List[Permission]) -> bool:
        """Verificar si un rol tiene todos los permisos especificados"""
        role = cls.ROLES.get(user_role)
        if not role:
            return False
        return all(permission in role.permissions for permission in permissions)
    
    @classmethod
    def get_role_permissions(cls, role_name: str) -> Set[Permission]:
        """Obtener permisos de un rol"""
        role = cls.ROLES.get(role_name)
        return role.permissions if role else set()
    
    @classmethod
    def get_available_roles(cls) -> Dict[str, Dict[str, Any]]:
        """Obtener todos los roles disponibles"""
        return {
            name: {
                "name": role.name,
                "display_name": role.display_name,
                "description": role.description,
                "level": role.level,
                "permissions": [p.value for p in role.permissions]
            }
            for name, role in cls.ROLES.items()
        }
    
    @classmethod
    def can_manage_user(cls, manager_role: str, target_user_role: str) -> bool:
        """Verificar si un rol puede gestionar a otro usuario"""
        manager = cls.ROLES.get(manager_role)
        target = cls.ROLES.get(target_user_role)
        
        if not manager or not target:
            return False
        
        # Un rol solo puede gestionar roles de menor nivel
        return manager.level > target.level
    
    @classmethod
    def get_permission_level(cls, permission: Permission) -> int:
        """Obtener nivel mínimo requerido para un permiso"""
        # Definir niveles mínimos para cada tipo de permiso
        if permission in [Permission.FULL_ADMIN]:
            return 100
        elif permission in [Permission.DELETE_ALL_TASKS, Permission.DELETE_USERS, Permission.MANAGE_WORKSPACE]:
            return 80
        elif permission in [Permission.WRITE_ALL_TASKS, Permission.WRITE_USERS, Permission.MANAGE_USER_ROLES]:
            return 60
        elif permission in [Permission.READ_ALL_TASKS, Permission.READ_USERS, Permission.WRITE_WORKSPACE]:
            return 40
        else:
            return 20

class TaskPermissionChecker:
    """Verificador de permisos específicos para tareas"""
    
    @staticmethod
    def can_read_task(user: User, task: Task) -> bool:
        """Verificar si un usuario puede leer una tarea específica"""
        # Administradores pueden leer todas las tareas
        if PermissionManager.has_permission(user.role, Permission.READ_ALL_TASKS):
            return True
        
        # Usuarios pueden leer sus propias tareas
        if PermissionManager.has_permission(user.role, Permission.READ_OWN_TASKS):
            if task.assignees and str(user.clickup_id) in [str(a.get('id', '')) for a in task.assignees]:
                return True
        
        # Usuarios pueden leer tareas asignadas
        if PermissionManager.has_permission(user.role, Permission.READ_ASSIGNED_TASKS):
            if task.assignees and str(user.clickup_id) in [str(a.get('id', '')) for a in task.assignees]:
                return True
        
        return False
    
    @staticmethod
    def can_write_task(user: User, task: Task) -> bool:
        """Verificar si un usuario puede escribir una tarea específica"""
        # Administradores pueden escribir todas las tareas
        if PermissionManager.has_permission(user.role, Permission.WRITE_ALL_TASKS):
            return True
        
        # Usuarios pueden escribir sus propias tareas
        if PermissionManager.has_permission(user.role, Permission.WRITE_OWN_TASKS):
            if task.assignees and str(user.clickup_id) in [str(a.get('id', '')) for a in task.assignees]:
                return True
        
        # Usuarios pueden escribir tareas asignadas
        if PermissionManager.has_permission(user.role, Permission.WRITE_ASSIGNED_TASKS):
            if task.assignees and str(user.clickup_id) in [str(a.get('id', '')) for a in task.assignees]:
                return True
        
        return False
    
    @staticmethod
    def can_delete_task(user: User, task: Task) -> bool:
        """Verificar si un usuario puede eliminar una tarea específica"""
        # Solo administradores pueden eliminar tareas
        return PermissionManager.has_permission(user.role, Permission.DELETE_ALL_TASKS)
    
    @staticmethod
    def filter_tasks_by_permission(user: User, tasks: List[Task]) -> List[Task]:
        """Filtrar lista de tareas según permisos del usuario"""
        if PermissionManager.has_permission(user.role, Permission.READ_ALL_TASKS):
            return tasks
        
        filtered_tasks = []
        for task in tasks:
            if TaskPermissionChecker.can_read_task(user, task):
                filtered_tasks.append(task)
        
        return filtered_tasks

class WorkspacePermissionChecker:
    """Verificador de permisos específicos para workspaces"""
    
    @staticmethod
    def can_read_workspace(user: User, workspace: Workspace) -> bool:
        """Verificar si un usuario puede leer un workspace"""
        # Administradores pueden leer todos los workspaces
        if PermissionManager.has_permission(user.role, Permission.READ_WORKSPACE):
            return True
        
        # Verificar si el usuario pertenece al workspace
        if user.workspaces and str(workspace.clickup_id) in user.workspaces:
            return True
        
        return False
    
    @staticmethod
    def can_write_workspace(user: User, workspace: Workspace) -> bool:
        """Verificar si un usuario puede escribir en un workspace"""
        # Administradores y gerentes pueden escribir
        if PermissionManager.has_permission(user.role, Permission.WRITE_WORKSPACE):
            return True
        
        return False
    
    @staticmethod
    def can_manage_workspace(user: User, workspace: Workspace) -> bool:
        """Verificar si un usuario puede gestionar un workspace"""
        # Solo administradores y gerentes pueden gestionar
        return PermissionManager.has_permission(user.role, Permission.MANAGE_WORKSPACE)

class UserPermissionChecker:
    """Verificador de permisos específicos para usuarios"""
    
    @staticmethod
    def can_read_user(current_user: User, target_user: User) -> bool:
        """Verificar si un usuario puede leer información de otro usuario"""
        # Administradores pueden leer todos los usuarios
        if PermissionManager.has_permission(current_user.role, Permission.READ_USERS):
            return True
        
        # Los usuarios pueden leer su propia información
        return current_user.id == target_user.id
    
    @staticmethod
    def can_write_user(current_user: User, target_user: User) -> bool:
        """Verificar si un usuario puede modificar otro usuario"""
        # Administradores pueden modificar todos los usuarios
        if PermissionManager.has_permission(current_user.role, Permission.WRITE_USERS):
            return True
        
        # Los usuarios pueden modificar su propia información
        return current_user.id == target_user.id
    
    @staticmethod
    def can_delete_user(current_user: User, target_user: User) -> bool:
        """Verificar si un usuario puede eliminar otro usuario"""
        # Solo administradores pueden eliminar usuarios
        if not PermissionManager.has_permission(current_user.role, Permission.DELETE_USERS):
            return False
        
        # No se puede eliminar a sí mismo
        return current_user.id != target_user.id
    
    @staticmethod
    def can_manage_user_role(current_user: User, target_user: User) -> bool:
        """Verificar si un usuario puede cambiar el rol de otro usuario"""
        # Solo administradores pueden gestionar roles
        if not PermissionManager.has_permission(current_user.role, Permission.MANAGE_USER_ROLES):
            return False
        
        # Solo se puede gestionar roles de menor nivel
        return PermissionManager.can_manage_user(current_user.role, target_user.role)

def get_user_accessible_tasks(user: User, db: Session) -> List[Task]:
    """Obtener tareas accesibles para un usuario según sus permisos"""
    if PermissionManager.has_permission(user.role, Permission.READ_ALL_TASKS):
        # Administradores y gerentes ven todas las tareas
        return db.query(Task).all()
    
    # Usuarios regulares ven solo sus tareas asignadas
    accessible_tasks = []
    
    # Buscar tareas donde el usuario es asignado
    all_tasks = db.query(Task).all()
    for task in all_tasks:
        if task.assignees and str(user.clickup_id) in [str(a.get('id', '')) for a in task.assignees]:
            accessible_tasks.append(task)
    
    return accessible_tasks

def get_user_accessible_workspaces(user: User, db: Session) -> List[Workspace]:
    """Obtener workspaces accesibles para un usuario según sus permisos"""
    if PermissionManager.has_permission(user.role, Permission.READ_WORKSPACE):
        # Administradores y gerentes ven todos los workspaces
        return db.query(Workspace).all()
    
    # Usuarios regulares ven solo workspaces a los que pertenecen
    accessible_workspaces = []
    
    if user.workspaces:
        workspace_ids = [str(wid) for wid in user.workspaces]
        accessible_workspaces = db.query(Workspace).filter(
            Workspace.clickup_id.in_(workspace_ids)
        ).all()
    
    return accessible_workspaces
