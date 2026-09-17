#!/usr/bin/env python3
"""Apply the Rukn SA content-SEO audit: intent rewrites, boilerplate purge,
intra-city cannibalization drafts + Rank Math redirects, missing images.

Reads credentials from `.env` (repo root) or the environment.

THIS SCRIPT DOES NOT WRITE TO WORDPRESS UNLESS YOU PASS BOTH:
    --apply --yes

Default mode is dry-run (plan + logs only).

Usage:
  python3 audit/seo_apply_fixes.py --self-test
  python3 audit/seo_apply_fixes.py --tasks intent,boilerplate,cannibal,images
  python3 audit/seo_apply_fixes.py --tasks all --apply --yes

Environment (.env):
  WP_BASE_URL, WP_USERNAME (or WP_USER), WP_APP_PASSWORD
  LLM_API_KEY, LLM_PROVIDER=openai|gemini, LLM_MODEL
  FEATURED_MEDIA_ID, WHATSAPP_NUMBER
"""

from __future__ import annotations

import argparse
import base64
import csv
import json
import logging
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "audit" / "seo-run"
FIX_DIR = ROOT / "audit" / "seo-fix"
LOG_DIR = FIX_DIR / "logs"
CHECKPOINT_DIR = FIX_DIR / "checkpoints"

DEFAULT_BASE = "https://www.rukn-eltatawer.com/sa"
DEFAULT_MEDIA = 2733
DEFAULT_WA = "971586634710"

CITY_SLUG_RE = re.compile(
    r"-(?:riyadh|jeddah|mecca|makkah|medina|madinah|dammam|khobar|taif|abha|"
    r"al-baha|khafji|rabigh|sakakah|al-kharj|hafar-al-batin|abu-arish)$",
    re.I,
)
DISTRICT_RE = re.compile(r"-(?:east|west|north|south|center)(?=-|$)", re.I)

KEEP_PEAK_TITLE_RE = re.compile(r"نقل|شحن|عفش")
NON_PROPERTY_TITLE_RE = re.compile(
    r"شحن سيارات|شحن أثاث|شحن داخلي|نقل سيارات|مكاتب الشحن|شحن بحري|شحن جوي|شحن بري"
)
PROPERTY_TITLE_RE = re.compile(
    r"شقق|فلل|منازل|عقار|تنظيف|عزل|دهان|سباك|تسرب|صيانة|عشب|جبس|حديق|حمام|مطبخ|"
    r"رخام|كنب|سجاد|مكافحة|كهرب"
)
VILLA_FAQ_IRRELEVANT_RE = re.compile(
    r"شحن سيارات|شحن أثاث|شحن داخلي|شحن بحري|شحن جوي|شحن بري|نقل سيارات|"
    r"دكتات المكيفات|غسيل وتنظيف مكيفات|تنظيف وصيانة دكت"
)

PEAK_PHRASE_RE = re.compile(
    r"(?:أو عندما تريد\s*)?تجهيزاً?\s*مرتباً?\s*قبل\s*انتقال\s*أو\s*موسم\s*ذروة"
    r"(?:\s+في\s+[\u0600-\u06FF ]{2,30})?"
)
AQAR_PHRASE_RE = re.compile(r"لا نضع رقماً?\s*ثابتاً?\s*لا يمثّ?ل عقارك\.?\s*")
VILLA_FAQ_BLOCK_RE = re.compile(
    r"<h([23])[^>]*>((?:(?!</h[123]).){0,500}هل الخدمة للشقق والفلل(?:(?!</h[123]).){0,250})</h\1>"
    r"\s*(?:<p\b[^>]*>.*?</p>)?",
    re.I | re.S,
)
EMPTY_P_RE = re.compile(r"<p[^>]*>\s*</p>", re.I)
EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001F6FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FAFF"
    "\u2600-\u27BF"
    "]+"
)
MD_FENCE_RE = re.compile(r"^```(?:html|HTML)?\s*|\s*```$", re.M)
TEL_HREF_RE = re.compile(r'href=["\']tel:[^"\']+["\']', re.I)

CANNIBAL_ALIASES = {
    "home-plumber-elec": "home-plumber",
    "home-electrician-elec": "home-electrician",
    "gypsum-tech": "gypsum-board",
    "gypsum-board-decor": "gypsum-board",
    "wall-grass": "artificial-grass",
    "artificial-grass-grdn": "artificial-grass",
    "automatic-irrigation": "modern-irrigation",
    "electric-panel-maintenance": "electrical-maintenance",
}

