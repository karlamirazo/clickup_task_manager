#!/usr/bin/env python3
import csv
from collections import defaultdict

INPUT_CSV = "tasks_prod.csv"

def main():
    groups = defaultdict(list)
    # Intentar UTF-8 y caer a latin-1 si hay BOM o caracteres no válidos
    try:
        f = open(INPUT_CSV, newline='', encoding='utf-8')
        reader = csv.DictReader(f)
    except Exception:
        f = open(INPUT_CSV, newline='', encoding='latin-1')
        reader = csv.DictReader(f)
        for row in reader:
            status = (row.get('status') or '').strip().lower()
            name = (row.get('name') or '').strip()
            cid = (row.get('clickup_id') or '').strip()
            groups[status].append((name, cid))
    f.close()

    # Print grouped results
    for key in sorted(groups.keys()):
        print(f"\n=== {key.upper()} ({len(groups[key])}) ===")
        for name, cid in groups[key]:
            print(f"- {name} | {cid}")

if __name__ == "__main__":
    main()


