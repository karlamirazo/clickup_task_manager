import asyncio
import os
import sys
from typing import Any, Dict

# Asegurar root en path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from integrations.clickup.client import ClickUpClient
from core.database import SessionLocal
from models.task import Task


async def main(clickup_task_id: str) -> None:
    client = ClickUpClient()
    # ClickUp
    cu: Dict[str, Any] = {}
    try:
        cu = await client.get_task(clickup_task_id)
    except Exception as e:
        print({"clickup_error": str(e)})

    cu_status = None
    if cu:
        if isinstance(cu.get("status"), dict):
            cu_status = str(cu["status"].get("status"))
        else:
            cu_status = str(cu.get("status"))

    # DB local
    db_status = None
    db_id = None
    try:
        db = SessionLocal()
        row = db.query(Task).filter(Task.clickup_id == clickup_task_id).first()
        if row:
            db_status = row.status
            db_id = row.id
    except Exception as e:
        print({"db_error": str(e)})
    finally:
        try:
            db.close()
        except Exception:
            pass

    print({
        "clickup_id": clickup_task_id,
        "clickup_status": cu_status,
        "db_local_id": db_id,
        "db_local_status": db_status,
        "clickup_name": cu.get("name") if cu else None,
    })


if __name__ == "__main__":
    # Por defecto revisar la tarea Dependencias (86b6zzqfh)
    clickup_task_id = sys.argv[1] if len(sys.argv) > 1 else "86b6zzqfh"
    asyncio.run(main(clickup_task_id))







