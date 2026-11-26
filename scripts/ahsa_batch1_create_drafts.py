# -*- coding: utf-8 -*-
"""Phase 2: create WordPress drafts for Ahsa batch-1 missing services."""

from __future__ import annotations

import csv
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ahsa_batch1_content import (
    arabic_word_count,
    build_html,
    secondary_note,
    seo_description,
    seo_title,
)
from ahsa_batch1_targets import (
    CATEGORY_ID,
    CATEGORY_LEAK,
    CATEGORY_LEAK_INSUL,
    CREATE_TARGETS,
    MEDIA,
)
from ahsa_batch1_wp import confirm_user, create_draft, get_by_slug, update_rank_math

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "ahsa-batch1"
STORE_DOCS = Path(
    os.environ.get(
        "AHSA_STORE_DOCS",
        "/cursor/stores/bc-64c23f33-0042-4da8-b945-442fb8d0b9d8/docs",
    )
)
STATE = REPORTS / "ahsa_batch1_creation_state.json"
AUDIT = REPORTS / "ahsa_batch1_audit.csv"


def load_audit_decisions():
    decisions = {}
    path = AUDIT if AUDIT.exists() else STORE_DOCS / "ahsa_batch1_audit.csv"
    with path.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            decisions[row["service"]] = row
    return decisions


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"created": {}}


def save_state(state):
    REPORTS.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def uniqueness_gate(htmls: dict) -> list:
    """Fail if openers or FAQ question sets are cloned across drafts."""
    issues = []
    openers = {}
    faq_sets = {}
    for key, html in htmls.items():
        # first paragraph text
        import re

        paras = re.findall(r"<p>(.*?)</p>", html, flags=re.S)
        opener = re.sub(r"<[^>]+>", "", paras[0]).strip()[:180] if paras else ""
        faq_html = re.search(r'<div class="faq">(.*?)</div>', html, flags=re.S)
        faqs = tuple(re.findall(r"<h3>(.*?)</h3>", faq_html.group(1) if faq_html else ""))
        for other, op in openers.items():
            if opener and opener == op:
                issues.append(f"cloned opener: {key} == {other}")
        for other, fq in faq_sets.items():
            if faqs and faqs == fq:
                issues.append(f"cloned FAQ set: {key} == {other}")
        openers[key] = opener
        faq_sets[key] = faqs
        wc = arabic_word_count(html)
        if wc < 900:
            issues.append(f"thin content {key}: {wc} arabic tokens")
        # ensure batch H2 themes present
        needed = ["المشكلة والأعراض", "أخطاء تؤخر الحل", "أسئلة شائعة"]
        for n in needed:
            if n not in html:
                issues.append(f"missing H2 theme '{n}' in {key}")
        if "الأحساء" not in html and "بيوت الأحساء" not in html:
            # location section title varies; body must mention city
            if "الأحساء" not in html:
                issues.append(f"missing city mention in {key}")
    return issues


