#!/usr/bin/env python3
"""Make SA posts index-ready: unique local content, strip template spam, safe for crawl."""

from __future__ import annotations

import hashlib
import html as html_lib
import json
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

BASE = "https://www.rukn-eltatawer.com/sa"
AUTH = HTTPBasicAuth("cursor", "PCkk ig95 Gu6c zOgC GLYG FYsk")
H = {"User-Agent": "Mozilla/5.0 RuknIndexReady/1.0", "Content-Type": "application/json"}
PHONE = "0568060309"
ROOT = Path(__file__).resolve().parents[1]
CITY_META = json.loads((ROOT / "data/city-local-meta.json").read_text(encoding="utf-8"))

IMG = {
    "leak": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2026/08/water-leak-detection.webp",
    "leak2": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2026/08/leak-detection-machien.webp",
    "insul": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2026/08/roof-insulation-ae.webp",
    "clean": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/12/cleaning-6.webp",
    "pest": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/12/clean-2.webp",
    "ac": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/08/plumber-1.webp",
    "plumb": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/08/plumbing.webp",
    "elec": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/12/toolbox.webp",
    "build": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/12/plumber.webp",
    "default": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2020/10/equipment.webp",
}

HUBS = {
    "leak": ("https://www.rukn-eltatawer.com/sa/water-leak-detection-riyadh/", "كشف تسربات المياه في الرياض"),
    "insul": ("https://www.rukn-eltatawer.com/sa/roof-insulation-riyadh/", "عزل الأسطح في الرياض"),
    "clean": ("https://www.rukn-eltatawer.com/sa/apartment-cleaning-in-riyadh/", "تنظيف الشقق في الرياض"),
    "ac": ("https://www.rukn-eltatawer.com/sa/split-ac-maintenance-riyadh/", "صيانة مكيفات سبليت بالرياض"),
    "pest": ("https://www.rukn-eltatawer.com/sa/cockroach-control-riyadh/", "مكافحة الصراصير بالرياض"),
    "plumb": ("https://www.rukn-eltatawer.com/sa/home-plumber-riyadh/", "سباك منازل بالرياض"),
    "elec": ("https://www.rukn-eltatawer.com/sa/home-electrician-elec-riyadh/", "كهربائي منازل بالرياض"),
}

EXTRA_CITY = {
    "الرياض": {"region": "الرياض", "climate": "حرارة حضرية وغبار", "risk": "ضغط على الشبكات والتكييف", "districts": ["النسيم", "الملز", "العليا", "الياسمين", "طويق", "حطين"], "property": "فلل وشقق", "hook": "تكرار العَرَض رغم الحلول المؤقتة", "case": "فيلا في النسيم احتاجت تشخيصاً أدق قبل التنفيذ", "note": "الرياض تحتاج استجابة سريعة قبل توسع الضرر."},
    "جدة": {"region": "مكة المكرمة", "climate": "رطوبة ساحلية", "risk": "تآكل وتسارع تلف التشطيب", "districts": ["الروضة", "أبحر", "الصفا", "النعيم", "الفيصلية"], "property": "شقق وفلل ساحلية", "hook": "رطوبة أو أعطال متكررة قرب الساحل", "case": "شقة في أبحر عاد فيها العَرَض بعد حل سطحي", "note": "جدة تحتاج تفريقاً بين أثر الرطوبة والمشكلة الفعلية."},
    "مكة": {"region": "مكة المكرمة", "climate": "حرارة وضغط موسمي", "risk": "إجهاد الشبكات في المواسم", "districts": ["العزيزية", "الشوقية", "العوالي", "النسيم"], "property": "شقق ومبانٍ سكنية", "hook": "ارتفاع الأعطال في مواسم الذروة", "case": "شقة في العزيزية احتاجت تدخلاً قبل الموسم", "note": "مكة تستفيد من الصيانة المبكرة قبل الذروة."},
    "المدينة": {"region": "المدينة", "climate": "جو حار جاف", "risk": "تشقق وصلات وإجهاد أجهزة", "districts": ["قباء", "العوالي", "الحرة الشرقية", "الملك فهد"], "property": "شقق وفلل", "hook": "هدر أو عطل يظهر مع الاستهلاك المرتفع", "case": "منزل في العوالي تأكد فيه المصدر بعد فحص مرتب", "note": "المدينة المنورة تحتاج تدخلاً مبكراً قبل توسع الضرر."},
    "الدمام": {"region": "الشرقية", "climate": "رطوبة وحرارة", "risk": "ضغط على الشبكات والتكييف", "districts": ["الفيصلية", "الشاطئ", "الجلوية", "أحد"], "property": "فلل وأبراج", "hook": "تكرار نفس العطل خلال أسابيع", "case": "فيلا في الفيصلية كان التشخيص أوفر من التخمين", "note": "الدمام تحتاج خطة تناسب الرطوبة والحر."},
    "الخبر": {"region": "الشرقية", "climate": "رطوبة ساحلية", "risk": "تلف أسرع للتشطيب والأجهزة", "districts": ["العقربية", "الحزام", "اليرموك", "الثقبة"], "property": "شقق وفلل", "hook": "عودة المشكلة بعد حلول سريعة", "case": "شقة في العقربية احتاجت نطاقاً أوضح قبل التنفيذ", "note": "الخبر تستفيد من تشخيص دقيق قبل أي توسع."},
    "الطائف": {"region": "مكة المكرمة", "climate": "برودة نسبية وأمطار موسمية", "risk": "أثر المطر والعزل والتقلبات", "districts": ["الشفا", "الحوية", "الروضة", "السلامة"], "property": "فلل واستراحات", "hook": "عَرَض يظهر بعد موجة طقس", "case": "استراحة في الشفا ارتبطت المشكلة بظروف موسمية", "note": "الطائف تربط كثيراً بين التوقيت الموسمي ونوع التدخل."},
    "أبها": {"region": "عسير", "climate": "أمطار وضباب", "risk": "رطوبة وعزل ونقاط ضعف خارجية", "districts": ["المنسك", "الموظفين", "الوردتين", "الخالدية"], "property": "فلل جبلية", "hook": "تكرار الرطوبة أو الأعطال مع تقلب الطقس", "case": "فيلا في المنسك احتاجت فحص مصدر قبل الترميم", "note": "أبها تحتاج ربطاً بين العَرَض والظروف الجبلية."},
}

