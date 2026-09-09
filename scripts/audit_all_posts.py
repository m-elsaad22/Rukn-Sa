#!/usr/bin/env python3
"""Audit all published posts: length, similarity, topic mismatch, empty blocks."""
from __future__ import annotations

import hashlib
import html as html_lib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_client import get_paged

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data"
OUT.mkdir(exist_ok=True)

SERVICE_HINTS = {
    "leak": ["تسرب", "تسريب", "كشف تسرب"],
    "insul": ["عزل", "فوم", "عازل"],
    "pest": ["مكافحة", "حشرات", "صراصير", "نمل", "بق", "قوارض", "فئران", "عقارب", "بعوض", "وزغ"],
    "clean": ["تنظيف", "تعقيم", "جلي", "غسيل"],
    "ac": ["مكيف", "تكييف", "فريون", "دكت", "سبليت", "تبريد"],
    "plumb": ["سباك", "سباكة", "مجاري", "تسليك", "انسداد", "سخان", "مضخ"],
    "elec": ["كهرب", "إنارة", "انارة", "قواطع"],
    "paint": ["دهان", "صبغ", "بوية", "جبس"],
    "garden": ["حدائق", "حديقة", "عشب", "تنسيق"],
    "pool": ["مسبح", "مسابح", "نوافير"],
    "move": ["نقل عفش", "نقل اثاث", "نقل أثاث", "تخزين"],
    "maint": ["صيانة", "ترميم", "شروخ"],
    "tank": ["خزان", "خزانات"],
}

MISMATCH_FOREIGN = {
    "paint": ["تسرب تحت ممر", "كشف صوتي", "كاميرا حرارية", "عزل فوم", "فريون"],
    "pest": ["شحن الفريون", "دكت التكييف", "كشف تسربات"],
    "clean": ["كاميرا حرارية للتسرب", "عزل الأسطح بالفوم"],
    "garden": ["تسليك المجاري", "شحن فريون"],
    "move": ["كشف تسرب", "عزل فوم", "مكافحة صراصير"],
    "ac": ["عشب صناعي", "نقل عفش"],
}


