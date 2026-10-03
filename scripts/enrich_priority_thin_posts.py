#!/usr/bin/env python3
"""Enrich high-priority thin posts (AR + EN) and strip leftover PHONE placeholders."""

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
H = {"User-Agent": "Mozilla/5.0 RuknEnrich2/1.0", "Content-Type": "application/json"}
PHONE = "0568060309"
ROOT = Path(__file__).resolve().parents[1]

IMG = {
    "clean": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/12/cleaning-6.webp",
    "pest": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/12/clean-2.webp",
    "insul": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2026/08/roof-insulation-ae.webp",
    "leak": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2026/08/water-leak-detection.webp",
    "ac": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/08/plumber-1.webp",
    "plumb": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/08/plumbing.webp",
    "elec": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2021/12/toolbox.webp",
    "default": "https://www.rukn-eltatawer.com/sa/wp-content/uploads/2026/08/water-leak-detection.webp",
}

DISTRICTS = {
    "الرياض": ["النسيم", "الملز", "العليا", "الياسمين", "الشفا", "طويق", "حطين", "النرجس"],
    "جدة": ["الروضة", "أبحر", "الصفا", "النعيم", "الفيصلية"],
    "مكة": ["العزيزية", "الشوقية", "العوالي", "النسيم"],
    "المدينة": ["قباء", "العوالي", "الحرة الشرقية", "الملك فهد"],
    "الدمام": ["الفيصلية", "الشاطئ", "الجلوية", "أحد"],
    "الخبر": ["العقربية", "الحزام", "اليرموك", "الثقبة"],
    "الطائف": ["الشفا", "الحوية", "الروضة", "السلامة"],
    "أبها": ["المنسك", "الموظفين", "الوردتين", "الخالدية"],
}


def wc(html: str) -> int:
    t = re.sub(r"\[[^\]]+\]", " ", html or "")
    t = re.sub(r"<[^>]+>", " ", t)
    return len(re.findall(r"[\w\u0600-\u06FFA-Za-z0-9]+", html_lib.unescape(t)))


def pick(key: str, options: list):
    h = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return options[h % len(options)]


def city_of(title: str) -> str:
    for c in DISTRICTS:
        if c in title:
            return c
    return "الرياض"


def topic_of(title: str) -> str:
    t = title.lower()
    if any(k in title for k in ["مكيف", "تكييف", "فريون", "دكت", "سبليت", "تبريد"]):
        return "ac"
    if any(k in title for k in ["تسرب", "تسريب"]):
        return "leak"
    if any(k in title for k in ["تنظيف", "تعقيم", "جلي"]):
        return "clean"
    if any(k in title for k in ["مكافحة", "حشرات", "صراصير", "نمل", "بق", "عقارب", "بعوض"]):
        return "pest"
    if any(k in title for k in ["عزل", "فوم"]):
        return "insul"
    if any(k in title for k in ["سباك", "سباكة", "سخان", "مضخ", "مواسير"]):
        return "plumb"
    if any(k in title for k in ["كهرب", "إنارة"]):
        return "elec"
    return "default"


def service_name(title: str) -> str:
    t = re.sub(r"^شركة\s+", "", title)
    t = re.sub(r"\s+ب(?:الرياض|جدة|مكة|المدينة|الدمام|الخبر|الطائف|أبها).*$", "", t)
    return t.strip() or title


def strip_junk(body: str) -> str:
    body = body or ""
    # broken placeholders
    body = body.replace("{PHONE_RUKN}", PHONE)
    body = body.replace("{PHONE}", PHONE)
    body = body.replace("01556644443", PHONE)
    body = body.replace("+971", "+966")
    # remove manual CTA button clusters
    body = re.sub(
        r'<div[^>]*>\s*(?:<a[^>]+href="(?:tel:|https?://wa\.me/)[^"]*"[^>]*>.*?</a>\s*){1,4}</div>',
        "",
        body,
        flags=re.S | re.I,
    )
    body = re.sub(r'<a[^>]+href="tel:[^"]*"[^>]*>.*?</a>', "", body, flags=re.S | re.I)
    body = re.sub(r'<a[^>]+href="https?://wa\.me/[^"]*"[^>]*>.*?</a>', "", body, flags=re.S | re.I)
    # collapse post_call
    body = re.sub(r"(?:\[post_call\]\s*){3,}", "[post_call]\n", body)
    return body



