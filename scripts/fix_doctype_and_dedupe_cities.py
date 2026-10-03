#!/usr/bin/env python3
"""Strip full HTML documents from posts and uniquify templated city leak pages."""

from __future__ import annotations

import hashlib
import html as html_lib
import json
import re
import time
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

BASE = "https://www.rukn-eltatawer.com/sa"
AUTH = HTTPBasicAuth("cursor", "PCkk ig95 Gu6c zOgC GLYG FYsk")
H = {"User-Agent": "Mozilla/5.0 RuknFix/1.0", "Content-Type": "application/json"}
PHONE = "0568060309"
WA = "966568060309"

DOCTYPE_IDS = [
    9278, 9279, 9280, 9281, 9282, 9283, 9284, 9285, 9286, 9288,
    9292, 9293, 9294, 9295, 9296, 9297, 9298, 9299, 9300, 9301,
    9302, 9303, 9304, 9305, 9306, 9307,
]

ROOT = Path(__file__).resolve().parents[1]
CITY_META = json.loads((ROOT / "data/city-local-meta.json").read_text(encoding="utf-8"))


def word_count(text: str) -> int:
    plain = re.sub(r"<[^>]+>", " ", text or "")
    plain = re.sub(r"\[[^\]]+\]", " ", plain)
    plain = re.sub(r"\s+", " ", html_lib.unescape(plain)).strip()
    return len(re.findall(r"[\w\u0600-\u06FF]+", plain))


def strip_full_html_document(raw: str) -> str:
    """Extract body content from a full HTML document pasted into post content."""
    if not raw:
        return raw
    lower = raw.lower()
    if "<!doctype" not in lower and "<html" not in lower:
        return raw

    m = re.search(r"<body[^>]*>(.*)</body>", raw, flags=re.S | re.I)
    body = m.group(1) if m else raw

    # Drop head leftovers if body regex failed partially
    body = re.sub(r"<head\b[^>]*>.*?</head>", "", body, flags=re.S | re.I)
    body = re.sub(r"<!DOCTYPE[^>]*>", "", body, flags=re.I)
    body = re.sub(r"</?html\b[^>]*>", "", body, flags=re.I)
    body = re.sub(r"</?body\b[^>]*>", "", body, flags=re.I)
    body = re.sub(r"<style\b[^>]*>.*?</style>", "", body, flags=re.S | re.I)
    body = re.sub(r"<script\b[^>]*>.*?</script>", "", body, flags=re.S | re.I)
    body = re.sub(r"<meta\b[^>]*>", "", body, flags=re.I)
    body = re.sub(r"<title\b[^>]*>.*?</title>", "", body, flags=re.S | re.I)
    body = re.sub(r"<link\b[^>]*>", "", body, flags=re.I)

    # Avoid duplicate H1 vs theme title: demote first H1 to paragraph lead
    body = re.sub(
        r"<h1\b[^>]*>(.*?)</h1>",
        r'<p style="font-size:1.35em;font-weight:700;color:#005CB9;line-height:1.5;">\1</p>',
        body,
        count=1,
        flags=re.S | re.I,
    )

    # Replace manual call/WhatsApp button clusters with shortcode once near top
    button_block = re.compile(
        r"<div[^>]*>\s*(?:<a[^>]+href=\"(?:tel:|https://wa\.me/)[^\"]+\"[^>]*>.*?</a>\s*){1,3}</div>",
        flags=re.S | re.I,
    )
    body, n_btn = button_block.subn("\n[post_call]\n", body, count=1)
    if n_btn:
        body = button_block.sub("", body)  # remove remaining button clusters

    # Soft-replace leftover tel/wa CTA anchors that are standalone gradient buttons
    body = re.sub(
        r"<a[^>]+href=\"tel:[^\"]+\"[^>]*>\s*(?:📞\s*)?[^<]{0,80}</a>",
        "",
        body,
        flags=re.I,
    )
    body = re.sub(
        r"<a[^>]+href=\"https://wa\.me/[^\"]+\"[^>]*>\s*[^<]{0,80}</a>",
        "",
        body,
        flags=re.I,
    )

    # Keep plain-text phone mentions; ensure shortcode present
    if "[post_call]" not in body:
        body = "[post_call]\n" + body
    elif body.count("[post_call]") > 3:
        parts = body.split("[post_call]")
        # keep first + last only (+ maybe middle)
        body = parts[0] + "[post_call]" + "".join(parts[1:-1]) + "[post_call]" + parts[-1]

    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    return body


def extract_city(title: str) -> str | None:
    m = re.search(r"كشف تسربات المياه في (.+?)(?:\s*\||$)", title)
    if not m:
        return None
    return m.group(1).strip()


