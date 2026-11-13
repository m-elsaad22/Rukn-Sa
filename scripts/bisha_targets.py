# -*- coding: utf-8 -*-
"""RSCA-6 Bisha target catalog: 68 service titles with SEO/slug/category plans."""

CITY_AR = "بيشة"
CITY_EN = "bisha"
PHONE_DISPLAY = "0542264115"
PHONE_E164 = "+966542264115"
PHONE_WA = "966542264115"
CATEGORY_ID = 2457  # الخدمات (active SA pattern)
CATEGORY_NAME = "الخدمات"

# Proposed unused/low-use taxonomy (do NOT auto-create; document only)
PROPOSED_CATS = {
    "cleaning": "خدمات التنظيف (251) / تنظيف منازل (2754) — حالياً بلا مقالات مربوطة عبر REST",
    "pest": "خدمات مكافحة الحشرات (83) — حالياً بلا مقالات مربوطة",
    "electrician": "صيانة كهرباء (2592) — عدّاد التصنيف غير متسق مع استعلام المقالات",
    "electrical": "صيانة كهرباء (2592) / خدمات الصيانة (2590)",
}

# Existing live URLs safe for internal links
INTERNAL_LINKS = {
    "services": "https://www.rukn-eltatawer.com/sa/services/",
    "cities": "https://www.rukn-eltatawer.com/sa/cities/",
    "contact": "https://www.rukn-eltatawer.com/sa/contact-us/",
    "about": "https://www.rukn-eltatawer.com/sa/about/",
    "bisha_leak": "https://www.rukn-eltatawer.com/sa/water-leak-detection-bisha/",
}

# Featured media from library (verified IDs)
MEDIA = {
    "cleaning": 2895,  # clean-2.webp
    "cleaning_pool": 2896,
    "cleaning_net": 2894,
    "electrical": 2690,  # electrical-maintenance.webp
    "pest": 2894,  # reuse sanitized cleaning/net visual if no pest asset
}

