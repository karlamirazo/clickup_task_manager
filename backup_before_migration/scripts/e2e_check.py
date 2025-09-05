from __future__ import annotations

import json
import sys
import time
from typing import Any, Dict

import requests


BASE = "http://localhost:8000"


def must_ok(resp: requests.Response, expected: int | None = None) -> None:
    if expected is not None and resp.status_code != expected:
        raise SystemExit(f"HTTP {resp.status_code}: {resp.text}")
    resp.raise_for_status()


def main() -> None:
    # health
    r = requests.get(f"{BASE}/health", timeout=20)
    must_ok(r, 200)

    # discover workspace -> space -> list
    r = requests.get(f"{BASE}/api/v1/workspaces/", timeout=30)
    must_ok(r, 200)
    data = r.json()
    ws_id = data["workspaces"][0]["clickup_id"]

    r = requests.get(f"{BASE}/api/v1/workspaces/{ws_id}/spaces", timeout=30)
    must_ok(r, 200)
    space_id = r.json()["spaces"][0]["id"]

    r = requests.get(f"{BASE}/api/v1/spaces/{space_id}/lists", timeout=30)
    must_ok(r, 200)
    list_id = r.json()["lists"][0]["id"]

    # create task (probar varias listas por si alguna no permite crear)
    created: Dict[str, Any] | None = None
    clickup_id: str | None = None
    last_err: str | None = None
    for lst in [list_id] + [x["id"] for x in r.json()["lists"][1:]]:
        payload: Dict[str, Any] = {
            "name": "Tarea Prueba E2E",
            "workspace_id": ws_id,
            "list_id": lst,
        }
        rr = requests.post(f"{BASE}/api/v1/tasks/", json=payload, timeout=60)
        if rr.status_code == 201:
            created = rr.json()
            clickup_id = created["clickup_id"]
            print(f"CREATED {clickup_id} in list {lst}")
            break
        else:
            last_err = rr.text
            continue
    if not clickup_id:
        raise SystemExit(f"No se pudo crear tarea en ninguna lista. Ultimo error: {last_err}")

    # get task
    r = requests.get(f"{BASE}/api/v1/tasks/{clickup_id}", timeout=30)
    must_ok(r, 200)
    got = r.json()
    assert got["clickup_id"] == clickup_id
    print(f"GOT {got['id']}")

    # delete task
    r = requests.delete(f"{BASE}/api/v1/tasks/{clickup_id}", timeout=60)
    must_ok(r, 204)
    print("DELETED 204")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"E2E FAILED: {e}")
        sys.exit(1)


