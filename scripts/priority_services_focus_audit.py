#!/usr/bin/env python3
"""READ-ONLY focused audit: leak, roof insulation, oven cleaning, AC, cleaning, pest, solar, furniture moving."""

from __future__ import annotations

import base64
import json
import re
import time
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://www.rukn-eltatawer.com/sa/wp-json"
AUTH = base64.b64encode(b"cursor:PCkk ig95 Gu6c zOgC GLYG FYsk").decode()
H = {"Authorization": f"Basic {AUTH}", "User-Agent": "Mozilla/5.0 RuknPriorityFocusAudit/2026-11-05"}
ROOT = Path(__file__).resolve().parents[1]
DATA, REPORTS = ROOT / "data", ROOT / "reports"
DATA.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)

CITIES = {
    "riyadh": "الرياض", "jeddah": "جدة", "mecca": "مكة المكرمة", "makkah": "مكة المكرمة",
    "medina": "المدينة المنورة", "madinah": "المدينة المنورة", "dammam": "الدمام", "khobar": "الخبر",
    "taif": "الطائف", "abha": "أبها", "tabuk": "تبوك", "buraidah": "بريدة",
    "khamis-mushait": "خميس مشيط", "najran": "نجران", "jazan": "جازان", "yanbu": "ينبع",
    "jubail": "الجبيل", "ahsa": "الأحساء", "hail": "حائل", "khafji": "الخفجي",
    "qatif": "القطيف", "dhahran": "الظهران", "hafar-albatin": "حفر الباطن", "kharj": "الخرج",
    "baha": "الباحة", "unaizah": "عنيزة", "hofuf": "الهفوف", "arar": "عرعر",
}
CORE8 = ["riyadh", "jeddah", "mecca", "medina", "dammam", "khobar", "taif", "abha"]
EXTENDED = ["tabuk", "buraidah", "khamis-mushait", "najran", "jazan", "yanbu", "jubail", "ahsa", "hail", "khafji", "qatif", "dhahran", "hafar-albatin", "kharj", "baha"]

# Priority families requested by user
FAM = {
    "leak": {
        "ar": "كشف التسربات",
        "slug_any": ["leak", "water-leak", "pipe-leak", "تسرب"],
        "title_re": re.compile(r"تسرب|كشف تسرب", re.I),
        "topic": re.compile(r"تسرب|كشف تسرب|رطوبة|فاتورة مياه|مواسير"),
        "anti": re.compile(r"نقل عفش|عشب صناعي|مكافحة حشرات"),
    },
    "insul": {
        "ar": "عزل الأسطح",
        "slug_any": ["insulation", "waterproof", "roof-insul", "عزل"],
        "title_re": re.compile(r"عزل\s*أسطح|عزل الأسطح|عزل اسطح|waterproof|insulation", re.I),
        "topic": re.compile(r"عزل|عازل|مواد عزل|عزل مائي|عزل حراري|سطح|أسطح"),
        "anti": re.compile(r"نقل عفش|مكافحة|غسيل مكيف"),
    },
    "oven": {
        "ar": "تنظيف الأفران",
        "slug_any": ["oven", "fran", "فرن", "افران", "أفران"],
        "title_re": re.compile(r"فرن|أفران|افران|oven", re.I),
        "topic": re.compile(r"فرن|أفران|افران|شواية|فرن غاز|فرن كهرب"),
        "anti": re.compile(r"مكيف|تسرب مياه|عزل أسطح"),
    },
    "ac": {
        "ar": "المكيفات (غسيل/صيانة/دكتات)",
        "slug_any": ["ac-", "ac-cleaning", "split-ac", "duct", "central-ac", "مكيف", "تكييف"],
        "title_re": re.compile(r"مكيف|تكييف|دكت|غسيل.*مكيف|ac\b", re.I),
        "topic": re.compile(r"مكيف|تكييف|فريون|دكت|سبليت|غسيل مكيف"),
        "anti": re.compile(r"نقل عفش|عشب|كشف تسربات المياه"),
    },
    "clean": {
        "ar": "التنظيف العام",
        "slug_any": ["cleaning", "sofa", "carpet", "steriliz", "تنظيف"],
        "title_re": re.compile(r"تنظيف|غسيل كنب|سجاد|تعقيم", re.I),
        "topic": re.compile(r"تنظيف|غسيل|سجاد|كنب|تعقيم|جلي"),
        "anti": re.compile(r"كشف تسرب|عزل أسطح|نقل بيانو"),
    },
    "pest": {
        "ar": "مكافحة الحشرات",
        "slug_any": ["pest", "termite", "cockroach", "ant-control", "bed-bug", "rodent", "مكافحة"],
        "title_re": re.compile(r"مكافحة|حشرات|نمل|صراصير|بق|فئران", re.I),
        "topic": re.compile(r"مكافحة|حشرات|نمل|صراصير|بق|فئران|مبيد|آفات"),
        "anti": re.compile(r"عزل أسطح|غسيل مكيف|نقل عفش"),
    },
    "solar": {
        "ar": "الطاقة الشمسية",
        "slug_any": ["solar", "pv", "شمسي", "طاقة-شمسية", "الواح"],
        "title_re": re.compile(r"طاقة شمسية|ألواح شمسية|سخان شمسي|solar|photovolta", re.I),
        "topic": re.compile(r"طاقة شمسية|ألواح|شمسي|إنفرتر|خلايا|watt|كيلوواط"),
        "anti": re.compile(r"تنظيف منازل|كشف تسرب|مكافحة"),
    },
    "move": {
        "ar": "نقل الأثاث",
        "slug_any": ["moving", "furniture-mov", "furniture-shipping", "نقل", "عفش", "piano"],
        "title_re": re.compile(r"نقل\s*عفش|نقل\s*أثاث|نقل اثاث|شحن أثاث|نقل بيانو|furniture moving", re.I),
        "topic": re.compile(r"نقل|عفش|أثاث|تغليف|شاحنة|تحميل|بيانو"),
        "anti": re.compile(r"كشف تسرب|عزل أسطح|مكافحة حشرات"),
    },
}


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