SERVICE_PACKS = {
    "leak": {
        "label": "كشف تسربات المياه",
        "topic": "leak",
        "signs": ["تحرك العداد والصنابير مغلقة", "ارتفاع فاتورة المياه", "بقع رطوبة أو تقشر دهان", "رائحة عفن متكررة", "انخفاض ضغط في جناح واحد"],
        "steps": ["فحص العداد ونقاط الاستهلاك", "تتبع جهازي للمصدر", "تقرير واضح قبل الفتح", "إصلاح ضيق عند الطلب", "اختبار تأكد بعد الإصلاح"],
        "mistakes": ["إعادة دهان فوق الرطوبة", "تكسير عشوائي بعيد عن المسار", "إهمال خطوط الري الخارجية", "تأجيل الفحص حتى يتوسع الضرر"],
        "faqs": [
            ("هل الكشف يحتاج تكسير؟", "غالباً لا. نحدد المصدر أولاً ولا نفتح إلا نطاقاً ضيقاً بعد التأكيد."),
            ("كم مدة الفحص؟", "عادة من ساعة إلى ثلاث حسب المساحة وعدد نقاط الشك."),
            ("هل يتوفر إصلاح بعد الكشف؟", "نعم عند الطلب مع توضيح النطاق قبل التنفيذ."),
        ],
    },
    "insul": {
        "label": "العزل",
        "topic": "insul",
        "signs": ["حرارة دور علوي مرتفعة", "رطوبة سقف بعد المطر أو غسيل السطح", "تشقق طبقة عزل قديمة", "أثر حول الخزان", "تقشر دهان متكرر في السقف"],
        "steps": ["معاينة السطح/الخزان والميول", "تجهيز السطح ومعالجة النقاط الضعيفة", "تنفيذ نظام عزل مناسب", "فحص نقاط الصرف", "إرشادات وقاية موسمية"],
        "mistakes": ["عزل فوق رطوبة نشطة", "إهمال الميول والصرف", "اختيار مادة غير مناسبة للمناخ", "تأجيل العزل حتى ضرر السقف"],
        "faqs": [
            ("هل العزل للأسطح فقط؟", "لا، يشمل أيضاً الخزانات عند الحاجة حسب المعاينة."),
            ("متى أفضل وقت؟", "قبل موسم الأمطار أو فور ظهور تشققات ورطوبة."),
            ("هل يلزم كشف تسرب أولاً؟", "أحياناً نعم إذا كان المصدر غير واضح."),
        ],
    },
    "clean": {
        "label": "التنظيف",
        "topic": "clean",
        "signs": ["غبار يعود بسرعة", "روائح في المطبخ/الحمام", "بقع مفروشات ثابتة", "حاجة تنظيف قبل انتقال أو مناسبات", "تراكم بعد فترة طويلة"],
        "steps": ["تحديد الغرف ذات الأولوية", "تنظيف عميق للنقاط المتفق عليها", "الاهتمام بالمطابخ والحمامات", "تعقيم نقاط اللمس عند الطلب", "مراجعة سريعة قبل التسليم"],
        "mistakes": ["خلط تنظيف روتيني بتنظيف عميق", "مواد قاسية تضر الأسطح", "إغفال مصدر الرائحة الحقيقي", "توقع نتيجة جلسة قصيرة على تراكم كبير"],
        "faqs": [
            ("هل توفرون المواد؟", "نعم ضمن الخدمة المعتادة مع مراعاة الأسطح الحساسة."),
            ("هل يمكن تخصيص غرف؟", "نعم، يمكن التركيز على نقاط محددة."),
            ("كم تستغرق الزيارة؟", "حسب المساحة ونوع التنظيف المطلوب."),
        ],
    },
    "pest": {
        "label": "مكافحة الحشرات",
        "topic": "pest",
        "signs": ["ظهور متكرر رغم الرش السطحي", "أثر ليلي في المطبخ", "دخول من مجارٍ أو شقوق", "عودتها بعد أيام", "قلق صحي من التكرار"],
        "steps": ["معاينة المداخل ومصادر الجذب", "خطة مكافحة مناسبة للنوع", "تنفيذ مرتب مع إرشادات", "نصائح وقاية بعد الرش", "متابعة عند الحاجة"],
        "mistakes": ["رش عشوائي دون تحديد النوع", "إهمال المداخل والفضلات", "تكرار نفس الرشة بلا نتيجة", "تنظيف متأخر يضعف أثر المكافحة"],
        "faqs": [
            ("هل آمنة للأطفال؟", "نوضح الاحتياطات ووقت العودة للمساحة حسب المادة المستخدمة."),
            ("كم جلسة تلزم؟", "تختلف حسب النوع وشدة الإصابة."),
            ("هل تمنعون العودة؟", "المكافحة تقلل الإصابة جداً مع الالتزام بالوقاية."),
        ],
    },
    "ac": {
        "label": "التكييف",
        "topic": "ac",
        "signs": ["ضعف تبريد", "رائحة من الوحدة", "صوت غير طبيعي", "تسرب مياه من المكيف", "ارتفاع استهلاك مع أداء ضعيف"],
        "steps": ["تشخيص العَرَض ونوع الوحدة", "تنظيف/صيانة أو إصلاح حسب الحالة", "فحص أداء أولي", "نصائح تشغيل", "تركيب أو تعاقد دوري عند الطلب"],
        "mistakes": ["تأجيل الصيانة حتى ذروة الحر", "غسيل غير مناسب للوحدة", "تجاهل تسريب الماء", "تشغيل مستمر بلا فلتر نظيف"],
        "faqs": [
            ("هل تشمل السبليت والمركزي؟", "نعم حسب نوع الطلب والتغطية."),
            ("متى الصيانة الدورية؟", "يفضّل قبل الصيف ومتابعة منتصف الموسم."),
            ("هل يتوفر تركيب جديد؟", "نعم عند الطلب مع توضيح النطاق."),
        ],
    },
    "plumb": {
        "label": "السباكة",
        "topic": "plumb",
        "signs": ["ضعف تصريف", "تسريب محابس", "سخان لا يعمل بكفاءة", "رطوبة حول المواسير", "ضغط غير منتظم"],
        "steps": ["معاينة نقطة العطل", "تحديد الإصلاح الأدنى الكافي", "تنفيذ مرتب", "اختبار سريع", "نصيحة لمنع التكرار"],
        "mistakes": ["تركيب قطع رديئة مؤقتة", "إهمال المصدر والاكتفاء بالعَرَض", "فتح واسع بلا داع", "تأجيل إصلاح يوسع الرطوبة"],
        "faqs": [
            ("هل تتوفر طوارئ؟", "حسب الجدولة؛ الحالات المتوسعة تُوضح عند الحجز."),
            ("هل تعملون مع فلل وشقق؟", "نعم."),
            ("هل يلزم كشف تسرب؟", "إذا كان العَرَض يشير لهدر خفي قد نوجّه لذلك."),
        ],
    },
    "elec": {
        "label": "الكهرباء",
        "topic": "elec",
        "signs": ["فصل متكرر", "سخونة في نقاط", "إنارة ضعيفة", "أعطال لوحات", "حاجة تمديدات جديدة"],
        "steps": ["تقييم الأمان أولاً", "تحديد العطل أو نطاق التمديد", "تنفيذ بحذر", "اختبار النقاط", "إرشادات استخدام آمن"],
        "mistakes": ["تجاهل سخونة القواطع", "تمديدات غير محكمة", "تحميل زائد على دائرة واحدة", "تأجيل عطل قد يسبب خطراً"],
        "faqs": [
            ("هل تعملون طوارئ؟", "حسب التغطية اليومية؛ اذكر أن الحالة طارئة عند الاتصال."),
            ("هل تشمل الإنارة واللوحات؟", "نعم ضمن نطاق الخدمة المطلوبة."),
            ("هل تحتاج تصريحاً؟", "حسب نوع العمل؛ نوضح ذلك عند المعاينة."),
        ],
    },
    "build": {
        "label": "الصيانة والمقاولات الخفيفة",
        "topic": "build",
        "signs": ["تشققات أو تلف تشطيب", "حاجة ترميم بعد إصلاح", "باب/نافذة/جلسة تحتاج ضبطاً", "تدهور مظهر خارجي", "صيانة دورية متأخرة"],
        "steps": ["معاينة العيب", "تحديد نطاق الإصلاح", "تنفيذ مرتب", "تنظيف محيط العمل", "ملاحظات وقاية"],
        "mistakes": ["ترميم فوق سبب غير محلول", "مواد غير مناسبة", "تأجيل يوسّع التلف", "طلب تجميلي قبل إصلاح المصدر"],
        "faqs": [
            ("هل تناسب المنازل فقط؟", "غالباً نعم للسكني والفلل والملاحق."),
            ("هل تربطون بخدمات أخرى؟", "نعم عند الحاجة مثل عزل أو سباكة."),
            ("كيف أحجز؟", f"عبر {PHONE} مع وصف العيب والحي."),
        ],
    },
}


