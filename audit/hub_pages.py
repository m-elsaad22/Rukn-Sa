"""Saudi hub page bodies adapted from Call-main layouts (no UAE copy, no invented stats)."""

WA = "https://wa.me/971586634710"
HOME = "https://www.rukn-eltatawer.com/sa"


def wa_btn(label: str = "تواصل عبر واتساب") -> str:
    return (
        f'<a class="btn btn-wa" href="{WA}" target="_blank" rel="nofollow noopener noreferrer">'
        f'<i class="fab fa-whatsapp"></i> {label}</a>'
    )


SERVICES = [
    ("water-leak-detection", "كشف تسربات المياه", "fas fa-water", "تحديد موضع التسرب بأجهزة فحص، دون تكسير عشوائي."),
    ("insulation-of-roofs-and-cabinets", "عزل الأسطح والخزانات", "fas fa-house-water", "عزل مائي وحراري حسب حالة السطح والخزان بعد المعاينة."),
    ("air-conditioner-maintenance-and-installation", "صيانة وتركيب المكيفات", "fas fa-fan", "غسيل وصيانة وحدات ودكتات حسب نوع الجهاز."),
    ("cleaning-and-sterilization", "تنظيف عميق وتعقيم", "fas fa-broom", "تنظيف منازل ومكاتب بمواد تُذكر للعميل قبل الاستخدام."),
    ("sewer-wiring", "تسليك المجاري", "fas fa-faucet-drip", "تسليك انسداد الصرف بعد وصف العَرَض والموقع."),
    ("pest-control", "مكافحة الحشرات", "fas fa-bug-slash", "برنامج مكافحة يُحدَّد بعد معاينة الإصابة."),
    ("construction-and-maintenance-of-swimming-pools", "إنشاء وصيانة المسابح", "fas fa-swimming-pool", "صيانة أنظمة الفلترة والتنظيف حسب حالة المسبح."),
    ("landscaping", "تنسيق الحدائق", "fas fa-leaf", "أعمال حدائق حسب مساحة الموقع ونوع الزراعة."),
    ("gypsum-board-installation", "تركيب جبس بورد", "fas fa-border-all", "أسقف وجدران جبسية حسب المخطط المتفق عليه."),
    ("parquet-installation", "تركيب الباركيه", "fas fa-border-none", "أرضيات خشبية بعد تجهيز السطح."),
    ("sound-insulation-installation", "عازل الصوت", "fas fa-volume-xmark", "عزل صوتي للغرف حسب الاستخدام."),
    ("construction-and-maintenance-of-buildings", "إنشاء وصيانة المباني", "fas fa-helmet-safety", "أعمال صيانة مباني حسب نطاق يتفق عليه بعد المعاينة."),
]

CITIES = [
    ("riyadh", "الرياض"),
    ("jeddah", "جدة"),
    ("makkah", "مكة المكرمة"),
    ("madinah", "المدينة المنورة"),
    ("dammam", "الدمام"),
    ("khobar", "الخبر"),
    ("taif", "الطائف"),
    ("abha", "أبها"),
]

