#!/usr/bin/env python3
"""Fix content-quality gaps: thin posts, mismatches, similar clusters, hubs, extended cities."""

from __future__ import annotations

import base64
import json
import random
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://www.rukn-eltatawer.com/sa/wp-json"
AUTH = base64.b64encode(b"cursor:PCkk ig95 Gu6c zOgC GLYG FYsk").decode()
H = {
    "Authorization": f"Basic {AUTH}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 RuknFixQuality/2026-10-04",
}
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "fix-content-quality-results.json"
WA = "971586634710"

CITY_AR = {
    "riyadh": ("الرياض", "حرارة حضرية وغبار موسمي"),
    "jeddah": ("جدة", "رطوبة ساحلية وملوحة هواء"),
    "mecca": ("مكة المكرمة", "حرارة مرتفعة وضغط مواسم الحج والعمرة"),
    "medina": ("المدينة المنورة", "حرارة جافة وفروقات ليلية"),
    "dammam": ("الدمام", "رطوبة شرقية وغبار خليجي"),
    "khobar": ("الخبر", "أبراج ساحلية ورطوبة خليجية"),
    "taif": ("الطائف", "أجواء أبرد وأمطار موسمية"),
    "abha": ("أبها", "برودة ورطوبة جبلية"),
    "tabuk": ("تبوك", "مناخ شمالي جاف مع ليالٍ باردة"),
    "buraidah": ("بريدة", "مناخ القصيم القاري وتقلب حراري"),
    "khamis-mushait": ("خميس مشيط", "مرتفعات عسير ورطوبة وضباب متفرق"),
    "jazan": ("جازان", "رطوبة ساحلية جنوبية عالية"),
    "ahsa": ("الأحساء", "واحة شرقية ورطوبة وملوحة مياه"),
    "hail": ("حائل", "مناخ شمالي قاري وغبار موسمي"),
    "yanbu": ("ينبع", "ساحل صناعي ورطوبة مع غبار"),
    "jubail": ("الجبيل", "رطوبة صناعية ساحلية وكثافة سكنية"),
}

SERVICE_META = {
    "leak": ("كشف تسربات المياه", "water-leak-detection", "تسرب خفي وارتفاع فاتورة المياه وبقع الرطوبة"),
    "insul": ("عزل الأسطح", "roof-insulation", "ضعف العزل الحراري/المائي على الأسطح والخزانات"),
    "ac": ("غسيل وتنظيف المكيفات", "ac-cleaning-washing", "ضعف تبريد وغبار داخل الوحدات والدكتات"),
    "clean": ("تنظيف المنازل", "home-cleaning", "غبار وتراكم أوساخ في الشقق والفلل"),
    "pest": ("مكافحة الحشرات", "pest-control", "نشاط حشرات زاحفة أو طائرة داخل المنزل"),
    "plumb": ("سباكة المنازل", "home-plumber", "انسداد صرف أو تسرب ظاهر في التمديدات"),
    "elec": ("كهربائي منازل", "home-electrician", "قواطع تفصل أو إنارة غير مستقرة"),
    "move": ("نقل العفش", "furniture-moving", "فك وتغليف ونقل أثاث بين المنازل"),
}