def wc(html: str) -> int:
    t = re.sub(r"\[[^\]]+\]", " ", html or "")
    t = re.sub(r"<[^>]+>", " ", t)
    return len(re.findall(r"[\w\u0600-\u06FFA-Za-z0-9]+", html_lib.unescape(t)))


def pick(key: str, options: list):
    h = int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)
    return options[h % len(options)]


def topic_of(title: str) -> str:
    if any(k in title for k in ["تسرب", "تسريب"]):
        return "leak"
    if any(k in title for k in ["عزل", "فوم", "عازل"]):
        return "insul"
    if any(k in title for k in ["تنظيف", "تعقيم", "جلي"]):
        return "clean"
    if any(k in title for k in ["مكافحة", "حشرات", "صراصير", "نمل", "بق", "عقارب", "بعوض"]):
        return "pest"
    if any(k in title for k in ["مكيف", "تكييف", "فريون", "دكت", "سبليت", "تبريد"]):
        return "ac"
    if any(k in title for k in ["سباك", "سباكة", "سخان", "مضخ", "مواسير", "صحية", "مجاري", "تسليك"]):
        return "plumb"
    if any(k in title for k in ["كهرب", "إنارة", "لوحة"]):
        return "elec"
    return "build"


def city_of(title: str) -> str:
    for c in ["الرياض", "جدة", "مكة", "المدينة", "الدمام", "الخبر", "الطائف", "أبها"]:
        if c in title:
            return c
    # fallbacks from longer forms
    if "مكة المكرمة" in title:
        return "مكة"
    if "المدينة المنورة" in title:
        return "المدينة"
    m = re.search(r"ب(?:ال)?([^\s]+)$", title)
    if m:
        return m.group(1)
    return "الرياض"


def get_meta(city: str) -> dict:
    if city in CITY_META:
        return dict(CITY_META[city])
    if city in EXTRA_CITY:
        return dict(EXTRA_CITY[city])
    for k, v in {**CITY_META, **EXTRA_CITY}.items():
        if k in city or city in k:
            return dict(v)
    return dict(EXTRA_CITY["الرياض"])


def service_name(title: str) -> str:
    t = re.sub(r"^شركة\s+", "", title)
    t = re.sub(r"^فني\s+", "", t)
    t = re.sub(r"^سباك\s+", "سباك ", t)
    t = re.sub(r"\s+ب(?:ال)?(?:الرياض|جدة|مكة(?: المكرمة)?|المدينة(?: المنورة)?|الدمام|الخبر|الطائف|أبها).*$", "", t)
    return t.strip() or title


def strip_junk(body: str) -> str:
    body = body or ""
    body = body.replace("{PHONE_RUKN}", PHONE).replace("{PHONE}", PHONE)
    body = body.replace("01556644443", PHONE).replace("+971", "+966")
    body = re.sub(
        r'<div[^>]*>\s*(?:<a[^>]+href="(?:tel:|https?://wa\.me/)[^"]*"[^>]*>.*?</a>\s*){1,4}</div>',
        "",
        body,
        flags=re.S | re.I,
    )
    return body