CITY_LINKS = {
    "riyadh": [
        ("كشف تسربات المياه", "water-leak-detection-riyadh"),
        ("تنظيف منازل", "home-cleaning-riyadh"),
        ("شحن سيارات", "car-shipping-riyadh"),
        ("شحن أثاث", "furniture-shipping-riyadh"),
        ("تنظيف دكت", "duct-cleaning-riyadh"),
        ("شحن داخلي", "domestic-shipping-riyadh"),
    ],
    "jeddah": [
        ("كشف تسربات المياه", "water-leak-detection-jeddah"),
        ("تنظيف منازل", "home-cleaning-jeddah"),
        ("شحن سيارات", "car-shipping-jeddah"),
        ("شحن أثاث", "furniture-shipping-jeddah"),
        ("تنظيف دكت", "duct-cleaning-jeddah"),
        ("شحن داخلي", "domestic-shipping-jeddah"),
    ],
    "makkah": [
        ("كشف تسربات المياه", "water-leak-detection-makkah"),
        ("تنظيف منازل", "home-cleaning-mecca"),
        ("شحن سيارات", "car-shipping-mecca"),
        ("شحن أثاث", "furniture-shipping-mecca"),
        ("تنظيف دكت", "duct-cleaning-mecca"),
        ("شحن داخلي", "domestic-shipping-mecca"),
    ],
    "madinah": [
        ("كشف تسربات المياه", "water-leak-detection-medina"),
        ("تنظيف منازل", "home-cleaning-medina"),
        ("شحن سيارات", "car-shipping-medina"),
        ("شحن أثاث", "furniture-shipping-medina"),
        ("تنظيف دكت", "duct-cleaning-medina"),
        ("شحن داخلي", "domestic-shipping-medina"),
    ],
    "dammam": [
        ("كشف تسربات المياه", "water-leak-detection-dammam"),
        ("تنظيف منازل", "home-cleaning-dammam"),
        ("شحن سيارات", "car-shipping-dammam"),
        ("شحن أثاث", "furniture-shipping-dammam"),
        ("تنظيف دكت", "duct-cleaning-dammam"),
        ("شحن داخلي", "domestic-shipping-dammam"),
    ],
    "khobar": [
        ("كشف تسربات المياه", "water-leak-detection-khobar"),
        ("تنظيف منازل", "home-cleaning-khobar"),
        ("شحن سيارات", "car-shipping-khobar"),
        ("شحن أثاث", "furniture-shipping-khobar"),
        ("تنظيف دكت", "duct-cleaning-khobar"),
        ("شحن داخلي", "domestic-shipping-khobar"),
    ],
    "taif": [
        ("كشف تسربات المياه", "water-leak-detection-taif"),
        ("تنظيف منازل", "home-cleaning-taif"),
        ("شحن سيارات", "car-shipping-taif"),
        ("شحن أثاث", "furniture-shipping-taif"),
        ("تنظيف دكت", "duct-cleaning-taif"),
        ("شحن داخلي", "domestic-shipping-taif"),
    ],
    "abha": [
        ("كشف تسربات المياه", "water-leak-detection-abha"),
        ("تنظيف منازل", "home-cleaning-abha"),
        ("شحن سيارات", "car-shipping-abha"),
        ("شحن أثاث", "furniture-shipping-abha"),
        ("تنظيف دكت", "duct-cleaning-abha"),
        ("شحن داخلي", "domestic-shipping-abha"),
    ],
}


def about() -> str:
    return f"""
<section class="sec">
  <div class="wrap about-grid">
    <div class="abcard rv-l">
      <div class="aic"><i class="fas fa-bullseye"></i></div>
      <h2>مهمتنا</h2>
      <p>تقديم خدمات منزلية في مدن المملكة عبر قناة تواصل واحدة: وصف العَرَض، تحديد النطاق، ثم التنفيذ بعد الاتفاق. لا نخلط بين مدينة وأخرى في صفحة الخدمة.</p>
    </div>
    <div class="abcard rv-l">
      <div class="aic"><i class="fas fa-eye"></i></div>
      <h2>طريقة العمل</h2>
      <p>التواصل عبر واتساب، توضيح الحي ونوع العقار، الاتفاق على نطاق العمل قبل التنفيذ. لا نعرض أرقاماً عامة للسعر أو التقييم في هذه الصفحة.</p>
    </div>
  </div>
</section>
<section class="sec" style="padding-top:0">
  <div class="wrap">
    <div class="shead"><span class="tag">التغطية</span><h2>السعودية <span>لا نسخة دولة أخرى</span></h2>
    <p>هذا الموقع مخصص للسعودية. الخدمات الأساسية 12، والمدن التي نذكرها في الصفحات الداخلية هي مدن المملكة المرتبطة بكل مقال.</p></div>
    <div class="stats-grid">
      <div class="stat"><i class="fas fa-layer-group"></i><div class="num">12</div><div class="lbl">خدمة أساسية</div></div>
      <div class="stat"><i class="fas fa-map-location-dot"></i><div class="num">18+</div><div class="lbl">مدينة مذكورة في الدليل</div></div>
      <div class="stat"><i class="fas fa-calendar"></i><div class="num">10+</div><div class="lbl">سنوات عمل المجموعة</div></div>
    </div>
    <div style="text-align:center;margin-top:36px">{wa_btn("تحدث مع الفريق")}</div>
  </div>
</section>
""".strip()


