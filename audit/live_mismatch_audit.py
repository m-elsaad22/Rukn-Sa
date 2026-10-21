#!/usr/bin/env python3
"""Live /sa/ audit: errors, gaps, and articles whose body does not match the service."""
from __future__ import annotations

import csv
import html as html_lib
import json
import os
import re
import ssl
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audit" / "live-run-2026-10-21"
CTX = ssl.create_default_context()
UA = "RuknLiveAudit/2026-10-21"


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip().strip("'").strip('"')
        if k and k not in os.environ:
            os.environ[k] = v


load_dotenv(ROOT / ".env")
BASE = (os.environ.get("WP_BASE_URL") or "https://www.rukn-eltatawer.com/sa").rstrip("/")
USER = os.environ.get("WP_USERNAME") or os.environ.get("WP_USER") or ""
PASS = os.environ.get("WP_APP_PASSWORD") or ""
PUBLIC = "https://www.rukn-eltatawer.com"

CITIES = (
    "riyadh", "jeddah", "mecca", "makkah", "medina", "madinah", "dammam", "khobar",
    "taif", "abha", "tabuk", "buraidah", "jazan", "hail", "yanbu", "jubail", "ahsa",
    "khafji", "baha", "al-baha", "khamis-mushait", "khamis", "qassim", "najran",
    "hafuf", "hofuf", "unayzah", "kharj", "diriyah", "center", "south", "north",
    "east", "west",
)

# slug prefix (after stripping city tokens) -> family
FAMILY_PREFIXES = {
    "car-shipping": "car_shipping",
    "domestic-shipping": "parcel_shipping",
    "furniture-shipping": "furniture_shipping",
    "piano-moving": "moving",
    "home-cleaning": "home_cleaning",
    "villa-cleaning": "home_cleaning",
    "apartment-cleaning": "home_cleaning",
    "office-cleaning": "home_cleaning",
    "kitchen-cleaning": "home_cleaning",
    "mattress-cleaning": "home_cleaning",
    "moquette-cleaning": "home_cleaning",
    "curtain-cleaning": "home_cleaning",
    "furniture-cleaning": "home_cleaning",
    "school-nursery-cleaning": "home_cleaning",
    "hospital-clinic-cleaning": "home_cleaning",
    "stone-facade-cleaning": "facade_cleaning",
    "glass-facade-cleaning": "facade_cleaning",
    "chimney-cleaning": "home_cleaning",
    "ac-cleaning-washing": "ac",
    "ac-cleaning": "ac",
    "duct-cleaning": "ac",
    "split-ac-maintenance": "ac",
    "split-ac-installation": "ac",
    "central-ac-maintenance": "ac",
    "central-ac": "ac",
    "window-ac-installation": "ac",
    "ac-relocation-installation": "ac",
    "ac-freon-refill": "ac",
    "ac-leak-detection": "ac",
    "ac-duct-maintenance": "ac",
    "ac-periodic-maintenance-contracts": "ac",
    "ac-tech": "ac",
    "new-central-ac-installation": "ac",
    "solar-ac-installation": "ac",
    "water-leak-detection": "leak",
    "roof-insulation": "insulation",
    "roof-waterproofing": "insulation",
    "tank": "plumbing",
    "water-tank": "plumbing",
    "home-plumber": "plumbing",
    "home-electrician": "electrical",
    "electrical-maintenance": "electrical",
    "electric-panel-maintenance": "electrical",
    "pest-control": "pest",
    "rodent-control": "pest",
    "bed-bug-control": "pest",
    "lizard-control": "pest",
    "scorpion-control": "pest",
    "bird-control": "pest",
    "flying-pest-control": "pest",
    "crawling-pest-control": "pest",
    "mosquito-fly-control": "pest",
    "apartment-painting": "painting",
    "painter": "painting",
    "roof-insulation-painting": "painting",
    "gypsum-board": "gypsum",
    "gypsum-tech": "gypsum",
    "gypsum-board-decor": "gypsum",
    "carpenter": "carpentry",
    "blacksmith-doors-windows": "metalwork",
    "artificial-grass": "landscaping",
    "artificial-grass-grdn": "landscaping",
    "wall-grass": "landscaping",
    "automatic-irrigation": "landscaping",
    "modern-irrigation": "landscaping",
    "sat-dish-tech": "satellite",
    "satellite-tech": "satellite",
    "home-audio-tech": "av",
    "ro-plants": "plumbing",
}

