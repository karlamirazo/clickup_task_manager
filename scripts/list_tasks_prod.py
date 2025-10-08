#!/usr/bin/env python3
import requests

URL = "https://ctm-pro.up.railway.app/api/v1?limit=500"

def sanitize(text: str) -> str:
    if not text:
        return ""
    return str(text).replace("\n", " ").replace(",", " ").strip()

def main():
    r = requests.get(URL, timeout=60)
    r.raise_for_status()
    data = r.json()

    print("name,status,clickup_id")
    for t in data:
        name = sanitize(t.get("name"))
        status = sanitize(t.get("status"))
        cid = sanitize(t.get("clickup_id"))
        print(f"{name},{status},{cid}")

if __name__ == "__main__":
    main()