def pick(city: str, options: list[str]) -> str:
    h = int(hashlib.md5(city.encode("utf-8")).hexdigest(), 16)
    return options[h % len(options)]


def build_unique_city_content(city: str, meta: dict) -> str:
    meta = dict(meta)
    if "note" not in meta:
        meta["note"] = f"الفحص المبكر في {city} يقلل تكلفة الترميم ويمنع توسع الرطوبة إلى الأساسات."
    districts_li = "\n".join(f"<li>{d}</li>" for d in meta["districts"])
    districts_csv = "، ".join(meta["districts"])

    intros = [
        f"إذا لاحظت {meta['hook']} وأنت في <strong>{city}</strong> ضمن منطقة <strong>{meta['region']}</strong>، فالمشكلة غالباً تسرب مخفي وليس مجرد ارتفاع طبيعي في الاستهلاك.",
        f"سكان <strong>{city}</strong> يسألون كثيراً عن سبب {meta['hook']}؛ ومع {meta['climate']} يزيد احتمال {meta['risk']}.",
        f"في <strong>{city}</strong> ({meta['region']}) تظهر آثار التسرب بشكل مختلف حسب نوع العقار—خصوصاً في {meta['property']}—لذلك الفحص الجهازي أوفر من التخمين.",
        f"شركة ركن التطور تخدم <strong>{city}</strong> بفحص ميداني سريع لأن {meta['climate']} يجعل {meta['risk']} أمراً شائعاً إذا تأخر التدخل.",
    ]
    why_titles = [
        f"ما الذي يزيد تسربات المياه تحديداً في {city}؟",
        f"لماذا تتفاقم الرطوبة بسرعة داخل منازل {city}؟",
        f"طبيعة {city} وعلاقتها بمشاكل شبكات المياه",
    ]
    device_leads = [
        f"في عقارات {city} نختار أسلوب الكشف حسب التشطيب وعمر المبنى، لا وفق تخمين عام:",
        f"بدل تكسير واسع في {city} نبدأ بأجهزة تحدد المصدر أولاً:",
        f"معداتنا في زيارات {city} تركز على تقليل الضرر على البلاط والدهان:",
    ]
    tips = [
        f"أغلق جميع الصنابير في منزلك داخل {city} وراقب العداد دقيقتين؛ إذا تحرك فهو مؤشر قوي على تسرب.",
        f"صوّر بقع الرطوبة وتاريخ ظهورها في {city} قبل الزيارة؛ هذا يختصر وقت التشخيص.",
        f"لا تدهن فوق الرطوبة في {city} قبل الكشف؛ الدهان يخفي الأثر ولا يوقف الهدر.",
        f"افحص محابس الري والحديقة حول منازل {city}؛ كثير من الهدر يكون خارج المبنى.",
    ]
    faq_sets = [
        [
            (f"هل كشف التسربات في {city} يحتاج تكسير؟", "في أغلب الحالات لا. نحدد النقطة أولاً بالأجهزة، ولا نفتح إلا نطاقاً ضيقاً بعد التأكيد."),
            (f"كم مدة الفحص داخل {city}؟", "غالباً من ساعة إلى ثلاث ساعات حسب مساحة العقار وعدد نقاط الشك."),
            (f"هل تغطون أحياء {city}؟", f"نعم، نصل إلى {districts_csv} والمناطق المجاورة حسب جدولة اليوم."),
        ],
        [
            (f"متى أطلب كشف تسربات في {city}؟", f"عند {meta['hook']}، أو بقع رطوبة، أو رائحة عفن، أو انخفاض ضغط مفاجئ."),
            (f"هل يتوفر إصلاح بعد الكشف في {city}؟", "نعم عند الطلب: إصلاح التغذية/الصرف، وعزل الخزان أو السطح إذا لزم."),
            (f"هل الخدمة مناسبة لـ{meta['property']}؟", f"نعم، نتعامل مع {meta['property']} داخل {city} باختيار أداة الكشف المناسبة لكل حالة."),
        ],
    ]

    intro = pick(city, intros)
    why_t = pick(city, why_titles)
    devices = pick(city, device_leads)
    tip = pick(city, tips)
    faqs = pick(city, faq_sets)
    order = int(hashlib.md5(city.encode()).hexdigest(), 16) % 2

    section_why = f"""
<h2>{why_t}</h2>
<p>تقع {city} في نطاق <strong>{meta['region']}</strong> حيث {meta['climate']}. هذا المناخ يرفع احتمال <strong>{meta['risk']}</strong>، خصوصاً في {meta['property']}.</p>
<p>{meta['note'] if 'note' in meta else tip}</p>
<p>مثال عملي: {meta['case']}. مثل هذه الحالات تتكرر في {city} وتُحل أسرع عندما يبدأ العمل بالتشخيص لا بالتكسير.</p>
"""

    section_districts = f"""
<h2>نطاق التغطية داخل {city}</h2>
<p>فريق ركن التطور يصل إلى أحياء {city} وما حولها، ومنها:</p>
<ul>
{districts_li}
</ul>
<p>عند الحجز اذكر الحي ونوع العقار (فيلا/شقة/استراحة) ووصف العرض الظاهر؛ هذا يساعدنا على إحضار المعدات المناسبة من أول زيارة.</p>
"""

    section_devices = f"""
<h2>كيف نكشف التسرب في {city} بدون تكسير عشوائي؟</h2>
<p>{devices}</p>
<ul>
<li><strong>تتبع صوتي:</strong> لالتقاط تدفق المياه داخل الجدران أو تحت البلاط.</li>
<li><strong>قياس رطوبة/تصوير حراري:</strong> لتحديد الرطوبة المخفية قبل تحولها لعفن ظاهر.</li>
<li><strong>كاميرا مجارٍ:</strong> عند الاشتباه بكسور أو انسدادات في الصرف.</li>
<li><strong>اختبار ضغط:</strong> للتحقق من سلامة الخط بعد الإصلاح.</li>
</ul>
<p>الهدف في {city}: تشخيص أدق، فتح أضيق، وتكلفة ترميم أقل.</p>
"""

    section_signs = f"""
<h2>علامات مبكرة في {city} تستحق الفحص</h2>
<ul>
<li>{meta['hook']}.</li>
<li>بقع رطوبة أو تغير لون الدهان على الجدران/الأسقف.</li>
<li>رائحة عفن في غرفة مغلقة أو خزانة حائط.</li>
<li>انخفاض ضغط المياه في دور أو جناح واحد.</li>
<li>صوت خرير مستمر بعد إغلاق الصنابير.</li>
<li>هبوط بسيط في بلاط خارجي أو رطوبة حديقة غير مبررة.</li>
</ul>
<p><strong>نصيحة محلية:</strong> {tip}</p>
"""

    section_steps = f"""
<h2>خطوات الخدمة مع ركن التطور في {city}</h2>
<ol>
<li>تواصل عبر الاتصال أو الواتساب على {PHONE} مع ذكر الحي في {city}.</li>
<li>معاينة العداد ونقاط الاستهلاك ومسار الشبكة الظاهرة.</li>
<li>كشف جهازي لتحديد المصدر بأقل تدخل على التشطيب.</li>
<li>شرح التقرير والخيار الأنسب قبل أي إصلاح إضافي.</li>
<li>تنفيذ الإصلاح/العزل عند الطلب ثم اختبار التأكد.</li>
</ol>
"""

    section_why_us = f"""
<h2>لماذا يختار عملاء {city} ركن التطور؟</h2>
<ul>
<li>خبرة ميدانية في مدن منطقة {meta['region']} وليس قالب كشف عاماً فقط.</li>
<li>أجهزة حديثة تقلل التكسير وتحافظ على تشطيب {meta['property']}.</li>
<li>تقرير واضح وتسعير قبل التنفيذ.</li>
<li>تغطية أحياء {city}: {districts_csv}.</li>
<li>رقم موحّد للاتصال والواتساب: {PHONE}</li>
</ul>
"""

    section_faq = "<h2>أسئلة شائعة عن كشف التسربات في " + city + "</h2>\n"
    for q, a in faqs:
        section_faq += f"<h3>{q}</h3>\n<p>{a}</p>\n"

    section_close = f"""
<h2>احجز كشف تسربات المياه في {city}</h2>
<p>إذا كنت في <strong>{city}</strong> وتعاني من رطوبة أو هدر مياه، التدخل المبكر أوفر من ترميم واسع لاحقاً. تواصل مع <strong>شركة ركن التطور</strong> الآن:</p>
[post_call]
<p>ركن التطور — كشف تسربات المياه في {city} | {meta['region']} | {PHONE}</p>
"""

    # Vary section order slightly
    if order == 0:
        middle = section_why + section_districts + section_signs + section_devices + section_steps
    else:
        middle = section_districts + section_why + section_devices + section_signs + section_steps

    content = f"""
<p>{intro}</p>
<p><strong>شركة ركن التطور</strong> تقدّم <strong>كشف تسربات المياه في {city}</strong> بأجهزة دقيقة وبدون تكسير عشوائي، مع حلول إصلاح وعزل تناسب {meta['property']} في أحياء المدينة.</p>
[post_call]
{middle}
{section_why_us}
{section_faq}
{section_close}
""".strip()
    return content