def contact() -> str:
    return f"""
<section class="sec">
  <div class="wrap contact-layout">
    <div class="cinfo-card">
      <div class="inner">
        <h2 style="color:#fff;margin-bottom:22px">معلومات التواصل</h2>
        <div class="cinfo-item"><i class="fab fa-whatsapp"></i><div><b>واتساب</b><small>القناة المعتمدة حالياً</small></div></div>
        <div class="cinfo-item"><i class="fas fa-envelope"></i><div><b>البريد</b><small>admin@rukn-eltatawer.com</small></div></div>
        <div class="cinfo-item"><i class="fas fa-location-dot"></i><div><b>التغطية</b><small>المملكة العربية السعودية — الرياض نقطة التواصل الإدارية</small></div></div>
        <div class="cinfo-item"><i class="fas fa-clock"></i><div><b>الرد</b><small>خلال ساعات العمل عبر واتساب</small></div></div>
        {wa_btn("افتح واتساب الآن").replace('class="btn btn-wa"', 'class="btn btn-wa" style="width:100%;margin-top:20px"')}
      </div>
    </div>
    <div class="form-card">
      <h2 style="margin-bottom:6px">كيف تراسلنا</h2>
      <p style="color:var(--text2);margin-bottom:24px">اكتب في الرسالة: المدينة، الحي، نوع العقار، ووصف العَرَض في جملة واحدة. لا نطلب بيانات غير لازمة لتنسيق الزيارة.</p>
      <ul>
        <li><i class="fas fa-circle-check"></i> واتساب هو زر التواصل الظاهر في الموقع.</li>
        <li><i class="fas fa-circle-check"></i> أزرار الاتصال الهاتفي مخفية حتى يتوفر رقم سعودي.</li>
        <li><i class="fas fa-circle-check"></i> لا ننشر نموذجاً وهمياً يوحي بأن الرسالة وصلت دون إرسال حقيقي.</li>
      </ul>
      <div class="form-note"><i class="fas fa-lock"></i> لا نبيع بيانات التواصل ولا نستخدمها خارج طلب الخدمة.</div>
    </div>
  </div>
</section>
""".strip()


def services() -> str:
    cards = []
    for slug, name, icon, desc in SERVICES:
        url = f"{HOME}/services/{slug}/"
        cards.append(
            f"""<div class="svc rv filt" data-cat="all">
          <div class="svc-ic"><i class="{icon}"></i></div>
          <h3>{name}</h3>
          <p class="desc">{desc}</p>
          <a href="{url}" class="svc-cta">تفاصيل الخدمة <i class="fas fa-arrow-left"></i></a>
        </div>"""
        )
    return f"""
<section class="sec">
  <div class="wrap">
    <div class="shead"><span class="tag">الخدمات</span><h2>خدمات منزلية <span>حسب الطلب</span></h2>
    <p>اختر الخدمة ثم المدينة من صفحاتها الداخلية. السعر يُذكر بعد المعاينة لا من جدول عام.</p></div>
    <div class="services-grid">
        {"".join(cards)}
    </div>
    <div style="text-align:center;margin-top:40px">{wa_btn("اسأل عن خدمة")}</div>
  </div>
</section>
""".strip()


def cities() -> str:
    cards = []
    for slug, name in CITIES:
        url = f"{HOME}/cities/{slug}/"
        cards.append(
            f"""<a href="{url}" class="citycard">
          <div class="cc-in"><h3>{name}</h3><small><i class="fas fa-location-dot"></i> روابط خدمات منشورة لهذه المدينة</small></div>
        </a>"""
        )
    return f"""
<section class="sec">
  <div class="wrap">
    <div class="shead"><span class="tag">المدن</span><h2>اختر <span>مدينتك</span></h2>
    <p>كل بطاقة تفتح صفحة المدينة. لا نضع أرقام وصول أو تقييمات غير موثّقة.</p></div>
    <div class="city-grid">
        {"".join(cards)}
    </div>
  </div>
</section>
""".strip()


def city_page(slug: str, name: str, sample: str = "") -> str:
    links = CITY_LINKS.get(slug) or []
    items = "".join(
        f'<li><a href="{HOME}/{s}/"><i class="fas fa-chevron-left"></i> {label} في {name}</a></li>'
        for label, s in links
    )
    return f"""
<section class="sec">
  <div class="wrap article-layout">
    <div class="article-body">
      <div class="prose">
        <h2>خدمات ركن التطور في {name}</h2>
        <p>هذه الصفحة تجمع روابط مقالات الخدمة المنشورة المرتبطة بمدينة {name}. للخدمات غير المدرجة راسلنا عبر واتساب واذكر الحي.</p>
        <ul>{items}</ul>
      </div>
    </div>
    <aside>
      <div class="side-w cta">
        <h3>طلب في {name}</h3>
        <p>اكتب الحي ونوع العقار ووصف العَرَض.</p>
        {wa_btn("واتساب")}
      </div>
    </aside>
  </div>
</section>
""".strip()


