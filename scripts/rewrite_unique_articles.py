#!/usr/bin/env python3
"""Rewrite thin/similar/mismatched /sa posts into unique on-topic articles
and fill Kayan shortcode blocks, FAQs, schema, Rank Math, tags, and cities.
"""
from __future__ import annotations

import html as html_lib
import json
import re
import sys
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geo_packs import CITIES, city_pack, ALIASES
from service_packs import pack_for, pick, pick_n, hid, family_of
from wp_client import get, post, put, PHONE, WHATSAPP, WA_INTL

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SKIP_IDS = {10603, 10604}  # already unique long hubs with filled blocks
PHONE_TEL = "0568060309"
BRAND = "ركن التطور"
NAVY = "#0A1F4E"
NAVY2 = "#1A3A6B"
BLUE = "#2980D4"
TURQ = "#1AB8B8"
BG = "#F4F8FD"
BORDER = "#E2EAF5"
TEXT = "#1C2E44"
GOLD = "#F4A428"
OK = "#18C96A"
WARN = "#991229"
WA = "#25D366"

IMG = {
    "leak": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2026/08/water-leak-detection.webp",
    "insul_water": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2026/08/roof-insulation-ae.webp",
    "insul_thermal": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2020/10/temperature-3.webp",
    "insul_sound": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/12/toolbox.webp",
    "insul_kitchen": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/08/plumbing.webp",
    "insul_bath": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2020/10/waterproof-fabric-3.webp",
    "tank": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2020/10/water-pollution.webp",
    "pest": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/12/clean-2.webp",
    "clean": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/12/cleaning-6.webp",
    "move": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/12/toolbox.webp",
    "ac": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/08/plumber-1.webp",
    "plumb": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/08/plumbing.webp",
    "elec": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/08/electrical-maintenance.webp",
    "paint": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/12/toolbox.webp",
    "gypsum": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/12/toolbox.webp",
    "garden": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/12/cleaning-6.webp",
    "pool": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/12/pool-cleaning.webp",
    "default": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/12/toolbox.webp",
}
for k in list(CORE_FAM_IMG := [
    "pest_bedbug", "pest_gecko", "pest_scorpion", "pest_birds", "pest_fly",
    "pest_ant", "pest_flea", "pest_snake", "clean_tank", "clean_diesel",
    "clean_facade", "clean_upholstery", "piano", "wallpaper", "tile", "stone",
    "floor", "kitchen", "humidity", "inspect", "restore", "appliance", "access",
    "shipping", "carpenter", "blacksmith", "satellite", "audio", "water_air",
    "install", "maint", "trade",
]):
    IMG.setdefault(k, IMG["default"])
IMG["pest_bedbug"] = IMG["pest"]
IMG["pest_gecko"] = IMG["pest"]
IMG["pest_scorpion"] = IMG["pest"]
IMG["pest_birds"] = IMG["pest"]
IMG["pest_fly"] = IMG["pest"]
IMG["pest_ant"] = IMG["pest"]
IMG["pest_flea"] = IMG["pest"]
IMG["pest_snake"] = IMG["pest"]
IMG["clean_tank"] = IMG["tank"]
IMG["clean_diesel"] = IMG["tank"]
IMG["clean_facade"] = IMG["clean"]
IMG["clean_upholstery"] = IMG["clean"]
IMG["humidity"] = IMG["insul_bath"]
IMG["restore"] = IMG["paint"]
IMG["wallpaper"] = IMG["paint"]
IMG["kitchen"] = IMG["plumb"]
IMG["water_air"] = IMG["plumb"]

CITY_PAT = sorted(list(CITIES.keys()) + list(ALIASES.keys()), key=len, reverse=True)


def esc(s: str) -> str:
    return html_lib.escape(s or "", quote=True)


def wc(html: str) -> int:
    t = re.sub(r"\[[^\]]+\]", " ", html or "")
    t = re.sub(r"<[^>]+>", " ", t)
    t = html_lib.unescape(t)
    return len(re.findall(r"[\w\u0600-\u06FF]+", t))


def parse_title(title: str) -> tuple[str, str]:
    city = "السعودية"
    found = None
    for c in CITY_PAT:
        if c in title:
            found = ALIASES.get(c, c)
            if found == "مكة":
                found = "مكة المكرمة"
            if found == "المدينة":
                found = "المدينة المنورة"
            city = found
            break
    svc = title
    svc = re.sub(r"^شركة\s+", "", svc)
    svc = re.sub(r"^فني\s+", "", svc)
    names = []
    if found:
        names.append(found)
    names.extend(CITY_PAT)
    for c in names:
        c2 = ALIASES.get(c, c)
        for token in {c, c2}:
            svc = re.sub(rf"(?:بال|ب|في\s+|ل)?{re.escape(token)}", " ", svc)
    svc = re.sub(r"\|\s*.*$", "", svc)
    svc = re.sub(r"\s{2,}", " ", svc).strip(" |/-")
    svc = re.sub(r"\s+(?:في|ب)$", "", svc).strip()
    svc = re.sub(r"\s+في\s+(?:وسط|شمال|جنوب|شرق|غرب)$", "", svc).strip()
    svc = re.sub(r"\s+(?:وسط|شمال|جنوب|شرق|غرب)$", "", svc).strip()
    if svc.endswith(" داخل"):
        svc = svc[: -len(" داخل")].strip()
    return city, svc or title