def enrich_ar(title: str, raw: str) -> tuple[str, str]:
    city = city_of(title)
    topic = topic_of(title)
    svc = service_name(title)
    districts = DISTRICTS.get(city, DISTRICTS["الرياض"])
    dcsv = "، ".join(districts[:5])
    dcsv2 = "، ".join(districts[2:6] if len(districts) > 5 else districts)
    img = IMG.get(topic, IMG["default"])
    img2 = IMG.get("default" if topic == "default" else ("plumb" if topic in ("ac", "leak") else "clean" if topic == "pest" else topic), IMG["default"])
    body = strip_junk(raw)

    why = pick(
        title,
        [
            f"في {city} يختلف الاحتياج حسب نوع العقار وحجم المشكلة؛ لذلك نبدأ بفهم العَرَض ثم نحدد نطاق التنفيذ بوضوح قبل أي توسع.",
            f"سكان {city} يبحثون عن نتيجة عملية لا وعود عامة؛ نوضح الخطوات والنطاق المتوقع قبل البدء حتى تكون الصورة واضحة.",
            f"خدمة {svc} في {city} تحتاج تنفيذاً مرتباً يحافظ على التشطيب ويختصر الوقت، خصوصاً في الفلل والشقق عالية الاستخدام.",
        ],
    )
    tip = pick(
        title,
        [
            f"عند الحجز اذكر الحي في {city} ونوع العقار ووصف مختصر للمشكلة؛ هذه التفاصيل تختصر المعاينة.",
            f"صوّر العَرَض إن أمكن؛ ذلك يساعدنا على تجهيز المعدات المناسبة لـ{svc} من أول زيارة.",
            f"لا تعتمد على حلول مؤقتة متكررة قبل التشخيص، خصوصاً داخل منازل {city} حيث يتفاقم الضرر مع الحر والغبار.",
        ],
    )
    mistake = pick(
        title,
        [
            "تأجيل المشكلة حتى يتوسع الضرر إلى تشطيبات إضافية",
            "طلب تنفيذ واسع قبل التأكد من السبب الحقيقي",
            "استخدام مواد أو حلول غير مناسبة لنوع السطح أو الجهاز",
            "إغفال الصيانة الدورية ثم الاصطدام بعطل في موسم الذروة",
        ],
    )
    season = pick(
        title,
        [
            f"قبل ذروة الصيف في {city} حين يزيد الضغط على التكييف والشبكات",
            f"قبل انتقال السكن أو استقبال ضيوف داخل {city}",
            f"مباشرة بعد ملاحظة تكرار العَرَض أسبوعياً في نفس النقطة",
            f"عند استعدادك لصيانة موسمية تحفظ المنزل قبل تفاقم الأعطال في {city}",
        ],
    )
    property_note = pick(
        title,
        [
            f"في الشقق داخل {city} نراعي ضيق المساحة وسرعة الإنجاز دون إغفال الزوايا الحساسة.",
            f"في الفلل داخل {city} نوزّع الأولويات على الأدوار والملحقات والنقاط الخارجية المرتبطة بالخدمة.",
            f"سواء كان العقار شقة أو فيلا في {city}، نضبط الخطة حسب التشطيب وسهولة الوصول لنقطة المشكلة.",
        ],
    )

    content = f"""
<p style="font-size:1.25em;font-weight:700;color:#005CB9;line-height:1.5;">{html_lib.escape(title)} — دليل عملي من ركن التطور</p>
<p><strong>شركة ركن التطور</strong> تقدّم <strong>{html_lib.escape(svc)}</strong> في <strong>{city}</strong> بأسلوب ميداني واضح: معاينة العَرَض، تحديد النطاق، ثم التنفيذ بعد الاتفاق. {why}</p>
<p>الهدف ليس تعبئة صفحة بكلمات عامة، بل مساعدة صاحب المنزل على اتخاذ قرار صحيح: هل المشكلة تستدعي تدخلاً الآن؟ وما النطاق الأنسب دون صرف زائد؟ لهذا نربط كل زيارة بوصف عملي يناسب عقارات {city} وطبيعة الخدمة.</p>
[post_call]
<p style="margin:28px 0;"><img src="{img}" alt="{html_lib.escape(title)}" loading="lazy" decoding="async" style="width:100%;height:auto;border-radius:8px;" /></p>

<h2>متى تحتاج {html_lib.escape(svc)} في {city}؟</h2>
<ul>
<li>عند ظهور عَرَض يؤثر على استخدام المنزل أو الراحة اليومية.</li>
<li>قبل موسم الذروة المرتبط بالمشكلة (حر، غبار، أمطار، انتقال سكن).</li>
<li>عند فشل الحلول المؤقتة أو تكرار نفس المشكلة أسبوعياً.</li>
<li>كجزء من صيانة وقائية تحفظ التشطيب وقيمة العقار في {city}.</li>
<li>عندما تريد رأياً مهنياً يحدد إن كانت المشكلة محلية أم تحتاج خدمة مساندة.</li>
</ul>
<p>{tip}</p>
<p>أفضل وقت للطلب غالباً {season}. التأجيل في منازل {city} يحوّل مشكلة صغيرة إلى ترميم أوسع أو تكرار أعطال مزعج.</p>

<h2>نطاق التغطية داخل {city}</h2>
<p>نصل حسب الجدولة اليومية إلى أحياء {city} وما حولها، ومنها: {dcsv}. كما نغطي نطاقات قريبة مثل {dcsv2} وفق ضغط الطلب اليومي.</p>
<p>عند الحجز اذكر الحي بدقة ونوع العقار (شقة/فيلا/استراحة) وعدد النقاط المتأثرة. هذه المعلومات تجعل زيارة {html_lib.escape(svc)} أسرع وأكثر ترتيباً.</p>
<p>{property_note}</p>

<h2>كيف ننفّذ خدمة {html_lib.escape(svc)}؟</h2>
<ol>
<li>تواصل على {PHONE} (اتصال أو واتساب) مع وصف العَرَض والحي داخل {city}.</li>
<li>معاينة ميدانية سريعة لتحديد السبب والنطاق الأنسب.</li>
<li>شرح الخيار العملي قبل أي توسع غير لازم.</li>
<li>تنفيذ الخدمة بأدوات مناسبة لحالة العقار والتشطيب.</li>
<li>ملاحظات ختامية لتقليل تكرار المشكلة قدر الإمكان.</li>
</ol>
<p style="margin:28px 0;"><img src="{img2}" alt="تنفيذ {html_lib.escape(svc)} في {city}" loading="lazy" decoding="async" style="width:100%;height:auto;border-radius:8px;" /></p>
<p>خلال التنفيذ نحرص على ترتيب منطقة العمل وحماية الأسطح المجاورة قدر الإمكان، ثم مراجعة النقاط المتفق عليها قبل المغادرة. إذا ظهرت حاجة لخدمة مساندة نوضحها بصراحة بدل إخفائها أو فرضها.</p>

<h2>ما الذي يميز ركن التطور في {city}؟</h2>
<ul>
<li>تركيز على خدمات المنازل داخل السعودية بهوية محلية واضحة.</li>
<li>تشخيص قبل التنفيذ لتقليل الأعمال العشوائية.</li>
<li>إمكانية ربط الخدمة بخدمات مساندة عند الحاجة مثل التسربات أو العزل أو التنظيف أو التكييف.</li>
<li>رقم موحّد للتواصل: {PHONE}</li>
<li>تغطية أحياء {city} ضمن جدول يومي منظم.</li>
<li>توضيح النطاق قبل البدء حتى لا يختلط العمل الأساسي بالكماليات.</li>
</ul>

<h2>أخطاء شائعة تؤخر الحل</h2>
<ul>
<li>{mistake}.</li>
<li>الاعتماد على وصف سعر عام دون ربطه بمساحة عقارك وحالته في {city}.</li>
<li>إخفاء العَرَض بدهان أو تنظيف سطحي دون معالجة المصدر.</li>
<li>تأجيل الحجز حتى تتحول المشكلة البسيطة إلى ترميم أوسع.</li>
<li>طلب باقة كاملة بينما تكفي معالجة نقطة واحدة محددة.</li>
</ul>

<h2>إرشاد عملي للوقت والتكلفة</h2>
<p>لا يوجد رقم واحد يناسب كل طلب لـ{html_lib.escape(svc)} في {city}. الزمن والتكلفة يتغيران حسب المساحة ودرجة الحالة وسهولة الوصول ونوع التشطيب. نوضّح النطاق قبل التنفيذ حتى تعرف ما سيتم إنجازه دون مفاجآت.</p>
<p>إذا كان الطلب عاجلاً بسبب ضرر يتوسع، اذكر ذلك عند الحجز لنرتب الأولوية ضمن الجدول المتاح. الحالات التي تهدد التشطيب أو تسبب إزعاجاً يومياً واضحاً تُعامل بأولوية أعلى قدر الإمكان.</p>
<p>للحصول على تقدير أوضح: صف العَرَض، اذكر الحي، وحدّد إن كانت المشكلة جديدة أم متكررة بعد حلول سابقة. هذه الثلاثة تختصر كثيراً من الجدل حول السعر والوقت.</p>

<h2>نصائح قبل زيارة الفريق</h2>
<ul>
<li>جهّز وصولاً آمناً لمكان المشكلة (خزان، مكيف، مطبخ، سطح، لوحة كهرباء… حسب نوع الخدمة).</li>
<li>أزل العوائق البسيطة من محيط العمل إن أمكن لتسريع التنفيذ.</li>
<li>أخبرنا بأي محاولة سابقة أو مواد استُخدمت على نفس النقطة.</li>
<li>حدّد الغرف أو النقاط الأعلى أولوية إذا كان الوقت محدوداً.</li>
<li>احتفظ بصور قبل وبعد عند الإمكان؛ تفيد في المتابعة لاحقاً.</li>
</ul>

<h2>خطة وقاية بسيطة بعد الخدمة</h2>
<ul>
<li>راقب العَرَض خلال الأيام التالية وتأكد أنه لم يعد بنفس القوة.</li>
<li>لا تغطِّ أي أثر متبقٍ قبل التأكد من جفاف المصدر أو استقرار الحالة.</li>
<li>اجعل للصيانة الدورية موعداً موسمياً بدل الانتظار حتى العطل الكامل.</li>
<li>إذا عاد العَرَض بسرعة، تواصل مبكراً بدل تكرار حلول منزلية عشوائية.</li>
</ul>
<p>الوقاية في مناخ {city} ليست ترفاً؛ الحر والغبار والرطوبة الموسمية يضغطون على المنازل باستمرار. زيارة مبكرة لـ{html_lib.escape(svc)} غالباً أوفر من ترميم متأخر.</p>

<h2>الربط مع خدمات أخرى من ركن التطور</h2>
<p>أحياناً تبدأ بـ{html_lib.escape(svc)} ثم يتضح احتياج مساند مثل كشف تسرب، عزل، تسليك، تنظيف أعمق، أو صيانة تكييف. وجود هذه الخدمات تحت مظلة واحدة يختصر التنقل بين جهات متعددة بتوصيات متعارضة.</p>
<p>لا نضيف خدمة مساندة إلا إذا كانت تضيف قيمة حقيقية لعقارك. الهدف إغلاق السبب لا تكبير الفاتورة.</p>

<h2>سيناريوهات شائعة في {city}</h2>
<ul>
<li>عَرَض جديد ظهر فجأة وتريد معرفة إن كان يحتاج تدخلاً فورياً.</li>
<li>مشكلة متكررة بعد حلول مؤقتة ولم تُغلق جذرياً.</li>
<li>تحضير موسمي قبل الحر أو الأمطار أو استقبال سكان جدد.</li>
<li>ربط الخدمة بفحص مساند عندما يشتبه الفريق بسبب مشترك.</li>
</ul>
<p>في كل سيناريو نبدأ من وصفك ثم المعاينة، ونبني نطاقاً يناسب منزلك لا قالباً ثابتاً. هذا مهم مع تنوع الفلل والشقق والتشطيبات داخل {city}.</p>

<h2>تفصيل إضافي حسب نوع العقار في {city}</h2>
<p>الشقق تحتاج تركيزاً على سرعة الوصول والنقاط الأكثر استخداماً مثل المطبخ والحمامات والمجالس. الفلل تحتاج توزيعاً أوسع يشمل الأدوار والملحقات وأحياناً النقاط الخارجية المرتبطة بنفس العَرَض. عند طلب {html_lib.escape(svc)} في {city} نضبط الخطة حسب هذا الاختلاف حتى لا يضيع الوقت في ترتيب غير مناسب للمساحة.</p>
<p>إذا كان لديك أكثر من نقطة متأثرة، رتبها بالأهمية قبل الزيارة. هذا يجعل خدمة {html_lib.escape(svc)} أوضح ويعطي نتيجة ملموسة خلال نفس الموعد.</p>

<h2>معايير جودة بسيطة بعد الزيارة</h2>
<p>بعد خدمة {html_lib.escape(svc)} في {city} اسأل نفسك: هل اتضح السبب؟ هل تقلص العَرَض؟ هل عرفت الخطوة التالية إن وجدت؟ هل كان النطاق مفهوماً قبل التنفيذ؟ هذه الأسئلة أوضح من الانطباع العام وتساعدك على تقييم النتيجة بوعي.</p>
<p>ركن التطور يركز على هذه المعايير لأنها ترتبط برضا عملي مباشر. ومع منازل {city} نحرص أن تخرج بقرار أوضح: ماذا أُنجز، وما الذي تراقبه خلال الأيام التالية، ومتى تحتاج متابعة.</p>

<h2>لماذا التشخيص أهم من الاستعجال؟</h2>
<p>الاستعجال مفهوم عندما يتضرر التشطيب أو يتعطل جزء أساسي من المنزل. لكن التنفيذ السريع دون فهم السبب قد يكرر الزيارة خلال أيام. في خدمة {html_lib.escape(svc)} داخل {city} نوازن بين سرعة الاستجابة ودقة النطاق، حتى لا تدفع مرتين على نفس المشكلة.</p>
<p>إذا كانت حالتك طارئة، أخبرنا بذلك منذ أول تواصل على {PHONE}. نرتب الأولوية ضمن الجدول المتاح ونوضح ما يمكن إنجازه اليوم وما يُجدول لاحقاً إن لزم.</p>

<h2>أسئلة شائعة عن {html_lib.escape(svc)} في {city}</h2>
<h3>هل الخدمة متاحة في كل أحياء {city}؟</h3>
<p>نعم حسب جدولة اليوم، بما في ذلك نطاق مثل {dcsv}.</p>
<h3>هل يمكن تخصيص نطاق العمل؟</h3>
<p>نعم. يمكن التركيز على نقاط محددة بدل باقة عامة غير لازمة.</p>
<h3>كيف أحجز؟</h3>
<p>اتصل أو راسل واتساب على {PHONE} واذكر الحي ونوع العقار ووصف العَرَض.</p>
<h3>هل التسعير ثابت؟</h3>
<p>يختلف حسب الحالة؛ نوضّح التكلفة قبل الأعمال الإضافية.</p>
<h3>ماذا أجهز قبل الزيارة؟</h3>
<p>وصول آمن لنقطة المشكلة، ووصف مختصر، وأي ملاحظات عن محاولات سابقة داخل {city}.</p>
<h3>هل يمكن دمج الخدمة مع عمل آخر في نفس الزيارة؟</h3>
<p>أحياناً نعم إذا كان ذلك عملياً ويختصر الوقت؛ نخبرك بذلك بعد المعاينة.</p>
[post_call]
<p>ركن التطور — {html_lib.escape(title)} | {city} | {PHONE}</p>
""".strip()

    excerpt = (
        f"{title} من ركن التطور في {city}: تنفيذ عملي، نطاق واضح قبل البدء، "
        f"وتغطية أحياء مثل {dcsv}. تواصل {PHONE}."
    )
    return content, excerpt


