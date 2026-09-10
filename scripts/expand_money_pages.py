#!/usr/bin/env python3
"""Deepen high-intent city+service money pages without inventing prices or reviews."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geo_packs import city_pack
from rewrite_unique_articles import (
    BRAND,
    PHONE_TEL,
    SKIP_IDS,
    build_article,
    load_index,
    parse_title,
    wc,
)
from service_packs import pack_for, pick_n

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

# Already unique long pages — do not shorten or overwrite.
PROTECTED = SKIP_IDS | {10274, 9333, 9287, 10293, 10292}

MONEY_PAIRS = [
    ("كشف تسربات المياه", ("الرياض", "جدة", "الدمام", "الخبر", "مكة المكرمة", "المدينة المنورة", "الطائف", "أبها")),
    ("عزل أسطح", ("الرياض", "جدة", "الدمام", "الخبر", "مكة المكرمة", "المدينة المنورة")),
    ("عزل فوم", ("الرياض", "جدة", "الدمام")),
    ("تنظيف شامل", ("الرياض", "جدة", "الدمام")),
    ("تنظيف منازل", ("الرياض", "جدة", "الدمام")),
    ("نقل عفش", ("الرياض", "جدة", "الدمام", "مكة المكرمة")),
    ("مكافحة بق", ("الرياض", "جدة", "الدمام")),
    ("مكافحة حشرات", ("الرياض", "جدة", "الدمام")),
    ("صيانة مكيفات", ("الرياض", "جدة", "الدمام", "الخبر")),
    ("تسليك مجاري", ("الرياض", "جدة", "الدمام")),
]


def extra_depth(title: str, svc: str, city: str) -> str:
    geo = city_pack(city)
    pack = pack_for(svc)
    districts = geo["districts"]
    seed = title
    local_ops = pick_n(
        seed + "ops",
        [
            f"في {districts[0]} نسأل عن نوع العقار (شقة أو فيلا) قبل تحميل المعدات.",
            f"أحياء مثل {districts[1]} و{districts[2]} تختلف في سهولة الوقوف وإدخال العدد.",
            f"{geo['note']}",
            f"المناخ المحلي: {geo['climate']}. هذا يغيّر ترتيب التجفيف أو العزل أو التبريد حسب الخدمة.",
            f"طبيعة العقار هنا: {geo['property']}.",
        ],
        5,
    )
    season = pick_n(
        seed + "season",
        [
            "قبل ذروة الحر نفحص التبريد والتصريف لأن الشكوى تتفاقم خلال أسبوع.",
            "بعد موجة غبار نراجع الفلاتر والوحدات الخارجية إن كانت الخدمة تكييفاً أو نظافة واجهات.",
            "بعد أمطار مفاجئة نراجع الأسطح ونقاط الميل قبل أي طبقة تجميل.",
            "في الرطوبة الساحلية نؤخر الدهان فوق عزل غير مستقر.",
        ],
        3,
    )
    questions = [
        f"أين ظهر العَرَض أول مرة داخل {city}؟",
        "هل هو جديد أم متكرر بعد محاولة سابقة؟",
        "هل يتأثر الاستخدام اليومي (ماء، تبريد، نوم، رائحة)؟",
        f"ما الحي؟ مثال شائع في الطلبات: {districts[0]}.",
    ]
    return "\n".join(
        [
            f"<h2>تفاصيل تشغيل {esc_safe(svc)} داخل {esc_safe(city)}</h2>",
            f"<p>بعد الإطار العام للخدمة، هذا القسم يخص {esc_safe(city)} في {esc_safe(geo['region'])}.</p>",
            "<ul>" + "".join(f"<li>{x}</li>" for x in local_ops) + "</ul>",
            f"<h2>أسئلة نطرحها في أول تواصل من {esc_safe(city)}</h2>",
            "<p>الإجابات المختصرة تختصر الزيارة:</p>",
            "<ul>" + "".join(f"<li>{q}</li>" for q in questions) + "</ul>",
            f"<h2>الترتيب الموسمي للعمل في {esc_safe(geo['region'])}</h2>",
            "<ul>" + "".join(f"<li>{x}</li>" for x in season) + "</ul>",
            f"<h2>ما الذي لا نعدك به في صفحة {esc_safe(title)}</h2>",
            "<p>لا نضع سعراً ثابتاً لا يخص مساحة منزلك، ولا نختلق تقييماً أو عدد عملاء. "
            f"نوضح نطاق {esc_safe(svc)} بعد المعاينة، ونتواصل عبر {PHONE_TEL}.</p>",
            f"<h2>وقاية بعد {esc_safe(svc)} في {esc_safe(city)}</h2>",
            f"<p>{esc_safe(pack['what'])} بعد التسليم راقب العَرَض 48–72 ساعة إن كانت الحالة رطوبة أو آفات أو تبريد. "
            f"لا تغطِّ الأثر بدهان أو عطر قبل التأكد من الاستقرار.</p>",
            f"<p>إن عاد العَرَض بسرعة، أعد التواصل مبكراً واذكر أن الزيارة كانت في {esc_safe(city)} مع اسم الحي.</p>",
        ]
    )


def esc_safe(s: str) -> str:
    from rewrite_unique_articles import esc

    return esc(s)


def pick_money_rows(rows: list[dict]) -> list[dict]:
    chosen = []
    seen = set()
    for needle, cities in MONEY_PAIRS:
        for city in cities:
            for r in rows:
                if r["id"] in PROTECTED or r["id"] in seen:
                    continue
                title = r.get("title") or ""
                if needle in title and city in title:
                    chosen.append(r)
                    seen.add(r["id"])
                    break
        if len(chosen) >= 32:
            break
    return chosen[:32]


def main() -> None:
    rows = json.loads((DATA / "audit-posts.json").read_text(encoding="utf-8"))
    money = pick_money_rows(rows)
    index = load_index(rows)
    results = []
    errors = []
    for row in money:
        try:
            built = build_article(row, index)
            city, svc = parse_title(row["title"])
            extra = extra_depth(row["title"], svc, city)
            html = built["content"]
            marker = "<h2>أسئلة شائعة"
            if marker in html:
                html = html.replace(marker, extra + marker, 1)
            else:
                html += extra
            built["content"] = html
            built["words"] = wc(html)
            # reuse rewrite_one payload path but with our html
            from rewrite_unique_articles import ensure_city, ensure_tag, update_rankmath
            from wp_client import put

            tag_ids = [tid for t in built["tags"] if (tid := ensure_tag(t))]
            city_id = ensure_city(built["city"])
            payload = {"content": built["content"], "excerpt": built["excerpt"], "meta": built["meta"]}
            if tag_ids:
                payload["tags"] = tag_ids
            if city_id:
                payload["cities"] = [city_id]
            put(f"/wp/v2/posts/{row['id']}", payload)
            update_rankmath(row["id"], built["rank_math"])
            results.append({"id": row["id"], "title": row["title"], "words": built["words"], "city": city, "svc": svc})
            print("OK", row["id"], built["words"], row["title"][:60], flush=True)
        except Exception as e:
            errors.append({"id": row["id"], "error": str(e)[:400]})
            print("ERR", row["id"], e, flush=True)

    report = {"updated": results, "errors": errors, "count": len(results)}
    out = ROOT / "reports" / "money-pages-expand.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": len(results), "err": len(errors)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
