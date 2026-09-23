#!/usr/bin/env python3
"""Apply KSA hub designs + theme hardening to live WordPress /sa/."""
from __future__ import annotations

import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "audit"))
from hub_pages import CITIES, HUBS, TERMS, city_page  # noqa: E402

CTX = ssl.create_default_context()
UA = "RuknThemeFix/2026-09-23"


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


class HttpError(RuntimeError):
    def __init__(self, status: int, body: str):
        super().__init__(f"HTTP {status}: {body[:300]}")
        self.status = status
        self.body = body


class Wp:
    def __init__(self, delay: float = 0.35):
        self.delay = delay

    def request(self, method: str, path: str, payload=None, query=None):
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
            with urllib.request.urlopen(req, context=CTX, timeout=90) as r:
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

    def post(self, path: str, payload):
        body, _, status = self.request("POST", path, payload=payload)
        return body, status


def snippet_code(name: str) -> str:
    return (ROOT / "audit" / "snippets" / name).read_text(encoding="utf-8")


def upsert_snippet(wp: Wp, snippet_id: int | None, name: str, filename: str, desc: str, scope: str = "global"):
    code = snippet_code(filename)
    payload = {
        "name": name,
        "desc": desc,
        "code": code,
        "scope": scope,
        "active": True,
        "priority": 10 if "16-" in filename else 0,
    }
    if snippet_id:
        try:
            body, status = wp.put(f"/wp-json/code-snippets/v1/snippets/{snippet_id}", payload)
            print(f"  snippet #{snippet_id} PUT {status} active={body.get('active')} err={body.get('code_error')}")
            return body
        except HttpError as e:
            print(f"  snippet #{snippet_id} PUT fail {e}")
    body, status = wp.post("/wp-json/code-snippets/v1/snippets", payload)
    print(f"  snippet created id={body.get('id')} POST {status} err={body.get('code_error')}")
    return body


def find_snippet(wp: Wp, name_substr: str) -> dict | None:
    data, _ = wp.get("/wp-json/code-snippets/v1/snippets", per_page="50")
    if not isinstance(data, list):
        return None
    for s in data:
        if name_substr.lower() in (s.get("name") or "").lower():
            return s
    return None


def rankmath(wp: Wp, object_id: int, title: str, desc: str, keyword: str, object_type: str = "post") -> str:
    payload = {
        "objectType": object_type,
        "objectID": object_id,
        "meta": {
            "rank_math_title": title,
            "rank_math_description": desc,
            "rank_math_focus_keyword": keyword,
            "rank_math_robots": ["index", "follow"],
        },
    }
    try:
        wp.post("/wp-json/rankmath/v1/updateMeta", payload)
        return "ok"
    except HttpError as e:
        return f"fail {e.status}"


def pages_by_slug(wp: Wp) -> dict[str, dict]:
    out = {}
    page = 1
    while page <= 5:
        data, hdrs = wp.get("/wp-json/wp/v2/pages", per_page="50", page=str(page), _fields="id,slug,status,link,parent")
        if not isinstance(data, list) or not data:
            break
        for p in data:
            out[p["slug"]] = p
        total_pages = int(hdrs.get("X-WP-TotalPages") or hdrs.get("x-wp-totalpages") or 1)
        if page >= total_pages:
            break
        page += 1
    return out


def upsert_page(wp: Wp, slug: str, spec: dict, existing: dict, parent: int = 0) -> dict:
    payload = {
        "title": spec["title"],
        "content": spec["content"],
        "excerpt": spec["excerpt"],
        "status": "publish",
        "slug": slug,
    }
    if parent:
        payload["parent"] = parent
    if slug in existing:
        pid = existing[slug]["id"]
        body, status = wp.put(f"/wp-json/wp/v2/pages/{pid}", payload)
        print(f"  page {slug} id={pid} PUT {status}")
    else:
        body, status = wp.post("/wp-json/wp/v2/pages", payload)
        print(f"  page {slug} created id={body.get('id')} POST {status}")
        pid = body.get("id")
    if pid:
        rm = rankmath(wp, int(pid), spec["rm_title"], spec["rm_desc"], spec["kw"])
        print(f"    rankmath {rm}")
    return body if isinstance(body, dict) else {}


UAE_MARKERS = (
    "إمارات",
    "الامارات",
    "دبي",
    "أبوظبي",
    "ابوظبي",
    "الشارقة",
    "عجمان",
    "الفجيرة",
    "أم القيوين",
    "971568060309",
    "0568060309",
)