def img_tag(src: str, alt: str, eager: bool = False) -> str:
    loading = "eager" if eager else "lazy"
    return (
        f'<p style="margin:24px 0 8px;"><img src="{esc(src)}" alt="{esc(alt)}" '
        f'width="800" height="450" loading="{loading}" decoding="async" '
        f'style="width:100%;max-width:100%;height:auto;border-radius:16px;'
        f'display:block;box-shadow:0 12px 32px rgba(10,31,78,.10);" /></p>'
    )


def box(title: str, body: str, color: str = NAVY) -> str:
    return (
        f'<div style="background:{BG};border:1px solid {BORDER};border-right:5px solid {color};'
        f'border-radius:16px;padding:16px 18px;margin:18px 0;">'
        f'<p style="margin:0 0 8px;color:{color};font-weight:800;">{title}</p>'
        f'<p style="margin:0;color:{TEXT};">{body}</p></div>'
    )


def warning(text: str) -> str:
    return (
        f'<blockquote style="background:#FFF5F5;border-right:5px solid {WARN};'
        f'border-radius:16px;padding:14px 16px;margin:18px 0;">'
        f'<i class="fa-solid fa-triangle-exclamation" style="color:{WARN};"></i> '
        f'<strong>تنبيه:</strong> {text}</blockquote>'
    )


def tip(text: str) -> str:
    return (
        f'<blockquote style="background:#F3FFFB;border-right:5px solid {TURQ};'
        f'border-radius:16px;padding:14px 16px;margin:18px 0;">'
        f'<i class="fa-solid fa-lightbulb" style="color:{GOLD};"></i> '
        f'<strong>نصيحة عملية:</strong> {text}</blockquote>'
    )


def cards(items: list[tuple[str, str, str]]) -> str:
    parts = [
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));'
        'gap:12px;margin:18px 0;">'
    ]
    for icon, h, p in items:
        parts.append(
            f'<div style="background:#fff;border:1px solid {BORDER};border-radius:16px;'
            f'padding:16px;box-shadow:0 4px 16px rgba(10,31,78,.06);">'
            f'<div style="color:{BLUE};font-size:22px;margin-bottom:8px;"><i class="fa-solid {icon}"></i></div>'
            f'<h3 style="margin:0 0 6px;color:{NAVY};font-size:17px;">{h}</h3>'
            f'<p style="margin:0;color:{TEXT};font-size:15px;line-height:1.7;">{p}</p></div>'
        )
    parts.append("</div>")
    return "".join(parts)


def steps_html(items: list[tuple[str, str]]) -> str:
    parts = ['<div style="display:grid;gap:10px;margin:18px 0;">']
    for i, (h, p) in enumerate(items, 1):
        n = f"{i:02d}"
        parts.append(
            f'<div style="display:flex;gap:12px;align-items:flex-start;background:{BG};'
            f'border:1px solid {BORDER};border-radius:16px;padding:14px 16px;">'
            f'<span style="flex:0 0 42px;height:42px;border-radius:50%;background:{NAVY};color:#fff;'
            f'display:flex;align-items:center;justify-content:center;font-weight:800;">{n}</span>'
            f'<div><h3 style="margin:0 0 4px;color:{NAVY};font-size:17px;">{h}</h3>'
            f'<p style="margin:0;color:{TEXT};">{p}</p></div></div>'
        )
    parts.append("</div>")
    return "".join(parts)


def table(headers: list[str], rows: list[list[str]]) -> str:
    th = "".join(f'<th style="padding:10px;background:{NAVY};color:#fff;text-align:right;">{esc(h)}</th>' for h in headers)
    body = []
    for i, row in enumerate(rows):
        bg = "#fff" if i % 2 == 0 else BG
        tds = "".join(f'<td style="padding:10px;border-bottom:1px solid {BORDER};">{c}</td>' for c in row)
        body.append(f'<tr style="background:{bg};">{tds}</tr>')
    return (
        f'<div class="responsive-table" style="overflow-x:auto;-webkit-overflow-scrolling:touch;margin:18px 0;">'
        f'<table style="width:100%;min-width:480px;border-collapse:collapse;border-radius:12px;overflow:hidden;">'
        f'<thead><tr>{th}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'
    )


def author_box() -> str:
    return (
        f'<div style="background:{BG};border:1px solid {BORDER};padding:14px 16px;margin:16px 0;'
        f'border-radius:12px;font-size:14px;color:{TEXT};">'
        f'<i class="fa-solid fa-pen"></i> <strong>كتب هذا المقال:</strong> فريق المحتوى الفني في {BRAND}'
        f' &nbsp;|&nbsp; <i class="fa-solid fa-calendar"></i> <strong>آخر تحديث:</strong> سبتمبر 2026'
        f' &nbsp;|&nbsp; <i class="fa-solid fa-check"></i> <strong>مراجعة:</strong> فريق العمليات'
        f"</div>"
    )


