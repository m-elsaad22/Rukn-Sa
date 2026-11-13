# -*- coding: utf-8 -*-
"""Phase 1: audit 68 Bisha targets against live WP; write CSV + plan summary."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bisha_targets import (
    CATEGORY_ID,
    CATEGORY_NAME,
    GROUP_LABELS,
    PROPOSED_CATS,
    TARGETS,
)
from bisha_wp import get_by_slug, search_posts

ROOT = Path(__file__).resolve().parents[1]
STORE_DOCS = Path(
    os.environ.get(
        "BISHA_STORE_DOCS",
        "/cursor/stores/bc-64c23f33-0042-4da8-b945-442fb8d0b9d8/docs",
    )
)
REPORTS = ROOT / "reports" / "bisha"


def find_existing(title: str, slug: str, focus: str):
    """Return (exists_bool, post_or_none, reason)."""
    by_slug = get_by_slug(slug)
    if by_slug:
        return True, by_slug, "slug_match"

    # Exact / near title search
    for term in (title, focus, f"{focus} بيشة"):
        hits = search_posts(term, status="any")
        for p in hits:
            raw = (p.get("title") or {}).get("raw") or ""
            pslug = p.get("slug") or ""
            if "بيشة" not in raw and "bisha" not in pslug.lower():
                continue
            if raw.strip() == title or focus in raw:
                return True, p, "title_intent_match"
            if slug.replace("-bisha", "") in pslug and "bisha" in pslug:
                return True, p, "near_slug_bisha"
    return False, None, ""


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    STORE_DOCS.mkdir(parents=True, exist_ok=True)

    # Broader Bisha inventory
    bisha_posts = []
    seen = set()
    for term in ("بيشة", "bisha"):
        for p in search_posts(term, status="any"):
            if p["id"] in seen:
                continue
            seen.add(p["id"])
            bisha_posts.append(p)

    rows = []
    create_n = skip_n = 0
    for t in TARGETS:
        exists, post, reason = find_existing(t["title"], t["slug"], t["focus"])
        if exists:
            decision = "skip_duplicate"
            skip_n += 1
            existing_id = post["id"]
            existing_status = post.get("status")
        else:
            decision = "create_draft"
            create_n += 1
            existing_id = ""
            existing_status = ""
        rows.append(
            {
                "service_name": t["title"],
                "group": GROUP_LABELS[t["group"]],
                "category": CATEGORY_NAME,
                "category_id": CATEGORY_ID,
                "proposed_taxonomy_note": PROPOSED_CATS[t["group"]],
                "existing_article": "yes" if exists else "no",
                "existing_post_id": existing_id,
                "existing_status": existing_status,
                "match_reason": reason,
                "focus_keyword": t["focus"],
                "proposed_slug": t["slug"],
                "decision": decision,
            }
        )

    fieldnames = list(rows[0].keys())
    for dest in (REPORTS / "bisha_articles_audit.csv", STORE_DOCS / "bisha_articles_audit.csv"):
        with dest.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows)

    inventory = []
    for p in bisha_posts:
        inventory.append(
            {
                "id": p["id"],
                "status": p.get("status"),
                "slug": p.get("slug"),
                "title": (p.get("title") or {}).get("raw"),
                "link": p.get("link"),
                "categories": p.get("categories"),
            }
        )
    (REPORTS / "bisha_existing_inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    plan = f"""# خطة مقالات بيشة — المرحلة 1 (تدقيق)

**المهمة:** RSCA-6  
**الموقع:** https://www.rukn-eltatawer.com/sa/  
**التاريخ:** 2026-11-13  
**الهاتف لمسودات بيشة الجديدة فقط:** اتصال/واتساب `+966542264115` — SEO `0542264115`  
**لا تغيير** لأرقام المقالات المنشورة الحالية.

## ملخص التدقيق

| البند | العدد |
|--------|------:|
| عناوين مستهدفة رُوجعت | **{len(TARGETS)}** |
| قرار إنشاء مسودة | **{create_n}** |
| مستبعد لتكرار نية/Slug | **{skip_n}** |
| مقالات/صفحات بيشة موجودة مسبقاً (بحث عام) | **{len(inventory)}** |

## موجود مسبقاً في بيشة (خارج أو ضمن النطاق)

"""
    for item in inventory:
        plan += (
            f"- ID `{item['id']}` — `{item['status']}` — `{item['slug']}` — {item['title']}\n"
        )
    if not inventory:
        plan += "- لا يوجد.\n"

    plan += f"""

## التصنيفات

- التصنيف التشغيلي المستخدم في غالب مقالات الخدمات السعودية المنشورة: **الخدمات** (ID `{CATEGORY_ID}`).
- تصنيفات فرعية للتنظيف/المكافحة/الكهرباء موجودة في التصنيف لكن بدون ربط مقالات فعّال عبر REST؛ **لن ننشئ تصنيفات جديدة**.
- ملاحظات مقترحة للمرحلة اللاحقة موثّقة في عمود `proposed_taxonomy_note` داخل `bisha_articles_audit.csv`.

## صفحة مدينة بيشة

- **غير موجودة** ضمن `/sa/cities/` (على خلاف الرياض/جدة/أحساء…).
- وفق الموجز: **لا ننشئ صفحة مدينة**. الروابط الداخلية ستشير إلى `/sa/services/` و`/sa/cities/` و`/sa/water-leak-detection-bisha/` والمقالات الشقيقة ضمن الدفعة.

## قواعد المرحلة 2

1. إنشاء مسودات فقط للعناوين ذات القرار `create_draft`.
2. عدم النشر.
3. عدم تعديل/حذف/إعادة توجيه أي محتوى قائم.
4. عدم تغيير إعدادات Rank Math / Polylang / KAYAN العامة.
5. محتوى عربي مستقل 2000–2500 كلمة تقريباً لكل مسودة، مع SEO title يتضمن `0542264115` للمسودات الجديدة فقط.

## الملفات

- `{STORE_DOCS / 'bisha_articles_audit.csv'}`
- `{REPORTS / 'bisha_articles_audit.csv'}` (مرآة المستودع)
- `{REPORTS / 'bisha_existing_inventory.json'}`
"""

    for dest in (
        STORE_DOCS / "bisha_articles_plan_summary.md",
        REPORTS / "bisha_articles_plan_summary.md",
    ):
        dest.write_text(plan, encoding="utf-8")

    print(json.dumps({"audited": len(TARGETS), "create": create_n, "skip": skip_n, "existing_bisha": len(inventory)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