MEDIA_BY_PREFIX = (
    ("villa-cleaning", 2684),
    ("water-leak", 10618),
    ("home-cleaning", 2733),
)

FILLER_TOKENS = {"elec", "grdn", "decor", "tech"}
DISTRICT_TOKENS = {"east", "west", "north", "south"}


@dataclass
class PostRef:
    id: int
    title: str
    url: str
    slug: str
    words: int = 0
    notes: str = ""


@dataclass
class FixResult:
    ok: int = 0
    skipped: int = 0
    failed: int = 0
    planned: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def log() -> logging.Logger:
    return logging.getLogger("seo_apply")


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = val


def env(name: str, default: str = "") -> str:
    if name == "WP_USERNAME":
        return os.environ.get("WP_USERNAME") or os.environ.get("WP_USER") or default
    return os.environ.get(name, default)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


# ---------------------------------------------------------------------------
# HTML purge (Task 2) — pure functions, no network
# ---------------------------------------------------------------------------

def cleanup_after_purge(html: str) -> str:
    html = re.sub(r"أو عندما تريد\s*[.،,]?", "", html)
    html = re.sub(r"\s+([.،,])", r"\1", html)
    html = re.sub(r"([.،]){2,}", r"\1", html)
    html = re.sub(r"\s{2,}", " ", html)
    html = EMPTY_P_RE.sub("", html)
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html.strip()


def should_strip_peak(title: str) -> bool:
    return not bool(KEEP_PEAK_TITLE_RE.search(title or ""))


def should_strip_aqar(title: str) -> bool:
    if NON_PROPERTY_TITLE_RE.search(title or ""):
        return True
    if PROPERTY_TITLE_RE.search(title or ""):
        return False
    return True


def should_strip_villa_faq(title: str) -> bool:
    return bool(VILLA_FAQ_IRRELEVANT_RE.search(title or ""))


def purge_boilerplate(html: str, title: str) -> tuple[str, list[str]]:
    """Return (new_html, list of applied rule names)."""
    applied: list[str] = []
    out = html or ""
    if should_strip_peak(title) and PEAK_PHRASE_RE.search(out):
        out = PEAK_PHRASE_RE.sub("", out)
        applied.append("peak_season")
    if should_strip_aqar(title) and AQAR_PHRASE_RE.search(out):
        out = AQAR_PHRASE_RE.sub("", out)
        applied.append("aqar_price")
    if should_strip_villa_faq(title) and VILLA_FAQ_BLOCK_RE.search(out):
        out = VILLA_FAQ_BLOCK_RE.sub("", out)
        applied.append("villa_faq")
    if applied:
        out = cleanup_after_purge(out)
    return out, applied


# ---------------------------------------------------------------------------
# Cannibalization (Task 3) — slug families
# ---------------------------------------------------------------------------

def slug_from_url(url: str) -> str:
    path = urllib.parse.urlparse(url).path.rstrip("/")
    return path.split("/")[-1] if path else ""