def hero(svc: str, city: str, value: str) -> str:
    return (
        f'<section style="background:linear-gradient(135deg,{NAVY} 0%,{NAVY2} 48%,{TURQ} 100%);'
        f'color:#fff;border-radius:24px;padding:26px 20px;margin:18px 0;">'
        f'<span style="display:inline-block;background:rgba(255,255,255,.14);padding:4px 10px;'
        f'border-radius:999px;font-size:12px;margin-bottom:10px;">خدمة ميدانية في {esc(city)}</span>'
        f'<h2 style="color:#fff;margin:0 0 8px;font-size:22px;line-height:1.45;">{esc(svc)} داخل {esc(city)}</h2>'
        f'<p style="margin:0 0 14px;opacity:.95;">{value}</p>'
        f'<div style="display:flex;flex-wrap:wrap;gap:8px;">'
        f'<a href="tel:{PHONE_TEL}" style="background:#fff;color:{NAVY};padding:12px 18px;border-radius:12px;'
        f'font-weight:800;text-decoration:none;min-height:44px;display:inline-flex;align-items:center;gap:6px;">'
        f'<i class="fa-solid fa-phone"></i> اتصل الآن</a>'
        f'<a href="https://wa.me/{WA_INTL}" style="background:{WA};color:#fff;padding:12px 18px;border-radius:12px;'
        f'font-weight:800;text-decoration:none;min-height:44px;display:inline-flex;align-items:center;gap:6px;">'
        f'<i class="fa-brands fa-whatsapp"></i> واتساب</a></div></section>'
    )


def cta(svc: str, city: str) -> str:
    return (
        f'<section style="background:{NAVY};color:#fff;border-radius:20px;padding:22px 18px;margin:22px 0;text-align:center;">'
        f'<i class="fa-solid fa-headset" style="font-size:26px;color:{TURQ};"></i>'
        f'<h2 style="color:#fff;margin:8px 0;">هل تحتاج {esc(svc)} في {esc(city)}؟</h2>'
        f'<p style="margin:0 0 12px;">صف العَرَض والحي عبر {PHONE_TEL} لنحدد نطاقاً واضحاً قبل التنفيذ.</p>'
        f'<a href="tel:{PHONE_TEL}" style="background:{TURQ};color:{NAVY};padding:12px 18px;border-radius:12px;'
        f'font-weight:800;text-decoration:none;display:inline-block;">اتصل على {PHONE_TEL}</a></section>'
    )


def ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def related_links(city: str, svc: str, index: dict, n: int = 3) -> str:
    bucket = index.get(city) or []
    links = []
    for item in bucket:
        if item["svc"] == svc:
            continue
        links.append(item)
        if len(links) >= n:
            break
    if not links:
        return ""
    lis = "".join(
        f'<li><a href="{esc(it["link"])}">{esc(it["title"])}</a></li>' for it in links
    )
    return f"<h2>خدمات مرتبطة داخل {esc(city)}</h2><p>قد تحتاج بنداً مسانداً حسب نتيجة المعاينة:</p><ul>{lis}</ul>"


def build_faqs(svc: str, city: str, pack: dict, districts: list[str], seed: str) -> list[dict]:
    dcsv = "، ".join(districts[:4])
    pool = [
        {"q": f"ما هي خدمة {svc} في {city}؟", "a": f"{pack['what']} نقدّمها في {city} بعد معاينة العقار وتحديد النطاق."},
        {"q": f"متى أحتاج {svc} داخل {city}؟", "a": f"عندما يظهر {pack['problem']} أو عندما تريد تجهيزاً مرتباً قبل انتقال أو موسم ذروة في {city}."},
        {"q": f"هل تغطون أحياء {city}؟", "a": f"نعم حسب الجدولة اليومية، ومن الأحياء التي نصل إليها غالباً: {dcsv}."},
        {"q": f"كم تكلفة {svc} في {city}؟", "a": "لا نضع رقماً ثابتاً لا يمثّل عقارك. التكلفة تتأثر بالمساحة ودرجة الحالة وسهولة الوصول ونوع المواد، وتُوضَّح بعد فهم العَرَض."},
        {"q": "هل المعاينة قبل التنفيذ؟", "a": "نعم. نوضّح ما سيدخل في النطاق وما لن يدخل، وأي احتمال لأعمال إضافية بعد اكتشاف جديد."},
        {"q": "كم تستغرق الزيارة؟", "a": "تختلف حسب المساحة وتعقيد الحالة. نوضّح تقديراً زمنياً بعد وصفك للحي ونوع العقار."},
        {"q": f"هل الخدمة للشقق والفلل في {city}؟", "a": f"نعم. نضبط الخطة حسب التشطيب وسهولة الوصول في شقق وفلل {city}."},
        {"q": "ما الأخطاء التي تؤخر الحل؟", "a": "من أبرزها: " + "، ".join(pack["mistakes"][:3]) + "."},
        {"q": "هل تستخدمون مواد أو أجهزة محددة؟", "a": "نختار الأدوات حسب الحالة بعد المعاينة. أمثلة شائعة: " + "، ".join(pack["tools"][:3]) + "."},
        {"q": f"كيف أحجز {svc} في {city}؟", "a": f"عبر الاتصال أو واتساب على {PHONE_TEL}. اذكر الحي ونوع العقار ووصفاً مختصراً للعَرَض."},
        {"q": "هل يوجد ضمان؟", "a": "نطاق الضمان يُوضَّح قبل البدء حسب نوع العمل والخامة المستخدمة، دون وعود عامة خارج الاتفاق."},
        {"q": "ماذا أحضّر قبل وصول الفريق؟", "a": "وصف العَرَض، إتاحة وصول آمن للنقطة، وذكر أي محاولة سابقة على نفس الموضع."},
    ]
    chosen = pick_n(seed + "|faq", pool, 10)
    return [{"question": x["q"], "answer": x["a"]} for x in chosen]


