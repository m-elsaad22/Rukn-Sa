#!/usr/bin/env python3
"""Rewrite pest-control posts that inherited maintenance/AC boilerplate."""
from __future__ import annotations

import hashlib
import json
import re
import urllib.request
import base64

BASE = "https://www.rukn-eltatawer.com/sa/wp-json"
AUTH = base64.b64encode(b"cursor:PCkk ig95 Gu6c zOgC GLYG FYsk").decode()
H = {
    "Authorization": f"Basic {AUTH}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
}


def get(path: str):
    r = urllib.request.Request(BASE + path, headers=H)
    with urllib.request.urlopen(r, timeout=90) as resp:
        return json.loads(resp.read().decode())


def put(path: str, payload: dict):
    r = urllib.request.Request(
        BASE + path, data=json.dumps(payload).encode(), headers=H, method="PUT"
    )
    with urllib.request.urlopen(r, timeout=90) as resp:
        return json.loads(resp.read().decode())


# Content builders live in the cloud run that produced data/pest-*.json
# This file documents the repair entrypoint for re-runs.
if __name__ == "__main__":
    print("Use the cloud agent run artifacts in data/pest-mismatch-rewrite.json")
