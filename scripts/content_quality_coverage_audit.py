#!/usr/bin/env python3
"""Full SA content-quality & coverage audit for rukn-eltatawer.com/sa."""

from __future__ import annotations

import base64
import hashlib
import json
import re
import time
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

BASE = "https://www.rukn-eltatawer.com/sa/wp-json"
AUTH = base64.b64encode(b"cursor:PCkk ig95 Gu6c zOgC GLYG FYsk").decode()
H = {
    "Authorization": f"Basic {AUTH}",
    "User-Agent": "Mozilla/5.0 RuknContentAudit/2026-10-04",
}
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
DATA.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)

# Major SA cities expected for coverage matrix
TARGET_CITIES = {
    "riyadh": "الرياض",
    "jeddah": "جدة",
    "mecca": "مكة المكرمة",
    "makkah": "مكة المكرمة",
    "medina": "المدينة المنورة",
    "madinah": "المدينة المنورة",
    "dammam": "الدمام",
    "khobar": "الخبر",
    "taif": "الطائف",
    "abha": "أبها",
    "tabuk": "تبوك",
    "buraidah": "بريدة",
    "qassim": "القصيم",
    "khamis-mushait": "خميس مشيط",
    "khamis": "خميس مشيط",
    "najran": "نجران",
    "jazan": "جازان",
    "yanbu": "ينبع",
    "jubail": "الجبيل",
    "hofuf": "الهفوف",
    "alhasa": "الأحساء",
    "ahsa": "الأحساء",
    "hail": "حائل",
    "sakaka": "سكاكا",
    "arar": "عرعر",
    "najran": "نجران",
    "al-khafji": "الخفجي",
    "khafji": "الخفجي",
    "ras-tanura": "رأس تنورة",
    "qatif": "القطيف",
    "dhahran": "الظهران",
    "unaizah": "عنيزة",
    "hafar-albatin": "حفر الباطن",
    "hafar": "حفر الباطن",
    "kharj": "الخرج",
    "dawadmi": "الدوادمي",
    "majmaah": "المجمعة",
    "zulfi": "الزلفي",
    "shaqra": "شقراء",
    "wadi-aldawasir": "وادي الدواسر",
    "bisha": "بيشة",
    "muhail": "محايل عسير",
    "sabya": "صبيا",
    "abu-arish": "أبو عريش",
    "rabigh": "رابغ",
    "lith": "الليث",
    "baha": "الباحة",
    "albaha": "الباحة",
}

CORE_SERVICES = {
    "leak": {
        "ar": "كشف تسربات المياه",
        "tokens": ["leak", "تسرب", "water-leak", "pipe-leak"],
        "topic": r"تسرب|كشف تسرب|رطوبة|فاتورة مياه|مواسير",
    },
    "insul": {
        "ar": "عزل أسطح/خزانات",
        "tokens": ["insulation", "waterproof", "عزل", "roof-insul", "tank-insul"],
        "topic": r"عزل|عازل|مواد عزل|عزل مائي|عزل حراري|خزان",
    },
    "ac": {
        "ar": "تكييف/غسيل مكيفات",
        "tokens": ["ac-", "split-ac", "duct", "central-ac", "مكيف", "تكييف", "ac-cleaning"],
        "topic": r"تكييف|مكيف|فريون|دكت|سبليت|غسيل مكيف",
    },
    "clean": {
        "ar": "تنظيف منازل",
        "tokens": ["cleaning", "sofa", "carpet", "steriliz", "disinfect", "تنظيف", "غسيل كنب"],
        "topic": r"تنظيف|غسيل|سجاد|كنب|تعقيم|جلي",
    },
    "pest": {
        "ar": "مكافحة حشرات",
        "tokens": ["pest", "termite", "cockroach", "ant-control", "bed-bug", "rodent", "mosquito", "مكافحة"],
        "topic": r"مكافحة|حشرات|نمل|صراصير|بق|فئران|مبيد|آفات",
    },
    "plumb": {
        "ar": "سباكة",
        "tokens": ["plumb", "sewer", "سباك", "plumber"],
        "topic": r"سباكة|سباك|مواسير|انسداد|صرف|تمديدات صحي",
    },
    "elec": {
        "ar": "كهرباء منازل",
        "tokens": ["electric", "electrician", "كهرب"],
        "topic": r"كهرباء|كهربائي|قواطع|تمديدات|إنارة",
    },
    "grass": {
        "ar": "عشب صناعي",
        "tokens": ["grass", "artificial-grass", "wall-grass", "عشب"],
        "topic": r"عشب|نجيلة|جداري|صناعي",
    },
    "move": {
        "ar": "نقل عفش",
        "tokens": ["moving", "furniture-mov", "نقل", "shipping"],
        "topic": r"نقل|عفش|تغليف|شاحنة|تحميل",
    },
}

