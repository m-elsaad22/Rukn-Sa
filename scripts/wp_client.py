#!/usr/bin/env python3
"""WordPress REST helper for rukn-eltatawer.com/sa."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any

BASE = "https://www.rukn-eltatawer.com/sa/wp-json"
AUTH_USER = "cursor"
AUTH_PASS = "PCkk ig95 Gu6c zOgC GLYG FYsk"
PHONE = "0568060309"
WHATSAPP = "0568060309"
WA_INTL = "966568060309"
UA = "Mozilla/5.0 RuknRewrite/2026-09"

import base64

_AUTH = base64.b64encode(f"{AUTH_USER}:{AUTH_PASS}".encode()).decode()
HEADERS = {
    "Authorization": f"Basic {_AUTH}",
    "Content-Type": "application/json",
    "User-Agent": UA,
    "Accept": "application/json",
}


def _req(method: str, path: str, payload: dict | None = None, timeout: int = 120) -> tuple[Any, dict]:
    url = path if path.startswith("http") else BASE + path
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    r = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            body = json.loads(raw) if raw else None
            return body, dict(resp.headers)
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")[:2000]
        raise RuntimeError(f"HTTP {e.code} {method} {url}: {err}") from e


def get(path: str, timeout: int = 120) -> tuple[Any, dict]:
    return _req("GET", path, timeout=timeout)


def post(path: str, payload: dict, timeout: int = 120) -> tuple[Any, dict]:
    return _req("POST", path, payload, timeout=timeout)


def put(path: str, payload: dict, timeout: int = 180) -> tuple[Any, dict]:
    return _req("PUT", path, payload, timeout=timeout)


def delete(path: str, timeout: int = 60) -> tuple[Any, dict]:
    return _req("DELETE", path + ("&" if "?" in path else "?") + "force=true", timeout=timeout)


def get_paged(path: str, per_page: int = 100, extra: str = "", sleep: float = 0.15) -> list:
    items: list = []
    page = 1
    while True:
        sep = "&" if "?" in path else "?"
        body, hdr = get(f"{path}{sep}per_page={per_page}&page={page}{extra}")
        if not body:
            break
        items.extend(body)
        total_pages = int(hdr.get("X-WP-TotalPages") or hdr.get("x-wp-totalpages") or 1)
        if page >= total_pages:
            break
        page += 1
        if sleep:
            time.sleep(sleep)
    return items