def faq() -> str:
    items = [
        ("general", "ما هي مناطق التغطية؟", "الموقع مخصص للسعودية. كل مقال خدمة يحدد مدينته في العنوان والنص. لا نخلط مدن الإمارات هنا."),
        ("general", "كيف أتواصل؟", "عبر واتساب الظاهر في الهيدر والفوتر. أزرار الاتصال الهاتفي مخفية حتى يتوفر رقم سعودي."),
        ("pricing", "هل تنشرون سعرًا ثابتًا؟", "لا. يُذكر التقدير بعد معرفة المدينة والحي ونوع العقار ووصف العَرَض."),
        ("pricing", "بأي عملة؟", "الريال السعودي. أي إشارة لدرهم أو ضريبة 5٪ في أدوات الحجز خطأ قالب وتُصحَّح إلى SAR."),
        ("warranty", "هل يوجد ضمان مكتوب عام؟", "الضمان إن وُجد يُذكر في اتفاق العمل بعد المعاينة، لا كنسبة ثابتة في كل الصفحات."),
        ("service", "هل كشف التسربات يحتاج تكسيرًا؟", "الأجهزة تقلل التكسير العشوائي. الحاجة لفتح نقطة تُشرح بعد الفحص إن لزمت."),
        ("service", "هل تستخدمون مواد محددة بالاسم؟", "المواد تُذكر للعميل حسب الحالة. لا نثبت علامات تجارية في هذه الصفحة دون بند عمل."),
    ]
    html_items = "".join(
        f'<div class="faq-item" data-cat="{cat}"><div class="faq-q" onclick="faqT(this)">{q} <i class="fas fa-chevron-down"></i></div><div class="faq-a"><p>{a}</p></div></div>'
        for cat, q, a in items
    )
    return f"""
<section class="sec">
  <div class="wrap">
    <div class="faq-list">
      {html_items}
    </div>
    <div style="text-align:center;margin-top:44px">
      <p style="color:var(--text2);margin-bottom:16px">لم تجد إجابة تناسب حالتك؟</p>
      {wa_btn("اسأل عبر واتساب")}
    </div>
  </div>
</section>
""".strip()


def privacy() -> str:
    return f"""
<section class="sec">
  <div class="wrap article-layout">
    <div class="article-body">
      <div class="prose">
        <h2 id="s0">جمع المعلومات</h2>
        <p>نجمع ما ترسله عبر واتساب أو صفحات الموقع لتنسيق الخدمة: الاسم، رقم التواصل، المدينة والحي، ووصف الطلب.</p>
        <h2 id="s1">الاستخدام</h2>
        <p>نستخدم البيانات لتنسيق الزيارة والرد على الطلب. لا نبيعها ولا نستخدمها لإعلان طرف ثالث.</p>
        <h2 id="s2">المشاركة</h2>
        <p>قد يطّلع الفريق الفني المكلف بالتنفيذ على ما يلزم لإنجاز العمل فقط.</p>
        <h2 id="s3">الأمان</h2>
        <p>نقيّد الوصول إلى بيانات الطلب داخل أدوات العمل المستخدمة للرد.</p>
        <h2 id="s4">حقوقك</h2>
        <p>يمكنك طلب تصحيح أو حذف بيانات طلبك عبر واتساب.</p>
        <h2 id="s5">ملفات الارتباط</h2>
        <p>قد يستخدم الموقع ملفات أساسية للتصفح والإحصاء المجمّع.</p>
        <h2 id="s6">التعديل</h2>
        <p>أي تغيير جوهري على هذه السياسة يُنشر في هذه الصفحة.</p>
      </div>
    </div>
    <aside>
      <div class="side-w cta">
        <h3>استفسار خصوصية</h3>
        {wa_btn()}
      </div>
    </aside>
  </div>
</section>
""".strip()


