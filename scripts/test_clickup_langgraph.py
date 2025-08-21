"""
Pruebas exhaustivas para la biblioteca de herramientas LangGraph de ClickUp.

Usa CLICKUP_API_TOKEN del entorno.
"""

from __future__ import annotations

import asyncio
import os
from typing import Dict, Any

from langgraph_tools.clickup import ClickUpTools
from dotenv import load_dotenv


async def run_suite() -> None:
    load_dotenv()
    token = os.getenv("CLICKUP_API_TOKEN")
    assert token, "CLICKUP_API_TOKEN no configured"

    client = ClickUpTools(api_token=token)

    # 1) Descubrimiento
    teams = await client.list_workspaces()
    assert teams, "No se encontraron workspaces"
    ws_id = teams[0]["id"]

    spaces = await client.list_spaces(ws_id)
    assert spaces, "No se encontraron spaces"
    space_id = spaces[0]["id"]

    lists = await client.list_lists_by_space(space_id)
    assert lists, "No se encontraron listas"
    list_id = lists[0]["id"]

    # 2) Create tarea
    created = await client.create_task(list_id, name="Test LangGraph Tools", description="End-to-end")
    task_id = created["id"]
    print("CREATED:", task_id)

    # 3) Get task
    got = await client.get_task(task_id)
    assert got["id"] == task_id

    # 4) Update task (status / description)
    await client.update_task(task_id, status="to do", description="Updated")
    got2 = await client.get_task(task_id)
    assert got2.get("status", {}).get("status", "") in {"to do", "to_do", "open"}

    # 5) Add comment
    await client.add_comment(task_id, "Comentario desde test suite")

    # 6) List tasks by list (smoke)
    tasks = await client.list_tasks_in_list(list_id, include_closed=False)
    assert isinstance(tasks, list)

    # 7) Delete task
    await client.delete_task(task_id)
    print("DELETED:", task_id)


if __name__ == "__main__":
    asyncio.run(run_suite())