# Distinctive body tokens. Overlap (ماء، شركة) is ignored.
FAMILY_TOKENS = {
    "car_shipping": {"سيارة", "سيارات", "مركبة", "ناقلة", "سطحة", "ونش سيارات", "الميناء", "اللوحات", "المقصورة"},
    "parcel_shipping": {"طرد", "طرود", "بضاعة", "كرتون", "صندوق", "شحنة"},
    "furniture_shipping": {"عفش", "أثاث", "اثاث", "تغليف", "فك", "تركيب", "خزانة", "خزائن"},
    "moving": {"عفش", "أثاث", "تغليف", "ونش", "دينا", "انتقال"},
    "home_cleaning": {"رخام", "كنب", "موكيت", "سجاد", "غبار", "جلي", "تعقيم أرضيات"},
    "facade_cleaning": {"واجهة", "واجهات", "زجاج", "حجر", "سقالات"},
    "ac": {"مكيف", "مكيفات", "تكييف", "فريون", "سبليت", "دكت", "كمبروسر", "فلتر", "مكثف"},
    "leak": {"تسرب", "تسربات", "رطوبة", "عزل", "عداد", "بدون تكسير"},
    "insulation": {"عزل", "أسطح", "حراري", "مائي", "فوم", "بيتومين"},
    "plumbing": {"سباكة", "سباك", "تمديدات", "مجاري", "خزان", "سخان"},
    "electrical": {"كهرباء", "كهربائي", "لوحة", "قواطع", "تأريض", "أسلاك"},
    "pest": {"حشرات", "مكافحة", "صراصير", "قوارض", "نمل", "بق", "فئران", "بعوض"},
    "painting": {"دهان", "بوية", "معجون", "نقاشة", "طلاء"},
    "gypsum": {"جبس", "جبسم بورد", "أسقف مستعارة"},
    "carpentry": {"نجار", "خشب", "أبواب خشب"},
    "metalwork": {"حداد", "ألمنيوم", "شبابيك"},
    "landscaping": {"عشب", "حديقة", "ري", "نوافير", "جداري"},
    "satellite": {"ستلايت", "دش", "رسيفر"},
    "av": {"صوتيات", "سينما منزلية", "سماعات"},
}

# If title/slug is family A, these body phrases mean leftover template from family B.
WRONG_PHRASES = [
    ("car_shipping", ("شقق والفلل", "للشقق والفلل", "عقارك", "رخام", "كنب", "موكيت", "موسم ذروة"), "شحن سيارات بنص منازل/تنظيف"),
    ("parcel_shipping", ("شقق والفلل", "للشقق والفلل", "رخام", "كنب", "فريون"), "شحن طرود بنص منازل/تكييف"),
    ("ac", ("رخام", "كنب", "موكيت", "سجاد", "جلي الأرض", "بلل مفرط للخشب"), "تكييف بنص تنظيف منازل"),
    ("electrical", ("رخام", "كنب", "موكيت", "فريون", "صراصير"), "كهرباء بنص تنظيف/حشرات/تكييف"),
    ("pest", ("فريون", "سبليت", "دكت", "رخام", "جبس بورد"), "مكافحة حشرات بنص تكييف/تشطيب"),
    ("painting", ("فريون", "صراصير", "تسليك مجاري", "ستلايت"), "دهان بنص خدمة أخرى"),
    ("leak", ("فريون", "صراصير", "كنب", "موكيت", "ستلايت"), "كشف تسربات بنص خدمة أخرى"),
    ("landscaping", ("فريون", "صراصير", "تسليك مجاري"), "حدائق بنص خدمة أخرى"),
]