def wc(html: str) -> int:
    t = re.sub(r"\[[^\]]+\]", " ", html or "")
    t = re.sub(r"<script[\s\S]*?</script>", " ", t, flags=re.I)
    t = re.sub(r"<style[\s\S]*?</style>", " ", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html_lib.unescape(t)
    return len(re.findall(r"[\w\u0600-\u06FF]+", t))


def topic_of(title: str) -> str:
    for k, words in SERVICE_HINTS.items():
        if any(w in title for w in words):
            return k
    return "other"


def fingerprint(html: str, title: str) -> str:
    t = re.sub(r"<[^>]+>", " ", html or "")
    t = html_lib.unescape(t)
    # strip city/service-specific tokens so templates collide
    for w in re.findall(r"[\u0600-\u06FF]{3,}", title):
        t = t.replace(w, " ")
    t = re.sub(r"\s+", " ", t)
    t = t.strip()[:900]
    return hashlib.md5(t.encode("utf-8")).hexdigest()[:12]


def has_shortcodes(html: str) -> dict:
    html = html or ""
    return {
        "post_call": "[post_call]" in html,
        "post_features": "[post_features]" in html,
        "post_steps": "[post_steps]" in html,
        "post_services": "[post_services]" in html,
        "post_prices": "[post_prices]" in html,
        "post_gallery": "[post_gallery]" in html,
    }


def meta_filled(meta: dict) -> dict:
    meta = meta or {}

    def nonempty_group(key: str, inner_keys: list[str]) -> bool:
        g = meta.get(key) or {}
        if not isinstance(g, dict):
            return bool(g)
        if any(g.get(k) for k in inner_keys):
            return True
        for v in g.values():
            if isinstance(v, list) and v:
                return True
            if isinstance(v, str) and v.strip():
                return True
        return False

    faqs = meta.get("yourcolor__faqs") or []
    return {
        "features": nonempty_group("post__features__data", ["features__title", "yourcolor__post_features"]),
        "steps": nonempty_group("post__work_steps__data", ["work_steps__title", "work_steps_items"]),
        "services": nonempty_group("post__services__data", ["services__title", "post_services_items"]),
        "prices": nonempty_group("post__price_list__data", ["price_list__title", "price_list__items"]),
        "call": nonempty_group("post__call_section__data", ["call_section_title", "call_section_phone"]),
        "card": nonempty_group("post__card__data", ["post_card_title"]),
        "popover": nonempty_group("post__popover__data", ["popover_call_title"]),
        "request": nonempty_group("post__service_request__data", ["orderservices"]),
        "schema_service": nonempty_group("YourColor_Service", ["description", "telephone"]),
        "schema_article": nonempty_group("YourColor_Article", ["headline", "description"]),
        "faqs": bool(faqs),
        "phone": bool((meta.get("phone_number") or "").strip()),
    }


def mismatch(title: str, html: str, topic: str) -> bool:
    foreigners = MISMATCH_FOREIGN.get(topic) or []
    body = html or ""
    hits = sum(1 for w in foreigners if w in body)
    # painting talking about leaks
    if topic == "paint" and ("تسرب" in body and "دهان" not in body[:800]):
        return True
    if topic == "paint" and body.count("تسرب") >= 3 and body.count("دهان") + body.count("صبغ") < 3:
        return True
    if topic == "pest" and ("تكييف" in body or "فريون" in body) and "حشر" not in body[:500]:
        return True
    return hits >= 2


def main():
    fields = "id,title,slug,status,date,excerpt,featured_media,tags,cities,content,meta"
    extra = f"&context=edit&status=publish&_fields={fields}"
    print("Fetching published posts...", flush=True)
    posts = get_paged("/wp/v2/posts", per_page=50, extra=extra, sleep=0.12)
    print(f"Fetched {len(posts)}", flush=True)

    rows = []
    fp_map = defaultdict(list)
    for p in posts:
        title = (p.get("title") or {}).get("raw") or ""
        content = (p.get("content") or {}).get("raw") or ""
        excerpt = (p.get("excerpt") or {}).get("raw") or ""
        words = wc(content)
        topic = topic_of(title)
        fp = fingerprint(content, title)
        sc = has_shortcodes(content)
        mf = meta_filled(p.get("meta") or {})
        mm = mismatch(title, content, topic)
        thin = words < 1000
        template = fp
        missing_sc = not sc["post_call"]
        empty_blocks = not (mf["features"] and mf["steps"] and mf["faqs"] and mf["call"])
        needs = thin or mm or missing_sc or empty_blocks
        rec = {
            "id": p["id"],
            "title": title,
            "slug": p.get("slug"),
            "date": p.get("date"),
            "words": words,
            "topic": topic,
            "fp": fp,
            "thin": thin,
            "mismatch": mm,
            "shortcodes": sc,
            "meta": mf,
            "empty_blocks": empty_blocks,
            "featured_media": p.get("featured_media") or 0,
            "tags": p.get("tags") or [],
            "cities": p.get("cities") or [],
            "excerpt_len": wc(excerpt),
            "needs_rewrite": needs,
        }
        rows.append(rec)
        fp_map[fp].append(p["id"])

    similar_groups = {k: v for k, v in fp_map.items() if len(v) >= 2}
    similar_ids = {i for ids in similar_groups.values() for i in ids}
    for rec in rows:
        rec["similar_group"] = rec["fp"] if rec["id"] in similar_ids else None
        if rec["similar_group"]:
            rec["needs_rewrite"] = True

    summary = {
        "total": len(rows),
        "thin": sum(1 for r in rows if r["thin"]),
        "mismatch": sum(1 for r in rows if r["mismatch"]),
        "similar_groups": len(similar_groups),
        "similar_posts": len(similar_ids),
        "empty_blocks": sum(1 for r in rows if r["empty_blocks"]),
        "missing_post_call": sum(1 for r in rows if not r["shortcodes"]["post_call"]),
        "needs_rewrite": sum(1 for r in rows if r["needs_rewrite"]),
        "by_topic": {},
        "word_buckets": {
            "lt500": sum(1 for r in rows if r["words"] < 500),
            "lt1000": sum(1 for r in rows if r["words"] < 1000),
            "lt1500": sum(1 for r in rows if r["words"] < 1500),
            "ge1500": sum(1 for r in rows if r["words"] >= 1500),
        },
    }
    for r in rows:
        summary["by_topic"].setdefault(r["topic"], {"n": 0, "needs": 0, "thin": 0})
        summary["by_topic"][r["topic"]]["n"] += 1
        summary["by_topic"][r["topic"]]["needs"] += int(r["needs_rewrite"])
        summary["by_topic"][r["topic"]]["thin"] += int(r["thin"])

    (OUT / "audit-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "audit-posts.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    (OUT / "audit-similar-groups.json").write_text(
        json.dumps({k: v for k, v in list(similar_groups.items())[:80]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