def build_unique(title: str) -> tuple[str, str]:
    city = city_of(title)
    topic = topic_of(title)
    pack = SERVICE_PACKS.get(topic, SERVICE_PACKS["build"])
    meta = get_meta(city)
    svc = service_name(title)
    districts = meta.get("districts") or EXTRA_CITY.get(city, EXTRA_CITY["الرياض"])["districts"]
    dcsv = "، ".join(districts[:5])
    dcsv2 = "، ".join(districts[1:6])
    img = IMG.get(pack["topic"], IMG["default"])
    img2 = IMG.get("leak2" if topic == "leak" else "plumb" if topic in ("ac", "plumb") else "clean", IMG["default"])
    hub = HUBS.get(topic)
    seed = f"{title}|{city}|{topic}"

    intro = pick(seed + "i", [
        f"إذا كنت تبحث عن <strong>{html_lib.escape(svc)}</strong> في <strong>{city}</strong> ضمن منطقة {meta.get('region', city)}، فابدأ بتشخيص واضح ثم تنفيذ بنطاق مفهوم.",
        f"في <strong>{city}</strong> يتكرر الطلب على {html_lib.escape(svc)} بسبب {meta.get('climate', 'طبيعة المنطقة')} و{meta.get('risk', 'ضغط الاستخدام')}. ركن التطور يضبط الخطة حسب الحي ونوع العقار.",
        f"<strong>ركن التطور</strong> تقدّم {html_lib.escape(svc)} لـ{meta.get('property', 'المنازل')} في {city} مع توضيح ما سيتم قبل أي توسع غير لازم.",
    ])
    local_story = pick(seed + "s", [
        f"مثال من {city}: {meta.get('case', 'حالة محلية احتاجت تشخيصاً أدق')}. مثل هذه الحالات تُحل أسرع عندما لا نبدأ بالتخمين.",
        f"ملاحظة تشغيلية في {city}: {meta.get('note', 'التدخل المبكر يقلل التكلفة')}. كل يوم تأخير قد يوسّع الضرر على التشطيب.",
        f"لأن {meta.get('hook', 'العَرَض يتكرر')} شائع في أحياء مثل {districts[0] if districts else city}، نوثق العَرَض أولاً ثم نختار أقل تدخل كافٍ.",
    ])
    timing = pick(seed + "t", [
        f"أفضل وقت غالباً قبل تفاقم العَرَض أو قبل موسم الذروة المرتبط بـ{html_lib.escape(pack['label'])} في {city}.",
        f"إذا كان العَرَض يتوسع أسبوعياً داخل {city}، فالحجز المبكر أوفر من انتظار ترميم أكبر.",
        f"بعد انتقال سكن أو ملاحظة مفاجئة في {city}، الفحص/التنفيذ السريع يمنع تحول المشكلة لنقطة مزمنة.",
    ])
    property_line = pick(seed + "p", [
        f"في الشقق داخل {city} نركز على سرعة الوصول والنقاط عالية الاستخدام مع احترام الجيران وضيق المساحة.",
        f"في الفلل داخل {city} نوزّع الأولويات على الأدوار والملحقات وأي نقاط خارجية مرتبطة بنفس العَرَض.",
        f"سواء كان العقار من فئة {meta.get('property', 'المنازل')}، نضبط أدوات {html_lib.escape(pack['label'])} حسب التشطيب وسهولة الوصول.",
    ])

    signs = "\n".join(f"<li>{s}</li>" for s in pack["signs"])
    steps = "\n".join(f"<li>{s}</li>" for s in pack["steps"])
    mistakes = "\n".join(f"<li>{s}</li>" for s in pack["mistakes"])
    faqs = ""
    for q, a in pack["faqs"]:
        faqs += f"<h3>{q}</h3>\n<p>{a}</p>\n"
    faqs += f"<h3>هل تغطون أحياء {city}؟</h3>\n<p>نعم حسب الجدولة، بما يشمل {dcsv} وغالباً امتدادات قريبة مثل {dcsv2}.</p>\n"
    faqs += f"<h3>كيف أحجز {html_lib.escape(svc)} في {city}؟</h3>\n<p>عبر الاتصال أو الواتساب على {PHONE}. اذكر الحي ونوع العقار ووصف العَرَض بجملة واضحة.</p>\n"
    faqs += f"<h3>هل السعر ثابت في {city}؟</h3>\n<p>لا. يتغير حسب المساحة وشدة الحالة. نوضّح النطاق قبل الأعمال الإضافية.</p>\n"

    hub_html = ""
    if hub:
        hub_html = f'<p>مرجع عام مرتبط: <a href="{hub[0]}">{hub[1]}</a> — مع تخصيص التنفيذ لواقع {city}.</p>'


    # Long unique expansions to reach index-ready depth without filler loops
    expand_a = pick(seed + "ea", [
        f"خدمة {html_lib.escape(svc)} في {city} لا تُدار بنفس أسلوب مدينة أخرى لأن كثافة الأحياء ونوع العقارات وطريقة الاستخدام اليومية تختلف. لذلك نسأل عن الحي ونوع العقار منذ أول تواصل على {PHONE} قبل أن نقترح أي نطاق تنفيذ.",
        f"كثير من طلبات {html_lib.escape(svc)} داخل {city} تأتي بعد محاولات منزلية متكررة لم تغلق المشكلة. في هذه الحالة نبدأ بإعادة تعريف العَرَض: هل هو جديد أم متكرر؟ هل يرتبط بموسم؟ هل يظهر في نقطة واحدة أم في أكثر من مكان؟",
        f"الهدف من زيارة {html_lib.escape(pack['label'])} في {city} هو نتيجة يمكن قياسها: انخفاض العَرَض، وضوح السبب، ومعرفة الخطوة التالية إن وجدت. هذا أفضل من وعود عامة لا ترتبط بواقع منزلك.",
    ])
    expand_b = pick(seed + "eb", [
        f"عند مقارنة الخيارات في {city} اسأل عن أسلوب التشخيص، وما الذي يشمله السعر، وهل هناك أعمال إضافية محتملة بعد المعاينة. هذه الأسئلة تحميك من مفاجآت وتجعل قرارك أوضح قبل التنفيذ.",
        f"في أحياء مثل {dcsv} يختلف الوصول وطبيعة التشطيبات؛ لذلك التفاصيل الصغيرة (دور العقار، وجود ملحق، قرب نقطة العطل من التشطيب الحساس) تغيّر خطة العمل حتى داخل نفس المدينة.",
        f"إذا كان لديك صور للعَرَض أو تاريخ تقريبي لظهوره في {city}، أرسلها عند الحجز. التوثيق يختصر وقت المعاينة ويجعل تنفيذ {html_lib.escape(svc)} أدق من أول زيارة.",
    ])
    expand_c = pick(seed + "ec", [
        f"بعد انتهاء التنفيذ ننصح بمراقبة بسيطة خلال يومين إلى ثلاثة. إذا عاد العَرَض بنفس القوة، لا تكرر الحلول العشوائية؛ تواصل مباشرة لتقييم سريع. الإغلاق الصحيح للمشكلة أوفر من تكرار زيارات بلا تشخيص.",
        f"الربط مع خدمة مساندة يتم فقط عند الحاجة الفعلية. أحياناً يكفي نطاق {html_lib.escape(svc)} وحده، وأحياناً يظهر أن المصدر مرتبط بخدمة أخرى. نوضح ذلك بصراحة بدل فرض باقات غير لازمة.",
        f"للعملاء الذين يريدون تنظيماً أطول أمداً داخل {city}، يمكن تحويل الزيارة إلى بداية خطة وقاية موسمية تناسب {meta.get('climate', 'المناخ المحلي')} بدل الانتظار حتى العطل الكامل في كل مرة.",
    ])
    sec_expand = f"""
<h2>تفاصيل عملية لأصحاب المنازل في {city}</h2>
<p>{expand_a}</p>
<p>{expand_b}</p>
<p>{expand_c}</p>
<h2>ماذا تجهز قبل وصول الفريق؟</h2>
<ul>
<li>وصف مختصر للعَرَض باللغة التي تناسبك مع ذكر الحي داخل {city}.</li>
<li>تأمين وصول آمن لنقطة المشكلة وإبعاد العوائق البسيطة إن أمكن.</li>
<li>الإفصاح عن أي محاولة سابقة أو مواد استُخدمت على نفس النقطة.</li>
<li>تحديد الأولوية إذا كان الوقت محدوداً (أهم غرفة/نقطة أولاً).</li>
</ul>
<p>هذه التحضيرات البسيطة تجعل زيارة {html_lib.escape(svc)} أسرع وتعطي نتيجة أوضح في نفس الموعد.</p>
<h2>سيناريوهات متكررة في {city}</h2>
<ul>
<li>عَرَض مفاجئ تريد معرفة إن كان يحتاج تدخلاً اليوم.</li>
<li>مشكلة متكررة بعد حلول مؤقتة.</li>
<li>تحضير موسمي قبل الحر أو الأمطار أو استقبال ضيوف.</li>
<li>طلب ربط مع فحص مساند إذا كان السبب غير واضح.</li>
</ul>
<p>في كل سيناريو نبدأ من وصفك ثم المعاينة، ونكتب نطاقاً يناسب عقارك في {city} لا قالباً ثابتاً لكل العملاء.</p>
<h2>الفرق بين الحل السريع والحل الصحيح</h2>
<p>الحل السريع قد يخفف العَرَض ساعات أو أياماً، ثم يعود. الحل الصحيح لـ{html_lib.escape(svc)} في {city} يمر عبر فهم السبب، ثم أقل تدخل كافٍ، ثم وقاية بسيطة. هذا المسار أطول قليلاً في الشرح، لكنه أوفر على المدى المتوسط.</p>
<p>إذا طلبت سرعة قصوى بسبب ضرر يتوسع، نوازن بين سرعة الاستجابة ودقة النطاق. أخبرنا بذلك منذ الرسالة الأولى على {PHONE} حتى لا يضيع الوقت في ترتيبات غير مناسبة لحالتك.</p>
<h2>لغة واضحة قبل التنفيذ</h2>
<p>قبل أن يبدأ الفريق نوضّح بقدر الإمكان: ما الذي سيُفحص أو يُنفذ؟ ما الذي لن يدخل في النطاق الحالي؟ وهل هناك احتمال لأعمال إضافية بعد اكتشاف جديد؟ الوضوح هنا يحمي الطرفين ويجعل تجربة {html_lib.escape(pack['label'])} داخل {city} أكثر احترافية.</p>
<p>بعد الزيارة تحتفظ بملخص بسيط لما تم. إذا احتجت متابعة لاحقاً، يكون النقاش مبنياً على وقائع الزيارة لا على افتراضات عامة.</p>
"""

    order = int(hashlib.md5(seed.encode()).hexdigest(), 16) % 3


    sec_why = f"""
<h2>ما الذي يميز الطلب على {html_lib.escape(svc)} داخل {city}؟</h2>
<p>تقع {city} في نطاق <strong>{meta.get('region', city)}</strong> حيث {meta.get('climate', 'ظروف محلية واضحة')}. هذا المناخ يرفع احتمال <strong>{meta.get('risk', 'تكرار الأعطال')}</strong> خاصة في {meta.get('property', 'المنازل')}.</p>
<p>{local_story}</p>
<p>{property_line}</p>
<p>{timing}</p>
"""
    sec_cover = f"""
<h2>نطاق الوصول في {city}</h2>
<p>نخدم أحياء {city} وفق الجدول اليومي، ومن أبرزها:</p>
<ul>
{''.join(f'<li>{d}</li>' for d in districts[:6])}
</ul>
<p>اذكر الحي عند الحجز. معرفة أنك في {districts[0] if districts else city} أو جواره تساعدنا على ترتيب الوصول والمعدات الصحيحة لـ{html_lib.escape(svc)}.</p>
<p>إذا كان طلبك خارج الأحياء المعتادة حول {city}، وضّح الموقع وسنخبرك بإمكانية التغطية لنفس اليوم أو أقرب جدولة.</p>
"""
    sec_signs = f"""
<h2>علامات تستدعي الخدمة الآن في {city}</h2>
<ul>
{signs}
<li>{meta.get('hook', 'تكرار العَرَض رغم المحاولات السابقة')}.</li>
<li>أثر متكرر في نفس الزاوية بعد كل معالجة سطحية.</li>
</ul>
<p>لا تنتظر حتى يتحول العَرَض إلى ضرر تشطيب واسع. في {city} التأجيل عادة أغلى من الفحص/التنفيذ المبكر.</p>
"""
    sec_steps = f"""
<h2>كيف نعمل خطوة بخطوة؟</h2>
<ol>
<li>تواصل على {PHONE} مع الحي ووصف العَرَض.</li>
{steps}
</ol>
<p style="margin:28px 0;"><img src="{img2}" alt="{html_lib.escape(svc)} في {city}" loading="lazy" decoding="async" style="width:100%;height:auto;border-radius:8px;" /></p>
<p>خلال الزيارة نوضح ما هو ضروري الآن وما يمكن تأجيله. الهدف إغلاق السبب بأقل تدخل مناسب لمنزلك في {city}، لا تكبير النطاق بلا داع.</p>
"""
    sec_mistakes = f"""
<h2>أخطاء تؤخر الحل في {city}</h2>
<ul>
{mistakes}
<li>طلب باقة عامة بينما تكفي نقطة محددة.</li>
<li>إخفاء العَرَض بدهان أو تنظيف سطحي دون معالجة المصدر.</li>
<li>مقارنة سعر فقط دون سؤال عن أسلوب التشخيص.</li>
</ul>
"""
    sec_cost = f"""
<h2>الوقت والتكلفة بدون غموض</h2>
<p>تكلفة {html_lib.escape(svc)} في {city} تختلف حسب المساحة ودرجة الحالة وسهولة الوصول. لذلك نفضّل تقدير النطاق بعد فهم العَرَض بدل رقم عشوائي لا يمثل عقارك.</p>
<p>للحصول على تقدير أوضح: صف العَرَض، اذكر الحي، وحدد إن كانت المشكلة جديدة أم متكررة. هذه الثلاثة تختصر الجدل حول الوقت والسعر.</p>
<p>الحالات المتوسعة يُفضّل ذكرها صراحة عند الاتصال لتقديم أولوية ضمن الجدول.</p>
"""
    sec_prevent = f"""
<h2>بعد انتهاء العمل: وقاية تناسب {city}</h2>
<ul>
<li>راقب العَرَض 48–72 ساعة.</li>
<li>لا تغطِّ الأثر قبل استقرار الحالة.</li>
<li>اجعل للمتابعة الموسمية موعداً مرتبطاً بطبيعة {meta.get('climate', 'المنطقة')}.</li>
<li>إذا عاد العَرَض بسرعة، تواصل مبكراً على {PHONE}.</li>
</ul>
<p>{meta.get('note', 'الوقاية المبكرة أوفر من الترميم المتأخر.')}</p>
"""
    sec_quality = f"""
<h2>معايير جودة بسيطة لتقييم الزيارة</h2>
<p>بعد خدمة {html_lib.escape(svc)} في {city} اسأل: هل اتضح السبب؟ هل تقلص العَرَض؟ هل عرفت الخطوة التالية؟ هل كان النطاق مفهوماً قبل التنفيذ؟ هذه الأسئلة أفضل من الانطباع السريع.</p>
<p>ركن التطور يبني الزيارة على هذه المعايير لأنها ترتبط بنتيجة عملية يمكن ملاحظتها داخل المنزل.</p>
"""
    sec_why_us = f"""
<h2>لماذا يختار عملاء {city} ركن التطور؟</h2>
<ul>
<li>هوية سعودية محلية ورقم موحّد {PHONE} للاتصال والواتساب.</li>
<li>تشخيص قبل التنفيذ لتقليل الأعمال العشوائية.</li>
<li>إمكانية الربط مع خدمات مساندة عند الحاجة فقط.</li>
<li>تغطية عملية لأحياء {city}: {dcsv}.</li>
</ul>
{hub_html}
"""
    sec_faq = f"<h2>أسئلة شائعة — {html_lib.escape(svc)} في {city}</h2>\n{faqs}"

    if order == 0:
        middle = sec_why + sec_cover + sec_signs + sec_steps + sec_expand + sec_mistakes + sec_cost + sec_prevent + sec_quality
    elif order == 1:
        middle = sec_cover + sec_signs + sec_why + sec_steps + sec_expand + sec_cost + sec_quality + sec_mistakes + sec_prevent
    else:
        middle = sec_signs + sec_why + sec_steps + sec_cover + sec_expand + sec_prevent + sec_quality + sec_mistakes + sec_cost

    content = f"""
<p style="font-size:1.22em;font-weight:700;color:#005CB9;line-height:1.55;">{html_lib.escape(title)}</p>
<p>{intro}</p>
<p>شركة <strong>ركن التطور</strong> تنفّذ {html_lib.escape(pack['label'])} داخل السعودية بأسلوب ميداني: وضوح النطاق، تقليل الضرر على التشطيب، وشرح الخيارات قبل التوسع. الصفحة هذه مخصّصة لـ{city} وليست نسخة عمياء من مدينة أخرى.</p>
[post_call]
<p style="margin:28px 0;"><img src="{img}" alt="{html_lib.escape(title)}" loading="lazy" decoding="async" style="width:100%;height:auto;border-radius:8px;" /></p>
{middle}
{sec_why_us}
{sec_faq}
[post_call]
<p>ركن التطور — {html_lib.escape(title)} | {meta.get('region', city)} | {PHONE}</p>
""".strip()

    excerpt = (
        f"{title} من ركن التطور في {city}: خطة محلية، نطاق واضح قبل التنفيذ، "
        f"وتغطية {dcsv}. تواصل {PHONE}."
    )
    return content, excerpt



