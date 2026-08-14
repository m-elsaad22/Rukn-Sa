#!/usr/bin/env python3
"""Re-run a lightweight WordPress content audit for rukn-eltatawer.com/sa."""

from __future__ import annotations

import base64
import csv
import html
import json
import os
import re
import ssl
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

BASE = os.environ.get("WP_BASE", "https://www.rukn-eltatawer.com/sa/wp-json")
USER = os.environ.get("WP_USER", "")
PASSWORD = os.environ.get("WP_APP_PASSWORD", "")
OUT_DIR = Path(__file__).resolve().parents[1] / "data"
CTX = ssl.create_default_context()


def get(url: str, auth: bool = True):
    req = urllib.request.Request(url)
    if auth:
        if not USER or not PASSWORD:
            raise SystemExit("Set WP_USER and WP_APP_PASSWORD")
        token = base64.b64encode(f"{USER}:{PASSWORD}".encode()).decode()
        req.add_header("Authorization", f"Basic {token}")
    with urllib.request.urlopen(req, context=CTX, timeout=60) as resp:
        return json.loads(resp.read().decode()), dict(resp.headers)


def fetch_all(endpoint: str, extra: str = ""):
    items, page = [], 1
    while True:
        data, headers = get(f"{BASE}{endpoint}?per_page=100&page={page}{extra}")
        if not data:
            break
        items.extend(data)
        if page >= int(headers.get("X-WP-TotalPages", 1)):
            break
        page += 1
    return items


def strip_html(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def word_count(text: str) -> int:
    return len(re.findall(r"[\w\u0600-\u06FF]+", text, re.U))


def main() -> None:
    me, _ = get(f"{BASE}/wp/v2/users/me")
    print(f"Logged in as {me.get('slug')} roles={me.get('roles')}")

    posts = fetch_all("/wp/v2/posts", "&status=publish&context=edit")
    drafts = fetch_all("/wp/v2/posts", "&status=draft&context=edit")
    services = fetch_all("/wp/v2/services", "&status=publish&context=edit")

    rows = []
    phone_counter = Counter()
    thin_cities = []

    for post in posts:
        title = strip_html(post.get("title", {}).get("raw") or "")
        content = strip_html(post.get("content", {}).get("raw") or post.get("content", {}).get("rendered") or "")
        wc = word_count(content)
        has_uae = bool(re.search(r"\+971|00971", content))
        has_placeholder = "0500000000" in content
        for match in re.findall(r"\+971[\d\s-]+|0500000000|05\d{8}|\+966[\d\s-]+", content):
            phone_counter[match.strip()] += 1

        if re.search(r"كشف تسربات المياه في ", title):
            ptype = "city-leak"
            if wc < 100:
                thin_cities.append(title)
        elif wc < 50:
            ptype = "thin-hub"
        elif wc >= 400:
            ptype = "guide"
        else:
            ptype = "other"

        if has_uae or has_placeholder:
            urgency = "critical"
        elif wc < 100:
            urgency = "high"
        elif not post.get("featured_media"):
            urgency = "low"
        else:
            urgency = "ok"

        rows.append(
            {
                "id": post["id"],
                "title": title,
                "type": ptype,
                "words": wc,
                "modified": post["modified"][:10],
                "urgency": urgency,
                "uae_phone": has_uae,
                "placeholder_phone": has_placeholder,
                "featured_media": post.get("featured_media") or 0,
                "url": post["link"],
            }
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUT_DIR / "articles-audit.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: ({"critical": 0, "high": 1, "low": 2, "ok": 3}[r["urgency"]], r["words"])))

    summary = {
        "posts": len(posts),
        "drafts": len(drafts),
        "services": len(services),
        "urgency": Counter(r["urgency"] for r in rows),
        "types": Counter(r["type"] for r in rows),
        "thin_city_pages": len(thin_cities),
        "phones": phone_counter.most_common(10),
        "service_word_counts": [
            {
                "title": strip_html(s.get("title", {}).get("raw") or ""),
                "words": word_count(strip_html(s.get("content", {}).get("raw") or "")),
                "modified": s["modified"][:10],
                "url": s["link"],
            }
            for s in services
        ],
        "draft_ids": [d["id"] for d in drafts],
    }
    summary_path = OUT_DIR / "audit-summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {csv_path}")
    print(f"Wrote {summary_path}")
    print(json.dumps({"posts": summary["posts"], "urgency": summary["urgency"], "types": summary["types"]}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"HTTP {exc.code}: {exc.read().decode()[:300]}") from exc