UAE_PATTERNS = [
    r"دبي", r"أبوظبي", r"ابوظبي", r"الشارقة", r"عجمان", r"الفجيرة", r"أم القيوين",
    r"الإمارات", r"الامارات", r"\bAED\b", r"درهم", r"0568060309", r"971568060309",
]
PLACEHOLDERS = [
    r"lorem ipsum", r"\bTODO\b", r"نص هنا", r"اكتب هنا", r"966000000000",
    r"vi/الفيديو/", r"youtube\.com/vi/الفيديو", r"\{PHONE", r"placeholder",
]
BOILER_LEFTOVER = [
    "تجهيزاً مرتباً قبل انتقال أو موسم ذروة",
    "هل الخدمة للشقق والفلل",
    "لا نضع رقماً ثابتاً لا يمثّل عقارك",
    "نوضّح ما سيدخل في النطاق وما لن يدخل",
]

AR_CITIES = (
    "الرياض", "جدة", "مكة", "المدينة", "الدمام", "الخبر", "الطائف", "أبها",
    "تبوك", "بريدة", "جازان", "حائل", "ينبع", "الجبيل", "الأحساء",
)


def auth_header() -> str:
    import base64

    return "Basic " + base64.b64encode(f"{USER}:{PASS}".encode()).decode()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


def http(url: str, headers=None, follow=True, timeout=40):
    h = {"User-Agent": UA, "Accept": "*/*"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    handlers = [urllib.request.HTTPSHandler(context=CTX)]
    if not follow:
        handlers.append(NoRedirect())
    opener = urllib.request.build_opener(*handlers)
    try:
        with opener.open(req, timeout=timeout) as resp:
            return resp.status, dict(resp.headers), resp.read(), resp.geturl()
    except urllib.error.HTTPError as e:
        body = e.read() if e.fp else b""
        loc = e.headers.get("Location") if e.headers else None
        return e.code, dict(e.headers or {}), body, loc


def wp(path: str, query=None):
    url = BASE + path
    if query:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(query)
    headers = {"Accept": "application/json"}
    if USER and PASS:
        headers["Authorization"] = auth_header()
    st, hdrs, body, _ = http(url, headers=headers, timeout=90)
    try:
        data = json.loads(body.decode("utf-8", "replace"))
    except Exception:
        data = body[:400].decode("utf-8", "replace")
    return st, hdrs, data


def strip_html(raw: str) -> str:
    raw = re.sub(r"<script[\s\S]*?</script>", " ", raw, flags=re.I)
    raw = re.sub(r"<style[\s\S]*?</style>", " ", raw, flags=re.I)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = html_lib.unescape(raw)
    raw = unicodedata.normalize("NFKC", raw)
    return re.sub(r"\s+", " ", raw).strip()


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z\u0600-\u06FF]+", text))


def headings(html: str, level: int) -> list[str]:
    found = re.findall(rf"<h{level}[^>]*>(.*?)</h{level}>", html, flags=re.I | re.S)
    return [strip_html(x) for x in found if strip_html(x)]


def service_key(slug: str) -> str:
    parts = [p for p in slug.split("-") if p and p not in CITIES]
    return "-".join(parts) or slug


def family_of(slug: str) -> str:
    key = service_key(slug)
    if key in FAMILY_PREFIXES:
        return FAMILY_PREFIXES[key]
    # longest prefix
    best = ""
    fam = "other"
    for pref, family in FAMILY_PREFIXES.items():
        if key.startswith(pref) and len(pref) > len(best):
            best = pref
            fam = family
    return fam


def token_hits(text: str, tokens: set[str]) -> list[str]:
    return [t for t in tokens if t in text]


