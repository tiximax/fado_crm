"""Developer helper: update a system setting via admin API.

This script obtains a short-lived access token and calls
PUT /admin/system-settings/app_name to set the application name.

Usage:
  python -m backend.dev_put_setting --backend http://127.0.0.1:8000 \
      --value "FADO CRM PRO" --description "Ten ung dung"
"""
from __future__ import annotations

import argparse
import sys
from typing import Optional

import requests

from .auth import create_access_token


def put_setting(
    backend_url: str,
    key: str,
    value: str,
    description: Optional[str] = None,
    subject: str = "admin@fado.vn",
    role: str = "admin",
) -> requests.Response:
    token = create_access_token({"sub": subject, "role": role})
    url = f"{backend_url.rstrip('/')}/admin/system-settings/{key}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"value": value}
    if description is not None:
        payload["description"] = description
    resp = requests.put(url, headers=headers, json=payload, timeout=15)
    return resp


def main() -> None:
    parser = argparse.ArgumentParser(description="PUT a system setting via admin API")
    parser.add_argument("--backend", default="http://127.0.0.1:8000", help="Backend base URL")
    parser.add_argument("--key", default="app_name", help="Setting key to update")
    parser.add_argument("--value", required=True, help="Setting value")
    parser.add_argument("--description", default=None, help="Optional description")
    args = parser.parse_args()

    try:
        resp = put_setting(args.backend, args.key, args.value, args.description)
        print(resp.status_code)
        print(resp.text)
        sys.exit(0 if resp.ok else 1)
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(2)


if __name__ == "__main__":
    main()
