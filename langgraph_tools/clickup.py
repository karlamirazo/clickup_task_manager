"""
Herramientas de ClickUp listas para usar en LangGraph.

Requiere variable de entorno CLICKUP_API_TOKEN.
Referencia API: https://developer.clickup.com/docs/index
"""

from __future__ import annotations

import os
import asyncio
from typing import Any, Dict, List, Optional

import aiohttp


class ClickUpTools:
    """Cliente minimalista para exponer funciones de ClickUp como herramientas LangGraph."""

    def __init__(self, api_token: Optional[str] = None, base_url: str = "https://api.clickup.com/api/v2") -> None:
        token = api_token or os.getenv("CLICKUP_API_TOKEN")
        if not token:
            raise RuntimeError("CLICKUP_API_TOKEN no configurado")
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=self.headers, json=json, params=params) as resp:
                # Manejo de 204 o cuerpo vacío
                if resp.status == 204:
                    return {}
                ct = resp.headers.get("Content-Type", "")
                if not ct.startswith("application/json"):
                    # Si no es JSON, devolver vacío
                    if resp.status < 400:
                        return {}
                resp.raise_for_status()
                return await resp.json()

    # Workspaces / Teams
    async def list_workspaces(self) -> List[Dict[str, Any]]:
        data = await self._request("GET", "team")
        return data.get("teams", [])

    # Spaces
    async def list_spaces(self, workspace_id: str) -> List[Dict[str, Any]]:
        data = await self._request("GET", f"team/{workspace_id}/space")
        return data.get("spaces", [])

    # Lists
    async def list_lists_by_space(self, space_id: str) -> List[Dict[str, Any]]:
        data = await self._request("GET", f"space/{space_id}/list")
        lists = data.get("lists", [])
        # Incluir listas en folders
        folders = await self._request("GET", f"space/{space_id}/folder")
        for folder in folders.get("folders", []):
            fl = await self._request("GET", f"folder/{folder['id']}/list")
            lists.extend(fl.get("lists", []))
        return lists

    # Tasks
    async def create_task(self, list_id: str, name: str, description: str = "", **kwargs: Any) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"name": name, "description": description}
        payload.update(kwargs)
        return await self._request("POST", f"list/{list_id}/task", json=payload)

    async def get_task(self, task_id: str) -> Dict[str, Any]:
        return await self._request("GET", f"task/{task_id}")

    async def update_task(self, task_id: str, **kwargs: Any) -> Dict[str, Any]:
        return await self._request("PUT", f"task/{task_id}", json=kwargs)

    async def delete_task(self, task_id: str) -> None:
        await self._request("DELETE", f"task/{task_id}")

    async def list_tasks_in_list(self, list_id: str, include_closed: bool = False, page: int = 0) -> List[Dict[str, Any]]:
        params = {"include_closed": str(include_closed).lower(), "page": page}
        data = await self._request("GET", f"list/{list_id}/task", params=params)
        return data.get("tasks", [])

    # Comments
    async def add_comment(self, task_id: str, comment_text: str) -> Dict[str, Any]:
        return await self._request("POST", f"task/{task_id}/comment", json={"comment_text": comment_text})


def get_langgraph_tools(client: Optional[ClickUpTools] = None) -> Dict[str, Any]:
    """Devuelve un diccionario de callable tools para LangGraph."""
    client = client or ClickUpTools()

    async def tool_list_workspaces(_: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        return await client.list_workspaces()

    async def tool_list_spaces(args: Dict[str, Any]) -> List[Dict[str, Any]]:
        return await client.list_spaces(args["workspace_id"])

    async def tool_list_lists(args: Dict[str, Any]) -> List[Dict[str, Any]]:
        return await client.list_lists_by_space(args["space_id"])

    async def tool_create_task(args: Dict[str, Any]) -> Dict[str, Any]:
        return await client.create_task(args["list_id"], args["name"], args.get("description", ""), **args.get("extra", {}))

    async def tool_get_task(args: Dict[str, Any]) -> Dict[str, Any]:
        return await client.get_task(args["task_id"])

    async def tool_update_task(args: Dict[str, Any]) -> Dict[str, Any]:
        kwargs = args.get("updates", {})
        return await client.update_task(args["task_id"], **kwargs)

    async def tool_delete_task(args: Dict[str, Any]) -> Dict[str, Any]:
        await client.delete_task(args["task_id"])
        return {"deleted": True}

    async def tool_add_comment(args: Dict[str, Any]) -> Dict[str, Any]:
        return await client.add_comment(args["task_id"], args["comment_text"])

    return {
        "clickup_list_workspaces": tool_list_workspaces,
        "clickup_list_spaces": tool_list_spaces,
        "clickup_list_lists": tool_list_lists,
        "clickup_create_task": tool_create_task,
        "clickup_get_task": tool_get_task,
        "clickup_update_task": tool_update_task,
        "clickup_delete_task": tool_delete_task,
        "clickup_add_comment": tool_add_comment,
    }


async def _quick_smoke_test() -> None:
    """Pequeña prueba: lista primer workspace/space/lista y crea/borra una tarea temporal."""
    client = ClickUpTools()
    teams = await client.list_workspaces()
    assert teams, "No hay workspaces disponibles"
    ws = teams[0]["id"]
    spaces = await client.list_spaces(ws)
    assert spaces, "No hay spaces disponibles"
    space_id = spaces[0]["id"]
    lists = await client.list_lists_by_space(space_id)
    assert lists, "No hay listas disponibles"
    list_id = lists[0]["id"]
    created = await client.create_task(list_id, name="LangGraph Test Task", description="Temporal")
    task_id = created["id"]
    await client.add_comment(task_id, "Comentario de prueba")
    await client.update_task(task_id, status="to do")
    await client.delete_task(task_id)


if __name__ == "__main__":
    asyncio.run(_quick_smoke_test())



