#!/usr/bin/env python3
"""Critical SA fixes — content/NAP/dups only. NEVER touch SEO titles / post titles / rank_math_title."""

from __future__ import annotations

import json
import re
import time
import urllib.request
import base64
from pathlib import Path

BASE = "https://www.rukn-eltatawer.com/sa/wp-json"
AUTH = base64.b64encode(b"cursor:PCkk ig95 Gu6c zOgC GLYG FYsk").decode()
H = {
    "Authorization": f"Basic {AUTH}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 RuknCritical/2026-10-04",
}
PHONE = "0568060309"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "critical-fixes-oct4-results.json"

CITIES = [
    {
        "id": 23070,
        "slug": "riyadh",
        "name": "الرياض",
        "climate": "حرارة حضرية وغبار موسمي مع ليالٍ أبرد شتاءً",
        "risk": "ضغط الاستخدام على التكييف والعزل والخزانات في الفلل والشقق",
        "districts": ["الملز", "الياسمين", "النسيم", "طويق", "العقيق"],
        "services": [
            ("كشف تسربات المياه في الرياض", "https://www.rukn-eltatawer.com/sa/water-leak-detection-riyadh/"),
            ("عزل أسطح في الرياض", "https://www.rukn-eltatawer.com/sa/roof-insulation-riyadh/"),
            ("تنظيف منازل في الرياض", "https://www.rukn-eltatawer.com/sa/house-cleaning-in-riyadh/"),
            ("غسيل مكيفات في الرياض", "https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-riyadh/"),
            ("مكافحة حشرات في الرياض", "https://www.rukn-eltatawer.com/sa/pest-control-riyadh/"),
            ("سباك منازل في الرياض", "https://www.rukn-eltatawer.com/sa/home-plumber-riyadh/"),
            ("كهربائي منازل في الرياض", "https://www.rukn-eltatawer.com/sa/home-electrician-riyadh/"),
            ("نقل عفش في الرياض", "https://www.rukn-eltatawer.com/sa/furniture-moving-riyadh/"),
        ],
        "note": "شرق الرياض قريب من مقر الخدمة؛ الأحياء الشمالية تحتاج جدولة أوضح بسبب الازدحام.",
    },
    {
        "id": 23071,
        "slug": "jeddah",
        "name": "جدة",
        "climate": "رطوبة ساحلية وملوحة هواء تسرّع تلف الدهان والمعدن",
        "risk": "تسربات بطيئة وعفن وتآكل وصلات ظاهرة قرب البحر",
        "districts": ["الروضة", "أبحر", "الصفا", "الفيصلية", "النعيم"],
        "services": [
            ("غسيل مكيفات في جدة", "https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-jeddah/"),
            ("كشف تسرب مواسير في جدة", "https://www.rukn-eltatawer.com/sa/water-pipe-leak-detection-jeddah/"),
            ("تنظيف منازل في جدة", "https://www.rukn-eltatawer.com/sa/home-cleaning-jeddah/"),
            ("عزل أسطح في جدة", "https://www.rukn-eltatawer.com/sa/roof-insulation-jeddah/"),
            ("مكافحة حشرات في جدة", "https://www.rukn-eltatawer.com/sa/pest-control-jeddah/"),
            ("سباك منازل في جدة", "https://www.rukn-eltatawer.com/sa/home-plumber-jeddah/"),
            ("كهربائي منازل في جدة", "https://www.rukn-eltatawer.com/sa/home-electrician-jeddah/"),
            ("نقل عفش في جدة", "https://www.rukn-eltatawer.com/sa/furniture-moving-jeddah/"),
        ],
        "note": "في جدة الرطوبة تخفي علامات التسرب؛ المعاينة الميدانية أهم من التقدير عن بُعد.",
    },
    {
        "id": 23072,
        "slug": "makkah",
        "name": "مكة المكرمة",
        "climate": "حرارة مرتفعة مع ضغط مواسم الحج والعمرة على المباني",
        "risk": "ازدحام مواسم الذروة يؤخر الصيانة إن لم تُحجز مبكراً",
        "districts": ["العزيزية", "الشوقية", "العوالي", "النوارية", "الشرايع"],
        "services": [
            ("كشف تسربات في مكة", "https://www.rukn-eltatawer.com/sa/water-leak-detection-mecca/"),
            ("تنظيف منازل في مكة", "https://www.rukn-eltatawer.com/sa/home-cleaning-mecca/"),
            ("عزل أسطح في مكة", "https://www.rukn-eltatawer.com/sa/roof-insulation-mecca/"),
            ("غسيل مكيفات في مكة", "https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-mecca/"),
            ("مكافحة حشرات في مكة", "https://www.rukn-eltatawer.com/sa/pest-control-mecca/"),
            ("سباك منازل في مكة", "https://www.rukn-eltatawer.com/sa/home-plumber-mecca/"),
            ("كهربائي منازل في مكة", "https://www.rukn-eltatawer.com/sa/home-electrician-mecca/"),
            ("نقل عفش في مكة", "https://www.rukn-eltatawer.com/sa/furniture-moving-mecca/"),
        ],
        "note": "اذكر الحي وقربك من الحرم عند الطلب لتفادي تأخير الوصول في المواسم.",
    },
    {
        "id": 23073,
        "slug": "madinah",
        "name": "المدينة المنورة",
        "climate": "حرارة جافة مع فروقات ليلية أوضح شتاءً",
        "risk": "تمدد وانكماش الوصلات مع تشغيل الخزانات والتكييف",
        "districts": ["قباء", "العوالي", "الحرم", "العيون", "المناخة"],
        "services": [
            ("كشف تسربات في المدينة", "https://www.rukn-eltatawer.com/sa/water-leak-detection-medina/"),
            ("تنظيف منازل في المدينة", "https://www.rukn-eltatawer.com/sa/home-cleaning-medina/"),
            ("عزل أسطح في المدينة", "https://www.rukn-eltatawer.com/sa/roof-insulation-medina/"),
            ("غسيل مكيفات في المدينة", "https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-medina/"),
            ("مكافحة حشرات في المدينة", "https://www.rukn-eltatawer.com/sa/pest-control-medina/"),
            ("سباك منازل في المدينة", "https://www.rukn-eltatawer.com/sa/home-plumber-medina/"),
            ("كهربائي منازل في المدينة", "https://www.rukn-eltatawer.com/sa/home-electrician-medina/"),
            ("نقل عفش في المدينة", "https://www.rukn-eltatawer.com/sa/furniture-moving-medina/"),
        ],
        "note": "المدينة تناسب جدولة صباحية هادئة؛ وضّح نوع العقار (شقة/فيلا) لتقصير المعاينة.",
    },
    {
        "id": 23074,
        "slug": "dammam",
        "name": "الدمام",
        "climate": "رطوبة شرقية مع غبار وصحوة حرارية صيفاً",
        "risk": "تأثر الدكتات والعزل الخارجي بالرطوبة والغبار معاً",
        "districts": ["الفيصلية", "الشاطئ", "الجلوية", "الروضة", "النور"],
        "services": [
            ("كشف تسربات في الدمام", "https://www.rukn-eltatawer.com/sa/water-leak-detection-dammam/"),
            ("تنظيف منازل في الدمام", "https://www.rukn-eltatawer.com/sa/home-cleaning-dammam/"),
            ("عزل أسطح في الدمام", "https://www.rukn-eltatawer.com/sa/roof-insulation-dammam/"),
            ("غسيل مكيفات في الدمام", "https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-dammam/"),
            ("مكافحة حشرات في الدمام", "https://www.rukn-eltatawer.com/sa/pest-control-dammam/"),
            ("سباك منازل في الدمام", "https://www.rukn-eltatawer.com/sa/home-plumber-dammam/"),
            ("كهربائي منازل في الدمام", "https://www.rukn-eltatawer.com/sa/home-electrician-dammam/"),
            ("نقل عفش في الدمام", "https://www.rukn-eltatawer.com/sa/furniture-moving-dammam/"),
        ],
        "note": "الدمام والخبر متجاورتان؛ حدّد المدينة بدقة لتفادي خلط الجدولة.",
    },
    {
        "id": 23075,
        "slug": "khobar",
        "name": "الخبر",
        "climate": "رطوبة ساحلية خليجية مع أبراج وشقق كثيفة",
        "risk": "تسربات وصيانة تكييف في مبانٍ متعددة الأدوار",
        "districts": ["العقربية", "اليرموك", "الحزام", "الثقافة", "الكورنيش"],
        "services": [
            ("كشف تسربات في الخبر", "https://www.rukn-eltatawer.com/sa/water-leak-detection-khobar/"),
            ("تنظيف منازل في الخبر", "https://www.rukn-eltatawer.com/sa/home-cleaning-khobar/"),
            ("عزل أسطح في الخبر", "https://www.rukn-eltatawer.com/sa/roof-insulation-khobar/"),
            ("غسيل مكيفات في الخبر", "https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-khobar/"),
            ("مكافحة حشرات في الخبر", "https://www.rukn-eltatawer.com/sa/pest-control-khobar/"),
            ("سباك منازل في الخبر", "https://www.rukn-eltatawer.com/sa/home-plumber-khobar/"),
            ("كهربائي منازل في الخبر", "https://www.rukn-eltatawer.com/sa/home-electrician-khobar/"),
            ("نقل عفش في الخبر", "https://www.rukn-eltatawer.com/sa/furniture-moving-khobar/"),
        ],
        "note": "الأبراج تحتاج تنسيقاً مع الإدارة؛ جهّز تصريح الدخول قبل الموعد.",
    },
    {
        "id": 23076,
        "slug": "taif",
        "name": "الطائف",
        "climate": "أجواء أبرد نسبياً وأمطار موسمية أوضح من الرياض",
        "risk": "ضعف العزل يظهر أسرع مع تبلل الأسطح وتقلبات الحرارة",
        "districts": ["الشفا", "الهدا", "الحوية", "الفيصلية", "الوشحاء"],
        "services": [
            ("كشف تسربات في الطائف", "https://www.rukn-eltatawer.com/sa/water-leak-detection-taif/"),
            ("تنظيف منازل في الطائف", "https://www.rukn-eltatawer.com/sa/home-cleaning-taif/"),
            ("عزل أسطح في الطائف", "https://www.rukn-eltatawer.com/sa/roof-insulation-taif/"),
            ("غسيل مكيفات في الطائف", "https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-taif/"),
            ("مكافحة حشرات في الطائف", "https://www.rukn-eltatawer.com/sa/pest-control-taif/"),
            ("سباك منازل في الطائف", "https://www.rukn-eltatawer.com/sa/home-plumber-taif/"),
            ("كهربائي منازل في الطائف", "https://www.rukn-eltatawer.com/sa/home-electrician-taif/"),
            ("نقل عفش في الطائف", "https://www.rukn-eltatawer.com/sa/furniture-moving-taif/"),
        ],
        "note": "بعد مواسم المطر افحص العزل مبكراً قبل أن تنتقل الرطوبة للدور السفلي.",
    },
    {
        "id": 23077,
        "slug": "abha",
        "name": "أبها",
        "climate": "برودة ورطوبة جبلية مع ضباب وأمطار متفرقة",
        "risk": "رطوبة مستمرة تضعف الدهان والعزل إن لم تُعالج من المصدر",
        "districts": ["الموظفين", "الوردتين", "المطار", "السودة", "النميص"],
        "services": [
            ("كشف تسربات في أبها", "https://www.rukn-eltatawer.com/sa/water-leak-detection-abha/"),
            ("تنظيف منازل في أبها", "https://www.rukn-eltatawer.com/sa/home-cleaning-abha/"),
            ("عزل أسطح في أبها", "https://www.rukn-eltatawer.com/sa/roof-insulation-abha/"),
            ("غسيل مكيفات في أبها", "https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-abha/"),
            ("مكافحة حشرات في أبها", "https://www.rukn-eltatawer.com/sa/pest-control-abha/"),
            ("سباك منازل في أبها", "https://www.rukn-eltatawer.com/sa/home-plumber-abha/"),
            ("كهربائي منازل في أبها", "https://www.rukn-eltatawer.com/sa/home-electrician-abha/"),
            ("نقل عفش في أبها", "https://www.rukn-eltatawer.com/sa/furniture-moving-abha/"),
        ],
        "note": "في أبها لا تعتمد على تجفيف سطحي فقط؛ عالج مصدر الرطوبة ثم أعد التشطيب.",
    },
]


