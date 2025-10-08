import asyncio
import json
import os
import sys
from typing import Dict, Any, List

# Asegurar que el root del proyecto esté en sys.path cuando se ejecuta desde scripts/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from integrations.clickup.client import ClickUpClient
from core.config import settings


async def find_tasks_with_dependencies(max_spaces: int = 5, max_lists_per_space: int = 10, max_tasks_per_list: int = 50) -> List[Dict[str, Any]]:
    client = ClickUpClient()
    results: List[Dict[str, Any]] = []

    workspaces = await client.get_workspaces()
    workspace_id = settings.CLICKUP_WORKSPACE_ID or (workspaces[0]["id"] if workspaces else None)
    if not workspace_id:
        return results

    spaces = await client.get_spaces(workspace_id)
    for space in spaces[:max_spaces]:
        space_id = space.get("id")
        space_name = space.get("name")
        lists = await client.get_lists(space_id)
        for lst in lists[:max_lists_per_space]:
            list_id = lst.get("id")
            list_name = lst.get("name")
            tasks = await client.get_tasks(list_id, include_closed=True, limit=max_tasks_per_list)
            for task in tasks:
                task_id = task.get("id")
                task_name = task.get("name")
                blocking_tasks = await client.get_blocking_tasks(task_id)
                if blocking_tasks:
                    blockers_summary = []
                    for bt in blocking_tasks:
                        bt_status = ""
                        if isinstance(bt.get("status"), dict):
                            bt_status = str(bt["status"].get("status", "")).lower()
                        else:
                            bt_status = str(bt.get("status", "")).lower()
                        blockers_summary.append({
                            "id": bt.get("id"),
                            "name": bt.get("name"),
                            "status": bt_status,
                        })
                    results.append({
                        "space": {"id": space_id, "name": space_name},
                        "list": {"id": list_id, "name": list_name},
                        "task": {"id": task_id, "name": task_name},
                        "blocking": blockers_summary,
                    })
    return results


async def main() -> None:
    try:
        findings = await find_tasks_with_dependencies()
        print(json.dumps({"count": len(findings), "items": findings}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())