def main():
    me = confirm_user()
    print(f"Auth OK: id={me.get('id')} slug={me.get('slug')}")

    REPORTS.mkdir(parents=True, exist_ok=True)
    STORE_DOCS.mkdir(parents=True, exist_ok=True)
    decisions = load_audit_decisions()
    state = load_state()

    # Pre-build all HTML and run uniqueness gate before any WP write
    html_map = {}
    for t in CREATE_TARGETS:
        row = decisions.get(t["service"], {})
        if row.get("decision", "create_draft") != "create_draft":
            continue
        html_map[t["key"]] = build_html(t)
    gate = uniqueness_gate(html_map)
    if gate:
        raise SystemExit("Uniqueness gate failed:\n- " + "\n- ".join(gate))
    print(f"Uniqueness gate OK for {len(html_map)} drafts")

    results = []
    # Include skipped general leak from audit for completeness
    for service, row in decisions.items():
        if row.get("decision") != "create_draft":
            results.append(
                {
                    "title": row.get("existing_title") or service,
                    "service": service,
                    "post_id": row.get("post_id", ""),
                    "link": "",
                    "slug": row.get("existing_slug") or row.get("proposed_slug", ""),
                    "focus_keyword": row.get("focus_keyword", ""),
                    "meta_description": "",
                    "word_count": "",
                    "status": "skipped",
                    "decision": row.get("decision", ""),
                    "skip_reason": row.get("match_reason") or row.get("decision", ""),
                }
            )

    for t in CREATE_TARGETS:
        row = decisions.get(t["service"], {})
        if row.get("decision", "create_draft") != "create_draft":
            continue

        html = html_map[t["key"]]
        wc = arabic_word_count(html)
        meta_desc = seo_description(t["focus"], secondary_note(t))
        rm_title = seo_title(t["title"], t.get("emoji", "🔎"))
        featured = MEDIA.get(t.get("media", "leak_a"))

        existing = get_by_slug(t["slug"])
        created_new = False
        if existing and existing.get("status") in ("draft", "publish", "pending", "private"):
            post = existing
            print(f"Reuse existing slug {t['slug']} -> {post['id']}")
        elif t["slug"] in state.get("created", {}):
            from ahsa_batch1_wp import get_post

            post = get_post(state["created"][t["slug"]]["id"])
            print(f"Reuse state id for {t['slug']} -> {post['id']}")
        else:
            post = create_draft(
                title=t["title"],
                content=html,
                slug=t["slug"],
                categories=[CATEGORY_ID, CATEGORY_LEAK, CATEGORY_LEAK_INSUL],
                featured_media=featured,
            )
            created_new = True
            try:
                update_rank_math(
                    post["id"],
                    {
                        "rank_math_title": rm_title,
                        "rank_math_description": meta_desc,
                        "rank_math_focus_keyword": t["focus"],
                    },
                )
                rm_ok = True
            except Exception as e:
                rm_ok = False
                post["_rankmath_error"] = str(e)[:300]
            state.setdefault("created", {})[t["slug"]] = {
                "id": post["id"],
                "link": post.get("link"),
                "word_count": wc,
                "rank_math": rm_ok,
            }
            save_state(state)
            print(f"Created draft {post['id']} {t['slug']} words={wc}")
            time.sleep(0.4)

        results.append(
            {
                "title": t["title"],
                "service": t["service"],
                "post_id": post.get("id", ""),
                "link": post.get("link", f"https://www.rukn-eltatawer.com/sa/?p={post.get('id')}"),
                "slug": t["slug"],
                "focus_keyword": t["focus"],
                "meta_description": meta_desc,
                "word_count": wc,
                "status": "مسودة" if post.get("status") == "draft" else post.get("status", "مسودة"),
                "decision": "created" if created_new else "reused",
                "skip_reason": "",
            }
        )

    fields = [
        "title",
        "service",
        "post_id",
        "link",
        "slug",
        "focus_keyword",
        "meta_description",
        "word_count",
        "status",
        "decision",
        "skip_reason",
    ]
    for dest in (
        REPORTS / "ahsa_batch1_creation_report.csv",
        STORE_DOCS / "ahsa_batch1_creation_report.csv",
    ):
        with dest.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(results)
        print("Wrote", dest)

    drafted = [r for r in results if r["status"] == "مسودة" or r.get("decision") == "created"]
    # Prefer counting newly relevant drafts (status مسودة from create targets)
    drafted_n = sum(1 for r in results if r.get("skip_reason") == "" and r.get("post_id"))
    skipped_n = sum(1 for r in results if r.get("skip_reason"))
    summary = {
        "auth_user": me.get("slug"),
        "drafted": drafted_n,
        "skipped": skipped_n,
        "word_counts": {r["slug"]: r["word_count"] for r in results if r.get("word_count")},
    }
    (REPORTS / "ahsa_batch1_creation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
