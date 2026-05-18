#!/usr/bin/env python3
"""
Shared Cognito auth helper for test platform scripts.

Reads API URL and Cognito config from ../swen-project-react-app/.env,
then performs USER_PASSWORD_AUTH to get an ID token.

Usage (in other scripts):
    from _auth import base_url, get_cognito_token, auth_headers
"""

import os
import re
from pathlib import Path

import boto3

_ENV_FILE = Path(__file__).parent.parent / "webapp" / "swen-project-react-app" / ".env"

_cached_token: str | None = None
_config: dict | None = None


def _load_env() -> dict:
    global _config
    if _config:
        return _config

    if not _ENV_FILE.exists():
        raise FileNotFoundError(
            f".env not found at {_ENV_FILE}\n"
            "Run 'terraform apply' in terraform/ to generate it."
        )

    cfg = {}
    for line in _ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^(\w+)=(.*)$", line)
        if m:
            cfg[m.group(1)] = m.group(2).strip('"').strip("'")

    required = ["VITE_API_URL", "VITE_COGNITO_REGION", "VITE_COGNITO_USER_POOL_ID", "VITE_COGNITO_CLIENT_ID"]
    missing = [k for k in required if k not in cfg]
    if missing:
        raise ValueError(f".env is missing required keys: {missing}")

    _config = cfg
    return cfg


def base_url() -> str:
    """Return the API base URL (no trailing slash)."""
    return _load_env()["VITE_API_URL"].rstrip("/")


def get_cognito_token() -> str:
    """Return a cached Cognito ID token. Reads EMAIL/PASSWORD from env or prompts."""
    global _cached_token
    if _cached_token:
        return _cached_token

    cfg = _load_env()
    email = os.environ.get("TRAIL_EMAIL") or input("Cognito email: ")
    password = os.environ.get("TRAIL_PASSWORD") or input("Cognito password: ")

    client = boto3.client("cognito-idp", region_name=cfg["VITE_COGNITO_REGION"])
    resp = client.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": email, "PASSWORD": password},
        ClientId=cfg["VITE_COGNITO_CLIENT_ID"],
    )
    _cached_token = resp["AuthenticationResult"]["IdToken"]
    return _cached_token


def auth_headers() -> dict:
    """Return headers dict with Authorization: Bearer <token>."""
    return {"Authorization": f"Bearer {get_cognito_token()}", "Content-Type": "application/json"}