TEMPLATE_MARKERS = [
    "كتب هذا المقال:  فريق المحتوى الفني في ركن التطور",
    "كتب هذا المقال: فريق المحتوى الفني في ركن التطور",
    "آخر تحديث:  سبتمبر 2026",
    "آخر تحديث: سبتمبر 2026",
    "مراجعة:  فريق العمليات",
    "البحث عن",
    "يبدأ من فهم العَرَض",
    "نقدّم",
    "بأسلوب ميداني: وصف العَرَض، معاينة، ثم اتفاق على النطاق",
    "دليل شامل 2026",
    "شركة متخصصة تقدم خدمات عالية الجودة",
    "نضمن لك خدمة عالية الجودة بأسعار تنافسية",
    "الصفحة هذه مخصّصة",
]

ERROR_PATTERNS = [
    ("bad_phone", re.compile(r"0?1556644443|01556644443|0500000000|\{\{phone\}\}|\[phone\]|XXXXXX|رقم\s*الهاتف\s*هنا|05X{2,}", re.I)),
    ("uae_geo", re.compile(r"\b(دبي|أبوظبي|ابوظبي|الشارقة|عجمان|الإمارات|الامارات|UAE|Dubai|Abu Dhabi)\b")),
    ("placeholder", re.compile(r"\{[A-Z_]+\}|TODO|FIXME|lorem ipsum|نص تجريبي|اكتب هنا", re.I)),
    ("broken_shortcode", re.compile(r"\[post_call\]\[post_call\]|\[/?[a-z_]+_broken\]", re.I)),
    ("multi_h1", re.compile(r"<h1\b", re.I)),
    ("empty_img_alt_issue", re.compile(r"img\.youtube\.com/vi/الفيديو")),
]


def get(path: str):
    last = None
    for i in range(4):
        try:
            req = urllib.request.Request(BASE + path, headers=H)
            with urllib.request.urlopen(req, timeout=90) as resp:
                return dict(resp.headers), json.loads(resp.read().decode())
        except Exception as e:
            last = e
            time.sleep(1.1 * (i + 1))
    raise last