def enrich_en_leak() -> tuple[str, str]:
    content = f"""
<p><strong>Rukn Eltatawer</strong> provides professional <strong>water leak detection in Riyadh</strong> for villas, apartments, and commercial properties across Saudi Arabia. We locate hidden leaks with modern equipment, reduce unnecessary demolition, and explain the repair scope before work starts.</p>
<p>Homeowners in Riyadh often notice the problem late: a rising bill, damp paint, or a meter that keeps moving after every tap is closed. Our job is to confirm the source quickly and recommend the narrowest practical fix.</p>
[post_call]
<p style="margin:28px 0;"><img src="{IMG['leak']}" alt="Water leak detection in Riyadh" loading="lazy" style="width:100%;height:auto;border-radius:8px;" /></p>

<h2>When do you need leak detection in Riyadh?</h2>
<ul>
<li>Your water meter moves while all taps are closed.</li>
<li>Unexpected rise in the water bill over one or two cycles.</li>
<li>Damp walls, peeling paint, or a recurring mold smell.</li>
<li>Low pressure in one wing or floor of the property.</li>
<li>Wet garden areas with no recent irrigation explanation.</li>
<li>Repeated paint failure in the same corner after every touch-up.</li>
</ul>

<h2>How we work</h2>
<ol>
<li>Call or WhatsApp {PHONE} with your district and symptoms.</li>
<li>On-site inspection of the meter, tanks, and visible lines.</li>
<li>Device-based detection (acoustic, moisture, thermal, or camera as needed).</li>
<li>Clear report and repair options before extra work.</li>
<li>Targeted repair and confirmation test when requested.</li>
</ol>

<h2>Areas we cover in Riyadh</h2>
<p>We serve major districts including Al Naseem, Al Malaz, Olaya, Al Yasmin, Tuwaiq, Hittin, and nearby neighborhoods according to daily scheduling. Mention your district when booking so the team arrives prepared.</p>

<h2>Common mistakes that delay the fix</h2>
<ul>
<li>Repainting over damp areas without stopping the source.</li>
<li>Breaking random tiles far from the real path of the leak.</li>
<li>Assuming the problem is always the neighbor without testing the meter.</li>
<li>Ignoring garden irrigation lines around villas.</li>
<li>Waiting weeks until ceiling damage becomes expensive to restore.</li>
</ul>

<h2>Why homeowners in Riyadh choose Rukn Eltatawer</h2>
<ul>
<li>Saudi-focused local service with Riyadh as the operating base.</li>
<li>Diagnosis first to reduce unnecessary demolition.</li>
<li>One contact number for calls and WhatsApp: {PHONE}.</li>
<li>Related services available when needed: waterproofing, drainage, and maintenance.</li>
<li>Clear scope before additional work so you know what you are approving.</li>
</ul>

<h2>Practical booking tips</h2>
<p>Prepare a short description of the symptom, the district, and the property type (villa/apartment). Photos of damp spots help. If the issue is expanding quickly, say so when you call so we can prioritize within the available schedule.</p>
<p>For villas, tell us whether you have an overhead tank, irrigation lines, or a recent roof wash. For apartments, mention which floor and whether neighbors share similar symptoms.</p>

<h2>After detection</h2>
<p>If repair is requested, we focus on the confirmed point first. Related waterproofing or drainage work is suggested only when the inspection shows a real link. The goal is to stop the loss and protect finishing, not to enlarge the job without reason.</p>

<h2>Cost and scope clarity</h2>
<p>There is no single price for every villa or apartment in Riyadh. Scope depends on property size, number of suspect points, and whether repair is requested after detection. We explain the inspection path first, then any additional work.</p>
<p>If you compare providers, ask about diagnosis method, whether demolition is minimized, and whether repair is optional after the report. Those questions matter more than a vague package promise.</p>

<h2>Prevention tips for Riyadh homes</h2>
<ul>
<li>Test the meter monthly for two minutes with all taps closed.</li>
<li>Check garden valves each season on villa properties.</li>
<li>Photograph new damp spots with the date they appeared.</li>
<li>Do not repaint over active moisture before the source is confirmed.</li>
</ul>

<h2>FAQ</h2>
<h3>Do you break tiles immediately?</h3>
<p>No. We identify the source first and open only a narrow area when confirmed.</p>
<h3>Is the service available outside Riyadh?</h3>
<p>Yes. Coverage depends on daily scheduling across Saudi cities.</p>
<h3>Can you repair after detection?</h3>
<p>Yes, when requested. We explain the option and cost before additional work.</p>
<h3>How long does an inspection take?</h3>
<p>Usually one to three hours depending on property size and the number of suspect points.</p>
[post_call]
<p>Rukn Eltatawer — Water Leak Detection in Riyadh | {PHONE}</p>
""".strip()
    excerpt = f"Professional water leak detection in Riyadh without unnecessary demolition. Call Rukn Eltatawer on {PHONE}."
    return content, excerpt