def build_article(post: dict, index: dict) -> dict:
    title = post["title"]
    city, svc = parse_title(title)
    seed = f"{post['id']}|{title}"
    geo = city_pack(city)
    pack = pack_for(svc)
    fam = pack["family"]
    districts = geo["districts"]
    dcsv = "، ".join(districts[:5])
    img = IMG.get(fam, IMG["default"])
    img2 = IMG.get("default") if img == IMG.get("default") else IMG.get("clean", IMG["default"])
    if fam in ("leak", "plumb"):
        img2 = IMG["plumb"]
    icon = pack["icon"]
    kw = title if title.startswith("شركة") or title.startswith("فني") else f"شركة {svc} في {city}"

    intros = [
        f"إذا لاحظت {pack['problem']} داخل عقارك في <strong>{esc(city)}</strong>، فالمطلوب ليس حلاً عاماً بل خطة تناسب هذه الخدمة تحديداً: <strong>{esc(svc)}</strong>.",
        f"البحث عن <strong>{esc(svc)}</strong> في <strong>{esc(city)}</strong> يبدأ من فهم العَرَض: {pack['problem']} ثم تحديد نطاق التنفيذ قبل أي توسع.",
        f"في {esc(city)} يختلف الطلب على <strong>{esc(svc)}</strong> حسب نوع العقار. {esc(geo['property'])}. لذلك نبدأ بالمعاينة لا بالتخمين.",
    ]
    lead2 = [
        f"{pack['what']} شركة <strong>{BRAND}</strong> تنفّذ ذلك ميدانياً في {esc(city)} ({esc(geo['region'])}) مع وضوح النطاق ورقم موحّد {PHONE_TEL}.",
        f"نقدّم <strong>{esc(svc)}</strong> بأسلوب ميداني: وصف العَرَض، معاينة، ثم اتفاق على النطاق. {esc(geo['note'])}.",
        f"الهدف أن تعرف قبل البدء: ما السبب المحتمل؟ ما الذي سيُنفَّذ اليوم؟ وما الذي يمكن تأجيله داخل منزلك في {esc(city)}؟",
    ]
    layout = hid(seed) % 6

    signs = pick_n(seed, pack["signs"], min(5, len(pack["signs"])))
    causes = pick_n(seed + "c", pack["causes"], min(4, len(pack["causes"])))
    methods = pick_n(seed + "m", pack["methods"], min(5, len(pack["methods"])))
    mistakes = pick_n(seed + "x", pack["mistakes"], min(4, len(pack["mistakes"])))
    tools = pack["tools"]

    feat_cards = [
        (icon, "تشخيص قبل التوسع", f"نربط {svc} بالعَرَض الظاهر داخل {city} قبل أي فك أو تركيب واسع."),
        ("fa-map-location-dot", f"تغطية {city}", f"نصل حسب الجدول إلى أحياء منها {dcsv}."),
        ("fa-clipboard-list", "نطاق مكتوب", "ما يدخل وما لا يدخل يتضح قبل التنفيذ."),
        ("fa-shield-halved", "حماية التشطيب", "نقلّل الضرر على الأرضيات والأثاث المجاور قدر الإمكان."),
        ("fa-clock", "ترتيب الزيارة", "ذكر الحي ونوع العقار يختصر التجهيز من أول تواصل."),
        ("fa-comments", "لغة واضحة", "بدون مبالغة تسويقية؛ نشرح الخيارات كما هي على أرض الواقع."),
    ]
    feat_cards = pick_n(seed + "fc", feat_cards, 4)

    step_items = [
        ("التواصل", f"اتصل أو راسل واتساب على {PHONE_TEL} واذكر الحي داخل {city} ووصف {svc}."),
        ("المعاينة", "نرى موضع العمل ونقارنه بنوع العقار والتشطيب."),
        ("تحديد النطاق", "نشرح الخيار العملي وما قد يظهر بعد الفتح أو الفك إن لزم."),
        ("التنفيذ", f"تنفيذ {svc} بالأدوات المناسبة للحالة لا بقالب ثابت."),
        ("المراجعة", "نتأكد من النقاط المتفق عليها ونترك ملاحظات وقاية تخص هذه الخدمة."),
    ]
    if layout % 2:
        step_items.insert(3, ("التجهيز", "حماية الأسطح المجاورة وإخلاء مسار آمن للمعدات."))

    cost_factors = pick_n(
        seed + "cost",
        [
            "مساحة العمل وعدد النقاط",
            "درجة التلف أو الإهمال السابق",
            "سهولة الوصول (دور عالٍ، مصعد، سطح)",
            "نوع المواد المناسبة لمناخ " + city,
            "الحاجة لبند مساند بعد المعاينة",
            "الوقت المتاح إن كان العمل طارئاً",
        ],
        5,
    )

    type_rows = [
        [f"{svc} للنقطة المحددة", "إغلاق عَرَض واضح في موضع واحد", "أقل تدخلاً إذا شُخّص المصدر"],
        [f"{svc} لنطاق غرفة/جناح", "عدة نقاط مترابطة داخل نفس المساحة", "أنسب عند تكرار العَرَض"],
        ["بند مساند بعد المعاينة", "لا يُفرض إلا إذا ظهر سبب مرتبط", "يمنع عودة المشكلة من مصدر آخر"],
    ]
    cmp_rows = [
        ["التشخيص", "معاينة مربوطة بنوع الخدمة", "تخمين أو حل عام لكل الأعطال"],
        ["النطاق", "مكتوب قبل التنفيذ", "يتوسع أثناء العمل دون اتفاق"],
        ["المواد", "حسب السطح ومناخ " + city, "أرخص خامة دون ملاءمة"],
        ["النتيجة", "مراجعة النقاط المتفق عليها", "مغادرة فور اختفاء العَرَض شكلياً"],
    ]

    h_when = pick(seed, [f"متى تحتاج {svc} في {city}؟", f"علامات تستدعي {svc} الآن", f"هل مشكلتك تناسب {svc}؟"])
    h_how = pick(seed, [f"كيف تتم خدمة {svc} خطوة بخطوة؟", f"مسار العمل داخل {city}", f"من المعاينة حتى التسليم"])
    h_cost = pick(seed, [f"كم تكلفة {svc} في {city}؟", f"ما الذي يغيّر سعر {svc}؟", f"الوقت والتكلفة بدون رقم عشوائي"])

    internal = related_links(city, svc, index)
    faqs = build_faqs(svc, city, pack, districts, seed)

    parts: list[str] = []
    parts.append(f'<p style="font-size:1.2em;font-weight:800;color:{BLUE};line-height:1.55;margin:0 0 12px;">{esc(title)}</p>')
    parts.append(author_box())
    parts.append(f"<p>{pick(seed, intros)}</p>")
    parts.append(f"<p>{pick(seed, lead2, 1)}</p>")
    parts.append(f"<p>{esc(geo['climate'])}. هذا يؤثر على طريقة تنفيذ <strong>{esc(svc)}</strong> أكثر من أي قالب جاهز لمدينة أخرى.</p>")
    parts.append("[post_call]")
    parts.append(hero(svc, city, pack["what"]))
    parts.append(img_tag(img, f"{title} — {BRAND}", eager=True))

    sec_what = (
        f"<h2>ما هي خدمة {esc(svc)}؟</h2>"
        f"<p>{esc(pack['what'])}</p>"
        f"<p>في <strong>{esc(city)}</strong> نواجه {esc(geo['property'])}. لذلك لا ننسخ خطوات مدينة أخرى حرفياً؛ نسأل عن الحي (مثل {esc(districts[0])} أو {esc(districts[1])}) ونوع الاستخدام اليومي.</p>"
        + cards([(c[0], c[1], c[2]) for c in feat_cards])
        + "[post_features]"
    )
    sec_when = (
        f"<h2>{esc(h_when)}</h2>"
        f"<p>ابدأ بالسؤال المباشر: هل العَرَض يؤثر على الاستخدام اليومي أم أنه تجميلي فقط؟ لـ{esc(svc)} داخل {esc(city)} غالباً تظهر الحاجة عند:</p>"
        + ul(signs)
        + warning(f"تأجيل {svc} بعد ظهور {pack['signs'][0]} قد يوسّع نطاق المواد والوقت لاحقاً.")
        + f"<p>مثال محلي: عقار في {esc(districts[2 % len(districts)])} قد يختلف عن آخر في {esc(districts[3 % len(districts)])} بسبب {esc(geo['climate']).split('مع')[0].strip()} وسهولة وقوف المعدات.</p>"
    )
    sec_why = (
        f"<h2>لماذا تظهر المشكلة المرتبطة بـ{esc(svc)}؟</h2>"
        f"<p>الأسباب ليست واحدة في كل بيت. داخل {esc(city)} نراجع غالباً:</p>"
        + ul(causes)
        + tip(f"صوّر العَرَض واذكر إن كان جديداً أم متكرراً. هذه الجملة تختصر زيارة {svc} أكثر من أي وصف إنشائي.")
    )
    sec_how = (
        f"<h2>{esc(h_how)}</h2>"
        + steps_html([(a, b) for a, b in step_items])
        + "[post_steps]"
        + f"<p>خلال التنفيذ نستخدم ما يناسب الحالة، ومن الأدوات الشائعة: {esc('، '.join(tools))}.</p>"
        + img_tag(img2, f"تنفيذ {svc} في {city}")
        + f"<p>إذا ظهر بند مساند (مثل {esc(pack['related'][0])} عند الحاجة فقط) نوضحه بصراحة بدل إخفائه أو فرض باقة غير لازمة.</p>"
    )
    sec_types = (
        f"<h2>كيف نحدد نطاق {esc(svc)} المناسب؟</h2>"
        f"<p>لا يوجد «مقاس واحد». الجدول التالي يوضح فروقاً عملية دون اختراع أسعار:</p>"
        + table(["النطاق", "متى يناسب", "الفائدة"], type_rows)
        + "[post_prices]"
    )
    sec_cmp = (
        f"<h2>الفرق بين التنفيذ المرتب والحل السريع</h2>"
        + table(["المعيار", f"{BRAND}", "حل مرتجل"], cmp_rows)
        + f"<p>الحل السريع قد يخفف العَرَض ساعات. التنفيذ المرتب لـ{esc(svc)} في {esc(city)} يمر عبر السبب ثم أقل تدخل كافٍ ثم وقاية تناسب {esc(geo['climate'])}.</p>"
    )
    sec_area = (
        f"<h2>أحياء {esc(city)} التي نصل إليها</h2>"
        f"<p>نخدم نطاق {esc(geo['region'])} ومن الأحياء المتكررة في طلبات {esc(svc)}: {esc(dcsv)}. {esc(geo['note'])}.</p>"
        f"<p>اذكر اسم الحي حتى لو كان خارج القائمة؛ نخبرك بإمكانية نفس اليوم أو أقرب جدولة.</p>"
    )
    sec_prep = (
        f"<h2>ماذا تجهز قبل الزيارة؟</h2>"
        + ul(
            [
                f"وصف العَرَض بجملة واحدة مع ذكر {esc(city)} والحي.",
                "إتاحة وصول آمن لنقطة العمل وإبعاد العوائق البسيطة.",
                "الإفصاح عن أي مادة أو محاولة سابقة على نفس الموضع.",
                "تحديد الأولوية إن كان الوقت ضيقاً (أهم غرفة أولاً).",
            ]
        )
    )
    sec_cost = (
        f"<h2>{esc(h_cost)}</h2>"
        f"<p>لا نعرض هنا أرقاماً مخترعة لا تمثّل منزلك. تكلفة {esc(svc)} في {esc(city)} تتأثر بـ:</p>"
        + ul(cost_factors)
        + f"<p>للحصول على تقدير أوضح: صف العَرَض، اذكر الحي، وحدّد إن كانت الحالة جديدة أم متكررة. تواصل على {PHONE_TEL}.</p>"
    )
    sec_err = (
        f"<h2>أخطاء شائعة تؤخر {esc(svc)}</h2>"
        + ul(mistakes)
        + warning("مقارنة السعر فقط دون سؤال عن أسلوب التشخيص قد يعيد المشكلة خلال أيام.")
    )
    sec_after = (
        f"<h2>بعد انتهاء العمل داخل {esc(city)}</h2>"
        f"<p>راقب النتيجة 48–72 ساعة إن كانت الخدمة تتعلق برطوبة أو حشرات أو تبريد. لا تغطِّ الأثر بدهان أو عطر قبل التأكد من استقرار الحالة. إذا عاد العَرَض بسرعة، تواصل مبكراً على {PHONE_TEL}.</p>"
        + tip(f"اربط المتابعة الموسمية بمناخ {city}: {geo['climate']}.")
    )
    sec_tech = (
        f"<h2>تفاصيل فنية لـ{esc(svc)} تناسب {esc(city)}</h2>"
        f"<p>بعد تحديد النطاق نراجع طريقة التنفيذ. لـ{esc(svc)} نعتمد عادةً على: {esc('، '.join(methods))}.</p>"
        f"<p>كل بند يغيّر الوقت والأدوات. في {esc(city)} حيث {esc(geo['property'])} نسأل عن ارتفاع الدور ووجود مصعد وحساسية الأرضيات قبل نقل المعدات.</p>"
        f"<p>الأدوات الشائعة تشمل {esc('، '.join(tools))}. الطلب في {esc(districts[0])} قد يحتاج تجهيزاً مختلفاً عن {esc(districts[-1])} بسبب الوصول ونوع التشطيب.</p>"
        f"<p>إذا ارتبط العَرَض بموسم — حر أو رطوبة أو غبار أو أمطار — نربطه بـ{esc(geo['climate'])} حتى لا تُعالج النتيجة الظاهرية وتُترك البيئة التي تعيد المشكلة.</p>"
    )
    sec_quality = (
        f"<h2>كيف تقيّم جودة زيارة {esc(svc)}؟</h2>"
        f"<p>بعد انتهاء العمل اسأل: هل اتضح السبب؟ هل تقلّص العَرَض؟ هل عرفت الخطوة التالية؟ هل كان النطاق مفهوماً قبل التنفيذ؟</p>"
        f"<p>{BRAND} تبني الزيارة على هذه المعايير لأنها مرتبطة بنتيجة يمكن ملاحظتها داخل المنزل في {esc(city)}.</p>"
        f"<p>إذا احتجت متابعة لاحقاً، يكون النقاش مبنياً على ما سُجّل: الحي، نوع العقار، والنقاط التي نُفّذت ضمن {esc(svc)}.</p>"
        f"<p>لا نستخدم عبارات مثل «الأفضل» أو «مضمون 100٪»؛ نلتزم بما يمكن التحقق منه ميدانياً بعد الاتفاق.</p>"
    )
    sec_whyus = (
        f"<h2>لماذا يتعامل سكان {esc(city)} مع {BRAND}؟</h2>"
        + ul(
            [
                f"هوية عمل داخل السعودية ورقم موحّد {PHONE_TEL} للاتصال والواتساب.",
                f"محتوى هذه الصفحة عن {esc(svc)} وليس عن خدمة أخرى لا تخص العنوان.",
                "تشخيص قبل التوسع، وربط بالخدمات المساندة عند الحاجة فقط.",
                f"تغطية عملية لأحياء {esc(city)} مع توضيح إمكانية الوصول.",
            ]
        )
        + "[post_services]"
        + internal
    )
    faq_html = "<h2>أسئلة شائعة عن " + esc(svc) + " في " + esc(city) + "</h2>"
    for f in faqs:
        faq_html += f"<h3>{esc(f['question'])}</h3><p>{esc(f['answer'])}</p>"

    blocks = [sec_what, sec_when, sec_why, sec_how, sec_tech, sec_types, sec_cmp, sec_area, sec_prep, sec_cost, sec_err, sec_quality, sec_after]
    # rotate order of middle blocks for uniqueness, keep what/when early-ish
    mid = blocks[2:-1]
    rot = hid(seed) % max(1, len(mid))
    mid = mid[rot:] + mid[:rot]
    ordered = [blocks[0], blocks[1]] + mid + [blocks[-1], sec_whyus, faq_html, cta(svc, city)]
    html = "\n".join(parts) + "\n" + "\n".join(ordered)
    html += f'\n<p style="margin-top:18px;color:{TEXT};"> {BRAND} — {esc(title)} | {esc(geo["region"])} | {PHONE_TEL}</p>'
    if wc(html) < 1200:
        html += (
            f"<h2>خلاصة عملية لسكان {esc(city)}</h2>"
            f"<p>إذا كان عنوان بحثك {esc(title)} فابدأ بوصف صادق للعَرَض لا بطلب باقة جاهزة. {esc(pack['what'])} "
            f"وكلما كان الحي ونوع العقار واضحين من أول رسالة على {PHONE_TEL} صار نطاق {esc(svc)} أدق وأسرع.</p>"
            f"<p>احتفظ بصورة للعَرَض وتاريخ ظهوره. هذه التفاصيل تساعد الفريق على اختيار أدوات {esc('، '.join(tools[:3]))} المناسبة من الزيارة الأولى داخل {esc(geo['region'])}.</p>"
        )

    excerpt = (
        f"{title} من {BRAND} في {city}: {pack['what']} تغطية {dcsv}. تواصل {PHONE_TEL}."
    )[:180]

    features_items = [
        {"title": a, "content": b, "icon": f'<i class="fa-solid {ic}"></i>'}
        for ic, a, b in feat_cards
    ]
    steps_meta = [{"title": a, "content": b} for a, b in step_items]
    services_meta = []
    for rel in pack["related"][:4]:
        services_meta.append({"title": rel, "content": f"بند يُطرح فقط إذا أظهر الفحص ارتباطاً حقيقياً بـ{svc} داخل {city}."})
    price_items = [
        {"title": "معاينة وتحديد نطاق", "value": "تُوضَّح عند التواصل حسب العَرَض"},
        {"title": f"تنفيذ {svc} لنقطة محددة", "value": "حسب المساحة ودرجة الحالة"},
        {"title": "مواد إضافية إن لزم", "value": "بعد الاتفاق وقبل التنفيذ"},
        {"title": "متابعة بعد الزيارة", "value": "ضمن الاتفاق الموضّح لك"},
    ]

    meta = {
        "phone_number": PHONE,
        "whatsapp_number": WHATSAPP,
        "yourcolor__faqs": faqs,
        "post__features__data": {
            "features__title": f"مميزات {svc} في {city}",
            "features__content": f"جوانب عملية تهم صاحب العقار قبل اختيار {svc} داخل {city}.",
            "yourcolor__post_features": features_items,
        },
        "post__work_steps__data": {
            "work_steps__title": f"خطوات {svc}",
            "work_steps__content": f"مسار واضح من البلاغ حتى المراجعة داخل {city}.",
            "work_steps_items": steps_meta,
        },
        "post__services__data": {
            "services__title": "خدمات قد ترتبط بعد المعاينة",
            "services__content": "لا تُضاف إلا عند الحاجة الفعلية.",
            "post_services_items": services_meta,
        },
        "post__price_list__data": {
            "price_list__title": f"عناصر تقدير {svc}",
            "price_list__content": "بدون أرقام مخترعة؛ القيمة النهائية بعد فهم العقار.",
            "price_list__table_title1": "البند",
            "price_list__table_title2": "كيف تُحدد",
            "price_list__items": price_items,
        },
        "post__call_section__data": {
            "call_section_title": f"اطلب {svc} في {city}",
            "call_section_content": f"اذكر الحي والعَرَض على {PHONE_TEL} لنرتب المعاينة.",
            "call_section_phone": PHONE_TEL,
            "call_section_whatsapp": WA_INTL,
        },
        "post__card__data": {
            "post_card_title": f"{svc} في {city}",
            "post_card_content": f"خطة واضحة قبل التنفيذ — تواصل {PHONE_TEL}.",
        },
        "post__popover__data": {
            "popover_call_title": f"هل تحتاج {svc}؟",
            "popover_call_content": f"فريق {BRAND} في {city} جاهز لترتيب المعاينة.",
            "popover_call_icon": f'<i class="fa-solid {icon}"></i>',
        },
        "post__service_request__data": {
            "orderservices": f"طلب {svc}",
            "contentservices": f"أدخل الحي داخل {city} ووصفاً مختصراً للعَرَض.",
        },
        "YourColor_ImageObject": {
            "description": f"{title} — صورة توضيحية لخدمة {svc}",
            "contentLocation": city,
        },
        "YourColor_Service": {
            "priceRange": "يُحدد بعد المعاينة",
            "description": f"{pack['what']} خدمة {svc} في {city}.",
            "addressLocality": city,
            "telephone": PHONE_TEL,
            "addressCountry": "SA",
            "addressRegion": geo["region"],
            "areaServed": city,
            "OfferCatalog": svc,
            "streetAddress": city,
        },
        "YourColor_Article": {
            "headline": title,
            "description": excerpt,
        },
    }

    rm_title = title if 35 <= len(title) <= 60 else (title[:57] + "…" if len(title) > 60 else f"{title} | {BRAND}")
    rm_desc = excerpt[:155]
    tags = [svc[:40], city, BRAND, pack["family"]]
    return {
        "content": html,
        "excerpt": excerpt,
        "meta": meta,
        "rank_math": {
            "rank_math_title": rm_title,
            "rank_math_description": rm_desc,
            "rank_math_focus_keyword": kw[:80],
        },
        "tags": tags,
        "city": city,
        "svc": svc,
        "words": wc(html),
    }