def normalize_service_slug(slug: str) -> str:
    s = (slug or "").lower()
    s = DISTRICT_RE.sub("", s)
    s = CITY_SLUG_RE.sub("", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return CANNIBAL_ALIASES.get(s, s)


def is_true_cannibal_pair(slug_a: str, slug_b: str) -> bool:
    if not slug_a or not slug_b or slug_a == slug_b:
        return False
    return normalize_service_slug(slug_a) == normalize_service_slug(slug_b)


def keeper_rank(slug: str, words: int) -> tuple:
    tokens = slug.lower().split("-")
    district = sum(1 for t in tokens if t in DISTRICT_TOKENS)
    filler = sum(1 for t in tokens if t in FILLER_TOKENS)
    # Prefer a city-level slug over neighborhoods; prefer a non-center slug
    # when a shorter city slug exists (jeddah beats jeddah-center).
    center = 1 if "center" in tokens else 0
    return (district, filler, center, len(tokens), -int(words or 0), len(slug))


def pick_keeper(members: list[PostRef]) -> PostRef:
    return min(members, key=lambda p: keeper_rank(p.slug, p.words))


def uf_parent(n: int) -> list[int]:
    return list(range(n))


def uf_find(p: list[int], i: int) -> int:
    while p[i] != i:
        p[i] = p[p[i]]
        i = p[i]
    return i


def uf_union(p: list[int], a: int, b: int) -> None:
    ra, rb = uf_find(p, a), uf_find(p, b)
    if ra != rb:
        p[rb] = ra


# ---------------------------------------------------------------------------
# HTTP / WordPress / LLM
# ---------------------------------------------------------------------------

class HttpError(RuntimeError):
    def __init__(self, status: int, body: str, url: str):
        super().__init__(f"HTTP {status} {url}: {body[:300]}")
        self.status = status
        self.body = body
        self.url = url


class WpClient:
    def __init__(self, base: str, user: str, password: str, delay: float = 0.35):
        self.base = base.rstrip("/")
        self.delay = delay
        raw = f"{user}:{password}".encode("utf-8")
        self.auth = "Basic " + base64.b64encode(raw).decode("ascii")
        self._last = 0.0

    def _sleep(self) -> None:
        wait = self.delay - (time.time() - self._last)
        if wait > 0:
            time.sleep(wait)
        self._last = time.time()

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
        retries: int = 4,
    ) -> Any:
        q = f"?{urllib.parse.urlencode(query)}" if query else ""
        url = f"{self.base}{path}{q}"
        data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {
            "User-Agent": "rukn-seo-apply/1.0",
            "Accept": "application/json",
            "Authorization": self.auth,
        }
        if data is not None:
            headers["Content-Type"] = "application/json; charset=utf-8"
        last_err: Exception | None = None
        for attempt in range(retries):
            self._sleep()
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=90) as resp:
                    raw = resp.read().decode("utf-8")
                    return json.loads(raw) if raw else {}
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", errors="replace")
                if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    last_err = HttpError(e.code, body, url)
                    continue
                raise HttpError(e.code, body, url) from e
            except (urllib.error.URLError, TimeoutError) as e:
                last_err = e
                time.sleep(2 ** attempt)
        raise last_err or RuntimeError(f"request failed {url}")

    def get_post(self, post_id: int, context: str = "edit") -> dict[str, Any]:
        return self.request("GET", f"/wp-json/wp/v2/posts/{post_id}", query={"context": context})

    def list_posts(self, page: int, per_page: int = 50, context: str = "edit") -> tuple[list[dict], int]:
        q = {
            "page": page,
            "per_page": per_page,
            "status": "publish",
            "context": context,
        }
        # Need total pages from headers — wrap a header-aware call.
        self._sleep()
        url = f"{self.base}/wp-json/wp/v2/posts?{urllib.parse.urlencode(q)}"
        headers = {
            "User-Agent": "rukn-seo-apply/1.0",
            "Accept": "application/json",
            "Authorization": self.auth,
        }
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=90) as resp:
            total = int(resp.headers.get("X-WP-TotalPages") or 1)
            body = json.loads(resp.read().decode("utf-8"))
            return body, total

    def update_post(self, post_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        path = f"/wp-json/wp/v2/posts/{post_id}"
        try:
            return self.request("PUT", path, payload=payload)
        except HttpError as e:
            if e.status in (404, 405, 501):
                return self.request("POST", path, payload=payload)
            raise

    def get_media(self, media_id: int) -> dict[str, Any]:
        return self.request("GET", f"/wp-json/wp/v2/media/{media_id}")


def llm_complete(prompt: str, provider: str, api_key: str, model: str, delay: float) -> str:
    if not api_key:
        raise RuntimeError("LLM_API_KEY is missing")
    time.sleep(delay)
    provider = (provider or "gemini").lower()
    if provider == "openai":
        model = model or "gpt-4o-mini"
        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": model,
            "temperature": 0.4,
            "messages": [
                {
                    "role": "system",
                    "content": "You write Arabic service-page HTML for a Saudi home-services company.",
                },
                {"role": "user", "content": prompt},
            ],
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "rukn-seo-apply/1.0",
        }
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
        )
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]
    # Gemini
    model = model or "gemini-2.0-flash"
    qs = urllib.parse.urlencode({"key": api_key})
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?{qs}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 8192},
    }
    headers = {"Content-Type": "application/json", "User-Agent": "rukn-seo-apply/1.0"}
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    parts = data["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts)


def sanitize_llm_html(html: str, wa: str) -> str:
    text = MD_FENCE_RE.sub("", html or "").strip()
    text = EMOJI_RE.sub("", text)
    wa_href = f'href="https://wa.me/{wa}"'
    text = TEL_HREF_RE.sub(wa_href, text)
    text = text.replace("0568060309", wa)
    text = text.replace("+966000000000", wa)
    if "<" not in text:
        raise RuntimeError("LLM did not return HTML")
    if re.search(r"lorem ipsum", text, re.I):
        raise RuntimeError("LLM returned placeholder copy")
    return text


def intent_prompt(title: str, slug: str, notes: str, wa: str) -> str:
    return f"""أعد كتابة مقال خدمة لشركة «ركن التطور» في السعودية.

العنوان: {title}
الرابط/السلَج: {slug}
سبب عدم تطابق النية: {notes}

المتطلبات:
- HTML نظيف فقط (بدون markdown، بدون سياج ```).
- النبرة تسويقية مهنية عربية فصحى مبسّطة.
- المحتوى يطابق الخدمة في العنوان حرفياً. لا تتحدث عن تنظيف منازل أو رخام أو خشب أو كنب إذا كانت الخدمة شحن سيارات/أثاث أو دكتات مكيفات/غسيل مكيفات.
- لا إيموجي. استخدم أيقونات Font Awesome بهذا الشكل فقط: <i class="fa-solid fa-truck"></i> أو fa-snowflake أو fa-check أو fa-location-dot أو fa-box.
- هيكل: مقدمة، ثم H2/H3 (خطوات العمل، الأحياء، ما يشمله النطاق، أسئلة شائعة مطابقة للخدمة).
- 1100 إلى 1600 كلمة عربية.
- دعوة واتساب فقط على https://wa.me/{wa} — لا تستخدم tel: ولا أي رقم سعودي.
- لا تذكر الإمارات. الموقع سعودي.
- لا تضع H1 (القالب يرسم العنوان كـ H1).
"""


def featured_id_for_slug(slug: str, fallback: int) -> int:
    for prefix, mid in MEDIA_BY_PREFIX:
        if slug.startswith(prefix):
            return mid
    return fallback


def extract_content(item: dict[str, Any]) -> str:
    content = item.get("content") or {}
    raw = content.get("raw") or ""
    if raw.strip():
        return raw
    return content.get("rendered") or ""


def extract_title(item: dict[str, Any]) -> str:
    t = item.get("title")
    if isinstance(t, dict):
        return t.get("raw") or t.get("rendered") or ""
    return str(t or "")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_intent_targets() -> list[PostRef]:
    path = AUDIT_DIR / "intent-mismatch.csv"
    rows = read_csv_rows(path)
    out = []
    for r in rows:
        out.append(
            PostRef(
                id=int(r["id"]),
                title=r.get("title") or "",
                url=r.get("url") or "",
                slug=r.get("slug") or "",
                words=int(r.get("words") or 0),
                notes=r.get("notes") or "",
            )
        )
    return out


def load_image_targets() -> list[PostRef]:
    path = AUDIT_DIR / "errors-missing.csv"
    rows = read_csv_rows(path)
    out = []
    for r in rows:
        if "لا صور" not in (r.get("notes") or ""):
            continue
        out.append(
            PostRef(
                id=int(r["id"]),
                title=r.get("title") or "",
                url=r.get("url") or "",
                slug=r.get("slug") or "",
                words=int(r.get("words") or 0),
                notes=r.get("notes") or "",
            )
        )
    return out


def load_all_docs_index() -> dict[str, PostRef]:
    path = AUDIT_DIR / "all-docs.csv"
    idx: dict[str, PostRef] = {}
    for r in read_csv_rows(path):
        ref = PostRef(
            id=int(r["id"]),
            title=r.get("title") or "",
            url=r.get("url") or "",
            slug=r.get("slug") or "",
            words=int(r.get("words") or 0),
        )
        idx[ref.url.rstrip("/") + "/"] = ref
        idx[ref.url.rstrip("/")] = ref
        idx[ref.slug] = ref
    return idx


def load_cannibal_clusters(index: dict[str, PostRef]) -> list[list[PostRef]]:
    path = AUDIT_DIR / "similar-pairs.csv"
    pairs: list[tuple[PostRef, PostRef]] = []
    skipped_template = 0
    for r in read_csv_rows(path):
        if "داخل نفس المدينة" not in (r.get("notes") or ""):
            continue
        slug_a, slug_b = slug_from_url(r["url_a"]), slug_from_url(r["url_b"])
        if not is_true_cannibal_pair(slug_a, slug_b):
            skipped_template += 1
            continue
        a = index.get(r["url_a"]) or index.get(r["url_a"].rstrip("/"))
        b = index.get(r["url_b"]) or index.get(r["url_b"].rstrip("/"))
        if not a or not b:
            continue
        a.words = int(r.get("words_a") or a.words)
        b.words = int(r.get("words_b") or b.words)
        pairs.append((a, b))
    log().info("true same-city cannibal pairs: %s (skipped template-similar: %s)", len(pairs), skipped_template)
    urls: list[str] = []
    refs: dict[str, PostRef] = {}
    for a, b in pairs:
        for p in (a, b):
            if p.url not in refs:
                refs[p.url] = p
                urls.append(p.url)
    pos = {u: i for i, u in enumerate(urls)}
    parent = uf_parent(len(urls))
    for a, b in pairs:
        uf_union(parent, pos[a.url], pos[b.url])
    groups: dict[int, list[PostRef]] = defaultdict(list)
    for u in urls:
        groups[uf_find(parent, pos[u])].append(refs[u])
    clusters = [g for g in groups.values() if len(g) >= 2]
    clusters.sort(key=lambda g: -len(g))
    return clusters


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_checkpoint(path: Path) -> set[int]:
    if not path.is_file():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    return set(int(x) for x in data.get("done_ids", []))


def save_checkpoint(path: Path, done: Iterable[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"done_ids": sorted(done)}, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def task_intent(wp: WpClient | None, args: argparse.Namespace, run_log: Path) -> FixResult:
    result = FixResult()
    targets = load_intent_targets()
    if args.limit:
        targets = targets[: args.limit]
    ck = CHECKPOINT_DIR / "intent.json"
    done = load_checkpoint(ck)
    wa = env("WHATSAPP_NUMBER", DEFAULT_WA)
    provider = env("LLM_PROVIDER", "gemini")
    api_key = env("LLM_API_KEY")
    model = env("LLM_MODEL")
    for post in targets:
        if post.id in done:
            result.skipped += 1
            continue
        plan = {
            "task": "intent",
            "id": post.id,
            "title": post.title,
            "url": post.url,
            "action": "llm_rewrite_put",
            "notes": post.notes,
        }
        result.planned.append(plan)
        append_jsonl(run_log, {"event": "plan", **plan})
        if not args.apply:
            result.ok += 1
            continue
        assert wp is not None
        try:
            prompt = intent_prompt(post.title, post.slug, post.notes, wa)
            html = llm_complete(prompt, provider, api_key, model, args.llm_delay)
            html = sanitize_llm_html(html, wa)
            wp.update_post(post.id, {"content": html, "status": "publish"})
            done.add(post.id)
            save_checkpoint(ck, done)
            result.ok += 1
            append_jsonl(run_log, {"event": "updated", "task": "intent", "id": post.id})
            log().info("intent rewritten id=%s %s", post.id, post.slug)
        except Exception as e:
            result.failed += 1
            result.errors.append(f"intent {post.id}: {e}")
            log().exception("intent failed id=%s", post.id)
    return result


def task_boilerplate(wp: WpClient | None, args: argparse.Namespace, run_log: Path) -> FixResult:
    result = FixResult()
    ck = CHECKPOINT_DIR / "boilerplate.json"
    done = load_checkpoint(ck)
    intent_ids = {p.id for p in load_intent_targets()}
    processed = 0
    if not args.apply:
        # Dry-run uses the public cache/audit CSV rather than 1718 authenticated fetches.
        path = AUDIT_DIR / "boilerplate-overuse.csv"
        rows = read_csv_rows(path)
        if args.limit:
            rows = rows[: args.limit]
        for r in rows:
            pid = int(r["id"])
            if pid in intent_ids:
                result.skipped += 1
                continue
            title = r.get("title") or ""
            # Approximate: we do not have raw HTML here; record which rules would fire by title.
            rules = []
            if should_strip_peak(title):
                rules.append("peak_season")
            if should_strip_aqar(title):
                rules.append("aqar_price")
            if should_strip_villa_faq(title):
                rules.append("villa_faq")
            plan = {"task": "boilerplate", "id": pid, "title": title, "url": r.get("url"), "rules": rules}
            result.planned.append(plan)
            result.ok += 1
        append_jsonl(run_log, {"event": "boilerplate_dry_run", "count": result.ok})
        return result

    assert wp is not None
    page = 1
    while True:
        try:
            items, total_pages = wp.list_posts(page=page, per_page=50, context="edit")
        except HttpError as e:
            result.failed += 1
            result.errors.append(f"list page {page}: {e}")
            break
        if not items:
            break
        for item in items:
            pid = int(item.get("id") or 0)
            if pid in done or pid in intent_ids:
                result.skipped += 1
                continue
            title = extract_title(item)
            html = extract_content(item)
            new_html, applied = purge_boilerplate(html, title)
            if not applied or new_html == html:
                result.skipped += 1
                continue
            processed += 1
            if args.limit and processed > args.limit:
                return result
            try:
                wp.update_post(pid, {"content": new_html})
                done.add(pid)
                save_checkpoint(ck, done)
                result.ok += 1
                append_jsonl(
                    run_log,
                    {"event": "updated", "task": "boilerplate", "id": pid, "rules": applied, "title": title},
                )
                log().info("boilerplate id=%s rules=%s", pid, ",".join(applied))
            except Exception as e:
                result.failed += 1
                result.errors.append(f"boilerplate {pid}: {e}")
                log().exception("boilerplate failed id=%s", pid)
        if page >= total_pages:
            break
        page += 1
    return result


def task_cannibal(wp: WpClient | None, args: argparse.Namespace, run_log: Path) -> FixResult:
    result = FixResult()
    index = load_all_docs_index()
    clusters = load_cannibal_clusters(index)
    redirects: list[dict[str, Any]] = []
    ck = CHECKPOINT_DIR / "cannibal.json"
    done = load_checkpoint(ck)
    drafted = 0
    for cluster in clusters:
        if args.limit and drafted >= args.limit:
            break
        keeper = pick_keeper(cluster)
        for loser in cluster:
            if loser.id == keeper.id:
                continue
            if args.limit and drafted >= args.limit:
                break
            old_path = urllib.parse.urlparse(loser.url).path
            new_path = urllib.parse.urlparse(keeper.url).path
            row = {
                "source": old_path,
                "destination": keeper.url,
                "type": "301",
                "status": "active",
                "id_from": loser.id,
                "id_to": keeper.id,
                "from_title": loser.title,
                "to_title": keeper.title,
                "from_slug": loser.slug,
                "to_slug": keeper.slug,
                "reason": f"intra-city cannibal; keep {keeper.slug}",
            }
            redirects.append(row)
            result.planned.append({"task": "cannibal_draft", **row})
            drafted += 1
            append_jsonl(run_log, {"event": "plan", "task": "cannibal", **row})
            if not args.apply:
                result.ok += 1
                continue
            if loser.id in done:
                result.skipped += 1
                continue
            assert wp is not None
            try:
                wp.update_post(loser.id, {"status": "draft"})
                done.add(loser.id)
                save_checkpoint(ck, done)
                result.ok += 1
                log().info("drafted id=%s -> keep %s", loser.id, keeper.slug)
            except Exception as e:
                result.failed += 1
                result.errors.append(f"cannibal {loser.id}: {e}")
                log().exception("draft failed id=%s", loser.id)
    out_csv = FIX_DIR / "redirects.csv"
    write_csv(
        out_csv,
        redirects,
        [
            "source",
            "destination",
            "type",
            "status",
            "id_from",
            "id_to",
            "from_title",
            "to_title",
            "from_slug",
            "to_slug",
            "reason",
        ],
    )
    write_csv(
        FIX_DIR / "cannibal-plan.csv",
        [
            {
                "keeper_id": pick_keeper(c).id,
                "keeper_slug": pick_keeper(c).slug,
                "keeper_url": pick_keeper(c).url,
                "cluster_size": len(c),
                "draft_slugs": " ".join(p.slug for p in c if p.id != pick_keeper(c).id),
            }
            for c in clusters
        ],
        ["keeper_id", "keeper_slug", "keeper_url", "cluster_size", "draft_slugs"],
    )
    log().info("wrote %s (%s redirects)", out_csv, len(redirects))
    return result


def inject_featured_image(html: str, src: str, alt: str, media_id: int) -> str:
    if re.search(r"<img\b", html or "", re.I):
        return html
    figure = (
        f'<figure class="wp-block-image"><img src="{src}" alt="{alt}" '
        f'class="wp-image-{media_id}" /></figure>\n'
    )
    if re.search(r"<h[2-3]\b", html or "", re.I):
        return re.sub(r"(<h[2-3]\b[^>]*>)", figure + r"\1", html, count=1, flags=re.I)
    return figure + (html or "")


def task_images(wp: WpClient | None, args: argparse.Namespace, run_log: Path) -> FixResult:
    result = FixResult()
    targets = load_image_targets()
    fallback = int(env("FEATURED_MEDIA_ID") or DEFAULT_MEDIA)
    ck = CHECKPOINT_DIR / "images.json"
    done = load_checkpoint(ck)
    for post in targets:
        media_id = featured_id_for_slug(post.slug, fallback)
        plan = {
            "task": "images",
            "id": post.id,
            "title": post.title,
            "url": post.url,
            "featured_media": media_id,
            "also_inject_inline_img": True,
        }
        result.planned.append(plan)
        append_jsonl(run_log, {"event": "plan", **plan})
        if not args.apply:
            result.ok += 1
            continue
        if post.id in done:
            result.skipped += 1
            continue
        assert wp is not None
        try:
            item = wp.get_post(post.id, context="edit")
            current_fm = int(item.get("featured_media") or 0)
            use_id = current_fm or media_id
            src = ""
            try:
                media = wp.get_media(use_id)
                src = media.get("source_url") or (media.get("guid") or {}).get("rendered") or ""
            except Exception as e:
                log().warning("media %s fetch failed: %s", use_id, e)
            html = extract_content(item)
            payload: dict[str, Any] = {}
            if not current_fm:
                payload["featured_media"] = use_id
            if src:
                new_html = inject_featured_image(html, src, post.title, use_id)
                if new_html != html:
                    payload["content"] = new_html
            if not payload:
                result.skipped += 1
                continue
            wp.update_post(post.id, payload)
            done.add(post.id)
            save_checkpoint(ck, done)
            result.ok += 1
            append_jsonl(run_log, {"event": "updated", "task": "images", "id": post.id, "payload_keys": list(payload)})
        except Exception as e:
            result.failed += 1
            result.errors.append(f"images {post.id}: {e}")
            log().exception("images failed id=%s", post.id)
    return result


# ---------------------------------------------------------------------------
# Self-test (offline)
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    painting = "شركة دهان شقق بالدمام"
    shipping = "شركة شحن سيارات بجدة"
    moving = "شركة نقل عفش بالرياض"
    ducts = "شركة تنظيف وصيانة دكتات المكيفات بالدمام"
    sample = """
<h2>متى أحتاج دهان شقق؟</h2>
<p>عندما يظهر بهتان. أو عندما تريد تجهيزاً مرتباً قبل انتقال أو موسم ذروة في الدمام.</p>
<h3>كم التكلفة؟</h3>
<p>لا نضع رقماً ثابتاً لا يمثّل عقارك. التكلفة تتأثر بالمساحة.</p>
<h3>هل الخدمة للشقق والفلل في الدمام؟</h3>
<p>نعم. نضبط الخطة حسب التشطيب وسهولة الوصول في شقق وفلل الدمام.</p>
"""
    html, rules = purge_boilerplate(sample, painting)
    assert "peak_season" in rules, rules
    assert "تجهيزاً مرتباً" not in html
    assert "villa_faq" not in rules
    assert "هل الخدمة للشقق والفلل" in html
    html2, rules2 = purge_boilerplate(sample, moving)
    assert "peak_season" not in rules2
    html3, rules3 = purge_boilerplate(sample, shipping)
    assert "peak_season" not in rules3
    assert "aqar_price" in rules3
    assert "villa_faq" in rules3
    assert "هل الخدمة للشقق والفلل" not in html3
    html4, rules4 = purge_boilerplate(sample, ducts)
    assert "villa_faq" in rules4
    assert "peak_season" in rules4

    assert is_true_cannibal_pair("home-plumber-riyadh", "home-plumber-elec-riyadh")
    assert is_true_cannibal_pair("water-leak-detection-east-jeddah", "water-leak-detection-jeddah")
    assert is_true_cannibal_pair("gypsum-board-jeddah", "gypsum-tech-jeddah")
    assert not is_true_cannibal_pair("car-shipping-jeddah", "wall-grass-jeddah")
    assert not is_true_cannibal_pair("mattress-cleaning-abha", "wall-grass-abha")
    k = pick_keeper(
        [
            PostRef(1, "شركة سباك", "https://x/home-plumber-elec-riyadh/", "home-plumber-elec-riyadh", 2000),
            PostRef(2, "سباك", "https://x/home-plumber-riyadh/", "home-plumber-riyadh", 1800),
        ]
    )
    assert k.slug == "home-plumber-riyadh", k.slug
    k2 = pick_keeper(
        [
            PostRef(1, "شرق", "https://x/water-leak-detection-east-jeddah/", "water-leak-detection-east-jeddah", 3000),
            PostRef(2, "جدة", "https://x/water-leak-detection-jeddah/", "water-leak-detection-jeddah", 2100),
        ]
    )
    assert k2.slug == "water-leak-detection-jeddah", k2.slug
    k3 = pick_keeper(
        [
            PostRef(1, "جنوب", "https://x/a/", "water-leak-detection-south-riyadh", 3000),
            PostRef(2, "وسط", "https://x/b/", "water-leak-detection-riyadh-center", 2100),
        ]
    )
    assert k3.slug == "water-leak-detection-riyadh-center", k3.slug

    cleaned = sanitize_llm_html(
        "```html\n<p>مرحبا <i class=\"fa-solid fa-check\"></i> 😀</p><a href=\"tel:0568060309\">x</a>\n```",
        "971586634710",
    )
    assert "😀" not in cleaned
    assert "wa.me/971586634710" in cleaned
    assert "```" not in cleaned

    img = inject_featured_image("<h2>عنوان</h2><p>نص</p>", "https://cdn.example/a.jpg", "alt", 2684)
    assert "<img" in img and img.index("<img") < img.index("<h2")

    # Audit CSVs present
    assert (AUDIT_DIR / "intent-mismatch.csv").is_file()
    n_intent = len(load_intent_targets())
    assert n_intent == 38, n_intent
    n_img = len(load_image_targets())
    assert n_img == 3, n_img
    clusters = load_cannibal_clusters(load_all_docs_index())
    draft_n = sum(len(c) - 1 for c in clusters)
    assert draft_n > 0
    print(
        json.dumps(
            {
                "self_test": "ok",
                "intent_targets": n_intent,
                "image_targets": n_img,
                "cannibal_clusters": len(clusters),
                "planned_drafts": draft_n,
            },
            ensure_ascii=False,
        )
    )
    return 0


def parse_tasks(raw: str) -> list[str]:
    raw = (raw or "all").strip().lower()
    if raw == "all":
        return ["intent", "boilerplate", "cannibal", "images"]
    allowed = {"intent", "boilerplate", "cannibal", "images"}
    tasks = [t.strip() for t in raw.split(",") if t.strip()]
    bad = [t for t in tasks if t not in allowed]
    if bad:
        raise SystemExit(f"unknown tasks: {bad}")
    return tasks


def setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        stream=sys.stderr,
    )


def main(argv: list[str] | None = None) -> int:
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser(description="Apply Rukn SA SEO content fixes via WP REST")
    parser.add_argument("--self-test", action="store_true", help="Run offline unit checks and exit")
    parser.add_argument("--tasks", default="all", help="all or comma list: intent,boilerplate,cannibal,images")
    parser.add_argument("--apply", action="store_true", help="Write to WordPress (default: dry-run)")
    parser.add_argument("--yes", action="store_true", help="Required with --apply to confirm writes")
    parser.add_argument("--limit", type=int, default=0, help="Cap items per task (testing)")
    parser.add_argument("--wp-delay", dest="wp_delay", type=float, default=0.35)
    parser.add_argument("--llm-delay", dest="llm_delay", type=float, default=1.2)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)
    setup_logging(args.verbose)
    FIX_DIR.mkdir(parents=True, exist_ok=True)

    if args.self_test:
        return run_self_test()

    if args.apply and not args.yes:
        log().error("Refusing to write: pass --apply --yes after you approve the dry-run plan.")
        return 2

    tasks = parse_tasks(args.tasks)
    run_id = utc_now()
    run_log = LOG_DIR / f"run-{run_id}.jsonl"
    summary = {
        "run_id": run_id,
        "apply": bool(args.apply),
        "tasks": tasks,
        "started": datetime.now(timezone.utc).isoformat(),
    }
    append_jsonl(run_log, {"event": "start", **summary})

    wp: WpClient | None = None
    if args.apply:
        user = env("WP_USERNAME")
        password = env("WP_APP_PASSWORD")
        base = env("WP_BASE_URL", DEFAULT_BASE)
        if not user or not password:
            log().error("WP_USERNAME / WP_APP_PASSWORD missing in .env")
            return 2
        wp = WpClient(base, user, password, delay=args.wp_delay)

    results: dict[str, FixResult] = {}
    dispatch = {
        "intent": task_intent,
        "boilerplate": task_boilerplate,
        "cannibal": task_cannibal,
        "images": task_images,
    }
    rc = 0
    for name in tasks:
        log().info("=== task %s apply=%s ===", name, args.apply)
        results[name] = dispatch[name](wp, args, run_log)
        if results[name].failed:
            rc = 1

    report = {
        "run_id": run_id,
        "apply": args.apply,
        "tasks": {
            k: {"ok": v.ok, "skipped": v.skipped, "failed": v.failed, "planned": len(v.planned), "errors": v.errors[:20]}
            for k, v in results.items()
        },
        "redirects_csv": str(FIX_DIR / "redirects.csv"),
        "log": str(run_log),
    }
    report_path = FIX_DIR / f"last-run.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    log().info("done %s", json.dumps(report, ensure_ascii=False))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return rc


if __name__ == "__main__":
    sys.exit(main())
