"""Utility to generate JWT tokens for development.

This script prints a valid access token using the same settings as backend.auth.
Usage (PowerShell):
  python -m backend.generate_token [-Subject <email>] [-Minutes <int>] [-Role <role>]

Defaults:
  Subject: admin@fado.vn
  Minutes: 30
  Role: admin
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta

from jose import jwt

from .auth import ALGORITHM, SECRET_KEY


def generate_access_token(subject: str, role: str = "admin", minutes: int = 30) -> str:
    """Create a short-lived access token for local testing."""
    exp = datetime.utcnow() + timedelta(minutes=minutes)
    payload = {"sub": subject, "role": role, "type": "access", "exp": exp}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a JWT access token for testing")
    parser.add_argument("--subject", "-s", default="admin@fado.vn", help="Subject (email)")
    parser.add_argument("--minutes", "-m", type=int, default=30, help="Expiry in minutes")
    parser.add_argument("--role", "-r", default="admin", help="Role claim")
    args = parser.parse_args()

    token = generate_access_token(args.subject, role=args.role, minutes=args.minutes)
    print(token)


if __name__ == "__main__":
    main()