EN_PAGES = {
    14833: "leak",
    14834: "insul",
    14835: "clean",
}



def build_en(kind: str) -> tuple[str, str]:
    if kind == "leak":
        content = f"""
<p><strong>Rukn Eltatawer</strong> provides professional <strong>water leak detection in Riyadh</strong> for villas, apartments, and light commercial properties across Saudi Arabia. We locate hidden leaks with modern tools, minimize unnecessary demolition, and explain repair options before extra work begins.</p>
<p>Many Riyadh homeowners discover leaks late: a rising bill, damp paint, mold smell, or a meter that still moves after every tap is closed. Our process starts with confirmation, not guesswork.</p>
[post_call]
<p style="margin:28px 0;"><img src="{IMG['leak']}" alt="Water leak detection in Riyadh" loading="lazy" style="width:100%;height:auto;border-radius:8px;" /></p>
<h2>Signs you need leak detection in Riyadh</h2>
<ul>
<li>Meter movement with all taps closed</li>
<li>Unexpected water-bill increase</li>
<li>Damp walls, peeling paint, or recurring mold smell</li>
<li>Low pressure in one wing or floor</li>
<li>Wet garden zones without recent irrigation explanation</li>
<li>The same corner fails after every paint touch-up</li>
</ul>
<h2>How we work</h2>
<ol>
<li>Call or WhatsApp {PHONE} with your district and symptoms</li>
<li>Inspect meter, tanks, and visible supply lines</li>
<li>Use acoustic, moisture, thermal, or camera tools as needed</li>
<li>Provide a clear report before opening finishes</li>
<li>Repair narrowly when requested and retest</li>
</ol>
<p style="margin:28px 0;"><img src="{IMG['leak2']}" alt="Leak detection equipment in Riyadh" loading="lazy" style="width:100%;height:auto;border-radius:8px;" /></p>
<h2>Areas we cover</h2>
<p>Al Naseem, Al Malaz, Olaya, Al Yasmin, Tuwaiq, Hittin, and nearby Riyadh districts based on daily scheduling. Mention your district when booking.</p>
<h2>Mistakes that delay the fix</h2>
<ul>
<li>Repainting over active moisture</li>
<li>Breaking random tiles far from the real path</li>
<li>Ignoring villa irrigation lines</li>
<li>Waiting until ceiling damage expands</li>
</ul>
<h2>Cost and scope</h2>
<p>There is no single price for every property. Scope depends on size, number of suspect points, and whether repair is requested after detection. We explain the path before additional work.</p>
<h2>Why Rukn Eltatawer</h2>
<ul>
<li>Saudi local identity based in Riyadh</li>
<li>Diagnosis first to reduce demolition</li>
<li>One number for calls and WhatsApp: {PHONE}</li>
<li>Related waterproofing and drainage support when truly needed</li>
</ul>
<p>Arabic version: <a href="https://www.rukn-eltatawer.com/sa/water-leak-detection-riyadh/">كشف تسربات المياه في الرياض</a></p>
<h2>FAQ</h2>
<h3>Do you demolish first?</h3><p>No. We identify the source first.</p>
<h3>Available outside Riyadh?</h3><p>Yes, according to daily coverage.</p>
<h3>Can you repair after detection?</h3><p>Yes, after clarifying scope and cost.</p>
<h3>How long is an inspection?</h3><p>Usually 1–3 hours depending on property complexity.</p>
<h2>Prevention tips for Riyadh homes</h2>
<ul>
<li>Test the meter monthly for two minutes with all taps closed.</li>
<li>Check garden valves each season on villa properties.</li>
<li>Photograph new damp spots with the date they appeared.</li>
<li>Do not repaint over active moisture before the source is confirmed.</li>
</ul>
<p>These habits do not replace professional detection, but they help you book earlier and give the technician better context.</p>
[post_call]
<p>Rukn Eltatawer — Water Leak Detection in Riyadh | {PHONE}</p>
""".strip()
        return content, f"Professional water leak detection in Riyadh without unnecessary demolition. Call {PHONE}."
    if kind == "insul":
        content = f"""
<p><strong>Roof waterproofing in Riyadh</strong> from <strong>Rukn Eltatawer</strong> protects homes from UV aging, heat stress, and seasonal moisture. We inspect slopes, drains, joints, and tank surroundings, then recommend a practical system for the property.</p>
[post_call]
<p style="margin:28px 0;"><img src="{IMG['insul']}" alt="Roof waterproofing in Riyadh" loading="lazy" style="width:100%;height:auto;border-radius:8px;" /></p>
<h2>Signs you need waterproofing</h2>
<ul>
<li>Ceiling dampness after rain or roof washing</li>
<li>Hot upper-floor rooms</li>
<li>Cracked or aging coatings</li>
<li>Overflow marks around roof tanks</li>
<li>Standing water in roof corners</li>
</ul>
<h2>Our process</h2>
<ol>
<li>Inspection of slopes, drains, joints, and tanks</li>
<li>Surface preparation and weak-point treatment</li>
<li>Application of a suitable waterproofing system</li>
<li>Final checks and maintenance tips for Riyadh weather</li>
</ol>
<h2>Why timing matters</h2>
<p>Delaying a small crack often becomes a larger ceiling repair. Early waterproofing is usually cheaper than late renovation, especially on large villa roofs.</p>
<h2>Related checks</h2>
<p>If moisture continues, we may recommend leak detection to confirm whether the source is roofing, tanks, or an internal line.</p>
<p>Arabic version: <a href="https://www.rukn-eltatawer.com/sa/roof-insulation-riyadh/">عزل الأسطح في الرياض</a></p>
<h2>FAQ</h2>
<h3>Roofs only?</h3><p>Tanks too when needed.</p>
<h3>How do I book?</h3><p>Call {PHONE} with district and roof type.</p>
<h3>Can you inspect before quoting?</h3><p>Yes. Scope after inspection is more reliable.</p>
<h2>Maintenance habits</h2>
<p>Keep roof drains clear, avoid trapping water around tanks, and inspect coatings after major sandstorms. In Riyadh heat, small cracks expand faster than many homeowners expect.</p>
[post_call]
<p>Rukn Eltatawer — Roof Waterproofing in Riyadh | {PHONE}</p>
""".strip()
        return content, f"Roof waterproofing in Riyadh for heat and rain protection. Call {PHONE}."
    content = f"""
<p><strong>Home cleaning in Riyadh</strong> by <strong>Rukn Eltatawer</strong> focuses on practical results: dust control, kitchens, bathrooms, and high-touch disinfection when requested. Tell us your property type and priority rooms for a clear scope before the visit.</p>
[post_call]
<p style="margin:28px 0;"><img src="{IMG['clean']}" alt="Home cleaning in Riyadh" loading="lazy" style="width:100%;height:auto;border-radius:8px;" /></p>
<h2>What we clean</h2>
<ul>
<li>Apartments, villas, and deep seasonal cleaning</li>
<li>Kitchens, bathrooms, floors, and high-touch points</li>
<li>Optional sofa or carpet add-ons</li>
<li>Move-in / move-out readiness cleaning</li>
</ul>
<h2>How booking works</h2>
<ol>
<li>Contact {PHONE} with district and property size</li>
<li>Confirm scope and preferred timing</li>
<li>Clean and review agreed points before handover</li>
</ol>
<h2>Riyadh cleaning challenges</h2>
<p>Dust returns quickly with long AC hours. That is why we separate quick tidying from deeper cleaning of high-use rooms and fabrics when requested.</p>
<h2>Districts</h2>
<p>Al Naseem, Al Malaz, Olaya, Al Yasmin, Al Narjis and nearby areas by schedule.</p>
<p>Arabic related page: <a href="https://www.rukn-eltatawer.com/sa/apartment-cleaning-in-riyadh/">تنظيف شقق بالرياض</a></p>
<h2>FAQ</h2>
<h3>Are materials included?</h3><p>Yes for standard jobs, with care for sensitive surfaces.</p>
<h3>Specific rooms only?</h3><p>Yes.</p>
<h3>Deep vs regular cleaning?</h3><p>Deep cleaning takes longer and targets accumulated detail areas.</p>
<h2>Apartment vs villa notes</h2>
<p>Apartments need faster quieter work with clear room priorities. Villas need floor-by-floor planning. Tell us which rooms matter most so the visit matches your day in Riyadh.</p>
[post_call]
<p>Rukn Eltatawer — Home Cleaning in Riyadh | {PHONE}</p>
""".strip()
    return content, f"Practical home cleaning in Riyadh with clear scope. Call {PHONE}."