TAG_CACHE: dict[str, int] = {}
CITY_CACHE: dict[str, int] = {}
CACHE_LOCK = Lock()


def ensure_tag(name: str) -> int | None:
    name = (name or "").strip()
    if not name:
        return None
    with CACHE_LOCK:
        if name in TAG_CACHE:
            return TAG_CACHE[name]
    try:
        body, _ = get("/wp/v2/tags?per_page=1&search=" + urllib.parse.quote(name))
        if body and body[0].get("name") == name:
            with CACHE_LOCK:
                TAG_CACHE[name] = body[0]["id"]
            return body[0]["id"]
        created, _ = post("/wp/v2/tags", {"name": name})
        with CACHE_LOCK:
            TAG_CACHE[name] = created["id"]
        return created["id"]
    except Exception:
        try:
            created, _ = post("/wp/v2/tags", {"name": name})
            with CACHE_LOCK:
                TAG_CACHE[name] = created["id"]
            return created["id"]
        except Exception:
            return None


def ensure_city(name: str) -> int | None:
    # Prefer the populated Riyadh term (slug الرياض-ar) over any duplicate.
    if name == "الرياض":
        with CACHE_LOCK:
            CITY_CACHE[name] = 3327
        return 3327
    with CACHE_LOCK:
        if name in CITY_CACHE:
            return CITY_CACHE[name]
    try:
        body, _ = get("/wp/v2/cities?per_page=100")
        with CACHE_LOCK:
            best: dict[str, tuple[int, int]] = {}
            for t in body or []:
                n = t["name"]
                pair = (int(t.get("count") or 0), int(t["id"]))
                if n not in best or pair[0] > best[n][0]:
                    best[n] = pair
            for n, (_count, tid) in best.items():
                CITY_CACHE[n] = tid
            CITY_CACHE["الرياض"] = 3327
            if name in CITY_CACHE:
                return CITY_CACHE[name]
        created, _ = post("/wp/v2/cities", {"name": name})
        with CACHE_LOCK:
            CITY_CACHE[name] = created["id"]
        return created["id"]
    except Exception:
        return None