def get(path: str):
    last = None
    for i in range(4):
        try:
            req = urllib.request.Request(BASE + path, headers=H)
            with urllib.request.urlopen(req, timeout=90) as resp:
                return dict(resp.headers), json.loads(resp.read().decode())
        except Exception as e:
            last = e
            time.sleep(1.2 * (i + 1))
    raise last


def put(path: str, payload: dict):
    # Safety: never allow title / rank_math_title in payload
    payload = {k: v for k, v in payload.items() if k not in ("title", "rank_math_title")}
    if "meta" in payload and isinstance(payload["meta"], dict):
        payload["meta"] = {
            k: v for k, v in payload["meta"].items() if k not in ("rank_math_title", "rank_math_focus_keyword")
        }
    data = json.dumps(payload, ensure_ascii=False).encode()
    last = None
    for i in range(4):
        try:
            req = urllib.request.Request(BASE + path, data=data, headers=H, method="PUT")
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            last = e
            time.sleep(1.2 * (i + 1))
    raise last


def ar_words(html: str) -> int:
    t = re.sub(r"<script[\s\S]*?</script>", "", html or "", flags=re.I)
    t = re.sub(r"<style[\s\S]*?</style>", "", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return len(re.findall(r"[\u0600-\u06FF]+", t))


def city_html(c: dict) -> str:
    links = "".join(f'<li><a href="{url}">{label}</a></li>' for label, url in c["services"])
    districts = "، ".join(c["districts"])
    name = c["name"]
    return f"""<!-- wp:paragraph -->
<p>صفحة مدينة <strong>{name}</strong> من <strong>شركة ركن التطور</strong> تجمع مداخل الخدمات المنزلية المرتبطة بهذه المدينة داخل السعودية. المناخ المحلي يتسم بـ{c['climate']}؛ لذلك نوجّهك لصفحات خدمة محلية بدل نص عام منسوخ. للحجز أو الاستفسار: <strong>{PHONE}</strong>.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>ماذا يميز الطلب في {name}؟</h2>
<!-- /wp:heading -->
<!-- wp:paragraph -->
<p>{c['risk']}. الأحياء الأكثر طلباً تشمل: {districts}. اذكر الحي ونوع العقار (شقة، فيلا، دور) ووصف المشكلة باختصار حتى نؤكد التغطية والوقت المناسب قبل الزيارة.</p>
<!-- /wp:paragraph -->
<!-- wp:paragraph -->
<p>{c['note']} الهدف ليس وعداً عاماً، بل مسار واضح: وصف الطلب → تأكيد النطاق → تنفيذ ميداني → مراجعة سريعة بعد الإنجاز عند الحاجة.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>خدمات متاحة في {name}</h2>
<!-- /wp:heading -->
<!-- wp:list -->
<ul>{links}</ul>
<!-- /wp:list -->
<!-- wp:paragraph -->
<p>هذه الروابط تقود إلى صفحات خدمة مرتبطة بـ{name}. إن لم تجد طلبك في القائمة، راسلنا على واتساب أو اتصل <strong>{PHONE}</strong> واكتب اسم المدينة والخدمة المطلوبة.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>كشف تسربات وعزل في {name}</h2>
<!-- /wp:heading -->
<!-- wp:paragraph -->
<p>ارتفاع فاتورة المياه، بقع سقف متكررة، أو تقشر دهان حول الحمامات قد يشير إلى تسرب خفي. في {name} نبدأ بفهم العَرَض ثم نحدد نطاق الفحص قبل أي تكسير. بعد تحديد المصدر يمكن الانتقال إلى عزل مناسب للسطح أو المنطقة الرطبة حسب حالة العقار.</p>
<!-- /wp:paragraph -->
<!-- wp:paragraph -->
<p>العزل الجيد يقلل انتقال الحرارة والرطوبة، لكنّه لا يغني عن إصلاح مصدر التسرب. لذلك نفصل بين مرحلة الكشف ومرحلة العزل حتى لا تُدفع تكلفة مرتين.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>تكييف وتنظيف ومكافحة في {name}</h2>
<!-- /wp:heading -->
<!-- wp:paragraph -->
<p>غسيل المكيفات وتنظيف الدكتات يخفف الغبار والروائح ويحسن تدفق الهواء داخل المنزل. التنظيف الدوري للشقق والفلل يقلل تراكم الأتربة خاصة بعد المواسم المزدحمة. أما مكافحة الحشرات فتُخطط حسب نوع الآفة ومناطق الاختباء، مع إرشادات سلامة واضحة للأسرة قبل وبعد الزيارة.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>سباكة وكهرباء ونقل عفش في {name}</h2>
<!-- /wp:heading -->
<!-- wp:paragraph -->
<p>تسربات ظاهرة، ضعف صرف، قواطع تفصل، أو إنارة غير مستقرة تحتاج تدخلاً ميدانياً سريعاً بعد وصف دقيق للعَرَض. كذلك نقل العفش داخل {name} أو منها إلى مدينة أخرى يعتمد على التغليف والمسار وطبيعة الأثاث، لا على وعد عام بالسعر قبل المعاينة.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>كيف تطلب خدمة في {name}؟</h2>
<!-- /wp:heading -->
<!-- wp:paragraph -->
<p>راسلنا على واتساب أو اتصل <strong>{PHONE}</strong> واكتب: المدينة ({name})، الحي، نوع العقار، وصف الطلب، وصورة إن أمكن. نؤكد التغطية والوقت والنطاق قبل التنفيذ. للمقارنة العامة راجع <a href="https://www.rukn-eltatawer.com/sa/cities/">كل المدن</a> و<a href="https://www.rukn-eltatawer.com/sa/pricing/">الأسعار</a> و<a href="https://www.rukn-eltatawer.com/sa/services/">الخدمات</a>.</p>
<!-- /wp:paragraph -->
<!-- wp:paragraph -->
<p>شركة ركن التطور تعمل برقم سعودي موحّد <strong>{PHONE}</strong>، مع جدولة مرنة حسب حيّك في {name}. لا نغيّر عنوان الصفحة لأغراض إعلانية؛ المحتوى هنا للتوجيه العملي نحو الخدمة الصحيحة.</p>
<!-- /wp:paragraph -->

<!-- wp:shortcode -->
[post_call]
<!-- /wp:shortcode -->
"""


BLEED = [
    (r"بسبب حرارة حضرية وغبار وضغط على الشبكات والتكييف", "بسبب طبيعة الطقس المحلي ونمط السكن"),
    (r"ضغط على الشبكات والتكييف", "ضغط الاستخدام اليومي على المنزل"),
    (r"إجهاد الشبكات في المواسم", "ضغط الاستخدام في المواسم"),
    (r"ارتفاع الأعطال في مواسم الذروة", "ارتفاع الشكاوى في مواسم الذروة"),
    (r"تآكل الشبكات وتسربات الحمامات", "الرطوبة ومناطق الصرف داخل المنزل"),
    (r"تسربات أسطح وعزل خارجي مع تقلب الحرارة", "الرطوبة وتقلبات الطقس المحيطة بالمنزل"),
    (r"تنفّذ الصيانة والمقاولات الخفيفة داخل السعودية", "تنفّذ الخدمة المطلوبة ميدانياً داخل السعودية"),
    (r"الصيانة والمقاولات الخفيفة", "الخدمة المطلوبة"),
]


THIN_BOOST = {
    "duct-cleaning": {
        "h2": "خطوات تنظيف الدكت ميدانياً",
        "paras": [
            "نبدأ بمعاينة فتحات الراجع والخطوط الظاهرة قدر الإمكان، ثم نحدد إن كان العمل على مجرى واحد أو شبكة كاملة فوق السقف المستعار.",
            "بعد عزل المنطقة المحيطة تُسحب الأتربة المتراكمة من المجرى، مع الاهتمام بالأكواع والمناطق منخفضة التدفق التي تتجمع فيها الأتربة.",
            "يُغسل الفلتر والوحدة المرتبطة حسب الحالة، ثم يُختبر تدفق الهواء بعد التنظيف لملاحظة الفرق قبل إغلاق السقف المستعار.",
            "في الفلل ذات الدكت الطويل قد يظهر تحسن التبريد بعد تنظيف المجرى حتى لو كانت الوحدة الخارجية سليمة ظاهرياً.",
            "لا يُنصح بتشغيل غسيل عشوائي بالماء داخل مجرى غير مجهز للصرف؛ الأسلوب يعتمد على نوع الدكت وحالة العزل حوله.",
        ],
        "faq": [
            ("هل يكفي غسيل الوحدة الداخلية؟", "غالباً لا إذا كان الغبار داخل المجرى فوق السقف. الوحدة قد تبدو نظيفة بينما الراجع يعيد الأتربة للغرفة."),
            ("كم مرة يُنصح بالتنظيف؟", "بعد مواسم الغبار أو عند ضعف التبريد مع نظافة ظاهرية للفلتر. الجدولة تعتمد على الحي ونوع العقار."),
        ],
    },
    "furniture-shipping": {
        "h2": "خطة شحن الأثاث بدون خدش",
        "paras": [
            "نبدأ بجرد القطع الحساسة: زجاج، خشب مطلي، أجهزة، وغرف تحتاج تفكيك أبواب أو رفوف قبل التحريك.",
            "التغليف يكون حسب السطح: بطانية وطبقة حماية للزوايا، وصناديق مناسبة للمفكك الصغير حتى لا يتداخل أثناء الطريق.",
            "مسار الشاحنة داخل الحي يُحدد مسبقاً إن أمكن، خاصة في الشوارع الضيقة أو الأبراج التي تحتاج تصريح تحميل.",
            "عند الشحن بين مدن السعودية نوضح وقت التحميل ونافذة التسليم التقريبية بعد معرفة المسافة وحجم الحمولة.",
            "التأمين والتنظيف النهائي ليسا بديلاً عن تغليف جيد؛ الوقاية من الخدش تبدأ من مرحلة الفك داخل المنزل.",
        ],
        "faq": [
            ("هل السعر ثابت قبل المعاينة؟", "لا. الحجم وعدد الغرف والطوابق والمسافة تغيّر التكلفة. نؤكد نطاقاً واضحاً بعد وصف الحمولة أو المعاينة."),
            ("هل تفككون غرف النوم والمطابخ؟", "نعم عند الاتفاق مسبقاً. بعض المطابخ المثبتة خارج نطاق النقل السكني المعتاد."),
        ],
    },
    "car-shipping": {
        "h2": "شحن السيارات بين المدن بحذر",
        "paras": [
            "نوضح نوع المركبة وحالتها (تعمل / لا تعمل) ومكان الاستلام والتسليم قبل حجز الموعد.",
            "الفحص الظاهري للخدوش الحالية يُوثق عند الاستلام لتقليل الخلاف بعد الوصول.",
            "اختيار النقل المفتوح أو المغلق يعتمد على الميزانية وحساسية الطلاء وطول الرحلة.",
            "في المدن الكثيفة نحدد نقطة تحميل سهلة للشاحنة بدل انتظار طويل داخل حي ضيق.",
            "بعد التسليم راجع مع المندوب حالة الإطارات والزجاج والأضواء بسرعة قبل المغادرة.",
        ],
        "faq": [
            ("هل تشحنون السيارات المتعطلة؟", "غالباً نعم مع معدات سحب مناسبة، ويُذكر ذلك عند الحجز لأن التكلفة تختلف."),
            ("كم يستغرق الوصول؟", "يعتمد على المسار والحمولة المشتركة. نذكر نافذة زمنية تقريبية لا موعداً فورياً مضموناً بلا سياق."),
        ],
    },
    "domestic-shipping": {
        "h2": "شحن داخلي منظم داخل المدينة وبين المدن",
        "paras": [
            "الشحن الداخلي يشمل طروداً وأثاثاً خفيفاً وأغراض عمل صغيرة، ويحتاج وصفاً دقيقاً للوزن والحجم.",
            "نحدد إن كان الاستلام من دور أرضي أو علوي، وهل يوجد مصعد، لأن ذلك يغيّر وقت الفريق.",
            "التغليف الجيد يقلل تلف الزوايا أثناء المناولة المتكررة داخل المستودع أو الشاحنة.",
            "للطلبات العاجلة داخل المدينة نؤكد نافذة اليوم نفسه فقط عند توفر جدول فعلي لا كوعد تسويقي.",
            "احتفظ بصورة للمحتويات وقائمة مختصرة؛ ذلك يسهّل المطابقة عند التسليم.",
        ],
        "faq": [
            ("هل يوجد تتبع؟", "نشارك تحديثات عبر واتساب حسب مرحلة الاستلام/التحرك/التسليم."),
            ("ما الذي لا يُشحن؟", "المواد الخطرة والسوائل القابلة للاشتعال والمواد الممنوعة نظاماً."),
        ],
    },
    "ac-cleaning-washing": {
        "h2": "غسيل المكيفات خطوة بخطوة",
        "paras": [
            "نفصل التيار ونحمي الجدار والأرضية حول الوحدة قبل فتح الغطاء وإخراج الفلتر.",
            "غسيل المبخرة والفلاتر يزيل طبقة الغبار الدهنية التي تخنق التبريد وتزيد استهلاك الكهرباء.",
            "للوحدات المركزية قد يلزم تنظيف إضافي للراجع القريب إن كان مغبراً بوضوح.",
            "بعد الغسيل نختبر التصريف والتبريد ونتأكد من عدم رذاذ ماء على الكهرباء المكشوفة.",
            "الغسيل الدوري أرخص من انتظار ضعف تبريد حاد في ذروة الصيف داخل المدينة.",
        ],
        "faq": [
            ("هل الغسيل يصلح نقص الفريون؟", "لا. نقص الغاز مشكلة منفصلة تُشخص بعد التأكد من نظافة التبادل الحراري."),
            ("هل يناسب السبليت والدكت؟", "نعم مع اختلاف الأسلوب. الدكت قد يحتاج وقتاً أطول بسبب المجاري."),
        ],
    },
}


def boost_html(kind: str, city: str, title: str) -> str:
    conf = THIN_BOOST[kind]
    paras = "".join(f"<p>{p.replace('المدينة', city) if False else p}</p>" for p in conf["paras"])
    # inject city naturally
    paras = paras.replace("داخل المدينة", f"داخل {city}").replace("في ذروة الصيف داخل المدينة", f"في ذروة الصيف داخل {city}")
    faqs = "".join(
        f"<h3>{q}</h3><p>{a}</p>" for q, a in conf["faq"]
    )
    return f"""
<h2>{conf['h2']} في {city}</h2>
<p>هذه الصفحة مخصّصة لخدمة <strong>{title}</strong> داخل <strong>{city}</strong> عبر شركة ركن التطور، برقم تواصل <strong>{PHONE}</strong>. نركز على التنفيذ الميداني الواضح بدل وعود عامة.</p>
{paras}
<h2>أسئلة شائعة حول الخدمة في {city}</h2>
{faqs}
<p>للطلب: واتساب أو اتصال <strong>{PHONE}</strong> مع ذكر المدينة ({city}) والحي ونوع العقار. <strong>الصفحة هذه مخصّصة</strong> لتوضيح نطاق الخدمة محلياً قبل الحجز.</p>
"""


def detect_thin_kind(slug: str) -> str | None:
    for k in THIN_BOOST:
        if slug.startswith(k) or k in slug:
            return k
    return None


def city_from_slug(slug: str) -> str:
    m = {
        "riyadh": "الرياض",
        "jeddah": "جدة",
        "mecca": "مكة المكرمة",
        "medina": "المدينة المنورة",
        "dammam": "الدمام",
        "khobar": "الخبر",
        "taif": "الطائف",
        "abha": "أبها",
    }
    for k, v in m.items():
        if slug.endswith(k) or f"-{k}" in slug:
            return v
    return "مدينتك"


def enrich_cities(results: dict):
    done = []
    for c in CITIES:
        html = city_html(c)
        put(f"/wp/v2/pages/{c['id']}", {"content": html, "excerpt": f"خدمات ركن التطور في {c['name']} مع روابط محلية ورقم {PHONE}."})
        done.append({"id": c["id"], "slug": c["slug"], "aw": ar_words(html)})
        print("city", c["slug"], "aw", ar_words(html), flush=True)
        time.sleep(0.2)
    results["cities"] = done


def enrich_thin(results: dict):
    thin_ids = [
        10880, 10906, 10932, 10958, 10984, 11010, 11036,
        12792, 12793, 12795, 12796, 12797, 12798, 12799,
        12802, 12803, 12805, 12806, 12807,
        12816, 12817, 12818, 12819, 12820, 12821, 12822, 12823,
        13104, 13105, 13106, 13107, 13108, 13109, 13110, 13111,
    ]
    done = []
    for pid in thin_ids:
        _, p = get(f"/wp/v2/posts/{pid}?context=edit&_fields=id,title,slug,content")
        slug = p["slug"]
        title = p["title"]["raw"]
        raw = p["content"].get("raw") or ""
        kind = detect_thin_kind(slug)
        if not kind:
            print("skip kind", pid, slug, flush=True)
            continue
        city = city_from_slug(slug)
        if "الصفحة هذه مخصّصة" in raw and ar_words(raw) >= 850:
            done.append({"id": pid, "slug": slug, "aw": ar_words(raw), "skipped": True})
            continue
        # remove previous boost marker duplicates
        raw2 = re.sub(r"<h2>خطوات تنظيف الدكت ميدانياً.*$", "", raw, flags=re.S)
        raw2 = re.sub(r"<h2>خطة شحن الأثاث بدون خدش.*$", "", raw2, flags=re.S)
        raw2 = re.sub(r"<h2>شحن السيارات بين المدن بحذر.*$", "", raw2, flags=re.S)
        raw2 = re.sub(r"<h2>شحن داخلي منظم.*$", "", raw2, flags=re.S)
        raw2 = re.sub(r"<h2>غسيل المكيفات خطوة بخطوة.*$", "", raw2, flags=re.S)
        new = raw2.rstrip() + "\n" + boost_html(kind, city, title)
        put(f"/wp/v2/posts/{pid}", {"content": new})
        done.append({"id": pid, "slug": slug, "aw": ar_words(new)})
        print("thin", pid, slug, "aw", ar_words(new), flush=True)
        time.sleep(0.2)
    results["thin"] = done


def fix_bleed(results: dict):
    fixed = 0
    samples = []
    page = 1
    while True:
        hdr, posts = get(
            f"/wp/v2/posts?per_page=100&page={page}&status=publish&context=edit&orderby=id&order=asc&_fields=id,title,slug,content"
        )
        if not posts:
            break
        for p in posts:
            title = p["title"]["raw"]
            slug = p["slug"]
            raw = p["content"].get("raw") or ""
            # skip pure AC pages unless also cleaning/pest/grass
            if re.search(r"تكييف|مكيف|duct|split-ac|central-ac", title + " " + slug) and not re.search(
                r"مكافحة|تنظيف|عشب|نقل|شحن|سباك|كهرب", title
            ):
                # still replace maint_line if present
                pass
            new = raw
            for a, b in BLEED:
                new = re.sub(a, b, new)
            if new != raw:
                put(f"/wp/v2/posts/{p['id']}", {"content": new})
                fixed += 1
                if len(samples) < 20:
                    samples.append({"id": p["id"], "slug": slug})
                if fixed % 25 == 0:
                    print("bleed fixed", fixed, flush=True)
        print("bleed page", page, "fixed", fixed, flush=True)
        if page >= int(hdr.get("X-WP-TotalPages", page)):
            break
        page += 1
    results["bleed_fixed"] = fixed
    results["bleed_samples"] = samples


def fix_post_call(results: dict):
    done = []
    for pid in [12801, 12804]:
        _, p = get(f"/wp/v2/posts/{pid}?context=edit&_fields=id,slug,content")
        raw = p["content"].get("raw") or ""
        if "[post_call]" not in raw:
            raw = raw.rstrip() + "\n\n[post_call]\n"
            put(f"/wp/v2/posts/{pid}", {"content": raw})
            done.append(pid)
            print("post_call", pid, flush=True)
    results["post_call_fixed"] = done


def enrich_core_pages(results: dict):
    """Light enrichment for about/contact/cities index — content only."""
    pages = {
        7465: (
            "المدن",
            f"""<!-- wp:paragraph -->
<p>تجمع صفحة المدن في <strong>شركة ركن التطور</strong> مداخل الخدمات المنزلية داخل المملكة العربية السعودية. نعمل بجدولة مرنة لتغطية احتياجات المنازل والفلل والشقق في الرياض وجدة ومكة والمدينة والدمام والخبر والطائف وأبها، مع رقم تواصل موحّد <strong>{PHONE}</strong>.</p>
<!-- /wp:paragraph -->
<!-- wp:heading --><h2>لماذا صفحة المدن مهمة؟</h2><!-- /wp:heading -->
<!-- wp:paragraph -->
<p>لأن احتياج المنزل يتأثر بالمناخ ونوع التشطيب. غبار الرياض غير رطوبة جدة، وأمطار أبها تظهر ضعف العزل أسرع. لذلك نبني صفحات مدينة بروابط داخلية للخدمات الأكثر طلباً بدل نص واحد منسوخ لكل المملكة.</p>
<!-- /wp:paragraph -->
<!-- wp:heading --><h2>اختر مدينتك</h2><!-- /wp:heading -->
<!-- wp:list -->
<ul>
<li><a href="https://www.rukn-eltatawer.com/sa/cities/riyadh/">الرياض</a> — كشف تسربات وعزل وتنظيف وتكييف</li>
<li><a href="https://www.rukn-eltatawer.com/sa/cities/jeddah/">جدة</a> — تكييف وتنظيف وتسربات</li>
<li><a href="https://www.rukn-eltatawer.com/sa/cities/makkah/">مكة المكرمة</a> — خدمات منزلية مع مراعاة المواسم</li>
<li><a href="https://www.rukn-eltatawer.com/sa/cities/madinah/">المدينة المنورة</a></li>
<li><a href="https://www.rukn-eltatawer.com/sa/cities/dammam/">الدمام</a></li>
<li><a href="https://www.rukn-eltatawer.com/sa/cities/khobar/">الخبر</a></li>
<li><a href="https://www.rukn-eltatawer.com/sa/cities/taif/">الطائف</a></li>
<li><a href="https://www.rukn-eltatawer.com/sa/cities/abha/">أبها</a></li>
</ul>
<!-- /wp:list -->
<!-- wp:heading --><h2>كيف تختار الخدمة من صفحة المدينة؟</h2><!-- /wp:heading -->
<!-- wp:paragraph -->
<p>ادخل مدينة العقار، ثم افتح رابط الخدمة الأقرب لمشكلتك: تسرب، عزل، تنظيف، تكييف، مكافحة، سباكة، كهرباء أو نقل. إن ترددت، راسلنا على <strong>{PHONE}</strong> بوصف قصير وصورة إن أمكن.</p>
<!-- /wp:paragraph -->
<!-- wp:paragraph -->
<p>راجع أيضاً <a href="https://www.rukn-eltatawer.com/sa/services/">الخدمات</a> و<a href="https://www.rukn-eltatawer.com/sa/pricing/">الأسعار</a>. السعر النهائي يُذكر بعد فهم النطاق لا من جدول عام.</p>
<!-- /wp:paragraph -->
<!-- wp:shortcode -->
[post_call]
<!-- /wp:shortcode -->
""",
        ),
    }
    done = []
    for pid, (label, html) in pages.items():
        put(f"/wp/v2/pages/{pid}", {"content": html})
        done.append({"id": pid, "label": label, "aw": ar_words(html)})
        print("page", label, ar_words(html), flush=True)
    results["core_pages"] = done


def main():
    results = {"note": "SEO titles intentionally untouched", "phone": PHONE}
    print("=== enrich cities ===", flush=True)
    enrich_cities(results)
    print("=== enrich core pages ===", flush=True)
    enrich_core_pages(results)
    print("=== fix post_call ===", flush=True)
    fix_post_call(results)
    print("=== enrich thin ===", flush=True)
    enrich_thin(results)
    print("=== fix bleed ===", flush=True)
    fix_bleed(results)
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print("WROTE", OUT, flush=True)
    print("SUMMARY", json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in results.items()}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