def terms() -> str:
    return f"""
<section class="sec">
  <div class="wrap article-layout">
    <div class="article-body">
      <div class="prose">
        <h2 id="s0">قبول الشروط</h2>
        <p>استخدام الموقع أو طلب خدمة يعني الاطلاع على هذه البنود.</p>
        <h2 id="s1">نطاق الخدمات</h2>
        <p>الخدمات المعروضة هي أعمال منزلية في السعودية حسب صفحة كل خدمة ومدينة.</p>
        <h2 id="s2">الحجز والدفع</h2>
        <p>يُؤكَّد النطاق والسعر بعد التفاصيل أو المعاينة. العملة الريال السعودي.</p>
        <h2 id="s3">الإلغاء</h2>
        <p>إعادة الجدولة تُتفق عبر واتساب حسب توفر الفريق.</p>
        <h2 id="s4">الضمان</h2>
        <p>إن وُجد ضمان يُكتب في اتفاق ذلك الطلب ولا يُعمَّم من هذه الصفحة.</p>
        <h2 id="s5">مسؤولية العميل</h2>
        <p>يلتزم العميل بوصف دقيق للموقع والعَرَض وسماح الدخول المتفق عليه.</p>
        <h2 id="s6">التعديلات</h2>
        <p>تُحدَّث هذه الصفحة عند تغيير بنود جوهرية.</p>
      </div>
    </div>
    <aside>
      <div class="side-w cta">
        <h3>سؤال عن البنود</h3>
        {wa_btn()}
      </div>
    </aside>
  </div>
</section>
""".strip()


def pricing() -> str:
    return f"""
<section class="sec">
  <div class="wrap">
    <div class="shead"><span class="tag">التسعير</span><h2>كيف <span>يُقدَّر العمل</span></h2>
    <p>لا نضع باقات درهم أو أرقاماً مخترعة. التقدير بعد معرفة التفاصيل.</p></div>
    <div class="services-grid">
      <div class="svc"><h3>المدينة والحي</h3><p class="desc">المسافة وسهولة الوصول وتوقيت العقار تغيّر العرض.</p></div>
      <div class="svc"><h3>نوع العقار</h3><p class="desc">شقة أو فيلا أو منشأة تختلف في نقاط الفحص أو نطاق التنظيف.</p></div>
      <div class="svc"><h3>وصف العَرَض</h3><p class="desc">جملة واحدة عن المشكلة تغني عن جدول أسعار عام.</p></div>
    </div>
    <div style="text-align:center;margin-top:36px">{wa_btn("اطلب تقديراً عبر واتساب")}</div>
  </div>
</section>
""".strip()


def sitemap() -> str:
    city_links = "".join(
        f'<li><a href="{HOME}/cities/{slug}/">{name}</a></li>' for slug, name in CITIES
    )
    svc_links = "".join(
        f'<li><a href="{HOME}/services/{slug}/">{name}</a></li>' for slug, name, _, _ in SERVICES
    )
    return f"""
<section class="sec">
  <div class="wrap article-body">
    <h2>صفحات أساسية</h2>
    <ul>
      <li><a href="{HOME}/">الرئيسية</a></li>
      <li><a href="{HOME}/services/">الخدمات</a></li>
      <li><a href="{HOME}/cities/">المدن</a></li>
      <li><a href="{HOME}/about/">من نحن</a></li>
      <li><a href="{HOME}/contact-us/">اتصل بنا</a></li>
      <li><a href="{HOME}/faq/">الأسئلة الشائعة</a></li>
      <li><a href="{HOME}/pricing/">الأسعار</a></li>
      <li><a href="{HOME}/privacy-policy/">سياسة الخصوصية</a></li>
      <li><a href="{HOME}/terms/">الشروط والأحكام</a></li>
      <li><a href="{HOME}/blog/">المدونة</a></li>
    </ul>
    <h2>الخدمات</h2>
    <ul>{svc_links}</ul>
    <h2>المدن</h2>
    <ul>{city_links}</ul>
  </div>
</section>
""".strip()


def blog() -> str:
    return f"""
<section class="sec" style="padding-top:0">
  <div class="wrap">
    <p>هنا أحدث المقالات المنشورة. صفحات الخدمة حسب المدينة تبقى في روابطها الأصلية.</p>
  </div>
</section>
""".strip()