def fetch_all_posts():
    posts = []
    page = 1
    while True:
        r = requests.get(
            f"{BASE}/wp-json/wp/v2/posts",
            auth=AUTH,
            headers=H,
            params={"per_page": 100, "page": page, "context": "edit", "status": "publish"},
            timeout=90,
        )
        if r.status_code != 200:
            break
        batch = r.json()
        if not batch:
            break
        posts.extend(batch)
        page += 1
    return posts


def update_post(pid: int, content: str) -> dict:
    r = requests.post(
        f"{BASE}/wp-json/wp/v2/posts/{pid}",
        auth=AUTH,
        headers=H,
        json={"content": content},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def is_template_city_content(raw: str) -> bool:
    markers = [
        "أجهزة التتبع الصوتي: تلتقط صوت تدفق المياه داخل الجدران أو تحت البلاط حتى عندما يكون التسرب غير ظاهر للعين",
        "هدفنا دائماً: تشخيص أدق، إصلاح أضيق، ونتيجة أوضح للعميل",
        "ننصح أيضاً بالاحتفاظ بصور السطح قبل التنفيذ",  # shouldn't be on leak pages
        "هل تلاحظ ارتفاعاً مفاجئاً في فاتورة المياه أو رطوبة داخل الجدران في",
        "هل تلاحظ ارتفاعاً في فاتورة المياه أو رطوبة في الجدران داخل",
    ]
    hits = sum(1 for m in markers if m in (raw or ""))
    # also old shared device list exact
    if "كاميرات فحص المجاري: تكشف الكسور والتشققات والانسدادات داخل خطوط الصرف بدقة مرئية" in (raw or ""):
        hits += 1
    return hits >= 1


def main():
    posts = fetch_all_posts()
    by_id = {p["id"]: p for p in posts}
    report = {"doctype_fixed": [], "cities_rewritten": [], "skipped": []}

    # 1) Strip doctype documents
    for pid in DOCTYPE_IDS:
        p = by_id.get(pid)
        if not p:
            report["skipped"].append({"id": pid, "reason": "missing"})
            continue
        raw = (p.get("content") or {}).get("raw") or ""
        if "<!DOCTYPE" not in raw and "<!doctype" not in raw.lower() and "<html" not in raw.lower():
            report["skipped"].append({"id": pid, "reason": "no-doctype"})
            continue
        cleaned = strip_full_html_document(raw)
        update_post(pid, cleaned)
        report["doctype_fixed"].append(
            {
                "id": pid,
                "title": p["title"]["raw"],
                "old_wc": word_count(raw),
                "new_wc": word_count(cleaned),
                "had_doctype": True,
            }
        )
        print(f"DOCTYPE fixed #{pid} {p['title']['raw'][:40]} wc {word_count(raw)}->{word_count(cleaned)}")
        time.sleep(0.15)

    # refresh posts after doctype fixes
    posts = fetch_all_posts()

    # 2) Rewrite templated city pages (those with shared template markers OR in city meta band)
    for p in posts:
        title = p["title"]["raw"]
        city = extract_city(title)
        if not city:
            continue
        # normalize city key
        city_key = city
        if city_key not in CITY_META:
            # try without extras
            city_key = city.replace("أحياء ", "").strip()
        if city_key not in CITY_META:
            continue
        raw = (p.get("content") or {}).get("raw") or ""
        wc = word_count(raw)
        # Rewrite if template-like, or previously rewritten thin band (800-1000) with city meta
        if not (is_template_city_content(raw) or (800 <= wc <= 1000)):
            continue
        # Skip if already unique enough: no markers and has varied case? still rewrite band with markers
        if not is_template_city_content(raw) and wc > 1000:
            continue

        meta = dict(CITY_META[city_key])
        if "note" not in meta:
            meta["note"] = f"الفحص المبكر في {city_key} يقلل تكلفة الترميم ويمنع توسع الرطوبة إلى الأساسات."
        content = build_unique_city_content(city_key, meta)
        update_post(p["id"], content)
        report["cities_rewritten"].append(
            {
                "id": p["id"],
                "city": city_key,
                "title": title,
                "old_wc": wc,
                "new_wc": word_count(content),
            }
        )
        print(f"CITY rewrite #{p['id']} {city_key} {wc}->{word_count(content)}")
        time.sleep(0.15)

    out = ROOT / "data/doctype-dedupe-results.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "doctype_fixed": len(report["doctype_fixed"]),
                "cities_rewritten": len(report["cities_rewritten"]),
                "skipped": len(report["skipped"]),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
