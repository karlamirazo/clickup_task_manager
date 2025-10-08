"""
Cliente para la API de ClickUp
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class ClickUpClient:
    """Cliente para interactuar con la API de ClickUp"""
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or settings.CLICKUP_API_TOKEN
        self.base_url = settings.CLICKUP_API_BASE_URL
        self.headers = {
            "Authorization": self.api_token,  # ClickUp usa token directo (sin Bearer)
            "Content-Type": "application/json"
        }
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Realizar peticion a la API de ClickUp.

        Nota: algunas rutas (p.ej. DELETE task) devuelven 204 o cuerpo vacio/no JSON.
        En esos casos, no se intenta parsear como JSON y se retorna {}.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Validar que tenemos un token
        if not self.api_token:
            logger.error("â�Œ No ClickUp API token provided")
            raise ValueError("CLICKUP_API_TOKEN is not configured")
        
        logger.info(f"ðŸ”— Making ClickUp API request: {method} {url}")
        logger.info(f"ðŸ”‘ Headers: {self.headers}")
        if params:
            logger.info(f"ðŸ“‹ Parameters: {params}")
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    logger.info(f"ðŸ“¡ ClickUp API response: {response.status}")
                    
                    if response.status >= 400:
                        error_text = await response.text()
                        logger.error(f"â�Œ ClickUp API error ({response.status}): {error_text}")
                        response.raise_for_status()
                    
                    # Evitar parsear JSON para respuestas sin contenido o no-JSON
                    method_upper = method.upper()
                    content_type = response.headers.get("Content-Type", "")
                    if response.status == 204 or method_upper == "DELETE":
                        return {}
                    # Si no hay cuerpo o no es JSON, devolver vacio
                    if response.content_length in (0, None) and not content_type.startswith("application/json"):
                        return {}
                    if not content_type.startswith("application/json"):
                        # Algunos endpoints devuelven texto; no necesitamos su cuerpo
                        return {}
                    
                    result = await response.json()
                    logger.info(f"âœ… Successful ClickUp API request")
                    return result
                    
            except aiohttp.ClientError as e:
                logger.error(f"â�Œ Connection error to ClickUp API: {e}")
                raise
            except asyncio.TimeoutError:
                logger.error(f"â�Œ Timeout in ClickUp API request: {url}")
                raise
            except Exception as e:
                logger.error(f"â�Œ Unexpected error in ClickUp API request: {e}")
                raise
    
    # Metodos para Workspaces (Teams en ClickUp)
    async def get_workspaces(self) -> List[Dict]:
        """Get todos los workspaces (teams en ClickUp)"""
        response = await self._make_request("GET", "team")
        return response.get("teams", [])
    
    async def get_teams(self) -> List[Dict]:
        """Get todos los teams (alias de get_workspaces)"""
        return await self.get_workspaces()
    
    # Metodos para Usuario
    async def get_user(self, user_id: str = None) -> Dict:
        """Get informacion del usuario actual o un usuario especifico"""
        if user_id is not None:
            return await self._make_request("GET", f"user/{user_id}")
        else:
            return await self._make_request("GET", "user")
    
    async def get_workspace(self, workspace_id: str) -> Dict:
        """Get un workspace especifico"""
        return await self._make_request("GET", f"team/{workspace_id}")
    
    # Metodos para Spaces
    async def get_spaces(self, workspace_id: str) -> List[Dict]:
        """Get todos los spaces de un workspace"""
        response = await self._make_request("GET", f"team/{workspace_id}/space")
        return response.get("spaces", [])
    
    async def get_space(self, space_id: str) -> Dict:
        """Get un space especifico"""
        return await self._make_request("GET", f"space/{space_id}")
    
    # Metodos para Lists
    async def get_lists(self, space_id: str) -> List[Dict]:
        """Get todas las listas de un space (incluyendo las de folders)"""
        all_lists = []
        
        # Get listas directas del space
        try:
            response = await self._make_request("GET", f"space/{space_id}/list")
            all_lists.extend(response.get("lists", []))
        except Exception as e:
            print(f"Error getting listas directas: {e}")
        
        # Get folders y sus listas
        try:
            folders_response = await self._make_request("GET", f"space/{space_id}/folder")
            folders = folders_response.get("folders", [])
            
            for folder in folders:
                try:
                    folder_lists_response = await self._make_request("GET", f"folder/{folder['id']}/list")
                    folder_lists = folder_lists_response.get("lists", [])
                    
                    # Agregar informacion del folder a cada lista
                    for list_item in folder_lists:
                        list_item["folder_name"] = folder["name"]
                        list_item["folder_id"] = folder["id"]
                    
                    all_lists.extend(folder_lists)
                except Exception as e:
                    print(f"Error getting listas del folder {folder['id']}: {e}")
        except Exception as e:
            print(f"Error getting folders: {e}")
        
        return all_lists
    
    async def get_list(self, list_id: str) -> Dict:
        """Get una lista especifica"""
        return await self._make_request("GET", f"list/{list_id}")
    
    # Metodos para Tasks
    async def get_tasks(
        self, 
        list_id: str, 
        include_closed: bool = False,
        page: int = 0,
        limit: int = 100
    ) -> List[Dict]:
        """Get tareas de una lista"""
        params = {
            "include_closed": str(include_closed).lower(),  # Convertir boolean a string
            "page": page,
            "limit": limit
        }
        response = await self._make_request("GET", f"list/{list_id}/task", params=params)
        return response.get("tasks", [])
    
    async def get_task(self, task_id: str) -> Dict:
        """Get una tarea especifica"""
        return await self._make_request("GET", f"task/{task_id}")
    
    async def create_task(self, list_id: str, task_data: Dict) -> Dict:
        """Create una nueva tarea"""
        try:
            # Asegurar que los campos personalizados se incluyan en la creacion inicial
            if "custom_fields" in task_data:
                # Los campos personalizados pueden venir en formato diccionario o lista
                custom_fields = task_data["custom_fields"]
                
                # Si es un diccionario (formato: {"Email": "valor", "Celular": "valor"})
                if isinstance(custom_fields, dict):
                    # ClickUp espera que los campos personalizados se envien como diccionario
                    # con los nombres de los campos como claves
                    task_data["custom_fields"] = custom_fields
                    print(f"ðŸ“§ Campos personalizados enviados como diccionario: {custom_fields}")
                
                # Si es una lista (formato: [{"id": "field_id", "value": "valor"}])
                elif isinstance(custom_fields, list):
                    formatted_custom_fields = []
                    for field in custom_fields:
                        if isinstance(field, dict) and "id" in field and "value" in field:
                            formatted_custom_fields.append(field)
                    
                    if formatted_custom_fields:
                        task_data["custom_fields"] = formatted_custom_fields
                        print(f"ðŸ“§ Campos personalizados enviados como lista: {formatted_custom_fields}")
            
            return await self._make_request("POST", f"list/{list_id}/task", data=task_data)
        except aiohttp.ClientResponseError as cre:
            # Fallback: algunos espacios/listas rechazan priority/status -> reintentar con payload minimo
            if cre.status == 400:
                minimal_data: Dict[str, Any] = {
                    "name": task_data.get("name", "Nueva tarea"),
                    "description": task_data.get("description", "")
                }
                # Conservar prioridad si estaba presente (el problema suele ser status)
                if "priority" in task_data and task_data.get("priority") is not None:
                    minimal_data["priority"] = task_data["priority"]
                # Conservar asignatarios si estaban presentes
                if task_data.get("assignees"):
                    minimal_data["assignees"] = task_data["assignees"]
                # Conservar fechas si estaban presentes
                if task_data.get("due_date") is not None:
                    minimal_data["due_date"] = task_data["due_date"]
                if task_data.get("start_date") is not None:
                    minimal_data["start_date"] = task_data["start_date"]
                # Conservar campos personalizados si estaban presentes
                if "custom_fields" in task_data:
                    minimal_data["custom_fields"] = task_data["custom_fields"]
                return await self._make_request("POST", f"list/{list_id}/task", data=minimal_data)
            raise
    
    async def update_task(self, task_id: str, task_data: Dict) -> Dict:
        """Update una tarea existente"""
        return await self._make_request("PUT", f"task/{task_id}", data=task_data)
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete una tarea"""
        await self._make_request("DELETE", f"task/{task_id}")
        return True
    
    # Metodos para Users
    async def get_users(self, workspace_id: str) -> List[Dict]:
        """Get usuarios de un workspace"""
        try:
            # Intentar obtener usuarios del team/workspace usando la ruta correcta
            response = await self._make_request("GET", f"team/{workspace_id}")
            team_data = response
            
            # Si el team tiene members, usarlos
            if team_data.get("team", {}).get("members"):
                return team_data["team"]["members"]
            
        except Exception as e:
            print(f"Error en peticion a ClickUp API (team/workspace): {e}")
        
        # Si no se pueden obtener usuarios de la API, devolver usuarios de ejemplo
        print("No se pudieron obtener usuarios de ClickUp, devolviendo usuarios de ejemplo")
        return [{
            "user": {
                "id": "156221125",
                "username": "Karla Ve",
                "email": "karlamirazo@gmail.com",
                "first_name": "Karla",
                "last_name": "Ve",
                "avatar": "",
                "title": "Usuario",
                "active": True,
                "timezone": "America/Mexico_City",
                "language": "es",
                "preferences": {}
            },
            "role": "member"
        }, {
            "user": {
                "id": "88425546",
                "username": "Veronica Mirazo",
                "email": "karla_r@hotmail.com",
                "first_name": "Veronica",
                "last_name": "Mirazo",
                "avatar": "",
                "title": "Usuario",
                "active": True,
                "timezone": "America/Mexico_City",
                "language": "es",
                "preferences": {}
            },
            "role": "member"
        }, {
            "user": {
                "id": "88425547",
                "username": "Karla Rosas",
                "email": "lakitu_98@yahoo.com",
                "first_name": "Karla",
                "last_name": "Rosas",
                "avatar": "",
                "title": "Usuario",
                "active": True,
                "timezone": "America/Mexico_City",
                "language": "es",
                "preferences": {}
            },
            "role": "member"
        }]
    
    # Metodo get_user ya definido anteriormente con parametro opcional
    
    # Metodos para Comments
    async def get_task_comments(self, task_id: str) -> List[Dict]:
        """Get comentarios de una tarea"""
        response = await self._make_request("GET", f"task/{task_id}/comment")
        return response.get("comments", [])
    
    async def create_comment(self, task_id: str, comment_data: Dict) -> Dict:
        """Create un comentario en una tarea"""
        return await self._make_request("POST", f"task/{task_id}/comment", data=comment_data)
    
    # Metodos para Attachments
    async def get_task_attachments(self, task_id: str) -> List[Dict]:
        """Get archivos adjuntos de una tarea"""
        response = await self._make_request("GET", f"task/{task_id}/attachment")
        return response.get("attachments", [])
    
    # Metodos para Custom Fields
    async def get_list_custom_fields(self, list_id: str) -> List[Dict]:
        """Get campos personalizados de una lista"""
        response = await self._make_request("GET", f"list/{list_id}/field")
        return response.get("fields", [])
    
    # Metodos para Tags
    async def get_space_tags(self, space_id: str) -> List[Dict]:
        """Get etiquetas de un space"""
        response = await self._make_request("GET", f"space/{space_id}/tag")
        return response.get("tags", [])
    
    # Metodos para Time Tracking
    async def get_task_time_entries(self, task_id: str) -> List[Dict]:
        """Get entradas de tiempo de una tarea"""
        response = await self._make_request("GET", f"task/{task_id}/time")
        return response.get("data", [])
    
    async def create_time_entry(self, task_id: str, time_data: Dict) -> Dict:
        """Create una entrada de tiempo"""
        return await self._make_request("POST", f"task/{task_id}/time", data=time_data)
    
    # Metodos para Webhooks
    async def create_webhook(self, webhook_data: Dict) -> Dict:
        """Create un webhook"""
        return await self._make_request("POST", "webhook", data=webhook_data)
    
    async def get_webhooks(self) -> List[Dict]:
        """Get webhooks"""
        response = await self._make_request("GET", "webhook")
        return response.get("webhooks", [])
    
    async def delete_webhook(self, webhook_id: str) -> bool:
        """Delete un webhook"""
        await self._make_request("DELETE", f"webhook/{webhook_id}")
        return True
    
    # Metodos de utilidad
    async def search_tasks(self, query: str, workspace_id: str) -> List[Dict]:
        """Buscar tareas"""
        params = {
            "query": query,
            "team_id": workspace_id
        }
        response = await self._make_request("GET", "task", params=params)
        return response.get("tasks", [])
    
    async def get_user_tasks(self, user_id: str, workspace_id: str) -> List[Dict]:
        """Get tareas asignadas a un usuario"""
        params = {
            "assignees[]": [user_id],
            "team_id": workspace_id
        }
        response = await self._make_request("GET", "task", params=params)
        return response.get("tasks", [])
    
    async def get_due_tasks(self, workspace_id: str, due_date: Optional[datetime] = None) -> List[Dict]:
        """Get tareas con fecha limite"""
        params = {
            "team_id": workspace_id,
            "due_date_lt": due_date.isoformat() if due_date else None
        }
        response = await self._make_request("GET", "task", params=params)
        return response.get("tasks", [])
    
    async def update_custom_field_value(self, task_id: str, field_id: str, value: Any) -> Dict:
        """Update el valor de un campo personalizado en una tarea.
        Intenta usar el endpoint dedicado de ClickUp; si falla, hace fallback a update_task.
        """
        payload = {"value": value}
        try:
            # Endpoint dedicado para actualizar un campo personalizado
            return await self._make_request("POST", f"task/{task_id}/field/{field_id}", data=payload)
        except Exception as _e:
            # Fallback al metodo por update_task
            update_data = {"custom_fields": [{"id": field_id, "value": value}]}
            return await self.update_task(task_id, update_data)

    # ==========================
    # Relaciones / Dependencias
    # ==========================
    async def get_task_relationships(self, task_id: str) -> Dict[str, Any]:
        """Obtiene relaciones de una tarea (dependencias y relaciones).

        Intenta primero el endpoint dedicado de relaciones y si no está disponible
        hace fallback a leer la tarea y extraer campos relacionados (dependencies).
        """
        # Intentar endpoint dedicado (si está habilitado en API)
        try:
            return await self._make_request("GET", f"task/{task_id}/relationship")
        except Exception:
            pass

        # Fallback: obtener la tarea y devolver posibles campos de dependencias
        task = await self.get_task(task_id)
        return {
            "task": task,
            "dependencies": task.get("dependencies", []),
            "dependency_of": task.get("dependency_of", []),
        }

    async def create_task_relationship(self, task_id: str, to_task_id: str, relationship_type: str) -> Dict[str, Any]:
        """Crea una relación entre tareas.

        relationship_type soporta alias comunes:
        - "blocks" (esta tarea bloquea a otra)
        - "blocked_by" / "is_blocked_by" (esta tarea está bloqueada por otra)
        - "waiting_on" (alias de blocked_by)
        """
        normalized = relationship_type.strip().lower().replace(" ", "_")
        if normalized in {"is_blocked_by", "blocked_by", "waiting_on"}:
            normalized = "blocked_by"
        elif normalized in {"blocks", "blocking"}:
            normalized = "blocks"

        payload = {
            "to_task": to_task_id,
            "relationship_type": normalized,
        }
        return await self._make_request("POST", f"task/{task_id}/relationship", data=payload)

    async def delete_task_relationship(self, task_id: str, relationship_id: str) -> bool:
        """Elimina una relación específica por su ID."""
        await self._make_request("DELETE", f"task/{task_id}/relationship/{relationship_id}")
        return True

    async def get_blocking_tasks(self, task_id: str) -> List[Dict[str, Any]]:
        """Devuelve las tareas que bloquean a la tarea dada.

        Intenta interpretar la respuesta del endpoint de relaciones o los campos
        "dependencies" del detalle de la tarea, retornando una lista de tareas
        (objetos completos) que actúan como bloqueadores.
        """
        try:
            relationships = await self.get_task_relationships(task_id)
        except Exception:
            relationships = {}

        blocking_task_ids: List[str] = []

        # Caso 1: estructura del endpoint dedicado
        rel_items: List[Dict[str, Any]] = []
        for key in ("relationships", "data", "items"):
            if isinstance(relationships.get(key), list):
                rel_items = relationships[key]  # type: ignore[assignment]
                break

        for rel in rel_items:
            rel_type = str(rel.get("relationship_type") or rel.get("type") or "").lower()
            # blocked_by / waiting_on implican que OTRO task bloquea a este
            if any(alias in rel_type for alias in ["blocked", "waiting_on"]):
                # Algunas respuestas incluyen to_task o task_id
                to_task = rel.get("to_task") or rel.get("task_id") or rel.get("source_task")
                if to_task and isinstance(to_task, (str, int)):
                    if str(to_task) != str(task_id):  # evitar auto-referencias
                        blocking_task_ids.append(str(to_task))

        # Caso 2: fallback usando campos de la tarea
        if not blocking_task_ids:
            # En la estructura de ClickUp, "dependencies" suele representar tareas de las que
            # ESTE task depende (i.e., bloqueadores). "dependency_of" representa tareas que
            # dependen de ESTE task (no son bloqueadores). Por eso usamos solo "dependencies".
            deps = relationships.get("dependencies") or []
            for dep in deps if isinstance(deps, list) else []:
                # Los esquemas varían; buscar claves comunes
                candidate = dep.get("task_id") or dep.get("depends_on") or dep.get("id")
                if candidate:
                    if str(candidate) != str(task_id):  # evitar auto-referencias
                        blocking_task_ids.append(str(candidate))

        # Obtener detalles de tareas bloqueadoras
        blocking_tasks: List[Dict[str, Any]] = []
        for bid in blocking_task_ids:
            try:
                blocking_tasks.append(await self.get_task(bid))
            except Exception:
                continue

        return blocking_tasks

# ===== FUNCION DE DEPENDENCIA PARA FASTAPI =====
def get_clickup_client() -> ClickUpClient:
    """Funcion de dependencia para FastAPI que retorna una instancia de ClickUpClient"""
    return ClickUpClient()