def enrich_en_roof() -> tuple[str, str]:
    content = f"""
<p><strong>Roof waterproofing in Riyadh</strong> from <strong>Rukn Eltatawer</strong> protects homes from heat stress, moisture, and seasonal rain damage. We inspect the roof surface, drains, joints, and tank areas, then recommend a practical insulation method for your property.</p>
<p>In Riyadh, roof coatings age faster because of UV exposure and temperature swings. A small crack can become ceiling dampness, paint failure, or repeated upper-floor heat complaints if ignored.</p>
[post_call]
<p style="margin:28px 0;"><img src="{IMG['insul']}" alt="Roof waterproofing in Riyadh" loading="lazy" style="width:100%;height:auto;border-radius:8px;" /></p>

<h2>Signs you need roof waterproofing</h2>
<ul>
<li>Ceiling dampness after rain or after washing the roof.</li>
<li>Hot upper-floor rooms despite AC use.</li>
<li>Cracked or aging waterproofing layers.</li>
<li>Tank overflow marks around the roof slab.</li>
<li>Repeated blistering or peeling on ceiling paint.</li>
<li>Standing water that does not drain properly from roof corners.</li>
</ul>

<h2>Our process</h2>
<ol>
<li>Inspection of slopes, drains, joints, and tanks.</li>
<li>Surface preparation and treatment of weak points.</li>
<li>Application of a suitable waterproofing system.</li>
<li>Final checks and simple maintenance tips for Riyadh weather.</li>
</ol>

<h2>Why timing matters in Riyadh</h2>
<p>Waiting until the next rainy period often turns a small crack into a wider ceiling repair. Early inspection is usually cheaper than late renovation, especially on villas with large exposed roofs.</p>

<h2>Serving Riyadh and Saudi Arabia</h2>
<p>Based in Riyadh with nationwide scheduling. Call {PHONE} for assessment and booking. Share your district and roof type for a clearer scope.</p>

<h2>Related checks</h2>
<p>If ceiling moisture continues after waterproofing discussions, we may recommend leak detection to confirm whether the source is roofing, tanks, or an internal line. The inspection decides the order of work.</p>

<h2>Roof maintenance habits</h2>
<p>Keep drains clear, avoid trapping water around tanks, and inspect the coating after major sandstorms or temperature spikes. These habits extend the life of waterproofing work in Riyadh and reduce emergency ceiling repairs.</p>
<p>If you recently remodeled an upper floor, tell the team; new openings around AC lines or tanks are common weak points.</p>

<h2>What affects roof waterproofing cost?</h2>
<p>Roof size, existing coating condition, drain points, and tank surroundings all change the scope. An inspection in Riyadh is the reliable way to avoid under-quoting or over-selling.</p>
<p>If upper-floor heat is your main complaint, we also discuss whether thermal performance and waterproofing should be handled together or sequenced.</p>

<h2>FAQ</h2>
<h3>Do you only waterproof roofs?</h3>
<p>We also handle related tank waterproofing and leak checks when the inspection shows a connected issue.</p>
<h3>How do I book?</h3>
<p>Call or WhatsApp {PHONE} with your location and a short description of the problem.</p>
<h3>Can you inspect before quoting?</h3>
<p>Yes. A clear scope after inspection is more reliable than a blind package price.</p>
[post_call]
<p>Rukn Eltatawer — Roof Waterproofing in Riyadh | {PHONE}</p>
""".strip()
    excerpt = f"Roof and tank waterproofing in Riyadh for heat and rain protection. Contact Rukn Eltatawer on {PHONE}."
    return content, excerpt