def update_post(pid: int, payload: dict) -> dict:
    r = requests.post(f"{BASE}/wp-json/wp/v2/posts/{pid}", auth=AUTH, headers=H, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()


def fetch_status(status: str, max_pages: int = 30) -> list[dict]:
    items = []
    page = 1
    while page <= max_pages:
        r = requests.get(
            f"{BASE}/wp-json/wp/v2/posts",
            auth=AUTH,
            headers=H,
            params={
                "per_page": 100,
                "page": page,
                "status": status,
                "context": "edit",
                "orderby": "date",
                "order": "asc" if status == "future" else "desc",
                "_fields": "id,title,content,status,date,featured_media,link",
            },
            timeout=120,
        )
        if r.status_code != 200:
            break
        batch = r.json()
        if not batch:
            break
        items.extend(batch)
        page += 1
    return items


def needs_rewrite(raw: str, words: int) -> bool:
    # Already uniquified by this engine
    if "الصفحة هذه مخصّصة لـ" in (raw or "") and words >= 980:
        return False
    if words < 1000:
        return True
    markers = [
        "دليل شامل 2026",
        "فريق المحتوى الفني في ركن التطور",
        "تختلف تفاصيل التنفيذ باختلاف حجم العمل المطلوب وطبيعة الموقع",
        "ملاحظة تدهور تدريجي في الحالة مقارنة بالفترة السابقة",
        "دليل عملي من ركن التطور",
        "أخطاء شائعة تؤخر الحل",
        "Absence of tools",  # noop
        "يمكن التعرف على الحاجة الفعلية لهذه الخدمة من خلال ملاحظة عدد من المؤشرات الواضحة",
    ]
    hits = sum(1 for m in markers if m in (raw or ""))
    return hits >= 2


def process_posts(posts: list[dict], report: dict, label: str):
    for i, p in enumerate(posts, 1):
        pid = p["id"]
        title = p["title"]["raw"]
        raw = (p.get("content") or {}).get("raw") or ""
        old = wc(raw)
        try:
            if pid in EN_PAGES:
                content, excerpt = build_en(EN_PAGES[pid])
            else:
                if not needs_rewrite(raw, old) and "{PHONE" not in raw:
                    report["skipped"].append({"id": pid, "words": old, "title": title, "bucket": label})
                    continue
                content, excerpt = build_unique(title)
            # keep existing featured if present
            payload = {"content": content, "excerpt": excerpt}
            update_post(pid, payload)
            new = wc(content)
            report["updated"].append(
                {"id": pid, "title": title, "old": old, "new": new, "status": p.get("status"), "bucket": label}
            )
            if i <= 20 or i % 25 == 0:
                print(f"{label} {i}/{len(posts)} #{pid} {old}->{new} {title[:48]}", flush=True)
            time.sleep(0.05)
        except Exception as e:
            report["errors"].append({"id": pid, "error": str(e)[:200], "title": title})
            print("ERR", pid, e, flush=True)
            time.sleep(0.2)


def stretch_far_future(min_hours: int = 48, interval_minutes: int = 45) -> dict:
    """Slow remaining far-future duplicates to reduce crawl damage while uniqueness catches up."""
    riyadh = timezone(timedelta(hours=3))
    now = datetime.now(riyadh)
    gate = now + timedelta(hours=min_hours)
    futures = fetch_status("future", max_pages=30)
    far = []
    for p in futures:
        dt = datetime.fromisoformat(p["date"]).replace(tzinfo=riyadh)
        if dt > gate:
            far.append(p)
    far.sort(key=lambda p: p["date"])
    cursor = gate + timedelta(minutes=interval_minutes)
    changed = 0
    for p in far:
        # only stretch if still template-like
        raw = (p.get("content") or {}).get("raw") or ""
        if not needs_rewrite(raw, wc(raw)):
            continue
        payload = {"date": cursor.strftime("%Y-%m-%dT%H:%M:%S"), "status": "future"}
        update_post(p["id"], payload)
        changed += 1
        cursor += timedelta(minutes=interval_minutes)
        if changed <= 5 or changed % 100 == 0:
            print(f"stretch #{p['id']} -> {payload['date']}", flush=True)
        time.sleep(0.04)
    return {"far_candidates": len(far), "stretched": changed}


def main():
    report = {"updated": [], "skipped": [], "errors": [], "stretch": {}}
    print("fetch publish...", flush=True)
    published = fetch_status("publish", max_pages=5)
    print("publish", len(published), flush=True)

    print("fetch future...", flush=True)
    futures = fetch_status("future", max_pages=30)
    print("future", len(futures), flush=True)

    riyadh = timezone(timedelta(hours=3))
    now = datetime.now(riyadh)
    soon_gate = now + timedelta(hours=48)
    soon, later = [], []
    for p in futures:
        dt = datetime.fromisoformat(p["date"]).replace(tzinfo=riyadh)
        (soon if dt <= soon_gate else later).append(p)
    print(f"soon48={len(soon)} later={len(later)}", flush=True)

    # 1) uniquify next 48h first (prevent damage)
    process_posts(soon, report, "soon48")
    # 2) published
    process_posts(published, report, "publish")
    # 3) stretch far future templates to slower cadence
    report["stretch"] = stretch_far_future(48, 45)
    # 4) uniquify a large later chunk now (up to 400) to keep pipeline healthy
    process_posts(later[:400], report, "later400")

    out = ROOT / "data/index-ready-dedupe-results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    slim = {
        "updated": len(report["updated"]),
        "skipped": len(report["skipped"]),
        "errors": len(report["errors"]),
        "stretch": report["stretch"],
        "avg_new": round(sum(x["new"] for x in report["updated"]) / max(1, len(report["updated"]))),
        "sample": report["updated"][:30],
        "error_sample": report["errors"][:20],
    }
    out.write_text(json.dumps(slim, ensure_ascii=False, indent=2), encoding="utf-8")
    # full dump separately
    (ROOT / "data/index-ready-dedupe-full.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(slim, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
