# -*- coding: utf-8 -*-
"""Phase 2: create WordPress drafts for non-duplicate Bisha targets."""

from __future__ import annotations

import csv
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bisha_content import (
    arabic_word_count,
    build_html,
    secondary_keywords,
    seo_description,
    seo_title,
)
from bisha_targets import CATEGORY_ID, GROUP_LABELS, MEDIA, TARGETS
from bisha_wp import create_draft, get_by_slug, update_rank_math

ROOT = Path(__file__).resolve().parents[1]
STORE_DOCS = Path(
    os.environ.get(
        "BISHA_STORE_DOCS",
        "/cursor/stores/bc-64c23f33-0042-4da8-b945-442fb8d0b9d8/docs",
    )
)
REPORTS = ROOT / "reports" / "bisha"
STATE = REPORTS / "bisha_creation_state.json"
AUDIT = REPORTS / "bisha_articles_audit.csv"


def load_audit_decisions():
    decisions = {}
    path = AUDIT if AUDIT.exists() else STORE_DOCS / "bisha_articles_audit.csv"
    with path.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            decisions[row["proposed_slug"]] = row
    return decisions


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"created": {}}


def save_state(state):
    REPORTS.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def related_targets(current):
    same = [t for t in TARGETS if t["group"] == current["group"] and t["slug"] != current["slug"]]
    # deterministic three neighbors
    idx = next(i for i, t in enumerate(TARGETS) if t["slug"] == current["slug"])
    picks = []
    for off in (1, 2, 3):
        picks.append(same[(idx + off) % len(same)])
    return picks


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    STORE_DOCS.mkdir(parents=True, exist_ok=True)
    decisions = load_audit_decisions()
    state = load_state()
    results = []

    for t in TARGETS:
        row = decisions.get(t["slug"], {})
        decision = row.get("decision", "create_draft")
        if decision != "create_draft":
            results.append(
                {
                    "title": t["title"],
                    "post_id": row.get("existing_post_id", ""),
                    "link": "",
                    "category": GROUP_LABELS[t["group"]],
                    "focus_keyword": t["focus"],
                    "meta_description": "",
                    "word_count": "",
                    "status": "مستبعد",
                    "skip_reason": row.get("match_reason") or "duplicate",
                }
            )
            continue

        # Idempotent: skip if already created in state or slug exists as draft
        existing = get_by_slug(t["slug"])
        if existing and existing.get("status") in ("draft", "publish", "pending", "private"):
            post = existing
            created_new = False
        elif t["slug"] in state.get("created", {}):
            # trust state id
            from bisha_wp import request

            post, _ = request("GET", f"/wp/v2/posts/{state['created'][t['slug']]['id']}", {"context": "edit"})
            created_new = False
        else:
            html = build_html(t, related_targets(t))
            wc = arabic_word_count(html)
            featured = MEDIA.get(t.get("media", "cleaning"))
            post = create_draft(
                title=t["title"],
                content=html,
                slug=t["slug"],
                categories=[CATEGORY_ID],
                featured_media=featured,
            )
            created_new = True
            # Rank Math SEO
            meta = {
                "rank_math_title": seo_title(t),
                "rank_math_description": seo_description(t),
                "rank_math_focus_keyword": t["focus"],
            }
            try:
                update_rank_math(post["id"], meta)
            except Exception as e:
                post["_rankmath_error"] = str(e)[:300]
            state.setdefault("created", {})[t["slug"]] = {
                "id": post["id"],
                "link": post.get("link"),
                "word_count": wc,
            }
            save_state(state)
            time.sleep(0.35)

        html_len = arabic_word_count((post.get("content") or {}).get("raw") or "")
        if not html_len and t["slug"] in state.get("created", {}):
            html_len = state["created"][t["slug"]].get("word_count", "")

        results.append(
            {
                "title": t["title"],
                "post_id": post.get("id", ""),
                "link": post.get("link", ""),
                "category": f"{GROUP_LABELS[t['group']]} → الخدمات ({CATEGORY_ID})",
                "focus_keyword": t["focus"],
                "meta_description": seo_description(t),
                "word_count": html_len or state.get("created", {}).get(t["slug"], {}).get("word_count", ""),
                "status": "مسودة" if post.get("status") == "draft" else post.get("status", "مسودة"),
                "skip_reason": "" if created_new or post.get("status") == "draft" else "",
            }
        )
        print(f"OK {t['slug']} id={post.get('id')} status={post.get('status')} new={created_new}")

    # Write creation report
    fieldnames = [
        "title",
        "post_id",
        "link",
        "category",
        "focus_keyword",
        "meta_description",
        "word_count",
        "status",
        "skip_reason",
    ]
    for dest in (
        REPORTS / "bisha_articles_creation_report.csv",
        STORE_DOCS / "bisha_articles_creation_report.csv",
    ):
        with dest.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(results)

    drafted = sum(1 for r in results if r["status"] == "مسودة" or r["status"] == "draft")
    skipped = sum(1 for r in results if r["status"] == "مستبعد")
    summary = {
        "audited": len(TARGETS),
        "drafted": drafted,
        "skipped": skipped,
        "results": len(results),
    }
    (REPORTS / "bisha_creation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