def update_rankmath(pid: int, meta: dict) -> None:
    try:
        post("/rankmath/v1/updateMeta", {"objectType": "post", "objectID": pid, "meta": meta})
    except Exception as e:
        print("RM", pid, e, flush=True)


def rewrite_one(row: dict, index: dict) -> dict:
    built = build_article(row, index)
    tag_ids = [tid for t in built["tags"] if (tid := ensure_tag(t))]
    city_id = ensure_city(built["city"])
    payload = {
        "content": built["content"],
        "excerpt": built["excerpt"],
        "meta": built["meta"],
    }
    if tag_ids:
        payload["tags"] = tag_ids
    if city_id:
        payload["cities"] = [city_id]
    put(f"/wp/v2/posts/{row['id']}", payload)
    update_rankmath(row["id"], built["rank_math"])
    return {"id": row["id"], "words": built["words"], "svc": built["svc"], "city": built["city"], "title": row["title"]}


def load_index(rows: list[dict]) -> dict:
    idx: dict[str, list] = {}
    for r in rows:
        city, svc = parse_title(r["title"])
        idx.setdefault(city, []).append(
            {"id": r["id"], "title": r["title"], "svc": svc, "link": f"https://www.rukn-eltatawer.com/sa/{r['slug']}/"}
        )
    return idx