def enrich_en_clean() -> tuple[str, str]:
    content = f"""
<p><strong>Home cleaning in Riyadh</strong> by <strong>Rukn Eltatawer</strong> focuses on practical results: dust control, kitchens and bathrooms, and high-touch disinfection when needed. Tell us your property type and priority rooms for a clear scope before the visit.</p>
<p>Dust, long AC hours, and busy family schedules make light weekly wiping insufficient for many homes in Riyadh. A structured visit prioritizes high-use rooms first so you notice the difference quickly.</p>
[post_call]
<p style="margin:28px 0;"><img src="{IMG['clean']}" alt="Home cleaning in Riyadh" loading="lazy" style="width:100%;height:auto;border-radius:8px;" /></p>

<h2>What we clean</h2>
<ul>
<li>Apartments, villas, and deep seasonal cleaning.</li>
<li>Kitchens, bathrooms, floors, and high-touch points.</li>
<li>Optional add-ons such as sofa or carpet cleaning.</li>
<li>Move-in / move-out readiness cleaning when requested.</li>
</ul>

<h2>How booking works</h2>
<ol>
<li>Contact {PHONE} with district and property size.</li>
<li>Confirm scope and preferred time window.</li>
<li>On-site cleaning with a final walkthrough of agreed points.</li>
</ol>

<h2>Riyadh cleaning challenges</h2>
<p>Fine dust returns quickly, especially in rooms with frequent AC use. That is why we separate routine tidying from deeper cleaning of kitchens, bathrooms, and fabric surfaces when those are part of the request.</p>

<h2>Riyadh districts</h2>
<p>Coverage includes Al Naseem, Al Malaz, Olaya, Al Yasmin, Al Narjis, and nearby areas based on daily schedule.</p>

<h2>Tips before the visit</h2>
<ul>
<li>Clear small personal items from priority surfaces.</li>
<li>Tell us about sensitive finishes or fabrics in advance.</li>
<li>Mention if you need ventilation time after steam or disinfection.</li>
</ul>

<h2>Pricing expectations for cleaning</h2>
<p>Cleaning cost in Riyadh depends on property size, clutter level, and whether the request is routine or deep cleaning. A clear room list produces a clearer visit than a vague “clean everything” instruction.</p>
<p>If you need the home ready for guests the same day, say so early. We can prioritize visible high-impact rooms first.</p>

<h2>Apartment vs villa cleaning in Riyadh</h2>
<p>Apartments usually need faster, quieter work with clear room priorities. Villas need floor-by-floor planning and attention to annex spaces. Tell us which rooms matter most so the visit matches your day.</p>
<p>If odors return quickly after cleaning, the source may be AC units, humidity, or another issue. We can guide you to the right follow-up service instead of repeating the same clean blindly.</p>

<h2>FAQ</h2>
<h3>Do you bring cleaning materials?</h3>
<p>Yes for standard jobs, with care for sensitive surfaces when you tell us in advance.</p>
<h3>Can I request specific rooms only?</h3>
<p>Yes. You can limit the visit to majlis, kitchen, bathrooms, or other priorities.</p>
<h3>Is deep cleaning different from regular cleaning?</h3>
<p>Yes. Deep cleaning takes longer and targets accumulated dust and detail areas beyond a quick pass.</p>
[post_call]
<p>Rukn Eltatawer — Home Cleaning in Riyadh | {PHONE}</p>
""".strip()
    excerpt = f"Practical home and villa cleaning in Riyadh with clear scope and scheduling. Call {PHONE}."
    return content, excerpt