def strip_html(html: str) -> str:
    t = re.sub(r"<script[\s\S]*?</script>", " ", html or "", flags=re.I)
    t = re.sub(r"<style[\s\S]*?</style>", " ", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"&\w+;", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def ar_words(text: str) -> int:
    return len(re.findall(r"[\u0600-\u06FF]+", text or ""))


def en_words(text: str) -> int:
    return len(re.findall(r"[A-Za-z']+", text or ""))


def opener(text: str, n: int = 220) -> str:
    return re.sub(r"\s+", " ", text or "")[:n]


def city_from_slug(slug: str) -> str | None:
    s = (slug or "").lower()
    # longest match wins
    best = None
    bl = 0
    for tok in TARGET_CITIES:
        if s.endswith("-" + tok) or s.endswith("/" + tok) or s == tok or f"-{tok}-" in s:
            if len(tok) >= bl:
                best = tok
                bl = len(tok)
    return best


def service_family(slug: str, title: str = "") -> str | None:
    s = f"{slug} {title}".lower()
    best = None
    bl = 0
    for fam, conf in CORE_SERVICES.items():
        for tok in conf["tokens"]:
            if tok.lower() in s and len(tok) >= bl:
                best = fam
                bl = len(tok)
    return best


def template_score(plain: str, raw: str) -> tuple[int, list[str]]:
    hits = []
    for m in TEMPLATE_MARKERS:
        if m in plain or m in raw:
            hits.append(m[:40])
    return len(hits), hits


def fetch_all_posts():
    items = []
    page = 1
    while True:
        hdr, posts = get(
            f"/wp/v2/posts?per_page=100&page={page}&status=publish,draft,future&context=edit&orderby=id&order=asc"
            f"&_fields=id,title,slug,status,link,content,excerpt,date,modified,meta"
        )
        if not posts:
            break
        items.extend(posts)
        print(f"posts page {page}/{hdr.get('X-WP-TotalPages')} n={len(items)}", flush=True)
        if page >= int(hdr.get("X-WP-TotalPages", page)):
            break
        page += 1
    return items


def fetch_pages():
    hdr, pages = get("/wp/v2/pages?per_page=100&status=publish&context=edit&_fields=id,title,slug,link,content,status")
    return pages


def fetch_services_cpt():
    try:
        hdr, items = get("/wp/v2/services?per_page=100&status=publish&context=edit&_fields=id,title,slug,link,content,status")
        return items
    except Exception as e:
        print("services CPT err", e, flush=True)
        return []


def analyze_posts(posts: list[dict]) -> dict:
    thin = []
    templates = []
    mismatches = []
    errors = []
    missing_call = []
    short_excerpt = []
    en_posts = []
    title_map = defaultdict(list)
    hash_map = defaultdict(list)
    opener_map = defaultdict(list)
    structure_map = defaultdict(list)
    coverage = defaultdict(set)  # fam -> set of city keys
    by_status = Counter()
    word_buckets = Counter()
    records = []

    for p in posts:
        by_status[p.get("status") or "?"] += 1
        title = (p.get("title") or {}).get("raw") or ""
        slug = p.get("slug") or ""
        raw = (p.get("content") or {}).get("raw") or ""
        plain = strip_html(raw)
        aw = ar_words(plain)
        ew = en_words(plain)
        excerpt = strip_html((p.get("excerpt") or {}).get("raw") or "")
        is_en = slug.startswith("en-") or (ew > aw and ew >= 80)
        city = city_from_slug(slug)
        fam = service_family(slug, title)
        words = ew if is_en else aw

        if fam and city and p.get("status") == "publish" and not is_en:
            coverage[fam].add(city)

        title_map[title.strip().lower()].append({"id": p["id"], "slug": slug, "status": p.get("status")})
        if len(plain) > 80:
            h = hashlib.sha1(plain.encode()).hexdigest()
            hash_map[h].append({"id": p["id"], "slug": slug, "title": title[:60], "status": p.get("status")})
            op = opener(plain)
            opener_map[op].append({"id": p["id"], "slug": slug, "title": title[:60], "status": p.get("status"), "aw": aw})

        # structural template fingerprint: sequence of h2 headings
        heads = re.findall(r"<h2[^>]*>(.*?)</h2>", raw, flags=re.I | re.S)
        heads_plain = [re.sub(r"\s+", " ", strip_html(h))[:40] for h in heads]
        if len(heads_plain) >= 3:
            fp = " | ".join(heads_plain[:6])
            structure_map[fp].append({"id": p["id"], "slug": slug, "title": title[:50], "status": p.get("status")})

        ts, thits = template_score(plain, raw)
        if ts >= 3 and p.get("status") == "publish":
            templates.append({"id": p["id"], "slug": slug, "title": title[:70], "score": ts, "hits": thits, "aw": aw})

        if is_en:
            en_posts.append({"id": p["id"], "slug": slug, "title": title[:70], "ew": ew, "aw": aw, "status": p.get("status")})
            if ew < 1000 and p.get("status") == "publish":
                thin.append({"id": p["id"], "slug": slug, "title": title[:70], "words": ew, "lang": "en", "status": p.get("status")})
        else:
            if p.get("status") == "publish":
                if aw < 700:
                    word_buckets["ar_lt_700"] += 1
                elif aw < 1000:
                    word_buckets["ar_700_999"] += 1
                elif aw < 1200:
                    word_buckets["ar_1000_1199"] += 1
                else:
                    word_buckets["ar_ge_1200"] += 1
                if aw < 1000:
                    thin.append({"id": p["id"], "slug": slug, "title": title[:70], "words": aw, "lang": "ar", "city": city, "fam": fam, "status": p.get("status")})

        # mismatch: topic keywords weak vs foreign family strong
        if fam and not is_en and p.get("status") == "publish" and aw >= 200:
            scores = {f: len(re.findall(CORE_SERVICES[f]["topic"], plain)) for f in CORE_SERVICES}
            own = scores.get(fam, 0)
            other = sorted([(f, c) for f, c in scores.items() if f != fam], key=lambda x: -x[1])
            top = other[0] if other else ("", 0)
            if (own < 5 and top[1] >= 8) or (own < 8 and top[1] >= max(12, own * 2)):
                mismatches.append(
                    {
                        "id": p["id"],
                        "slug": slug,
                        "title": title[:70],
                        "fam": fam,
                        "own": own,
                        "dom": top,
                        "scores": scores,
                        "aw": aw,
                    }
                )

        # errors / deficiencies
        err_hits = []
        for code, pat in ERROR_PATTERNS:
            if code == "multi_h1":
                if len(pat.findall(raw)) >= 1:
                    # content H1 is usually bad (theme already has H1)
                    err_hits.append(code)
            elif pat.search(plain) or pat.search(raw) or pat.search(title):
                err_hits.append(code)
        if "[post_call]" not in raw and p.get("status") == "publish":
            missing_call.append({"id": p["id"], "slug": slug, "title": title[:60]})
            err_hits.append("no_post_call")
        if len(excerpt) < 40 and p.get("status") == "publish":
            short_excerpt.append(p["id"])
            err_hits.append("short_excerpt")
        if err_hits and p.get("status") == "publish":
            errors.append({"id": p["id"], "slug": slug, "title": title[:70], "errors": err_hits, "aw": aw})

        records.append(
            {
                "id": p["id"],
                "slug": slug,
                "title": title,
                "status": p.get("status"),
                "aw": aw,
                "ew": ew,
                "words": words,
                "city": city,
                "fam": fam,
                "is_en": is_en,
                "link": p.get("link"),
                "template_score": ts,
            }
        )

    # near duplicates by opener
    near = [{"n": len(v), "fp": k[:120], "items": v} for k, v in opener_map.items() if len(v) > 1]
    near.sort(key=lambda x: -x["n"])

    # similar by pairwise opener ratio within same family (sample heavy groups)
    similar_groups = []
    by_fam_city = defaultdict(list)
    for r in records:
        if r["status"] != "publish" or r["is_en"]:
            continue
        if r["fam"]:
            by_fam_city[r["fam"]].append(r)
    # use opener groups already; also structure template clones
    struct_clones = [{"n": len(v), "fp": k, "items": v} for k, v in structure_map.items() if len(v) >= 5]
    struct_clones.sort(key=lambda x: -x["n"])

    exact = [{"n": len(v), "items": v} for v in hash_map.values() if len(v) > 1]
    exact.sort(key=lambda x: -x["n"])

    dup_titles = [{"title": k, "items": v} for k, v in title_map.items() if k and len(v) > 1]
    pub_dup_titles = []
    for d in dup_titles:
        pubs = [x for x in d["items"] if x["status"] == "publish"]
        if len(pubs) > 1:
            pub_dup_titles.append({"title": d["title"], "items": pubs})

    thin.sort(key=lambda x: x["words"])
    templates.sort(key=lambda x: -x["score"])
    mismatches.sort(key=lambda x: (-x["dom"][1], x["own"]))

    return {
        "checked": len(posts),
        "by_status": dict(by_status),
        "word_buckets": dict(word_buckets),
        "thin_lt_1000": thin,
        "thin_count": len(thin),
        "template_posts": templates,
        "template_count": len(templates),
        "exact_content_dups": exact[:40],
        "exact_content_dup_count": len(exact),
        "near_openers": near[:40],
        "near_opener_count": len(near),
        "structure_clones": struct_clones[:30],
        "structure_clone_count": len(struct_clones),
        "dup_titles_all": len(dup_titles),
        "publish_dup_titles": pub_dup_titles,
        "publish_dup_title_count": len(pub_dup_titles),
        "mismatches": mismatches,
        "mismatch_count": len(mismatches),
        "mismatch_by_fam": dict(Counter(m["fam"] for m in mismatches)),
        "errors": errors[:80],
        "error_count": len(errors),
        "error_by_code": dict(Counter(e for row in errors for e in row["errors"])),
        "missing_post_call": missing_call,
        "short_excerpt_count": len(short_excerpt),
        "en_posts": en_posts,
        "coverage": {k: sorted(v) for k, v in coverage.items()},
        "records_sample": records[:5],
        "_records": records,  # internal for coverage matrix
    }


def coverage_gaps(analysis: dict) -> dict:
    records = analysis.get("_records") or []
    # published AR posts mapping
    present = defaultdict(set)
    for r in records:
        if r["status"] != "publish" or r["is_en"]:
            continue
        if r["fam"] and r["city"]:
            present[r["fam"]].add(r["city"])

    # normalize city aliases to canonical arabic name keys
    alias_to_canon = {}
    for tok, ar in TARGET_CITIES.items():
        alias_to_canon[tok] = ar

    # focus matrix on 8 core metros + extended
    core_metro = ["riyadh", "jeddah", "mecca", "medina", "dammam", "khobar", "taif", "abha"]
    extended = [
        "tabuk",
        "buraidah",
        "khamis-mushait",
        "najran",
        "jazan",
        "yanbu",
        "jubail",
        "ahsa",
        "hail",
        "khafji",
        "qatif",
        "dhahran",
        "hafar-albatin",
        "kharj",
        "baha",
    ]

    gaps = {}
    for fam, conf in CORE_SERVICES.items():
        have = present.get(fam, set())
        miss_core = [c for c in core_metro if c not in have and not any(alias_to_canon.get(c) == alias_to_canon.get(h) for h in have)]
        # handle mecca/makkah alias
        def has_city(c):
            if c in have:
                return True
            ar = alias_to_canon.get(c)
            for h in have:
                if alias_to_canon.get(h) == ar:
                    return True
            return False

        miss_core = [c for c in core_metro if not has_city(c)]
        miss_ext = [c for c in extended if not has_city(c)]
        gaps[fam] = {
            "service": conf["ar"],
            "have_cities": sorted(have),
            "have_count": len(have),
            "missing_core8": miss_core,
            "missing_extended": miss_ext,
        }

    # cities pages
    return gaps


def analyze_hubs(pages, services):
    hubs = []
    for p in pages:
        plain = strip_html((p.get("content") or {}).get("raw") or "")
        aw = ar_words(plain)
        hubs.append({"type": "page", "id": p["id"], "slug": p.get("slug"), "title": (p.get("title") or {}).get("raw"), "aw": aw, "link": p.get("link")})
    for p in services:
        plain = strip_html((p.get("content") or {}).get("raw") or "")
        aw = ar_words(plain)
        hubs.append({"type": "service", "id": p["id"], "slug": p.get("slug"), "title": (p.get("title") or {}).get("raw"), "aw": aw, "link": p.get("link")})
    thin_hubs = [h for h in hubs if h["aw"] < 500]
    return {"hubs": hubs, "thin_hubs": thin_hubs}


def write_report(out: dict):
    thin = out["thin_lt_1000"]
    gaps = out["coverage_gaps"]
    lines = []
    lines.append("# فحص جودة المحتوى والتغطية — 4 أكتوبر 2026")
    lines.append("")
    lines.append(f"**الموقع:** https://www.rukn-eltatawer.com/sa  ")
    lines.append(f"**وقت الفحص:** {out['at']}  ")
    lines.append(f"**المفحوص:** {out['checked']} مقالاً (publish/draft/future) + صفحات وخدمات CPT")
    lines.append("")
    lines.append("## الحكم السريع")
    lines.append("")
    lines.append(f"| المؤشر | العدد |")
    lines.append(f"|--------|------|")
    lines.append(f"| منشور / مسودة / مجدول | {out['by_status'].get('publish',0)} / {out['by_status'].get('draft',0)} / {out['by_status'].get('future',0)} |")
    lines.append(f"| مقالات < 1000 كلمة (منشورة) | **{out['thin_count']}** |")
    lines.append(f"| مقالات بنفس القالب (علامات ≥3) | **{out['template_count']}** |")
    lines.append(f"| تكرار محتوى حرفي | {out['exact_content_dup_count']} |")
    lines.append(f"| تكرار افتتاحية متشابهة | {out['near_opener_count']} |")
    lines.append(f"| قوالب عناوين H2 متطابقة (≥5 مقالات) | {out['structure_clone_count']} |")
    lines.append(f"| عناوين مكررة منشورة | {out['publish_dup_title_count']} |")
    lines.append(f"| عدم تطابق موضوع/خدمة | **{out['mismatch_count']}** |")
    lines.append(f"| مقالات بأخطاء/نواقص | **{out['error_count']}** |")
    lines.append("")
    lines.append("### توزيع الكلمات (عربي منشور)")
    lines.append("")
    wb = out.get("word_buckets") or {}
    lines.append(f"- أقل من 700: {wb.get('ar_lt_700',0)}")
    lines.append(f"- 700–999: {wb.get('ar_700_999',0)}")
    lines.append(f"- 1000–1199: {wb.get('ar_1000_1199',0)}")
    lines.append(f"- ≥1200: {wb.get('ar_ge_1200',0)}")
    lines.append("")

    lines.append("## 1) مقالات أقل من 1000 كلمة")
    lines.append("")
    lines.append(f"الإجمالي: **{out['thin_count']}** مقالاً منشوراً.")
    lines.append("")
    # group by fam
    byf = Counter((t.get("fam") or "other") for t in thin if t.get("lang") == "ar")
    lines.append("حسب العائلة: " + ", ".join(f"{k}={v}" for k, v in byf.most_common()))
    lines.append("")
    lines.append("| ID | الكلمات | العائلة | المدينة | العنوان |")
    lines.append("|----|---------|---------|---------|---------|")
    for t in thin[:80]:
        lines.append(f"| {t['id']} | {t['words']} | {t.get('fam') or t.get('lang')} | {t.get('city') or '-'} | {t['title'][:50]} |")
    if len(thin) > 80:
        lines.append(f"| … | | | | +{len(thin)-80} أخرى في JSON |")
    lines.append("")

    lines.append("## 2) مقالات مكتوبة بنفس القالب")
    lines.append("")
    lines.append(f"عدد المقالات بعلامات القالب المتكرر (≥3): **{out['template_count']}**")
    lines.append("")
    lines.append("أبرز علامات القالب: بطاقة المؤلف/سبتمبر 2026، «يبدأ من فهم العَرَض»، «بأسلوب ميداني: وصف العَرَض…».")
    lines.append("")
    lines.append(f"مجموعات هيكل H2 متطابق (≥5 مقالات): **{out['structure_clone_count']}**")
    lines.append("")
    for g in out["structure_clones"][:8]:
        lines.append(f"- **{g['n']} مقالات** — هيكل: `{g['fp'][:100]}`")
        sample = ", ".join(f"{i['id']}:{i['slug'][:30]}" for i in g["items"][:5])
        lines.append(f"  - عيّنة: {sample}")
    lines.append("")

    lines.append("## 3) مقالات متشابهة / مكررة")
    lines.append("")
    lines.append(f"- تكرار محتوى حرفي: **{out['exact_content_dup_count']}**")
    lines.append(f"- افتتاحيات متطابقة: **{out['near_opener_count']}**")
    lines.append(f"- عناوين مكررة (منشورة): **{out['publish_dup_title_count']}**")
    lines.append("")
    if out["publish_dup_titles"]:
        lines.append("### عناوين مكررة حية")
        for d in out["publish_dup_titles"][:20]:
            ids = ", ".join(f"{x['id']}({x['slug'][:28]})" for x in d["items"])
            lines.append(f"- `{d['title'][:60]}` → {ids}")
        lines.append("")
    if out["near_openers"]:
        lines.append("### أكبر مجموعات الافتتاحية المتشابهة")
        for g in out["near_openers"][:10]:
            lines.append(f"- **{g['n']}** — `{g['fp'][:90]}…`")
            lines.append("  - " + ", ".join(f"{i['id']}:{i['slug'][:25]}" for i in g["items"][:6]))
        lines.append("")

    lines.append("## 4) محتوى لا يتناسب مع الموضوع/الخدمة")
    lines.append("")
    lines.append(f"الإجمالي: **{out['mismatch_count']}**")
    if out.get("mismatch_by_fam"):
        lines.append("حسب العائلة: " + ", ".join(f"{k}={v}" for k, v in out["mismatch_by_fam"].items()))
    lines.append("")
    lines.append("| ID | المتوقع | الغالب | own/dom | العنوان |")
    lines.append("|----|---------|--------|---------|---------|")
    for m in out["mismatches"][:40]:
        lines.append(
            f"| {m['id']} | {m['fam']} | {m['dom'][0]} ({m['dom'][1]}) | {m['own']}/{m['dom'][1]} | {m['title'][:45]} |"
        )
    lines.append("")

    lines.append("## 5) أخطاء ونواقص")
    lines.append("")
    lines.append(f"مقالات بها إشارة خطأ/نقص: **{out['error_count']}**")
    lines.append("توزيع الأكواد: " + ", ".join(f"{k}={v}" for k, v in (out.get("error_by_code") or {}).items()))
    lines.append("")
    lines.append(f"- بدون `[post_call]`: {len(out.get('missing_post_call') or [])}")
    lines.append(f"- مقتطف قصير: {out.get('short_excerpt_count', 0)}")
    lines.append("")
    for e in out["errors"][:25]:
        lines.append(f"- `{e['id']}` {e['slug'][:40]} — {', '.join(e['errors'])}")
    lines.append("")

    lines.append("## 6) نواقص التغطية — خدمات × مدن السعودية")
    lines.append("")
    lines.append("المصفوفة على 8 مدن أساسية + مدن ممتدة شائعة.")
    lines.append("")
    for fam, g in gaps.items():
        lines.append(f"### {g['service']} (`{fam}`)")
        lines.append(f"- مدن متوفرة: **{g['have_count']}** — {', '.join(g['have_cities'][:20])}")
        lines.append(f"- ناقص من الأساسية (8): {', '.join(g['missing_core8']) if g['missing_core8'] else 'لا يوجد ✅'}")
        miss = g["missing_extended"]
        lines.append(f"- ناقص ممتد (عيّنة): {', '.join(miss[:12]) if miss else '—'}" + (f" (+{len(miss)-12})" if len(miss) > 12 else ""))
        lines.append("")

    # city hubs
    lines.append("### صفحات المدن / الخدمات الأساسية")
    lines.append("")
    for h in out.get("thin_hubs") or []:
        lines.append(f"- [{h['type']}] `{h['id']}` {h['slug']} — {h['aw']} كلمة — {h['title']}")
    lines.append("")

    lines.append("## أولويات مقترحة")
    lines.append("")
    lines.append("1. إغناء كل منشور <1000 كلمة (خصوصاً الشحن/الدكتات/غسيل المكيفات إن بقيت).")
    lines.append("2. كسر القالب المتكرر: افتتاحية + H2 مختلفة لكل مدينة/خدمة.")
    lines.append("3. إعادة كتابة mismatches (عزل/نقل/سباكة) لتطابق الكلمات المفتاحية للخدمة.")
    lines.append("4. سد فجوات المدن الممتدة للخدمات الأساسية (تبوك، القصيم، جازان، الأحساء…).")
    lines.append("5. إصلاح نواقص `[post_call]` والمقتطفات القصيرة والأخطاء الظاهرة.")
    lines.append("")
    lines.append("الملفات التفصيلية: `data/content-quality-coverage-2026-10-04.json`")
    lines.append("")

    path = REPORTS / "content-quality-coverage-2026-10-04.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main():
    print("=== fetch posts ===", flush=True)
    posts = fetch_all_posts()
    print("=== analyze posts ===", flush=True)
    analysis = analyze_posts(posts)
    print("=== fetch hubs ===", flush=True)
    pages = fetch_pages()
    services = fetch_services_cpt()
    hubs = analyze_hubs(pages, services)
    gaps = coverage_gaps(analysis)

    out = {
        "at": datetime.now(timezone.utc).isoformat(),
        "checked": analysis["checked"],
        "by_status": analysis["by_status"],
        "word_buckets": analysis["word_buckets"],
        "thin_count": analysis["thin_count"],
        "thin_lt_1000": analysis["thin_lt_1000"],
        "template_count": analysis["template_count"],
        "template_posts": analysis["template_posts"][:100],
        "exact_content_dup_count": analysis["exact_content_dup_count"],
        "exact_content_dups": analysis["exact_content_dups"],
        "near_opener_count": analysis["near_opener_count"],
        "near_openers": analysis["near_openers"],
        "structure_clone_count": analysis["structure_clone_count"],
        "structure_clones": analysis["structure_clones"],
        "publish_dup_title_count": analysis["publish_dup_title_count"],
        "publish_dup_titles": analysis["publish_dup_titles"],
        "mismatch_count": analysis["mismatch_count"],
        "mismatch_by_fam": analysis["mismatch_by_fam"],
        "mismatches": analysis["mismatches"],
        "error_count": analysis["error_count"],
        "error_by_code": analysis["error_by_code"],
        "errors": analysis["errors"],
        "missing_post_call": analysis["missing_post_call"],
        "short_excerpt_count": analysis["short_excerpt_count"],
        "en_posts": analysis["en_posts"],
        "coverage": analysis["coverage"],
        "coverage_gaps": gaps,
        "thin_hubs": hubs["thin_hubs"],
        "hubs": hubs["hubs"],
    }

    json_path = DATA / "content-quality-coverage-2026-10-04.json"
    # compact: drop huge if needed — keep full thin list
    json_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    report_path = write_report(out)
    print("WROTE", json_path, flush=True)
    print("WROTE", report_path, flush=True)
    print(
        "SUMMARY",
        json.dumps(
            {
                "checked": out["checked"],
                "thin": out["thin_count"],
                "template": out["template_count"],
                "near": out["near_opener_count"],
                "mismatch": out["mismatch_count"],
                "errors": out["error_count"],
                "pub_dup_titles": out["publish_dup_title_count"],
            },
            ensure_ascii=False,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
