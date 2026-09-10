#!/usr/bin/env python3
"""Merge duplicate city terms and reassign the generic «السعودية» term."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rewrite_unique_articles import parse_title, ensure_city
from wp_client import delete, get, get_paged, put

ROOT = Path(__file__).resolve().parents[1]
RIYADH_MAIN = 3327  # الرياض-ar
RIYADH_DUP = 2837
SAUDI_TERM = 3455


def posts_for_term(term_id: int) -> list[dict]:
    return get_paged(
        "/wp/v2/posts",
        extra=f"&cities={term_id}&_fields=id,title,slug,cities&context=edit",
    )


def set_cities(pid: int, term_ids: list[int]) -> None:
    ids = []
    for t in term_ids:
        if t and t not in ids:
            ids.append(int(t))
    put(f"/wp/v2/posts/{pid}", {"cities": ids})


def main() -> None:
    report = {"riyadh_merged": [], "saudi_reassigned": [], "deleted": [], "errors": []}

    # 1) Merge duplicate Riyadh
    try:
        dup_posts = posts_for_term(RIYADH_DUP)
    except Exception as e:
        dup_posts = []
        report["errors"].append(f"list riyadh dup: {e}")
    for p in dup_posts:
        cities = [int(x) for x in (p.get("cities") or []) if int(x) != RIYADH_DUP]
        if RIYADH_MAIN not in cities:
            cities.append(RIYADH_MAIN)
        try:
            set_cities(p["id"], cities)
            report["riyadh_merged"].append(p["id"])
        except Exception as e:
            report["errors"].append(f"merge {p['id']}: {e}")
        time.sleep(0.05)

    # 2) Reassign generic السعودية
    try:
        saudi_posts = posts_for_term(SAUDI_TERM)
    except Exception as e:
        saudi_posts = []
        report["errors"].append(f"list saudi: {e}")

    for p in saudi_posts:
        title = (p.get("title") or {}).get("raw") or (p.get("title") or {}).get("rendered") or ""
        city, _svc = parse_title(title)
        if city in ("السعودية", ""):
            slug = p.get("slug") or ""
            for token, name in (
                ("riyadh", "الرياض"),
                ("jeddah", "جدة"),
                ("dammam", "الدمام"),
                ("khobar", "الخبر"),
                ("makkah", "مكة المكرمة"),
                ("madinah", "المدينة المنورة"),
                ("medina", "المدينة المنورة"),
            ):
                if token in slug:
                    city = name
                    break
        term_id = ensure_city(city) if city and city != "السعودية" else None
        cities = [int(x) for x in (p.get("cities") or []) if int(x) != SAUDI_TERM]
        if term_id:
            if term_id not in cities:
                cities.append(term_id)
        try:
            set_cities(p["id"], cities)
            report["saudi_reassigned"].append(
                {"id": p["id"], "title": title, "city": city, "term": term_id}
            )
        except Exception as e:
            report["errors"].append(f"reassign {p['id']}: {e}")
        time.sleep(0.05)

    for tid in (RIYADH_DUP, SAUDI_TERM):
        try:
            remaining = posts_for_term(tid)
            if remaining:
                report["deleted"].append({"id": tid, "skipped": f"still {len(remaining)} posts"})
                continue
            delete(f"/wp/v2/cities/{tid}")
            report["deleted"].append({"id": tid, "ok": True})
        except Exception as e:
            report["deleted"].append({"id": tid, "error": str(e)[:300]})

    cities, _ = get("/wp/v2/cities?per_page=100")
    report["cities_after"] = [
        {"id": c["id"], "name": c["name"], "slug": c["slug"], "count": c.get("count")}
        for c in cities or []
    ]
    out = ROOT / "reports" / "cities-taxonomy-fix.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "riyadh_merged": len(report["riyadh_merged"]),
                "saudi_reassigned": len(report["saudi_reassigned"]),
                "errors": len(report["errors"]),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