def clean_categories(wp: Wp) -> int:
    n = 0
    page = 1
    while page <= 30:
        data, hdrs = wp.get(
            "/wp-json/wp/v2/categories",
            per_page="50",
            page=str(page),
            hide_empty="false",
            _fields="id,slug,name,description,count",
        )
        if not isinstance(data, list) or not data:
            break
        for c in data:
            blob = json.dumps(c, ensure_ascii=False)
            name = c.get("name") or ""
            desc = c.get("description") or ""
            new_name = name
            for ch in "🚚💧🧹🧴🧼🧽🏠":
                new_name = new_name.replace(ch, "")
            new_name = " ".join(new_name.split())
            new_desc = desc
            # reuse PHP-equivalent light replacements in Python
            replacements = [
                ("تغطي خدماتنا جميع إمارات الدولة، بدءًا من أبوظبي ودبي، وصولًا إلى الشارقة وعجمان، وأم القيوين، ورأس الخيمة، والفجيرة.",
                 "تغطي خدماتنا مدن المملكة بما في ذلك الرياض وجدة ومكة والمدينة والدمام والخبر والطائف وأبها."),
                ("داخل الإمارات", "داخل السعودية"),
                ("في الإمارات", "في السعودية"),
                ("في الامارات", "في السعودية"),
                ("دولة الإمارات العربية المتحدة", "المملكة العربية السعودية"),
                ("إمارات الدولة", "مدن المملكة"),
                ("أبوظبي: محمد بن زايد، خليفة، شخبوط، بني ياس، الشهامة", ""),
                ("دبي: وسط المدينة، مردف، البرشاء، ديرة، الجميرا", ""),
                ("باقي الإمارات: العين، الشارقة، رأس الخيمة، الفجيرة، عجمان، أم القيوين", ""),
                ("+971568060309", ""),
                ("971568060309", ""),
                ("tel:0568060309", ""),
                ("0568060309", ""),
                ("خصم 15% على أول طلب للعملاء الجدد عبر", ""),
            ]
            for old, new in replacements:
                new_desc = new_desc.replace(old, new)
            payload = {}
            if new_name != name:
                payload["name"] = new_name
            if new_desc != desc:
                payload["description"] = new_desc
            if payload:
                try:
                    wp.put(f"/wp-json/wp/v2/categories/{c['id']}", payload)
                    n += 1
                    print(f"  cat {c['slug']} cleaned")
                except HttpError as e:
                    print(f"  cat {c['slug']} fail {e.status}")
        total_pages = int(hdrs.get("X-WP-TotalPages") or hdrs.get("x-wp-totalpages") or 1)
        if page >= total_pages:
            break
        page += 1
    return n


def main() -> int:
    if not USER or not PASS:
        print("WP credentials missing", file=sys.stderr)
        return 2
    wp = Wp()
    print("== snippets ==")
    s12 = find_snippet(wp, "Frontend Copy Guard")
    upsert_snippet(
        wp,
        s12["id"] if s12 else 12,
        "Rukn SA Frontend Copy Guard",
        "12-frontend-guard.php",
        "Hide call, unify UAE WhatsApp, strip leftover UAE geo copy, SAR currency, titles fallback",
    )
    s15 = find_snippet(wp, "Trust NAP")
    upsert_snippet(
        wp,
        s15["id"] if s15 else 15,
        "Rukn SA Trust NAP Fix",
        "15-trust-nap.php",
        "WhatsApp UAE temporary, hide call, Saudi identity, dump-keys requires admin",
    )
    s16 = find_snippet(wp, "Theme Hardening")
    upsert_snippet(
        wp,
        s16["id"] if s16 else None,
        "Rukn SA Theme Hardening",
        "16-theme-hardening.php",
        "Force title tags, redirect /sa/sa/ and /city/*, dump-keys 401, EN noindex",
    )
    try:
        wp.post("/wp-json/rukn/v1/apply-trust-fix", {})
        print("  apply-trust-fix ok")
    except HttpError as e:
        print(f"  apply-trust-fix {e.status}")

    print("== hub pages ==")
    existing = pages_by_slug(wp)
    for slug, spec in HUBS.items():
        upsert_page(wp, slug, spec, existing)

    existing = pages_by_slug(wp)
    print("== terms ==")
    upsert_page(wp, "terms", TERMS, existing)

    existing = pages_by_slug(wp)
    cities_id = int(existing.get("cities", {}).get("id") or 0)
    print("== city pages parent", cities_id, "==")
    for slug, name in CITIES:
        spec = {
            "title": f"خدمات ركن التطور في {name}",
            "excerpt": f"روابط خدمات ركن التطور المرتبطة بمدينة {name} في السعودية.",
            "content": city_page(slug, name),
            "rm_title": f"{name} | ركن التطور السعودية",
            "rm_desc": f"خدمات منزلية في {name}: روابط المقالات المرتبطة بالمدينة دون أرقام وصول مخترعة.",
            "kw": f"ركن التطور {name}",
        }
        upsert_page(wp, slug, spec, existing, parent=cities_id)

    print("== categories ==")
    n = clean_categories(wp)
    print(f"  cleaned {n} categories")

    print("DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