def analyze_post(post: dict) -> dict:
    title = strip_html(post.get("title", {}).get("rendered") or "")
    html = post.get("content", {}).get("rendered") or ""
    text = strip_html(html)
    slug = post.get("slug") or ""
    fam = family_of(slug)
    words = word_count(text)
    h2 = headings(html, 2)
    notes = []
    cats = []

    own = token_hits(text, FAMILY_TOKENS.get(fam, set()))
    foreign = {}
    for other, toks in FAMILY_TOKENS.items():
        if other == fam:
            continue
        hits = token_hits(text, toks)
        if hits:
            foreign[other] = hits
    top_foreign = max(foreign.items(), key=lambda kv: len(kv[1]), default=None)

    if fam != "other" and top_foreign and len(top_foreign[1]) >= 4 and len(top_foreign[1]) > max(len(own), 1) + 1:
        cats.append("wrong_service_body")
        notes.append(
            f"السلَج عائلة «{fam}» ({len(own)} مفردة مطابقة) بينما النص يغلبه «{top_foreign[0]}» ({', '.join(top_foreign[1][:6])})"
        )

    for rule_fam, phrases, note in WRONG_PHRASES:
        if fam != rule_fam:
            continue
        hit = [p for p in phrases if p in text]
        if len(hit) >= 2 or (len(hit) == 1 and hit[0] in ("شقق والفلل", "للشقق والفلل", "عقارك")):
            if "wrong_service_body" not in cats:
                cats.append("wrong_service_body")
            notes.append(note + ": " + "، ".join(hit[:4]))

    boiler = [p for p in BOILER_LEFTOVER if p in text]
    if boiler:
        cats.append("boilerplate_leftover")
        notes.append("قالب باقٍ: " + " | ".join(boiler[:3]))

    uae = []
    for pat in UAE_PATTERNS:
        if re.search(pat, text) or re.search(pat, html, flags=re.I):
            # «أدبي» false positive on دبي handled by word-ish patterns; skip أدبي
            if pat == r"دبي" and "أدبي" in text and "دبي" not in text.replace("أدبي", ""):
                continue
            uae.append(pat.replace("\\b", "").replace("\\", ""))
    if uae:
        cats.append("uae_leftover")
        notes.append("بقايا إمارات في المحتوى: " + ", ".join(uae[:6]))

    ph = [p for p in PLACEHOLDERS if re.search(p, html + "\n" + text, flags=re.I)]
    if ph:
        cats.append("placeholder")
        notes.append("نصوص نائبة: " + ", ".join(ph[:4]))

    if "tel:" in html.lower() and "wa.me" not in html.lower():
        cats.append("tel_cta")
        notes.append("رابط tel: داخل المحتوى")

    if words < 350 and post.get("type") != "page":
        cats.append("thin")
        notes.append(f"قصير: {words} كلمة")

    city_in_title = next((c for c in AR_CITIES if c in title), None)
    if city_in_title and city_in_title not in text and fam != "other":
        cats.append("city_missing_in_body")
        notes.append(f"المدينة «{city_in_title}» في العنوان وغائبة عن النص")

    imgs = len(re.findall(r"<img\b", html, flags=re.I))
    featured = post.get("featured_media") or 0
    if imgs == 0 and not featured:
        cats.append("no_images")
        notes.append("لا صورة بارزة ولا صور داخل المحتوى")

    if len(h2) < 2 and fam != "other":
        cats.append("weak_structure")
        notes.append(f"H2 قليلة ({len(h2)})")

    return {
        "id": post.get("id"),
        "slug": slug,
        "title": title,
        "url": post.get("link"),
        "family": fam,
        "service_key": service_key(slug),
        "words": words,
        "h2": len(h2),
        "images": imgs,
        "featured_media": featured,
        "own_hits": "|".join(own),
        "foreign_family": top_foreign[0] if top_foreign else "",
        "foreign_hits": "|".join(top_foreign[1][:8]) if top_foreign else "",
        "categories": "|".join(cats),
        "notes": " // ".join(notes),
        "modified": (post.get("modified") or "")[:10],
    }