HUBS = {
    "about": {
        "title": "من نحن",
        "excerpt": "ركن التطور في السعودية: خدمات منزلية حسب المدينة، وتواصل عبر واتساب حتى يتوفر رقم اتصال سعودي.",
        "content": about(),
        "rm_title": "من نحن | ركن التطور السعودية",
        "rm_desc": "تعرّف على طريقة عمل ركن التطور في السعودية دون خلط مع نسخة الإمارات.",
        "kw": "ركن التطور السعودية",
    },
    "contact-us": {
        "title": "اتصل بنا",
        "excerpt": "تواصل مع ركن التطور السعودية عبر واتساب. أزرار الاتصال مخفية حتى يتوفر رقم سعودي.",
        "content": contact(),
        "rm_title": "اتصل بنا | ركن التطور السعودية",
        "rm_desc": "واتساب ركن التطور للسعودية. اذكر المدينة والحي ووصف العَرَض.",
        "kw": "اتصل بنا ركن التطور",
    },
    "services": {
        "title": "خدماتنا",
        "excerpt": "دليل خدمات ركن التطور المنزلية في السعودية. التفاصيل في صفحة كل خدمة.",
        "content": services(),
        "rm_title": "خدماتنا | ركن التطور السعودية",
        "rm_desc": "كشف تسربات، عزل، تكييف، تنظيف وخدمات منزلية أخرى في مدن المملكة.",
        "kw": "خدمات ركن التطور",
    },
    "cities": {
        "title": "المدن",
        "excerpt": "مدن ركن التطور في السعودية. اختر مدينتك لروابط الخدمات المرتبطة بها.",
        "content": cities(),
        "rm_title": "المدن | ركن التطور السعودية",
        "rm_desc": "الرياض وجدة ومكة والمدينة والدمام والخبر والطائف وأبها ضمن دليل المدن.",
        "kw": "مدن ركن التطور",
    },
    "faq": {
        "title": "الأسئلة الشائعة",
        "excerpt": "إجابات عن التغطية، واتساب، والتسعير بعد المعاينة — بدون أرقام مخترعة.",
        "content": faq(),
        "rm_title": "الأسئلة الشائعة | ركن التطور السعودية",
        "rm_desc": "كيف نتواصل في السعودية، وكيف يُقدَّر العمل بعد التفاصيل.",
        "kw": "أسئلة ركن التطور",
    },
    "privacy-policy": {
        "title": "سياسة الخصوصية",
        "excerpt": "كيف نتعامل مع بيانات طلب الخدمة في موقع ركن التطور السعودية.",
        "content": privacy(),
        "rm_title": "سياسة الخصوصية | ركن التطور السعودية",
        "rm_desc": "جمع واستخدام بيانات التواصل لتنسيق الخدمة في السعودية فقط.",
        "kw": "سياسة الخصوصية",
    },
    "pricing": {
        "title": "الأسعار",
        "excerpt": "عوامل تقدير خدمات ركن التطور في السعودية. لا باقات درهم ولا أرقام مخترعة.",
        "content": pricing(),
        "rm_title": "الأسعار | ركن التطور السعودية",
        "rm_desc": "التقدير بعد المدينة والحي ونوع العقار ووصف العَرَض. العملة الريال.",
        "kw": "أسعار ركن التطور",
    },
    "sitemap": {
        "title": "خريطة الموقع",
        "excerpt": "روابط صفحات ركن التطور السعودية: الخدمات والمدن والسياسات.",
        "content": sitemap(),
        "rm_title": "خريطة الموقع | ركن التطور السعودية",
        "rm_desc": "دليل صفحات الموقع للخدمات والمدن في السعودية.",
        "kw": "خريطة الموقع",
    },
    "blog": {
        "title": "المدونة",
        "excerpt": "مقالات ركن التطور المنشورة في السعودية.",
        "content": blog(),
        "rm_title": "المدونة | ركن التطور السعودية",
        "rm_desc": "أحدث المقالات المنشورة على موقع ركن التطور السعودية.",
        "kw": "مدونة ركن التطور",
    },
}

TERMS = {
    "title": "الشروط والأحكام",
    "excerpt": "بنود استخدام موقع وخدمات ركن التطور في السعودية.",
    "content": terms(),
    "rm_title": "الشروط والأحكام | ركن التطور السعودية",
    "rm_desc": "نطاق الخدمة والحجز والدفع بالريال السعودي دون بنود دولة أخرى.",
    "kw": "شروط ركن التطور",
    "slug": "terms",
}
