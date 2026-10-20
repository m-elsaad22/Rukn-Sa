#!/usr/bin/env python3
"""Apply GSC indexing fixes to live WordPress /sa/ (redirects, noindex, sitemap)."""
from __future__ import annotations

import csv
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CTX = ssl.create_default_context()
UA = "RuknGSC/2026-10-20"


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = val


load_dotenv(ROOT / ".env")
BASE = (os.environ.get("WP_BASE_URL") or "https://www.rukn-eltatawer.com/sa").rstrip("/")
USER = os.environ.get("WP_USERNAME") or os.environ.get("WP_USER") or ""
PASS = os.environ.get("WP_APP_PASSWORD") or ""
PUBLIC = "https://www.rukn-eltatawer.com"


class HttpError(RuntimeError):
    def __init__(self, status: int, body: str):
        super().__init__(f"HTTP {status}: {body[:400]}")
        self.status = status
        self.body = body


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


class Wp:
    def __init__(self, delay: float = 0.25):
        self.delay = delay

    def request(self, method: str, path: str, payload=None, query=None, timeout=90):
        url = BASE + path
        if query:
            url += ("&" if "?" in url else "?") + urllib.parse.urlencode(query)
        data = None
        headers = {"User-Agent": UA, "Accept": "application/json"}
        if USER and PASS:
            import base64

            headers["Authorization"] = "Basic " + base64.b64encode(f"{USER}:{PASS}".encode()).decode()
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode()
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        time.sleep(self.delay)
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
                raw = r.read()
                hdrs = dict(r.headers)
                body = json.loads(raw.decode()) if raw else None
                return body, hdrs, r.status
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", "replace")
            raise HttpError(e.code, raw) from e

    def get(self, path: str, **query):
        body, hdrs, _ = self.request("GET", path, query=query or None)
        return body, hdrs

    def put(self, path: str, payload):
        body, _, status = self.request("PUT", path, payload=payload)
        return body, status

    def post(self, path: str, payload=None):
        body, _, status = self.request("POST", path, payload=payload if payload is not None else {})
        return body, status


def public_status(url: str, timeout: int = 25):
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method="GET")
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=CTX), NoRedirect())
    try:
        with opener.open(req, timeout=timeout) as resp:
            body = resp.read(8000)
            return resp.status, dict(resp.headers), body, resp.geturl()
    except urllib.error.HTTPError as e:
        body = e.read(4000) if e.fp else b""
        loc = e.headers.get("Location") if e.headers else None
        return e.code, dict(e.headers or {}), body, loc
    except Exception as e:  # noqa: BLE001
        return 0, {}, str(e).encode(), None


def load_redirects() -> list[dict]:
    path = ROOT / "audit" / "seo-fix" / "redirects.csv"
    return list(csv.DictReader(path.open(encoding="utf-8")))


def find_snippet(wp: Wp, name_substr: str):
    data, _ = wp.get("/wp-json/code-snippets/v1/snippets", per_page="100")
    if not isinstance(data, list):
        return None
    for s in data:
        if name_substr.lower() in (s.get("name") or "").lower():
            return s
    return None


def upsert_snippet(wp: Wp, snippet_id, name: str, filename: str, desc: str, priority: int = 5):
    code = (ROOT / "audit" / "snippets" / filename).read_text(encoding="utf-8")
    payload = {
        "name": name,
        "desc": desc,
        "code": code,
        "scope": "global",
        "active": True,
        "priority": priority,
    }
    if snippet_id:
        body, status = wp.put(f"/wp-json/code-snippets/v1/snippets/{snippet_id}", payload)
        print(f"  snippet #{snippet_id} PUT {status} active={body.get('active')} err={body.get('code_error')}")
        return body
    body, status = wp.post("/wp-json/code-snippets/v1/snippets", payload)
    print(f"  snippet created id={body.get('id')} POST {status} err={body.get('code_error')}")
    return body


def draft_cannibals(wp: Wp, rows: list[dict]) -> dict:
    stats = {"drafted": 0, "already": 0, "fail": 0}
    for row in rows:
        pid = (row.get("id_from") or "").strip()
        if not pid.isdigit():
            continue
        try:
            post, _ = wp.get(f"/wp-json/wp/v2/posts/{pid}", context="edit", _fields="id,status,slug,link")
        except HttpError as e:
            print(f"  get {pid} fail {e.status}")
            stats["fail"] += 1
            continue
        status = (post or {}).get("status")
        if status == "draft":
            stats["already"] += 1
            continue
        if status != "publish":
            print(f"  skip {pid} status={status}")
            stats["already"] += 1
            continue
        try:
            body, st = wp.put(f"/wp-json/wp/v2/posts/{pid}", {"status": "draft"})
            print(f"  draft {pid} {post.get('slug')} PUT {st} -> {body.get('status')}")
            stats["drafted"] += 1
        except HttpError as e:
            print(f"  draft {pid} fail {e.status}")
            stats["fail"] += 1
    return stats