TARGETS = [
    # A cleaning 22
    {"group": "cleaning", "title": "شركة تنظيف منازل ببيشة", "focus": "شركة تنظيف منازل ببيشة", "slug": "home-cleaning-bisha", "emoji": "🧹", "media": "cleaning"},
    {"group": "cleaning", "title": "شركة تنظيف فلل ببيشة", "focus": "شركة تنظيف فلل ببيشة", "slug": "villa-cleaning-bisha", "emoji": "🏠", "media": "cleaning"},
    {"group": "cleaning", "title": "شركة تنظيف شقق ببيشة", "focus": "شركة تنظيف شقق ببيشة", "slug": "apartment-cleaning-bisha", "emoji": "🏢", "media": "cleaning"},
    {"group": "cleaning", "title": "شركة تنظيف مجالس ببيشة", "focus": "شركة تنظيف مجالس ببيشة", "slug": "majlis-cleaning-bisha", "emoji": "🧹", "media": "cleaning"},
    {"group": "cleaning", "title": "شركة تنظيف كنب بالبخار ببيشة", "focus": "شركة تنظيف كنب بالبخار ببيشة", "slug": "sofa-steam-cleaning-bisha", "emoji": "🛋️", "media": "cleaning"},
    {"group": "cleaning", "title": "شركة تنظيف سجاد وموكيت ببيشة", "focus": "شركة تنظيف سجاد وموكيت ببيشة", "slug": "carpet-cleaning-bisha", "emoji": "🧹", "media": "cleaning"},
    {"group": "cleaning", "title": "شركة تنظيف ستائر ومراتب ببيشة", "focus": "شركة تنظيف ستائر ومراتب ببيشة", "slug": "curtains-mattress-cleaning-bisha", "emoji": "🛏️", "media": "cleaning"},
    {"group": "cleaning", "title": "شركة تنظيف مطابخ وحمامات ببيشة", "focus": "شركة تنظيف مطابخ وحمامات ببيشة", "slug": "kitchen-bathroom-cleaning-bisha", "emoji": "🚿", "media": "cleaning"},
    {"group": "cleaning", "title": "شركة تنظيف خزانات المياه ببيشة", "focus": "شركة تنظيف خزانات المياه ببيشة", "slug": "water-tank-cleaning-bisha", "emoji": "💧", "media": "cleaning_net"},
    {"group": "cleaning", "title": "شركة تعقيم خزانات المياه ببيشة", "focus": "شركة تعقيم خزانات المياه ببيشة", "slug": "water-tank-disinfection-bisha", "emoji": "🧴", "media": "cleaning_net"},
    {"group": "cleaning", "title": "شركة تنظيف مكيفات ببيشة", "focus": "شركة تنظيف مكيفات ببيشة", "slug": "ac-cleaning-bisha", "emoji": "❄️", "media": "cleaning"},
    {"group": "cleaning", "title": "شركة غسيل مكيفات سبليت ببيشة", "focus": "شركة غسيل مكيفات سبليت ببيشة", "slug": "split-ac-washing-bisha", "emoji": "❄️", "media": "cleaning"},
    {"group": "cleaning", "title": "شركة تنظيف واجهات زجاجية ببيشة", "focus": "شركة تنظيف واجهات زجاجية ببيشة", "slug": "glass-facade-cleaning-bisha", "emoji": "🪟", "media": "cleaning"},
    {"group": "cleaning", "title": "شركة تنظيف واجهات المباني ببيشة", "focus": "شركة تنظيف واجهات المباني ببيشة", "slug": "building-facade-cleaning-bisha", "emoji": "🏗️", "media": "cleaning"},
    {"group": "cleaning", "title": "شركة جلي وتلميع الرخام ببيشة", "focus": "شركة جلي وتلميع الرخام ببيشة", "slug": "marble-polishing-bisha", "emoji": "✨", "media": "cleaning"},
    {"group": "cleaning", "title": "شركة تنظيف بالبخار ببيشة", "focus": "شركة تنظيف بالبخار ببيشة", "slug": "steam-cleaning-bisha", "emoji": "💨", "media": "cleaning"},
    {"group": "cleaning", "title": "شركة تنظيف عميق للمنازل ببيشة", "focus": "شركة تنظيف عميق للمنازل ببيشة", "slug": "deep-home-cleaning-bisha", "emoji": "🧹", "media": "cleaning"},
    {"group": "cleaning", "title": "شركة تنظيف بعد التشطيب ببيشة", "focus": "شركة تنظيف بعد التشطيب ببيشة", "slug": "post-construction-cleaning-bisha", "emoji": "🏗️", "media": "cleaning"},
    {"group": "cleaning", "title": "شركة تنظيف شقق قبل وبعد الانتقال ببيشة", "focus": "شركة تنظيف شقق قبل وبعد الانتقال ببيشة", "slug": "move-in-out-apartment-cleaning-bisha", "emoji": "📦", "media": "cleaning"},
    {"group": "cleaning", "title": "شركة تنظيف عمائر ومباني ببيشة", "focus": "شركة تنظيف عمائر ومباني ببيشة", "slug": "building-cleaning-bisha", "emoji": "🏢", "media": "cleaning"},
    {"group": "cleaning", "title": "شركة تنظيف مسابح ببيشة", "focus": "شركة تنظيف مسابح ببيشة", "slug": "pool-cleaning-bisha", "emoji": "🏊", "media": "cleaning_pool"},
    {"group": "cleaning", "title": "شركة تنظيف مكاتب وشركات ببيشة", "focus": "شركة تنظيف مكاتب وشركات ببيشة", "slug": "office-cleaning-bisha", "emoji": "💼", "media": "cleaning"},
    # B pest 18
    {"group": "pest", "title": "شركة مكافحة حشرات ببيشة", "focus": "شركة مكافحة حشرات ببيشة", "slug": "pest-control-bisha", "emoji": "🐛", "media": "pest"},
    {"group": "pest", "title": "شركة رش مبيدات ببيشة", "focus": "شركة رش مبيدات ببيشة", "slug": "pesticide-spraying-bisha", "emoji": "🧴", "media": "pest"},
    {"group": "pest", "title": "شركة مكافحة الصراصير ببيشة", "focus": "شركة مكافحة الصراصير ببيشة", "slug": "cockroach-control-bisha", "emoji": "🪳", "media": "pest"},
    {"group": "pest", "title": "شركة مكافحة النمل ببيشة", "focus": "شركة مكافحة النمل ببيشة", "slug": "ant-control-bisha", "emoji": "🐜", "media": "pest"},
    {"group": "pest", "title": "شركة مكافحة النمل الأبيض ببيشة", "focus": "شركة مكافحة النمل الأبيض ببيشة", "slug": "termite-control-bisha", "emoji": "🪵", "media": "pest"},
    {"group": "pest", "title": "شركة مكافحة البق ببيشة", "focus": "شركة مكافحة البق ببيشة", "slug": "bed-bug-control-bisha", "emoji": "🛏️", "media": "pest"},
    {"group": "pest", "title": "شركة مكافحة الفئران والقوارض ببيشة", "focus": "شركة مكافحة الفئران والقوارض ببيشة", "slug": "rodent-control-bisha", "emoji": "🐭", "media": "pest"},
    {"group": "pest", "title": "شركة مكافحة البعوض والذباب ببيشة", "focus": "شركة مكافحة البعوض والذباب ببيشة", "slug": "mosquito-fly-control-bisha", "emoji": "🦟", "media": "pest"},
    {"group": "pest", "title": "شركة مكافحة العناكب والحشرات الزاحفة ببيشة", "focus": "شركة مكافحة العناكب والحشرات الزاحفة ببيشة", "slug": "spider-crawling-pest-control-bisha", "emoji": "🕷️", "media": "pest"},
    {"group": "pest", "title": "شركة مكافحة الثعابين ببيشة", "focus": "شركة مكافحة الثعابين ببيشة", "slug": "snake-control-bisha", "emoji": "🐍", "media": "pest"},
    {"group": "pest", "title": "شركة مكافحة حشرات المطابخ ببيشة", "focus": "شركة مكافحة حشرات المطابخ ببيشة", "slug": "kitchen-pest-control-bisha", "emoji": "🍳", "media": "pest"},
    {"group": "pest", "title": "شركة مكافحة حشرات المنازل ببيشة", "focus": "شركة مكافحة حشرات المنازل ببيشة", "slug": "home-pest-control-bisha", "emoji": "🏠", "media": "pest"},
    {"group": "pest", "title": "شركة مكافحة حشرات الفلل ببيشة", "focus": "شركة مكافحة حشرات الفلل ببيشة", "slug": "villa-pest-control-bisha", "emoji": "🏡", "media": "pest"},
    {"group": "pest", "title": "شركة مكافحة حشرات الحدائق ببيشة", "focus": "شركة مكافحة حشرات الحدائق ببيشة", "slug": "garden-pest-control-bisha", "emoji": "🌿", "media": "pest"},
    {"group": "pest", "title": "شركة مكافحة آفات المستودعات ببيشة", "focus": "شركة مكافحة آفات المستودعات ببيشة", "slug": "warehouse-pest-control-bisha", "emoji": "📦", "media": "pest"},
    {"group": "pest", "title": "شركة مكافحة الحمام والطيور ببيشة", "focus": "شركة مكافحة الحمام والطيور ببيشة", "slug": "pigeon-bird-control-bisha", "emoji": "🕊️", "media": "pest"},
    {"group": "pest", "title": "شركة تركيب طارد الحمام ببيشة", "focus": "شركة تركيب طارد الحمام ببيشة", "slug": "pigeon-repellent-installation-bisha", "emoji": "🛡️", "media": "pest"},
    {"group": "pest", "title": "شركة تعقيم المنازل بعد مكافحة الحشرات ببيشة", "focus": "شركة تعقيم المنازل بعد مكافحة الحشرات ببيشة", "slug": "post-pest-home-disinfection-bisha", "emoji": "🧴", "media": "pest"},
    # C home electrician 14
    {"group": "electrician", "title": "كهربائي منازل ببيشة", "focus": "كهربائي منازل ببيشة", "slug": "home-electrician-bisha", "emoji": "⚡", "media": "electrical"},
    {"group": "electrician", "title": "أفضل كهربائي منازل ببيشة", "focus": "أفضل كهربائي منازل ببيشة", "slug": "best-home-electrician-bisha", "emoji": "⭐", "media": "electrical"},
    {"group": "electrician", "title": "فني كهرباء منازل ببيشة", "focus": "فني كهرباء منازل ببيشة", "slug": "home-electrical-technician-bisha", "emoji": "🔧", "media": "electrical"},
    {"group": "electrician", "title": "كهربائي منازل 24 ساعة ببيشة", "focus": "كهربائي منازل 24 ساعة ببيشة", "slug": "home-electrician-24h-bisha", "emoji": "🕒", "media": "electrical"},
    {"group": "electrician", "title": "كهربائي طوارئ ببيشة", "focus": "كهربائي طوارئ ببيشة", "slug": "emergency-electrician-bisha", "emoji": "🚨", "media": "electrical"},
    {"group": "electrician", "title": "كهربائي منازل لتأسيس الكهرباء ببيشة", "focus": "كهربائي منازل لتأسيس الكهرباء ببيشة", "slug": "home-electrician-foundation-bisha", "emoji": "🔌", "media": "electrical"},
    {"group": "electrician", "title": "فني إصلاح أعطال الكهرباء ببيشة", "focus": "فني إصلاح أعطال الكهرباء ببيشة", "slug": "electrical-fault-repair-tech-bisha", "emoji": "🛠️", "media": "electrical"},
    {"group": "electrician", "title": "كهربائي تركيب وصيانة الإنارة ببيشة", "focus": "كهربائي تركيب وصيانة الإنارة ببيشة", "slug": "lighting-install-maintenance-electrician-bisha", "emoji": "💡", "media": "electrical"},
    {"group": "electrician", "title": "فني تركيب مفاتيح وأفياش كهرباء ببيشة", "focus": "فني تركيب مفاتيح وأفياش كهرباء ببيشة", "slug": "switches-outlets-technician-bisha", "emoji": "🔌", "media": "electrical"},
    {"group": "electrician", "title": "فني تركيب نجف وثريات ببيشة", "focus": "فني تركيب نجف وثريات ببيشة", "slug": "chandelier-installation-tech-bisha", "emoji": "chandelier", "media": "electrical"},
    {"group": "electrician", "title": "كهربائي تركيب إنارة LED ببيشة", "focus": "كهربائي تركيب إنارة LED ببيشة", "slug": "led-lighting-electrician-bisha", "emoji": "💡", "media": "electrical"},
    {"group": "electrician", "title": "فني تركيب كشافات وإنارة خارجية ببيشة", "focus": "فني تركيب كشافات وإنارة خارجية ببيشة", "slug": "outdoor-floodlight-tech-bisha", "emoji": "🔦", "media": "electrical"},
    {"group": "electrician", "title": "فني صيانة لوحات الكهرباء المنزلية ببيشة", "focus": "فني صيانة لوحات الكهرباء المنزلية ببيشة", "slug": "home-panel-maintenance-tech-bisha", "emoji": "🧰", "media": "electrical"},
    {"group": "electrician", "title": "فني إصلاح القواطع الكهربائية ببيشة", "focus": "فني إصلاح القواطع الكهربائية ببيشة", "slug": "breaker-repair-technician-bisha", "emoji": "⚡", "media": "electrical"},
    # D electrical services 14
    {"group": "electrical", "title": "شركة تأسيس كهرباء منازل ببيشة", "focus": "شركة تأسيس كهرباء منازل ببيشة", "slug": "home-electrical-installation-bisha", "emoji": "🔌", "media": "electrical"},
    {"group": "electrical", "title": "شركة تمديد أسلاك كهربائية ببيشة", "focus": "شركة تمديد أسلاك كهربائية ببيشة", "slug": "electrical-wiring-extension-bisha", "emoji": "🧵", "media": "electrical"},
    {"group": "electrical", "title": "شركة تمديد كابلات الكهرباء ببيشة", "focus": "شركة تمديد كابلات الكهرباء ببيشة", "slug": "power-cable-extension-bisha", "emoji": "📡", "media": "electrical"},
    {"group": "electrical", "title": "شركة تمديد كهرباء المباني ببيشة", "focus": "شركة تمديد كهرباء المباني ببيشة", "slug": "building-electrical-extension-bisha", "emoji": "🏢", "media": "electrical"},
    {"group": "electrical", "title": "شركة تركيب لوحات توزيع الكهرباء ببيشة", "focus": "شركة تركيب لوحات توزيع الكهرباء ببيشة", "slug": "distribution-board-installation-bisha", "emoji": "🧰", "media": "electrical"},
    {"group": "electrical", "title": "شركة كشف التماسات الكهربائية ببيشة", "focus": "شركة كشف التماسات الكهربائية ببيشة", "slug": "electrical-short-detection-bisha", "emoji": "🔍", "media": "electrical"},
    {"group": "electrical", "title": "شركة كشف أعطال الكهرباء ببيشة", "focus": "شركة كشف أعطال الكهرباء ببيشة", "slug": "electrical-fault-detection-bisha", "emoji": "🔎", "media": "electrical"},
    {"group": "electrical", "title": "شركة إصلاح التماس كهربائي ببيشة", "focus": "شركة إصلاح التماس كهربائي ببيشة", "slug": "electrical-short-repair-bisha", "emoji": "🛠️", "media": "electrical"},
    {"group": "electrical", "title": "شركة إصلاح أعطال الكابلات الأرضية ببيشة", "focus": "شركة إصلاح أعطال الكابلات الأرضية ببيشة", "slug": "underground-cable-repair-bisha", "emoji": "🚧", "media": "electrical"},
    {"group": "electrical", "title": "شركة تركيب أنظمة الإنارة المنزلية ببيشة", "focus": "شركة تركيب أنظمة الإنارة المنزلية ببيشة", "slug": "home-lighting-systems-bisha", "emoji": "💡", "media": "electrical"},
    {"group": "electrical", "title": "شركة صيانة الكهرباء للمنازل والفلل ببيشة", "focus": "شركة صيانة الكهرباء للمنازل والفلل ببيشة", "slug": "home-villa-electrical-maintenance-bisha", "emoji": "🏠", "media": "electrical"},
    {"group": "electrical", "title": "شركة صيانة الكهرباء للمباني والمنشآت ببيشة", "focus": "شركة صيانة الكهرباء للمباني والمنشآت ببيشة", "slug": "building-facility-electrical-maintenance-bisha", "emoji": "🏭", "media": "electrical"},
    {"group": "electrical", "title": "شركة تركيب أنظمة الحماية الكهربائية ببيشة", "focus": "شركة تركيب أنظمة الحماية الكهربائية ببيشة", "slug": "electrical-protection-systems-bisha", "emoji": "🛡️", "media": "electrical"},
    {"group": "electrical", "title": "شركة تركيب وصيانة المولدات الكهربائية ببيشة", "focus": "شركة تركيب وصيانة المولدات الكهربائية ببيشة", "slug": "generator-install-maintenance-bisha", "emoji": "⚙️", "media": "electrical"},
]

assert len(TARGETS) == 68, len(TARGETS)

# Fix chandelier emoji (invalid in some contexts) — use light bulb
for t in TARGETS:
    if t["emoji"] == "chandelier":
        t["emoji"] = "💡"

GROUP_LABELS = {
    "cleaning": "خدمات التنظيف",
    "pest": "مكافحة الحشرات",
    "electrician": "كهربائي المنازل",
    "electrical": "خدمات الكهرباء والتمديدات",
}
