#!/usr/bin/env python3
import requests
from collections import defaultdict

URL = "https://ctm-pro.up.railway.app/api/v1?limit=500"

def main():
    r = requests.get(URL, timeout=60)
    r.raise_for_status()
    data = r.json()

    groups = defaultdict(list)
    for t in data:
        name = (t.get("name") or "").strip()
        status = (t.get("status") or "").strip().lower()
        cid = (t.get("clickup_id") or "").strip()
        groups[status].append((name, cid))

    def dump(title, keys):
        items = []
        for k in keys:
            for name, cid in groups.get(k, []):
                items.append(f"- {name} | {cid}")
        print(f"\n=== {title} ({len(items)}) ===")
        for line in items:
            print(line)

    dump("COMPLETADAS", ["completado", "complete", "cerrado", "closed"])
    dump("EN CURSO", ["en curso", "in progress", "en progreso"])
    dump("PENDIENTES", ["pendiente", "to do", "open", "abierto"]) 

if __name__ == "__main__":
    main()




