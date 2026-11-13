# -*- coding: utf-8 -*-
"""WordPress REST helpers for Bisha draft creation."""

from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

BASE = os.environ.get("WP_BASE", "https://www.rukn-eltatawer.com/sa/wp-json")
WP_USER = os.environ.get("WP_USER", "cursor")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "")


def _auth_header() -> str:
    if not WP_APP_PASSWORD:
        raise RuntimeError("Set WP_APP_PASSWORD (WordPress Application Password) in the environment.")
    token = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()
    return f"Basic {token}"


def request(
    method: str,
    path: str,
    params: Optional[Dict] = None,
    body: Optional[Dict] = None,
    retries: int = 4,
) -> Tuple[Any, Dict[str, str]]:
    q = ("?" + urllib.parse.urlencode(params, doseq=True)) if params else ""
    url = BASE + path + q
    data = None
    headers = {
        "Authorization": _auth_header(),
        "Accept": "application/json",
        "User-Agent": "rukn-bisha-rs6/1.0",
    }
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    last_err = None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                raw = resp.read()
                payload = json.loads(raw.decode("utf-8")) if raw else None
                return payload, dict(resp.headers)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", "replace")
            last_err = RuntimeError(f"HTTP {e.code} {method} {path}: {err_body[:500]}")
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise last_err
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise
    raise last_err  # type: ignore


def search_posts(term: str, status: str = "any") -> List[dict]:
    out: List[dict] = []
    page = 1
    while True:
        data, headers = request(
            "GET",
            "/wp/v2/posts",
            {
                "search": term,
                "status": status,
                "per_page": 100,
                "page": page,
                "context": "edit",
            },
        )
        if not data:
            break
        out.extend(data)
        total_pages = int(headers.get("X-WP-TotalPages", 1))
        if page >= total_pages:
            break
        page += 1
    return out


def get_by_slug(slug: str) -> Optional[dict]:
    data, _ = request(
        "GET",
        "/wp/v2/posts",
        {"slug": slug, "status": "any", "context": "edit"},
    )
    return data[0] if data else None


def create_draft(
    title: str,
    content: str,
    slug: str,
    categories: List[int],
    featured_media: Optional[int] = None,
) -> dict:
    body: Dict[str, Any] = {
        "title": title,
        "content": content,
        "slug": slug,
        "status": "draft",
        "categories": categories,
    }
    if featured_media:
        body["featured_media"] = featured_media
    data, _ = request("POST", "/wp/v2/posts", body=body)
    return data


def update_rank_math(post_id: int, meta: Dict[str, Any]) -> Any:
    payload = {
        "objectType": "post",
        "objectID": post_id,
        "meta": meta,
    }
    data, _ = request("POST", "/rankmath/v1/updateMeta", body=payload)
    return data
