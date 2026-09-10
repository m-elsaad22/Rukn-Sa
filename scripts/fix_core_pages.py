#!/usr/bin/env python3
"""Rewrite thin city/pricing hubs and clean leftover hype on core pages."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_client import PHONE, WA_INTL, get, put

ROOT = Path(__file__).resolve().parents[1]
PHONE_TEL = "0568060309"
BRAND = "ركن التطور"
NAVY = "#0A1F4E"
BLUE = "#2980D4"
TURQ = "#1AB8B8"
BG = "#F4F8FD"
TEXT = "#1C2E44"

SERVICE_LINKS = [
    ("كشف تسربات المياه", "https://www.rukn-eltatawer.com/sa/services/water-leak-detection/"),
    ("عزل الأسطح والخزانات", "https://www.rukn-eltatawer.com/sa/services/insulation-of-roofs-and-cabinets/"),
    ("التنظيف والتعقيم", "https://www.rukn-eltatawer.com/sa/services/cleaning-and-sterilization/"),
    ("مكافحة الحشرات", "https://www.rukn-eltatawer.com/sa/services/pest-control/"),
    ("المكيفات", "https://www.rukn-eltatawer.com/sa/services/air-conditioner-maintenance-and-installation/"),
    ("تسليك المجاري", "https://www.rukn-eltatawer.com/sa/services/sewer-wiring/"),
    ("المسابح", "https://www.rukn-eltatawer.com/sa/services/construction-and-maintenance-of-swimming-pools/"),
    ("تنسيق الحدائق", "https://www.rukn-eltatawer.com/sa/services/landscaping/"),
    ("الباركيه", "https://www.rukn-eltatawer.com/sa/services/parquet-installation/"),
    ("جبس بورد", "https://www.rukn-eltatawer.com/sa/services/gypsum-board-installation/"),
    ("عازل الصوت", "https://www.rukn-eltatawer.com/sa/services/sound-insulation-installation/"),
    ("صيانة المباني", "https://www.rukn-eltatawer.com/sa/services/construction-and-maintenance-of-buildings/"),
]


def wrap(inner: str) -> str:
    return (
        f'<div dir="rtl" style="font-family:Tahoma,Arial,sans-serif;line-height:1.9;color:{TEXT};font-size:16px;">'
        + inner
        + "</div>"
    )


def h2(t: str) -> str:
    return f'<h2 style="color:{NAVY};font-size:22px;margin:28px 0 12px;">{t}</h2>'


def lead(title: str, p: str) -> str:
    return (
        f'<div style="background:{BG};border-right:6px solid {BLUE};padding:22px;border-radius:16px;margin-bottom:24px;">'
        f'<p style="color:{BLUE};font-weight:800;font-size:20px;margin:0 0 10px;">{title}</p>'
        f"<p style=\"margin:0;\">{p}</p></div>"
    )


def cities_html(terms: list[dict]) -> str:
    cards = []
    for t in terms:
        name = t.get("name") or ""
        if name in ("السعودية",):
            continue
        link = t.get("link") or ""
        count = t.get("count") or 0
        cards.append(
            f'<a href="{link}" style="display:block;background:#fff;border:1px solid #E2EAF5;border-radius:14px;'
            f'padding:14px 16px;text-decoration:none;color:{TEXT};">'
            f'<strong style="color:{NAVY};">{name}</strong>'
            f'<span style="display:block;font-size:13px;color:#5b6b7c;margin-top:4px;">{count} موضوع خدمة محلي</span></a>'
        )
    grid = (
        '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px;margin:18px 0;">'
        + "".join(cards)
        + "</div>"
    )
    svc_list = "<ul>" + "".join(f'<li><a href="{u}">{n}</a></li>' for n, u in SERVICE_LINKS) + "</ul>"
    return wrap(
        lead(
            "المدن التي نخدمها في السعودية",
            f"هذه الصفحة دليل جغرافي لموقع {BRAND}. اختر مدينتك لعرض موضوعات الخدمة المحلية، أو ابدأ من صفحة الخدمة إن كنت تعرف نوع العمل. رقم التواصل الموحّد {PHONE_TEL}.",
        )
        + "<p>لا نستخدم تصنيفاً اسمه «السعودية» كمدينة؛ المملكة هي نطاق التغطية، والمدينة هي حيّز الوصول والجدولة.</p>"
        + h2("قائمة المدن")
        + grid
        + h2("ابدأ من الخدمة ثم المدينة")
        + "<p>إن كنت تعرف نوع العمل (تسرب، عزل، تنظيف، مكافحة…) افتح دليل الخدمة ثم انتقل لمقال مدينتك:</p>"
        + svc_list
        + h2("كيف تستخدم الصفحة؟")
        + "<ul><li>اختر المدينة.</li><li>افتح موضوع الخدمة الأقرب لعَرَضك.</li><li>صف الحي والعَرَض على واتساب أو اتصال.</li></ul>"
        + f'<p><a href="tel:{PHONE_TEL}" style="background:{NAVY};color:#fff;padding:12px 18px;border-radius:12px;text-decoration:none;display:inline-block;">اتصل {PHONE_TEL}</a> '
        f'<a href="https://wa.me/{WA_INTL}" style="background:#25D366;color:#fff;padding:12px 18px;border-radius:12px;text-decoration:none;display:inline-block;margin-right:8px;">واتساب</a></p>'
    )


def pricing_html() -> str:
    rows = ""
    factors = {
        "كشف تسربات المياه": "عدد النقاط، نوع التشطيب، الحاجة لفتح محدود",
        "عزل الأسطح والخزانات": "المساحة، حالة الميل، الرطوبة السابقة",
        "التنظيف والتعقيم": "المساحة، نوع الأسطح، درجة الاتساخ",
        "مكافحة الحشرات": "نوع الآفة، عدد الغرف، الحاجة لمتابعة",
        "المكيفات": "عدد الوحدات، سبب العطل، ارتفاع التركيب",
        "تسليك المجاري": "موضع الانسداد، إمكانية الكاميرا، تكرار الحالة",
        "المسابح": "حجم المسبح، نوع العطل (فلترة/تسرب/ماء)",
        "تنسيق الحدائق": "المساحة، الري، نوع الزراعة",
        "الباركيه": "المساحة ورطوبة الأرضية",
        "جبس بورد": "المتر ونقاط الإضاءة",
        "عازل الصوت": "المسار (جدار/سقف/باب) ومساحة الغرفة",
        "صيانة المباني": "أولوية العيب الإنشائي مقابل التجميل",
    }
    for name, url in SERVICE_LINKS:
        rows += (
            f'<tr><td style="padding:10px;border-bottom:1px solid #E2EAF5;"><a href="{url}">{name}</a></td>'
            f'<td style="padding:10px;border-bottom:1px solid #E2EAF5;">{factors.get(name, "حسب المعاينة")}</td>'
            f'<td style="padding:10px;border-bottom:1px solid #E2EAF5;">حسب المعاينة</td></tr>'
        )
    table = (
        f'<table style="width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;">'
        f'<thead><tr style="background:{NAVY};color:#fff;"><th style="padding:10px;text-align:right;">الخدمة</th>'
        f'<th style="padding:10px;text-align:right;">ما الذي يغيّر التكلفة؟</th>'
        f'<th style="padding:10px;text-align:right;">السعر الظاهر هنا</th></tr></thead><tbody>{rows}</tbody></table>'
    )
    return wrap(
        lead(
            "كيف نسعّر خدمات ركن التطور في السعودية؟",
            "لا نعرض رقماً ثابتاً مضللاً لكل طلب. تنظيف شقة في الرياض يختلف عن عزل سطح في جدة أو كشف تسرب في الدمام. هذه الصفحة تشرح عوامل التقدير وكيف تحصل على رقم يخص عقارك عبر المعاينة.",
        )
        + h2("لماذا لا توجد قائمة أسعار ثابتة؟")
        + "<p>السعر الثابت يناسب منتجاً معلّباً. الخدمات المنزلية تتغير مع المساحة، الوصول، التلف السابق، ونوع المادة المناسبة لمناخ المدينة. وضع رقم جزافي في الصفحة يضر صاحب العقار أكثر مما يساعده.</p>"
        + h2("عوامل التقدير لكل خدمة")
        + table
        + h2("ماذا يشمل العرض بعد المعاينة؟")
        + "<ul><li>وصف النطاق: ما سيُنفَّذ اليوم.</li><li>ما هو بند مساند إن ظهر سبب مرتبط.</li><li>ما الذي لا يدخل حتى لا يتوسع العمل دون اتفاق.</li></ul>"
        + h2("كيف تحصل على تقدير؟")
        + f"<p>راسلنا على {PHONE_TEL} واذكر: المدينة، الحي، نوع العقار، وصفاً لجملة واحدة للعَرَض، وصورة إن أمكن. هذا يكفي لترتيب المعاينة أو تقدير أوضح.</p>"
        + h2("أسئلة شائعة عن الأسعار")
        + "<h3>هل المعاينة ملزمة بتنفيذ؟</h3><p>لا. المعاينة لتوضيح النطاق. التنفيذ بعد اتفاقك.</p>"
        + "<h3>هل يتغير السعر أثناء العمل؟</h3><p>فقط إذا ظهر سبب جديد خارج النطاق المتفق عليه، ويُعرض عليك قبل التوسع.</p>"
        + f'<p style="margin-top:22px;"><a href="tel:{PHONE_TEL}" style="background:{NAVY};color:#fff;padding:12px 18px;border-radius:12px;text-decoration:none;">اتصل {PHONE_TEL}</a></p>'
    )


def scrub_page(raw: str) -> str:
    raw = raw.replace("الحل النهائي", "خيار عملي")
    raw = raw.replace("خيارك الأفضل والمضمون", "دليلك لخدمات الصيانة في السعودية")
    raw = raw.replace("تجربة استثنائية", "تجربة واضحة")
    raw = raw.replace("الجودة الفائقة", "تنفيذ مرتب")
    # leftover Egypt mentions if any
    raw = re.sub(r"جمهورية مصر العربية", "المملكة العربية السعودية", raw)
    raw = raw.replace("+201556644443", "+966568060309")
    raw = raw.replace("01556644443", "0568060309")
    raw = raw.replace("201151481000", "966568060309")
    return raw


def main() -> None:
    report = {}
    terms, _ = get("/wp/v2/cities?per_page=100")
    put("/wp/v2/pages/7465", {"content": cities_html(terms or []), "excerpt": f"دليل مدن {BRAND} في السعودية. تواصل {PHONE_TEL}."})
    report["cities"] = {"id": 7465, "terms": len(terms or [])}
    put("/wp/v2/pages/7464", {"content": pricing_html(), "excerpt": f"عوامل تسعير خدمات {BRAND} بدون أرقام مخترعة. {PHONE_TEL}"})
    report["pricing"] = {"id": 7464}

    for pid, key in ((7460, "about"), (7461, "contact"), (7463, "services")):
        page, _ = get(f"/wp/v2/pages/{pid}?context=edit")
        raw = (page.get("content") or {}).get("raw") or ""
        cleaned = scrub_page(raw)
        if cleaned != raw:
            put(f"/wp/v2/pages/{pid}", {"content": cleaned})
            report[key] = {"id": pid, "scrubbed": True}
        else:
            report[key] = {"id": pid, "scrubbed": False}

    out = ROOT / "reports" / "core-pages-fix.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
