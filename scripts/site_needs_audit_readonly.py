#!/usr/bin/env python3
"""READ-ONLY site needs audit for rukn-eltatawer.com/sa — no writes/updates."""

from __future__ import annotations

import base64
import hashlib
import json
import re
import time
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://www.rukn-eltatawer.com/sa/wp-json"
AUTH = base64.b64encode(b"cursor:PCkk ig95 Gu6c zOgC GLYG FYsk").decode()
H = {"Authorization": f"Basic {AUTH}", "User-Agent": "Mozilla/5.0 RuknNeedsAuditRO/2026-11-03"}
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
DATA.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)

# Expected Saudi coverage
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
    "najran": "نجران",
    "jazan": "جازان",
    "yanbu": "ينبع",
    "jubail": "الجبيل",
    "ahsa": "الأحساء",
    "alhasa": "الأحساء",
    "hofuf": "الهفوف",
    "hail": "حائل",
    "khafji": "الخفجي",
    "qatif": "القطيف",
    "dhahran": "الظهران",
    "hafar-albatin": "حفر الباطن",
    "kharj": "الخرج",
    "baha": "الباحة",
    "albaha": "الباحة",
    "sakaka": "سكاكا",
    "arar": "عرعر",
    "unaizah": "عنيزة",
    "najran": "نجران",
}

CORE8 = ["riyadh", "jeddah", "mecca", "medina", "dammam", "khobar", "taif", "abha"]
EXTENDED = [
    "tabuk", "buraidah", "khamis-mushait", "najran", "jazan", "yanbu", "jubail",
    "ahsa", "hail", "khafji", "qatif", "dhahran", "hafar-albatin", "kharj", "baha",
]

SERVICES = {
    "leak": {"ar": "كشف تسربات المياه", "tokens": ["leak", "water-leak", "pipe-leak", "تسرب"], "topic": r"تسرب|كشف تسرب|رطوبة|فاتورة مياه"},
    "insul": {"ar": "عزل أسطح/خزانات", "tokens": ["insulation", "waterproof", "roof-insul", "tank-insul", "عزل"], "topic": r"عزل|عازل|مواد عزل|عزل مائي|عزل حراري"},
    "ac": {"ar": "تكييف/غسيل مكيفات", "tokens": ["ac-", "ac-cleaning", "split-ac", "duct", "central-ac", "مكيف"], "topic": r"تكييف|مكيف|فريون|دكت|سبليت|غسيل مكيف"},
    "clean": {"ar": "تنظيف", "tokens": ["cleaning", "sofa", "carpet", "steriliz", "تنظيف"], "topic": r"تنظيف|غسيل كنب|سجاد|تعقيم|جلي"},
    "pest": {"ar": "مكافحة حشرات", "tokens": ["pest", "termite", "cockroach", "ant-control", "bed-bug", "rodent", "مكافحة"], "topic": r"مكافحة|حشرات|نمل|صراصير|بق|فئران|مبيد"},
    "plumb": {"ar": "سباكة", "tokens": ["plumb", "sewer", "plumber", "سباك"], "topic": r"سباكة|سباك|انسداد|صرف"},
    "elec": {"ar": "كهرباء", "tokens": ["electric", "electrician", "كهرب"], "topic": r"كهرباء|كهربائي|قواطع|إنارة"},
    "grass": {"ar": "عشب صناعي", "tokens": ["grass", "artificial-grass", "wall-grass", "عشب"], "topic": r"عشب|نجيلة|جداري"},
    "move": {"ar": "نقل/شحن", "tokens": ["moving", "shipping", "furniture-mov", "نقل", "شحن"], "topic": r"نقل عفش|تغليف|شاحنة|شحن أثاث|شحن سيارات|بيانو"},
}

TEMPLATE_STRONG = [
    "فريق المحتوى الفني",
    "يبدأ من فهم العَرَض",
    "يبدأ من فهم العرض",
    "بأسلوب ميداني",
    "الهدف أن تعرف قبل البدء",
]