def verify(rows: list[dict]) -> dict:
    report = {"redirects": Counter(), "bad": []}
    checks = []
    for row in rows:
        src = row["source"]
        dest = row["destination"].rstrip("/") + "/"
        url = PUBLIC + src
        checks.append((url, dest, src))
    extras = [
        (f"{PUBLIC}/sa/sa/", f"{PUBLIC}/sa/", "/sa/sa/"),
        (f"{PUBLIC}/sa/city/riyadh/", f"{PUBLIC}/sa/cities/riyadh/", "/city/riyadh/"),
        (
            f"{PUBLIC}/sa/city/{urllib.parse.quote('الرياض')}/",
            f"{PUBLIC}/sa/cities/riyadh/",
            "/city/الرياض/",
        ),
        (f"{PUBLIC}/sa/page/2/", f"{PUBLIC}/sa/", "/page/2/"),
        (f"{PUBLIC}/sa/?p=1", f"{PUBLIC}/sa/", "?p=1"),
        (f"{PUBLIC}/sa/en/about/", f"{PUBLIC}/sa/en/", "/en/about/"),
    ]
    for item in extras:
        checks.append(item)

    for url, dest, label in checks:
        st, hdrs, body, loc = public_status(url)
        loc_n = (loc or hdrs.get("Location") or "").split("?")[0].rstrip("/") + ("/" if loc else "")
        dest_n = dest.split("?")[0].rstrip("/") + "/"
        report["redirects"][st] += 1
        ok = st in (301, 308) and dest_n.rstrip("/") in loc_n.rstrip("/")
        if not ok:
            report["bad"].append({"label": label, "status": st, "loc": loc, "expected": dest})
            print(f"  BAD {st} {label} loc={loc} expected={dest}")
        else:
            print(f"  OK  {st} {label} -> {loc}")

    en_st, en_hdrs, en_body, _ = public_status(f"{PUBLIC}/sa/en/")
    html = (en_body or b"").decode("utf-8", "replace")
    robots_hdr = en_hdrs.get("X-Robots-Tag") or en_hdrs.get("x-robots-tag") or ""
    robots_html = "noindex" in html.lower()
    report["en"] = {"status": en_st, "x_robots": robots_hdr, "html_noindex": robots_html}
    print(f"  EN {en_st} x-robots={robots_hdr!r} html_noindex={robots_html}")

    sm_st, _, sm_body, _ = public_status(f"{PUBLIC}/sa/sitemap_index.xml")
    sm = (sm_body or b"").decode("utf-8", "replace")
    children = []
    import re

    children = re.findall(r"<loc>(.*?)</loc>", sm)
    report["sitemap_index"] = {"status": sm_st, "children": children}
    print(f"  sitemap_index {sm_st} children={children}")

    pg_st, _, pg_body, _ = public_status(f"{PUBLIC}/sa/page-sitemap.xml")
    pg = (pg_body or b"").decode("utf-8", "replace")
    page_locs = re.findall(r"<loc>(.*?)</loc>", pg) if pg_st == 200 else []
    report["page_sitemap"] = {"status": pg_st, "count": len(page_locs), "sample": page_locs[:12]}
    print(f"  page-sitemap {pg_st} n={len(page_locs)} sample={page_locs[:8]}")

    keep_st, _, _, _ = public_status(f"{PUBLIC}/sa/water-leak-detection-jeddah/")
    report["keeper"] = keep_st
    print(f"  keeper water-leak-detection-jeddah {keep_st}")
    return report


def main() -> int:
    if not USER or not PASS:
        print("WP credentials missing", file=sys.stderr)
        return 2
    wp = Wp()
    rows = load_redirects()
    print("== snippet 17 ==")
    s17 = find_snippet(wp, "GSC Indexing")
    body = upsert_snippet(
        wp,
        s17["id"] if s17 else None,
        "Rukn SA GSC Indexing Fix",
        "17-gsc-indexing-fix.php",
        "301 cannibals/404 leftovers, noindex EN/author, include pages in sitemap",
        priority=5,
    )
    if body.get("code_error"):
        print("SNIPPET PHP ERROR", body.get("code_error"), file=sys.stderr)
        return 3

    print("== apply-gsc-fix ==")
    try:
        info, st = wp.post("/wp-json/rukn/v1/apply-gsc-fix", {})
        print(f"  POST {st} {json.dumps(info, ensure_ascii=False)[:800]}")
    except HttpError as e:
        print(f"  apply-gsc-fix fail {e}")
        return 4

    print("== draft remaining cannibals ==")
    cannibal = [r for r in rows if (r.get("reason") or "").startswith("intra-city cannibal")]
    stats = draft_cannibals(wp, cannibal)
    print("  draft stats", stats)

    print("== lite-speed already purged by apply-gsc-fix; wait 2s ==")
    time.sleep(2)

    print("== verify ==")
    report = verify(rows)
    out = ROOT / "audit" / "seo-fix" / "gsc-apply-status.json"
    payload = {
        "snippet": {"id": body.get("id"), "active": body.get("active"), "error": body.get("code_error")},
        "draft": stats,
        "verify": {
            "redirect_status": dict(report["redirects"]),
            "bad": report["bad"],
            "en": report["en"],
            "sitemap_index": report["sitemap_index"],
            "page_sitemap": report["page_sitemap"],
            "keeper": report["keeper"],
        },
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", out)
    if report["bad"]:
        print(f"{len(report['bad'])} verification mismatches", file=sys.stderr)
        return 5
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
