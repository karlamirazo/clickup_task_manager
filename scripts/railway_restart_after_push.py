#!/usr/bin/env python3
"""
Reinicia el servicio de Railway tras un push cuando el deployment falla.

Uso:
  python scripts/railway_restart_after_push.py \
    --project ff751b77-21e2-4508-a247-5e4bbb9c00f9 \
    --service 203045a3-fb41-4abf-b28f-32653251621d \
    --env 43e813bd-acb3-48df-81b3-5a7db854b9e9 \
    --token b3059aec-9c1f-4af9-a143-82839d99aaa3
"""

import argparse
import sys
import requests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--service", required=True)
    parser.add_argument("--env", required=True)
    parser.add_argument("--token", required=True)
    args = parser.parse_args()

    base = "https://backboard.railway.app/graphql/v2"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {args.token}",
    }

    # Restart mutation
    query = {
        "query": "mutation ServiceRestart($serviceId: String!, $environmentId: String!) { serviceRestart(serviceId: $serviceId, environmentId: $environmentId) }",
        "variables": {
            "serviceId": args.service,
            "environmentId": args.env,
        },
        "operationName": "ServiceRestart",
    }

    try:
        resp = requests.post(base, json=query, headers=headers, timeout=25)
        resp.raise_for_status()
        data = resp.json()
        ok = data.get("data", {}).get("serviceRestart")
        if ok:
            print("✅ Servicio reiniciado correctamente")
            sys.exit(0)
        else:
            print("❌ No se pudo reiniciar el servicio", data)
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error reiniciando servicio: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()