ERROR_PATS = [
    ("bad_phone", re.compile(r"0?1556644443|01556644443|0500000000|\{\{phone\}\}|\[phone\]|XXXXXX|رقم\s*الهاتف\s*هنا|05X{2,}", re.I)),
    ("uae_geo", re.compile(r"\b(دبي|أبوظبي|ابوظبي|الشارقة|عجمان|الإمارات(?!\s*العربية\s*المتحدة\s*قد)|UAE|Dubai|Abu Dhabi)\b")),
    ("placeholder", re.compile(r"\{[A-Z_]{3,}\}|TODO|FIXME|lorem ipsum|نص تجريبي|اكتب هنا", re.I)),
    ("polluted_title_phone", re.compile(r"01151481000|الإعلان للإيجار")),
    ("multi_h1", re.compile(r"<h1\b", re.I)),
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


def ar_words(t: str) -> int:
    return len(re.findall(r"[\u0600-\u06FF]+", t or ""))


def en_words(t: str) -> int:
    return len(re.findall(r"[A-Za-z']+", t or ""))


def city_from_slug(slug: str) -> str | None:
    s = (slug or "").lower()
    best, bl = None, 0
    for tok in TARGET_CITIES:
        if s == tok or s.endswith("-" + tok) or f"-{tok}-" in s or s.endswith("/" + tok):
            if len(tok) >= bl:
                best, bl = tok, len(tok)
    return best


def fam_from_slug(slug: str, title: str = "") -> str | None:
    s = f"{slug} {title}".lower()
    best, bl = None, 0
    for fam, conf in SERVICES.items():
        for tok in conf["tokens"]:
            if tok.lower() in s and len(tok) >= bl:
                best, bl = fam, len(tok)
    return best


def canon_city(tok: str | None) -> str | None:
    if not tok:
        return None
    return TARGET_CITIES.get(tok, tok)


def fetch_all(endpoint: str, statuses: str = "publish,draft,future"):
    items = []
    page = 1
    while True:
        path = (
            f"/wp/v2/{endpoint}?per_page=100&page={page}&status={statuses}"
            f"&context=edit&orderby=id&order=asc"
            f"&_fields=id,title,slug,status,link,content,excerpt,date,modified,meta,parent"
        )
        try:
            hdr, batch = get(path)
        except Exception as e:
            if page == 1:
                print(f"{endpoint} fetch err", e, flush=True)
                return []
            break
        if not batch:
            break
        items.extend(batch)
        total_pages = int(hdr.get("X-WP-TotalPages", page))
        print(f"{endpoint} page {page}/{total_pages} n={len(items)}", flush=True)
        if page >= total_pages:
            break
        page += 1
    return items


def analyze_posts(posts: list[dict]) -> dict:
    thin, templates, mismatches, errors = [], [], [], []
    missing_call, short_excerpt, en_posts = [], [], []
    needs_update = []
    title_map = defaultdict(list)
    opener_map = defaultdict(list)
    hash_map = defaultdict(list)
    coverage = defaultdict(set)
    by_status = Counter()
    word_buckets = Counter()
    city_norm_clusters = defaultdict(list)
    polluted_titles = []
    records = []

    CITY_AR_LIST = list(set(TARGET_CITIES.values())) + ["مكة", "المدينة"]

    for p in posts:
        by_status[p.get("status") or "?"] += 1
        title = (p.get("title") or {}).get("raw") or ""
        slug = p.get("slug") or ""
        raw = (p.get("content") or {}).get("raw") or ""
        plain = strip_html(raw)
        excerpt = strip_html((p.get("excerpt") or {}).get("raw") or "")
        aw, ew = ar_words(plain), en_words(plain)
        is_en = slug.startswith("en-") or (ew > aw and ew >= 80)
        city = city_from_slug(slug)
        fam = fam_from_slug(slug, title)
        words = ew if is_en else aw
        status = p.get("status")
        meta = p.get("meta") or {}
        rm_title = meta.get("rank_math_title") if isinstance(meta, dict) else None
        robots = meta.get("rank_math_robots") if isinstance(meta, dict) else None

        if fam and city and status == "publish" and not is_en:
            coverage[fam].add(city)

        title_map[title.strip().lower()].append({"id": p["id"], "slug": slug, "status": status})
        if len(plain) > 80 and status == "publish":
            h = hashlib.sha1(plain.encode()).hexdigest()
            hash_map[h].append({"id": p["id"], "slug": slug, "title": title[:55]})
            op = re.sub(r"\s+", " ", plain)[:220]
            opener_map[op].append({"id": p["id"], "slug": slug, "title": title[:55]})
            # city-normalized opener
            t = op
            for c in CITY_AR_LIST:
                t = t.replace(c, "CITY")
            t = re.sub(r"\s+", " ", t)[:130]
            city_norm_clusters[t].append({"id": p["id"], "slug": slug, "title": title[:50], "fam": fam})

        # thin
        if status == "publish":
            if is_en:
                en_posts.append({"id": p["id"], "slug": slug, "title": title[:70], "ew": ew, "aw": aw})
                if ew < 1000:
                    thin.append({"id": p["id"], "slug": slug, "title": title[:70], "words": ew, "lang": "en", "city": city, "fam": fam})
            else:
                if aw < 700:
                    word_buckets["ar_lt_700"] += 1
                elif aw < 1000:
                    word_buckets["ar_700_999"] += 1
                elif aw < 1200:
                    word_buckets["ar_1000_1199"] += 1
                else:
                    word_buckets["ar_ge_1200"] += 1
                if aw < 1000:
                    thin.append({"id": p["id"], "slug": slug, "title": title[:70], "words": aw, "lang": "ar", "city": city, "fam": fam})

        # strong template
        thits = [m for m in TEMPLATE_STRONG if m in plain]
        if status == "publish" and len(thits) >= 3:
            templates.append({"id": p["id"], "slug": slug, "title": title[:60], "hits": len(thits), "aw": aw})

        # mismatch
        if fam and not is_en and status == "publish" and aw >= 150:
            scores = {f: len(re.findall(SERVICES[f]["topic"], plain)) for f in SERVICES}
            own = scores.get(fam, 0)
            other = sorted([(f, c) for f, c in scores.items() if f != fam], key=lambda x: -x[1])
            top = other[0] if other else ("", 0)
            if (own <= 3 and top[1] >= 6) or (top[1] >= max(8, own * 3)):
                mismatches.append({"id": p["id"], "slug": slug, "title": title[:60], "fam": fam, "own": own, "dom": list(top), "scores": scores, "aw": aw})

        # errors
        err = []
        for code, pat in ERROR_PATS:
            if code == "multi_h1":
                if len(pat.findall(raw)) >= 1:
                    err.append(code)
            elif code == "polluted_title_phone":
                if pat.search(title) or (isinstance(rm_title, str) and pat.search(rm_title)):
                    err.append(code)
                    polluted_titles.append({"id": p["id"], "slug": slug, "title": title[:80], "rm_title": (rm_title[:80] if isinstance(rm_title, str) else None)})
            elif pat.search(plain) or pat.search(raw) or pat.search(title):
                err.append(code)
        if status == "publish" and "[post_call]" not in raw:
            missing_call.append({"id": p["id"], "slug": slug, "title": title[:55]})
            err.append("no_post_call")
        if status == "publish" and len(excerpt) < 40:
            short_excerpt.append(p["id"])
            err.append("short_excerpt")
        if isinstance(robots, list) and "noindex" in robots and status == "publish":
            err.append("noindex")
        if err and status == "publish":
            errors.append({"id": p["id"], "slug": slug, "title": title[:60], "errors": err, "aw": aw})

        # needs update heuristics
        reasons = []
        if status == "publish" and not is_en and aw < 1000:
            reasons.append("thin_lt_1000")
        if status == "publish" and len(thits) >= 3:
            reasons.append("template_heavy")
        if status == "publish" and fam and any(m["id"] == p["id"] for m in mismatches[-1:]):
            pass
        # stale marker without 2026 refresh note when thin
        if status == "publish" and aw < 900:
            reasons.append("priority_refresh")
        if "سبتمبر 2025" in plain or "2024" in plain[:400]:
            reasons.append("possibly_outdated_date")
        if reasons and status == "publish":
            needs_update.append({"id": p["id"], "slug": slug, "title": title[:60], "reasons": reasons, "aw": aw if not is_en else ew, "lang": "en" if is_en else "ar"})

        records.append({
            "id": p["id"], "slug": slug, "title": title, "status": status,
            "aw": aw, "ew": ew, "city": city, "fam": fam, "is_en": is_en, "link": p.get("link"),
        })

    # mark mismatches into needs_update
    mism_ids = {m["id"] for m in mismatches}
    for row in needs_update:
        if row["id"] in mism_ids and "mismatch" not in row["reasons"]:
            row["reasons"].append("mismatch")

    near = [{"n": len(v), "fp": k[:120], "items": v[:10]} for k, v in opener_map.items() if len(v) > 1]
    near.sort(key=lambda x: -x["n"])
    exact = [{"n": len(v), "items": v} for v in hash_map.values() if len(v) > 1]
    exact.sort(key=lambda x: -x["n"])
    city_clusters = [{"n": len(v), "fp": k, "items": v[:12]} for k, v in city_norm_clusters.items() if len(v) >= 4]
    city_clusters.sort(key=lambda x: -x["n"])

    pub_dup_titles = []
    for k, v in title_map.items():
        pubs = [x for x in v if x["status"] == "publish"]
        if k and len(pubs) > 1:
            pub_dup_titles.append({"title": k[:80], "items": pubs})

    thin.sort(key=lambda x: x["words"])
    mismatches.sort(key=lambda x: (-x["dom"][1], x["own"]))
    templates.sort(key=lambda x: -x["hits"])

    return {
        "checked": len(posts),
        "by_status": dict(by_status),
        "word_buckets": dict(word_buckets),
        "thin_lt_1000": thin,
        "thin_count": len(thin),
        "template_strong_count": len(templates),
        "template_strong_sample": templates[:60],
        "exact_dup_count": len(exact),
        "exact_dups": exact[:20],
        "near_opener_count": len(near),
        "near_openers": near[:20],
        "city_swap_cluster_count": len(city_clusters),
        "city_swap_clusters": city_clusters[:30],
        "publish_dup_title_count": len(pub_dup_titles),
        "publish_dup_titles": pub_dup_titles[:30],
        "mismatch_count": len(mismatches),
        "mismatch_by_fam": dict(Counter(m["fam"] for m in mismatches)),
        "mismatches": mismatches[:60],
        "error_count": len(errors),
        "error_by_code": dict(Counter(e for row in errors for e in row["errors"])),
        "errors_sample": errors[:50],
        "missing_post_call": missing_call[:40],
        "missing_post_call_count": len(missing_call),
        "short_excerpt_count": len(short_excerpt),
        "polluted_titles_count": len(polluted_titles),
        "polluted_titles_sample": polluted_titles[:30],
        "en_posts": en_posts,
        "needs_update_count": len(needs_update),
        "needs_update_sample": needs_update[:80],
        "coverage": {k: sorted(v) for k, v in coverage.items()},
        "_records": records,
    }


def coverage_gaps(analysis: dict) -> dict:
    present = defaultdict(set)
    for r in analysis.get("_records") or []:
        if r["status"] != "publish" or r["is_en"]:
            continue
        if r["fam"] and r["city"]:
            present[r["fam"]].add(r["city"])

    def has_city(have: set, c: str) -> bool:
        if c in have:
            return True
        ar = TARGET_CITIES.get(c)
        for h in have:
            if TARGET_CITIES.get(h) == ar:
                return True
        return False

    gaps = {}
    for fam, conf in SERVICES.items():
        have = present.get(fam, set())
        gaps[fam] = {
            "service": conf["ar"],
            "have_count": len(have),
            "have_cities": sorted(have),
            "missing_core8": [c for c in CORE8 if not has_city(have, c)],
            "missing_extended": [c for c in EXTENDED if not has_city(have, c)],
        }
    return gaps


def analyze_hubs(pages, services_cpt):
    hubs = []
    for kind, items in (("page", pages), ("service_cpt", services_cpt)):
        for p in items:
            plain = strip_html((p.get("content") or {}).get("raw") or "")
            aw = ar_words(plain)
            hubs.append({
                "type": kind,
                "id": p["id"],
                "slug": p.get("slug"),
                "title": (p.get("title") or {}).get("raw"),
                "aw": aw,
                "status": p.get("status"),
                "link": p.get("link"),
                "parent": p.get("parent"),
            })
    thin = [h for h in hubs if h["status"] == "publish" and h["aw"] < 500]
    city_pages = [h for h in hubs if h["type"] == "page" and (h.get("slug") in TARGET_CITIES or (h.get("link") or "").find("/cities/") >= 0)]
    return {"hubs": hubs, "thin_hubs": thin, "city_pages": city_pages}


def frontend_smoke() -> dict:
    samples = {}
    urls = [
        "https://www.rukn-eltatawer.com/sa/",
        "https://www.rukn-eltatawer.com/sa/cities/riyadh/",
        "https://www.rukn-eltatawer.com/sa/cities/tabuk/",
        "https://www.rukn-eltatawer.com/sa/water-leak-detection-riyadh/",
    ]
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": H["User-Agent"]})
            with urllib.request.urlopen(req, timeout=60) as resp:
                html = resp.read().decode("utf-8", "ignore")
            title_m = re.search(r"<title>([^<]+)</title>", html, re.I)
            samples[url] = {
                "status": getattr(resp, "status", 200),
                "wa": sorted(set(re.findall(r"wa\.me/(\d+)", html))),
                "tel": sorted(set(re.findall(r"tel:([+\d]+)", html))),
                "has_011": "01151481000" in html,
                "has_056": "0568060309" in html,
                "has_971": "971586634710" in html,
                "title": (title_m.group(1).strip()[:140] if title_m else None),
            }
        except Exception as e:
            samples[url] = {"error": str(e)}
    return samples


def missing_services_overall(records: list[dict]) -> dict:
    """Services that appear conceptually missing as site offerings (hub level)."""
    # Expected service hubs / categories
    expected_service_labels = {
        "leak": "كشف تسربات",
        "insul": "عزل",
        "ac": "تكييف/مكيفات",
        "clean": "تنظيف",
        "pest": "مكافحة",
        "plumb": "سباكة",
        "elec": "كهرباء",
        "grass": "عشب",
        "move": "نقل/شحن",
    }
    present_fams = set()
    for r in records:
        if r["status"] == "publish" and r.get("fam"):
            present_fams.add(r["fam"])
    missing_fams = [expected_service_labels[f] for f in expected_service_labels if f not in present_fams]

    # Additional desired niches often requested in KSA home services
    niche_patterns = {
        "camera_drain": r"كاميرا.*مجار|فحص مجاري",
        "tank_cleaning": r"تنظيف خزانات",
        "septic": r"بيارات|صرف صحي",
        "marble": r"جلي رخام|تلميع رخام",
        "curtain": r"تنظيف ستائر",
        "kitchen_hood": r"شفاط|تنظيف مداخن",
        "solar": r"ألواح شمسية|سخان شمسي",
        "generator": r"مولد كهرباء",
        "smart_home": r"منزل ذكي|سمارت هوم",
    }
    # scan titles/slugs only for niche presence among publish
    blob = " ".join(f"{r['slug']} {r['title']}" for r in records if r["status"] == "publish")
    niche_missing = []
    niche_present = []
    for k, pat in niche_patterns.items():
        if re.search(pat, blob, re.I):
            niche_present.append(k)
        else:
            niche_missing.append(k)
    return {
        "core_fams_present": sorted(present_fams),
        "core_fams_missing": missing_fams,
        "niche_present": niche_present,
        "niche_missing_suggested": niche_missing,
    }


def write_report(out: dict) -> Path:
    gaps = out["coverage_gaps"]
    thin = out["thin_lt_1000"]
    lines = []
    A = lines.append
    A("# فحص احتياجات الموقع (قراءة فقط) — 3 نوفمبر 2026")
    A("")
    A("**الموقع:** https://www.rukn-eltatawer.com/sa  ")
    A(f"**وقت الفحص (UTC):** {out['at']}  ")
    A("**الوضع:** فحص فقط — لم يُنفَّذ أي تعديل على المحتوى أو الإعدادات.")
    A("")
    A("## الخلاصة التنفيذية")
    A("")
    A("| المؤشر | القيمة |")
    A("|--------|--------|")
    A(f"| مقالات مفحوصة | {out['checked']} |")
    A(f"| منشور / مسودة / مجدول | {out['by_status'].get('publish',0)} / {out['by_status'].get('draft',0)} / {out['by_status'].get('future',0)} |")
    A(f"| مقالات < 1000 كلمة | **{out['thin_count']}** |")
    A(f"| قالب قوي متكرر | **{out['template_strong_count']}** |")
    A(f"| مجموعات متشابهة (city-swap) | **{out['city_swap_cluster_count']}** |")
    A(f"| عناوين مكررة منشورة | **{out['publish_dup_title_count']}** |")
    A(f"| محتوى لا يطابق الخدمة | **{out['mismatch_count']}** |")
    A(f"| مقالات بأخطاء/نواقص | **{out['error_count']}** |")
    A(f"| عناوين ملوّثة برقم/إعلان | **{out['polluted_titles_count']}** |")
    A(f"| يحتاج تحديث (إشارات) | **{out['needs_update_count']}** |")
    A("")
    wb = out.get("word_buckets") or {}
    A("### توزيع الكلمات (عربي منشور)")
    A(f"- <700: {wb.get('ar_lt_700',0)}")
    A(f"- 700–999: {wb.get('ar_700_999',0)}")
    A(f"- 1000–1199: {wb.get('ar_1000_1199',0)}")
    A(f"- ≥1200: {wb.get('ar_ge_1200',0)}")
    A("")
    A("---")
    A("")
    A("## 1) أخطاء ومشاكل تقنية/محتوى")
    A("")
    A(f"توزيع أكواد الأخطاء: {out.get('error_by_code')}")
    A("")
    A(f"- بدون `[post_call]`: {out.get('missing_post_call_count')}")
    A(f"- مقتطف قصير: {out.get('short_excerpt_count')}")
    A(f"- عناوين ملوّثة (`01151481000` / إعلان للإيجار): {out.get('polluted_titles_count')}")
    A("")
    A("### عيّنة أخطاء")
    for e in (out.get("errors_sample") or [])[:25]:
        A(f"- `{e['id']}` {e['slug'][:40]} — {', '.join(e['errors'])}")
    A("")
    if out.get("polluted_titles_sample"):
        A("### عيّنة عناوين ملوّثة")
        for t in out["polluted_titles_sample"][:15]:
            A(f"- `{t['id']}` {t['slug'][:35]} — {t['title'][:70]}")
        A("")
    A("### فحص واجهة سريع")
    for url, s in (out.get("frontend_smoke") or {}).items():
        A(f"- {url}: {s}")
    A("")
    A("---")
    A("")
    A("## 2) مقالات ناقصة المحتوى (<1000 كلمة)")
    A("")
    A(f"الإجمالي: **{out['thin_count']}**")
    A("")
    byf = Counter((t.get("fam") or t.get("lang") or "other") for t in thin)
    A("حسب العائلة: " + ", ".join(f"{k}={v}" for k, v in byf.most_common()))
    A("")
    A("| ID | كلمات | لغة/عائلة | مدينة | العنوان |")
    A("|----|-------|-----------|--------|---------|")
    for t in thin[:100]:
        A(f"| {t['id']} | {t['words']} | {t.get('fam') or t.get('lang')} | {t.get('city') or '-'} | {t['title'][:50]} |")
    if len(thin) > 100:
        A(f"| … | | | | +{len(thin)-100} في JSON |")
    A("")
    A("---")
    A("")
    A("## 3) محتوى غير مناسب / غير متطابق مع الخدمة")
    A("")
    A(f"الإجمالي: **{out['mismatch_count']}** — حسب العائلة: {out.get('mismatch_by_fam')}")
    A("")
    A("| ID | المتوقع | الغالب | own/dom | العنوان |")
    A("|----|---------|--------|---------|---------|")
    for m in out.get("mismatches") or []:
        A(f"| {m['id']} | {m['fam']} | {m['dom'][0]} ({m['dom'][1]}) | {m['own']}/{m['dom'][1]} | {m['title'][:45]} |")
    A("")
    A("---")
    A("")
    A("## 4) مقالات متشابهة / قالب واحد")
    A("")
    A(f"- قالب قوي (≥3 علامات): **{out['template_strong_count']}**")
    A(f"- تكرار محتوى حرفي: {out['exact_dup_count']}")
    A(f"- افتتاحيات متطابقة: {out['near_opener_count']}")
    A(f"- مجموعات city-swap (≥4): **{out['city_swap_cluster_count']}**")
    A(f"- عناوين مكررة منشورة: **{out['publish_dup_title_count']}**")
    A("")
    A("### أكبر مجموعات التشابه الجغرافي")
    for g in (out.get("city_swap_clusters") or [])[:12]:
        A(f"- **{g['n']}** — `{g['fp'][:90]}`")
        A("  - " + ", ".join(f"{i['id']}:{i['slug'][:28]}" for i in g["items"][:6]))
    A("")
    A("---")
    A("")
    A("## 5) مقالات تحتاج تحديث")
    A("")
    A(f"إشارات تحديث: **{out['needs_update_count']}** (thin / قالب ثقيل / mismatch / تواريخ قديمة…)")
    A("")
    for n in (out.get("needs_update_sample") or [])[:40]:
        A(f"- `{n['id']}` {n['slug'][:40]} — {', '.join(n['reasons'])} — {n['aw']} كلمة")
    A("")
    A("---")
    A("")
    A("## 6) فجوات المدن × الخدمات (تغطية السعودية)")
    A("")
    A("### المدن الأساسية (8)")
    for fam, g in gaps.items():
        miss = g["missing_core8"]
        A(f"- **{g['service']}**: متوفر {g['have_count']} مدينة — ناقص أساسي: {', '.join(miss) if miss else 'لا شيء ✅'}")
    A("")
    A("### المدن الممتدة الناقصة")
    for fam, g in gaps.items():
        miss = g["missing_extended"]
        A(f"#### {g['service']} (`{fam}`)")
        A(f"- موجود: {', '.join(g['have_cities'][:18])}{'…' if g['have_count']>18 else ''}")
        A(f"- ناقص ممتد ({len(miss)}): {', '.join(miss) if miss else '—'}")
        A("")
    A("### صفحات المدن الحالية")
    for h in out.get("city_pages") or []:
        A(f"- `{h['slug']}` — {h['aw']} كلمة — {h.get('link')}")
    A("")
    A("---")
    A("")
    A("## 7) خدمات ناقصة / غير موجودة")
    A("")
    ms = out.get("missing_services") or {}
    A(f"- عائلات أساسية موجودة: {', '.join(ms.get('core_fams_present') or [])}")
    A(f"- عائلات أساسية ناقصة كلياً: {', '.join(ms.get('core_fams_missing') or []) or 'لا شيء'}")
    A(f"- خدمات متخصصة موجودة إشارات لها: {', '.join(ms.get('niche_present') or []) or '—'}")
    A(f"- خدمات متخصصة مقترحة وغير ظاهرة بوضوح: {', '.join(ms.get('niche_missing_suggested') or [])}")
    A("")
    A("### صفحات أساسية ضعيفة (<500 كلمة)")
    for h in out.get("thin_hubs") or []:
        A(f"- [{h['type']}] `{h['slug']}` — **{h['aw']}** — {h['title']}")
    A("")
    A("---")
    A("")
    A("## أولويات مقترحة (بدون تنفيذ في هذا التقرير)")
    A("")
    A("1. معالجة المقالات <1000 كلمة والمطابقات الخاطئة أولاً.")
    A("2. كسر أكبر مجموعات city-swap وتنويع الافتتاحيات.")
    A("3. سد فجوات المدن الممتدة للخدمات الأساسية ناقصة التغطية.")
    A("4. تنظيف العناوين الملوّثة وأرقام الهاتف غير المرغوبة عند اعتماد رقم سعودي نهائي.")
    A("5. تقوية about/contact/faq/services وصفحات المدن الرفيعة.")
    A("")
    A("## الملفات")
    A("")
    A("- `data/site-needs-audit-2026-11-03.json`")
    A("- `scripts/site_needs_audit_readonly.py`")
    A("")
    path = REPORTS / "site-needs-audit-2026-11-03.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main():
    print("READ-ONLY AUDIT — no mutations", flush=True)
    posts = fetch_all("posts")
    pages = fetch_all("pages", statuses="publish")
    try:
        services = fetch_all("services", statuses="publish")
    except Exception:
        services = []

    print("analyze posts", flush=True)
    analysis = analyze_posts(posts)
    gaps = coverage_gaps(analysis)
    hubs = analyze_hubs(pages, services)
    smoke = frontend_smoke()
    missing = missing_services_overall(analysis.get("_records") or [])

    out = {
        "at": datetime.now(timezone.utc).isoformat(),
        "mode": "read_only",
        "checked": analysis["checked"],
        "by_status": analysis["by_status"],
        "word_buckets": analysis["word_buckets"],
        "thin_count": analysis["thin_count"],
        "thin_lt_1000": analysis["thin_lt_1000"],
        "template_strong_count": analysis["template_strong_count"],
        "template_strong_sample": analysis["template_strong_sample"],
        "exact_dup_count": analysis["exact_dup_count"],
        "exact_dups": analysis["exact_dups"],
        "near_opener_count": analysis["near_opener_count"],
        "near_openers": analysis["near_openers"],
        "city_swap_cluster_count": analysis["city_swap_cluster_count"],
        "city_swap_clusters": analysis["city_swap_clusters"],
        "publish_dup_title_count": analysis["publish_dup_title_count"],
        "publish_dup_titles": analysis["publish_dup_titles"],
        "mismatch_count": analysis["mismatch_count"],
        "mismatch_by_fam": analysis["mismatch_by_fam"],
        "mismatches": analysis["mismatches"],
        "error_count": analysis["error_count"],
        "error_by_code": analysis["error_by_code"],
        "errors_sample": analysis["errors_sample"],
        "missing_post_call_count": analysis["missing_post_call_count"],
        "missing_post_call": analysis["missing_post_call"],
        "short_excerpt_count": analysis["short_excerpt_count"],
        "polluted_titles_count": analysis["polluted_titles_count"],
        "polluted_titles_sample": analysis["polluted_titles_sample"],
        "en_posts": analysis["en_posts"],
        "needs_update_count": analysis["needs_update_count"],
        "needs_update_sample": analysis["needs_update_sample"],
        "coverage": analysis["coverage"],
        "coverage_gaps": gaps,
        "thin_hubs": hubs["thin_hubs"],
        "city_pages": hubs["city_pages"],
        "hubs": hubs["hubs"],
        "frontend_smoke": smoke,
        "missing_services": missing,
    }
    # drop internal
    json_path = DATA / "site-needs-audit-2026-11-03.json"
    json_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    report = write_report(out)
    print("WROTE", json_path, flush=True)
    print("WROTE", report, flush=True)
    print(
        "SUMMARY",
        json.dumps(
            {
                "checked": out["checked"],
                "thin": out["thin_count"],
                "template": out["template_strong_count"],
                "city_swap": out["city_swap_cluster_count"],
                "mismatch": out["mismatch_count"],
                "errors": out["error_count"],
                "polluted_titles": out["polluted_titles_count"],
                "needs_update": out["needs_update_count"],
                "pub_dup_titles": out["publish_dup_title_count"],
            },
            ensure_ascii=False,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
