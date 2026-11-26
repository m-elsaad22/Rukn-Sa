# -*- coding: utf-8 -*-
"""Phase 1: audit Ahsa batch-1 leak/moisture services against WP publish+draft."""

from __future__ import annotations

import csv
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ahsa_batch1_targets import AUDIT_SERVICES, CITY_AR
from ahsa_batch1_wp import confirm_user, get_by_slug, get_post, search_posts

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "ahsa-batch1"
STORE_DOCS = Path(
    os.environ.get(
        "AHSA_STORE_DOCS",
        "/cursor/stores/bc-64c23f33-0042-4da8-b945-442fb8d0b9d8/docs",
    )
)

AHSA_MARKERS = ("أحساء", "احساء", "ahsa", "Ahsa", "الأحساء")


def title_of(p: dict) -> str:
    t = p.get("title") or {}
    return (t.get("raw") or t.get("rendered") or "").strip()


def is_ahsa(p: dict) -> bool:
    blob = title_of(p) + " " + (p.get("slug") or "")
    return any(m in blob for m in AHSA_MARKERS)


def intent_hits(service: str) -> list:
    queries = [
        f"{service} {CITY_AR}",
        f"{service} بالأحساء",
        service,
    ]
    seen = {}
    for q in queries:
        for p in search_posts(q, status="any"):
            if is_ahsa(p):
                seen[p["id"]] = p
    return list(seen.values())


def decide(service_row: dict) -> dict:
    key = service_row["key"]
    service = service_row["service"]
    slug = service_row["slug"]

    # Hard rules from assignment / audit
    if key == "general_leak":
        primary = get_post(9308)
        conflict = get_post(23824)
        return {
            "service": service,
            "exists": "yes",
            "post_id": "9308",
            "decision": "keep_existing_primary",
            "existing_status": primary.get("status", "publish"),
            "existing_slug": primary.get("slug", "water-leak-detection-al-ahsa"),
            "existing_title": title_of(primary),
            "focus_keyword": service_row["focus"],
            "proposed_slug": slug,
            "match_reason": (
                "Primary Ahsa leak page 9308 retained; conflicting twin 23824 "
                f"({title_of(conflict)}) must not be recreated; no new general-leak draft."
            ),
            "notes": "Do not edit/delete/redirect 9308 or 23824 in this batch.",
        }

    by_slug = get_by_slug(slug)
    hits = intent_hits(service)

    # Filter hits that are clearly the same narrow intent (title contains service core)
    core = service.replace("في الأحساء", "").strip()
    strong = []
    for p in hits:
        tit = title_of(p)
        # general leak pages should not block specialized intents
        if key != "general_leak" and p["id"] in (9308, 23824):
            # 9308/23824 are general detection — not duplicates of specialized services
            continue
        if core[:12] in tit or service_row["slug"].replace("-ahsa", "") in (p.get("slug") or ""):
            strong.append(p)

    if by_slug and by_slug.get("status") in ("draft", "publish", "pending", "private"):
        return {
            "service": service,
            "exists": "yes",
            "post_id": str(by_slug["id"]),
            "decision": "skip_existing_slug",
            "existing_status": by_slug.get("status"),
            "existing_slug": by_slug.get("slug"),
            "existing_title": title_of(by_slug),
            "focus_keyword": service_row["focus"],
            "proposed_slug": slug,
            "match_reason": "Proposed slug already occupied",
            "notes": "",
        }

    if strong:
        p = strong[0]
        return {
            "service": service,
            "exists": "yes",
            "post_id": str(p["id"]),
            "decision": "skip_duplicate_intent",
            "existing_status": p.get("status"),
            "existing_slug": p.get("slug"),
            "existing_title": title_of(p),
            "focus_keyword": service_row["focus"],
            "proposed_slug": slug,
            "match_reason": "Existing Ahsa post covers same search intent",
            "notes": "",
        }

    return {
        "service": service,
        "exists": "no",
        "post_id": "",
        "decision": "create_draft",
        "existing_status": "",
        "existing_slug": "",
        "existing_title": "",
        "focus_keyword": service_row["focus"],
        "proposed_slug": slug,
        "match_reason": "",
        "notes": "Missing specialized Ahsa service page; draft only.",
    }


def main():
    me = confirm_user()
    print(f"Auth OK: id={me.get('id')} slug={me.get('slug')} roles={me.get('roles')}")

    REPORTS.mkdir(parents=True, exist_ok=True)
    STORE_DOCS.mkdir(parents=True, exist_ok=True)

    rows = [decide(s) for s in AUDIT_SERVICES]
    fields = [
        "service",
        "exists",
        "post_id",
        "decision",
        "existing_status",
        "existing_slug",
        "existing_title",
        "focus_keyword",
        "proposed_slug",
        "match_reason",
        "notes",
    ]

    for dest in (REPORTS / "ahsa_batch1_audit.csv", STORE_DOCS / "ahsa_batch1_audit.csv"):
        with dest.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        print("Wrote", dest)

    summary = {
        "auth_user": me.get("slug"),
        "audited": len(rows),
        "create_draft": sum(1 for r in rows if r["decision"] == "create_draft"),
        "skipped": sum(1 for r in rows if r["decision"] != "create_draft"),
        "rows": rows,
    }
    (REPORTS / "ahsa_batch1_audit_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({k: summary[k] for k in ("audited", "create_draft", "skipped")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