def main():
    rows = json.loads((DATA / "audit-posts.json").read_text(encoding="utf-8"))
    progress_path = DATA / "rewrite-progress.json"
    done = set()
    log = []
    if progress_path.exists():
        log = json.loads(progress_path.read_text(encoding="utf-8"))
        done = {x["id"] for x in log if x.get("ok")}
    index = load_index(rows)
    targets = [r for r in rows if r["id"] not in SKIP_IDS and r.get("needs_rewrite") and r["id"] not in done]
    print(f"Targets {len(targets)} (done {len(done)})", flush=True)
    ok = fail = 0
    log_lock = Lock()
    workers = 2

    def job(row, idx):
        rec = rewrite_one(row, index)
        rec["ok"] = True
        rec["_i"] = idx
        return rec

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(job, row, i): row for i, row in enumerate(targets, 1)}
        finished = 0
        for fut in as_completed(futs):
            row = futs[fut]
            finished += 1
            try:
                rec = fut.result()
                with log_lock:
                    log.append(rec)
                    ok += 1
                print(f"[{finished}/{len(targets)}] OK {row['id']} words={rec['words']} {row['title'][:40]}", flush=True)
            except Exception as e:
                with log_lock:
                    log.append({"id": row["id"], "ok": False, "error": str(e)[:400], "title": row["title"]})
                    fail += 1
                print(f"[{finished}/{len(targets)}] FAIL {row['id']} {e}", flush=True)
            if finished % 20 == 0:
                with log_lock:
                    progress_path.write_text(json.dumps(log, ensure_ascii=False), encoding="utf-8")
    progress_path.write_text(json.dumps(log, ensure_ascii=False), encoding="utf-8")
    summary = {
        "ok": ok,
        "fail": fail,
        "skipped_hubs": list(SKIP_IDS),
        "total_logged": len(log),
        "avg_words": round(sum(x.get("words") or 0 for x in log if x.get("ok")) / max(1, ok)),
    }
    (DATA / "rewrite-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