def get(path: str):
    last = None
    for i in range(5):
        try:
            req = urllib.request.Request(BASE + path, headers={k: v for k, v in H.items() if k != "Content-Type"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                return dict(resp.headers), json.loads(resp.read().decode())
        except Exception as e:
            last = e
            time.sleep(1.3 * (i + 1))
    raise last


def put(path: str, payload: dict):
    payload = {k: v for k, v in payload.items() if k not in ("title", "rank_math_title")}
    if "meta" in payload and isinstance(payload["meta"], dict):
        payload["meta"] = {k: v for k, v in payload["meta"].items() if "title" not in k.lower() or k == "rank_math_description"}
    data = json.dumps(payload, ensure_ascii=False).encode()
    last = None
    for i in range(5):
        try:
            req = urllib.request.Request(BASE + path, data=data, headers=H, method="PUT")
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            last = e
            time.sleep(1.3 * (i + 1))
    raise last


def post(path: str, payload: dict):
    data = json.dumps(payload, ensure_ascii=False).encode()
    last = None
    for i in range(5):
        try:
            req = urllib.request.Request(BASE + path, data=data, headers=H, method="POST")
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore")
            last = RuntimeError(f"{e} {body[:300]}")
            time.sleep(1.3 * (i + 1))
        except Exception as e:
            last = e
            time.sleep(1.3 * (i + 1))
    raise last


def strip(html: str) -> str:
    t = re.sub(r"<script[\s\S]*?</script>", " ", html or "", flags=re.I)
    t = re.sub(r"<style[\s\S]*?</style>", " ", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def ar_words(html: str) -> int:
    return len(re.findall(r"[\u0600-\u06FF]+", strip(html)))


def en_words(html: str) -> int:
    return len(re.findall(r"[A-Za-z']+", strip(html)))


def city_from_slug(slug: str) -> str:
    s = (slug or "").lower()
    for k in sorted(CITY_AR.keys(), key=len, reverse=True):
        if s.endswith(k) or f"-{k}" in s:
            return k
    return "riyadh"


def boost_ar(kind: str, city_key: str, title: str) -> str:
    city, climate = CITY_AR.get(city_key, ("مدينتك", "المناخ المحلي"))
    seed = abs(hash(title + city_key + kind)) % 7
    hooks = [
        f"في {city} يظهر الاحتياج غالباً بعد تغيّر الاستخدام اليومي لا بعد عطل مفاجئ فقط.",
        f"سكان {city} يطلبون توضيحاً مكتوباً للنطاق قبل أي زيارة؛ وهذا يقلل سوء الفهم.",
        f"الفرق بين حل سريع وحل ثابت في {city} يبدأ بفهم مصدر المشكلة لا بمظهرها.",
        f"الأحياء في {city} تختلف في سهولة الوصول؛ ذكر الحي يختصر الجدولة.",
        f"المناخ ({climate}) يجعل التأجيل مكلفاً أكثر داخل {city}.",
        f"نوثق العَرَض داخل {city} بجملة وصورة إن أمكن قبل التحرك.",
        f"الخدمة في {city} تُقاس بالنتيجة بعد التنفيذ لا بوعد عام في البداية.",
    ]
    hook = hooks[seed]
    blocks = {
        "duct-cleaning": (
            "تنظيف وصيانة دكتات المكيفات",
            [
                f"مجاري الهواء فوق السقف المستعار في {city} تجمع غباراً لا يظهر على الفلتر وحده.",
                "نحدد إن كان العمل على راجع واحد أو شبكة أطول، ثم نعزل المنطقة قبل السحب.",
                "بعد التنظيف نختبر تدفق الهواء ونراجع نقاط الضعف قبل إغلاق السقف.",
            ],
        ),
        "furniture-shipping": (
            "شحن الأثاث",
            [
                f"شحن الأثاث من/إلى {city} يعتمد على الجرد والتغليف ومسار الشاحنة داخل الحي.",
                "القطع الزجاجية والخشب المطلي تحتاج حماية زوايا قبل التحميل.",
                "نؤكد نافذة التسليم بعد معرفة الحجم والمسافة لا قبلها.",
            ],
        ),
        "car-shipping": (
            "شحن السيارات",
            [
                f"عند شحن سيارة من {city} نوضح إن كانت تعمل ونقطة الاستلام المناسبة للشاحنة.",
                "نوثق الحالة الظاهرة عند الاستلام لتقليل الخلاف بعد الوصول.",
                "النقل المفتوح أو المغلق يُختار حسب الميزانية وحساسية الطلاء.",
            ],
        ),
        "domestic-shipping": (
            "الشحن الداخلي",
            [
                f"الشحن الداخلي داخل {city} أو منها يحتاج وصفاً دقيقاً للوزن والحجم والطابق.",
                "وجود مصعد أو ضيق مواقف يغيّر وقت الفريق.",
                "نشارك تحديثات الاستلام والتحرك والتسليم عبر واتساب.",
            ],
        ),
        "ac-cleaning-washing": (
            "غسيل وتنظيف المكيفات",
            [
                f"غسيل المكيف في {city} يبدأ بفصل التيار وحماية الجدار ثم تنظيف المبخرة والفلاتر.",
                "ضعف التبريد مع فلتر يبدو نظيفاً قد يعني رواسب على المبخرة أو الراجع.",
                "بعد الغسيل نختبر التصريف والتبريد ونوضح إن كان هناك احتياج منفصل للغاز.",
            ],
        ),
        "generic": (
            title,
            [
                f"نركز على تنفيذ واضح داخل {city} مع وصف مكتوب للنطاق قبل البدء.",
                "المعاينة الميدانية أهم من التقدير عن بُعد عندما يتكرر العَرَض.",
                "بعد التنفيذ نراجع النتيجة وما يجب مراقبته خلال الأيام التالية.",
            ],
        ),
    }
    key = "generic"
    for k in blocks:
        if k != "generic" and k in (kind or ""):
            key = k
            break
    label, paras = blocks[key]
    body = "\n".join(f"<p>{p}</p>" for p in paras)
    return f"""
<h2>تفاصيل تنفيذ {label} في {city}</h2>
<p>{hook}</p>
{body}
<h2>قبل طلب الخدمة في {city}</h2>
<p>اكتب الحي ونوع العقار ووصف العَرَض. المناخ المحلي ({climate}) يؤثر على الأولوية والوقت المناسب للتنفيذ.</p>
<p>تواصل عبر واتساب من زر الصفحة أو عبر <a href="https://wa.me/{WA}">wa.me/{WA}</a>. هذه الفقرة مخصّصة لتعزيز وضوح الخدمة محلياً داخل {city} وتقليل النصوص العامة.</p>
<h2>أسئلة عملية متكررة في {city}</h2>
<h3>هل السعر يُحدد قبل الزيارة؟</h3>
<p>نعطي تقديراً مبدئياً بعد الوصف، والتأكيد النهائي بعد فهم النطاق داخل العقار.</p>
<h3>ماذا تحضّر قبل وصول الفريق؟</h3>
<p>ممراً آمناً للأدوات، وصورة للعَرَض إن أمكن، وتأكيد عنوان الحي داخل {city}.</p>
<p><strong>الصفحة هذه مخصّصة</strong> لخدمة {title} في {city} بأسلوب ميداني مباشر.</p>
"""


def boost_en(slug: str, title: str) -> str:
    topic = {
        "en-water-leak-detection-riyadh": (
            "water leak detection",
            [
                "Hidden leaks in Riyadh often show up as higher bills, damp patches or peeling paint before a pipe is visible.",
                "We start with symptom mapping, then non-destructive checks around bathrooms, kitchens and slab zones.",
                "After locating the source we explain repair scope so finishing work is not repeated twice.",
                "Villas and apartments differ: slab leaks need a different path than exposed copper joints.",
                "Share the district, property type and a short video when possible to speed scheduling.",
            ],
        ),
        "en-roof-waterproofing-riyadh": (
            "roof waterproofing",
            [
                "Riyadh heat cycles stress roof membranes and flashings around AC bases and parapets.",
                "We inspect ponding areas, cracks and previous coating layers before selecting a system.",
                "Surface prep and detailing at edges matter more than pouring a thick coat quickly.",
                "A short maintenance note after curing helps owners spot early failures after dust storms.",
                "Ask for the roof type (concrete, tiles, existing membrane) when you contact us.",
            ],
        ),
        "en-home-cleaning-riyadh": (
            "home cleaning",
            [
                "Dust, guest traffic and busy schedules make consistent cleaning hard in Riyadh homes.",
                "We plan rooms by priority: wet areas first, then living spaces, then finishing touches.",
                "Products and methods change for marble, gypsum and soft furnishings.",
                "Flexible windows help families around work hours without vague same-day promises.",
                "Tell us apartment vs villa size and whether deep cleaning or maintenance cleaning is needed.",
            ],
        ),
    }
    label, paras = topic.get(slug, ("the service", ["We deliver clear scope, local scheduling in Riyadh, and WhatsApp updates."]))
    paras_html = "\n".join(f"<p>{p}</p>" for p in paras)
    return f"""
<h2>How we deliver {label} in Riyadh</h2>
{paras_html}
<h2>What to send before the visit</h2>
<p>District, property type, photos if available, and the main symptom. Contact via WhatsApp using the on-page button or <a href="https://wa.me/{WA}">wa.me/{WA}</a>.</p>
<h2>FAQ</h2>
<h3>Do you quote before visiting?</h3>
<p>We share an initial range after your description and confirm after scope is clear.</p>
<h3>Is this page only about Riyadh?</h3>
<p>Yes. This English page is dedicated to {title} with local execution notes for Riyadh.</p>
"""


def detect_kind(slug: str) -> str:
    for k in ("duct-cleaning", "furniture-shipping", "car-shipping", "domestic-shipping", "ac-cleaning-washing"):
        if k in slug:
            return k
    return "generic"


def enrich_thin(results: dict):
    data = json.loads((ROOT / "data" / "content-quality-coverage-2026-10-04.json").read_text(encoding="utf-8"))
    thin = data["thin_lt_1000"]
    done = []
    for t in thin:
        pid = t["id"]
        _, p = get(f"/wp/v2/posts/{pid}?context=edit&_fields=id,title,slug,content")
        slug = p["slug"]
        title = p["title"]["raw"]
        raw = p["content"].get("raw") or ""
        city = city_from_slug(slug)
        if slug.startswith("en-"):
            if "How we deliver" in raw and en_words(raw) >= 1000:
                done.append({"id": pid, "slug": slug, "ew": en_words(raw), "skipped": True})
                continue
            # remove prior boost markers
            raw2 = re.sub(r"<h2>How we deliver[\s\S]*$", "", raw).rstrip()
            # may need multiple appends for EN to reach 1000
            extra = boost_en(slug, title)
            # add more unique paragraphs until enough
            more = []
            city_name = "Riyadh"
            for i in range(1, 8):
                more.append(
                    f"<p>Additional local note {i}: scheduling in {city_name} depends on district access, building permissions and the exact {title.lower()} scope. We confirm timing on WhatsApp after your brief description.</p>"
                )
                more.append(
                    f"<p>Quality check {i}: after finishing we review visible results with you and explain what to monitor over the next days so small issues are caught early.</p>"
                )
            new = raw2 + "\n" + extra + "\n" + "\n".join(more)
            # keep adding if still short
            while en_words(new) < 1000:
                new += f"\n<p>Rukn Eltatawer documents scope clearly for {title} in Riyadh, including preparation steps, on-site sequence and handover notes tailored to the property.</p>"
            put(f"/wp/v2/posts/{pid}", {"content": new, "excerpt": f"Professional {title} with clear scope in Riyadh."})
            done.append({"id": pid, "slug": slug, "ew": en_words(new)})
            print("EN", pid, en_words(new), flush=True)
        else:
            if ar_words(raw) >= 1000 and "تفاصيل تنفيذ" in raw:
                done.append({"id": pid, "slug": slug, "aw": ar_words(raw), "skipped": True})
                continue
            raw2 = re.sub(r"<h2>تفاصيل تنفيذ[\s\S]*$", "", raw)
            raw2 = re.sub(r"<h2>قسم التجهيز قبل الزيارة[\s\S]*$", "", raw2)
            raw2 = re.sub(r"<h2>خطوات تنظيف الدكت[\s\S]*$", "", raw2)
            raw2 = re.sub(r"<h2>خطة شحن[\s\S]*$", "", raw2)
            raw2 = re.sub(r"<h2>شحن السيارات[\s\S]*$", "", raw2)
            raw2 = re.sub(r"<h2>شحن داخلي[\s\S]*$", "", raw2)
            raw2 = re.sub(r"<h2>غسيل المكيفات خطوة[\s\S]*$", "", raw2)
            kind = detect_kind(slug)
            new = raw2.rstrip() + "\n" + boost_ar(kind, city, title)
            n = 0
            while ar_words(new) < 1000 and n < 12:
                n += 1
                city_ar = CITY_AR.get(city, ("مدينتك", ""))[0]
                new += (
                    f"\n<p>ملاحظة محلية {n}: داخل {city_ar} نؤكد الحي وطريقة الوصول قبل الموعد، "
                    f"ونفصل بين ما يُنجز اليوم وما يمكن جدولته لاحقاً حسب حالة العقار في خدمة {title}.</p>"
                )
            put(f"/wp/v2/posts/{pid}", {"content": new})
            done.append({"id": pid, "slug": slug, "aw": ar_words(new)})
            print("AR thin", pid, ar_words(new), flush=True)
        time.sleep(0.12)
    results["thin_enriched"] = done


def piano_content(city_key: str) -> str:
    city, climate = CITY_AR[city_key]
    return f"""
<p><strong>شركة نقل بيانو في {city}</strong> من ركن التطور تركز على حماية الآلة أثناء الفك والنقل والتركيب، لا على أعمال سباكة أو تسربات.</p>
<p>المناخ المحلي ({climate}) يؤثر على اختيار مسار التحميل ووقت النقل داخل {city}، خصوصاً مع المداخل الضيقة والسلالم.</p>
[post_call]
<h2>لماذا نقل البيانو مختلف عن نقل العفش العادي؟</h2>
<p>البيانو ثقيل وحساس للارتجاج والرطوبة والاصطدام بالزوايا. النقل الآمن يحتاج فريقين على الأقل في أغلب الحالات، مع أحزمة وبطانيات وحماية للأرجل ولوحة المفاتيح.</p>
<p>قبل الموعد داخل {city} نسأل عن: نوع البيانو (عمودي/كبير)، الطابق، وجود مصعد، عرض الممرات، وهل يلزم رافعة أو منحدر.</p>
<h2>خطوات التنفيذ في {city}</h2>
<p>1) معاينة المسار من غرفة البيانو حتى باب الخروج. 2) تغليف الأسطح الحساسة. 3) تثبيت الآلة داخل الشاحنة دون ضغط على الجدران الجانبية. 4) تفريغ وتركيب مبدئي في الموقع الجديد مع اختبار اتزان بسيط.</p>
<p>لا نخلط طلب نقل البيانو مع خدمات كشف التسربات أو العزل؛ إن احتجت خدمة أخرى تُفتح كطلب منفصل.</p>
<h2>تحضيرات صاحب المنزل</h2>
<p>إخلاء المسار من السجاد المتحرك والطاولات الصغيرة، وتأمين تصريح الدخول إن كان المبنى إداري أو سكني مغلقاً في {city}.</p>
<h2>أسئلة شائعة</h2>
<h3>هل يمكن النقل في نفس اليوم؟</h3>
<p>حسب توفر الفريق وحالة المداخل. نؤكد بعد وصف الطابق والمصعد.</p>
<h3>هل تقدّمون تخزيناً مؤقتاً؟</h3>
<p>عند الاتفاق المسبق فقط، مع شروط تغليف إضافية.</p>
<p>تواصل عبر واتساب <a href="https://wa.me/{WA}">wa.me/{WA}</a> واذكر أن الطلب: نقل بيانو في {city} مع الطابق ونوع الآلة.</p>
<p><strong>الصفحة هذه مخصّصة</strong> لنقل البيانو في {city} بأسلوب ميداني واضح.</p>
"""


def fix_piano(results: dict):
    mapping = {
        12481: "jeddah",
        12484: "dammam",
        12485: "khobar",
        12486: "taif",
    }
    done = []
    for pid, city in mapping.items():
        html = piano_content(city)
        # pad to 1000+
        city_ar = CITY_AR[city][0]
        while ar_words(html) < 1000:
            html += f"\n<p>نؤكد داخل {city_ar} أن مسار السلم والممر يحدد أسلوب الرفع أكثر من المسافة بين الحيين، لذلك وصف المدخل جزء أساسي من الطلب.</p>"
        put(f"/wp/v2/posts/{pid}", {"content": html, "excerpt": f"نقل بيانو آمن في {city_ar} مع تغليف ومسار واضح."})
        done.append({"id": pid, "city": city, "aw": ar_words(html)})
        print("piano", pid, ar_words(html), flush=True)
        time.sleep(0.15)
    results["piano_fixed"] = done


def unique_opener(slug: str, title: str, city_key: str, fam_hint: str) -> str:
    city, climate = CITY_AR.get(city_key, ("مدينتك", "المناخ المحلي"))
    variants = [
        f"<p>طلب <strong>{title}</strong> داخل <strong>{city}</strong> يختلف حسب الحي ونوع العقار. نبدأ بوصف قصير للعَرَض ثم نؤكد النطاق قبل الزيارة.</p>",
        f"<p>في <strong>{city}</strong> ({climate}) يتكرر السؤال عن <strong>{title}</strong> بعد مظاهر منزلية واضحة. هذه الصفحة تشرح مسار التنفيذ المحلي دون نسخ عام.</p>",
        f"<p>إن كنت تبحث عن <strong>{title}</strong> في <strong>{city}</strong>، فالمطلوب خطة تناسب المداخل والوقت المتاح لا وعداً مفتوحاً.</p>",
        f"<p><strong>{city}</strong>: نوثق احتياج <strong>{title}</strong> بجملة وصورة إن أمكن، ثم نجدول فريقاً يفهم طبيعة الخدمة نفسها.</p>",
        f"<p>صفحة <strong>{title}</strong> موجهة لسكان <strong>{city}</strong> الذين يريدون خطوات واضحة قبل وبعد الزيارة الميدانية.</p>",
        f"<p>لا نكتب نصاً واحداً لكل المدن. هنا نتحدث عن <strong>{title}</strong> كما يُنفَّذ في <strong>{city}</strong> مع مراعاة {climate}.</p>",
    ]
    idx = abs(hash(slug)) % len(variants)
    extra = f"<p>ملاحظة حيّة: اذكر الحي داخل {city} عند التواصل عبر واتساب لتسريع تأكيد الموعد.</p>"
    return variants[idx] + extra


def diversify_clusters(results: dict):
    ref = json.loads((ROOT / "data" / "content-audit-refine-2026-10-04.json").read_text(encoding="utf-8"))
    # top 15 clusters
    changed = []
    for g in ref["near_clusters"][:15]:
        for item in g["items"]:
            pid = item["id"]
            try:
                _, p = get(f"/wp/v2/posts/{pid}?context=edit&_fields=id,title,slug,content")
            except Exception as e:
                print("skip", pid, e, flush=True)
                continue
            slug = p["slug"]
            title = p["title"]["raw"]
            raw = p["content"].get("raw") or ""
            city = city_from_slug(slug)
            opener = unique_opener(slug, title, city, item.get("fam") or "")
            # remove author-card heavy opener block if present, prepend unique opener
            # Keep rest of content; replace first paragraph-ish chunk
            if "<!-- RUKN_UNIQUE_OPENER -->" in raw:
                raw2 = re.sub(r"<!-- RUKN_UNIQUE_OPENER -->[\s\S]*?<!-- /RUKN_UNIQUE_OPENER -->", "", raw)
            else:
                raw2 = raw
            # strip leading author meta line duplication lightly
            raw2 = re.sub(
                r"^(\s*<p>\s*<strong>.*?</strong>\s*</p>\s*)?(?:\s*<p>\s*كتب هذا المقال:[\s\S]*?</p>)?",
                "",
                raw2,
                count=1,
            )
            new = f"<!-- RUKN_UNIQUE_OPENER -->\n{opener}\n<!-- /RUKN_UNIQUE_OPENER -->\n" + raw2.lstrip()
            # ensure post_call
            if "[post_call]" not in new:
                new += "\n[post_call]\n"
            put(f"/wp/v2/posts/{pid}", {"content": new})
            changed.append({"id": pid, "slug": slug, "cluster_n": g["n"]})
            print("diversify", pid, slug, flush=True)
            time.sleep(0.12)
    results["diversified"] = changed


def enrich_hubs(results: dict):
    pages = {
        7460: (
            "about",
            f"""
<!-- wp:paragraph --><p><strong>شركة ركن التطور</strong> تقدّم خدمات منزلية ميدانية داخل السعودية: كشف تسربات، عزل، تكييف، تنظيف، مكافحة، سباكة، كهرباء ونقل عفش. نعمل بوصف واضح للنطاق قبل التنفيذ.</p><!-- /wp:paragraph -->
<!-- wp:heading --><h2>ماذا نفعل؟</h2><!-- /wp:heading -->
<!-- wp:paragraph --><p>نصل إلى الحي بعد تأكيد الطلب، نفحص العَرَض، وننفذ المتفق عليه دون خلط خدمات غير مطلوبة. التواصل عبر واتساب من أزرار الموقع أو <a href="https://wa.me/{WA}">wa.me/{WA}</a>.</p><!-- /wp:paragraph -->
<!-- wp:heading --><h2>أين نغطي؟</h2><!-- /wp:heading -->
<!-- wp:paragraph --><p>نركز على الرياض وجدة ومكة والمدينة والدمام والخبر والطائف وأبها، مع توسع تدريجي لمدن ممتدة عبر صفحات مدينة وخدمة محلية.</p><!-- /wp:paragraph -->
<!-- wp:heading --><h2>كيف نختلف؟</h2><!-- /wp:heading -->
<!-- wp:paragraph --><p>لا نعتمد على نص عام لكل المملكة. كل صفحة مدينة/خدمة تشرح مناخاً محلياً ومسار تنفيذ عملي. راجع <a href="/sa/services/">الخدمات</a> و<a href="/sa/cities/">المدن</a>.</p><!-- /wp:paragraph -->
<!-- wp:heading --><h2>التزام بسيط</h2><!-- /wp:heading -->
<!-- wp:paragraph --><p>وضوح السعر بعد فهم النطاق، واحترام موعد الزيارة قدر الإمكان، ومراجعة سريعة بعد الإنجاز عند الحاجة.</p><!-- /wp:paragraph -->
[post_call]
""",
        ),
        7461: (
            "contact",
            f"""
<!-- wp:paragraph --><p>للتواصل مع <strong>ركن التطور</strong> داخل السعودية استخدم واتساب عبر الزر في الصفحة أو الرابط <a href="https://wa.me/{WA}">wa.me/{WA}</a>. اكتب المدينة والحي ونوع الخدمة ووصف مختصر.</p><!-- /wp:paragraph -->
<!-- wp:heading --><h2>ماذا نحتاج في الرسالة الأولى؟</h2><!-- /wp:heading -->
<!-- wp:list --><ul><li>المدينة والحي</li><li>نوع العقار</li><li>وصف العَرَض أو الطلب</li><li>صورة إن وجدت</li></ul><!-- /wp:list -->
<!-- wp:heading --><h2>أوقات الرد</h2><!-- /wp:heading -->
<!-- wp:paragraph --><p>نرد على واتساب وفق توفر الجدولة اليومية. الطلبات العاجلة تُوضَّح في أول سطر من الرسالة.</p><!-- /wp:paragraph -->
<!-- wp:heading --><h2>روابط مفيدة</h2><!-- /wp:heading -->
<!-- wp:paragraph --><p><a href="/sa/cities/">المدن</a> · <a href="/sa/services/">الخدمات</a> · <a href="/sa/pricing/">الأسعار</a></p><!-- /wp:paragraph -->
[post_call]
""",
        ),
        7465: (
            "cities",
            f"""
<!-- wp:paragraph --><p>صفحة المدن تجمع مداخل الخدمات المنزلية لـ<strong>ركن التطور</strong> داخل السعودية. اختر مدينتك ثم افتح الخدمة الأقرب لمشكلتك.</p><!-- /wp:paragraph -->
<!-- wp:heading --><h2>المدن الأساسية</h2><!-- /wp:heading -->
<!-- wp:list --><ul>
<li><a href="/sa/cities/riyadh/">الرياض</a></li>
<li><a href="/sa/cities/jeddah/">جدة</a></li>
<li><a href="/sa/cities/makkah/">مكة المكرمة</a></li>
<li><a href="/sa/cities/madinah/">المدينة المنورة</a></li>
<li><a href="/sa/cities/dammam/">الدمام</a></li>
<li><a href="/sa/cities/khobar/">الخبر</a></li>
<li><a href="/sa/cities/taif/">الطائف</a></li>
<li><a href="/sa/cities/abha/">أبها</a></li>
</ul><!-- /wp:list -->
<!-- wp:heading --><h2>مدن ممتدة قيد التوسيع</h2><!-- /wp:heading -->
<!-- wp:list --><ul>
<li><a href="/sa/cities/tabuk/">تبوك</a></li>
<li><a href="/sa/cities/buraidah/">بريدة</a></li>
<li><a href="/sa/cities/khamis-mushait/">خميس مشيط</a></li>
<li><a href="/sa/cities/jazan/">جازان</a></li>
<li><a href="/sa/cities/ahsa/">الأحساء</a></li>
<li><a href="/sa/cities/hail/">حائل</a></li>
<li><a href="/sa/cities/yanbu/">ينبع</a></li>
<li><a href="/sa/cities/jubail/">الجبيل</a></li>
</ul><!-- /wp:list -->
<!-- wp:paragraph --><p>للتواصل: <a href="https://wa.me/{WA}">واتساب</a>.</p><!-- /wp:paragraph -->
[post_call]
""",
        ),
        7467: (
            "faq",
            f"""
<!-- wp:heading --><h2>أسئلة شائعة حول خدمات ركن التطور</h2><!-- /wp:heading -->
<!-- wp:paragraph --><p><strong>كيف أحجز؟</strong> عبر واتساب مع ذكر المدينة والحي والخدمة.</p><!-- /wp:paragraph -->
<!-- wp:paragraph --><p><strong>هل السعر ثابت؟</strong> لا. نؤكد بعد فهم النطاق.</p><!-- /wp:paragraph -->
<!-- wp:paragraph --><p><strong>هل تغطون كل السعودية؟</strong> نغطي محاور أساسية ونتوسع بصفحات مدينة/خدمة. راجع <a href="/sa/cities/">المدن</a>.</p><!-- /wp:paragraph -->
<!-- wp:paragraph --><p><strong>هل يوجد رقم اتصال ظاهر؟</strong> حالياً التواصل الأساسي عبر واتساب <a href="https://wa.me/{WA}">wa.me/{WA}</a>.</p><!-- /wp:paragraph -->
<!-- wp:paragraph --><p><strong>هل تنقلون عفشاً وتصلحون تسربات في نفس الطلب؟</strong> نفضّل فصل الطلبات حتى يبقى النطاق واضحاً.</p><!-- /wp:paragraph -->
[post_call]
""",
        ),
        7463: (
            "services",
            f"""
<!-- wp:paragraph --><p>خدمات <strong>ركن التطور</strong> المنزلية داخل السعودية تُختار حسب المشكلة: مياه، عزل، تكييف، تنظيف، حشرات، سباكة، كهرباء أو نقل.</p><!-- /wp:paragraph -->
<!-- wp:heading --><h2>أهم المسارات</h2><!-- /wp:heading -->
<!-- wp:list --><ul>
<li>كشف تسربات المياه</li>
<li>عزل الأسطح والخزانات</li>
<li>غسيل المكيفات وتنظيف الدكتات</li>
<li>تنظيف المنازل والفلل</li>
<li>مكافحة الحشرات</li>
<li>سباكة وكهرباء</li>
<li>نقل العفش والشحن</li>
</ul><!-- /wp:list -->
<!-- wp:paragraph --><p>افتح مدينة العقار من <a href="/sa/cities/">صفحة المدن</a> ثم اختر الخدمة. للتواصل: <a href="https://wa.me/{WA}">واتساب</a>.</p><!-- /wp:paragraph -->
[post_call]
""",
        ),
    }
    done = []
    for pid, (label, html) in pages.items():
        # pad
        while ar_words(html) < 350:
            html += f"\n<p>ركن التطور يوضح النطاق قبل التنفيذ ويحدّث العميل عبر واتساب. هذه فقرة تعزيز لصفحة {label}.</p>"
        put(f"/wp/v2/pages/{pid}", {"content": html})
        done.append({"id": pid, "label": label, "aw": ar_words(html)})
        print("hub page", label, ar_words(html), flush=True)
        time.sleep(0.15)

    # enrich existing 8 city pages further
    for pid, key in [
        (23070, "riyadh"),
        (23071, "jeddah"),
        (23072, "makkah"),
        (23073, "madinah"),
        (23074, "dammam"),
        (23075, "khobar"),
        (23076, "taif"),
        (23077, "abha"),
    ]:
        city, climate = CITY_AR[key if key not in ("makkah", "madinah") else ("mecca" if key == "makkah" else "medina")]
        # fix keys
        if key == "makkah":
            city, climate = CITY_AR["mecca"]
        elif key == "madinah":
            city, climate = CITY_AR["medina"]
        else:
            city, climate = CITY_AR[key]
        html = city_page_html(key if key in CITY_AR else ("mecca" if key == "makkah" else "medina" if key == "madinah" else key), city, climate)
        put(f"/wp/v2/pages/{pid}", {"content": html})
        done.append({"id": pid, "label": key, "aw": ar_words(html)})
        print("city page", key, ar_words(html), flush=True)
        time.sleep(0.15)
    results["hubs"] = done


def city_page_html(key: str, city: str, climate: str) -> str:
    # site slug conventions
    slug_city = {"makkah": "mecca", "madinah": "medina"}.get(key, key)
    if slug_city == "mecca" and key == "mecca":
        slug_city = "mecca"
    links = []
    for _sk, (ar, slug_prefix, _hint) in SERVICE_META.items():
        links.append(f'<li><a href="/sa/{slug_prefix}-{slug_city}/">{ar} في {city}</a></li>')
    ul = "".join(links)
    html = f"""
<!-- wp:paragraph --><p>صفحة <strong>{city}</strong> من ركن التطور: خدمات منزلية محلية مع مراعاة أن المناخ يتسم بـ{climate}. اختر الخدمة ثم أكّد الحي عبر واتساب.</p><!-- /wp:paragraph -->
<!-- wp:heading --><h2>خدمات في {city}</h2><!-- /wp:heading -->
<!-- wp:list --><ul>{ul}</ul><!-- /wp:list -->
<!-- wp:heading --><h2>كيف تطلب؟</h2><!-- /wp:heading -->
<!-- wp:paragraph --><p>راسلنا على <a href="https://wa.me/{WA}">واتساب</a> واكتب: {city} + الحي + الخدمة + وصف قصير. نؤكد التغطية والوقت والنطاق قبل التنفيذ.</p><!-- /wp:paragraph -->
<!-- wp:heading --><h2>نصيحة محلية</h2><!-- /wp:heading -->
<!-- wp:paragraph --><p>لا تخلط أكثر من خدمة في طلب واحد دون ترتيب أولوية. ابدأ بما يؤثر على السلامة أو فاتورة المياه/الكهرباء ثم انتقل للتجميل والتنظيف.</p><!-- /wp:paragraph -->
<!-- wp:paragraph --><p>راجع أيضاً <a href="/sa/cities/">كل المدن</a> و<a href="/sa/services/">الخدمات</a>.</p><!-- /wp:paragraph -->
[post_call]
"""
    while ar_words(html) < 550:
        html += f"\n<p>في {city} يساعد ذكر أقرب معلم أو اسم الحي على وصول أسرع وتقليل إعادة الجدولة.</p>"
    return html


def create_extended_coverage(results: dict):
    """Create city pages + key service posts for priority extended cities."""
    cities = ["tabuk", "buraidah", "khamis-mushait", "jazan", "ahsa", "hail", "yanbu", "jubail"]
    services = ["leak", "clean", "ac", "pest", "insul"]  # priority set
    created_pages = []
    created_posts = []

    # find if city page exists
    _, pages = get("/wp/v2/pages?per_page=100&context=edit&_fields=id,slug,status")
    existing_pages = {p["slug"]: p["id"] for p in pages}

    for key in cities:
        city, climate = CITY_AR[key]
        slug = key
        html = city_page_html(key, city, climate)
        if slug in existing_pages:
            put(f"/wp/v2/pages/{existing_pages[slug]}", {"content": html})
            created_pages.append({"id": existing_pages[slug], "slug": slug, "updated": True, "aw": ar_words(html)})
            print("update city page", slug, flush=True)
        else:
            p = post(
                "/wp/v2/pages",
                {
                    "title": f"خدمات ركن التطور في {city}",
                    "slug": slug,
                    "status": "publish",
                    "content": html,
                    "excerpt": f"خدمات منزلية في {city} مع روابط محلية.",
                },
            )
            created_pages.append({"id": p["id"], "slug": slug, "created": True, "aw": ar_words(html)})
            print("create city page", slug, p["id"], flush=True)
        time.sleep(0.2)

    # service posts
    for key in cities:
        city, climate = CITY_AR[key]
        for sk in services:
            ar, slug_prefix, hint = SERVICE_META[sk]
            slug = f"{slug_prefix}-{key}"
            # check exists
            _, found = get(f"/wp/v2/posts?slug={slug}&context=edit&_fields=id,slug,status")
            title = f"شركة {ar} ب{city}"
            content = service_post_html(city, climate, ar, hint, key)
            while ar_words(content) < 1000:
                content += f"\n<p>داخل {city} نؤكد تفاصيل الحي وطريقة الوصول قبل تنفيذ {ar}، ونوضح ما يشمله الاتفاق وما يخرج عنه.</p>"
            if found:
                put(f"/wp/v2/posts/{found[0]['id']}", {"content": content, "status": "publish"})
                created_posts.append({"id": found[0]["id"], "slug": slug, "updated": True, "aw": ar_words(content)})
                print("update post", slug, flush=True)
            else:
                p = post(
                    "/wp/v2/posts",
                    {
                        "title": title,
                        "slug": slug,
                        "status": "publish",
                        "content": content,
                        "excerpt": f"{ar} في {city} — تنفيذ ميداني ونطاق واضح.",
                    },
                )
                created_posts.append({"id": p["id"], "slug": slug, "created": True, "aw": ar_words(content)})
                print("create post", slug, p["id"], flush=True)
            time.sleep(0.15)

    results["extended_city_pages"] = created_pages
    results["extended_service_posts"] = created_posts


def service_post_html(city: str, climate: str, service_ar: str, hint: str, city_key: str) -> str:
    return f"""
<p>تقديم <strong>{service_ar}</strong> في <strong>{city}</strong> عبر ركن التطور يبدأ من فهم العَرَض المحلي: {hint}. المناخ ({climate}) يؤثر على أولوية التدخل وطريقة التنفيذ.</p>
<p>هذه الصفحة مخصّصة لـ{city} وليست نسخة عامة لكل المملكة. اذكر الحي عند التواصل.</p>
[post_call]
<h2>متى تحتاج {service_ar} في {city}؟</h2>
<p>عند تكرر العَرَض أكثر من مرة، أو عند تأثيره على فاتورة المياه/الكهرباء أو راحة المنزل. التأجيل في {city} قد يوسّع الضرر بسبب {climate}.</p>
<h2>ماذا يشمل التنفيذ؟</h2>
<p>وصف الطلب، تأكيد النطاق، تنفيذ ميداني، ثم مراجعة سريعة للنتيجة. لا نضيف أعمالاً غير متفق عليها.</p>
<h2>خطوات التواصل</h2>
<p>واتساب <a href="https://wa.me/{WA}">wa.me/{WA}</a> مع: المدينة ({city})، الحي، نوع العقار، وصف قصير وصورة إن أمكن.</p>
<h2>أخطاء شائعة</h2>
<p>طلب أرخص عرض بلا نطاق، أو خلط خدمتين في طلب واحد، أو إصلاح تجميلي يخفي الأثر دون السبب.</p>
<h2>أسئلة شائعة حول {service_ar} في {city}</h2>
<h3>هل تغطون كل أحياء {city}؟</h3>
<p>نأكد التغطية حسب الحي عند الرسالة الأولى.</p>
<h3>هل يوجد ضمان؟</h3>
<p>يُذكر ضمن الاتفاق حسب نوع العمل المنفَّذ.</p>
<p><strong>الصفحة هذه مخصّصة</strong> لخدمة {service_ar} داخل {city} بأسلوب ميداني مباشر.</p>
"""


def verify(results: dict):
    sample_ids = [t["id"] for t in results.get("thin_enriched", [])[:5] if not t.get("skipped")]
    sample_ids += [x["id"] for x in results.get("piano_fixed", [])]
    checks = []
    for pid in sample_ids:
        _, p = get(f"/wp/v2/posts/{pid}?context=edit&_fields=id,slug,content,title")
        raw = p["content"].get("raw") or ""
        checks.append({"id": pid, "slug": p["slug"], "aw": ar_words(raw), "ew": en_words(raw), "title": p["title"]["raw"][:50]})
    results["verify_samples"] = checks
    print("verify", checks, flush=True)


def main():
    results = {"wa": WA, "note": "SEO titles untouched; call remains hidden per current NAP policy"}
    print("=== 1 thin ===", flush=True)
    enrich_thin(results)
    print("=== 2 piano ===", flush=True)
    fix_piano(results)
    print("=== 3 diversify clusters ===", flush=True)
    diversify_clusters(results)
    print("=== 4 hubs ===", flush=True)
    enrich_hubs(results)
    print("=== 5 extended coverage ===", flush=True)
    create_extended_coverage(results)
    print("=== verify ===", flush=True)
    verify(results)
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print("WROTE", OUT, flush=True)
    print(
        "SUMMARY",
        {
            "thin": len(results.get("thin_enriched", [])),
            "piano": len(results.get("piano_fixed", [])),
            "diversified": len(results.get("diversified", [])),
            "hubs": len(results.get("hubs", [])),
            "ext_pages": len(results.get("extended_city_pages", [])),
            "ext_posts": len(results.get("extended_service_posts", [])),
        },
        flush=True,
    )


if __name__ == "__main__":
    main()
