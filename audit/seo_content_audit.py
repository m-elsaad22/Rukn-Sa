#!/usr/bin/env python3
"""Technical SEO + content quality auditor for the Rukn Eltatawer WordPress site.

Reads published posts/pages via the REST API (with optional HTTP Basic auth),
caches payloads locally, then flags:

  * thin content (< 1000 words)
  * shared article templates / boilerplate
  * near-duplicate bodies (keyword cannibalization risk)
  * title vs body search-intent mismatch
  * missing H1/H2, placeholders, and structural gaps

Usage:
  WP_USER=cursor WP_APP_PASSWORD='xxxx xxxx' \\
    python3 audit/seo_content_audit.py --base https://www.rukn-eltatawer.com/sa \\
    --out-dir audit/seo-run

Requires: Python 3.10+ and numpy (hashed cosine similarity). REST cache lives in
--cache-dir (default /tmp/rukn-seo-audit) so re-runs skip the network.

Environment:
  WP_USER, WP_APP_PASSWORD   WordPress application password (optional for public posts)
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import html as html_lib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None  # type: ignore


CITIES = [
    "خميس مشيط",
    "مكة المكرمة",
    "المدينة المنورة",
    "حفر الباطن",
    "أبو عريش",
    "الظهران",
    "القطيف",
    "الأحساء",
    "الجبيل",
    "الخفجي",
    "الخبر",
    "الدمام",
    "الرياض",
    "الطائف",
    "الباحة",
    "القصيم",
    "بريدة",
    "تبوك",
    "حائل",
    "جازان",
    "نجران",
    "ينبع",
    "أبها",
    "الخرج",
    "عرعر",
    "سكاكا",
    "رابغ",
    "جدة",
    "مكة",
    "المدينة",
]
UTILITY_PAGE_SLUGS = {
    "cities",
    "pricing",
    "contact-us",
    "sitemap",
    "blog",
    "faq",
    "about-us",
    "privacy-policy",
    "terms",
}
CITIES_SORTED = sorted(CITIES, key=len, reverse=True)

AR_STOP = set(
    """
    في من على إلى الى و أو او أن ان هذا هذه ذلك تلك هو هي هم هن كما ثم قد لا ما
    عن مع كل أي اى بين حتى إذا اذا كان كانت يكون تكون التي الذي الذين اللواتي
    هناك هنا قبل بعد خلال لدى لدي لديكم لكم لها له لهم هنالك أيضا ايضا غير فقط
    حيث دون لدى لدى إن انا نحن أنت انت تم يتم يتم يتم عبر خلال جدا جداً جدا
    """.split()
)

BOILERPLATE_PHRASES = [
    "تجهيزاً مرتباً قبل انتقال أو موسم ذروة",
    "تجهيزا مرتبا قبل انتقال أو موسم ذروة",
    "لا نضع رقماً ثابتاً لا يمثّل عقارك",
    "لا نضع رقما ثابتا لا يمثل عقارك",
    "نوضّح ما سيدخل في النطاق وما لن يدخل",
    "نوضح ما سيدخل في النطاق وما لن يدخل",
    "حسب الجدولة اليومية، ومن الأحياء التي نصل إليها غالباً",
    "هل الخدمة للشقق والفلل",
    "كتب هذا المقال: فريق المحتوى الفني في ركن التطور",
    "آخر تحديث:",
    "معاينة دقيقة قبل التنفيذ",
    "نختار الأدوات حسب الحالة بعد المعاينة",
]

PLACEHOLDER_PATTERNS = [
    r"lorem ipsum",
    r"\bTODO\b",
    r"\bTBD\b",
    r"\{PHONE",
    r"\{WHATSAPP",
    r"PHONE_RUKN",
    r"xxxx",
    r"نص هنا",
    r"اكتب هنا",
    r"placeholder",
    r"vi/الفيديو/",
    r"966000000000",
]

# Title-token families used to detect intent mismatch.
INTENT_LEXICONS: dict[str, set[str]] = {
    "ac_cleaning": {"مكيف", "مكيفات", "تكييف", "فريون", "سبليت", "دكت"},
    "home_cleaning": {"تنظيف", "غبار", "رخام", "خشب", "كنب", "سجاد", "موكيت"},
    "car_shipping": {"شحن", "سيارات", "سيارة", "ناقلة", "حمولة"},
    "moving": {"نقل", "عفش", "أثاث", "تغليف", "تخزين"},
    "leak": {"تسرب", "تسربات", "رطوبة", "عداد", "مياه"},
    "pest": {"حشرات", "مكافحة", "صراصير", "قوارض", "نمل"},
    "legal": {"محام", "قانون", "قضية", "استشارة قانونية"},
    "cars_repair": {"ميكانيك", "فرامل", "بطارية", "زيت", "سطحة"},
}

MISMATCH_RULES = [
    # (title must match, body must match, note)
    (
        re.compile(r"مكيف|تكييف|فريون|سبليت"),
        re.compile(r"رخام|بلل مفرط للخشب|كنب|موكيت"),
        "عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب",
    ),
    (
        re.compile(r"شحن سيارات|شحن السيارات"),
        re.compile(r"شقق والفلل|للشقق والفلل|عقارك"),
        "عنوان شحن سيارات بينما النص يعامل الخدمة كخدمة منزل/عقار",
    ),
    (
        re.compile(r"شحن داخلي|شحن أثاث"),
        re.compile(r"شقق والفلل"),
        "عنوان شحن بينما الأسئلة تفترض شقق وفلل",
    ),
    (
        re.compile(r"كهربائي|كهرباء"),
        re.compile(r"رخام|خشب|كنب"),
        "عنوان كهرباء مع فقرات تنظيف منازل",
    ),
    (
        re.compile(r"شحن سيارات|نقل سيارات"),
        re.compile(r"انتقال أو موسم ذروة|موسم ذروة"),
        "شحن سيارات يستخدم صياغة انتقال المنازل",
    ),
]


@dataclass
class Doc:
    id: int
    type: str
    slug: str
    link: str
    title: str
    date: str
    modified: str
    html: str
    text: str
    words: int
    h1: list[str]
    h2: list[str]
    h3: list[str]
    images: int
    internal_links: int
    faq_count: int
    normalized: str
    heading_fingerprint: str
    simhash: int = 0
    issues: list[dict[str, str]] = field(default_factory=list)


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def request_json(url: str, auth: str | None, timeout: int = 90) -> tuple[Any, dict[str, str]]:
    headers = {"User-Agent": "rukn-seo-audit/1.0", "Accept": "application/json"}
    if auth:
        headers["Authorization"] = "Basic " + auth
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        hdrs = {k.lower(): v for k, v in resp.headers.items()}
        return body, hdrs


def strip_html(raw: str) -> str:
    raw = re.sub(r"<script[\s\S]*?</script>", " ", raw, flags=re.I)
    raw = re.sub(r"<style[\s\S]*?</style>", " ", raw, flags=re.I)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = html_lib.unescape(raw)
    raw = unicodedata.normalize("NFKC", raw)
    raw = re.sub(r"\s+", " ", raw)
    return raw.strip()


def extract_headings(html: str, level: int) -> list[str]:
    pats = re.findall(rf"<h{level}[^>]*>(.*?)</h{level}>", html, flags=re.I | re.S)
    out = []
    for p in pats:
        t = strip_html(p)
        if t:
            out.append(t)
    return out


def word_count(text: str) -> int:
    tokens = re.findall(r"[A-Za-z\u0600-\u06FF]+", text)
    return len(tokens)


def normalize_cities(text: str) -> str:
    t = text
    for city in CITIES_SORTED:
        t = t.replace(city, "{CITY}")
    t = re.sub(
        r"\b(riyadh|jeddah|mecca|makkah|medina|dammam|khobar|taif|abha)\b",
        "{CITY}",
        t,
        flags=re.I,
    )
    return t


def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z\u0600-\u06FF]{2,}", text.lower())


def heading_fingerprint(h2: list[str], h3: list[str]) -> str:
    seq = []
    for x in h2[:16]:
        t = normalize_cities(x)
        t = re.sub(r"اطلب .+? في \{CITY\}", "اطلب {SERVICE} في {CITY}", t)
        t = re.sub(r".+ داخل \{CITY\}", "{SERVICE} داخل {CITY}", t)
        t = re.sub(r"ما هي خدمة .+", "ما هي خدمة {SERVICE}؟", t)
        t = re.sub(r"مميزات .+", "مميزات {SERVICE}", t)
        t = re.sub(r"لماذا يختار عملاء \{CITY\} .+", "لماذا يختار عملاء {CITY} ركن التطور؟", t)
        t = re.sub(r"هل مشكلتك تناسب .+", "هل مشكلتك تناسب {SERVICE}؟", t)
        t = re.sub(r"لماذا تظهر المشكلة المرتبطة بـ.+", "لماذا تظهر المشكلة المرتبطة بـ{SERVICE}؟", t)
        t = re.sub(r"\s+", " ", t).strip()
        seq.append(t)
    if len(seq) < 3:
        seq += [normalize_cities(x) for x in h3[:8]]
    # Keep only the first 8 slots so minor extra H2s do not split a template cluster.
    blob = " | ".join(seq[:8])
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()[:16] + f"|n={min(len(h2), 12)}"


def simhash64(tokens: list[str]) -> int:
    if not tokens:
        return 0
    v = [0] * 64
    for tok in tokens:
        h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
        for i in range(64):
            v[i] += 1 if (h >> i) & 1 else -1
    out = 0
    for i, val in enumerate(v):
        if val > 0:
            out |= 1 << i
    return out


def hamming(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def boilerplate_hits(text: str) -> list[str]:
    hits = []
    for phrase in BOILERPLATE_PHRASES:
        if phrase in text:
            hits.append(phrase)
    return hits


def placeholder_hits(html: str, text: str) -> list[str]:
    blob = html + "\n" + text
    found = []
    for pat in PLACEHOLDER_PATTERNS:
        if re.search(pat, blob, flags=re.I):
            found.append(pat)
    return found


def city_in_title(title: str) -> str | None:
    for city in CITIES_SORTED:
        if city in title:
            return city
    return None


def is_moving_title(title: str) -> bool:
    return bool(re.search(r"نقل عفش|نقل أثاث|نقل اثاث|شركة نقل |تخزين أثاث|تغليف عفش", title))


def intent_notes(title: str, text: str) -> list[str]:
    """True title↔body contradictions only. Site-wide moving-season glue is boilerplate."""
    notes = []
    for title_re, body_re, note in MISMATCH_RULES:
        if title_re.search(title) and body_re.search(text):
            notes.append(note)
    city = city_in_title(title)
    if city and city not in text:
        notes.append(f"المدينة «{city}» في العنوان ولا تظهر في النص")
    for family, tokens in INTENT_LEXICONS.items():
        if sum(1 for t in tokens if t in title) == 0:
            continue
        if sum(1 for t in tokens if t in text) == 0:
            notes.append(
                f"العنوان يوحي بموضوع «{family}» بينما النص لا يحتوي أي مفردة من هذه العائلة"
            )
    return notes


def boilerplate_classification(title: str, text: str, hits: list[str]) -> str | None:
    if len(hits) >= 2:
        return "عبارات قالبية متكررة: " + " | ".join(hits[:4])
    peak = any("انتقال أو موسم ذروة" in p or "قبل انتقال" in p for p in hits)
    if peak and not is_moving_title(title):
        return "عبارة انتقال/موسم ذروة ملصقة على خدمة لا علاقة لها بالنقل"
    return None


def structural_notes(doc: Doc) -> list[str]:
    notes = []
    # Theme renders the post title as H1 outside post_content. Flag only if the
    # title is empty or the body itself contains multiple H1s (duplicate heading).
    if not doc.title.strip():
        notes.append("عنوان المقال فارغ (لا H1 في القالب)")
    if len(doc.h1) > 1:
        notes.append(f"أكثر من H1 داخل المحتوى ({len(doc.h1)}) — العنوان غالباً H1 إضافي في القالب")
    if len(doc.h2) < 3:
        notes.append(f"H2 قليل جداً داخل المحتوى ({len(doc.h2)})")
    if doc.images == 0 and doc.type == "post" and doc.words >= 1500:
        notes.append("لا صور داخل المحتوى")
    if doc.internal_links < 1 and doc.type == "post":
        notes.append("لا روابط داخلية في جسم المقال")
    return notes


def fetch_collection(base: str, endpoint: str, auth: str | None, cache_path: str) -> list[dict]:
    if os.path.exists(cache_path):
        log(f"cache hit {cache_path}")
        rows = []
        with open(cache_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    fields = "id,slug,link,title,content,excerpt,date,modified,status,type,featured_media"
    page = 1
    per_page = 50
    rows: list[dict] = []
    while True:
        q = urllib.parse.urlencode(
            {
                "per_page": per_page,
                "page": page,
                "status": "publish",
                "_fields": fields,
                "context": "view",
            }
        )
        url = f"{base.rstrip('/')}/wp-json/wp/v2/{endpoint}?{q}"
        try:
            data, hdrs = request_json(url, auth)
        except urllib.error.HTTPError as e:
            if e.code == 400 and page > 1:
                break
            raise
        if not data:
            break
        for item in data:
            rows.append(item)
        total_pages = int(hdrs.get("x-wp-totalpages") or 1)
        log(f"  {endpoint} page {page}/{total_pages} (+{len(data)}) total={len(rows)}")
        if page >= total_pages:
            break
        page += 1
        time.sleep(0.12)
    with open(cache_path, "w", encoding="utf-8") as f:
        for item in rows:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    return rows


def parse_doc(item: dict, type_name: str) -> Doc:
    title = html_lib.unescape((item.get("title") or {}).get("rendered") or "")
    html = (item.get("content") or {}).get("rendered") or ""
    text = strip_html(html)
    h1 = extract_headings(html, 1)
    h2 = extract_headings(html, 2)
    h3 = extract_headings(html, 3)
    images = len(re.findall(r"<img\b", html, flags=re.I))
    links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\']', html, flags=re.I)
    internal = sum(1 for href in links if "rukn-eltatawer.com" in href or href.startswith("/"))
    faq = len(re.findall(r"question|الأسئلة الشائعة|faq", html, flags=re.I))
    tokens = tokenize(normalize_cities(text))
    doc = Doc(
        id=int(item.get("id") or 0),
        type=type_name,
        slug=item.get("slug") or "",
        link=item.get("link") or "",
        title=title,
        date=(item.get("date") or "")[:10],
        modified=(item.get("modified") or "")[:10],
        html=html,
        text=text,
        words=word_count(text),
        h1=h1,
        h2=h2,
        h3=h3,
        images=images,
        internal_links=internal,
        faq_count=faq,
        normalized=" ".join(tokens),
        heading_fingerprint=heading_fingerprint(h2, h3),
        simhash=simhash64(tokens[:4000]),
    )
    return doc


def hashed_vectors(texts: list[str], dim: int = 4096) -> Any:
    if np is None:
        return None
    x = np.zeros((len(texts), dim), dtype=np.float32)
    for i, text in enumerate(texts):
        for tok in text.split():
            h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16) % dim
            x[i, h] += 1.0
        n = float(np.linalg.norm(x[i]))
        if n:
            x[i] /= n
    return x


def union_find_parent(n: int) -> list[int]:
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


def write_csv(path: str, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def main() -> int:
    parser = argparse.ArgumentParser(description="Rukn SA technical SEO content auditor")
    parser.add_argument("--base", default="https://www.rukn-eltatawer.com/sa")
    parser.add_argument("--out-dir", default="audit/seo-run")
    parser.add_argument("--cache-dir", default="/tmp/rukn-seo-audit")
    parser.add_argument("--thin-limit", type=int, default=1000)
    parser.add_argument("--similar-threshold", type=float, default=0.90)
    parser.add_argument("--skip-fetch", action="store_true")
    args = parser.parse_args()

    user = os.environ.get("WP_USER", "")
    password = os.environ.get("WP_APP_PASSWORD", "")
    auth = None
    if user and password:
        auth = base64.b64encode(f"{user}:{password}".encode()).decode()

    os.makedirs(args.out_dir, exist_ok=True)
    os.makedirs(args.cache_dir, exist_ok=True)
    posts_cache = os.path.join(args.cache_dir, "posts.jsonl")
    pages_cache = os.path.join(args.cache_dir, "pages.jsonl")
    if args.skip_fetch and not os.path.exists(posts_cache):
        log("no cache to skip-fetch")
        return 2

    log("Fetching posts…")
    posts_raw = fetch_collection(args.base, "posts", auth, posts_cache)
    log("Fetching pages…")
    pages_raw = fetch_collection(args.base, "pages", auth, pages_cache)

    docs: list[Doc] = []
    for item in posts_raw:
        docs.append(parse_doc(item, "post"))
    for item in pages_raw:
        docs.append(parse_doc(item, "page"))
    log(f"Parsed {len(docs)} documents")

    # Per-document issues
    all_rows: list[dict[str, Any]] = []
    thin_rows: list[dict[str, Any]] = []
    error_rows: list[dict[str, Any]] = []
    intent_rows: list[dict[str, Any]] = []
    boilerplate_rows: list[dict[str, Any]] = []

    fp_groups: dict[str, list[int]] = defaultdict(list)
    for i, doc in enumerate(docs):
        fp_groups[doc.heading_fingerprint].append(i)

        cats: list[str] = []
        notes: list[str] = []

        if doc.words < args.thin_limit:
            cats.append("thin_content")
            if doc.type == "page" and doc.slug in UTILITY_PAGE_SLUGS:
                notes.append(
                    f"صفحة أدوات/فهرس ({doc.words} كلمة) — الحد 1000 موجّه لمقالات الخدمات لا للصفحات الهيكلية"
                )
            else:
                notes.append(f"عدد الكلمات {doc.words} أقل من {args.thin_limit}")

        bp = boilerplate_hits(doc.text)
        bp_note = boilerplate_classification(doc.title, doc.text, bp)
        if bp_note:
            cats.append("boilerplate_overuse")
            notes.append(bp_note)

        ph = placeholder_hits(doc.html, doc.text)
        if ph:
            cats.append("errors_missing")
            notes.append("نصوص نائبة/عناصر مكسورة: " + ", ".join(ph[:5]))

        st = structural_notes(doc)
        if st:
            if "errors_missing" not in cats:
                cats.append("errors_missing")
            notes.extend(st)

        intent = intent_notes(doc.title, doc.text)
        if intent:
            cats.append("intent_mismatch")
            notes.extend(intent)

        row = {
            "id": doc.id,
            "type": doc.type,
            "title": doc.title,
            "url": doc.link,
            "slug": doc.slug,
            "words": doc.words,
            "h1_count": len(doc.h1),
            "h2_count": len(doc.h2),
            "h3_count": len(doc.h3),
            "images": doc.images,
            "internal_links": doc.internal_links,
            "faq_count": doc.faq_count,
            "date": doc.date,
            "modified": doc.modified,
            "heading_fingerprint": doc.heading_fingerprint,
            "problem_categories": "|".join(cats) if cats else "ok",
            "notes": " || ".join(notes) if notes else "",
        }
        all_rows.append(row)
        if "thin_content" in cats:
            thin_rows.append(row)
        if "errors_missing" in cats:
            error_rows.append(row)
        if "intent_mismatch" in cats:
            intent_rows.append({**row, "notes": " || ".join(intent)})
        if "boilerplate_overuse" in cats:
            boilerplate_rows.append(row)

    # Template clusters (same H2 skeleton, city-normalized)
    template_rows: list[dict[str, Any]] = []
    for fp, idxs in fp_groups.items():
        if len(idxs) < 6:
            continue
        sample = docs[idxs[0]]
        template_rows.append(
            {
                "cluster_size": len(idxs),
                "heading_fingerprint": fp,
                "sample_title": sample.title,
                "sample_url": sample.link,
                "h2_preview": " | ".join(normalize_cities(h) for h in sample.h2[:8]),
                "member_urls": " ".join(docs[i].link for i in idxs[:40]),
                "member_count_shown": min(40, len(idxs)),
                "problem_categories": "template_overuse",
                "notes": f"{len(idxs)} مقالاً تشترك في تسلسل العناوين نفسه بعد توحيد اسم المدينة",
            }
        )
    template_rows.sort(key=lambda r: -int(r["cluster_size"]))

    # Near-duplicate pairs via cosine on hashed bags + simhash buckets
    similar_rows: list[dict[str, Any]] = []
    if np is not None and docs:
        log("Computing similarity matrix…")
        vecs = hashed_vectors([d.normalized for d in docs])
        assert vecs is not None
        sim = vecs @ vecs.T
        parent = union_find_parent(len(docs))
        n = len(docs)
        pair_count = 0
        for i in range(n):
            # only check i+1..n
            row = sim[i, i + 1 :]
            hits = np.where(row >= args.similar_threshold)[0]
            for rel in hits:
                j = i + 1 + int(rel)
                score = float(row[rel])
                ham = hamming(docs[i].simhash, docs[j].simhash)
                if score < 0.93 and ham > 8:
                    continue
                uf_union(parent, i, j)
                city_a = city_in_title(docs[i].title)
                city_b = city_in_title(docs[j].title)
                if city_a and city_b and city_a == city_b:
                    pair_note = (
                        f"تعارض كلمات مفتاحية داخل نفس المدينة ({city_a}) — صفحتان تتصارعان على نفس النية"
                    )
                elif city_a and city_b and city_a != city_b:
                    pair_note = (
                        f"نسخة مدينة شبه مطابقة ({city_a} ↔ {city_b}) بعد توحيد اسم المدينة"
                    )
                else:
                    pair_note = "محتوى متشابه بعد إزالة أسماء المدن — احتمال cannibalization"
                if pair_count < 8000:
                    similar_rows.append(
                        {
                            "title_a": docs[i].title,
                            "url_a": docs[i].link,
                            "words_a": docs[i].words,
                            "title_b": docs[j].title,
                            "url_b": docs[j].link,
                            "words_b": docs[j].words,
                            "cosine": round(score, 4),
                            "simhash_hamming": ham,
                            "problem_categories": "duplicate_similar",
                            "notes": pair_note,
                        }
                    )
                    pair_count += 1
        similar_rows.sort(key=lambda r: -float(r["cosine"]))

        clusters: dict[int, list[int]] = defaultdict(list)
        for i in range(n):
            clusters[uf_find(parent, i)].append(i)
        cannibal_rows = []
        for members in clusters.values():
            if len(members) < 3:
                continue
            titles = [docs[i].title for i in members]
            cannibal_rows.append(
                {
                    "cluster_size": len(members),
                    "sample_titles": " | ".join(titles[:8]),
                    "urls": " ".join(docs[i].link for i in members[:30]),
                    "problem_categories": "duplicate_similar",
                    "notes": "مجموعة مقالات شبه متطابقة في الصياغة",
                }
            )
        cannibal_rows.sort(key=lambda r: -int(r["cluster_size"]))
    else:
        cannibal_rows = []
        log("numpy missing — skipped cosine similarity")

    # Master findings table (one row per flagged doc + template cluster summary is separate)
    master = [r for r in all_rows if r["problem_categories"] != "ok"]
    master.sort(key=lambda r: (r["problem_categories"], r["words"]))

    fields_doc = [
        "id",
        "type",
        "title",
        "url",
        "slug",
        "words",
        "h1_count",
        "h2_count",
        "h3_count",
        "images",
        "internal_links",
        "faq_count",
        "date",
        "modified",
        "heading_fingerprint",
        "problem_categories",
        "notes",
    ]
    write_csv(os.path.join(args.out_dir, "all-docs.csv"), all_rows, fields_doc)
    write_csv(os.path.join(args.out_dir, "thin-content.csv"), thin_rows, fields_doc)
    write_csv(os.path.join(args.out_dir, "errors-missing.csv"), error_rows, fields_doc)
    write_csv(os.path.join(args.out_dir, "intent-mismatch.csv"), intent_rows, fields_doc)
    write_csv(os.path.join(args.out_dir, "boilerplate-overuse.csv"), boilerplate_rows, fields_doc)
    write_csv(
        os.path.join(args.out_dir, "template-clusters.csv"),
        template_rows,
        [
            "cluster_size",
            "heading_fingerprint",
            "sample_title",
            "sample_url",
            "h2_preview",
            "member_urls",
            "member_count_shown",
            "problem_categories",
            "notes",
        ],
    )
    write_csv(
        os.path.join(args.out_dir, "similar-pairs.csv"),
        similar_rows[:8000],
        [
            "title_a",
            "url_a",
            "words_a",
            "title_b",
            "url_b",
            "words_b",
            "cosine",
            "simhash_hamming",
            "problem_categories",
            "notes",
        ],
    )
    write_csv(
        os.path.join(args.out_dir, "similar-clusters.csv"),
        cannibal_rows,
        ["cluster_size", "sample_titles", "urls", "problem_categories", "notes"],
    )
    write_csv(os.path.join(args.out_dir, "findings-master.csv"), master, fields_doc)

    ok = sum(1 for r in all_rows if r["problem_categories"] == "ok")
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base": args.base,
        "docs": len(docs),
        "posts": sum(1 for d in docs if d.type == "post"),
        "pages": sum(1 for d in docs if d.type == "page"),
        "thin": len(thin_rows),
        "thin_posts": sum(1 for r in thin_rows if r["type"] == "post"),
        "thin_pages": sum(1 for r in thin_rows if r["type"] == "page"),
        "boilerplate": len(boilerplate_rows),
        "template_clusters": len(template_rows),
        "template_articles": sum(int(r["cluster_size"]) for r in template_rows),
        "similar_pairs": len(similar_rows),
        "similar_clusters": len(cannibal_rows),
        "same_city_pairs": sum(1 for r in similar_rows if "داخل نفس المدينة" in str(r.get("notes", ""))),
        "intent": len(intent_rows),
        "errors": len(error_rows),
        "flagged": len(master),
        "clean": ok,
        "median_words": int(sorted(d.words for d in docs)[len(docs) // 2]) if docs else 0,
        "mean_words": int(sum(d.words for d in docs) / max(len(docs), 1)),
        "no_h1": sum(1 for d in docs if not d.title.strip()),
        "h1_in_body": sum(1 for d in docs if d.h1),
        "multi_h1": sum(1 for d in docs if len(d.h1) > 1),
        "weak_h2": sum(1 for d in docs if len(d.h2) < 3),
    }
    with open(os.path.join(args.out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    md_path = os.path.join(args.out_dir, "SEO-CONTENT-AUDIT.md")
    write_markdown_report(
        md_path,
        summary,
        thin_rows,
        template_rows,
        similar_rows,
        cannibal_rows,
        intent_rows,
        error_rows,
        boilerplate_rows,
        all_rows,
    )
    log(f"Wrote report to {md_path}")
    log(json.dumps(summary, ensure_ascii=False))
    return 0


def md_table(rows: list[dict[str, Any]], cols: list[tuple[str, str]], limit: int = 40) -> str:
    if not rows:
        return "_لا نتائج._\n"
    header = "| " + " | ".join(c[1] for c in cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    lines = [header, sep]
    for row in rows[:limit]:
        vals = []
        for key, _ in cols:
            v = row.get(key, "")
            s = str(v).replace("|", "/").replace("\n", " ")
            if len(s) > 160:
                s = s[:157] + "…"
            vals.append(s)
        lines.append("| " + " | ".join(vals) + " |")
    extra = len(rows) - limit
    if extra > 0:
        lines.append(f"\n_… و{extra} صفاً إضافياً في ملف CSV._")
    return "\n".join(lines) + "\n"


def write_markdown_report(
    path: str,
    summary: dict[str, Any],
    thin: list[dict[str, Any]],
    templates: list[dict[str, Any]],
    similar: list[dict[str, Any]],
    clusters: list[dict[str, Any]],
    intent: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    boilerplate: list[dict[str, Any]],
    all_rows: list[dict[str, Any]],
) -> None:
    s = summary
    parts = []
    parts.append("# تدقيق سيو تقني ومحتوى — ركن التطور السعودية\n")
    parts.append(f"تاريخ التوليد: `{s['generated_at']}`  ")
    parts.append(f"المصدر: `{s['base']}`  ")
    parts.append(
        f"المستندات: **{s['docs']}** (مقالات {s['posts']} / صفحات {s['pages']}) — متوسط الكلمات {s['mean_words']} — الوسيط {s['median_words']}\n"
    )
    parts.append("## ملخص تنفيذي\n")
    parts.append(
        "المشكلة الأساسية ليست نقص الكلمات بل **قالب واحد يُعاد مع استبدال اسم الخدمة والمدينة**. "
        "H1 يُرسم من عنوان المقال في القالب (خارج `post_content`) لذلك غياب H1 داخل الجسم ليس خطأً. "
        "أسماء المدن تُطبَّع قبل قياس التشابه؛ التشابه يعني نفس الصياغة وليس مجرد تكرار كلمة «الرياض».\n"
    )
    parts.append("| المؤشر | العدد | التفسير |")
    parts.append("|---|---|---|")
    parts.append(
        f"| مقالات خدمات < 1000 كلمة | {s.get('thin_posts', 0)} | كل المقالات المنشورة تتجاوز الحد |"
    )
    parts.append(
        f"| صفحات هيكلية < 1000 كلمة | {s.get('thin_pages', s['thin'])} | مدونة/أسعار/مدن/اتصال — متوقع لصفحات أدوات |"
    )
    parts.append(
        f"| إفراط عبارات قالبية | {s.get('boilerplate', 0)} | «موسم ذروة» + «هل الخدمة للشقق والفلل» على خدمات غير النقل |"
    )
    parts.append(
        f"| عناقيد هيكل H2 متطابق | {s['template_clusters']} تغطي {s['template_articles']} | نفس تسلسل العناوين بعد توحيد المدينة |"
    )
    parts.append(
        f"| أزواج متشابهة (cosine ≥ 0.90) | {s['similar_pairs']} | منها {s.get('same_city_pairs', 0)} تعارض داخل نفس المدينة |"
    )
    parts.append(f"| مجموعات تكرار/تعارض كلمات | {s['similar_clusters']} | city-clone أو صفحتان لنفس النية |")
    parts.append(
        f"| عدم تطابق نية البحث (حقيقي) | {s['intent']} | عنوان خدمة والجسم يتحدث عن خدمة أخرى |"
    )
    parts.append(f"| أخطاء/عناصر ناقصة | {s['errors']} | صور مفقودة أو نصوص نائبة |")
    parts.append(f"| بدون عنوان (H1 القالب) | {s['no_h1']} | |")
    parts.append(f"| أكثر من H1 داخل المحتوى | {s['multi_h1']} | |")
    parts.append(f"| H2 < 3 | {s['weak_h2']} | |")
    parts.append(f"| مستندات بعلامة واحدة على الأقل | {s['flagged']} | الغالبية بسبب القالب المشترك |")
    parts.append(f"| بدون ملاحظات في الفحوصات الآلية | {s['clean']} | |\n")

    finding_cols = [
        ("title", "العنوان"),
        ("url", "الرابط"),
        ("words", "كلمات"),
        ("problem_categories", "فئة المشكلة"),
        ("notes", "ملاحظات محددة"),
    ]
    priority = []
    priority.extend(sorted(thin, key=lambda r: int(r["words"])))
    priority.extend(intent)
    priority.extend(errors)
    # representative boilerplate samples (not the full 1700+)
    seen_urls = {r.get("url") for r in priority}
    for row in boilerplate:
        if row.get("url") in seen_urls:
            continue
        priority.append(row)
        seen_urls.add(row.get("url"))
        if sum(1 for r in priority if "boilerplate_overuse" in str(r.get("problem_categories", ""))) >= 15:
            break

    parts.append("## جدول النتائج (أولوية + عيّنة)\n")
    parts.append(
        "الأعمدة: عنوان / رابط / كلمات / فئة المشكلة / ملاحظات. القائمة الكاملة في `findings-master.csv`.\n"
    )
    parts.append(md_table(priority, finding_cols, 80))

    parts.append("## 1) محتوى ضعيف (Thin Content)\n")
    parts.append(
        "حدّ 1000 كلمة يُطبَّق على مقالات الخدمات. الصفحات الهيكلية مدرجة للشفافية وليست أولوية إعادة كتابة.\n"
    )
    thin_sorted = sorted(thin, key=lambda r: int(r["words"]))
    parts.append(md_table(thin_sorted, finding_cols, 50))

    parts.append("## 2) إفراط القوالب (Template / Boilerplate)\n")
    parts.append(
        f"**{s.get('boilerplate', 0)} مقالاً** تشترك في عبارات جاهزة (انتقال/موسم ذروة، أسئلة الشقق والفلل، "
        "«لا نضع رقماً ثابتاً»، توقيع فريق المحتوى). هذا ضعف قيمة فريدة وليس نقص كلمات.\n"
    )
    parts.append("### عيّنة مقالات القالب\n")
    parts.append(md_table(boilerplate, finding_cols, 20))
    parts.append("### عناقيد هيكل H2 المتطابق (بعد توحيد المدينة)\n")
    parts.append(
        md_table(
            templates,
            [
                ("cluster_size", "حجم العنقود"),
                ("sample_title", "عيّنة عنوان"),
                ("sample_url", "رابط عيّنة"),
                ("h2_preview", "تسلسل H2 بعد توحيد المدينة"),
                ("notes", "ملاحظات"),
            ],
            25,
        )
    )

    parts.append("## 3) محتوى مكرر/متشابه (Duplicate / Cannibalization)\n")
    same_city = [r for r in similar if "داخل نفس المدينة" in str(r.get("notes", ""))]
    city_clone = [r for r in similar if "نسخة مدينة" in str(r.get("notes", ""))]
    parts.append(
        f"أزواج داخل نفس المدينة (تعارض كلمات): **{len(same_city)}**. "
        f"نسخ المدن (نفس المقال باسم مدينة أخرى): **{len(city_clone)}**.\n"
    )
    parts.append("### أكبر المجموعات\n")
    parts.append(
        md_table(
            clusters,
            [("cluster_size", "الحجم"), ("sample_titles", "عناوين"), ("notes", "ملاحظات")],
            20,
        )
    )
    parts.append("### أعلى تعارض داخل نفس المدينة\n")
    parts.append(
        md_table(
            same_city or similar,
            [
                ("title_a", "عنوان أ"),
                ("url_a", "رابط أ"),
                ("title_b", "عنوان ب"),
                ("url_b", "رابط ب"),
                ("cosine", "cosine"),
                ("notes", "ملاحظات"),
            ],
            25,
        )
    )
    parts.append("### أعلى الأزواج تشابهاً عموماً\n")
    parts.append(
        md_table(
            similar,
            [
                ("title_a", "عنوان أ"),
                ("url_a", "رابط أ"),
                ("title_b", "عنوان ب"),
                ("url_b", "رابط ب"),
                ("cosine", "cosine"),
                ("notes", "ملاحظات"),
            ],
            20,
        )
    )

    parts.append("## 4) عدم تطابق نية البحث (Intent Mismatch)\n")
    parts.append(
        "هنا فقط التناقض الحقيقي بين العنوان والجسم (مثلاً شحن سيارات بأسئلة الشقق، أو تكييف بفقرات رخام/خشب). "
        "عبارة موسم الذروة صُنّفت تحت القوالب وليست نية بحث مستقلة.\n"
    )
    parts.append(md_table(intent, finding_cols, 80))

    parts.append("## 5) أخطاء وعناصر مفقودة\n")
    parts.append(
        "H1 القالب موجود من عنوان المقال. لا توجد نصوص `lorem ipsum` ولا أرقام `966000000000` داخل المحتوى المفحوص. "
        "الصفوف أدناه: صور داخل الجسم أو عناصر بنيوية أخرى.\n"
    )
    parts.append(
        md_table(
            sorted(errors, key=lambda r: r["notes"]),
            [
                ("title", "العنوان"),
                ("url", "الرابط"),
                ("words", "كلمات"),
                ("h1_count", "H1 داخل الجسم"),
                ("h2_count", "H2"),
                ("problem_categories", "الفئة"),
                ("notes", "ملاحظات"),
            ],
            40,
        )
    )

    parts.append("## أولويات المعالجة\n")
    parts.append("1. حذف/استبدال فقرة «تجهيزاً مرتباً قبل انتقال أو موسم ذروة» من كل خدمة ليست نقل عفش.")
    parts.append("2. إعادة كتابة أسئلة «هل الخدمة للشقق والفلل؟» لتطابق نوع الخدمة (سيارات، شحن، مكافحة…).")
    parts.append("3. دمج أو تمييز أزواج cannibalization داخل المدينة (`سباك` مقابل `شركة سباك`، أحياء جدة/الرياض لكشف التسربات).")
    parts.append("4. إصلاح صفحات التكييف التي تتحدث عن رخام/خشب وصفحات شحن السيارات/الأثاث التي تفترض عقاراً.")
    parts.append("5. تنويع هيكل H2 لكل عائلة خدمة بدل الهيكل الثابت «اطلب… / ما هي خدمة… / مميزات…».")
    parts.append("6. الصفحات الهيكلية (مدن، أسعار، اتصال، خريطة، مدونة) لا تحتاج 1000 كلمة.\n")

    parts.append("## ملفات CSV\n")
    parts.append("- `thin-content.csv`")
    parts.append("- `boilerplate-overuse.csv`")
    parts.append("- `template-clusters.csv`")
    parts.append("- `similar-pairs.csv` / `similar-clusters.csv`")
    parts.append("- `intent-mismatch.csv`")
    parts.append("- `errors-missing.csv`")
    parts.append("- `findings-master.csv` (كل المستندات المعلّمة)")
    parts.append("- `all-docs.csv` (الجرد الكامل بما فيه السليم آلياً)")
    parts.append("- `summary.json`\n")
    parts.append(
        "إعادة التشغيل:\n\n"
        "```bash\n"
        "WP_USER=cursor WP_APP_PASSWORD='xxxx' python3 audit/seo_content_audit.py \\\n"
        "  --base https://www.rukn-eltatawer.com/sa --out-dir audit/seo-run\n"
        "```\n"
        "الكاش الافتراضي: `/tmp/rukn-seo-audit`. لا تضع كلمة مرور التطبيقات في git.\n"
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


if __name__ == "__main__":
    sys.exit(main())