def strip(html: str) -> str:
    t = re.sub(r"<script[\s\S]*?</script>", " ", html or "", flags=re.I)
    t = re.sub(r"<style[\s\S]*?</style>", " ", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def ar_words(t: str) -> int:
    return len(re.findall(r"[\u0600-\u06FF]+", t or ""))


def en_words(t: str) -> int:
    return len(re.findall(r"[A-Za-z']+", t or ""))


def city_from_slug(slug: str) -> str | None:
    s = (slug or "").lower()
    best, bl = None, 0
    for tok in CITIES:
        if s == tok or s.endswith("-" + tok) or f"-{tok}-" in s:
            if len(tok) >= bl:
                best, bl = tok, len(tok)
    return best


def classify(slug: str, title: str) -> list[str]:
    s = f"{slug} {title}".lower()
    hits = []
    for fam, conf in FAM.items():
        if conf["title_re"].search(title) or conf["title_re"].search(slug):
            hits.append(fam)
            continue
        if any(tok.lower() in s for tok in conf["slug_any"]):
            hits.append(fam)
    # prefer more specific: oven before clean, ac before clean
    if "oven" in hits and "clean" in hits:
        hits = [h for h in hits if h != "clean"] + ["oven"]
        hits = list(dict.fromkeys(hits))
    if "ac" in hits and "clean" in hits and re.search(r"مكيف|تكييف|duct|ac-cleaning", s):
        hits = [h for h in hits if h != "clean"]
        if "ac" not in hits:
            hits.append("ac")
    return hits


def has_city(have: set, c: str) -> bool:
    if c in have:
        return True
    ar = CITIES.get(c)
    return any(CITIES.get(h) == ar for h in have)


def fetch_posts():
    items, page = [], 1
    while True:
        hdr, batch = get(
            f"/wp/v2/posts?per_page=100&page={page}&status=publish,draft&context=edit&orderby=id&order=asc"
            f"&_fields=id,title,slug,status,link,content,excerpt,date,modified"
        )
        if not batch:
            break
        items.extend(batch)
        print(f"posts {page}/{hdr.get('X-WP-TotalPages')} n={len(items)}", flush=True)
        if page >= int(hdr.get("X-WP-TotalPages", page)):
            break
        page += 1
    return items


def fetch_services_cpt():
    try:
        hdr, items = get("/wp/v2/services?per_page=100&status=publish&context=edit&_fields=id,title,slug,link,content,status")
        return items
    except Exception as e:
        print("services err", e, flush=True)
        return []


def analyze(posts, services_cpt):
    by_fam = {k: [] for k in FAM}
    unmatched_priority_hints = []
    city_clusters = defaultdict(list)
    CITY_AR = list(set(CITIES.values())) + ["مكة", "المدينة"]

    for p in posts:
        title = (p.get("title") or {}).get("raw") or ""
        slug = p.get("slug") or ""
        raw = (p.get("content") or {}).get("raw") or ""
        plain = strip(raw)
        aw, ew = ar_words(plain), en_words(plain)
        status = p.get("status")
        city = city_from_slug(slug)
        fams = classify(slug, title)
        excerpt = strip((p.get("excerpt") or {}).get("raw") or "")

        # solar/oven may only appear in body
        if not fams:
            if FAM["solar"]["title_re"].search(plain[:800]) and ("شمسي" in title or "solar" in slug.lower()):
                fams = ["solar"]
            if FAM["oven"]["title_re"].search(title) or FAM["oven"]["title_re"].search(slug):
                fams = ["oven"]

        rec_base = {
            "id": p["id"], "slug": slug, "title": title[:80], "status": status,
            "link": p.get("link"), "city": city, "aw": aw, "ew": ew,
            "has_post_call": "[post_call]" in raw,
            "short_excerpt": len(excerpt) < 40,
            "placeholders": bool(re.search(r"\{[A-Z_]{3,}\}|TODO|نص تجريبي", raw)),
            "polluted_title": bool(re.search(r"01151481000|الإعلان للإيجار", title)),
        }

        for fam in fams:
            conf = FAM[fam]
            topic_hits = len(conf["topic"].findall(plain))
            anti_hits = len(conf["anti"].findall(plain))
            mismatch = status == "publish" and aw >= 150 and topic_hits <= 3 and anti_hits >= 6
            thin = status == "publish" and aw < 1000 and not (slug.startswith("en-") and ew >= 1000)
            thin_en = status == "publish" and slug.startswith("en-") and ew < 1000
            row = {
                **rec_base,
                "fam": fam,
                "topic_hits": topic_hits,
                "anti_hits": anti_hits,
                "mismatch": mismatch,
                "thin": thin or thin_en,
                "words": ew if slug.startswith("en-") else aw,
            }
            by_fam[fam].append(row)

            if status == "publish":
                op = plain[:200]
                for c in CITY_AR:
                    op = op.replace(c, "CITY")
                op = re.sub(r"\s+", " ", op)[:120]
                city_clusters[(fam, op)].append({"id": p["id"], "slug": slug, "city": city})

        # detect possible oven/solar pages missed by weak slug
        if status == "publish":
            if re.search(r"تنظيف\s*أفران|تنظيف\s*افران|oven clean", title, re.I) and "oven" not in fams:
                unmatched_priority_hints.append({"id": p["id"], "slug": slug, "title": title, "hint": "oven"})
            if re.search(r"طاقة\s*شمسية|ألواح\s*شمسية|solar", title, re.I) and "solar" not in fams:
                unmatched_priority_hints.append({"id": p["id"], "slug": slug, "title": title, "hint": "solar"})

    # coverage + gaps
    summary = {}
    for fam, conf in FAM.items():
        rows = by_fam[fam]
        pub = [r for r in rows if r["status"] == "publish"]
        draft = [r for r in rows if r["status"] == "draft"]
        cities = {r["city"] for r in pub if r.get("city")}
        thin = [r for r in pub if r["thin"]]
        mism = [r for r in pub if r["mismatch"]]
        ph = [r for r in pub if r["placeholders"]]
        no_call = [r for r in pub if not r["has_post_call"]]
        polluted = [r for r in pub if r["polluted_title"]]
        # clusters
        clusters = []
        for (f, op), items in city_clusters.items():
            if f == fam and len(items) >= 4:
                clusters.append({"n": len(items), "fp": op, "items": items[:10]})
        clusters.sort(key=lambda x: -x["n"])

        summary[fam] = {
            "label": conf["ar"],
            "publish": len(pub),
            "draft": len(draft),
            "cities_count": len(cities),
            "cities": sorted(cities),
            "missing_core8": [c for c in CORE8 if not has_city(cities, c)],
            "missing_extended": [c for c in EXTENDED if not has_city(cities, c)],
            "thin_count": len(thin),
            "thin_sample": sorted(thin, key=lambda r: r["words"])[:25],
            "mismatch_count": len(mism),
            "mismatch_sample": mism[:20],
            "placeholder_count": len(ph),
            "placeholder_sample": ph[:10],
            "no_post_call": len(no_call),
            "polluted_titles": len(polluted),
            "city_swap_clusters": clusters[:12],
            "city_swap_cluster_count": len(clusters),
            "sample_links": [{"id": r["id"], "slug": r["slug"], "city": r["city"], "words": r["words"]} for r in pub[:8]],
        }

    # CPT mapping
    cpt = []
    for s in services_cpt:
        title = (s.get("title") or {}).get("raw") or ""
        slug = s.get("slug") or ""
        plain = strip((s.get("content") or {}).get("raw") or "")
        fams = classify(slug, title)
        cpt.append({"id": s["id"], "slug": slug, "title": title, "aw": ar_words(plain), "fams": fams, "link": s.get("link")})

    return {
        "by_fam": summary,
        "unmatched_priority_hints": unmatched_priority_hints,
        "services_cpt": cpt,
        "posts_checked": len(posts),
    }


def write_report(out: dict) -> Path:
    lines = []
    A = lines.append
    A("# فحص مركّز للخدمات ذات الأولوية — 5 نوفمبر 2026")
    A("")
    A("**الموقع:** https://www.rukn-eltatawer.com/sa  ")
    A(f"**الوقت (UTC):** {out['at']}  ")
    A("**الوضع:** فحص فقط — بدون تنفيذ تعديلات.")
    A("")
    A("## نطاق التركيز")
    A("")
    A("1. كشف التسربات")
    A("2. عزل الأسطح")
    A("3. تنظيف الأفران")
    A("4. المكيفات")
    A("5. التنظيف")
    A("6. مكافحة الحشرات")
    A("7. الطاقة الشمسية")
    A("8. نقل الأثاث")
    A("")
    A("## لوحة سريعة")
    A("")
    A("| الخدمة | منشور | مدن | ناقص أساسي(8) | ناقص ممتد | <1000 كلمة | عدم تطابق | قوالب متشابهة |")
    A("|--------|-------|-----|---------------|-----------|------------|-----------|----------------|")
    for fam, s in out["by_fam"].items():
        A(
            f"| {s['label']} | {s['publish']} | {s['cities_count']} | "
            f"{len(s['missing_core8'])} | {len(s['missing_extended'])} | "
            f"{s['thin_count']} | {s['mismatch_count']} | {s['city_swap_cluster_count']} |"
        )
    A("")
    A("---")
    A("")

    for fam, s in out["by_fam"].items():
        A(f"## {s['label']} (`{fam}`)")
        A("")
        A(f"- منشور: **{s['publish']}** | مسودة: {s['draft']}")
        A(f"- مدن مغطاة ({s['cities_count']}): {', '.join(s['cities']) if s['cities'] else '—'}")
        A(f"- ناقص من الأساسية 8: {', '.join(s['missing_core8']) if s['missing_core8'] else 'لا شيء ✅'}")
        A(f"- ناقص ممتد ({len(s['missing_extended'])}): {', '.join(s['missing_extended']) if s['missing_extended'] else '—'}")
        A(f"- مقالات <1000: **{s['thin_count']}** | عدم تطابق: **{s['mismatch_count']}** | placeholders: {s['placeholder_count']} | بدون post_call: {s['no_post_call']}")
        A("")
        if s["publish"] == 0:
            A("> **خدمة شبه غائبة عن الموقع كصفحات مخصّصة.** تحتاج إنشاء محتوى وربط مدن.")
            A("")
        if s["thin_sample"]:
            A("### عيّنة محتوى قصير")
            for t in s["thin_sample"][:12]:
                A(f"- `{t['id']}` {t['slug'][:45]} — {t['words']} كلمة — {t['title'][:50]}")
            A("")
        if s["mismatch_sample"]:
            A("### عيّنة عدم تطابق")
            for m in s["mismatch_sample"][:10]:
                A(f"- `{m['id']}` {m['slug'][:45]} — topic={m['topic_hits']} anti={m['anti_hits']}")
            A("")
        if s["placeholder_sample"]:
            A("### Placeholders")
            for m in s["placeholder_sample"][:8]:
                A(f"- `{m['id']}` {m['slug']}")
            A("")
        if s["city_swap_clusters"]:
            A("### أكبر مجموعات التشابه (city-swap)")
            for g in s["city_swap_clusters"][:6]:
                A(f"- **{g['n']}** — `{g['fp'][:80]}`")
                A("  - " + ", ".join(f"{i['id']}:{i['slug'][:24]}" for i in g["items"][:5]))
            A("")
        A("")

    A("## خدمات CPT المرتبطة")
    A("")
    for s in out.get("services_cpt") or []:
        A(f"- `{s['id']}` {s['slug']} — {s['aw']} كلمة — fams={s['fams']} — {s['title']}")
    A("")
    A("## استنتاجات مركّزة")
    A("")
    # auto insights
    by = out["by_fam"]
    if by["oven"]["publish"] == 0:
        A("- **تنظيف الأفران:** لا توجد صفحات مخصّصة منشورة تقريباً — فجوة خدمة واضحة.")
    if by["solar"]["publish"] == 0:
        A("- **الطاقة الشمسية:** غير موجودة كخط خدمة محتوى — فجوة خدمة واضحة.")
    A("- **كشف التسربات / العزل / التنظيف / المكافحة / المكيفات / النقل:** موجودة، لكن تفاوت كبير في تغطية المدن (خصوصاً سباكة-مشابه النقل للممتدة).")
    if by["move"]["missing_extended"]:
        A(f"- **نقل الأثاث** ينقصه مدن ممتدة: {', '.join(by['move']['missing_extended'][:10])}…")
    if by["leak"]["placeholder_count"]:
        A("- بقايا placeholders في مقالات تسربات/عزل تحتاج تنظيف نصي.")
    A("")
    A("## أولويات مقترحة (بدون تنفيذ هنا)")
    A("")
    A("1. إنشاء خط **تنظيف أفران** و**طاقة شمسية** (صفحة خدمة + مدن أساسية أولاً).")
    A("2. سد فجوات المدن الممتدة لـ **نقل الأثاث** ثم المكيفات/التنظيف/المكافحة حيث تنقص.")
    A("3. كسر مجموعات city-swap داخل كل عائلة ذات أولوية.")
    A("4. إصلاح placeholders `{COMPANY}/{YEAR}` في مقالات التسربات/العزل.")
    A("")
    A("الملفات: `data/priority-services-focus-audit-2026-11-05.json`")
    A("")
    path = REPORTS / "priority-services-focus-audit-2026-11-05.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main():
    print("PRIORITY FOCUS AUDIT — read only", flush=True)
    posts = fetch_posts()
    services = fetch_services_cpt()
    analyzed = analyze(posts, services)
    out = {
        "at": datetime.now(timezone.utc).isoformat(),
        "mode": "read_only_focus",
        "posts_checked": analyzed["posts_checked"],
        "by_fam": analyzed["by_fam"],
        "unmatched_priority_hints": analyzed["unmatched_priority_hints"],
        "services_cpt": analyzed["services_cpt"],
    }
    # serialize without huge nested if needed — already trimmed samples
    path = DATA / "priority-services-focus-audit-2026-11-05.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    report = write_report(out)
    print("WROTE", path, flush=True)
    print("WROTE", report, flush=True)
    brief = {k: {"pub": v["publish"], "cities": v["cities_count"], "thin": v["thin_count"], "miss_ext": len(v["missing_extended"]), "mismatch": v["mismatch_count"]} for k, v in out["by_fam"].items()}
    print("SUMMARY", json.dumps(brief, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