def fetch_all_posts() -> list[dict]:
    out = []
    page = 1
    while page <= 40:
        st, hdrs, data = wp(
            "/wp-json/wp/v2/posts",
            {
                "per_page": "100",
                "page": str(page),
                "status": "publish",
                "context": "view",
                "_fields": "id,slug,title,link,content,date,modified,featured_media,type",
            },
        )
        if st != 200 or not isinstance(data, list) or not data:
            print(f"posts page {page} HTTP {st}", file=sys.stderr)
            break
        out.extend(data)
        total = int(hdrs.get("X-WP-TotalPages") or hdrs.get("x-wp-totalpages") or 1)
        print(f"  posts page {page}/{total} +{len(data)} total={len(out)}", file=sys.stderr)
        if page >= total:
            break
        page += 1
        time.sleep(0.15)
    return out


def fetch_pages() -> list[dict]:
    st, hdrs, data = wp(
        "/wp-json/wp/v2/pages",
        {"per_page": "50", "status": "publish", "_fields": "id,slug,title,link,content,modified"},
    )
    return data if isinstance(data, list) else []


def probe_live(paths: list[str]) -> list[dict]:
    rows = []

    def one(path: str) -> dict:
        url = PUBLIC + path if path.startswith("/") else path
        st, hdrs, body, loc = http(url, follow=False, timeout=25)
        html = (body or b"").decode("utf-8", "replace")
        title = re.search(r"<title>(.*?)</title>", html, flags=re.I | re.S)
        can = re.search(r'rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', html, flags=re.I)
        robots = re.search(r'name=["\']robots["\'][^>]*content=["\']([^"\']+)', html, flags=re.I)
        wa = sorted(set(re.findall(r"wa\.me/(\+?\d+)", html)))
        tel = sorted(set(re.findall(r"href=[\"']tel:([^\"']+)", html, flags=re.I)))
        flags = []
        if st == 200 and not title:
            flags.append("missing_title")
        if "AED" in html or 'currency":"AED"' in html or "taxRate\":\"5\"" in html:
            flags.append("aed_or_5pct_vat")
        if re.search(r"دبي|أبوظبي|الإمارات", html) and "/en/" not in path:
            flags.append("uae_visible")
        if "0568060309" in html:
            flags.append("old_sa_phone_visible")
        if re.search(r"4\.9|5841|6481|98\.7", html):
            flags.append("possible_fake_rating")
        if 'data-country="ae"' in html:
            flags.append("country_switcher_ae")
        if "vi/الفيديو" in html:
            flags.append("youtube_placeholder")
        return {
            "path": path,
            "status": st,
            "location": loc or "",
            "title": strip_html(title.group(1)) if title else "",
            "canonical": can.group(1) if can else "",
            "robots": robots.group(1) if robots else hdrs.get("X-Robots-Tag") or hdrs.get("x-robots-tag") or "",
            "whatsapp": ",".join(wa),
            "tel": ",".join(tel),
            "flags": "|".join(flags),
            "bytes": len(html),
        }

    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(one, p): p for p in paths}
        for fut in as_completed(futs):
            rows.append(fut.result())
    rows.sort(key=lambda r: r["path"])
    return rows


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = fieldnames or list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def md_table(rows: list[dict], cols: list[tuple[str, str]], limit: int = 40) -> str:
    lines = ["| " + " | ".join(h for h, _ in cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for r in rows[:limit]:
        lines.append("| " + " | ".join(str(r.get(k, "")).replace("|", "/")[:120] for _, k in cols) + " |")
    if len(rows) > limit:
        lines.append(f"| … | باقي {len(rows) - limit} في CSV |")
    return "\n".join(lines)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    print("== fetch posts ==", file=sys.stderr)
    posts = fetch_all_posts()
    print("== fetch pages ==", file=sys.stderr)
    pages = fetch_pages()
    analyzed = [analyze_post(p) for p in posts]
    page_rows = []
    for p in pages:
        r = analyze_post({**p, "type": "page", "featured_media": 1})
        r["family"] = "page"
        page_rows.append(r)

    mismatch = [r for r in analyzed if "wrong_service_body" in r["categories"]]
    uae = [r for r in analyzed if "uae_leftover" in r["categories"]]
    boiler = [r for r in analyzed if "boilerplate_leftover" in r["categories"]]
    thin = [r for r in analyzed if "thin" in r["categories"]]
    ph = [r for r in analyzed if "placeholder" in r["categories"]]
    citymiss = [r for r in analyzed if "city_missing_in_body" in r["categories"]]
    noimg = [r for r in analyzed if "no_images" in r["categories"]]

    fam_counts = Counter(r["family"] for r in analyzed)
    svc_counts = Counter(r["service_key"] for r in analyzed)

    print("== live HTML probes ==", file=sys.stderr)
    live_paths = [
        "/sa/",
        "/sa/about/",
        "/sa/services/",
        "/sa/pricing/",
        "/sa/cities/",
        "/sa/cities/riyadh/",
        "/sa/contact-us/",
        "/sa/privacy-policy/",
        "/sa/faq/",
        "/sa/blog/",
        "/sa/en/",
        "/sa/car-shipping-jeddah/",
        "/sa/car-shipping-dammam/",
        "/sa/car-shipping-riyadh/",
        "/sa/water-leak-detection-jeddah/",
        "/sa/ac-cleaning-washing-riyadh/",
        "/sa/duct-cleaning-riyadh/",
        "/sa/home-cleaning-riyadh/",
        "/sa/pest-control-riyadh/",
        "/sa/category/water-leak-detection/",
        "/sa/category/sewer-drainage/",
        "/sa/category/leak-detection-and-insulation/",
    ]
    live = probe_live(live_paths)

    write_csv(OUT / "all-posts.csv", analyzed)
    write_csv(OUT / "wrong-service.csv", mismatch)
    write_csv(OUT / "uae-in-posts.csv", uae)
    write_csv(OUT / "boilerplate-leftover.csv", boiler)
    write_csv(OUT / "thin-posts.csv", thin)
    write_csv(OUT / "placeholders.csv", ph)
    write_csv(OUT / "live-html-probes.csv", live)
    write_csv(OUT / "pages.csv", page_rows)

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "posts": len(analyzed),
        "pages": len(page_rows),
        "wrong_service_body": len(mismatch),
        "uae_in_posts": len(uae),
        "boilerplate_leftover": len(boiler),
        "thin_posts": len(thin),
        "placeholders": len(ph),
        "city_missing_in_body": len(citymiss),
        "no_images": len(noimg),
        "families": dict(fam_counts),
        "wrong_by_family": dict(Counter(r["family"] for r in mismatch)),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # coverage gaps: core services missing in major cities
    core = [
        "water-leak-detection",
        "home-cleaning",
        "ac-cleaning-washing",
        "pest-control",
        "roof-insulation",
        "car-shipping",
    ]
    major = ["riyadh", "jeddah", "mecca", "medina", "dammam", "khobar", "taif", "abha"]
    have = {(r["service_key"], r["slug"].rsplit("-", 1)[-1]) for r in analyzed}
    # better: slug endswith city
    have2 = set()
    for r in analyzed:
        for city in major:
            if r["slug"].endswith("-" + city):
                have2.add((r["service_key"], city))
    gaps = []
    for svc in core:
        for city in major:
            if (svc, city) not in have2:
                gaps.append({"service": svc, "city": city, "expected": f"/sa/{svc}-{city}/"})
    write_csv(OUT / "coverage-gaps.csv", gaps)

    print(json.dumps({k: summary[k] for k in summary if k != "families"}, ensure_ascii=False, indent=2))
    print("wrong", len(mismatch), "uae", len(uae), "boiler", len(boiler), "thin", len(thin), "gaps", len(gaps))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