PRIORITY_IDS = [
    # EN thin
    14833,
    14834,
    14835,
    # high-search AR recently published thin
    10856,
    10857,
    10858,
    10870,
    10872,
    10879,
    11339,
    11340,
    11341,
    12528,
    12552,
    12560,
    12568,
    12664,
    12672,
    12680,
]


def fetch_future_priority(limit: int = 40) -> list[int]:
    ids = []
    r = requests.get(
        f"{BASE}/wp-json/wp/v2/posts",
        auth=AUTH,
        headers=H,
        params={
            "per_page": limit,
            "status": "future",
            "orderby": "date",
            "order": "asc",
            "context": "edit",
            "_fields": "id,title,date",
        },
        timeout=90,
    )
    r.raise_for_status()
    for p in r.json():
        title = p["title"]["raw"]
        if "بالرياض" in title and any(
            k in title
            for k in [
                "تكييف",
                "مكيف",
                "سباك",
                "كهرب",
                "عزل",
                "تسرب",
                "تنظيف",
                "مكافحة",
                "فريون",
                "دكت",
            ]
        ):
            ids.append(p["id"])
    return ids


def update_post(pid: int, payload: dict) -> dict:
    r = requests.post(
        f"{BASE}/wp-json/wp/v2/posts/{pid}",
        auth=AUTH,
        headers=H,
        json=payload,
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def main():
    report = {"updated": [], "errors": []}
    targets = list(PRIORITY_IDS) + fetch_future_priority(50)
    # unique preserve order
    seen = set()
    ids = []
    for i in targets:
        if i not in seen:
            seen.add(i)
            ids.append(i)

    print(f"targets={len(ids)}", flush=True)
    for pid in ids:
        try:
            r = requests.get(
                f"{BASE}/wp-json/wp/v2/posts/{pid}",
                auth=AUTH,
                headers=H,
                params={"context": "edit"},
                timeout=60,
            )
            r.raise_for_status()
            p = r.json()
            title = p["title"]["raw"]
            raw = (p.get("content") or {}).get("raw") or ""
            old = wc(raw)
            if pid == 14833:
                content, excerpt = enrich_en_leak()
            elif pid == 14834:
                content, excerpt = enrich_en_roof()
            elif pid == 14835:
                content, excerpt = enrich_en_clean()
            else:
                # enrich if thin or still has placeholder junk
                if old >= 1200 and "{PHONE_RUKN}" not in raw and "tel:{PHONE" not in raw:
                    # still strip junk lightly
                    cleaned = strip_junk(raw)
                    if cleaned == raw:
                        report["updated"].append({"id": pid, "skipped": True, "words": old, "title": title})
                        continue
                    content, excerpt = cleaned, None
                else:
                    content, excerpt = enrich_ar(title, raw)
            payload = {"content": content}
            if excerpt is not None:
                payload["excerpt"] = excerpt
            update_post(pid, payload)
            new = wc(content if isinstance(content, str) else raw)
            report["updated"].append(
                {"id": pid, "title": title, "old": old, "new": wc(content), "status": p.get("status")}
            )
            print(f"OK #{pid} {old}->{wc(content)} {title[:50]}", flush=True)
            time.sleep(0.08)
        except Exception as e:
            report["errors"].append({"id": pid, "error": str(e)[:200]})
            print("ERR", pid, e, flush=True)
            time.sleep(0.2)

    out = ROOT / "data/priority-enrich-2026-09-02.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "updated": len([x for x in report["updated"] if not x.get("skipped")]),
                "skipped": len([x for x in report["updated"] if x.get("skipped")]),
                "errors": len(report["errors"]),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
